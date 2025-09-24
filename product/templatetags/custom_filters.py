from django import template

register = template.Library()

@register.filter
def format_price(value):
    """
    Format decimal: 299.500 -> 299.5, 299.000 -> 299
    """
    try:
        value = float(value)
        if value.is_integer():
            return str(int(value))   # agar .00 hai to pura integer
        return f"{value:.2f}".rstrip("0").rstrip(".")  # 299.500 -> 299.5
    except:
        return value
