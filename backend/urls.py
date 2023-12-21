"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from myapp import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
app_name = 'myapp'
 
from myapp.views import serve_file,serve_template_attachment
from rest_framework.authtoken.views import obtain_auth_token

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'roles', views.RoleViewSet)
router.register(r'users', views.UsersViewSet)
router.register(r'patients', views.PatientViewSet)
router.register(r'socialmedia', views.SocialMediaViewSet)
router.register(r'socialmediaaccount', views.SocialMediaAccountViewSet)
router.register(r'allergies', views.AllergiesViewSet)
router.register(r'specialneeds', views.SpecialNeedViewSet)
router.register(r'diagnosis', views.DiagnosisViewSet)
router.register(r'surgery', views.SurgeryViewSet)
router.register(r'vital', views.VitalViewSet)
router.register(r'prescription', views.PrescriptionViewSet)
router.register(r'notes', views.NotesViewSet)
router.register(r'attachment', views.AttachmentViewSet)
router.register(r'insurance', views.InsuranceViewSet)
router.register(r'patienthassurgery', views.PatientHasSurgeryViewSet)
router.register(r'patienthasinsurance', views.PatientHasInsuranceViewSet)
router.register(r'patienthasvital', views.PatientHasVitalViewSet)
router.register(r'patienthasprescription', views.PatientHasPrescriptionViewSet)
router.register(r'patienthasdiagnosis', views.PatientHasDiagnosisViewSet)
router.register(r'problem', views.ProblemViewSet)
router.register(r'patienthasproblem', views.PatientHasProblemViewSet)
router.register(r'medicaltest', views.MedicalTestViewSet)
router.register(r'result', views.ResultViewSet)
router.register(r'referraldoctors', views.ReferralDoctorsViewSet)
router.register(r'patienthasreferraldoctors', views.PatientHasReferralDoctorsViewSet)
router.register(r'usershasreferraldoctors', views.UsersHasReferralDoctorsViewSet)
router.register(r'usershaspatient', views.UsersHasPatientViewSet)
router.register(r'templates', views.TemplatesViewSet)
router.register(r'usershastemplates', views.UsersHasTemplatesViewSet)
router.register(r'patientreceivetemplates', views.PatientReceiveTemplatesViewSet)
router.register(r'clinic', views.ClinicViewSet)
router.register(r'virtualmeet', views.VirtualMeetViewSet)
router.register(r'appointment', views.AppointmentViewSet)
router.register(r'event', views.EventViewSet)
router.register(r'tasks', views.TasksViewSet)
router.register(r'usershastasks', views.UsersHasTasksViewSet)
router.register(r'radiologytest', views.RadiologyTestViewSet)
router.register(r'radiologyresult', views.RadiologyResultViewSet)
router.register(r'billing', views.BillingViewSet)
router.register(r'files', views.FilesViewSet, basename='files')
router.register(r'reference', views.ReferenceViewSet)
router.register(r'recurrences', views.RecurrenceViewSet)
router.register(r'attachment-reminders', views.AttachmentReminderViewSet,basename='attachment-reminders')
router.register(r'templates', views.TemplatesViewSet)
router.register(r'procedure-instruction', views.ProcedureInstructionViewSet)
router.register(r'patient-education', views.PatientEducationViewSet)
router.register(r'general-health-reminders', views.GeneralHealthRemindersViewSet)
router.register(r'media', views.MediaViewSet)
router.register(r'whatsmessage', views.WhatsMessageViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('media/attachments/<str:file_name>/', serve_file, name='serve_file'),
    path('media/templates/<str:file_name>/', serve_template_attachment, name='serve_template_attachment'),
    path('login/', views.custom_login, name='api_token_auth'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-password/', views.verify_password, name='verify_password'),
    path('templatesandrecurrences/', views.get_recurrence_and_template, name='templatesandrecurrences'),
    path('templatesandrecurrences/<int:idrecurrence>/', views.get_recurrence_and_template, name='templatesandrecurrences'),
    path('signup/', views.UserRegistration.as_view(), name='user-registration'),
    path('profile/update/<int:pk>/', views.ProfileUpdateView.as_view(), name='profile-update'),
    path('rooms/', views.rooms, name='rooms'),
    path('room/<int:id>/', views.room, name='room'),
     path('all-users/', views.AllUsersListView.as_view(), name='all-users-list'),
     path('profile/<str:email>/', views.ProfileView.as_view(), name='profile-detail'),
 path('create_media/', views.create_media, name='create_media'),
  path('whatsapp-webhook/', views.whatsapp_webhook, name='whatsapp_webhook'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)