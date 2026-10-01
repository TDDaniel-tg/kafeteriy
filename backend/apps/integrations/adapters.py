import time
from typing import Dict, Any, List
from django.conf import settings
from .models import IntegrationChannel

class BaseAdapter:
    channel_type = ''

    def is_mock(self) -> bool:
        channel = IntegrationChannel.objects.filter(channel_type=self.channel_type).first()
        if channel:
            return channel.is_mock
        return getattr(settings, 'MOCK_INTEGRATIONS', True)

    def ping(self) -> Dict[str, Any]:
        start = time.time()
        # Mock ping
        duration_ms = int((time.time() - start) * 1000) + 25
        return {'status': 'available', 'duration_ms': duration_ms, 'is_mock': self.is_mock()}

class ZUP1CAdapter(BaseAdapter):
    channel_type = '1c_zup'

    def sync_employees(self) -> List[Dict[str, Any]]:
        # In mock mode, returns sample sync results
        return [
            {'username': 'morozova', 'full_name': 'Анна Морозова', 'department': 'Продуктовая команда', 'grade': 'Middle', 'status': 'updated'},
            {'username': 'sokolov', 'full_name': 'Михаил Соколов', 'department': 'Разработка', 'grade': 'Senior', 'status': 'updated'},
        ]

class SSOAdapter(BaseAdapter):
    channel_type = 'sso'

    def verify_token(self, token: str) -> Dict[str, Any]:
        return {'valid': True, 'email': 'a.morozova@company.ru', 'username': 'a.morozova'}

class SMTPAdapter(BaseAdapter):
    channel_type = 'smtp'

    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        # In mock mode, outputs log or saves notification
        return True

class GifteryAdapter(BaseAdapter):
    channel_type = 'giftery'

    def issue_certificate(self, nominal: int, recipient_email: str) -> Dict[str, Any]:
        return {
            'success': True,
            'certificate_code': f"GIFT-{int(time.time())}-{nominal}",
            'nominal': nominal,
            'recipient': recipient_email
        }

class ProstodarAdapter(BaseAdapter):
    channel_type = 'prostodar'

    def issue_card(self, user_email: str, amount: int) -> Dict[str, Any]:
        return {
            'success': True,
            'card_pan_masked': '5536 91** **** 4812',
            'amount': amount,
            'delivery_email': user_email
        }
