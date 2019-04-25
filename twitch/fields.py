# Courtesy of django-social-auth
import json

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import six
from django.utils.encoding import smart_text


class JSONField(models.TextField):
    """Simple JSON field that stores python structures as JSON strings
    on database.
    """

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def to_python(self, value):
        """
        Convert the input JSON value into python structures, raises
        django.core.exceptions.ValidationError if the data can't be converted.
        """
        if self.blank and not value:
            return None
        if isinstance(value, six.string_types):
            try:
                return json.loads(value)
            except Exception as e:
                raise ValidationError(str(e))
        else:
            return value

    def validate(self, value, model_instance):
        """Check value is a valid JSON string, raise ValidationError on
        error."""
        if isinstance(value, six.string_types):
            super(JSONField, self).validate(value, model_instance)
            try:
                json.loads(value)
            except Exception as e:
                raise ValidationError(str(e))

    def get_prep_value(self, value):
        """Convert value to JSON string before save"""
        try:
            return json.dumps(value)
        except Exception as e:
            raise ValidationError(str(e))

    def value_to_string(self, obj):
        """Return value from object converted to string properly"""
        return smart_text(self.value_from_object(obj))

    def value_from_object(self, obj):
        """Return value dumped to string."""
        orig_val = super(JSONField, self).value_from_object(obj)
        return self.get_prep_value(orig_val)
