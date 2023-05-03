# Generated by Django 4.1.7 on 2023-04-30 11:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0002_alter_auctionproduct_end_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionproduct',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 4, 30, 17, 7, 0, 966601)),
        ),
        migrations.AlterField(
            model_name='auctionproduct',
            name='prod_image',
            field=models.ImageField(default='something.img', upload_to='auction/'),
        ),
        migrations.AlterField(
            model_name='auctionproduct',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 4, 30, 17, 7, 0, 966601)),
        ),
    ]