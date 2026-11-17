import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from books.models import Book


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="user", password="StrongPass123!")


@pytest.fixture
def admin(db):
    return User.objects.create_user(username="admin", password="StrongPass123!", is_staff=True)


@pytest.fixture
def user_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_client(admin):
    client = APIClient()
    client.force_authenticate(user=admin)
    return client


@pytest.fixture
def book(db):
    return Book.objects.create(title="1984", author="George Orwell", year=1949)
