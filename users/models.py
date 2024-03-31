from django.db import models

# Create your models here.
class User(models.Model):
    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    EXPERT = 'expert'

    PRODUCT_EXP_CHOICES = [
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (EXPERT, 'Expert'),
    ]

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    product_exp = models.CharField(max_length=20, choices=PRODUCT_EXP_CHOICES)

    def __str__(self):
        return self.username
    