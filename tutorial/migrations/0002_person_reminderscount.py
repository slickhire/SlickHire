# Generated by Django 3.0.5 on 2020-05-01 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorial', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='reminderscount',
            field=models.CharField(default=0, max_length=30),
            preserve_default=False,
        ),
    ]
