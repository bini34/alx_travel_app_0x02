# alx_travel_app_0x02

This project integrates the Chapa payment gateway for booking payments using Django, Django REST Framework and Celery.

Setup
1. Create and activate a virtual environment.
2. Install dependencies:

```
pip install -r requirements.txt
```

3. Set environment variables (example for Windows PowerShell):

```
setx CHAPA_SECRET_KEY "your_chapa_secret_key"
setx CHAPA_CALLBACK_URL "https://yourdomain.com/chapa/callback"
setx CELERY_BROKER_URL "redis://localhost:6379/0"
setx DEFAULT_FROM_EMAIL "noreply@example.com"
```

4. Run migrations:

```
python manage.py migrate
```

5. Start Redis (for Celery broker) and run Celery worker:

```
celery -A alx_travel_app worker --loglevel=info
```

Chapa Sandbox testing
- Use Chapa developer docs (https://developer.chapa.co/) and sandbox API key to test.
- When a booking is created, a Payment record is created and a Chapa transaction is initialized. The `chapa_checkout_url` is saved in the Payment model.
- Use the `/api/listings/payments/initiate/` endpoint to (re-)initiate payments and `/api/listings/payments/verify/<payment_id>/` to verify status.

Logs / Screenshots
- To capture proof of successful initiation/verification, check the Django logs and the Payment model row in the admin or via DRF responses. Save screenshots of the checkout_url and the updated payment status.

Notes
- Store secrets in environment variables. Do not commit them to source control.
- This repository includes a simple Celery task that sends a confirmation email on successful payment; configure your email backend in `settings.py` for production.
# alx_travel_app_0x02