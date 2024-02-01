# Generated by Django 3.0.5 on 2024-02-01 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0008_userquizprogress'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='time_limit_minutes',
        ),
        migrations.AlterField(
            model_name='question',
            name='skip',
            field=models.CharField(max_length=200, verbose_name='Skip'),
        ),
        migrations.DeleteModel(
            name='UserQuizProgress',
        ),
    ]
