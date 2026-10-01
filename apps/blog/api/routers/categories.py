from django.shortcuts import get_object_or_404
from ninja import Query
from ninja import Router
from ninja.pagination import PageNumberPagination
from ninja.pagination import paginate

from apps.blog.api.schemas import CategoryDetailSchema
from apps.blog.api.schemas import CategoryFilterSchema
from apps.blog.api.schemas import CategoryInSchema
from apps.blog.api.schemas import CategoryListSchema
from apps.blog.models import Category

router = Router(tags=["categories"])


@router.get("/", response={200: list[CategoryListSchema]})
@paginate(PageNumberPagination)
def list_categories(request, filters: Query[CategoryFilterSchema]):
    categories = Category.objects.all()
    return filters.filter(categories)


@router.get("/{category_id}", response={200: CategoryDetailSchema})
def get_category(request, category_id: int):
    return get_object_or_404(Category, id=category_id)


@router.post("/", response={201: CategoryDetailSchema})
def create_category(request, payload: CategoryInSchema):
    return Category.objects.create(**payload.dict(exclude_unset=True))


@router.put("/{category_id}", response={200: CategoryDetailSchema})
def update_category(request, category_id: int, payload: CategoryInSchema):
    category = get_object_or_404(Category, id=category_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(category, attr, value)
    category.save()
    return category


@router.delete("/{category_id}", response={204: None})
def delete_category(request, category_id: int):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
