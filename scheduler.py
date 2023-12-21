from apscheduler.schedulers.background import BackgroundScheduler
import os
import django
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')  
django.setup()
from myapp.models import PatientReceiveTemplates, Media, WhatsMessage
from django.utils import timezone
from datetime import timedelta
from django.core.files.base import ContentFile
import requests
from django.utils import timezone

def check_last_received_message(patient, template_date):
    try:
        # Get the patient's last received message
        last_message = WhatsMessage.objects.filter(patient=patient).exclude(received_time__isnull=True).order_by('-received_time').first()
        print("last", last_message)
        if last_message:
            # Calculate the time difference between the last received message and the template date
            time_difference = (template_date - last_message.received_time).total_seconds()

            # Check if the last message was within the last 24 hours
            twenty_four_hours = 0.5 * 60 * 60  # 24 hours in seconds
            if time_difference < twenty_four_hours:
                return True  # Last received message was within the last 24 hours
            else:
                return False  # Last received message was more than 24 hours ago
        else:
            return False  # No received messages found

    except Exception as e:
        print(f'Error checking last received message: {e}')
        return False


def check_last_received_within_24_hours(patient, template_date):
    try:
        # Get the patient's last received message
        last_message = WhatsMessage.objects.filter(patient=patient).exclude(received_time__isnull=True).order_by('-received_time').first()
        print("lastfuture",last_message)
        if last_message:
            # Calculate the time difference between the last received message and the template date
            time_difference = (template_date - last_message.received_time).total_seconds()

            # Check if the last message was within the last 24 hours
            twenty_four_hours = 0.5 * 60 * 60  # 24 hours in seconds
            return time_difference < twenty_four_hours
        else:
            return False  # No received messages found

    except Exception as e:
        print(f'Error checking last received message: {e}')
        return False


def scheduled_function():
    now = timezone.now()
    print("now", now)
    
    # Calculate the start time for the next 15 minutes
    start_time = now + timedelta(minutes=15)

    # Fetch PatientReceiveTemplates data for the next 15 minutes
    templates = PatientReceiveTemplates.objects.filter(
        status=False,
        date__range=(now, start_time)
    )
    print(f"Fetched {len(templates)} templates for processing at {now}")
    
    for template in templates:
        patient_data = template.patient
        item = template.templates
        if check_last_received_message(patient_data, template.date):
            time_difference = (template.date - now).total_seconds() / 60
            scheduled_time = now + timedelta(minutes=time_difference)

            # Schedule the sending of the message at the calculated time
            scheduler.add_job(send_message, 'date', run_date=scheduled_time, args=[item, patient_data, template])
            print(f"Message for patient {patient_data.id} with template ID {item.idTemplates} scheduled for {scheduled_time}")
        else:
            print(f"Last received message for patient {patient_data.id} was more than 24 hours ago.")

            # Add 15 minutes to the date attribute if the template is not expired
            if not item.expire:
                if not template.message_updated:
                    # Save the initial date as a string
                    template.initial_date_str = str(template.date)
                    template.message_updated = True  # Set the flag to True to indicate that the message has been updated

                    print(f"updating message")
                else:
                    print(f"Skipping update")
                template.date += timedelta(minutes=15)
                template.save()
                print(f"Added 15 minutes to the template date for patient {patient_data.id}. Updated message body.")
            else:
                print(f"Skipping message scheduling for patient {patient_data.id} as the template is expired.")

    print("Processing completed.")
    future_time_start = now + timedelta(hours=2)
    future_time_end = future_time_start + timedelta(minutes=15)
    future_templates = PatientReceiveTemplates.objects.filter(
        status=False,
        date__range=(future_time_start, future_time_end)
        )
    print("future", future_templates)
        # Send 'reply' template to patients with scheduled messages in the next 2 to 2.15 hours
    for template in future_templates:
        patient_data = template.patient

        # Calculate the time difference between the scheduled time and the current time
        time_difference = (template.date - now).total_seconds() / 60

        # Calculate the time to send the 'reply' template exactly 2 hours before the scheduled time
        scheduled_time = template.date - timedelta(hours=2)
        if not check_last_received_within_24_hours(patient_data, template.date):
            # Schedule the 'reply' template to be sent exactly 2 hours before the scheduled time
            scheduler.add_job(send_reply_template, 'date', run_date=scheduled_time, args=[patient_data])
            print(f"Predefined 'reply' template scheduled for patient {patient_data.id} at {scheduled_time}")



