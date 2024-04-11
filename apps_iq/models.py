from django.db import models

from users.models import User

# Create your models here.
class App(models.Model):
    app_name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    app_theme_color = models.CharField(max_length=50)
    app_logo = models.ImageField(upload_to='app_logos/')  # Assuming app logos are uploaded to a directory

    def __str__(self):
        return self.app_name
    

class Module(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    active = models.BooleanField(default=True)
    app = models.ForeignKey(App, on_delete=models.CASCADE)

    module_prompt = models.TextField(default='')
    lebel_prompt = models.TextField(default='')
    master_prompt = models.TextField(default='')

    def __str__(self):
        return self.name
    
class Challenge(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    active = models.BooleanField(default=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class Level(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    active = models.BooleanField(default=True)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)

    use_model_lebel_prompt = models.BooleanField(default=True)
    lebel_prompt = models.TextField(default='')

    def __str__(self):
        return self.name
    
class LevelResponses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    answer = models.TextField()
    evalution_result = models.IntegerField()
    result = models.JSONField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ' - ' + self.level.name