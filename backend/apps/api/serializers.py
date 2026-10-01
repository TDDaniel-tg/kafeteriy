from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.points.models import PointAccount, PointLot, PointTransaction
from apps.catalog.models import CatalogSection, CatalogCategory, Product, Cart, CartItem
from apps.orders.models import Order, OrderItem, OrderApproval, OrderStatusHistory
from apps.budgets.models import BudgetRule, EmployeeBudget, PositionLimit, CategoryLimit
from apps.campaigns.models import SelectionWindow
from apps.health_dms.models import DMSProgram, EmployeeDMSPolicy, FamilyMemberDMS, DMSChangeRequest
from apps.social import models as social_models
from apps.comms import models as comms_models
from apps.surveys_gamification import models as sg_models
from apps.support import models as support_models
from apps.audit import models as audit_models
from apps.settings_platform import models as settings_models
from apps.integrations import models as int_models

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    available_balance = serializers.SerializerMethodField()
    total_balance = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'middle_name',
            'full_name', 'role', 'department', 'grade', 'hire_date', 'birth_date',
            'gender', 'city', 'delivery_address', 'segment', 'is_frozen',
            'has_unspent_main_vacation', 'flexible_schedule_active',
            'onboarding_completed', 'totp_enabled', 'available_balance', 'total_balance'
        ]

    def get_available_balance(self, obj):
        acc = getattr(obj, 'point_account', None)
        return acc.available_balance if acc else 0

    def get_total_balance(self, obj):
        acc = getattr(obj, 'point_account', None)
        return acc.total_balance if acc else 0

class PointLotSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointLot
        fields = '__all__'

class PointTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointTransaction
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.IntegerField(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'custom_data', 'subtotal']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'price', 'quantity', 'subtotal', 'meta_info']

class OrderApprovalSerializer(serializers.ModelSerializer):
    approver_name = serializers.CharField(source='approver.full_name', read_only=True)

    class Meta:
        model = OrderApproval
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    approvals = OrderApprovalSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    can_cancel = serializers.BooleanField(source='can_be_cancelled', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

class SelectionWindowSerializer(serializers.ModelSerializer):
    is_open = serializers.BooleanField(source='is_currently_open', read_only=True)

    class Meta:
        model = SelectionWindow
        fields = '__all__'

class DMSProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = DMSProgram
        fields = '__all__'

class EmployeeDMSPolicySerializer(serializers.ModelSerializer):
    program = DMSProgramSerializer(read_only=True)

    class Meta:
        model = EmployeeDMSPolicy
        fields = '__all__'

class FamilyMemberDMSSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMemberDMS
        fields = '__all__'

class CharityFundSerializer(serializers.ModelSerializer):
    class Meta:
        model = social_models.CharityFund
        fields = '__all__'

class TeamPotSerializer(serializers.ModelSerializer):
    class Meta:
        model = social_models.TeamPot
        fields = '__all__'

class NewsArticleSerializer(serializers.ModelSerializer):
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = comms_models.NewsArticle
        fields = '__all__'

    def get_comments_count(self, obj):
        return obj.comments.filter(is_moderated=True).count()

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = comms_models.Notification
        fields = '__all__'

class SurveySerializer(serializers.ModelSerializer):
    responses_count = serializers.SerializerMethodField()

    class Meta:
        model = sg_models.Survey
        fields = '__all__'

    def get_responses_count(self, obj):
        return obj.responses.count()

class LotterySerializer(serializers.ModelSerializer):
    class Meta:
        model = sg_models.Lottery
        fields = '__all__'

class SupportTicketSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = support_models.SupportTicket
        fields = '__all__'

class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.full_name', read_only=True)

    class Meta:
        model = audit_models.AuditLog
        fields = '__all__'

class AnomalyTicketSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    rule_name = serializers.CharField(source='rule.name', read_only=True)

    class Meta:
        model = audit_models.AnomalyTicket
        fields = '__all__'

class PlatformSettingSerializer(serializers.ModelSerializer):
    typed_value = serializers.SerializerMethodField()

    class Meta:
        model = settings_models.PlatformSetting
        fields = '__all__'

    def get_typed_value(self, obj):
        return obj.get_typed_value()

class IntegrationChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = int_models.IntegrationChannel
        fields = '__all__'
