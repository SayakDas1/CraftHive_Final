# Generated by Django 4.1.5 on 2023-05-01 18:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0007_alter_auctionproduct_end_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionproduct',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 2, 0, 19, 36, 474246)),
        ),
        migrations.AlterField(
            model_name='auctionproduct',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 2, 0, 19, 36, 474246)),
        ),
    ]