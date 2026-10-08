import factory
from django.utils.text import slugify

from .models import Post


class PostFactory(factory.django.DjangoModelFactory[Post]):
    class Meta:
        model = Post

    title = factory.Faker("sentence")
    content = factory.Faker("text")

    @factory.lazy_attribute
    def slug(self: Post) -> str:
        return slugify(self.title)
