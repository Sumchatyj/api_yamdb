# Generated by Django 2.2.16 on 2022-05-11 20:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_auto_20220510_1942'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='title_id',
            new_name='title',
        ),
    ]