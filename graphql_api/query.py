import graphene

from .models import Pool
from .object_types import PoolType

from django.db.models import Avg


class Query(graphene.ObjectType):
    all_pools = graphene.List(PoolType)
    pool_by_id = graphene.Field(PoolType, id=graphene.Int())
    pool_by_slug = graphene.Field(PoolType, slug=graphene.String())

    def resolve_all_pools(root, info):
        return Pool.objects.all().\
            annotate(_average_value=Avg('rating__value')).\
            order_by('-created_at')
    
    def resolve_pool_by_id(root, info, id):
        return Pool.objects.get(pk=id)
    
    def resolve_pool_by_slug(root, info, slug):
        return Pool.objects.filter(slug=slug).first()
            