import logging
import secrets
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from notifications.dispatcher import dispatch
from notifications.models import VerificationAttempt

logger = logging.getLogger(__name__)


# ================================================================
# INACTIVITY CHECK — runs every day at 9:00 AM
# ================================================================
# This is the core of your death verification flow from the report:
#
#   1. Monitor user inactivity
#   2. Send warnings at 90, 30, 7 days before threshold
#   3. If threshold exceeded with no response → assume deceased
#   4. Trigger posthumous actions
# ================================================================

def run_inactivity_check():
    """
    Checks all active users for inactivity.
    Called daily by the scheduler.

    For each user it calculates:
      - days_inactive : how many days since last login
      - days_left     : how many days until the threshold

    Then sends the appropriate warning or triggers death assumption.
    """
    logger.info(
        "[scheduler] ====== Daily Inactivity Check Started ======"
    )

    # Get all active users who have logged in at least once
    users = User.objects.filter(
        is_active=True,
        last_login__isnull=False
    )

    logger.info(f"[scheduler] Checking {users.count()} active users...")

    for user in users:
        try:
            _check_single_user(user)
        except Exception as e:
            logger.error(
                f"[scheduler] Error checking user "
                f"{user.username}: {e}"
            )

    logger.info(
        "[scheduler] ====== Daily Inactivity Check Complete ======"
    )


def _check_single_user(user):
    """
    Checks inactivity for a single user and takes action.
    """

    # Calculate how long since they last logged in
    now          = datetime.utcnow()
    last_login   = user.last_login.replace(tzinfo=None)
    days_inactive = (now - last_login).days

    # Get threshold from settings (default 365 days)
    threshold = getattr(
        settings, "INACTIVITY_THRESHOLD_DAYS", 365
    )

    # How many days left before threshold is reached
    days_left = threshold - days_inactive

    logger.debug(
        f"[scheduler] User: {user.username} | "
        f"Inactive: {days_inactive} days | "
        f"Days left: {days_left}"
    )

    # ── WARNING CHECKPOINTS ───────────────────────────────────────
    # Send warnings at exactly 90, 30, and 7 days before threshold
    # These match your report's 3-step verification process
    if days_left in [90, 30, 7]:
        _send_warning(user, days_inactive, days_left)

    # ── THRESHOLD EXCEEDED ────────────────────────────────────────
    # User has not responded to any warnings
    # Assume deceased and trigger posthumous actions
    elif days_inactive >= threshold:
        _trigger_death_assumption(user, days_inactive)


def _send_warning(user, days_inactive, days_left):
    """
    Sends an inactivity warning to the user via all 3 channels.
    Creates a unique token the user can click to confirm they're alive.
    """

    # Generate a unique secure token for this verification attempt
    # This becomes the "I am alive" link
    token = secrets.token_urlsafe(32)

    # Token expires after VERIFICATION_EXPIRY_HOURS (default 48hrs)
    expiry_hours = getattr(
        settings, "VERIFICATION_EXPIRY_HOURS", 48
    )
    expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)

    # Save the token to the database
    VerificationAttempt.objects.create(
        user=user,
        token=token,
        expires_at=expires_at
    )

    # Build the confirmation URL
    # User clicks this link to confirm they are alive
    base_url    = getattr(settings, "APP_BASE_URL", "http://localhost:8000")
    confirm_url = f"{base_url}/notifications/alive/{token}/"

    # Pick the correct template based on urgency
    if days_left == 90:
        template_code = "INACTIVITY_WARNING_90"
    elif days_left == 30:
        template_code = "INACTIVITY_WARNING_30"
    else:
        template_code = "INACTIVITY_WARNING_7"

    # Get user's phone number if available
    # Django's default User model doesn't have phone
    # so we check for it safely
    phone = getattr(user, "phone", None)

    # Send via all 3 channels
    dispatch(
        template_code=template_code,
        template_data={
            "name":          user.get_full_name() or user.username,
            "days_inactive": days_inactive,
            "days_left":     days_left,
            "confirm_url":   confirm_url,
        },
        recipient={
            "email":   user.email,
            "phone":   phone,
            "user_id": user.id,
        },
        channels=["email", "sms", "in_app"],
        user=user,
        recipient_type="user"
    )

    logger.info(
        f"[scheduler] Warning sent to {user.username} | "
        f"Template: {template_code} | "
        f"Token: {token[:8]}..."
    )


def _trigger_death_assumption(user, days_inactive):
    """
    Called when a user exceeds the inactivity threshold
    and has not responded to any verification messages.

    Steps:
      1. Mark user as inactive in Django
      2. Notify admin
      3. Notify beneficiaries (when beneficiary model is ready)
      4. Log the event
    """

    logger.warning(
        f"[scheduler] ⚠️  DEATH ASSUMPTION TRIGGERED "
        f"for user: {user.username} | "
        f"Inactive: {days_inactive} days"
    )

    # Step 1 — Deactivate the user account
    # This prevents further logins
    User.objects.filter(pk=user.pk).update(is_active=False)

    # Step 2 — Notify admin
    # Get admin email from settings
    admin_email = getattr(settings, "ADMINS", [])
    admin_email = admin_email[0][1] if admin_email else None

    if admin_email:
        base_url  = getattr(
            settings, "APP_BASE_URL", "http://localhost:8000"
        )
        dispatch(
            template_code="DEATH_ASSUMED_ADMIN",
            template_data={
                "username":    user.username,
                "user_id":     user.id,
                "days_inactive": days_inactive,
                "triggered_at": datetime.utcnow().strftime(
                    "%Y-%m-%d %H:%M UTC"
                ),
                "admin_url":   f"{base_url}/admin/auth/user/{user.id}/"
            },
            recipient={
                "email":   admin_email,
                "phone":   None,
                "user_id": None,
            },
            channels=["email"],
            user=user,
            recipient_type="admin"
        )

    # Step 3 — Notify beneficiaries
    # This will be fully implemented once the Beneficiary
    # model is added to your project.
    # For now we log a placeholder.
    logger.info(
        f"[scheduler] TODO: Notify beneficiaries for "
        f"user {user.username}"
    )

    # Step 4 — Log completion
    logger.warning(
        f"[scheduler] Death assumption complete for "
        f"{user.username}. Account deactivated."
    )


def notify_beneficiary(deceased_user, beneficiary, assets):
    """
    Call this function after death is confirmed to notify
    a beneficiary that they can now access their assets.

    Args:
        deceased_user : the User object of the deceased
        beneficiary   : object with .name, .email, .phone,
                        .access_code, .id attributes
        assets        : list of asset objects with .title attribute
    """

    base_url   = getattr(
        settings, "APP_BASE_URL", "http://localhost:8000"
    )
    access_url = (
        f"{base_url}/notifications/beneficiary/"
        f"{beneficiary.id}/access/"
    )

    dispatch(
        template_code="BENEFICIARY_ACCESS_GRANTED",
        template_data={
            "beneficiary_name": beneficiary.name,
            "deceased_name":    deceased_user.get_full_name()
                                or deceased_user.username,
            "assets":           [a.title for a in assets],
            "access_code":      beneficiary.access_code,
            "access_url":       access_url,
        },
        recipient={
            "email":   beneficiary.email,
            "phone":   getattr(beneficiary, "phone", None),
            "user_id": None,
        },
        channels=["email", "sms"],
        user=deceased_user,
        recipient_type="beneficiary"
    )

    logger.info(
        f"[scheduler] Beneficiary notified: "
        f"{beneficiary.name} for user {deceased_user.username}"
    )