import os
import requests
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from .models import Payment, Booking

CHAPA_SECRET_KEY = os.environ.get('CHAPA_SECRET_KEY')
CHAPA_INITIATE_URL = 'https://api.chapa.co/v1/transaction/initialize'
CHAPA_VERIFY_URL = 'https://api.chapa.co/v1/transaction/verify/'


@shared_task
def initiate_chapa_payment(payment_id):
    """Initiate a Chapa payment for the given Payment record.

    This will call Chapa's initialize endpoint and store transaction_id and checkout url.
    """
    payment = Payment.objects.select_related('booking', 'booking__user').get(id=payment_id)
    booking = payment.booking
    user = booking.user

    headers = {
        'Authorization': f'Bearer {CHAPA_SECRET_KEY}',
        'Content-Type': 'application/json'
    }

    callback_url = getattr(settings, 'CHAPA_CALLBACK_URL', '')
    data = {
        'amount': str(payment.amount),
        'currency': 'ETB',
        'email': user.email or '',
        'first_name': user.first_name or user.username,
        'last_name': user.last_name or '',
        'tx_ref': f'booking-{booking.id}-{payment.id}',
        'callback_url': callback_url,
        'metadata': {'booking_id': booking.id}
    }

    resp = requests.post(CHAPA_INITIATE_URL, json=data, headers=headers, timeout=15)
    resp.raise_for_status()
    payload = resp.json()

    # Expect payload to contain 'data' with 'checkout_url' and 'id'
    chapa_data = payload.get('data', {})
    transaction_id = chapa_data.get('id')
    checkout_url = chapa_data.get('checkout_url')

    payment.transaction_id = transaction_id
    payment.chapa_checkout_url = checkout_url
    payment.status = Payment.STATUS_PENDING
    payment.save()

    return {'transaction_id': transaction_id, 'checkout_url': checkout_url}


@shared_task
def verify_chapa_payment(payment_id):
    """Verify payment status with Chapa and update the Payment record."""
    payment = Payment.objects.select_related('booking', 'booking__user').get(id=payment_id)
    if not payment.transaction_id:
        return {'error': 'no_transaction_id'}

    headers = {'Authorization': f'Bearer {CHAPA_SECRET_KEY}'}
    verify_url = CHAPA_VERIFY_URL + str(payment.transaction_id)
    resp = requests.get(verify_url, headers=headers, timeout=15)
    resp.raise_for_status()
    payload = resp.json()

    data = payload.get('data', {})
    status = data.get('status')

    if status == 'successful':
        payment.status = Payment.STATUS_COMPLETED
        payment.save()
        # send confirmation email asynchronously
        send_confirmation_email.delay(payment.id)
        return {'status': 'completed'}
    else:
        payment.status = Payment.STATUS_FAILED
        payment.save()
        return {'status': 'failed', 'raw': data}


@shared_task
def send_confirmation_email(payment_id):
    payment = Payment.objects.select_related('booking', 'booking__user').get(id=payment_id)
    user = payment.booking.user
    subject = 'Booking Confirmation'
    message = f"Your booking (id={payment.booking.id}) payment status is {payment.status}. Thank you." 
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
    recipient_list = [user.email] if user.email else []
    if recipient_list:
        send_mail(subject, message, from_email, recipient_list, fail_silently=True)
    return True
