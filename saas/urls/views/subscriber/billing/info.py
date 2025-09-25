"""
URLs responding to GET requests with billing history.
"""

from ..... import settings
from .....compat import path
from .....views.billing import ChargeReceiptView, BillingStatementView
from .....views.download import BillingStatementDownloadView

try:
    from .....views.extra import PrintableChargeReceiptView
    urlpatterns = [
        path('billing/<slug:%s>/receipt/<slug:charge>/printable/' %
            settings.PROFILE_URL_KWARG,
            PrintableChargeReceiptView.as_view(),
            name='saas_printable_charge_receipt'),
        ]
except ImportError:
    urlpatterns = []

urlpatterns += [
    path('billing/<slug:%s>/receipt/<slug:charge>/' %
        settings.PROFILE_URL_KWARG,
        ChargeReceiptView.as_view(), name='saas_charge_receipt'),
    path('billing/<slug:%s>/history/download/' %
        settings.PROFILE_URL_KWARG,
        BillingStatementDownloadView.as_view(), name='saas_statement_download'),
    path('billing/<slug:%s>/history/' %
        settings.PROFILE_URL_KWARG,
        BillingStatementView.as_view(), name='saas_billing_info'),
]
