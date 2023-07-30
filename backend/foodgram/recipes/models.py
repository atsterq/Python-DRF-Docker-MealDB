from django.db.models import CharField, Model, SlugField


class Tag(Model):
    name = CharField(max_length=200)
    color = CharField(max_length=7)
    slug = SlugField(max_length=200, unique=True)

