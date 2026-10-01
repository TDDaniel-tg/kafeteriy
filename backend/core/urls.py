from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from apps.api import views as api_views

router = DefaultRouter()
router.register(r'employees', api_views.EmployeeViewSet, basename='employee')
router.register(r'catalog', api_views.CatalogViewSet, basename='catalog')
router.register(r'orders', api_views.OrderViewSet, basename='order')
router.register(r'approvals', api_views.OrderApprovalViewSet, basename='approval')
router.register(r'campaigns', api_views.CampaignViewSet, basename='campaign')
router.register(r'support/tickets', api_views.SupportViewSet, basename='support-ticket')
router.register(r'admin/anomalies', api_views.AdminAnomalyViewSet, basename='admin-anomaly')
router.register(r'admin/audit', api_views.AdminAuditViewSet, basename='admin-audit')

def health_check(request):
    return JsonResponse({'status': 'ok', 'app': 'cafeteria', 'version': '1.0.0'})

urlpatterns = [
    path('admin/', admin.site.urls),

    # Health check for Docker / Kubernetes probes
    path('api/health/', health_check, name='health_check'),

    # OpenAPI Schema & Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Authentication & Profile
    path('api/auth/login/', api_views.login_view, name='login'),
    path('api/auth/logout/', api_views.logout_view, name='logout'),
    path('api/auth/me/', api_views.me_view, name='me'),
    path('api/auth/switch-role/', api_views.switch_demo_role_view, name='switch_role'),
    path('api/auth/setup-2fa/', api_views.setup_2fa_view, name='setup_2fa'),
    path('api/auth/verify-2fa/', api_views.verify_2fa_view, name='verify_2fa'),

    # Cart
    path('api/cart/', api_views.CartViewSet.as_view({'get': 'list'}), name='cart_list'),
    path('api/cart/add/', api_views.CartViewSet.as_view({'post': 'add'}), name='cart_add'),
    path('api/cart/remove/', api_views.CartViewSet.as_view({'post': 'remove'}), name='cart_remove'),
    path('api/cart/clear/', api_views.CartViewSet.as_view({'post': 'clear'}), name='cart_clear'),

    # Points & Balances
    path('api/points/balance/', api_views.PointsViewSet.as_view({'get': 'balance'}), name='points_balance'),
    path('api/points/history/', api_views.PointsViewSet.as_view({'get': 'history'}), name='points_history'),
    path('api/points/manual-adjust/', api_views.PointsViewSet.as_view({'post': 'manual_adjust'}), name='points_manual_adjust'),
    path('api/points/freeze/', api_views.PointsViewSet.as_view({'post': 'freeze'}), name='points_freeze'),
    path('api/points/transfer/', api_views.PointsViewSet.as_view({'post': 'transfer'}), name='points_transfer'),

    # Health & DMS
    path('api/health-dms/my-policy/', api_views.DMSViewSet.as_view({'get': 'my_policy'}), name='dms_my_policy'),
    path('api/health-dms/add-family/', api_views.DMSViewSet.as_view({'post': 'add_family_member'}), name='dms_add_family'),
    path('api/health-dms/opt-out/', api_views.DMSViewSet.as_view({'post': 'opt_out'}), name='dms_opt_out'),

    # Social & Charity
    path('api/social/funds/', api_views.SocialViewSet.as_view({'get': 'funds'}), name='charity_funds'),
    path('api/social/donate/', api_views.SocialViewSet.as_view({'post': 'donate'}), name='charity_donate'),

    # Communications
    path('api/comms/news/', api_views.CommsViewSet.as_view({'get': 'news'}), name='news_list'),
    path('api/comms/banners/', api_views.CommsViewSet.as_view({'get': 'banners'}), name='banners_list'),
    path('api/comms/notifications/', api_views.CommsViewSet.as_view({'get': 'notifications'}), name='notifications_list'),
    path('api/comms/notifications/<int:pk>/mark-read/', api_views.CommsViewSet.as_view({'post': 'mark_read'}), name='notifications_mark_read'),

    # Surveys & Gamification
    path('api/surveys/', api_views.SurveysViewSet.as_view({'get': 'list'}), name='surveys_list'),
    path('api/surveys/<int:pk>/submit/', api_views.SurveysViewSet.as_view({'post': 'submit'}), name='surveys_submit'),
    path('api/surveys/lotteries/', api_views.SurveysViewSet.as_view({'get': 'lotteries'}), name='lotteries_list'),

    # Support
    path('api/support/suggest-perk/', api_views.SupportViewSet.as_view({'post': 'suggest_perk'}), name='support_suggest_perk'),

    # Admin: Settings, Analytics & Integrations
    path('api/admin/settings/', api_views.AdminSettingsViewSet.as_view({'get': 'list', 'post': 'create'}), name='admin_settings'),
    path('api/admin/analytics/dashboard/', api_views.AdminAnalyticsViewSet.as_view({'get': 'dashboard'}), name='admin_analytics_dashboard'),
    path('api/admin/analytics/accounting-export/', api_views.AdminAnalyticsViewSet.as_view({'get': 'accounting_export'}), name='admin_accounting_export'),
    path('api/admin/analytics/payouts-export/', api_views.AdminAnalyticsViewSet.as_view({'get': 'payouts_export'}), name='admin_payouts_export'),
    path('api/admin/integrations/', api_views.AdminIntegrationsViewSet.as_view({'get': 'list'}), name='admin_integrations_list'),
    path('api/admin/integrations/<int:pk>/test/', api_views.AdminIntegrationsViewSet.as_view({'post': 'test_channel'}), name='admin_integrations_test'),

    # Router endpoints
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
