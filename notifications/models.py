from django.db import models
from django.contrib.auth.models import User
import uuid


class Notification(models.Model):
    """
    Stores every notification the system sends.
    One row per channel per message.
    e.g. one inactivity warning = 3 rows (email + sms + in_app)
    """

    CHANNEL_CHOICES = [
        ('email',  'Email'),
        ('sms',    'SMS'),
        ('in_app', 'In-App'),
    ]

    STATUS_CHOICES = [
        ('queued',    'Queued'),
        ('sent',      'Sent'),
        ('failed',    'Failed'),
        ('bounced',   'Bounced'),
    ]

    RECIPIENT_CHOICES = [
        ('user',         'User'),
        ('beneficiary',  'Beneficiary'),
        ('admin',        'Admin'),
    ]

    # Unique ID for this notification
    notification_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Which user this notification is about
    # (even if sent to a beneficiary, we still link it to the user)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )

    # Who received it
    recipient_type = models.CharField(
        max_length=20,
        choices=RECIPIENT_CHOICES,
        default='user'
    )

    # Which channel was used
    channel = models.CharField(
        max_length=20,
        choices=CHANNEL_CHOICES
    )

    # Which message template was used
    # e.g. 'INACTIVITY_WARNING_30' or 'BENEFICIARY_ACCESS_GRANTED'
    template_code = models.CharField(max_length=100)

    # Current status of this notification
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='queued'
    )

    # When it was actually sent (null if failed or still queued)
    sent_at = models.DateTimeField(null=True, blank=True)

    # When this record was created
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"{self.template_code} | "
            f"{self.channel} | "
            f"{self.status} | "
            f"{self.created_at.strftime('%Y-%m-%d %H:%M')}"
        )


class VerificationAttempt(models.Model):
    """
    Stores each 'are you alive?' verification token sent to a user.
    When the user clicks the link, we mark responded=True
    and reset their inactivity counter.
    """

    # Which user this verification is for
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='verification_attempts'
    )

    # Unique token included in the confirmation link
    token = models.CharField(
        max_length=100,
        unique=True
    )

    # Has the user clicked the link yet?
    responded = models.BooleanField(default=False)

    # When does this token expire?
    expires_at = models.DateTimeField()

    # When was this token created?
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status = "Responded" if self.responded else "Pending"
        return (
            f"User: {self.user.username} | "
            f"{status} | "
            f"Expires: {self.expires_at.strftime('%Y-%m-%d %H:%M')}"
        )