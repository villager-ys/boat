# Generated by Django 2.2.6 on 2019-10-14 07:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('playbookMode', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='playbook',
            options={'ordering': ['-create_time']},
        ),
        migrations.AddField(
            model_name='playbook',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='playbook',
            name='update_time',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='playbook',
            name='playbook_content',
            field=models.FileField(upload_to='.'),
        ),
    ]
