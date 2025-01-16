from django.db import models

class ImageUpload(models.Model):  # Corrected 'MOdel' to 'Model'
    image1 = models.ImageField(upload_to='uploads/')
    image2 = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
