# Generated by Django 5.0.7 on 2024-08-08 05:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='evento',
            options={'ordering': ['data']},
        ),
    ]