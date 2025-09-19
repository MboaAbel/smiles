
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.text import slugify
import uuid
from Accounts.models import User
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

class AccessToken(models.Model):
	token = models.CharField(max_length=30)
	created_at = models.DateTimeField(auto_now_add=True)
	B_token = models.CharField(max_length=30)

	class Meta:
		get_latest_by = 'created_at'

	def __str__(self):
		return self.token


class mpesa_transactions(models.Model):
        user = models.ForeignKey(User,
         verbose_name='UserPay',
         on_delete=models.CASCADE,)
        slug = models.SlugField(max_length=255, unique=True, blank=False,default=uuid.uuid4)
        Transaction_code = models.UUIDField(primary_key=True, default=uuid.uuid4)
        MerchantRequestID = models.CharField(max_length=50, null=True)
        CheckoutRequestID = models.CharField(max_length=50, null=True)
        ResponseCode = models.CharField(max_length=30, null=True)
        ResponseDescription = models.CharField(max_length=30, null=True)
        CustomerMessage = models.CharField(max_length=30, null=True)
        phone_number = models.CharField(max_length=15, null=True)
        amount = models.CharField(max_length=15, null=True)
        paid_at = models.DateTimeField(auto_now_add=True)
        account_reference = models.CharField(max_length=30)
        transaction_desc = models.CharField(max_length=30)
        occassion = models.CharField(max_length=30)
        is_finished = models.BooleanField(default=False)
        is_successful = models.BooleanField(default=False)
        timestamp = models.IntegerField(null=True)
        trans_id = models.CharField(max_length=30)


        def __str__(self):
                return f'{self.Transaction_code}'

        class Meta:
            verbose_name = _("Transaction")
            verbose_name_plural = _("Transactions")
            get_latest_by = 'paid_at'


        def get_absolute_url(self):
             return reverse('pay_stk', kwargs={'slug': self.slug},args=[str(self.id)])


# class B_AccessToken(models.Model):
# 	B_token = models.CharField(max_length=30)
# 	created_at = models.DateTimeField(auto_now_add=True)
#
# 	class Meta:
# 		get_latest_by = 'created_at'
#
# 	def __str__(self):
# 		return self.B_token

