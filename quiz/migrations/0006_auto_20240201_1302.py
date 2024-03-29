# Generated by Django 3.0.5 on 2024-02-01 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0005_auto_20201209_2125'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='skip',
            field=models.CharField(blank=True, max_length=200, verbose_name='Skip'),
        ),
        migrations.AddField(
            model_name='question',
            name='time_limit_minutes',
            field=models.PositiveIntegerField(default=5),
        ),
        migrations.AlterField(
            model_name='question',
            name='answer',
            field=models.CharField(choices=[('Option1', 'Option1'), ('Option2', 'Option2'), ('Option3', 'Option3'), ('Option4', 'Option4'), ('Skip', 'Skip')], max_length=200),
        ),
    ]
