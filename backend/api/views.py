from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializer import (
    CustomUserSerializer,
    CreateUserSerializer,
    SubscribeListSerializer,
    SubscriptionsSerializer,
    ChangePasswordSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer,
    TagSerializer,
    IngredientSerializer,
)
from .pagination import Paginator
from .filters import RecipesFilter
from .permissions import AuthorOrReadOnly
from recipes.models import (
    Recipe,
    RecipeIngredient,
    Favorite,
    Ingredient,
    Shopping_cart,
    Tag,
)

from users.models import User, Subscribe


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = Paginator

    def get_permissions(self):
        if self.action in ("retrieve", "create"):
            self.permission_classes = [
                permissions.AllowAny,
            ]
        return super(self.__class__, self).get_permissions()

    def get_serializer_class(self):
        if self.action in ['set_password']:
            return ChangePasswordSerializer
        if self.action in ('list', 'retrieve'):
            return CustomUserSerializer
        return CreateUserSerializer

    def create(self, request, *args, **kwargs):
        password = request.data.get("password")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(password)
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,),
        pagination_class=None,
    )
    def subscribe(self, request, **kwargs):
        user = self.request.user
        author = get_object_or_404(User, id=kwargs['id'])
        if request.method == 'POST':
            serializer = SubscribeListSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(Subscribe, user=user, author=author).delete()
        return Response(
            {'detail': 'Подписка удалена'}, status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,),
        pagination_class=Paginator,
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewsSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = Paginator
    filterset_class = RecipesFilter
    http_method_names = ['get', 'post', 'patch', 'create', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrive'):
            return RecipeSerializer
        return RecipeCreateSerializer

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient',
            'tags',
            'favorite_recipe',
            'shopping_recipe',
        ).all()
        return recipes

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = RecipeListSerializer(
                recipe, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Favorite.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(Favorite, user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,),
        pagination_class=None,
    )
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = RecipeListSerializer(
                recipe, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Shopping_cart.objects.create(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(
            Shopping_cart, user=request.user, recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_recipe__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total=Sum('amount'))

        shopping_cart_list = 'Список покупок:\n'
        for ingredient in ingredients:
            shopping_cart_list += (
                f' {ingredient["ingredient__name"]} - {ingredient["total"]}'
                f'({ingredient["ingredient__measurement_unit"]})\n')

        response = HttpResponse(shopping_cart_list, content_type='text/plain')
        response['Content-Disposition'] = (f'attachment;'
                                           f'filename={"Список покупок"}')
        return response
