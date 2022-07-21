from uuid import uuid4

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, views, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from reviews.models import Category, Comment, Genre, Review, Title, User

from .filtersets import TitleFilter
from .permissions import IsAdmin, IsAdminOrAuthor, IsAdminOrReadOnly
from .serializers import (AuthUserSignUpSerializer, AuthUserTokenSerializer,
                          CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, TitleSerializer,
                          UserMeSerializer, UserSerializer)
from .viewsets import CreateDestroyListModelViewSet, CreateModelViewSet


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdmin,)
    pagination_class = LimitOffsetPagination
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    lookup_field = "username"


class UserMeView(views.APIView):
    def get(self, request):
        user = self.request.user
        serializer = UserMeSerializer(user, many=False)
        return Response(serializer.data)

    def patch(self, request, pk=None):
        user = self.request.user
        serializer = UserMeSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TitleViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    pagination_class = LimitOffsetPagination


class GenreViewSet(CreateDestroyListModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class CategoryViewSet(CreateDestroyListModelViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    permission_classes = (IsAdminOrAuthor,)
    serializer_class = ReviewSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))

        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))

        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    permission_classes = (IsAdminOrAuthor,)
    serializer_class = CommentSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get("review_id"))

        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get("review_id"))

        serializer.save(author=self.request.user, review=review)


class AuthSignUpViewSet(CreateModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    serializer_class = AuthUserSignUpSerializer

    @staticmethod
    def generate_confirmation_code():
        return uuid4().hex

    @staticmethod
    def send_confirmation_code(email_to: str, confirmation_code: str):
        email_from = "api@yamdb.yamdb"
        subject = "Код подтверждения"

        send_mail(
            subject,
            confirmation_code,
            email_from,
            [email_to],
            fail_silently=False,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        confirmation_code = self.generate_confirmation_code()

        user_filter_params = {
            "username": serializer.initial_data.get("username"),
            "email": serializer.initial_data.get("email"),
        }

        if User.objects.filter(**user_filter_params).exists():
            user = User.objects.get(**user_filter_params)
            user.confirmation_code = confirmation_code
            user.save()
        else:
            serializer.is_valid(raise_exception=True)
            serializer.save(confirmation_code=confirmation_code)

        self.send_confirmation_code(
            serializer.initial_data["email"], confirmation_code
        )

        headers = self.get_success_headers(serializer.initial_data)

        return Response(
            serializer.initial_data, status=status.HTTP_200_OK, headers=headers
        )


class AuthTokenViewSet(TokenObtainPairView):
    serializer_class = AuthUserTokenSerializer
