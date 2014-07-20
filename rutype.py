#encoding=utf-8

import sys, re, base64, types, json
from EMT import EMTypograph
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(is_safe=False)
@stringfilter
def rutype(value):
	EMT = EMTypograph()
	EMT.set_text(value)
	return EMT.apply()
