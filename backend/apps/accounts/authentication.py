from rest_framework.authentication import BaseAuthentication
from django.contrib.auth import get_user_model

User = get_user_model()

class TokenAndSessionAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Access underlying HttpRequest safely without triggering DRF request.user property
        django_request = getattr(request, '_request', request)
        cached_user = getattr(django_request, 'user', None)
        if cached_user and cached_user.is_authenticated:
            return (cached_user, None)

        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            user = User.objects.filter(username=token).first() or User.objects.filter(id=token).first()
            if user:
                return (user, None)

        # Allow header X-User-Id
        user_id = request.headers.get('X-User-Id')
        if user_id:
            user = User.objects.filter(id=user_id).first()
            if user:
                return (user, None)

        return None
