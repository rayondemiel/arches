# Generated by Django 2.2.13 on 2021-03-19 20:17
from arches.app.models.fields.i18n import I18n_TextField
from django.db import migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("models", "7792_i18n_widgets"),
    ]

    sql = """
        SET CONSTRAINTS ALL IMMEDIATE;
        UPDATE public.graphs SET name=json_build_object('{0}', name);
        UPDATE public.graphs SET description=json_build_object('{0}', description);
        UPDATE public.graphs SET subtitle=json_build_object('{0}', subtitle);
        SET CONSTRAINTS ALL DEFERRED;
    """.format(
        settings.LANGUAGE_CODE
    )

    reverse_sql = """
        UPDATE public.graphs SET name=name::jsonb->>'{0}'::text;
        UPDATE public.graphs SET description=description::jsonb->>'{0}'::text;
        UPDATE public.graphs SET subtitle=subtitle::jsonb->>'{0}'::text;
    """.format(
        settings.LANGUAGE_CODE
    )

    operations = [
        migrations.RunSQL(sql, reverse_sql),
        migrations.AlterField(
            model_name="graphmodel",
            name="name",
            field=I18n_TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="graphmodel",
            name="description",
            field=I18n_TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="graphmodel",
            name="subtitle",
            field=I18n_TextField(blank=True, null=True),
        ),
    ]
