import logging
from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)


def send_sms(to: str, body: str) -> bool:
    """
    Sends an SMS message via Twilio.

    Args:
        to   : recipient phone number in E.164 format
               e.g. "+966501234567" (Saudi number)
               e.g. "+1234567890"   (US number)
        body : the text message content (keep under 160 chars
               to avoid being split into multiple messages)

    Returns:
        True  if the SMS was sent successfully
        False if something went wrong (error is logged)
    """

    # Safety check — don't attempt if no phone number provided
    if not to:
        logger.warning("send_sms called with empty 'to' number. Skipped.")
        return False

    # Safety check — don't attempt if Twilio is not configured
    if not settings.TWILIO_SID or not settings.TWILIO_TOKEN:
        logger.warning("Twilio credentials not configured. SMS skipped.")
        return False

    try:
        # Create Twilio client using credentials from settings.py
        # which reads them from your .env file
        client = Client(
            settings.TWILIO_SID,
            settings.TWILIO_TOKEN
        )

        # Send the message
        message = client.messages.create(
            body=body,
            from_=settings.TWILIO_PHONE,
            to=to
        )

        logger.info(
            f"[sms_channel] SMS sent successfully to: {to} "
            f"| Twilio SID: {message.sid}"
        )
        return True

    except TwilioRestException as e:
        # Twilio-specific error (e.g. invalid number, insufficient funds)
        logger.error(
            f"[sms_channel] Twilio error sending to {to}: "
            f"Code {e.code} — {e.msg}"
        )
        return False

    except Exception as e:
        # Any other unexpected error
        logger.error(f"[sms_channel] Unexpected error sending to {to}: {e}")
        return False