def send_message(item, patient_data, template):
    try:
        auth_token = 'EAAFSezp24bEBOZClnAdjpDdQkR5VbiBlZBpasajiAhqmBBAU9dRzv8yaPMiywHgmSfcll2JidnlevI6MVjBiqn2Qqua8q4m6BhhfllM7vgWc072d5TpAIJpLcC4vpDFNbborjjZBFHjafvdJeLh4GIT8qnLQRjKqKA7JKbJeVRhQQIbiCXZBXcjPRSReU5meZCTDCwRI69ZArd1bqnUOP8GEzZClxQMafN4VzzN7veT0YYZD'
        phone_number_id = '189179114270760'
        api_url_media = f'https://graph.facebook.com/v17.0/{phone_number_id}/media'
        api_url = f'https://graph.facebook.com/v17.0/189179114270760/messages'
        print(f"Sending message for patient {patient_data.id} with template ID {item.idTemplates}")
        recipient_phone = patient_data.phone
        print("item", item.body)
        if not item.body:
            print("t")
            attachment_response = requests.get('http://127.0.0.1:8000/attachment-reminders/', params={'templateID': item.idTemplates})
            print("res", attachment_response)
            attachment_data = attachment_response.json()
  
            if attachment_data and len(attachment_data) > 0:
                print("data")
                attachment = attachment_data[0]
                file_response = requests.get(attachment['attachment_file'], stream=True)
                file = file_response.content
                print("atta")
                supported_types = [
                    'audio/aac', 'audio/mp4', 'audio/mpeg', 'audio/amr', 'audio/ogg',
                    'audio/ogg; codecs:opus', 'text/plain', 'application/pdf',
                    'application/vnd.ms-powerpoint', 'application/msword', 'application/vnd.ms-excel',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'image/jpeg', 'image/png', 'video/mp4', 'video/3gp', 'image/webp'
                ]
  
                if attachment['type'] in supported_types:
                    print("type")
                    payload = {
                        'type': attachment['type'],
                        'messaging_product': 'whatsapp',
                    }

                    files = {
                        'file': (attachment['name'], file, attachment['type']),
                    }

                    headers = {
                        'Authorization': f'Bearer {auth_token}',
                    }
                    upload_response = requests.post(api_url_media, data=payload, files=files, headers=headers)

                    upload_result = upload_response.json()
                    media_type = get_media_content(attachment['type'])
                    print("media", media_type)
                    print("upload", upload_response)
                    if upload_result.get('id') and media_type:
                        print("if")
                        request_body = {
                            'messaging_product': 'whatsapp',
                            'recipient_type': 'individual',
                            'to': recipient_phone,
                            'type': media_type,
                            media_type: {'id': upload_result['id']}
                        }
  
                        response = requests.post(api_url, json=request_body, headers={'Authorization': f'Bearer {auth_token}', 'Content-Type': 'application/json'})
                        print(f'Media message sent: {response.json()}')
                        template.status = True
                        template.save()
                        media_instance = Media.objects.create(
                        media_id=upload_result['id'],
                        media_type=attachment['type'],
                        
                    )
                        extension = attachment['type'].split('/')[-1]
                        media_instance.media_data.save(f"media_{media_instance.id}.{extension}", ContentFile(file))
                        media_instance.save()
                        # Save message information in the WhatsMessage model
                        whats_message_instance = WhatsMessage.objects.create(

                            patient=patient_data,
                            media=media_instance,
                            sent_timestamp=timezone.now(),  
                            is_sent=True,

                        )
                        # Check conditions for sending additional text message
                        if template.message_updated and template.initial_date_str:
                            additional_message = f"This message should have been sent at the original scheduled date: {template.initial_date_str} (GMT)"
                            send_additional_text_message(additional_message, recipient_phone, auth_token, api_url)
        else:
            # Check conditions for appending sentence to text message
            bodymessage = item.body
            if template.message_updated and template.initial_date_str:
                additional_sentence = f"This message should have been sent at the original scheduled date: {template.initial_date_str} (GMT)"
                bodymessage += f"\n\n{additional_sentence}"
                request_body = {
                    'messaging_product': 'whatsapp',
                    'recipient_type': 'individual',
                    'to': recipient_phone,
                    'type': 'text',
                    'text': {'preview_url': False, 'body': bodymessage}
                }
            else:
                
                request_body = {
                    'messaging_product': 'whatsapp',
                    'recipient_type': 'individual',
                    'to': recipient_phone,
                    'type': 'text',
                    'text': {'preview_url': False, 'body': bodymessage}
                }
            response = requests.post(api_url, json=request_body, headers={'Authorization': f'Bearer {auth_token}', 'Content-Type': 'application/json'})
            print(f'Text message sent: {response.json()}')
            template.status = True
            template.save()
            whats_message_instance = WhatsMessage.objects.create(
                            text=bodymessage,
                            patient=patient_data,
                            sent_timestamp=timezone.now(),  
                            is_sent=True,
                        )
            print("saved to database")
    except Exception as e:
        print(f'Error sending WhatsApp messages: {e}')
        raise e

