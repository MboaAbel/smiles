import datetime

from django.db import connection

from .humanize import as_money


def read_balances(account, until=datetime.datetime.now()):
    """Balances associated to customer accounts.

    We are executing the following SQL to find the balance
    of each customer.

    The query returns a list of tuples (organization_id, amount in cents)
    we use to create the invoices.
    example:
        (2, 1200)
        (3, 1100)

    """
    cursor = connection.cursor()
    cursor.execute(
"""select t1.dest_organization_id,
     sum(t1.dest_amount - coalesce(t2.dest_amount, 0))
from saas_transaction t1 left outer join saas_transaction t2
on t1.dest_organization_id = t2.orig_organization_id
   and t1.dest_account = t2.orig_account
where t1.dest_account = '%s' and t1.created_at < '%s' and t2.created_at < '%s'
group by t1.dest_organization_id
""" % (account, until, until))
    return cursor.fetchall()


def export(output, transactions):
    """
    Export a set of Transaction in ledger format.
    """
    for transaction in transactions:
        dest = ("\t\t%(dest_organization)s:%(dest_account)s"
                % {'dest_organization': transaction.dest_organization,
                   'dest_account': transaction.dest_account})
        dest_amount = as_money(transaction.dest_amount,
            transaction.dest_unit).rjust(60 - len(dest))
        orig = ("\t\t%(orig_organization)s:%(orig_account)s"
                % {'orig_organization': transaction.orig_organization,
                   'orig_account': transaction.orig_account})
        if transaction.dest_unit != transaction.orig_unit:
            disp_orig_amount = "-%s" % as_money(transaction.orig_amount,
                transaction.orig_unit)
            orig_amount = disp_orig_amount.rjust(60 - len(orig))
        else:
            orig_amount = ''
        output.write("""
%(created_at)s #%(reference)s - %(description)s
%(dest)s%(dest_amount)s
%(orig)s%(orig_amount)s
""" % {'created_at': datetime.datetime.strftime(
            transaction.created_at, '%Y/%m/%d %H:%M:%S'),
        'reference': '%s' % transaction.event_id,
        'description': transaction.descr,
        'dest': dest, 'dest_amount': dest_amount,
        'orig': orig, 'orig_amount': orig_amount})
