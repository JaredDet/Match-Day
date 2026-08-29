from django.db import models
from rest_framework import serializers


class EnumChoiceField(serializers.ChoiceField):
    def __init__(self, enum_type: type[models.TextChoices], **kwargs):
        self.enum_type = enum_type
        super().__init__(choices=enum_type.choices, **kwargs)

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        return self.enum_type(value)
