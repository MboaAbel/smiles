"""
URLs updating processing information and inserting transactions
through POST requests.
"""

from ..... import settings
from .....compat import path
from .....views.billing import (CartPeriodsView, CartSeatsView,
    CardUpdateView, CartView, BalanceView, CheckoutView)


urlpatterns = [
    path('billing/<slug:%s>/checkout/' %
        settings.PROFILE_URL_KWARG,
        CheckoutView.as_view(), name='saas_checkout'),
    path('billing/<slug:%s>/cart-seats/' %
        settings.PROFILE_URL_KWARG,
        CartSeatsView.as_view(), name='saas_cart_seats'),
    path('billing/<slug:%s>/cart-periods/' %
        settings.PROFILE_URL_KWARG,
        CartPeriodsView.as_view(), name='saas_cart_periods'),
    path('billing/<slug:%s>/cart/' %
        settings.PROFILE_URL_KWARG,
        CartView.as_view(), name='saas_organization_cart'),
    path('billing/<slug:%s>/card/' %
        settings.PROFILE_URL_KWARG,
        CardUpdateView.as_view(), name='saas_update_card'),
    # Implementation Note: <subscribed_plan> (not <plan>) such that
    # the required_manager decorator does not raise a PermissionDenied
    # for a plan <organization> is subscribed to.
    path('billing/<slug:%s>/balance/<slug:subscribed_plan>/' %
        settings.PROFILE_URL_KWARG,
        BalanceView.as_view(), name='saas_subscription_balance'),
    path('billing/<slug:%s>/balance/' %
        settings.PROFILE_URL_KWARG,
        BalanceView.as_view(), name='saas_organization_balance'),
]
