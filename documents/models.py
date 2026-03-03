from django.db import models
from django.contrib.auth.models import User

class Document(models.Model):
    SENSITIVITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    sensitivity_level = models.CharField(
        max_length=10,
        choices=SENSITIVITY_CHOICES,
        default='LOW'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.title