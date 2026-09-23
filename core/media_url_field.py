from django.core.files.storage import default_storage
from rest_framework import serializers


class MediaUrlField(serializers.CharField):
    def to_representation(self, value):
        if not value:
            return None

        url = default_storage.url(value)
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request is not None else url
