# Generated by Django 4.1.7 on 2023-04-14 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_alter_product_pub_date_alter_product_seller_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='rating',
            field=models.IntegerField(default=0),
        ),
    ]