def get_media_content(media_type):
    supported_media_types = {
        'audio': ['audio/aac', 'audio/mp4', 'audio/mpeg', 'audio/amr', 'audio/ogg', 'audio/ogg; codecs:opus'],
        'document': [
            'text/plain', 'application/pdf', 'application/vnd.ms-powerpoint',
            'application/msword', 'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ],
        'image': ['image/jpeg', 'image/png', 'image/webp'],
        'video': ['video/mp4', 'video/3gp']
    }
  
    for content_type, types in supported_media_types.items():
        if media_type in types:
            return content_type
  
    return None  # Unsupported media type

def send_reply_template(patient_data):
    try:
       
        auth_token = 'EAAFSezp24bEBOZClnAdjpDdQkR5VbiBlZBpasajiAhqmBBAU9dRzv8yaPMiywHgmSfcll2JidnlevI6MVjBiqn2Qqua8q4m6BhhfllM7vgWc072d5TpAIJpLcC4vpDFNbborjjZBFHjafvdJeLh4GIT8qnLQRjKqKA7JKbJeVRhQQIbiCXZBXcjPRSReU5meZCTDCwRI69ZArd1bqnUOP8GEzZClxQMafN4VzzN7veT0YYZD'
        recipient_phone = patient_data.phone
        apiUrl = 'https://graph.facebook.com/v17.0/189179114270760/messages'

        requestBody = {
            'messaging_product': 'whatsapp',
            'to': recipient_phone,
            'type': 'template',
            'template': {
                'name': 'reply',
                'language': {'code': 'en'}
            },
        }

        response = requests.post(apiUrl, json=requestBody, headers={'Authorization': f'Bearer {auth_token}', 'Content-Type': 'application/json'})
        print(f"Predefined 'reply' template sent: {response.json()}")

    except Exception as e:
        print(f'Error sending predefined "reply" template: {e}')

def send_additional_text_message(additional_message, recipient_phone, auth_token, api_url):
    try:
        request_body = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': recipient_phone,
            'type': 'text',
            'text': {'preview_url': False, 'body': additional_message}
        }

        response = requests.post(api_url, json=request_body, headers={'Authorization': f'Bearer {auth_token}', 'Content-Type': 'application/json'})
        print(f'Additional text message sent: {response.json()}')
    except Exception as e:
        print(f'Error sending additional text message: {e}')
        raise e

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_function, 'interval', minutes=15)
scheduler.start()

try:
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()