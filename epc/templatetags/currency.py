from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

euro = '€'
dollar = '$'
rouble = ''


def get_current_currency():
    # TODO
    return euro


@register.filter
def currency(value):
    eth = round(float(value), 2)
    # return "%s%s" % (intcomma(int(dollars)), ("%0.2f" % value)[-3:])
    return get_current_currency() + "%s" % (intcomma(int(eth)))


@register.filter
def stringify(value):
    """converts int to string"""
    return str(value)
