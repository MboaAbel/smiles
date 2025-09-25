"""
Urls to metrics
"""

from .... import settings
from ....compat import path
from ....views.download import (CartItemDownloadView, BalancesDueDownloadView,
    BalancesMetricsDownloadView, CustomerMetricsDownloadView,
    RevenueMetricsDownloadView)
from ....views.profile import DashboardView
from ....views.metrics import (SubscribersActivityView,
    CouponMetricsView, LifeTimeValueDownloadView,
    LifeTimeValueMetricsView, PlansMetricsView, RevenueMetricsView,
    BalancesDueView)


urlpatterns = [
    path('metrics/<slug:%s>/coupons/download/' %
        settings.PROFILE_URL_KWARG,
        CartItemDownloadView.as_view(),
        name='saas_metrics_coupons_download'),
    path('metrics/<slug:%s>/coupons/<slug:coupon>/download/' %
        settings.PROFILE_URL_KWARG,
        CartItemDownloadView.as_view(), name='saas_coupon_uses_download'),
    path('metrics/<slug:%s>/coupons/<slug:coupon>/' %
        settings.PROFILE_URL_KWARG,
        CouponMetricsView.as_view(), name='saas_metrics_coupon'),
    path('metrics/<slug:%s>/coupons/' %
        settings.PROFILE_URL_KWARG,
        CouponMetricsView.as_view(), name='saas_metrics_coupons'),
    path('metrics/<slug:%s>/dashboard/' %
        settings.PROFILE_URL_KWARG,
        DashboardView.as_view(), name='saas_dashboard'),
    path('metrics/<slug:%s>/revenue/download/'
         % settings.PROFILE_URL_KWARG,
        RevenueMetricsDownloadView.as_view(),
         name='saas_metrics_revenue_download'),
    path('metrics/<slug:%s>/balances/download/'
         % settings.PROFILE_URL_KWARG,
         BalancesMetricsDownloadView.as_view(),
         name='saas_metrics_balances_download'),
    path('metrics/<slug:%s>/customers/download/'
         % settings.PROFILE_URL_KWARG,
         CustomerMetricsDownloadView.as_view(),
         name='saas_metrics_customers_download'),
    path('metrics/<slug:%s>/revenue/' %
        settings.PROFILE_URL_KWARG,
        RevenueMetricsView.as_view(), name='saas_metrics_summary'),
    path('metrics/<slug:%s>/plans/' %
        settings.PROFILE_URL_KWARG,
        PlansMetricsView.as_view(), name='saas_metrics_plans'),
    path('metrics/<slug:%s>/lifetimevalue/download/' %
        settings.PROFILE_URL_KWARG,
        LifeTimeValueDownloadView.as_view(),
        name='saas_metrics_lifetimevalue_download'),
    path('metrics/<slug:%s>/lifetimevalue/' %
        settings.PROFILE_URL_KWARG,
        LifeTimeValueMetricsView.as_view(), name='saas_metrics_lifetimevalue'),
    path('metrics/<slug:%s>/activity/' %
        settings.PROFILE_URL_KWARG,
        SubscribersActivityView.as_view(),
        name='saas_subscribers_activity'),
    path('metrics/<slug:%s>/balances-due/download/'
         % settings.PROFILE_URL_KWARG,
         BalancesDueDownloadView.as_view(),
         name='saas_metrics_balances_due_download'),
    path('metrics/<slug:%s>/balances-due/' %
         settings.PROFILE_URL_KWARG,
         BalancesDueView.as_view(),
         name='saas_metrics_balances_due'),
]
