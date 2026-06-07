"""URL patterns for CRM app."""

from django.urls import path

from . import views


urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("inbox/", views.InboundRequestListView.as_view(), name="inbox-list"),
    path("inbox/create/", views.InboundRequestCreateView.as_view(), name="inbox-create"),
    path("inbox/<int:pk>/edit/", views.InboundRequestUpdateView.as_view(), name="inbox-update"),

    path("territories/", views.TerritoryListView.as_view(), name="territories-list"),
    path("territories/create/", views.TerritoryCreateView.as_view(), name="territories-create"),
    path("territories/<int:pk>/edit/", views.TerritoryUpdateView.as_view(), name="territories-update"),

    path("outlets/", views.OutletListView.as_view(), name="outlets-list"),
    path("outlets/create/", views.OutletCreateView.as_view(), name="outlets-create"),
    path("outlets/<int:pk>/edit/", views.OutletUpdateView.as_view(), name="outlets-update"),

    path("promotions/", views.PromotionListView.as_view(), name="promotions-list"),
    path("promotions/create/", views.PromotionCreateView.as_view(), name="promotions-create"),
    path("promotions/<int:pk>/edit/", views.PromotionUpdateView.as_view(), name="promotions-update"),

    path("forecasts/", views.ForecastListView.as_view(), name="forecasts-list"),
    path("forecasts/create/", views.ForecastCreateView.as_view(), name="forecasts-create"),
    path("forecasts/<int:pk>/edit/", views.ForecastUpdateView.as_view(), name="forecasts-update"),

    path("routing-rules/", views.RoutingRuleListView.as_view(), name="routing-rules-list"),
    path("routing-rules/create/", views.RoutingRuleCreateView.as_view(), name="routing-rules-create"),
    path("routing-rules/<int:pk>/edit/", views.RoutingRuleUpdateView.as_view(), name="routing-rules-update"),

    path("careers/", views.CareerApplicationListView.as_view(), name="careers-list"),
    path("careers/create/", views.CareerApplicationCreateView.as_view(), name="careers-create"),
    path("careers/<int:pk>/edit/", views.CareerApplicationUpdateView.as_view(), name="careers-update"),

    path("newsletter/", views.NewsletterSubscriptionListView.as_view(), name="newsletter-list"),
    path("newsletter/create/", views.NewsletterSubscriptionCreateView.as_view(), name="newsletter-create"),
    path("newsletter/<int:pk>/edit/", views.NewsletterSubscriptionUpdateView.as_view(), name="newsletter-update"),

    path("customers/", views.CustomerListView.as_view(), name="customers-list"),
    path("customers/create/", views.CustomerCreateView.as_view(), name="customers-create"),
    path("customers/<int:pk>/", views.CustomerDetailView.as_view(), name="customers-detail"),
    path("customers/<int:pk>/edit/", views.CustomerUpdateView.as_view(), name="customers-update"),
    path("customers/<int:customer_id>/contacts/create/", views.ContactCreateView.as_view(), name="contacts-create"),

    path("leads/", views.LeadListView.as_view(), name="leads-list"),
    path("leads/create/", views.LeadCreateView.as_view(), name="leads-create"),
    path("leads/<int:pk>/edit/", views.LeadUpdateView.as_view(), name="leads-update"),

    path("opportunities/", views.OpportunityListView.as_view(), name="opportunities-list"),
    path("opportunities/create/", views.OpportunityCreateView.as_view(), name="opportunities-create"),
    path("opportunities/<int:pk>/edit/", views.OpportunityUpdateView.as_view(), name="opportunities-update"),

    path("products/", views.ProductListView.as_view(), name="products-list"),
    path("products/create/", views.ProductCreateView.as_view(), name="products-create"),
    path("products/<int:pk>/edit/", views.ProductUpdateView.as_view(), name="products-update"),
    path("products/categories/", views.ProductCategoryListView.as_view(), name="products-categories"),
    path("products/categories/create/", views.ProductCategoryCreateView.as_view(), name="products-categories-create"),

    path("orders/", views.OrderListView.as_view(), name="orders-list"),
    path("orders/create/", views.OrderCreateView.as_view(), name="orders-create"),
    path("orders/<int:pk>/edit/", views.OrderUpdateView.as_view(), name="orders-update"),

    path("sales/", views.SalesInvoiceListView.as_view(), name="sales-list"),
    path("sales/create/", views.SalesInvoiceCreateView.as_view(), name="sales-create"),
    path("sales/<int:pk>/edit/", views.SalesInvoiceUpdateView.as_view(), name="sales-update"),
    path("sales/<int:pk>/print/", views.SalesInvoicePrintView.as_view(), name="sales-print"),
    path("sales/<int:invoice_id>/payments/create/", views.SalesInvoicePaymentCreateView.as_view(), name="sales-payment-create"),
    path(
        "sales/<int:invoice_id>/payments/<int:payment_id>/delete/",
        views.SalesInvoicePaymentDeleteView.as_view(),
        name="sales-payment-delete",
    ),

    path("support/", views.SupportCaseListView.as_view(), name="support-list"),
    path("support/create/", views.SupportCaseCreateView.as_view(), name="support-create"),
    path("support/<int:pk>/edit/", views.SupportCaseUpdateView.as_view(), name="support-update"),

    path("visits/", views.VisitReportListView.as_view(), name="visits-list"),
    path("visits/create/", views.VisitReportCreateView.as_view(), name="visits-create"),

    path("tasks/", views.TaskListView.as_view(), name="tasks-list"),
    path("tasks/create/", views.TaskCreateView.as_view(), name="tasks-create"),
    path("tasks/<int:pk>/edit/", views.TaskUpdateView.as_view(), name="tasks-update"),
    path("governance/audit/", views.GovernanceAuditTrailListView.as_view(), name="governance-audit-list"),
    path("governance/data-quality/", views.GovernanceDataQualityListView.as_view(), name="governance-data-quality-list"),
    path(
        "governance/data-quality/<int:pk>/action/",
        views.GovernanceDataQualityActionView.as_view(),
        name="governance-data-quality-action",
    ),
    path("governance/escalations/", views.GovernanceEscalationListView.as_view(), name="governance-escalations-list"),
    path(
        "governance/escalations/<int:pk>/action/",
        views.GovernanceEscalationActionView.as_view(),
        name="governance-escalations-action",
    ),
    path("governance/approvals/", views.GovernanceApprovalListView.as_view(), name="governance-approvals-list"),
    path(
        "governance/approvals/<int:pk>/action/",
        views.GovernanceApprovalActionView.as_view(),
        name="governance-approvals-action",
    ),
    path("access/users/", views.AccessUserListView.as_view(), name="access-users-list"),
    path("access/users/<int:pk>/", views.AccessUserUpdateView.as_view(), name="access-user-update"),
    path("access/assignments/", views.RoleAssignmentListView.as_view(), name="access-assignments-list"),
    path("access/assignments/create/", views.RoleAssignmentCreateView.as_view(), name="access-assignment-create"),
    path("access/assignments/<int:pk>/edit/", views.RoleAssignmentUpdateView.as_view(), name="access-assignment-update"),
    path(
        "access/assignments/<int:pk>/revoke/",
        views.RoleAssignmentRevokeView.as_view(),
        name="access-assignment-revoke",
    ),
    path("sop/studio/", views.SOPStudioView.as_view(), name="sop-studio"),
    path("sop/diagnostic/", views.SOPDiagnosticView.as_view(), name="sop-diagnostic"),
    path("sop/studio/save/", views.SOPStudioSaveView.as_view(), name="sop-studio-save"),
    path("search/", views.GlobalSearchView.as_view(), name="global-search"),
]
