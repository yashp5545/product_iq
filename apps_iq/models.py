from django.db import models

# Create your models here.
class App(models.Model):
    app_name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    app_theme_color = models.CharField(max_length=50)
    app_logo = models.ImageField(upload_to='app_logos/')  # Assuming app logos are uploaded to a directory

    def __str__(self):
        return self.app_name