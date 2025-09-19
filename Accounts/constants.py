from django.utils.translation import gettext_lazy as _


GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
]

PATIENT_TYPE_CHOICES = [
    ('', '-----'),
    ('Member_Patient', 'Member_Patient'),
    ('NextOfKin_Patient', 'NextOfKin_Patient'),
    ('Staff', 'Staff'),
    ('New_Patient', 'New_Patient'),
]

SPECIALIZATION_CHOICES = [
    ('', '----------'),
    ('Dentistry', 'Dentistry'),
    ('Pharmacy', 'Pharmacy'),
    ('Consultation', 'Consultation'),
    ('Laboratory', 'Laboratory Tests'),
    ('Other issue', 'Other issue'), ]

APPOINTMENT_STATUS_CHOICES = (
    ('', '-----'),
    ('Revoked', 'Revoked'),
    ('Scheduled', 'Scheduled'),
    ('Cancelled', 'Cancelled'),
    ('Completed', 'Completed'),
    ('Pending','Pending'),
    ('Processing','Processing'),
)
PAYMENT_CHOICES = [
    (True, 'Verified'),
    (False, 'N/A'), ]

FOR_CHOICES = [
    ('', '-----'),
    ('self', 'Self'),
    ('next_of_kin', 'Next of Kin'),
]

BLOOD_GROUP  = [
    ("A+", "A+"),
    ("A-", "A-"),
    ("B+", "B+"),
    ("B-", "B-"),
    ("O+", "O+"),
    ("O-", "O-"),
    ("AB+", "AB+"),
    ("AB-", "AB-"),
]

RELATIONSHIP_CHOICES = [
    ('', '----------'),
    ('Brother', 'Brother'),
    ('Sister', 'Sister'),
    ('Son', 'Son'),
    ('Daughter', 'Daughter'),
    ('Mother', 'Mother'),
    ('Father', 'Father'),
    ('Aunt', 'Aunt'),
    ('Uncle', 'Uncle'),
    ('Niece', 'Niece'),
    ('Nephew', 'Nephew'),
    ('Cousin', 'Cousin'),
    ('Other close Relative', 'Other close Relative'),
    ('Wife', 'Wife'),
    ('Husband', 'Husband'),
    ('Guardian', 'Guardian'),
]

ROLE_CHOICES = [
    ('doctor', 'Doctor'),
    ('receptionist', 'Receptionist'),
    ('nurse', 'Nurse'),
    ('admin', 'Admin'),
    ('ICT','IT'),
      ]


PAYMENT_TYPES = (
    ('full', _('Full payment')),
    ('down', _('Down payment')),
)



DAYS_OF_WEEK = (
    (0, 'Sunday'),
    (1, 'Monday'),
    (2, 'Tuesday'),
    (3, 'Wednesday'),
    (4, 'Thursday'),
    (5, 'Friday'),
    (6, 'Saturday'),
)
