# Generated by Django 4.1.5 on 2023-04-15 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='rate',
            field=models.IntegerField(default=0),
        ),
        migrations.DeleteModel(
            name='Review',
        ),
    ]
