# Generated by Django 2.1.4 on 2018-12-23 17:40

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('randomizer', '0003_text_version_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='seed',
            name='file_select_char',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='seed',
            name='file_select_hash',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='seed',
            name='flags',
            field=jsonfield.fields.JSONField(),
        ),
        migrations.AlterField(
            model_name='seed',
            name='mode',
            field=models.CharField(choices=[('standard', 'Standard'), ('open', 'Open')], max_length=16),
        ),
    ]
