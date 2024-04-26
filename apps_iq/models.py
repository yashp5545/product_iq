from django.db import models
from django.contrib.postgres.fields import ArrayField

from users.models import User


# Create your models here.
class App(models.Model):
    app_name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    app_theme_color = models.CharField(max_length=50)
    # Assuming app logos are uploaded to a directory
    app_logo = models.ImageField(upload_to='app_logos/')

    def __str__(self):
        return self.app_name

    class Meta:
        verbose_name = "App"


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

    class Meta:
        verbose_name = "Product coach module"


class Challenge(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    active = models.BooleanField(default=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product coach challenge"


class Level(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    active = models.BooleanField(default=True)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)

    use_model_lebel_prompt = models.BooleanField(default=False)
    lebel_prompt = models.TextField(default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product coach lebel"


class LevelResponses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    answer = models.TextField()
    evalution_result = models.IntegerField()
    result = models.JSONField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ' - ' + self.level.name

    class Meta:
        verbose_name = "Product coach lebel Response"


class Categories(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    active = models.BooleanField(default=True)

    app = models.ForeignKey(App, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product worktools Categorie"


class Skill(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    active = models.BooleanField(default=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    tags = ArrayField(models.CharField(max_length=200),
                      blank=True, default=list)

    question_suggestion = models.JSONField()

    skill_prompt = models.TextField(default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product worktools Skill"


class SkillResponses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    answer = models.JSONField()

    class Meta:
        verbose_name = " Product worktools Responce"


class Section(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    app = models.ForeignKey(App, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product IQ section"


class Topic(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product IQ topic"


class Lession(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    active = models.BooleanField(default=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product IQ lession"
