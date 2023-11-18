from django.db.models.query_utils import Q
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import exceptions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorites, Ingredient, Recipe, RecipeIngredient,
                            Shopping_cart, Tag)
from users.models import Subscriptions, User

from .filters import RecipesFilter
from .pagination import CustomPaginator
from .permissions import CustomAuthorOrReadOnly
from .serializer import (CustomUserSerializer, IngredientSerializer,
                         PasswordSetSerializer, RecipeCreateSerializer,
                         RecipeListSerializer, RecipeSerializer,
                         SubscriptionsSerializer, TagSerializer,
                         UserCreateSerializer)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return CustomUserSerializer
        return UserCreateSerializer

    @action(
        detail=False,
        methods=['get'],
        pagination_class=None,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        serializer = PasswordSetSerializer(
            request.user, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': 'Пароль изменен!'},
            status=status.HTTP_204_NO_CONTENT,
        )

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
        permission_classes=(IsAuthenticated,),
        serializer_class=SubscriptionsSerializer,
        pagination_class=None,
    )
    def subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(User, pk=id)

        if self.request.method == 'POST':
            if user == author:
                raise exceptions.ValidationError(
                    'Нельзя подписаться на самого себя!'
                )
            if Subscriptions.objects.filter(
                user=user,
                author=author
            ).exists():
                raise exceptions.ValidationError(
                    'Вы уже подписаны на этого автора.'
                )
            Subscriptions.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not Subscriptions.objects.filter(
                user=user,
                author=author
            ).exists():
                raise exceptions.ValidationError(
                    'Подписка не была оформлена, либо уже удалена.'
                )
            subscription = get_object_or_404(
                Subscriptions,
                user=user,
                author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=['get'],
        serializer_class=SubscriptionsSerializer,
        permission_classes=IsAuthenticated,
    )
    def subscriptions(self, request):
        user = self.request.user
        subscriptions = User.objects.filter(
            subscribing__user=user
        ).prefetch_related('recipes')
        paginated_queryset = self.paginate_queryset(subscriptions)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewsSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None
    queryset = Ingredient.objects.all()

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name is not None:
            filter_one_input = queryset.filter(name__istartswith=name)
            filter_center_input = queryset.filter(
                ~Q(name__istartswith=name) & Q(name__icontains=name)
            )
            queryset = list(filter_one_input) + list(filter_center_input)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (CustomAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    pagination_class = CustomPaginator

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
        methods=['post', 'delete'],
        detail=True,
        url_path='favorite',
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            if Recipe.objects.filter(pk=pk).exists():
                if not Favorites.objects.filter(
                    user=request.user,
                        recipe=get_object_or_404(Recipe, pk=pk)).exists():
                    Favorites.objects.create(
                        user=request.user,
                        recipe=get_object_or_404(Recipe, pk=pk))
                    recipe = Recipe.objects.get(id=pk)
                    serializer = RecipeListSerializer(recipe)
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED)
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            if Favorites.objects.filter(
                    user=request.user,
                    recipe=get_object_or_404(Recipe, pk=pk)).exists():
                Favorites.objects.filter(
                    user=request.user,
                    recipe=get_object_or_404(Recipe, pk=pk)).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        pagination_class=None,
    )
    def shopping_cart(self, request, **kwargs):
        if Recipe.objects.filter(id=kwargs.get('pk')).exists():
            recipe = Recipe.objects.get(id=kwargs.get('pk'))
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            serializer = RecipeListSerializer(recipe, data=request.data,
                                              context={"request": request})
            serializer.is_valid(raise_exception=True)
            if not Shopping_cart.objects.filter(user=request.user,
                                                recipe=recipe).exists():
                Shopping_cart.objects.create(user=request.user, recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response({'errors': 'Рецепт уже в списке покупок.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            get_object_or_404(Shopping_cart, user=request.user,
                              recipe=recipe).delete()
            return Response(
                {'detail': 'Рецепт удален из списка покупок.'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping = user.shopping_user.all()
        shopping_list = {}
        for shop in shopping:
            recipe = shop.recipe
            ingredients = RecipeIngredient.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                name = ingredient.ingredient.name
                amount = ingredient.amount
                measurement_unit = ingredient.ingredient.measurement_unit
                if name not in shopping_list:
                    shopping_list[name] = {
                        'measurement_unit': measurement_unit,
                        'amount': amount,
                    }
                else:
                    shopping_list[name]['amount'] += amount
        shop_list = [
            f"{name} - {data['amount']}{data['measurement_unit']}"
            for name, data in shopping_list.items()
        ]
        responce = HttpResponse(
            'Cписок покупок:\n' + '\n'.join(shop_list),
            content_type='text/plain',
        )
        responce['Content-Disposition'] = 'attachment; filename=shop_list.txt'
        return responce
