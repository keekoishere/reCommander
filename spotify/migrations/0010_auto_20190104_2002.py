# Generated by Django 2.1.2 on 2019-01-04 20:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spotify', '0009_username_historyperm'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recommend',
            old_name='publico',
            new_name='top',
        ),
    ]
