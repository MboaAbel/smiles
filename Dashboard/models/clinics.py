from django.db import models
from Accounts.models import User
from django.utils.text import slugify
import uuid
from django.db.models import Q



# Create your models here.
class ClinicReg(models.Model):
    member = models.OneToOneField(User, on_delete=models.CASCADE,null=True, related_name='owned_clinic')
    clinic_code = models.UUIDField(primary_key=True, default=uuid.uuid4)
    clinic_name = models.CharField(max_length=120, null=True)
    clinic_email = models.CharField(max_length=120)
    clinic_logo = models.ImageField(upload_to='sp/', null=True,default='icon/bondijunction_dentalclinic_logo-300x258.jpg', blank=False)
    clinic_url = models.URLField(max_length=120, default='smileslot.onrender.com')
    mobile_number = models.CharField(max_length=15)
    reg_date_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    clinic_location = models.CharField(max_length=120, null=True)
    registered = models.BooleanField(default=False)

    def __str__(self):
        if self.member:
            return f"{self.clinic_name} - {self.mobile_number}"
        else:
            return f"User not associated - {self.clinic_name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.clinic_name + '--owner--' + self.member.username)
        super().save(*args, **kwargs)
    def get_absolute_url(self):
        return reverse('Dashboard:clinic-detail', kwargs={'slug': self.slug},args=[str(self.id)])


    def get_smile_link(self):
        """
        Return the clinic_name plus the registered_url, with a space in between.
        """
        smile_link = f"{self.clinic_url}/clinics/{self.clinic_code}"
        return smile_link.strip() or self.clinic_url

    def get_clinic_profile(self):
        """
        Return clinic profile URL
        """
        return reverse(
             "doctors:clinic-profile", kwargs={"clinic_code": self.clinic_code}
         )


class Review(models.Model):
     clinic = models.ForeignKey(
         ClinicReg, on_delete=models.CASCADE, related_name="clinic_reviews"
     )
     patient = models.ForeignKey(
         User, on_delete=models.CASCADE, related_name="clinic_reviews"
     )
     rating = models.PositiveSmallIntegerField(
         choices=[(i, i) for i in range(1, 6)]
     )
     comment = models.TextField()
     created_at = models.DateTimeField(auto_now_add=True)

     class Meta:
         unique_together = ["clinic", "patient"]
         ordering = ["-created_at"]
