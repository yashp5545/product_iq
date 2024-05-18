from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin


from enum import Enum


class PRODUCT_EXP_CHOICES(Enum):
    BEGINNER = 'Beginner'
    INTERMEDIATE = 'Intermediate'
    ADVANCED = 'Advanced'


class CustomUserManager(BaseUserManager):
    def __create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        print(user)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    product_exp = models.CharField(max_length=200, choices=[(
        tag.value, tag.value) for tag in PRODUCT_EXP_CHOICES], default=PRODUCT_EXP_CHOICES.BEGINNER.value)
    password = models.CharField(max_length=128)

    name = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    job_title = models.CharField(max_length=50, blank=True)
    company_or_institiution = models.CharField(max_length=50, blank=True)
    
    refered_by = models.ForeignKey(default=None, null= True, blank=True, on_delete= models.SET_NULL, to="User")
    referral_ct = models.IntegerField(default=0)
    number_of_discounts = models.IntegerField(default=0)
    given_reward_to_referer = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    last_login = models.DateTimeField(auto_now=True, blank=True, null=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return f"{self.username} - {self.email} - {self.product_exp}"

    def reduce_number_of_discount(self, num: int):
        if(self.number_of_discounts - num > 0):
            self.number_of_discounts -= num
        else:
            self.number_of_discounts = 0
        self.save()
