
from django.db import models
from inventory.models import Complaint


class ComplaintAnalysis(models.Model):
    complaint = models.OneToOneField(Complaint, on_delete=models.CASCADE, related_name="nlp_analysis")
    processed_text = models.TextField(blank=True)
    tokens = models.JSONField(default=list, blank=True)
    pos_tags = models.JSONField(default=list, blank=True)
    tfidf_terms = models.JSONField(default=list, blank=True)
    sentiment = models.CharField(max_length=20, blank=True)
    positive_score = models.FloatField(default=0)
    negative_score = models.FloatField(default=0)
    neutral_score = models.FloatField(default=0)
    compound_score = models.FloatField(default=0)
    category = models.CharField(max_length=50, default="Other")
    analyzed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analysis - Complaint {self.complaint_id}"
