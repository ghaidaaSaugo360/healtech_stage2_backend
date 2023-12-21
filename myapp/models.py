from django.db import models
from django.db.models import Count
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import Permission, Group
from django.utils import timezone
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.core.validators import RegexValidator
class Role(models.Model):
    idrole = models.AutoField(db_column='idRole', primary_key=True)  # Field name made lowercase.
    name = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'role'
# Define a custom user manager
class UsersManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        user = self.model(email=email, **extra_fields)
    
    # Set the user as a superuser and staff
        user.is_staff = True
        user.is_superuser = True
        return self.create_user(email, password, **extra_fields)

class Users(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(db_column='ID', primary_key=True)
    first_name = models.CharField(db_column='First_name', max_length=20, blank=True, null=True)
    last_name = models.CharField(db_column='Last_name', max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(unique=True)
    role_idrole = models.ForeignKey(Role, models.DO_NOTHING, db_column='Role_idRole')
    password = models.CharField(max_length=128)  # Add the password field
    gpt= models.CharField(max_length=200, blank=True, null=True)
    pin = models.CharField(max_length=8, blank=True, null=True, validators=[
            MinLengthValidator(4),
            MaxLengthValidator(8),
            RegexValidator(r'^[0-9]*$', 'Only digits are allowed for PIN.')
        ])
    key = models.CharField(max_length=8, blank=True, null=True, validators=[
        MinLengthValidator(4),
        MaxLengthValidator(8),
        RegexValidator(r'^[a-zA-Z0-9]*$', 'Only alphanumeric characters are allowed for the key.')
    ])
    # Add any other custom fields you need

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser= models.BooleanField(default=True)
    objects = UsersManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    class Meta:
        managed = False
        db_table = 'users'

class Patient(models.Model):
    phone_regex = RegexValidator(
        regex=r'^\d{1,15}$',
        message="Phone number must be entered in the format: '9999999999'. 15 digits allowed."
    )
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    ssn = models.CharField(db_column='SSN', max_length=20, blank=True, null=True)  # Field name made lowercase.
    mrn = models.CharField(db_column='MRN', max_length=20, blank=True, null=True)  # Field name made lowercase.
    blood_type = models.CharField(db_column='Blood_type', max_length=5, blank=True, null=True)  # Field name made lowercase.
    first_name = models.CharField(db_column='First_name', max_length=30, blank=True, null=True)  # Field name made lowercase.
    last_name = models.CharField(db_column='Last_name', max_length=30, blank=True, null=True)  # Field name made lowercase.
    middle_name = models.CharField(db_column='Middle_name', max_length=30, blank=True, null=True)  # Field name made lowercase.
    dob = models.DateField(db_column='DOB', blank=True, null=True)  # Field name made lowercase.
    gender = models.CharField(db_column='Gender', max_length=10, choices=[("Male", "Male"), ("Female", "Female")], blank=True, null=True)
    email = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True, validators=[phone_regex])
    height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    address = models.CharField(db_column='Address', max_length=100, blank=True, null=True)  # Field name made lowercase.
    first_name_emergency = models.CharField(db_column='First_name_emergency', max_length=10, blank=True, null=True)  # Field name made lowercase.
    last_name_emergency = models.CharField(db_column='Last_name_emergency', max_length=15, blank=True, null=True)  # Field name made lowercase.
    phone_emergency = models.CharField(max_length=30, blank=True, null=True)
    relation_emergency = models.CharField(max_length=30, blank=True, null=True)
    @property
    def full_name_phone(self):
        return f"{self.first_name} {self.middle_name} {self.last_name} - {self.phone}"
    class Meta:
        managed = False
        db_table = 'patient'

class SocialMedia(models.Model):
    id_social = models.AutoField(db_column='ID_Social', primary_key=True)  # Field name made lowercase.
    platform = models.CharField(max_length=10, blank=True, null=True)


    class Meta:
        managed = False
        db_table = 'social_media'


class SocialMediaAccount(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, models.DO_NOTHING, db_column='Patient_ID')  # Field name made lowercase. The composite primary key (Patient_ID, Social_ID) found, that is not supported. The first column is selected.
    social = models.ForeignKey(SocialMedia, models.DO_NOTHING, db_column='Social_ID')  # Field name made lowercase.
    username = models.CharField(db_column='UserName', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'social_media_account'
       

class Allergies(models.Model):
    id=models.AutoField(primary_key=True)
    type = models.CharField(max_length=20, blank=True, null=True)
    patient = models.ForeignKey(Patient, models.DO_NOTHING, blank=True, null=True, db_column='patient')
    level= models.CharField(max_length=20, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'allergies'

class SpecialNeed(models.Model):
    id=models.AutoField(primary_key=True)
    type = models.CharField(max_length=25, blank=True, null=True)
    patient = models.ForeignKey(Patient, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'special_need'

class Diagnosis(models.Model):
    iddiagnosis = models.AutoField(db_column='idDiagnosis', primary_key=True)  # Field name made lowercase.
    notes = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'diagnosis'

class Surgery(models.Model):
    idsurgery = models.AutoField(db_column='idSurgery', primary_key=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'surgery'

class Vital(models.Model):
    idvital = models.AutoField(db_column='idVital', primary_key=True)  # Field name made lowercase.
    type = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vital'

class Prescription(models.Model):
    idprescription = models.AutoField(db_column='idPrescription', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=45, blank=True, null=True)  # Field name made lowercase.
    instruction = models.TextField(db_column='Instruction', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'prescription'

class Notes(models.Model):
    idnotes = models.AutoField(db_column='idNotes', primary_key=True)  # Field name made lowercase.
    saved_notes = models.TextField(blank=True, null=True)
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    patient = models.ForeignKey(Patient, models.DO_NOTHING, blank=True, null=True, db_column='patient')
    user = models.ForeignKey(Users, models.DO_NOTHING, db_column='User_id', blank=True, null=True, related_name='created_notes')  # Field name made lowercase.
    title=models.CharField(max_length=30, blank=True, null=True)
    last_update=models.ForeignKey(Users, models.DO_NOTHING, db_column='last_update', blank=True, null=True, related_name='updated_notes')
    class Meta:
        managed = False
        db_table = 'notes'

class Attachment(models.Model):
    idattachment = models.AutoField(db_column='idAttachment', primary_key=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=20, blank=True, null=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=500, blank=True, null=True)  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    patient = models.ForeignKey(Patient, models.DO_NOTHING, blank=True, db_column='patient')
    files=models.BinaryField(blank=True, null=True)
    attachment_file = models.FileField(upload_to='attachments/')
    def __str__(self):
        return self.attachment_file
    class Meta:
        managed = False
        db_table = 'attachment'


class Files(models.Model):
    pdf = models.FileField(upload_to='store/pdfs/')
    def __str__(self):
        return self.pdf
    class Meta:
        managed = False
        db_table = 'myapp_files'

class Insurance(models.Model):
    idinsurance = models.AutoField(db_column='idInsurance', primary_key=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=20, blank=True, null=True)  # Field name made lowercase.
    insurance_company = models.CharField(db_column='Insurance_company', max_length=30, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'insurance'

class PatientHasSurgery(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, models.DO_NOTHING, db_column='Patient_ID')  # Field name made lowercase.
    surgery_idsurgery = models.ForeignKey(Surgery, models.DO_NOTHING, db_column='Surgery_idSurgery')  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'patient_has_surgery'
class PatientHasInsurance(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, models.DO_NOTHING, db_column='Patient_ID')  # Field name made lowercase.
    insurance_idinsurance = models.ForeignKey(Insurance, models.DO_NOTHING, db_column='Insurance_idInsurance')  # Field name made lowercase.
    document = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'patient_has_insurance'

class PatientHasVital(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, models.DO_NOTHING, db_column='Patient_ID')  # Field name made lowercase.
    vital_idvital = models.ForeignKey(Vital, models.DO_NOTHING, db_column='Vital_idVital')  # Field name made lowercase.
    value = models.CharField(db_column='Value', max_length=45, blank=True, null=True)  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'patient_has_vital'

class PatientHasPrescription(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, models.DO_NOTHING, db_column='Patient_ID')  # Field name made lowercase.
    prescription_idprescription = models.ForeignKey(Prescription, models.DO_NOTHING, db_column='Prescription_idPrescription')  # Field name made lowercase.
    dose = models.CharField(db_column='Dose', max_length=200, blank=True, null=True)  # Field name made lowercase.
    duration = models.CharField(db_column='Duration',max_length=200, blank=True, null=True)  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    unit = models.CharField(db_column='Unit', max_length=45, blank=True, null=True)  # Field name made lowercase.
    strength=models.CharField(db_column='Strength', max_length=20, blank=True, null=True)
    reason=models.TextField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'patient_has_prescription'



class PatientHasDiagnosis(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, models.DO_NOTHING, db_column='Patient_ID')  # Field name made lowercase.
    diagnosis_iddiagnosis = models.ForeignKey(Diagnosis, models.DO_NOTHING, db_column='Diagnosis_idDiagnosis')  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'patient_has_diagnosis'

class Problem(models.Model):
    id=models.AutoField(db_column='ICD',primary_key=True)
    icd = models.CharField(db_column='ICD_number',max_length=15, blank=True, null=True)  # Field name made lowercase.
    problem_desc = models.TextField( blank=True, null=True)  # Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'problem'

class PatientHasProblem(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, models.DO_NOTHING, db_column='Patient_ID')  # Field name made lowercase.
    icd_problem = models.ForeignKey(Problem, models.DO_NOTHING, db_column='ICD_problem')  # Field name made lowercase.
    date = models.DateField(db_column='Date', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'patient_has_problem'

class MedicalTest(models.Model):
    idmedical_test = models.AutoField(db_column='idMedical_test', primary_key=True)  # Field name made lowercase.
    test_name = models.CharField(max_length=45, blank=True, null=True)
    test_code = models.CharField(max_length=10, blank=True, null=True)
    normal_average = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    minimum=models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    maximum=models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'medical_test'
    def save(self, *args, **kwargs):
        if self.minimum is not None and self.maximum is not None:
            self.normal_average = (self.minimum + self.maximum) / 2
        super().save(*args, **kwargs)

class Result(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, models.DO_NOTHING, db_column='Patient_ID')  # Field name made lowercase.
    medical_test_idmedical_test = models.ForeignKey(MedicalTest, models.DO_NOTHING, db_column='Medical_test_idMedical_test')  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    value = models.DecimalField(db_column='Value', max_digits=10, decimal_places=5, blank=True, null=True)  # Field name made lowercase.
    value_type = models.CharField(db_column='vaue_type', max_length=20, blank=True, null=True)
    receive_type = models.CharField(max_length=10, blank=True, null=True)
    lab_date=models.DateField(blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'result'

    def save(self, *args, **kwargs):
        # Calculate the related medical test's minimum and maximum values
        medical_test = self.medical_test_idmedical_test
        minimum = medical_test.minimum
        maximum = medical_test.maximum

        if minimum is not None and maximum is not None:
            if minimum <= self.value <= maximum:
                self.value_type = 'normal'
            elif self.value < minimum:
                self.value_type = 'deficiency'
            else:
                self.value_type = 'sufficiency'

        super().save(*args, **kwargs)
class RadiologyTest(models.Model):
    idradiology_test = models.AutoField(primary_key=True)
    test_name = models.CharField(max_length=100, blank=True, null=True)
    test_code = models.CharField(max_length=10, blank=True, null=True)
    imaging_type = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'radiology_test'

class RadiologyResult(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, models.DO_NOTHING, db_column='Patient_ID')
    radiology_test = models.ForeignKey(RadiologyTest, models.DO_NOTHING, db_column='Radiology_test_id')
    date = models.DateTimeField(db_column='Date', blank=True, null=True)
    result_text = models.TextField(db_column='Result_Text', blank=True, null=True)
    conclusion = models.CharField(max_length=200, blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, null=True)
    rad_date=models.DateField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'radiology_result'
class ReferralDoctors(models.Model):
    idreferral_doctors = models.AutoField(db_column='idReferral_Doctors', primary_key=True)  # Field name made lowercase.
    first_name = models.CharField(db_column='First_name', max_length=20, blank=True, null=True)  # Field name made lowercase.
    last_name = models.CharField(db_column='Last_name', max_length=20, blank=True, null=True)  # Field name made lowercase.
    middle_name=models.CharField(db_column='Middle_name', max_length=20, blank=True, null=True)
    email = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    speciality = models.CharField(max_length=20, blank=True, null=True)
    sub_speciality = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'referral_doctors'


class PatientHasReferralDoctors(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, models.DO_NOTHING, db_column='Patient_ID')  # Field name made lowercase.
    referral_doctor = models.ForeignKey(ReferralDoctors, models.DO_NOTHING, db_column='Referral_doctor')  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    reason = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'patient_has_referral_doctors'

class UsersHasReferralDoctors(models.Model):
    id = models.AutoField(primary_key=True)
    users = models.ForeignKey(Users, models.DO_NOTHING, db_column='Users_ID')  # Field name made lowercase.
    referral_doctor = models.ForeignKey(ReferralDoctors, models.DO_NOTHING, db_column='Referral_doctor')  # Field name made lowercase.
    date = models.DateField(db_column='Date', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'users_has_referral_doctors'  

class UsersHasPatient(models.Model):
    id = models.AutoField(primary_key=True)
    users = models.ForeignKey(Users, models.DO_NOTHING, db_column='Users_ID')  # Field name made lowercase.
    patient = models.ForeignKey(Patient, models.DO_NOTHING, db_column='Patient_ID')  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'users_has_patient'

# class Templates(models.Model):
#     idtemplates = models.AutoField(db_column='idTemplates', primary_key=True)  # Field name made lowercase.
#     name = models.CharField(max_length=45, blank=True, null=True)
#     type = models.CharField(max_length=20, blank=True, null=True)
#     body = models.TextField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'templates'  

class Templates(models.Model):
    idTemplates = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, null=True,blank=True, db_column="Name")
    type = models.CharField(max_length=50, null=True, blank=True)
    subType = models.CharField(max_length=50, null=True, blank=True, db_column="subtype")
    body = models.TextField(null=True)
    expire=models.BooleanField(default=True, blank=True, null=True) 
    class Meta:
        managed = False
        db_table = 'templates' 

class Recurrence(models.Model):
    idrecurrence = models.AutoField(primary_key=True)
    send = models.CharField(max_length=20, null=True)
    appointment = models.CharField(max_length=20, null=True)
    type = models.CharField(max_length=20, null=True)
    occurrence = models.CharField(max_length=20,null=True)
    templateID = models.ForeignKey(Templates, models.DO_NOTHING, db_column='templateID',null=True)

    class Meta:
        managed = False
        db_table='recurrence'

class AttachmentReminder(models.Model):
    idAttachment = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500, null=True)
    Date = models.DateTimeField(null=True)
    type = models.CharField(max_length=100, null=True)
    files = models.BinaryField(null=True)
    templateID = models.ForeignKey(Templates, models.DO_NOTHING , db_column='templateID',null=True)
    attachment_file = models.FileField(upload_to='templates/')
    def __str__(self):
        return self.attachment_file
    class Meta:
        managed = False
        db_table = 'attachmentreminder'

class UsersHasTemplates(models.Model):
    id = models.AutoField(primary_key=True)
    users = models.ForeignKey(Users, models.DO_NOTHING, db_column='Users_ID')  # Field name made lowercase.
    templates_idtemplates = models.ForeignKey(Templates, models.DO_NOTHING, db_column='Templates_idTemplates')  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'users_has_templates'    



class Clinic(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(db_column='name_clinic',max_length=20, blank=True, null=True)
    location=models.TextField( db_column='location_clinic', blank=True, null=True)
    color=models.CharField(max_length=20, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'clinic'

class ProcedureInstruction(models.Model):
    id=models.AutoField(primary_key=True)
    name = models.CharField(max_length=20,db_column='name')
    class Meta:
        managed = False
        db_table = 'procedure_instruction'

class PatientEducation(models.Model):
    id=models.AutoField(primary_key=True)
    name = models.CharField(max_length=20,db_column='name')
    class Meta:
        managed = False
        db_table = 'patient_education'

class GeneralHealthReminders(models.Model):
    id=models.AutoField(primary_key=True)
    name = models.CharField(max_length=20,db_column='name')

    class Meta:
        managed = False
        db_table = 'general_health_reminders'




class VirtualMeet(models.Model):
    id=models.AutoField(primary_key=True)
    platform=models.CharField(max_length=20, blank=True, null=True)
    url=models.TextField( db_column='url_virtual', blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'virtual_meet'

class Appointment(models.Model):
    idappointment = models.AutoField(db_column='idAppointment', primary_key=True)  # Field name made lowercase.
    type = models.ForeignKey(ProcedureInstruction, models.DO_NOTHING,db_column='type', blank=True, null=True)
    nature = models.CharField(max_length=10,choices=[("Clinic", "Clinic"), ("Virtual", "Virtual")], blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    startdate = models.DateTimeField( blank=True, null=True)  # Field name made lowercase.
    end_date = models.DateTimeField( blank=True, null=True)  
    notes = models.TextField(blank=True, null=True)
    patient = models.ForeignKey(Patient, models.DO_NOTHING, db_column='patient_id', blank=True, null=True)  # Field name made lowercase.
    chief=models.CharField(max_length=50, blank=True, null=True)
    clinic=models.ForeignKey(Clinic, models.DO_NOTHING, db_column='clinic_id', blank=True, null=True)
    title= models.CharField(max_length=30,blank=True, null=True )
    online=models.ForeignKey(VirtualMeet, models.DO_NOTHING, db_column='virtual_id', blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'appointment'
 
 

class PatientReceiveTemplates(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.DO_NOTHING, db_column='patient_id',blank=True, null=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.DO_NOTHING, db_column='appointment_id',blank=True, null=True)
    templates = models.ForeignKey(Templates, on_delete=models.DO_NOTHING, db_column='templates_id',blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    initial_date = models.DateTimeField(blank=True, null=True)
    status = models.BooleanField(default=False, blank=True, null=True)  
    message_updated=models.BooleanField(default=False, blank=True, null=True)  
    initial_date_str = models.CharField(max_length=255, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'patient_receive_templates'

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=30,blank=True, null=True )
    notes = models.TextField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'event'
class Tasks(models.Model):
    idtasks = models.AutoField(db_column='idTasks', primary_key=True)  # Field name made lowercase.
    body = models.TextField(blank=True, null=True)
    task_date=models.DateTimeField(blank=True, null=True)
    title=models.CharField(max_length=30, blank=True, null=True)
    user = models.ForeignKey(Users, models.DO_NOTHING, db_column='user') 
    class Meta:
        managed = False
        db_table = 'tasks'

class UsersHasTasks(models.Model):
    id = models.AutoField(primary_key=True)
    users = models.ForeignKey(Users, models.DO_NOTHING, db_column='Users_ID')  # Field name made lowercase. The composite primary key (Users_ID, Tasks_idTasks) found, that is not supported. The first column is selected.
    tasks_idtasks = models.ForeignKey(Tasks, models.DO_NOTHING, db_column='Tasks_idTasks')  # Field name made lowercase.
    body = models.TextField(blank=True, null=True)
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'users_has_tasks'
        


class Billing(models.Model):
    billing_id = models.AutoField(primary_key=True)
    patient_id = models.ForeignKey(Patient, models.DO_NOTHING, db_column='patient_id')
    invoice_number = models.CharField(max_length=20, blank=True, null=True)
    invoice_date = models.DateField(blank=True, null=True)
    invoice_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'billing'





class Reference(models.Model):
    id = models.AutoField(primary_key=True)
    url_ref = models.CharField(max_length=200, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reference'


class Room(models.Model):
    id= models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    doctor = models.ForeignKey(Users, related_name='doctor_rooms', null=True, blank=True, db_column='doctor_id', on_delete=models.CASCADE)
    nurse = models.ForeignKey(Users, related_name='nurse_rooms', null=True, blank=True, db_column='nurse_id', on_delete=models.CASCADE)
    class Meta:
        managed = False
        db_table = 'room'

class Message(models.Model):
    id= models.AutoField(primary_key=True)
    room = models.ForeignKey(Room, related_name='messages', null=True, blank=True, db_column='room_id', on_delete=models.CASCADE)
    user = models.ForeignKey(Users, related_name='messages', null=True, blank=True, db_column='user_id', on_delete=models.CASCADE)
    content = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ('date_added',)
        managed = False
        db_table = 'message'


class Media(models.Model):
    id= models.AutoField(primary_key=True)
    media_id = models.CharField(max_length=255, null=True, blank=True)
    media_type = models.CharField(max_length=255, null=True, blank=True)
    media_data = models.FileField(upload_to='whats_files/')
    class Meta:
        managed = False
        db_table = 'media'

class WhatsMessage(models.Model):
    id= models.AutoField(primary_key=True)
    text = models.TextField(null=True, blank=True)
    user = models.ForeignKey(Users, db_column='user',on_delete=models.CASCADE, null=True, blank=True, related_name='sent_messages')
    patient = models.ForeignKey(Patient,db_column='patient', on_delete=models.CASCADE, null=True, blank=True, related_name='received_messages')
    media = models.ForeignKey(Media, db_column='media_id', on_delete=models.CASCADE, null=True, blank=True, related_name='messages')
    sent_timestamp = models.DateTimeField(auto_now_add=True)
    received_time=models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=18, decimal_places=15, null=True, blank=True)
    longitude = models.DecimalField(max_digits=18, decimal_places=15, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'whatsmessage'