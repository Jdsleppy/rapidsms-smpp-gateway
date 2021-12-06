# Generated by Django 2.2.24 on 2021-12-06 15:55

import django.db.models.deletion

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rapidsms", "0004_auto_20150801_2138"),
        ("smpp_gateway", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="momessage",
            options={"verbose_name": "mobile-originated message"},
        ),
        migrations.AlterModelOptions(
            name="mtmessage",
            options={"verbose_name": "mobile-terminated message"},
        ),
        migrations.CreateModel(
            name="MTMessageStatus",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("create_time", models.DateTimeField()),
                ("modify_time", models.DateTimeField()),
                ("sequence_number", models.IntegerField()),
                ("command_status", models.IntegerField(null=True)),
                (
                    "message_id",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                ("delivery_report", models.BinaryField(null=True)),
                (
                    "backend",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="rapidsms.Backend",
                    ),
                ),
                (
                    "mt_message",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="smpp_gateway.MTMessage",
                    ),
                ),
            ],
            options={
                "verbose_name": "mobile-terminated message status",
            },
        ),
        migrations.AddConstraint(
            model_name="mtmessagestatus",
            constraint=models.UniqueConstraint(
                fields=("backend", "sequence_number"), name="unique_seq_num"
            ),
        ),
    ]
