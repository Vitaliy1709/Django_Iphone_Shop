# Generated by Django 3.1.5 on 2021-02-03 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_auto_20210202_1247'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='shot_description',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
