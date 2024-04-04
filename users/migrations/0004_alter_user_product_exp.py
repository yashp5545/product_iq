# Generated by Django 5.0.3 on 2024-04-04 01:33

import users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_last_login'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='product_exp',
            field=models.CharField(choices=[(users.models.PRODUCT_EXP_CHOICES['BEGINNER'], 'Beginner'), (users.models.PRODUCT_EXP_CHOICES['INTERMEDIATE'], 'Intermediate'), (users.models.PRODUCT_EXP_CHOICES['ADVANCED'], 'Advanced')], default='Beginner', max_length=200),
        ),
    ]