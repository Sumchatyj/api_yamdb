# Generated by Django 2.2.16 on 2022-05-15 16:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_auto_20220515_1741'),
    ]

    operations = [
        migrations.RenameField(
            model_name='title',
            old_name='gerne',
            new_name='genre',
        ),
        migrations.AlterField(
            model_name='genretitle',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='genres', to='reviews.Title'),
        ),
    ]