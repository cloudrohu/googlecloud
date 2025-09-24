# utils.py
from django.utils.text import slugify
from django.db.models import Model

def unique_slugify(instance: Model, value: str, slug_field_name: str = 'slug') -> str:
    """
    Generate a unique slug for any model instance based on 'value'.
    - instance: model object
    - value: usually the name field
    - slug_field_name: which field to store slug (default = 'slug')
    """

    slug = slugify(value)
    model_class = instance.__class__

    # Check if slug already exists
    unique_slug = slug
    num = 1
    while model_class.objects.filter(**{slug_field_name: unique_slug}).exclude(pk=instance.pk).exists():
        unique_slug = f"{slug}-{num}"
        num += 1

    return unique_slug
