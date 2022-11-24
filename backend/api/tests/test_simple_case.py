from http import HTTPStatus

from rest_framework.test import APIClient, APITestCase

from api.tests.common import TAG_1_DATA
from foodgram.models import Tags


class TestTags(APITestCase):
    url_tags = '/api/tags/'
    url_tag = '/api/tags/1/'

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.tag = Tags.objects.create(**TAG_1_DATA)

    def setUp(self) -> None:
        self.client = APIClient()

    def test_urls(self):
        '''Проверка доступности страниц'''
        url_tuple = (self.url_tags, self.url_tag,)
        for url in url_tuple:
            with self.subTest(url=url):
                request = self.client.get(url)
                self.assertEqual(request.status_code, HTTPStatus.OK)
