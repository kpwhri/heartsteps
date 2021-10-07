# Generated by Django 3.1.7 on 2021-10-07 04:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fitbit_activities', '0010_delete_fbmhr'),
    ]

    operations = [
        migrations.RunSQL(sql="CREATE EXTENSION pgcrypto;", reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="CREATE TABLE fitbit_activities_fitbitminuteheartrate AS SELECT gen_random_uuid() as id, account_id, time, heart_rate from fitbit_activities_fitbitminuteheartrate_backup;", reverse_sql=migrations.RunSQL.noop),
    ]
