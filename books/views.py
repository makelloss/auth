from rest_framework import viewsets

from .models import Book
from .permissions import BookPermission
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by("id")
    serializer_class = BookSerializer
    permission_classes = [BookPermission]
