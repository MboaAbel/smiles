# Copyright (c) 2025, DjaoDjin inc.
# All rights reserved.
#
from __future__ import absolute_import

import django.template.defaultfilters
from django.utils.translation import gettext, ngettext
from jinja2.sandbox import SandboxedEnvironment as Jinja2Environment
import saas.templatetags.saas_tags

import billings.templatetags.testsite_tags


def environment(**options):
    options['extensions'] = ['jinja2.ext.i18n']

    env = Jinja2Environment(**options)

    # i18n
    env.install_gettext_callables(gettext=gettext, ngettext=ngettext,
        newstyle=True)

    # Generic filters to render pages
    env.filters['is_authenticated'] = \
        billings.templatetags.testsite_tags.is_authenticated
    env.filters['iteritems'] = saas.templatetags.saas_tags.iteritems
    env.filters['isoformat'] = saas.templatetags.saas_tags.isoformat
    env.filters['messages'] = billings.templatetags.testsite_tags.messages
    env.filters['pluralize'] = django.template.defaultfilters.pluralize
    env.filters['to_json'] = billings.templatetags.testsite_tags.to_json
    env.filters['url_profile'] = billings.templatetags.testsite_tags.url_profile

    # Specific to SaaS
    env.filters['humanize_money'] = saas.templatetags.saas_tags.humanize_money
    env.filters['humanize_period'] = saas.templatetags.saas_tags.humanize_period
    env.filters['date_in_future'] = saas.templatetags.saas_tags.date_in_future
    env.filters['md'] = saas.templatetags.saas_tags.md
    env.filters['describe'] = saas.templatetags.saas_tags.describe

    env.globals.update({
        'DATETIME_FORMAT': "MMM dd, yyyy",
    })

    return env
