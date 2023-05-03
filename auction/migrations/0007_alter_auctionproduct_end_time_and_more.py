# Generated by Django 4.1.7 on 2023-05-01 14:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auction', '0006_auctionproduct_graph_alter_auctionproduct_end_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionproduct',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 1, 20, 0, 28, 861003)),
        ),
        migrations.AlterField(
            model_name='auctionproduct',
            name='graph',
            field=models.CharField(default='{y:prod_price}', max_length=1000),
        ),
        migrations.AlterField(
            model_name='auctionproduct',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 5, 1, 20, 0, 28, 861003)),
        ),
    ]
