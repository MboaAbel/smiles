from django.views.generic import TemplateView
from extended_templates.backends.pdf import PdfTemplateResponse

from ..mixins import ChargeMixin


class PrintableChargeReceiptView(ChargeMixin, TemplateView):
    """
    ``Charge`` receipt as printable PDF format.

    template: saas/printable_charge_receipt.html
    """
    template_name = 'saas/printable_charge_receipt.html'
    response_class = PdfTemplateResponse
