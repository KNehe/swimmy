from .models import Pool

from graphene_django import DjangoObjectType
import graphene

# QUERY OBJECT TYPES


class PoolType(DjangoObjectType):
    average_rating = graphene.Decimal()
    class Meta:
        model = Pool
        fields = ('id', 'name', 'location',
                  'day_price', 'thumbnail_url', 'image_url', 'width',
                  'length', 'depth_shallow_end', 'depth_deep_end',
                  'maximum_people', 'slug', 'created_at','average_rating'
                  )

# MUTATION INPUT OBJECT TYPES


