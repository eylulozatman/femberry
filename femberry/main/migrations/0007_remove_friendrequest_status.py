# Generated by Django 5.0.6 on 2024-08-12 16:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_userpref'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='friendrequest',
            name='status',
        ),
    ]
