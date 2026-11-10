from rest_framework.permissions import SAFE_METHODS, BasePermission


class BookPermission(BasePermission):

    message = "Only administrators can delete books."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method == "DELETE":
            return request.user.is_staff
        return True
