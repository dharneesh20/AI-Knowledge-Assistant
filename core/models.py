from django.db import models
from django.contrib.auth.models import User


class Document(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/")
    file_type = models.CharField(max_length=50, blank=True)
    size_bytes = models.BigIntegerField(default=0)

    # indexing status
    is_indexed = models.BooleanField(default=False)
    chunks_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"
    
class DocumentChunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    content = models.TextField()
    chunk_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class Meta:
        unique_together = ("document", "chunk_index")
        indexes = [
            models.Index(fields=["document", "chunk_index"]),
        ]


class QueryLog(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="query_logs")
    query = models.TextField()
    top_k = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)


class Feedback(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feedbacks")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
