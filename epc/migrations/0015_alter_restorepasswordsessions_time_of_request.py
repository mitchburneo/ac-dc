# Generated by Django 3.2.8 on 2022-01-16 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epc', '0014_auto_20211227_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restorepasswordsessions',
            name='time_of_request',
            field=models.IntegerField(default=1642375136),
        ),
    ]