# Generated by Django 3.2.8 on 2021-12-27 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epc', '0012_auto_20211216_2358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='m2mpartgrouptopart',
            name='info',
            field=models.CharField(max_length=1024),
        ),
        migrations.AlterField(
            model_name='restorepasswordsessions',
            name='time_of_request',
            field=models.IntegerField(default=1640604448),
        ),
    ]