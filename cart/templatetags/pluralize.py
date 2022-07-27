from django import template

register = template.Library()


@register.filter
def pluralize_cart_item(value):
    """
    DESCRIPTION
    """
    mod = value % 10
    ending = ''
    try:
        if (mod == 0) or (mod >= 5) or (10 < value < 20):
            ending = 'ов'
        elif mod > 1:
            ending = 'а'
    except ValueError:  # Invalid string that's not a number.
        pass

    return ending
