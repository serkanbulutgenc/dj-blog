from django.shortcuts import get_object_or_404
from ninja import Query
from ninja import Router
from ninja.pagination import PageNumberPagination
from ninja.pagination import paginate

from apps.blog.api.schemas import TagSchemas
from apps.blog.models import Tag

router = Router(tags=["tags"])


@router.get("/", response={200: list[TagSchemas.TagListSchema]})
@paginate(PageNumberPagination)
def list_tags(request, filters: Query[TagSchemas.TagFilterSchema]):
    tags = Tag.objects.all()
    return filters.filter(tags)


@router.get("/{tag_id}", response={200: TagSchemas.TagDetailSchema})
def get_tag(request, tag_id: int):
    return get_object_or_404(Tag, id=tag_id)


@router.post("/", response={201: TagSchemas.TagDetailSchema})
def create_tag(request, payload: TagSchemas.TagInSchema):
    return Tag.objects.create(**payload.dict(exclude_unset=True))


@router.put("/{tag_id}", response={200: TagSchemas.TagDetailSchema})
def update_tag(request, tag_id: int, payload: TagSchemas.TagInSchema):
    tag = get_object_or_404(Tag, id=tag_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(tag, attr, value)
    tag.save()
    return tag


@router.delete("/{tag_id}", response={204: None})
def delete_tag(request, tag_id: int):
    tag = get_object_or_404(Tag, id=tag_id)
    tag.delete()
