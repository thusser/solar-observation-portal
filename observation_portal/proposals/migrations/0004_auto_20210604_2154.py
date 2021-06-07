# Generated by Django 2.2.18 on 2021-06-04 21:54

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0003_auto_20210203_0022'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='timeallocation',
            name='unique_proposal_timeallocation',
        ),
        migrations.AddField(
            model_name='timeallocation',
            name='instrument_types',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), default=[], help_text='One or more instrument_types to share this time allocation', size=None),
        ),
        migrations.AddConstraint(
            model_name='timeallocation',
            constraint=models.UniqueConstraint(fields=('semester', 'proposal', 'instrument_types'), name='unique_proposal_semester_instrument_type_ta'),
        ),
    ]
