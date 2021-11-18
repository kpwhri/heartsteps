# Generated by Django 3.1.7 on 2021-10-07 05:17

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('fitbit_activities', '0011_convert_fbmhr'),
    ]

    operations = [
        migrations.RunSQL(sql="""
                          ALTER TABLE "fitbit_activities_fitbitminuteheartrate" ALTER COLUMN "id" TYPE uuid USING "id"::uuid;
                          """, reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="""
                    ALTER TABLE "fitbit_activities_fitbitminuteheartrate" ALTER COLUMN "time" SET NOT NULL;
                    """, reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="""
                    ALTER TABLE "fitbit_activities_fitbitminuteheartrate" ALTER COLUMN "heart_rate" SET NOT NULL;
                    """, reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="""
                    ALTER TABLE "fitbit_activities_fitbitminuteheartrate" ALTER COLUMN "account_id" SET NOT NULL;
                    """, reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="""
                    ALTER TABLE fitbit_activities_fitbitminuteheartrate ADD CONSTRAINT fitbit_activities_fitbitminuteheartrate_pkey_new PRIMARY KEY (id);
                    """, reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="""
                    CREATE INDEX fitbit_activities_fitbit_account_id_new_like ON fitbit_activities_fitbitminuteheartrate USING btree (account_id varchar_pattern_ops);
                    """, reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="""
                    CREATE INDEX fitbit_activities_fitbitminuteheartrate_account_id_new ON fitbit_activities_fitbitminuteheartrate USING btree (account_id);
                    """, reverse_sql=migrations.RunSQL.noop),
        migrations.RunSQL(sql="""
                    ALTER TABLE fitbit_activities_fitbitminuteheartrate ADD CONSTRAINT fitbit_activities_fi_account_id_new_fk_fitbit_ap FOREIGN KEY (account_id) REFERENCES fitbit_api_fitbitaccount(uuid) DEFERRABLE INITIALLY DEFERRED;
                    """, reverse_sql=migrations.RunSQL.noop),
    ]
