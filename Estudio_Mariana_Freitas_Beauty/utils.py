from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
from datetime import datetime, timedelta
import pytz

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def format_phone_number(phone):
    """Format phone number to E.164 format"""
    phone = ''.join(filter(str.isdigit, phone))
    if phone.startswith('0'):
        phone = phone[1:]
    if not phone.startswith('55'):
        phone = '55' + phone
    return f"+{phone}"

def send_whatsapp_message(to_phone, message):
    """Send WhatsApp message using Twilio"""
    try:
        formatted_phone = format_phone_number(to_phone)
        message = twilio_client.messages.create(
            body=message,
            from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
            to=f"whatsapp:{formatted_phone}"
        )
        return True, message.sid
    except Exception as e:
        return False, str(e)

def send_appointment_confirmation(appointment):
    """Send appointment confirmation message"""
    message = (
        f"Olá {appointment.client_name}! 👋\n\n"
        f"Confirmando seu agendamento para {appointment.service_name} "
        f"no dia {appointment.datetime.strftime('%d/%m/%Y')} "
        f"às {appointment.datetime.strftime('%H:%M')}.\n\n"
        f"Por favor, confirme sua presença respondendo SIM.\n\n"
        f"Mariana Freitas Beauty 💅"
    )
    return send_whatsapp_message(appointment.client_phone, message)

def send_appointment_reminder(appointment):
    """Send appointment reminder message (24h before)"""
    message = (
        f"Olá {appointment.client_name}! 👋\n\n"
        f"Lembrando do seu agendamento amanhã para {appointment.service_name} "
        f"às {appointment.datetime.strftime('%H:%M')}.\n\n"
        f"Aguardamos você!\n\n"
        f"Mariana Freitas Beauty 💅"
    )
    return send_whatsapp_message(appointment.client_phone, message)

def calculate_fractional_cost(product, quantity_used):
    """Calculate cost for fractional product usage"""
    fraction = quantity_used / product.quantity
    return product.unit_cost * fraction

def check_low_stock(product, threshold):
    """Check if product is below low stock threshold"""
    return product.quantity < threshold 