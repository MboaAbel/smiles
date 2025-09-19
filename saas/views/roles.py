from __future__ import unicode_literals

import logging

from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.views.generic.base import RedirectView

from .. import signals
from ..compat import gettext_lazy as _
from ..mixins import product_url
from ..utils import get_role_model, validate_redirect_url

LOGGER = logging.getLogger(__name__)


class RoleGrantAcceptView(RedirectView):

    pattern_name = 'saas_organization_profile'
    permanent = False

    @property
    def role(self):
        #pylint:disable=attribute-defined-outside-init
        if not hasattr(self, '_role'):
            self._role = get_role_model().objects.filter(
                grant_key=self.kwargs.get('verification_key')).first()
        return self._role

    def get(self, request, *args, **kwargs):
        obj = self.role
        if not obj:
            # We either have a bogus `verification_key` or a `verification_key`
            # that has already been used. Either way, it is better to redirect
            # to the application page rather than showing a 404 to users
            # clicking on the link in the grant e-mail multiple times.
            return super(RoleGrantAcceptView, self).get(
                request, *args, **kwargs)

        existing_role = get_role_model().objects.filter(
            organization=obj.organization, user=request.user).exclude(
            pk=obj.pk).first()
        if existing_role:
            # We could have an `existing_role` that is actually a pending
            # request, in which case `existing_role.role_description is None`.
            messages.error(request, _("You already have a %(existing_role)s"\
                " role on %(organization)s. Please drop this role first if"\
                " you want to accept a role of %(role)s instead.") % {
                    'role': obj.role_description.title,
                    'organization': obj.organization.printable_name,
                    'existing_role': existing_role.role_description.title})
            return super(RoleGrantAcceptView, self).get(
                request, *args, organization=obj.organization)

        obj.user = request.user       # We appropriate the Role here.
        grant_key = obj.grant_key
        obj.grant_key = None
        obj.save()
        LOGGER.info("%s accepted role of %s to %s (grant_key=%s)",
            request.user, obj.role_description, obj.organization,
            grant_key, extra={
                'request': request, 'event': 'accept',
                'user': str(request.user),
                'organization': str(obj.organization),
                'role_description': str(obj.role_description),
                'grant_key': grant_key})
        signals.role_grant_accepted.send(sender=__name__,
            role=obj, grant_key=grant_key, request=request)
        messages.success(request,
            _("%(role)s role to %(organization)s accepted.") % {
                'role': obj.role_description.title,
                'organization': obj.organization.printable_name})
        return super(RoleGrantAcceptView, self).get(
            request, *args, organization=obj.organization)

    def get_redirect_url(self, *args, **kwargs):
        redirect_path = validate_redirect_url(
            self.request.GET.get(REDIRECT_FIELD_NAME, None))
        if redirect_path:
            return redirect_path
        if self.role:
            return product_url(subscriber=self.role.organization,
                request=self.request)
        return product_url(request=self.request)
