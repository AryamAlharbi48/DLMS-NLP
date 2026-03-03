from django.db import models


class AnalysisResult(models.Model):
    text = models.TextField()
    fuzzy_score = models.FloatField()
    ml_score = models.FloatField()
    final_score = models.FloatField()
    level = models.CharField(max_length=20)  # زياده الطول لتكون مرنة
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # ترتيب النتائج حسب الأحدث
        verbose_name = "Analysis Result"
        verbose_name_plural = "Analysis Results"

    def __str__(self):
        return f"{self.text[:50]}... | Level: {self.level}"