import factory
from django.utils.text import slugify

from .models import Post


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Faker("sentence")
    content = factory.Faker("text")

    @factory.lazy_attribute
    def slug(self):
        return slugify(self.title)
