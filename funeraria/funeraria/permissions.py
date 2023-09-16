from rest_framework import permissions
import logging 
from accounts.models import User
logger = logging.getLogger(__name__)
class IsAdmin(permissions.IsAdminUser):
    def has_permission(self, request, view):
        #logger.info(request.user)
        return bool(request.user and request.user.is_staff)

class IsSuperUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

class isEqualOrUpperPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        retrieved_user = User.objects.get(pk=view.kwargs.get('pk'))
        if retrieved_user is not None:
            if(request.user.is_superuser):
                return True
            if(request.user.is_staff and not retrieved_user.is_superuser):
                return True
        
        return False

