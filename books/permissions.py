import logging

from rest_framework.permissions import SAFE_METHODS, BasePermission

logger = logging.getLogger(__name__)


class BookPermission(BasePermission):

    message = "Only administrators can delete books."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not (request.user and request.user.is_authenticated):
            logger.warning("Anonymous user tried to %s %s", request.method, request.path)
            return False
        if request.method == "DELETE" and not request.user.is_staff:
            logger.warning("User id=%s is not admin and tried to delete %s", request.user.pk, request.path)
            return False
        return True
