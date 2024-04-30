# Generated by Django 5.0.4 on 2024-04-30 12:38

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('department', '0019_alter_customtoken_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='leave',
            name='percentage_of_salary',
            field=models.FloatField(default=1.0),
        ),
        migrations.AlterField(
            model_name='customtoken',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 4, 30, 12, 38, 32, 807272)),
        ),
        migrations.AlterField(
            model_name='leave',
            name='EmployeeName',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='leaves_requested', to='department.customuser'),
            preserve_default=False,
        ),
    ]
