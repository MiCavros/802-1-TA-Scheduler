# Generated by Django 5.1.3 on 2024-12-09 05:34

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TA_Scheduler', '0002_class_assignments_class_schedule_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='class',
            name='instructor',
        ),
        migrations.RemoveField(
            model_name='userprivateinfo',
            name='address',
        ),
        migrations.RemoveField(
            model_name='userprivateinfo',
            name='userID',
        ),
        migrations.RemoveField(
            model_name='userpublicinfo',
            name='userID',
        ),
        migrations.AddField(
            model_name='section',
            name='section_name',
            field=models.CharField(default='Default Section', max_length=100),
        ),
        migrations.AddField(
            model_name='userprivateinfo',
            name='dob',
            field=models.DateField(default=datetime.date(2000, 1, 1)),
        ),
        migrations.AddField(
            model_name='userprivateinfo',
            name='user',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='TA_Scheduler.user'),
        ),
        migrations.AddField(
            model_name='userpublicinfo',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='userpublicinfo',
            name='email',
            field=models.EmailField(default='example@uwm.edu', max_length=254),
        ),
        migrations.AddField(
            model_name='userpublicinfo',
            name='phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='userpublicinfo',
            name='user',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='TA_Scheduler.user'),
        ),
        migrations.AlterField(
            model_name='class',
            name='assignments',
            field=models.TextField(default='No assignments'),
        ),
        migrations.AlterField(
            model_name='class',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='class',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='class',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='class',
            name='schedule',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='class',
            name='title',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='section',
            name='TA',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TA_Scheduler.user'),
        ),
        migrations.AlterField(
            model_name='section',
            name='classId',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TA_Scheduler.class'),
        ),
        migrations.AlterField(
            model_name='section',
            name='max_capacity',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='section',
            name='schedule',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='MidInit',
            field=models.CharField(blank=True, max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='userType',
            field=models.CharField(max_length=20),
        ),
    ]