from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag


class RecipesFilter(filters.FilterSet):
    tags = filters.CharFilter(method='filter_tags')
    is_favorited = filters.BooleanFilter(method='is_favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter'
    )
    author = filters.NumberFilter(
        method='filter_author'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def is_favorited_filter(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return Recipe.objects.none()
        if value == 0:
            return queryset
        if value and user.is_authenticated:
            return queryset.filter(favorite_recipe__user=user)

    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if user.is_anonymous:
            return Recipe.objects.none()
        if value and user.is_authenticated:
            return queryset.filter(shopping_recipe__user=user)
        return queryset

    def filter_author(self, queryset, name, value):
        if value:
            return queryset.filter(author=value)
        else:
            return queryset

    def filter_tags(self, queryset, name, value):
        tags = self.request.GET.getlist('tags')
        return queryset.filter(tags__slug__in=tags).distinct()