from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .auth import CookieTokenObtainPairView, CookieTokenRefreshView, LogoutView

router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="users")
router.register(r"user-security", views.UserSecurityProfileViewSet, basename="user-security")
router.register(r"role-assignments", views.RoleAssignmentViewSet, basename="role-assignments")
router.register(r"customers", views.CustomerViewSet, basename="customers")
router.register(r"territories", views.TerritoryViewSet, basename="territories")
router.register(r"outlets", views.OutletViewSet, basename="outlets")
router.register(r"contacts", views.ContactViewSet, basename="contacts")
router.register(r"leads", views.LeadViewSet, basename="leads")
router.register(r"inbound", views.InboundRequestViewSet, basename="inbound")
router.register(r"careers", views.CareerApplicationViewSet, basename="careers")
router.register(r"newsletter", views.NewsletterSubscriptionViewSet, basename="newsletter")
router.register(r"approval-policies", views.ApprovalPolicyViewSet, basename="approval-policies")
router.register(r"approvals", views.ApprovalRequestViewSet, basename="approvals")
router.register(r"data-quality", views.DataQualityIssueViewSet, basename="data-quality")
router.register(r"sla-escalations", views.SlaEscalationViewSet, basename="sla-escalations")
router.register(r"audit-trail", views.AuditTrailViewSet, basename="audit-trail")
router.register(r"opportunities", views.OpportunityViewSet, basename="opportunities")
router.register(r"promotions", views.PromotionViewSet, basename="promotions")
router.register(r"forecasts", views.ForecastViewSet, basename="forecasts")
router.register(r"routing-rules", views.RoutingRuleViewSet, basename="routing-rules")
router.register(r"products/categories", views.ProductCategoryViewSet, basename="product-categories")
router.register(r"products", views.ProductViewSet, basename="products")
router.register(r"orders", views.OrderViewSet, basename="orders")
router.register(r"order-items", views.OrderItemViewSet, basename="order-items")
router.register(r"invoices", views.InvoiceViewSet, basename="invoices")
router.register(r"invoice-items", views.InvoiceItemViewSet, basename="invoice-items")
router.register(r"invoice-payments", views.InvoicePaymentViewSet, basename="invoice-payments")
router.register(r"support", views.SupportCaseViewSet, basename="support")
router.register(r"visits", views.VisitReportViewSet, basename="visits")
router.register(r"tasks", views.TaskViewSet, basename="tasks")

urlpatterns = [
    path("auth/csrf/", views.CsrfTokenView.as_view(), name="auth-csrf"),
    path("auth/login/", CookieTokenObtainPairView.as_view(), name="auth-login"),
    path("auth/refresh/", CookieTokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", views.MeView.as_view(), name="auth-me"),
    path("analytics/kpi/", views.KpiSummaryView.as_view(), name="kpi-summary"),
    path("analytics/alerts/", views.AlertsSummaryView.as_view(), name="alerts-summary"),
    path("observability/summary/", views.ObservabilitySummaryView.as_view(), name="observability-summary"),
    path("search/", views.GlobalSearchAPIView.as_view(), name="global-search"),
    path("public/leads/", views.PublicLeadCreateAPIView.as_view(), name="public-leads-create"),
    path("public/inbound/", views.PublicLeadCreateAPIView.as_view(), name="public-inbound-create"),
    path("public/careers/", views.PublicCareerCreateAPIView.as_view(), name="public-careers-create"),
    path("public/newsletter/", views.PublicNewsletterCreateAPIView.as_view(), name="public-newsletter-create"),
    path("", include(router.urls)),
]
