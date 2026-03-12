import logging
from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone
from notifications.models import VerificationAttempt
from notifications.dispatcher import dispatch

logger = logging.getLogger(__name__)


def confirm_alive(request, token):
    """
    This view is called when a user clicks the
    "I am alive" link from their email or SMS.

    URL: /notifications/alive/<token>/

    What it does:
      1. Finds the verification token in the database
      2. Checks it hasn't expired
      3. Checks it hasn't already been used
      4. Marks the user as active
      5. Resets their last_login to today
      6. Sends a confirmation notification back to them
      7. Returns a success response

    The frontend (your Flutter app) should show a
    success screen when it receives status "success".
    """

    # ── Step 1: Find the token ────────────────────────────────────
    try:
        attempt = VerificationAttempt.objects.get(token=token)
    except VerificationAttempt.DoesNotExist:
        logger.warning(
            f"[views] Invalid token used: {token[:8]}..."
        )
        return JsonResponse({
            "status":  "error",
            "message": "رابط غير صالح. / Invalid link.",
            "code":    "INVALID_TOKEN"
        }, status=404)

    # ── Step 2: Check if already used ────────────────────────────
    if attempt.responded:
        logger.info(
            f"[views] Token already used: {token[:8]}..."
        )
        return JsonResponse({
            "status":  "error",
            "message": "تم استخدام هذا الرابط مسبقاً. / "
                       "This link has already been used.",
            "code":    "TOKEN_ALREADY_USED"
        }, status=400)

    # ── Step 3: Check if expired ──────────────────────────────────
    now = datetime.utcnow()
    expires = attempt.expires_at.replace(tzinfo=None)

    if now > expires:
        logger.warning(
            f"[views] Expired token used by "
            f"user {attempt.user.username}"
        )
        return JsonResponse({
            "status":  "error",
            "message": "انتهت صلاحية الرابط. / Link has expired.",
            "code":    "TOKEN_EXPIRED"
        }, status=410)

    # ── Step 4: Mark token as responded ──────────────────────────
    attempt.responded = True
    attempt.save()

    # ── Step 5: Reset user activity ──────────────────────────────
    user = attempt.user

    # Reactivate account if it was deactivated
    user.is_active  = True

    # Reset last_login to right now
    # This restarts the inactivity counter from zero
    user.last_login = timezone.now()
    user.save()

    logger.info(
        f"[views] User {user.username} confirmed alive. "
        f"Inactivity counter reset."
    )

    # ── Step 6: Send confirmation notification ────────────────────
    phone = getattr(user, "phone", None)

    dispatch(
        template_code="CONFIRMED_ALIVE",
        template_data={
            "name": user.get_full_name() or user.username,
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

    # ── Step 7: Return success ────────────────────────────────────
    return JsonResponse({
        "status":  "success",
        "message": "✅ تم تأكيد نشاطك بنجاح. / "
                   "Your activity has been confirmed successfully.",
        "user":    user.username,
        "code":    "CONFIRMED"
    })


def beneficiary_access(request, beneficiary_id):
    """
    This view is called when a beneficiary tries to
    access their inherited assets after death confirmation.

    URL: /notifications/beneficiary/<beneficiary_id>/access/

    For now this is a placeholder that returns the
    beneficiary ID. You will expand this once the
    Beneficiary model is added to your project.
    """

    logger.info(
        f"[views] Beneficiary access request: "
        f"beneficiary_id={beneficiary_id}"
    )

    # Placeholder response
    # Replace this with actual beneficiary authentication
    # once your Beneficiary model is ready
    return JsonResponse({
        "status":         "success",
        "message":        "Beneficiary access endpoint ready.",
        "beneficiary_id": beneficiary_id,
        "note":           "Full implementation pending "
                          "Beneficiary model."
    })