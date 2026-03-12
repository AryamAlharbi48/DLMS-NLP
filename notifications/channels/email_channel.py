import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

# This creates a logger for this file specifically
# You'll see messages like "[email_channel] Email sent to ..."
# in your terminal when running the server
logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, html_body: str) -> bool:
    """
    Sends an HTML email to a single recipient.

    Args:
        to        : recipient email address e.g. "user@gmail.com"
        subject   : email subject line
        html_body : full HTML content of the email

    Returns:
        True  if the email was sent successfully
        False if something went wrong (error is logged)
    """

    # Safety check — don't attempt to send if no address provided
    if not to:
        logger.warning("send_email called with empty 'to' address. Skipped.")
        return False

    try:
        # EmailMultiAlternatives lets us send both plain text
        # and HTML in the same email. Email clients that don't
        # support HTML will show the plain text version instead.
        email = EmailMultiAlternatives(
            subject=subject,
            body="Please view this email in an HTML-supported client.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to]
        )

        # Attach the HTML version
        email.attach_alternative(html_body, "text/html")

        # Send it
        email.send()

        logger.info(f"[email_channel] Email sent successfully to: {to}")
        return True

    except Exception as e:
        logger.error(f"[email_channel] Failed to send email to {to}: {e}")
        return False