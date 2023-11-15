from django.db.models.query_utils import Q
from django.shortcuts import HttpResponse, get_object_or_404
from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializer import (
    UserSerializer,
    UserCreateSerializer,
    SubscribeListSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer, PasswordSetSerializer, SubscriptionsSerializer)
from .filters import RecipesFilter
from .pagination import CustomPaginator
from .permissions import CustomAuthorOrReadOnly
from recipes.models import (
    Favorites,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Shopping_cart,
    Tag,
)
from users.models import Subscriptions, User


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPaginator

    def get_permissions(self):
        if self.action in ("retrieve", "create"):
            self.permission_classes = [
                AllowAny,
            ]
        return super(self.__class__, self).get_permissions()

    def get_serializer_class(self):
        if self.action in ["set_password"]:
            return PasswordSetSerializer
        if self.request.method == "GET":
            return UserSerializer
        elif self.request.method == "POST":
            return UserCreateSerializer

    @action(
        detail=False,
        methods=['get'],
        pagination_class=None,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
            Subscriptions.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(Subscriptions, user=user, author=author).delete()
        return Response(
            {'detail': 'Подписка удалена'}, status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
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
