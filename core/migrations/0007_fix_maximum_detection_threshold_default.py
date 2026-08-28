from django.db import migrations, models

OLD_DEFAULT = 99
NEW_DEFAULT = 40


def update_existing_default_rows(apps, schema_editor):
    Config = apps.get_model('core', 'Config')
    # Only touch rows still at the old default - never clobber a value an
    # admin actually chose via the config-update form.
    Config.objects.filter(maximum_detection_threshold=OLD_DEFAULT).update(
        maximum_detection_threshold=NEW_DEFAULT
    )


def revert_existing_default_rows(apps, schema_editor):
    Config = apps.get_model('core', 'Config')
    Config.objects.filter(maximum_detection_threshold=NEW_DEFAULT).update(
        maximum_detection_threshold=OLD_DEFAULT
    )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_seed_default_config'),
    ]

    operations = [
        migrations.AlterField(
            model_name='config',
            name='maximum_detection_threshold',
            field=models.IntegerField(default=NEW_DEFAULT),
        ),
        migrations.RunPython(update_existing_default_rows, revert_existing_default_rows),
    ]
