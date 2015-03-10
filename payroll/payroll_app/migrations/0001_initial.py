# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(unique=True, max_length=255, verbose_name=b'email address')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BonusPay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bonus_id', models.CharField(max_length=100)),
                ('employee_id', models.CharField(max_length=100)),
                ('amount', models.CharField(max_length=100)),
                ('pay_start', models.DateTimeField()),
                ('pay_end', models.DateTimeField()),
                ('date_given', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('employee_id', models.CharField(max_length=100)),
                ('employer_id', models.CharField(max_length=100)),
                ('employee_name', models.CharField(max_length=100)),
                ('vacation_hours', models.DecimalField(max_digits=8, decimal_places=2)),
                ('vacation_pay_rate', models.DecimalField(max_digits=8, decimal_places=2)),
                ('sick_hours', models.DecimalField(max_digits=8, decimal_places=2)),
                ('sick_pay_rate', models.DecimalField(max_digits=8, decimal_places=2)),
                ('vacation_accrual_rate', models.DecimalField(max_digits=8, decimal_places=2)),
                ('address', models.CharField(max_length=300)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Employer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('employer_id', models.CharField(max_length=100)),
                ('employer_name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=100)),
                ('pay_start', models.DateTimeField()),
                ('pay_end', models.DateTimeField()),
                ('hash_key', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('job_id', models.CharField(max_length=100)),
                ('employee_id', models.CharField(max_length=100)),
                ('base_rate', models.DecimalField(max_digits=8, decimal_places=2)),
                ('incremental_hours_1', models.DecimalField(max_digits=8, decimal_places=2)),
                ('incremental_hours_2', models.DecimalField(max_digits=8, decimal_places=2)),
                ('job_title', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PayPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('employee_id', models.CharField(max_length=100)),
                ('job_id', models.CharField(max_length=100)),
                ('pay_start', models.DateTimeField()),
                ('pay_end', models.DateTimeField()),
                ('hours', models.DecimalField(max_digits=8, decimal_places=2)),
                ('overtime_hours', models.DecimalField(max_digits=8, decimal_places=2)),
                ('incremental_hours_1', models.DecimalField(max_digits=8, decimal_places=2)),
                ('incremental_hours_1_and_2', models.DecimalField(max_digits=8, decimal_places=2)),
                ('incremental_hours_2', models.DecimalField(max_digits=8, decimal_places=2)),
                ('holiday_hours', models.DecimalField(max_digits=8, decimal_places=2)),
                ('sick_hours', models.DecimalField(max_digits=8, decimal_places=2)),
                ('vacation_hours', models.DecimalField(max_digits=8, decimal_places=2)),
                ('holiday_hours_spent', models.DecimalField(max_digits=8, decimal_places=2)),
                ('sick_hours_spent', models.DecimalField(max_digits=8, decimal_places=2)),
                ('vacation_hours_spent', models.DecimalField(max_digits=8, decimal_places=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
