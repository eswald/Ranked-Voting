from google.appengine.ext import webapp
from django.utils.safestring import mark_safe
import markdown2

register = webapp.template.create_template_register()

@register.filter
def markdown(value):
    result = markdown2.markdown(value)
    return mark_safe(result)
