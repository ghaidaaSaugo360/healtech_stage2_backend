from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView 
from rest_framework import viewsets
from .models import Media, WhatsMessage,Recurrence, AttachmentReminder, ProcedureInstruction, GeneralHealthReminders, PatientEducation,Room, Message,Role, Event, Reference, Files, Clinic, VirtualMeet, Users, Patient, SocialMedia, SocialMediaAccount, Allergies, SpecialNeed, Diagnosis, Surgery, Vital, Prescription, Notes, Attachment, Insurance, PatientHasSurgery, PatientHasInsurance, PatientHasVital, PatientHasPrescription, PatientHasDiagnosis, Problem, PatientHasProblem, MedicalTest, Result, ReferralDoctors, PatientHasReferralDoctors, UsersHasReferralDoctors, UsersHasPatient, Templates, UsersHasTemplates, PatientReceiveTemplates, Appointment, Tasks, UsersHasTasks, RadiologyResult, RadiologyTest, Billing
from .serializers import MediaSerializer, WhatsMessageSerializer, PatientEducationSerializer, ProcedureInstructionSerializer, GeneralHealthRemindersSerializer, RecurrenceSerializer, AttachmentReminderSerializer, RoomSerializer, MessageSerializer, EventSerializer, ProfileUpdateSerializer, UserRegistrationSerializer, RoleSerializer,ReferenceSerializer, FilesSerializer, ClinicSerializer, VirtualMeetSerializer, UsersSerializer, PatientSerializer, SocialMediaSerializer, SocialMediaAccountSerializer, AllergiesSerializer, SpecialNeedSerializer, DiagnosisSerializer, SurgerySerializer, VitalSerializer, PrescriptionSerializer, NotesSerializer, AttachmentSerializer, InsuranceSerializer, PatientHasSurgerySerializer, PatientHasInsuranceSerializer, PatientHasVitalSerializer, PatientHasPrescriptionSerializer, PatientHasDiagnosisSerializer, ProblemSerializer, PatientHasProblemSerializer, MedicalTestSerializer, ResultSerializer, ReferralDoctorsSerializer,PatientHasReferralDoctorsPostSerializer,PatientHasReferralDoctorsGetSerializer, UsersHasReferralDoctorsSerializer, UsersHasPatientSerializer, TemplatesSerializer, UsersHasTemplatesSerializer, PatientReceiveTemplatesSerializer, AppointmentSerializer, TasksSerializer, UsersHasTasksSerializer, RadiologyTestSerializer, RadiologyResultSerializer, BillingSerializer
from django.http import JsonResponse
from rest_framework.generics import RetrieveUpdateAPIView
from django.http import HttpResponse, JsonResponse
from rest_framework import generics
from django.http import FileResponse
from django.http import Http404
from django.shortcuts import get_object_or_404
import subprocess
from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q,F, Value as V
from django.db.models.functions import Concat


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Recurrence

