from rest_framework import serializers

from .models import  Media, WhatsMessage, Recurrence, AttachmentReminder, PatientEducation, GeneralHealthReminders, ProcedureInstruction,Room, Message, Files, Clinic, Event, VirtualMeet, Reference, Billing, RadiologyTest, RadiologyResult, Role, Users, Patient, SocialMedia, SocialMediaAccount, Allergies, SpecialNeed, Diagnosis, Surgery, Vital, Prescription, Notes, Attachment, Insurance, PatientHasSurgery, PatientHasInsurance, PatientHasVital, PatientHasPrescription, PatientHasDiagnosis, Problem, PatientHasProblem, MedicalTest, Result, ReferralDoctors, PatientHasReferralDoctors, UsersHasReferralDoctors, UsersHasPatient, Templates, UsersHasTemplates, PatientReceiveTemplates, Appointment,  Tasks, UsersHasTasks

from django.db.models import Min, Max
from django.utils import timezone
from django.contrib.auth.hashers import make_password


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'
class RecurrenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recurrence
        fields = '__all__'

class AttachmentReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachmentReminder
        fields = '__all__'

class TemplatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Templates
        fields = '__all__'

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('id', 'first_name', 'last_name', 'email', 'password','phone','role_idrole','gpt','pin','key')
        extra_kwargs = {'password': {'write_only': True}}
        
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Make sure password is write-only

    class Meta:
        model = Users
        fields = ('first_name', 'last_name', 'email', 'password', 'role_idrole')  # Include any additional fields you want to capture during registration
    def get_role_name(self, obj):
        if obj.role_idrole:
            return obj.role_idrole.name
        return None
    def create(self, validated_data):
        user = Users.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            role_idrole=validated_data['role_idrole']
        )
        user.set_password(validated_data['password'])
        user.save()
        role_name = self.get_role_name(user)
        if role_name in ['Nurse', 'Secretary']:
            # If the user is a nurse, create a room for the nurse and associate it
            room_name = f'Room for {user.email}'
            room_slug = f'room_{user.email}'
            room = Room.objects.create(name=room_name, slug=room_slug)
            welcome_message = f'Welcome to the chat!'
            Message.objects.create(room=room, user=user, content=welcome_message)
        return user

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('id', 'first_name', 'last_name', 'email', 'phone', 'password','gpt', 'pin', 'key')

    def validate_email(self, value):
        """
        Validate that the email is unique among users.
        """
        user = self.instance  # Get the user being updated
        if Users.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("Email is already in use by another user.")
        return value

    def update(self, instance, validated_data):
        """
        Update the user's profile with the validated data.
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.gpt = validated_data.get('gpt', instance.gpt)
        instance.pin= validated_data.get('pin',instance.pin)
        instance.key=validated_data.get('key',instance.key)
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)  # Set the new password

        instance.save()
        return instance
class PatientSerializer(serializers.ModelSerializer):
    last_appointment = serializers.DateTimeField(read_only=True)
    next_appointment = serializers.DateTimeField(read_only=True)
    full_name_phone = serializers.CharField(read_only=True)
    class Meta:
        model = Patient
        fields = '__all__'
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['last_appointment'] = self.get_last_appointment(instance)
        representation['next_appointment'] = self.get_next_appointment(instance)
        representation['full_name_phone']= self.get_full_name_phone(instance)
        return representation

    def get_last_appointment(self, instance):
        now = timezone.now()
        last_appointment = Appointment.objects.filter(
            patient=instance,
            startdate__lt=now  # Filter appointments that are before the current time
        ).aggregate(Max('startdate'))['startdate__max']
        
        if last_appointment is None:
            return "No appointment"
        
        return last_appointment

    def get_next_appointment(self, instance):
        now = timezone.now()
        next_appointment = Appointment.objects.filter(
            patient=instance,
            startdate__gt=now  # Filter appointments that are after the current time
        ).aggregate(Min('startdate'))['startdate__min']
        
        if next_appointment is None:
            return "No appointment"
        
        return next_appointment
    
    def get_full_name_phone(self, instance):
        full_name_phone= f"{instance.first_name} {instance.middle_name} {instance.last_name} - {instance.phone}"
        return full_name_phone

class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = '__all__'

class SocialMediaAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaAccount
        fields = '__all__'

class AllergiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergies
        fields = '__all__'

class SpecialNeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialNeed
        fields = '__all__'

class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnosis
        fields = '__all__'

class SurgerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Surgery
        fields = '__all__'

class VitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vital
        fields = '__all__'

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = '__all__'

class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = '__all__'

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = '__all__'

class InsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insurance
        fields = '__all__'

class PatientHasSurgerySerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientHasSurgery
        fields = '__all__'

class PatientHasInsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientHasInsurance
        fields = '__all__'

class PatientHasVitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientHasVital
        fields = '__all__'

class PatientHasPrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientHasPrescription
        fields = '__all__'

class PatientHasDiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientHasDiagnosis
        fields = '__all__'

class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = '__all__'

class PatientHasProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientHasProblem
        fields = '__all__'

class MedicalTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalTest
        fields = '__all__'

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = '__all__'

class ReferralDoctorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralDoctors
        fields = '__all__'

class PatientHasReferralDoctorsGetSerializer(serializers.ModelSerializer):
    referral_doctor = ReferralDoctorsSerializer(read_only=True)
    class Meta:
        model = PatientHasReferralDoctors
        fields = '__all__'

class PatientHasReferralDoctorsPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientHasReferralDoctors
        fields = '__all__'

class UsersHasReferralDoctorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersHasReferralDoctors
        fields = '__all__'

class UsersHasPatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersHasPatient
        fields = '__all__'

class UsersHasTemplatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersHasTemplates
        fields = '__all__'

class PatientReceiveTemplatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientReceiveTemplates
        fields = '__all__'

class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = '__all__'

class VirtualMeetSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualMeet
        fields = '__all__'
class ProcedureInstructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcedureInstruction
        fields = '__all__'

class PatientEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientEducation
        fields = '__all__'

class GeneralHealthRemindersSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralHealthReminders
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class TasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = '__all__'

class UsersHasTasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersHasTasks
        fields = '__all__'

class RadiologyTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RadiologyTest
        fields = '__all__'

class RadiologyResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = RadiologyResult
        fields = '__all__'

class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        fields = '__all__'

class FilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ['id','pdf']
    
class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = '__all__'    

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'    

       
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'    


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'    

       
class WhatsMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsMessage
        fields = '__all__' 