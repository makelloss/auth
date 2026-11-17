import logging

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import viewsets

from .models import Book
from .permissions import BookPermission
from .serializers import BookSerializer

logger = logging.getLogger(__name__)

BOOK_EXAMPLE = OpenApiExample(
    "Книга", value={"title": "1984", "author": "George Orwell", "year": 1949}, request_only=True
)


@extend_schema_view(
    list=extend_schema(summary="Список книг (доступно всім)"),
    retrieve=extend_schema(
        summary="Книга за id (доступно всім)",
        responses={200: BookSerializer, 404: OpenApiResponse(description="Книгу не знайдено")},
    ),
    create=extend_schema(
        summary="Створити книгу (лише авторизовані)",
        examples=[BOOK_EXAMPLE],
        responses={
            201: BookSerializer,
            400: OpenApiResponse(description="Некоректні дані"),
            401: OpenApiResponse(description="Немає токена або він невалідний"),
        },
    ),
    update=extend_schema(
        summary="Оновити книгу (лише авторизовані)",
        examples=[BOOK_EXAMPLE],
        responses={
            200: BookSerializer,
            400: OpenApiResponse(description="Некоректні дані"),
            401: OpenApiResponse(description="Немає токена або він невалідний"),
            404: OpenApiResponse(description="Книгу не знайдено"),
        },
    ),
    partial_update=extend_schema(
        summary="Частково оновити книгу (лише авторизовані)",
        responses={
            200: BookSerializer,
            400: OpenApiResponse(description="Некоректні дані"),
            401: OpenApiResponse(description="Немає токена або він невалідний"),
            404: OpenApiResponse(description="Книгу не знайдено"),
        },
    ),
    destroy=extend_schema(
        summary="Видалити книгу (лише адміністратор)",
        responses={
            204: OpenApiResponse(description="Книгу видалено"),
            401: OpenApiResponse(description="Немає токена або він невалідний"),
            403: OpenApiResponse(description="Користувач не адміністратор"),
            404: OpenApiResponse(description="Книгу не знайдено"),
        },
    ),
)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by("id")
    serializer_class = BookSerializer
    permission_classes = [BookPermission]

    def perform_create(self, serializer):
        book = serializer.save()
        logger.info("Book id=%s created by user id=%s", book.pk, self.request.user.pk)

    def perform_update(self, serializer):
        book = serializer.save()
        logger.info("Book id=%s updated by user id=%s", book.pk, self.request.user.pk)

    def perform_destroy(self, instance):
        book_id = instance.pk
        instance.delete()
        logger.info("Book id=%s deleted by admin id=%s", book_id, self.request.user.pk)
