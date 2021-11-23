# Generated by Django 2.2.13 on 2021-03-19 20:17
from arches.app.models.fields.i18n import I18n_JSONField
from django.db import migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("models", "7801_i18n_boolean_datatype"),
    ]

    sql = """
        UPDATE public.cards_x_nodes_x_widgets
        SET config = config ||
        jsonb_set(
            jsonb_set(
                jsonb_set(
                    config, '{{label}}', json_build_object('{0}', config->>'label')::jsonb, true),
            '{{placeholder}}', json_build_object('{0}', config->>'placeholder')::jsonb, true),
        '{{defaultValue}}', json_build_object('{0}', config->>'defaultValue')::jsonb, true) ||
        '{{"i18n_properties": ["label", "placeholder", "defaultValue"]}}'
        WHERE nodeid in (SELECT nodeid FROM nodes WHERE datatype = 'string');

        UPDATE public.widgets
        SET defaultconfig = defaultconfig ||
        '{{"i18n_properties": ["placeholder", "defaultValue"]}}'
        WHERE datatype = 'string';
    """.format(
        settings.LANGUAGE_CODE
    )

    reverse_sql = """
        UPDATE public.cards_x_nodes_x_widgets
        SET config = config - 'i18n_properties' ||
        json_build_object('label', jsonb_extract_path(config, 'label', '{0}'))::jsonb ||
        json_build_object('placeholder', jsonb_extract_path(config, 'placeholder', '{0}'))::jsonb ||
        json_build_object('defaultValue', jsonb_extract_path(config, 'defaultValue', '{0}'))::jsonb
        WHERE nodeid in (SELECT nodeid FROM nodes WHERE datatype = 'string');

        UPDATE public.widgets
        SET defaultconfig = defaultconfig - 'i18n_properties' ||
        WHERE datatype = 'string';
    """.format(
        settings.LANGUAGE_CODE
    )

    operations = [
        migrations.RunSQL(sql, reverse_sql),
        migrations.AlterField(
            model_name="cardxnodexwidget",
            name="config",
            field=I18n_JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="widget",
            name="defaultconfig",
            field=I18n_JSONField(blank=True, null=True),
        ),
    ]
