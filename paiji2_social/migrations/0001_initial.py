# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('backbone_calendar', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bureau',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('createdDate', models.DateTimeField(auto_now_add=True, verbose_name='tenure beginning date')),
                ('endDate', models.DateTimeField(null=True, verbose_name='tenure end date', blank=True)),
            ],
            options={
                'ordering': ('group__category', 'group__name', '-createdDate'),
                'verbose_name': 'Bureau',
                'verbose_name_plural': 'Bureaux',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pubDate', models.DateTimeField(verbose_name='publication date')),
                ('content', models.CharField(max_length=140, verbose_name='content')),
                ('author', models.ForeignKey(related_name='comment', verbose_name='author', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('message', '-pubDate'),
                'verbose_name': 'comment',
                'verbose_name_plural': 'comments',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='name')),
                ('slug', models.SlugField()),
                ('createdOn', models.DateTimeField(auto_now_add=True, verbose_name='creation date')),
                ('deletedOn', models.DateTimeField(null=True, verbose_name='deletion date', blank=True)),
                ('logo', models.ImageField(upload_to=b'groups/logo', null=True, verbose_name='logo')),
                ('newsfeed', models.URLField(verbose_name='newsfeed', blank=True)),
                ('calendar', models.OneToOneField(related_name='group', null=True, verbose_name='calendar', to='backbone_calendar.Calendar')),
            ],
            options={
                'verbose_name': 'group',
                'verbose_name_plural': 'groups',
            },
        ),
        migrations.CreateModel(
            name='GroupCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='name')),
            ],
            options={
                'verbose_name': 'group category',
                'verbose_name_plural': 'group categories',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pubDate', models.DateTimeField(auto_now_add=True, verbose_name='publication date')),
                ('title', models.CharField(max_length=140, verbose_name='title')),
                ('content', models.TextField(verbose_name='content')),
                ('public', models.BooleanField(default=False, verbose_name='readable by unregistered visitors')),
                ('importance', models.IntegerField(default=0, verbose_name='importance level', choices=[(0, 'Normal'), (1, 'Priority')])),
                ('author', models.ForeignKey(related_name='message', verbose_name='author', to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(verbose_name='group', to='paiji2_social.Group')),
            ],
            options={
                'ordering': ('group__name', '-pubDate'),
                'verbose_name': 'message',
                'verbose_name_plural': 'messages',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('bureau', models.ForeignKey(related_name='members', verbose_name='Bureau', to='paiji2_social.Bureau')),
            ],
            options={
                'verbose_name': 'post',
                'verbose_name_plural': 'posts',
            },
        ),
        migrations.CreateModel(
            name='PostType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=50, verbose_name='description')),
            ],
            options={
                'verbose_name': 'post type',
                'verbose_name_plural': 'post types',
            },
        ),
        migrations.AddField(
            model_name='post',
            name='postType',
            field=models.ForeignKey(verbose_name='post type', to='paiji2_social.PostType'),
        ),
        migrations.AddField(
            model_name='post',
            name='utilisateur',
            field=models.ForeignKey(related_name='posts', verbose_name='user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='group',
            name='category',
            field=models.ForeignKey(verbose_name='category', to='paiji2_social.GroupCategory'),
        ),
        migrations.AddField(
            model_name='comment',
            name='message',
            field=models.ForeignKey(related_name='comment', verbose_name='message', to='paiji2_social.Message'),
        ),
        migrations.AddField(
            model_name='bureau',
            name='group',
            field=models.ForeignKey(related_name='bureaus', verbose_name='group', to='paiji2_social.Group'),
        ),
        migrations.AlterUniqueTogether(
            name='post',
            unique_together=set([('bureau', 'postType')]),
        ),
    ]
