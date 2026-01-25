import random
import factory
from django.utils.text import slugify
from apps.blog.models import Post, Category


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post
        exclude = ("paragraphs",)

    title = factory.Faker("text", max_nb_chars=125)
    paragraphs = factory.Faker("paragraphs", nb=3)

    @factory.lazy_attribute
    def body(self):
        return "\n".join(self.paragraphs)

    @factory.lazy_attribute
    def slug(self):
        return slugify(self.title)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    title = factory.Faker("word")

    description = factory.Faker("paragraph")

    posts = factory.RelatedFactoryList(
        PostFactory, factory_related_name="category", size=lambda: random.randint(3, 8)
    )

    @factory.lazy_attribute
    def slug(self):
        return slugify(self.title)
