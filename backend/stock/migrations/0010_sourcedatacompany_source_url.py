# Generated by Django 3.2.3 on 2021-06-18 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0009_alter_sourcedatacompany_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='sourcedatacompany',
            name='source_url',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Ссылка на источник данных'),
        ),
    ]
