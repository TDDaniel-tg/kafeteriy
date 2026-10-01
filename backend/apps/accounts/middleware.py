from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin

User = get_user_model()

class SSOMockAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 1. Allow header X-User-Id or X-User-Role
        user_id = request.headers.get('X-User-Id')
        user_role = request.headers.get('X-User-Role')
        demo_user_param = request.GET.get('demo_user')

        user = None
        if user_id:
            user = User.objects.filter(id=user_id).first()
        elif user_role:
            user = User.objects.filter(role=user_role).first()
        elif demo_user_param:
            user = User.objects.filter(username=demo_user_param).first() or User.objects.filter(role=demo_user_param).first()

        if user:
            request.user = user
