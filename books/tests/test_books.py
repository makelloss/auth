import pytest

from books.models import Book

URL = "/api/books/"
DATA = {"title": "Dune", "author": "Frank Herbert", "year": 1965}


def detail(pk):
    return f"/api/books/{pk}/"


# GET
@pytest.mark.django_db
def test_anyone_can_get_list(client, book):
    response = client.get(URL)
    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_anyone_can_get_book(client, book):
    response = client.get(detail(book.id))
    assert response.status_code == 200
    assert response.data["title"] == "1984"


@pytest.mark.django_db
def test_get_not_existing_book(client):
    response = client.get(detail(999))
    assert response.status_code == 404


# POST
@pytest.mark.django_db
def test_user_can_create_book(user_client):
    response = user_client.post(URL, DATA, format="json")
    assert response.status_code == 201
    assert Book.objects.filter(title="Dune").exists()


@pytest.mark.django_db
def test_anonymous_cannot_create_book(client):
    response = client.post(URL, DATA, format="json")
    assert response.status_code == 401
    assert Book.objects.count() == 0


@pytest.mark.django_db
def test_create_book_without_title(user_client):
    response = user_client.post(URL, {"author": "Someone"}, format="json")
    assert response.status_code == 400
    assert "title" in response.data


@pytest.mark.django_db
def test_create_book_with_negative_year(user_client):
    response = user_client.post(URL, {"title": "Book", "author": "Someone", "year": -5}, format="json")
    assert response.status_code == 400
    assert "year" in response.data


# PUT / PATCH
@pytest.mark.django_db
def test_user_can_update_book(user_client, book):
    response = user_client.put(detail(book.id), DATA, format="json")
    assert response.status_code == 200
    book.refresh_from_db()
    assert book.title == "Dune"


@pytest.mark.django_db
def test_user_can_patch_book(user_client, book):
    response = user_client.patch(detail(book.id), {"year": 1950}, format="json")
    assert response.status_code == 200
    book.refresh_from_db()
    assert book.year == 1950


@pytest.mark.django_db
def test_anonymous_cannot_update_book(client, book):
    response = client.patch(detail(book.id), {"title": "Hacked"}, format="json")
    assert response.status_code == 401
    book.refresh_from_db()
    assert book.title == "1984"


@pytest.mark.django_db
def test_update_not_existing_book(user_client):
    response = user_client.patch(detail(999), {"title": "New"}, format="json")
    assert response.status_code == 404


# DELETE
@pytest.mark.django_db
def test_admin_can_delete_book(admin_client, book):
    response = admin_client.delete(detail(book.id))
    assert response.status_code == 204
    assert Book.objects.count() == 0


@pytest.mark.django_db
def test_user_cannot_delete_book(user_client, book):
    response = user_client.delete(detail(book.id))
    assert response.status_code == 403
    assert Book.objects.count() == 1


@pytest.mark.django_db
def test_anonymous_cannot_delete_book(client, book):
    response = client.delete(detail(book.id))
    assert response.status_code == 401
    assert Book.objects.count() == 1


@pytest.mark.django_db
def test_admin_delete_not_existing_book(admin_client):
    response = admin_client.delete(detail(999))
    assert response.status_code == 404
