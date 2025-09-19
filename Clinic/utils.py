from twilio.rest import Client
from django.conf import settings


def send_sms(to, message):
    """
    Send an SMS using Twilio.

    :param to: The recipient's phone number (e.g., "+1234567890").
    :param message: The SMS body text.
    :return: The sent message object.
    """
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            to=to,
            from_=settings.TWILIO_PHONE_NUMBER,
            body=message
        )
        return message
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None
