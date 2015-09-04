# -*- encoding: utf-8 -*-
import os
from django.test import TestCase
from htmlvalidator.client import ValidatingClient
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.conf import settings
from django.core.files import File

from backbone_calendar.models import Calendar
from . import models


User = get_user_model()


class BaseTestCase(TestCase):

    def setUp(self):

        self.client = ValidatingClient()

        self.brunehilde = User.objects.create_user(
            'brunehilde',
            password='brunehilde_password',
        )

        self.gontran = User.objects.create_user(
            'gontran',
            password='gontran_password',
        )

        self.president = models.PostType.objects.create(
            description='president',
        )

        self.director = models.PostType.objects.create(
            description='director',
        )

        self.normal_groups = models.GroupCategory.objects.create(
            name='normal groups',
        )

        self.logo = File(open(os.path.join(
                        settings.BASE_DIR,
                        'logo.gif',
                    )
        ))

        self.calendar = Calendar.objects.create(
            name='mybestcalendar',
            slug='mybestcalendarslug',
        )

        self.best_group = models.Group.objects.create(
            name='the best group',
            slug='slugbestgroup',
            category=self.normal_groups,
            createdOn=timezone.now(),
            deletedOn=None,
            logo=self.logo,
            newsfeed='mynewsurl',
            calendar=self.calendar,
        )

        self.my_bureau = models.Bureau.objects.create(
            createdDate=timezone.now(),
            endDate=None,
            group=self.best_group,
        )

        self.gontran_post = models.Post.objects.create(
            utilisateur=self.gontran,
            bureau=self.my_bureau,
            description='the best one',
            postType=self.president,
        )

        self.brunehilde_post = models.Post.objects.create(
            utilisateur=self.brunehilde,
            bureau=self.my_bureau,
            description='the best one too',
            postType=self.director,
        )

        self.first_message = models.Message.objects.create(
            author=self.brunehilde,
            pubDate=timezone.now(),
            title='Welcome my friends !',
            content="""Hello everybody !

                This is the first message published !

                Thank you !
                """,
            public=True,
            group=self.best_group,
            importance=0,
        )

        self.second_message = models.Message.objects.create(
            author=self.gontran,
            pubDate=timezone.now(),
            title='Welcome my old friends ! &®',
            content="""Hi everybody !

                http://www.perdu.com

                This is the second message published !

                Thank you !
                """,
            public=False,
            group=self.best_group,
            importance=1,
        )

        self.first_comment = models.Comment.objects.create(
            author=self.gontran,
            message=self.first_message,
            pubDate=timezone.now(),
            content='Well ! <a href="http://perdu.com">[lien]</a> good job !',
        )

        self.second_comment = models.Comment.objects.create(
            author=self.brunehilde,
            message=self.first_message,
            pubDate=timezone.now(),
            content='<br/> ftp://lgdubois.rez Thank you Gontran ! ®',
        )

        self.third_comment = models.Comment.objects.create(
            author=self.gontran,
            message=self.second_message,
            pubDate=timezone.now(),
            content='third one<<ul>> aura»«épcuui..,ac.ànqikuoc(',
        )


class PagesTestCase(BaseTestCase):

    def test_permissions(self):
        # Unauthenticated user

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('directory'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('directory') + '?q=gont')
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('groups'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('newsfeed-add'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse(
            'newsfeed-edit',
            args=[self.first_message.pk],
        ))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse(
            'comment-add',
            args=[self.first_message.pk],
        ))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse(
            'workgroup-view',
            args=[self.best_group.slug],
        ))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse(
            'workgroup-members',
            args=[self.best_group.slug],
        ))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse(
            'workgroup-news',
            args=[self.best_group.slug],
        ))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('feed-latest'))
        self.assertEqual(response.status_code, 302)

        # Authenticated user

        self.client.login(
            username='brunehilde',
            password='brunehilde_password',
        )

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('directory'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('directory') + '?q=gont')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('groups'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('newsfeed-add'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(
            'newsfeed-edit',
            args=[self.first_message.pk],
        ))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(
            'comment-add',
            args=[self.first_message.pk],
        ))
        self.assertEqual(response.status_code, 405)

        response = self.client.get(reverse(
            'workgroup-view',
            args=[self.best_group.slug],
        ))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(
            'workgroup-members',
            args=[self.best_group.slug],
        ))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse(
            'workgroup-news',
            args=[self.best_group.slug],
        ))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('feed-latest'))
        self.assertEqual(response.status_code, 200)
