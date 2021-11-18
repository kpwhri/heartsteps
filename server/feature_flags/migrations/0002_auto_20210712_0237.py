# Generated by Django 3.1.7 on 2021-07-12 02:37

from feature_flags.models import FeatureFlags
from django.db import migrations
from django.conf import settings

def apply_feature_flags_to_existing_users(apps, schema_editor):
    """
    Creates new FeatureFlags model instance for every existing user that doesn't currently have one
    """
    User = apps.get_model(settings.AUTH_USER_MODEL)
    FeatureFlags = apps.get_model('feature_flags', 'FeatureFlags')
    new_feature_flag_objects = [FeatureFlags(user=user) for user in User.objects.filter(featureflags=None)]
    FeatureFlags.objects.bulk_create(new_feature_flag_objects)

class Migration(migrations.Migration):

    dependencies = [
        ('feature_flags', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(apply_feature_flags_to_existing_users),
    ]
