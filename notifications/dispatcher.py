import logging
from datetime import datetime
from notifications.templates import TEMPLATES
from notifications.channels.email_channel import send_email
from notifications.channels.sms_channel import send_sms
from notifications.channels.inapp_channel import send_inapp
from notifications.models import Notification

logger = logging.getLogger(__name__)


def dispatch(
    template_code: str,
    template_data: dict,
    recipient: dict,
    channels: list,
    user=None,
    recipient_type: str = "user"
) -> dict:
    """
    The main notification dispatcher.
    Call this function from anywhere in your Django project
    to send a notification across one or more channels.

    Args:
        template_code  : key from TEMPLATES dict
                         e.g. "INACTIVITY_WARNING_30"

        template_data  : variables injected into the template
                         e.g. {
                           "name":        "Ghala",
                           "days_inactive": 335,
                           "days_left":    30,
                           "confirm_url": "http://..."
                         }

        recipient      : who receives the notification
                         e.g. {
                           "email":   "user@gmail.com",
                           "phone":   "+966501234567",
                           "user_id": 5
                         }
                         Any of these can be None if not available.

        channels       : list of channels to use
                         e.g. ["email", "sms", "in_app"]
                         or just ["email"] for email only

        user           : the Django User object (for DB logging)
                         pass None if not available

        recipient_type : "user" | "beneficiary" | "admin"

    Returns:
        A dictionary with the result of each channel
        e.g. {
          "email":  "sent",
          "sms":    "sent",
          "in_app": "failed"
        }

    Example usage from anywhere in your project:
        from notifications.dispatcher import dispatch

        dispatch(
            template_code="INACTIVITY_WARNING_30",
            template_data={
                "name":         user.get_full_name(),
                "days_inactive": 335,
                "days_left":    30,
                "confirm_url":  "http://localhost:8000/alive/abc123"
            },
            recipient={
                "email":   user.email,
                "phone":   "+966501234567",
                "user_id": user.id
            },
            channels=["email", "sms", "in_app"],
            user=user
        )
    """

    # Step 1 — Get the template
    template = TEMPLATES.get(template_code)
    if not template:
        logger.error(
            f"[dispatcher] Unknown template_code: '{template_code}'. "
            f"Check notifications/templates.py for valid keys."
        )
        return {}

    # Step 2 — Track results for each channel
    results = {}

    # ── EMAIL ─────────────────────────────────────────────────────────
    if "email" in channels:
        email_address = recipient.get("email")

        if not email_address:
            logger.warning(
                f"[dispatcher] Email requested for {template_code} "
                f"but no email address provided. Skipped."
            )
            results["email"] = "skipped"
        else:
            try:
                # Build subject and body from template
                subject   = template["email_subject"](template_data)
                html_body = template["email_body"](template_data)

                # Send
                ok = send_email(email_address, subject, html_body)
                results["email"] = "sent" if ok else "failed"

            except Exception as e:
                logger.error(
                    f"[dispatcher] Error building email for "
                    f"{template_code}: {e}"
                )
                results["email"] = "failed"

        # Log to database
        _save_to_db(
            user=user,
            recipient_type=recipient_type,
            channel="email",
            template_code=template_code,
            status=results.get("email", "failed")
        )

    # ── SMS ───────────────────────────────────────────────────────────
    if "sms" in channels:
        phone_number = recipient.get("phone")

        if not phone_number:
            logger.warning(
                f"[dispatcher] SMS requested for {template_code} "
                f"but no phone number provided. Skipped."
            )
            results["sms"] = "skipped"
        else:
            try:
                # Build SMS body from template
                sms_body = template["sms_body"](template_data)

                # Send
                ok = send_sms(phone_number, sms_body)
                results["sms"] = "sent" if ok else "failed"

            except Exception as e:
                logger.error(
                    f"[dispatcher] Error building SMS for "
                    f"{template_code}: {e}"
                )
                results["sms"] = "failed"

        # Log to database
        _save_to_db(
            user=user,
            recipient_type=recipient_type,
            channel="sms",
            template_code=template_code,
            status=results.get("sms", "failed")
        )

    # ── IN-APP ────────────────────────────────────────────────────────
    if "in_app" in channels:
        user_id = recipient.get("user_id")

        if not user_id:
            logger.warning(
                f"[dispatcher] In-app requested for {template_code} "
                f"but no user_id provided. Skipped."
            )
            results["in_app"] = "skipped"
        else:
            try:
                # Build in-app payload from template
                payload = template["inapp_body"](template_data)

                # Send
                ok = send_inapp(user_id, payload)
                results["in_app"] = "sent" if ok else "failed"

            except Exception as e:
                logger.error(
                    f"[dispatcher] Error building in-app notification "
                    f"for {template_code}: {e}"
                )
                results["in_app"] = "failed"

        # Log to database
        _save_to_db(
            user=user,
            recipient_type=recipient_type,
            channel="in_app",
            template_code=template_code,
            status=results.get("in_app", "failed")
        )

    # Step 3 — Log summary
    logger.info(
        f"[dispatcher] Dispatch complete | "
        f"template: {template_code} | "
        f"results: {results}"
    )

    return results


def _save_to_db(user, recipient_type, channel, template_code, status):
    """
    Saves a record of this notification to the database.
    This is called automatically by dispatch() — you never
    need to call this directly.
    """
    try:
        Notification.objects.create(
            user=user,
            recipient_type=recipient_type,
            channel=channel,
            template_code=template_code,
            status=status,
            sent_at=datetime.utcnow() if status == "sent" else None
        )
    except Exception as e:
        logger.error(
            f"[dispatcher] Failed to save notification to DB: {e}"
        )