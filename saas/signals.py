from django.dispatch import Signal

#pylint: disable=invalid-name
profile_updated = Signal(
#    providing_args=['organization', 'changes', 'user']
)
plan_created = Signal(
#    providing_args=['plan']
)
plan_updated = Signal(
#    providing_args=['plan']
)
bank_updated = Signal(
#    providing_args=['organization', 'user']
)
card_updated = Signal(
#    providing_args=['organization', 'user', 'old_card', 'new_card']
)
charge_updated = Signal(
#    providing_args=['charge', 'user']
)
order_executed = Signal(
#    providing_args=['invoiced_items', 'user']
)
claim_code_generated = Signal(
#    providing_args=['subscriber', 'claim_code', 'user']
)
expires_soon = Signal(
#    providing_args=['subscription', 'nb_days']
)
card_expires_soon = Signal(
#    providing_args=['organization', 'nb_days']
)
subscription_upgrade = Signal(
#    providing_args=['subscription', 'nb_days']
)
payment_method_absent = Signal(
#    providing_args=['organization']
)
user_invited = Signal(
#    providing_args=['user', 'invited_by']
)
processor_setup_error = Signal(
#    providing_args=['provider', 'error_message', 'customer']
)
renewal_charge_failed = Signal(
#    providing_args=['invoiced_items', 'total_price', 'final_notice']
)
role_grant_accepted = Signal(
#    providing_args=['role', 'grant_key']
)
role_grant_created = Signal(
#    providing_args=['role', 'reason']
)
# There is no `role_request_accepted` because a `role_grant_created`
# will already be triggered when the request is accepted.
role_request_created = Signal(
#    providing_args=['role', 'reason']
)
subscription_grant_accepted = Signal(
#    providing_args=['subscription', 'grant_key']
)
subscription_grant_created = Signal(
#    providing_args=['subscription', 'reason', 'invite']
)
subscription_request_accepted = Signal(
#    providing_args=['subscription', 'request_key']
)
subscription_request_created = Signal(
#    providing_args=['subscription', 'reason']
)
period_sales_report_created = Signal(
#    providing_args=['provider', 'dates', 'data', 'unit', 'scale']
)
quota_reached = Signal(
#   providing_args=['usage', 'use_charge', 'subscription']
)
use_charge_limit_crossed = Signal(
#    providing_args=['usage', 'use_charge', 'subscription']
)
