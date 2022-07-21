import datetime as dt

from django.db import IntegrityError
from django.db.models import Avg
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Comment, Genre, Review, Title, User

from .validators import validate_username


class UserSerializer(serializers.ModelSerializer):
    def validate_username(self, value):
        return validate_username(value)

    class Meta:
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        model = User


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        read_only_fields = ("role",)
        model = User


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Category


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        required=True,
        slug_field="slug",
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        required=True,
        slug_field="slug",
    )
    rating = serializers.SerializerMethodField()

    @staticmethod
    def get_rating(obj: Title):
        return obj.reviews.aggregate(Avg("score"))["score__avg"]

    @staticmethod
    def process_data(validated_data, instance=None):
        try:
            genre = validated_data.pop("genre")
        except KeyError:
            genre = []

        if instance is None:
            title = Title.objects.create(**validated_data)
        else:
            title = instance

        if genre:
            title.genre.clear()

            for genre_item in genre:
                title.genre.add(genre_item)

        for attr, value in validated_data.items():
            setattr(title, attr, value)

        title.save()

        return title

    def create(self, validated_data):
        return self.process_data(validated_data)

    def update(self, instance, validated_data):
        return self.process_data(validated_data, instance)

    def validate_year(self, value):
        if value > dt.datetime.now().year:
            raise serializers.ValidationError(
                "Год выпуска не может быть больше текущего."
            )

        return value

    def to_representation(self, obj: Title):
        self.fields["genre"] = GenreSerializer(many=True)
        self.fields["category"] = CategorySerializer()

        return super().to_representation(obj)

    class Meta:
        fields = (
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category",
        )
        model = Title


class AuthUserSignUpSerializer(serializers.ModelSerializer):
    def validate_username(self, value):
        return validate_username(value)

    class Meta:
        fields = (
            "username",
            "email",
        )
        model = User


class AuthUserTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, trim_whitespace=True)
    confirmation_code = serializers.CharField(
        required=True, trim_whitespace=True
    )

    def validate(self, attrs):
        data = attrs

        if not User.objects.filter(username=data.get("username")).exists():
            raise exceptions.NotFound("Пользователь не найден.")

        user = User.objects.get(username=data.get("username"))

        if user.confirmation_code != data.get("confirmation_code"):
            raise exceptions.ValidationError("Некорректный код подтверждения.")

        refresh = RefreshToken.for_user(user)

        return {"token": str(refresh.access_token)}

    class Meta:
        fields = (
            "username",
            "confirmation_code",
        )
        model = User


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
    )

    def save(self, **kwargs):
        try:
            super().save(**kwargs)
        except IntegrityError:
            raise serializers.ValidationError("Отзыв уже существует.")

    class Meta:
        fields = ("id", "text", "author", "score", "pub_date")
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
    )

    class Meta:
        fields = ("id", "text", "author", "pub_date")
        model = Comment
