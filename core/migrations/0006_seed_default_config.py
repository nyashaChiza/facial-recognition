from django.db import migrations


def create_default_config(apps, schema_editor):
    Config = apps.get_model('core', 'Config')
    if not Config.objects.exists():
        Config.objects.create()


def remove_default_config(apps, schema_editor):
    Config = apps.get_model('core', 'Config')
    Config.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_rename_points_config_maximum_points_threshold'),
    ]

    operations = [
        migrations.RunPython(create_default_config, remove_default_config),
    ]
