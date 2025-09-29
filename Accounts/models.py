from django.db import models
from .managers import UserManager
# from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db.models import Q
from .constants import SPECIALIZATION_CHOICES, GENDER_CHOICES, BLOOD_GROUP, RELATIONSHIP_CHOICES
import string
import random
from django.urls import reverse
import uuid
from ckeditor.fields import RichTextField


def generate_service_id():
    alphanumeric = string.ascii_uppercase + string.digits
    return ''.join(random.choices(alphanumeric, k=6))

def generate_username():
     alphanumeric = string.ascii_uppercase + string.digits
     return 'SS'.join(random.choices(alphanumeric, k=4))

# Create a Custom User Model


class User(AbstractUser):
    class RoleChoices(models.TextChoices):
        DOCTOR = "doctor", "Doctor"
        PATIENT = "patient", "Patient"
        STAFF = "staff", "Staff"

    user_role = models.CharField(choices=RoleChoices.choices,max_length=20,default="Patient",error_messages={"required": "Role must be provided"},)
    username = models.CharField(null=False, max_length=50, blank=False,default=generate_username,)
    email = models.EmailField(unique=True, null=False, blank=False)
    related_clinic_name = models.ForeignKey('ClinicReg', on_delete=models.CASCADE, blank=True, null=True)
    next_of_kin = models.ForeignKey('NextOfKin', on_delete=models.CASCADE, blank=True, null=True)
    specialization = models.CharField(max_length=19, blank=True, choices=SPECIALIZATION_CHOICES,)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=False, default='icon/smile.png', blank=False)
    national_id = models.CharField(max_length=15, unique=True, blank=True, null=True)
    member_code = models.CharField(default=generate_service_id, max_length=6, unique=True)
    #mobile_number = PhoneNumberField(max_length=16,blank=False, null=True, unique=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    registered = models.BooleanField(default=False)
    open_for_mboka =models.BooleanField(default=False)
    is_clinic_owner =models.BooleanField(default=False)


    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


    def related_clinic_name(self):
         if self.user_role == User.RoleChoices.DOCTOR:
             try:
                 related_clinic_staff = ClinicStaff.objects.get(related_user=self)
                 return f"{related_clinic_staff.staff_code} {related_clinic_staff.role}"
             except ClinicStaff.DoesNotExist:
                  return "None"
         else:
              return "None"

    def set_last_login(self):
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])

    def set_last_logout(self):
        self.last_logout = timezone.now()
        self.save(update_fields=['last_logout'])

    def next_of_kin_name(self):
        if self.has_next_of_kin:
            try:
                next_of_kin = NextOfKin.objects.get(related_patient=self)
                return f"{next_of_kin.kin_first_name} {next_of_kin.kin_last_name}"
            except NextOfKin.DoesNotExist:
                return "None"
        else:
            return "None"

    # Meta class to set metadata options
    class Meta:
        ordering = ["-mobile_number"]
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __unicode__(self):
         return self.username

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse('profile-setting',args=[str(self.id)])

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip() or self.username

    def get_doctor_profile(self):
        """
        Return doctor profile URL
        """
        return reverse(
            "doctors:doctor-profile", kwargs={"username": self.username}
        )
    @property
    def rating(self):
         # Implement your rating logic here
         return 4  # Default value
    @property
    def average_rating(self):
         return (
             self.reviews_received.aggregate(Avg("rating"))["rating__avg"] or 0
         )

    @property
    def rating_count(self):
         return self.reviews_received.count()
    @property
    def rating_distribution(self):
         distribution = {i: 0 for i in range(1, 6)}
         for rating in self.reviews_received.values_list("rating", flat=True):
             distribution[rating] += 1
         return distribution


# Create a model for Next of Kin(for a Patient)
class NextOfKin(models.Model):

    kin_first_name = models.CharField(max_length=50)
    kin_code = models.CharField(max_length=15, unique=True, blank=True, null=True)
    kin_last_name = models.CharField(max_length=50)
    related_patient = models.ForeignKey(
        User,
        verbose_name='Related Patient',
        on_delete=models.CASCADE,
        limit_choices_to=Q(registered=True) | Q(mobile_number=True)
    )
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES)
    # kin_mobile_number = PhoneNumberField(max_length=13, blank=True, null=True, unique=False)
    kin_mobile_number = models.CharField(max_length=13, blank=True, null=True, unique=False)
    registered = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.kin_first_name} {self.kin_last_name}"

    class Meta:
        verbose_name = "Next of Kin"
        verbose_name_plural = "Next of Kins"





# Create a method to generate a random appointment ID
# Create a model for OTP(One Time Password)


class OTP(models.Model):
    otp_code = models.CharField(max_length=6)
    otp_created = models.DateTimeField(default=timezone.now)
    otp_verified = models.BooleanField(default=False)
    for_email = models.EmailField(null=True, blank=True, default="")

    @classmethod
    def generate_otp(cls):
        return ''.join(random.choices('0123456789', k=6))

    class Meta:
        verbose_name = "OTP"
        verbose_name_plural = "OTPs"

class Profile(models.Model):
    def profile_photo_directory_path(instance, filename):
        return "profile_photos/user_{0}/{1}".format(instance.user.id, filename)

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    registration_number = models.CharField(max_length=50,null=True,default=uuid.uuid4)
    about = models.CharField(max_length=180,blank=True, null=True)
    bio = RichTextField(blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="")
    state = models.CharField(max_length=100, blank=True)
    town_near = models.CharField(max_length=200, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True)
    county = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    is_available = models.BooleanField(default=True)
    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUP,
        blank=True,
        null=True,
    )
    allergies = models.CharField(max_length=400,null=True,blank=True)
    medical_conditions = RichTextField(null=True,blank=True)

    def __str__(self):
        return "Profile of {}".format(self.user.username)


