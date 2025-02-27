# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-08-29 11:09


from django.db import migrations, models


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    CardXNodeXWidget = apps.get_model("models", "CardXNodeXWidget")
    CardModel = apps.get_model("models", "CardModel")

    for card in CardModel.objects.all():
        cnw = CardXNodeXWidget.objects.filter(card=card)[1:]
        for item in cnw:
            item.delete()


def reverse_func(apps, schema_editor):
    # there is no way to reverse this
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("models", "3965_cardxnodexwidget_visible"),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
