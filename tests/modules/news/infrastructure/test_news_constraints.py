import pytest
from django.db import IntegrityError

from modules.news.domain.news import News

pytestmark = pytest.mark.django_db


def test_news_title_cannot_be_empty():
    with pytest.raises(IntegrityError):
        News.objects.create(
            title="",
            content={"blocks": []},
        )