@api_view(['GET'])
def get_recurrence_and_template(request, idrecurrence=None):
    try:
        if idrecurrence is not None:
            # Fetch the specific recurrence and template based on idrecurrence
            recurrence = Recurrence.objects.select_related('templateID').get(idrecurrence=idrecurrence)

            # Access fields from both models
            result = {
                'idrecurrence': recurrence.idrecurrence,
                'send': recurrence.send,
                'appointment': recurrence.appointment,
                'type': recurrence.type,
                'occurrence': recurrence.occurrence,
                'templateID': {
                    'idTemplates': recurrence.templateID.idTemplates,
                    'name': recurrence.templateID.name,
                    'type': recurrence.templateID.type,
                    'subType': recurrence.templateID.subType,
                    'body': recurrence.templateID.body,
                    'expire': recurrence.templateID.expire,
                }
            }

            return Response({'result': result}, status=status.HTTP_200_OK)
        else:
            # Fetch all recurrences and templates
            queryset = Recurrence.objects.select_related('templateID')

            # Access fields from both models
            result = list(queryset.values(
                'idrecurrence',         # Recurrence model fields
                'send',
                'appointment',
                'type',
                'occurrence',
                'templateID__idTemplates',  # Access fields from the related Templates model
                'templateID__name',
                'templateID__type',
                'templateID__subType',
                'templateID__body',
                'templateID__expire'
            ))

            return Response({'result': result}, status=status.HTTP_200_OK)

    except Recurrence.DoesNotExist:
        # Return a 404 response if the recurrence is not found
        return Response({'error': 'Recurrence not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # Handle other exceptions, log them, and return an appropriate response
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

class UsersViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def list(self, request, *args, **kwargs):
        if 'all' in request.query_params:
            return super().list(request, *args, **kwargs)
        else:
            user = request.user
            serializer = self.get_serializer(user)
            return Response(serializer.data)

@api_view(['POST'])
def verify_password(request):
    # Get the user's old password from the request
    old_password = request.data.get('old_password')

    # Get the authenticated user
    user = request.user

    # Check if the old password matches the user's current password
    if user.check_password(old_password):
        return Response({'success': True, 'message': 'Password verified successfully'})
    else:
        return Response({'success': False, 'message': 'Old password does not match'}, status=status.HTTP_400_BAD_REQUEST)

class ProfileUpdateView(generics.UpdateAPIView):
    queryset = Users.objects.all()  # Assuming Users is the model for user profiles
    serializer_class = ProfileUpdateSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

class ProfileView(RetrieveUpdateAPIView):
    serializer_class = ProfileUpdateSerializer
    queryset = Users.objects.all()
    lookup_field = 'email'  # Assuming email is used to identify the user

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRegistration(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def logout_view(request):
    # Log the user out
    logout(request)
    return Response({"message": "User logged out successfully"})

@api_view(['POST'])
def custom_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(request, username=username, password=password)

    if user:
        # If the user is valid, log them in
        login(request, user)
        print("user", user)
        # Generate or get the token for the user
        token, created = Token.objects.get_or_create(user=user)
        user_role = user.role_idrole  # Assuming 'user.role_roleid' is a foreign key to the 'Role' model
        role_name = user_role.name  # Access the 'name' field of the 'Role' model
        print ("user toke", token.user)
        return Response({'token': token.key, 'role': role_name})
    else:
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@permission_classes([IsAuthenticated])       
@api_view(['GET'])
def rooms(request):
    user = request.user
    role_name = user.role_idrole.name if user.role_idrole else None
    print(f'User: {user.email}, Role: {role_name}')
    if role_name in ['Nurse', 'Secretary']:
        rooms = Room.objects.filter(name=f'Room for {user.email}')
    else:
        rooms = Room.objects.all()

    serializer = RoomSerializer(rooms, many=True)
    return Response({'rooms': serializer.data})

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def room(request, id):
    print(f"room")
    room = get_object_or_404(Room, pk=id)
    messages = Message.objects.filter(room=room)
    print(f'request: {request}')
    room_serializer = RoomSerializer(room)
    message_serializer = MessageSerializer(messages, many=True)
    return Response({'room': room_serializer.data, 'messages': message_serializer.data})       

class AllUsersListView(APIView):
    def get(self, request):
        users = Users.objects.all()
        serializer = UsersSerializer(users, many=True)
        return Response(serializer.data)

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    filter_backends = [SearchFilter]
    search_fields = ['first_name', 'last_name']
    
    #search for patient by name (to be used later)
    # def get_queryset(self):
    #     query = self.request.query_params.get('query', None)
    #     if query:
    #         queryset = Patient.objects.annotate(
    #             full_name=Concat(F('first_name'), V(' '), F('last_name'))
    #         ).filter(
    #             Q(full_name__icontains=query)
    #         )
    #         return queryset
    #     return super().get_queryset()

            
class SocialMediaViewSet(viewsets.ModelViewSet):
    queryset = SocialMedia.objects.all()
    serializer_class = SocialMediaSerializer

class SocialMediaAccountViewSet(viewsets.ModelViewSet):
    queryset = SocialMediaAccount.objects.all()
    serializer_class = SocialMediaAccountSerializer
    http_method_names = ['get', 'post', 'put', 'delete'] 

class ProcedureInstructionViewSet(viewsets.ModelViewSet):
    queryset = ProcedureInstruction.objects.all()
    serializer_class = ProcedureInstructionSerializer

class PatientEducationViewSet(viewsets.ModelViewSet):
    queryset = PatientEducation.objects.all()
    serializer_class = PatientEducationSerializer

class GeneralHealthRemindersViewSet(viewsets.ModelViewSet):
    queryset = GeneralHealthReminders.objects.all()
    serializer_class = GeneralHealthRemindersSerializer

class AllergiesViewSet(viewsets.ModelViewSet):
    queryset = Allergies.objects.all()
    serializer_class = AllergiesSerializer

class SpecialNeedViewSet(viewsets.ModelViewSet):
    queryset = SpecialNeed.objects.all()
    serializer_class = SpecialNeedSerializer

class DiagnosisViewSet(viewsets.ModelViewSet):
    queryset = Diagnosis.objects.all()
    serializer_class = DiagnosisSerializer

class SurgeryViewSet(viewsets.ModelViewSet):
    queryset = Surgery.objects.all()
    serializer_class = SurgerySerializer

class VitalViewSet(viewsets.ModelViewSet):
    queryset = Vital.objects.all()
    serializer_class = VitalSerializer

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

class NotesViewSet(viewsets.ModelViewSet):
    queryset = Notes.objects.all()
    serializer_class = NotesSerializer

class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    
class InsuranceViewSet(viewsets.ModelViewSet):
    queryset = Insurance.objects.all()
    serializer_class = InsuranceSerializer

class PatientHasSurgeryViewSet(viewsets.ModelViewSet):
    queryset = PatientHasSurgery.objects.all()
    serializer_class = PatientHasSurgerySerializer

class PatientHasInsuranceViewSet(viewsets.ModelViewSet):
    queryset = PatientHasInsurance.objects.all()
    serializer_class = PatientHasInsuranceSerializer

class PatientHasVitalViewSet(viewsets.ModelViewSet):
    queryset = PatientHasVital.objects.all()
    serializer_class = PatientHasVitalSerializer

class PatientHasPrescriptionViewSet(viewsets.ModelViewSet):
    queryset = PatientHasPrescription.objects.all()
    serializer_class = PatientHasPrescriptionSerializer

class PatientHasDiagnosisViewSet(viewsets.ModelViewSet):
    queryset = PatientHasDiagnosis.objects.all()
    serializer_class = PatientHasDiagnosisSerializer

class ProblemViewSet(viewsets.ModelViewSet):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer

class PatientHasProblemViewSet(viewsets.ModelViewSet):
    queryset = PatientHasProblem.objects.all()
    serializer_class = PatientHasProblemSerializer

class MedicalTestViewSet(viewsets.ModelViewSet):
    queryset = MedicalTest.objects.all()
    serializer_class = MedicalTestSerializer

class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

class ReferralDoctorsViewSet(viewsets.ModelViewSet):
    queryset = ReferralDoctors.objects.all()
    serializer_class = ReferralDoctorsSerializer

class PatientHasReferralDoctorsViewSet(viewsets.ModelViewSet):
    queryset = PatientHasReferralDoctors.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PatientHasReferralDoctorsGetSerializer
        elif self.request.method == 'POST' :
            return PatientHasReferralDoctorsPostSerializer
        elif self.request.method == 'PUT':
            return PatientHasReferralDoctorsGetSerializer 

class UsersHasReferralDoctorsViewSet(viewsets.ModelViewSet):
    queryset = UsersHasReferralDoctors.objects.all()
    serializer_class = UsersHasReferralDoctorsSerializer

class UsersHasPatientViewSet(viewsets.ModelViewSet):
    queryset = UsersHasPatient.objects.all()
    serializer_class = UsersHasPatientSerializer

class UsersHasTemplatesViewSet(viewsets.ModelViewSet):
    queryset = UsersHasTemplates.objects.all()
    serializer_class = UsersHasTemplatesSerializer

class PatientReceiveTemplatesViewSet(viewsets.ModelViewSet):
    queryset = PatientReceiveTemplates.objects.all()
    serializer_class = PatientReceiveTemplatesSerializer

class ClinicViewSet(viewsets.ModelViewSet):
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer

class VirtualMeetViewSet(viewsets.ModelViewSet):
    queryset = VirtualMeet.objects.all()
    serializer_class = VirtualMeetSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class TasksViewSet(viewsets.ModelViewSet):
    queryset = Tasks.objects.all()
    serializer_class = TasksSerializer

class RecurrenceViewSet(viewsets.ModelViewSet):
    queryset = Recurrence.objects.all()
    serializer_class = RecurrenceSerializer

class AttachmentReminderViewSet(viewsets.ModelViewSet):
    
    serializer_class = AttachmentReminderSerializer

    def get_queryset(self):
        template_id = self.request.query_params.get("templateID")
        if (template_id):
            queryset = AttachmentReminder.objects.filter(templateID=template_id)
        else:
            queryset = AttachmentReminder.objects.all()
        return queryset

class TemplatesViewSet(viewsets.ModelViewSet):
    queryset = Templates.objects.all()
    serializer_class = TemplatesSerializer

class UsersHasTasksViewSet(viewsets.ModelViewSet):
    queryset = UsersHasTasks.objects.all()
    serializer_class = UsersHasTasksSerializer

class RadiologyTestViewSet(viewsets.ModelViewSet):
    queryset = RadiologyTest.objects.all()
    serializer_class = RadiologyTestSerializer

class RadiologyResultViewSet(viewsets.ModelViewSet):
    queryset = RadiologyResult.objects.all()
    serializer_class = RadiologyResultSerializer

class ReferenceViewSet(viewsets.ModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer

class BillingViewSet(viewsets.ModelViewSet):
    queryset = Billing.objects.all()
    serializer_class = BillingSerializer
    def perform_create(self, serializer):
        # Save the billing entry and get the object
        billing_entry = serializer.save()

        # Generate the invoice_number based on the created billing_id
        billing_entry.invoice_number = f'inv_{billing_entry.billing_id}'
        billing_entry.save()

        # Serialize and return the billing entry with the generated invoice_number
        serializer = self.get_serializer(billing_entry)
        return Response(serializer.data)


def most_prescribed_medications(request, patient_id):
    # Call the model method to retrieve the most prescribed medications
    most_prescribed_meds = PatientHasPrescription.most_prescribed_medications(patient_id)

    # You can process the data as needed and return a JSON response
    data = {
        'most_prescribed_medications': most_prescribed_meds,
    }
    return JsonResponse(data)

class FilesViewSet(viewsets.ModelViewSet):
    queryset = Files.objects.all()
    serializer_class = FilesSerializer

import os

def serve_file(request, file_name):
    # Construct the full path to the file
    file_path = os.path.join(settings.MEDIA_ROOT, 'attachments', file_name)

    if os.path.exists(file_path):
        # Open and serve the file
        with open(file_path, 'rb') as file:
            response = FileResponse(file)
            # Set the Content-Disposition header for inline display
            response['Content-Disposition'] = 'inline; filename="' + os.path.basename(file_path) + '"'
            return response
    else:
        # Handle the case where the file does not exist
        return HttpResponse("File not found", status=404)


def serve_template_attachment(request, file_name):
    # Construct the full path to the file
    file_path = os.path.join(settings.MEDIA_ROOT, 'templates', file_name)

    if os.path.exists(file_path):
        # Open and serve the file
        with open(file_path, 'rb') as file:
            response = FileResponse(file)
            # Set the Content-Disposition header for inline display
            response['Content-Disposition'] = 'inline; filename="' + os.path.basename(file_path) + '"'
            return response
    else:
        # Handle the case where the file does not exist
        return HttpResponse("File not found", status=404)
import json
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def receive_whatsapp_message(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            
            # Process the incoming payload as needed
            print("Received forwarded message:", payload)

            # Add your custom logic here to process the forwarded message
            
            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'method not allowed'}, status=405)

    
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timezone
import requests  # Import requests module
from django.core.files.base import ContentFile
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
access_token='EAAFSezp24bEBOZClnAdjpDdQkR5VbiBlZBpasajiAhqmBBAU9dRzv8yaPMiywHgmSfcll2JidnlevI6MVjBiqn2Qqua8q4m6BhhfllM7vgWc072d5TpAIJpLcC4vpDFNbborjjZBFHjafvdJeLh4GIT8qnLQRjKqKA7JKbJeVRhQQIbiCXZBXcjPRSReU5meZCTDCwRI69ZArd1bqnUOP8GEzZClxQMafN4VzzN7veT0YYZD'
@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'GET':
        # Handle verification
        verify_token = "doctor1"  # Replace with your actual verify token
        received_verify_token = request.GET.get("hub.verify_token", "")

        if received_verify_token == verify_token:
            # Respond with the challenge to complete the verification
            challenge = request.GET.get("hub.challenge", "")
            return HttpResponse(challenge, content_type="text/plain")
        else:
            # Respond with an error if tokens do not match
            return HttpResponse("Verification failed", status=403)

    elif request.method == 'POST':
        # Handle message processing
        try:
            payload = json.loads(request.body)
            print("Received", payload)

            # Extract relevant information from the payload
            entry = payload.get('entry', [])
            if entry:
                changes = entry[0].get('changes', [])
                if changes:
                    value = changes[0].get('value', {})
                    contacts = value.get('contacts', [])
                    messages = value.get('messages', [])
                    #message_id = messages[0]['id']
                    # Ensure required data is present
                    if contacts and messages:
                        phone_number = contacts[0].get('wa_id', '')
                        timestamp = messages[0].get('timestamp', 0)
                        received_time = datetime.utcfromtimestamp(int(timestamp)).replace(tzinfo=timezone.utc)

                        # Find patient using phone number and get the ID
                        patient, created = Patient.objects.get_or_create(phone=phone_number)

                        # Find user with role_idrole equal to 1 and get the ID
                       # user = Users.objects.filter(role_idrole=1).first()  # Replace with your actual logic
                        print("mess",messages[0])
                        # Check if the message contains text or media
                        if 'text' in messages[0]:
                            text = messages[0]['text']['body']
                            # Save the message to the database
                            WhatsMessage.objects.create(
                                text=text,
                                #user=user,
                                patient=patient,
                                is_sent=False,
                                received_time=received_time,
                            )
                            channel_layer = get_channel_layer()
                            async_to_sync(channel_layer.group_send)(
                                "whatsapp_group",  # Replace with the actual group name for WhatsApp messages
                                {
                                    "type": "notify.whatsapp_event",
                                    "message": "New WhatsApp message received!",
                                    #"user_id": user.id,  # Include user ID in the WebSocket message
                                    "patient_id": patient.id,  # Include patient ID in the WebSocket message
                                },
                            )
                            print('Text message saved to database')
                            send_acknowledgment(patient.phone, text)
                        elif 'button' in messages[0]:
                            button_payload = messages[0]['button']['payload']
                            # Save the button payload as a text message
                            WhatsMessage.objects.create(
                                text=button_payload,
                                #user=user,
                                patient=patient,
                                is_sent=False,
                                received_time=received_time,
                            )
                            channel_layer = get_channel_layer()
                            async_to_sync(channel_layer.group_send)(
                                "whatsapp_group",  # Replace with the actual group name for WhatsApp messages
                                {
                                    "type": "notify.whatsapp_event",
                                    "message": "New WhatsApp message received!",
                                   # "user_id": user.id,  # Include user ID in the WebSocket message
                                    "patient_id": patient.id,  # Include patient ID in the WebSocket message
                                },
                            )
                            print('Button payload saved as text message to database')
                            send_acknowledgment(patient.phone, 'reply')
                        elif 'location' in messages[0]:
                            location_data = messages[0]['location']
                            latitude = location_data.get('latitude')
                            longitude = location_data.get('longitude')
                            WhatsMessage.objects.create(
                                longitude=longitude,
                                latitude=latitude,
                                #user=user,
                                patient=patient,
                                is_sent=False,
                                received_time=received_time,
                            )
                            channel_layer = get_channel_layer()
                            async_to_sync(channel_layer.group_send)(
                                "whatsapp_group",  # Replace with the actual group name for WhatsApp messages
                                {
                                    "type": "notify.whatsapp_event",
                                    "message": "New WhatsApp message received!",
                                    #"user_id": user.id,  # Include user ID in the WebSocket message
                                    "patient_id": patient.id,  # Include patient ID in the WebSocket message
                                },
                            )
                            print('Location saved to database')
                            send_acknowledgment(patient.phone, 'location')
                        elif 'image' in messages[0]:
                            # Process image media message
                            image_media_id = messages[0]['image']['id']
                            image_url = get_media_url(image_media_id)
                            if image_url:
                                image_data = download_media(image_url)
                                # Save the media information to your database
                                media_obj=Media.objects.create(
                                    media_id=image_media_id,
                                    media_type='image/jpeg',
                                    
                                )
                                
                                media_obj.media_data.save(f"image_{media_obj.id}.jpeg", ContentFile(image_data))
                                media_obj.save()
                                WhatsMessage.objects.create(
                                #user=user,
                                patient=patient,
                                media=media_obj,
                                received_time=received_time,  # Assuming you want to use received_time as sent_timestamp
                                is_sent=False,
                            )
                                print('Image media saved to database')
                                send_acknowledgment(patient.phone, 'image')
                                channel_layer = get_channel_layer()
                                async_to_sync(channel_layer.group_send)(
                                    "whatsapp_group",  # Replace with the actual group name for WhatsApp messages
                                    {
                                        "type": "notify.whatsapp_event",
                                        "message": "New WhatsApp message received!",
                                        #"user_id": user.id,  # Include user ID in the WebSocket message
                                        "patient_id": patient.id,  # Include patient ID in the WebSocket message
                                    },
                                )
                            else:
                                print('Error getting image media URL')
                        elif 'document' in messages[0]:
                            # Process document media message
                            document_media_id = messages[0]['document']['id']
                            document_url = get_media_url(document_media_id)
                            if document_url:
                                document_data = download_media(document_url)
                                # Save the media information to your database
                                media_obj = Media.objects.create(
                                media_id=document_media_id,
                                media_type=messages[0]['document']['mime_type'],
                            )
                                # Determine the file extension based on the MIME type
                                extension = media_obj.media_type.split('/')[-1]
                                media_obj.media_data.save(f"document_{media_obj.id}.{extension}", ContentFile(document_data))
                                media_obj.save()
                                
                                WhatsMessage.objects.create(
                                #user=user,
                                patient=patient,
                                media=media_obj,
                                received_time=received_time,  # Assuming you want to use received_time as sent_timestamp
                                is_sent=False,
                            )
                                channel_layer = get_channel_layer()
                                async_to_sync(channel_layer.group_send)(
                                    "whatsapp_group",  # Replace with the actual group name for WhatsApp messages
                                    {
                                        "type": "notify.whatsapp_event",
                                        "message": "New WhatsApp message received!",
                                        #"user_id": user.id,  # Include user ID in the WebSocket message
                                        "patient_id": patient.id,  # Include patient ID in the WebSocket message
                                    },
                                )
                                print('Document media saved to database')
                                send_acknowledgment(patient.phone, 'document')
                            else:
                                print('Error getting document media URL')
                        elif 'audio' in messages[0]:
                            # Process audio media message
                            audio_media_id = messages[0]['audio']['id']
                            audio_url = get_media_url(audio_media_id)
                            if audio_url:
                                audio_data = download_media(audio_url)
                                # Save the media information to your database
                                media_obj = Media.objects.create(
                                media_id=audio_media_id,
                                media_type=messages[0]['audio']['mime_type'],
                            )
                                # Determine the file extension based on the MIME type
                                extension = media_obj.media_type.split('/')[-1]
                                media_obj.media_data.save(f"audio_{media_obj.id}.{extension}", ContentFile(audio_data))
                                media_obj.save()
                                WhatsMessage.objects.create(
                                #user=user,
                                patient=patient,
                                media=media_obj,
                                received_time=received_time,  # Assuming you want to use received_time as sent_timestamp
                                is_sent=False,
                            )
                                print('Audio media saved to database')
                                send_acknowledgment(patient.phone, 'audio')
                                channel_layer = get_channel_layer()
                                async_to_sync(channel_layer.group_send)(
                                    "whatsapp_group",  # Replace with the actual group name for WhatsApp messages
                                    {
                                        "type": "notify.whatsapp_event",
                                        "message": "New WhatsApp message received!",
                                        #"user_id": user.id,  # Include user ID in the WebSocket message
                                        "patient_id": patient.id,  # Include patient ID in the WebSocket message
                                    },
                                )
                            else:
                                print('Error getting audio media URL')
                        elif 'video' in messages[0]:
                            # Process video media message
                            video_media_id = messages[0]['video']['id']
                            video_url = get_media_url(video_media_id)
                            if video_url:
                                video_data = download_media(video_url)
                                # Save the media information to your database
                                media_obj = Media.objects.create(
                                media_id=video_media_id,
                                media_type='video/mp4',  # Adjust the media type based on actual payload
                            )
                                media_obj.media_data.save(f"video_{media_obj.id}.mp4", ContentFile(video_data))
                                media_obj.save()
                                WhatsMessage.objects.create(
                               # user=user,
                                patient=patient,
                                media=media_obj,
                                received_time=received_time,  # Assuming you want to use received_time as sent_timestamp
                                is_sent=False,
                            )
                                print('Video media saved to database')
                                send_acknowledgment(patient.phone, 'video')
                                channel_layer = get_channel_layer()
                                async_to_sync(channel_layer.group_send)(
                                    "whatsapp_group",  # Replace with the actual group name for WhatsApp messages
                                    {
                                        "type": "notify.whatsapp_event",
                                        "message": "New WhatsApp message received!",
                                        #"user_id": user.id,  # Include user ID in the WebSocket message
                                        "patient_id": patient.id,  # Include patient ID in the WebSocket message
                                    },
                                )
                            else:
                                print('Error getting video media URL')
                        elif 'sticker' in messages[0]:
                            # Process sticker media message
                            sticker_media_id = messages[0]['sticker']['id']
                            sticker_url = get_media_url(sticker_media_id)
                            if sticker_url:
                                sticker_data = download_media(sticker_url)
                                # Save the media information to your database
                                media_obj = Media.objects.create(
                                media_id=sticker_media_id,
                                media_type='image/webp',
                            )
                                media_obj.media_data.save(f"sticker_{media_obj.id}.webp", ContentFile(sticker_data))
                                media_obj.save()
                                WhatsMessage.objects.create(
                                #user=user,
                                patient=patient,
                                media=media_obj,
                                received_time=received_time,  # Assuming you want to use received_time as sent_timestamp
                                is_sent=False,
                            )
                                print('Sticker media saved to database')
                                send_acknowledgment(patient.phone, 'sticker')
                                channel_layer = get_channel_layer()
                                async_to_sync(channel_layer.group_send)(
                                    "whatsapp_group",  # Replace with the actual group name for WhatsApp messages
                                    {
                                        "type": "notify.whatsapp_event",
                                        "message": "New WhatsApp message received!",
                                        #"user_id": user.id,  # Include user ID in the WebSocket message
                                        "patient_id": patient.id,  # Include patient ID in the WebSocket message
                                    },
                                )
                            else:
                                print('Error getting sticker media URL')
                        # Add similar handling for other media types (if any)
                        
                        return JsonResponse({'status': 'success'})

            # If the payload structure is not as expected, return an error response
            return JsonResponse({'status': 'success', 'message': 'Message received but not processed'}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Error decoding JSON: ' + str(e)}, status=400)

    return JsonResponse({'status': 'method not allowed'}, status=405)

def get_media_url(media_id):
    # Replace <YOUR_ACCESS_TOKEN> with your actual access token
    #access_token = 'EAAFSezp24bEBO8DFtDmD8Bzevm86reUpawPfGbFZAJqw4y6en3XtEUuu1zDhY8AqhQqvDXLFFfUXSanqzCmyQpOOAjFpZB1wBf0XwRviF6XhGeBHJv9zorVOOWs7LsJVuVdpmYAefuGdo3PHZCdwbDMzR6b5BDxY15ZAtGKHmIlgN6aq685DSrVMZAuO3d9nT0zeXHd8PDeXKB4I2sN0DlDZBrhKT3yVUHDIiOGPXJfzoZD'
    url = f'https://graph.facebook.com/v17.0/{media_id}/'
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        media_url = data.get('url', '')
        return media_url
    except requests.exceptions.RequestException as e:
        # Handle request errors (you can log the error, raise an exception, etc.)
        print(f"Error getting media URL: {e}")
        return None  # Or raise an exception if you want to handle it differently
import base64
def download_media(media_url):
    #access_token = 'EAAFSezp24bEBO8DFtDmD8Bzevm86reUpawPfGbFZAJqw4y6en3XtEUuu1zDhY8AqhQqvDXLFFfUXSanqzCmyQpOOAjFpZB1wBf0XwRviF6XhGeBHJv9zorVOOWs7LsJVuVdpmYAefuGdo3PHZCdwbDMzR6b5BDxY15ZAtGKHmIlgN6aq685DSrVMZAuO3d9nT0zeXHd8PDeXKB4I2sN0DlDZBrhKT3yVUHDIiOGPXJfzoZD'
    headers = {'Authorization': f'Bearer {access_token}'}

    try:
        response = requests.get(media_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses

        # Return the response content
        return response.content

    except requests.exceptions.RequestException as e:
        # Handle request errors (you can log the error, raise an exception, etc.)
        print(f"Error downloading media: {e}")
        return None

def mark_message_as_read( message_id):
    #access_token = 'EAAFSezp24bEBO8DFtDmD8Bzevm86reUpawPfGbFZAJqw4y6en3XtEUuu1zDhY8AqhQqvDXLFFfUXSanqzCmyQpOOAjFpZB1wBf0XwRviF6XhGeBHJv9zorVOOWs7LsJVuVdpmYAefuGdo3PHZCdwbDMzR6b5BDxY15ZAtGKHmIlgN6aq685DSrVMZAuO3d9nT0zeXHd8PDeXKB4I2sN0DlDZBrhKT3yVUHDIiOGPXJfzoZD'
    phone_number_id= '189179114270760'
    url = f'https://graph.facebook.com/v17.0/{phone_number_id}/messages'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an error for bad responses
        print('Message marked as read successfully!')
    except requests.exceptions.RequestException as e:
        # Handle request errors (log the error, raise an exception, etc.)
        print(f"Error marking message as read: {e}")

def send_acknowledgment(recipient_phone, message_type):
    # Construct the acknowledgment message based on the message type
    acknowledgment_text = f"Ack: {message_type}"
    
    # Replace this with your logic to send the acknowledgment using the WhatsApp API
    #auth_token = 'EAAFSezp24bEBO8DFtDmD8Bzevm86reUpawPfGbFZAJqw4y6en3XtEUuu1zDhY8AqhQqvDXLFFfUXSanqzCmyQpOOAjFpZB1wBf0XwRviF6XhGeBHJv9zorVOOWs7LsJVuVdpmYAefuGdo3PHZCdwbDMzR6b5BDxY15ZAtGKHmIlgN6aq685DSrVMZAuO3d9nT0zeXHd8PDeXKB4I2sN0DlDZBrhKT3yVUHDIiOGPXJfzoZD'
    phone_number_id= '189179114270760'
    api_url = f'https://graph.facebook.com/v17.0/{phone_number_id}/messages'
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }
    
    requestBody = {
        'messaging_product': 'whatsapp',
        'recipient_type': 'individual',
        'to': recipient_phone,  # Replace this with the recipient's phone number
        'type': 'text',
        'text': {
            'preview_url': False,
            'body': acknowledgment_text,
        },
    }

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(requestBody))
        response.raise_for_status()  # Raise an error for bad responses
        print(f"Acknowledgment for {message_type} sent to {recipient_phone}")
    except requests.exceptions.RequestException as e:
        # Handle request errors (log the error, raise an exception, etc.)
        print(f"Error sending acknowledgment: {e}")


class MediaViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer

import base64

@api_view(['POST'])
def create_media(request):
    if request.method == 'POST':
        media_id = request.data.get('media_id')
        media_type = request.data.get('media_type')
        binary_data = request.data.get('media_data')

        # If binary_data is a string, convert it to bytes
        if isinstance(binary_data, str):
            binary_data = binary_data.encode('utf-8')

        # Base64 encode binary data
        encoded_data = base64.b64encode(binary_data).decode('utf-8')

        # Save to database
        media = Media.objects.create(
            media_id=media_id,
            media_type=media_type,
            media_data=encoded_data
        )

        return Response({'status': 'success', 'media_id': media.id}, status=status.HTTP_201_CREATED)
    else:
        return Response({'status': 'error', 'message': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)

class WhatsMessageViewSet(viewsets.ModelViewSet):
    queryset = WhatsMessage.objects.all()
    serializer_class = WhatsMessageSerializer