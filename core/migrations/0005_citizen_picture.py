# Generated by Django 5.0.1 on 2024-03-16 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_incident_incident_date_alter_citizenimage_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='citizen',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='citizen/images/'),
        ),
    ]