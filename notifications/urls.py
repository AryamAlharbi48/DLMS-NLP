from django.urls import path
from notifications import views

# All URLs in this file are prefixed with /notifications/
# because of how we connect them in config/urls.py (next step)
#
# Full URLs will be:
#   /notifications/alive/<token>/
#   /notifications/beneficiary/<id>/access/

urlpatterns = [

    # ── "I am alive" confirmation endpoint ───────────────────────
    # Called when user clicks the link in their email or SMS
    # Example: /notifications/alive/abc123xyz/
    path(
        "alive/<str:token>/",
        views.confirm_alive,
        name="confirm_alive"
    ),

    # ── Beneficiary access endpoint ───────────────────────────────
    # Called when a beneficiary logs in after death confirmation
    # Example: /notifications/beneficiary/42/access/
    path(
        "beneficiary/<int:beneficiary_id>/access/",
        views.beneficiary_access,
        name="beneficiary_access"
    ),

]