import logging
import json
from datetime import datetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


def send_inapp(user_id: int, payload: dict) -> bool:
    """
    Sends a real-time in-app notification to a specific user.

    How it works:
    - Django Channels creates a "channel layer" (in-memory message bus)
    - Each logged-in user joins a private "room" named "user_{user_id}"
    - We send a message to that room
    - The user's browser receives it instantly via WebSocket

    Args:
        user_id : the Django User's primary key (integer)
        payload : dictionary from template's inapp_body e.g.
                  {
                    "title":      "تنبيه عدم النشاط",
                    "message":    "حسابك غير نشط منذ 90 يوماً",
                    "action_url": "http://localhost:8000/alive/token",
                    "severity":   "warning"
                  }

    Severity levels and their meanings:
        "success"  → green  (e.g. confirmed alive)
        "warning"  → yellow (e.g. inactivity warning)
        "critical" → red    (e.g. final warning)
        "info"     → blue   (e.g. beneficiary access granted)

    Returns:
        True  if the notification was sent successfully
        False if something went wrong (error is logged)
    """

    # Safety check
    if not user_id:
        logger.warning("send_inapp called with empty user_id. Skipped.")
        return False

    try:
        # Get the channel layer (configured in settings.py)
        channel_layer = get_channel_layer()

        if channel_layer is None:
            logger.error(
                "[inapp_channel] Channel layer is None. "
                "Check CHANNEL_LAYERS in settings.py."
            )
            return False

        # Build the full notification event
        # This is what the frontend JavaScript will receive
        event = {
            "type": "dlms.notification",   # must match consumer method name
            "notification": {
                "title":      payload.get("title", "إشعار جديد"),
                "message":    payload.get("message", ""),
                "action_url": payload.get("action_url"),
                "severity":   payload.get("severity", "info"),
                "timestamp":  datetime.utcnow().isoformat(),
                "read":       False,
            }
        }

        # Send to the user's private room
        # The room name is "user_{user_id}"
        # e.g. user with id=5 is in room "user_5"
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}",
            event
        )

        logger.info(
            f"[inapp_channel] In-app notification sent "
            f"to user_{user_id} | title: {payload.get('title')}"
        )
        return True

    except Exception as e:
        logger.error(
            f"[inapp_channel] Failed to send in-app "
            f"notification to user_{user_id}: {e}"
        )
        return False