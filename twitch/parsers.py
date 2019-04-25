import json
import six

from rest_framework.parsers import BaseParser
from rest_framework import renderers
from rest_framework.parsers import ParseError
from django.conf import settings


class TwitchPostParser(BaseParser):
    """
    Allows me to access the raw_body attribute so i can compare hashes
    """
    media_type = 'application/json'
    renderer_class = renderers.JSONRenderer

    def parse(self, stream, media_type=None, parser_context=None):
        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)
        request = parser_context.get('request')
        try:
            data = stream.read().decode(encoding)
            setattr(request, 'raw_body', data)  # setting a 'body' alike custom attr with raw POST content
            return json.loads(data)
        except ValueError as exc:
            raise ParseError('JSON parse error - %s' % six.text_type(exc))
