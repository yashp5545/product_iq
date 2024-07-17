from django.db import models
from django.contrib.postgres.fields import ArrayField
from enum import Enum
from users.models import User

LEN_MAX = 400


class AppType(Enum):
    MODULES = "modules"
    WORKTOOLS = "worktools"
    PRODUCTIQ = 'productiq'
    
# Create your models here.
class App(models.Model):
    
    app_name = models.CharField(max_length=LEN_MAX)
    description = models.TextField()
    # price = models.DecimalField(max_digits=10, decimal_places=2)
    app_theme_color = models.CharField(max_length=50)
    # Assuming app logos are uploaded to a directory
    app_logo = models.ImageField(upload_to='app_logos/')
    order_of_display = models.IntegerField()
    app_type = models.CharField(max_length=20, choices=[
                            (tag.value, tag.value) for tag in AppType])
    
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.app_name

    class Meta:
        verbose_name = "App"

class productrole(Enum):
    Aspiring_Product_Manager = "Aspiring Product Manager"
    Associate_Product_Manager = "Associate Product Manager"
    Product_Manager = "Product Manager"
    Senior_Product_Manager = "Senior Product Manager"
    Director_of_Product_Management = "Director of Product Management"
    Head_of_Product = "Head of Product"
    Vice_President_of_Product = "Vice President of Product"
    Chief_Product_Officer = "Chief Product Officer"
    Entrepreneur = "Entrepreneur"

class Module(models.Model):
    name = models.CharField(max_length=LEN_MAX)
    description = models.TextField()
    active = models.BooleanField(default=True)
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    subscription_required = models.BooleanField(default=True)
    order_of_display = models.IntegerField()
    product_role = models.CharField(max_length=60, choices=[
                            (tag.value, tag.value) for tag in productrole],default=productrole.Product_Manager.value)
    module_prompt = models.TextField(default='')
    # lebel_prompt = models.TextField(default='')
    master_prompt = models.TextField(default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product_Coach_Module"

class ExperienceTag(Enum):
    Aspiring_Product_Manager = "Aspiring Product Manager"
    Associate_Product_Manager = "Associate Product Manager"
    Product_Manager = "Product Manager"
    Senior_Product_Manager = "Senior Product Manager"
    Director_of_Product_Management = "Director of Product Management"
    Head_of_Product = "Head of Product"
    Vice_President_of_Product = "Vice President of Product"
    Chief_Product_Officer = "Chief Product Officer"
    Entrepreneur = "Entrepreneur"


class Challenge(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    active = models.BooleanField(default=True)
    order_of_display = models.IntegerField()
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    challenge_prompt = models.CharField(max_length=300)
    user_role = models.CharField(max_length=60, choices=[
                            (tag.value, tag.value) for tag in ExperienceTag])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product_Coach_Challenge"

    def save(self, *args, **kwargs):
        if self.user_role:
            self.challenge_experience_tag = self.user_role
        super().save(*args, **kwargs)


class Level(models.Model):
    name = models.CharField(max_length=LEN_MAX)
    description = models.TextField(verbose_name="level_question")
    active = models.BooleanField(default=True)
    order_of_display = models.IntegerField()
    company_logo = models.ImageField(upload_to='company_logos/') 
    deep_link_iq = models.CharField(max_length=LEN_MAX, verbose_name="sampleanswer")
    level_hint = models.CharField(max_length=LEN_MAX, verbose_name="level_hint")
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    topics = models.ManyToManyField('Topic')
    # use_model_lebel_prompt = models.BooleanField(default=True)
    lebel_prompt = models.TextField(default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product_Coach_Level"


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
        verbose_name = "Product_Coach_Level_Response"


class Categories(models.Model):
    name = models.CharField(max_length=LEN_MAX)
    description = models.TextField()
    active = models.BooleanField(default=True)

    app = models.ForeignKey(App, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product_Worktools_Categorie"


class Skill(models.Model):
    name = models.CharField(max_length=LEN_MAX)
    description = models.TextField()
    active = models.BooleanField(default=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    tags = ArrayField(models.CharField(max_length=200),
                      blank=True, default=list)
    subscription_required = models.BooleanField(default=True)

    # question_suggestion = models.JSONField()

    skill_prompt = models.TextField(default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product_Worktools_Skill"


class FromInputType(Enum):
    TEXT = "text"
    TEXTAREA = "textarea"


class Question(models.Model):
    name = models.CharField(max_length=100, verbose_name="field_value")
    # label = models.CharField(max_length=100)
    placeholder = models.CharField(max_length=500)
    type = models.CharField(max_length=20, choices=[
                            (tag.value, tag.value) for tag in FromInputType])
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    class Meta():
        verbose_name = "Product_Worktools_Field"


class SkillResponses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    answer = models.JSONField()
    result = models.JSONField()

    class Meta:
        verbose_name = " Product_Worktools_Response"


class Section(models.Model):
    name = models.CharField(max_length=LEN_MAX)
    active = models.BooleanField(default=True)
    app = models.ForeignKey(App, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product_IQ_section"


class Topic(models.Model):
    name = models.CharField(max_length=LEN_MAX)
    active = models.BooleanField(default=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    subscription_required = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product_IQ_Topic"


class Lession(models.Model):
    name = models.CharField(max_length=LEN_MAX)
    description = models.TextField()
    active = models.BooleanField(default=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product_IQ_Lesson"
