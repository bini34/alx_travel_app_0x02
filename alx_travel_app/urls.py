from django.contrib import admin
from django.urls import path
from django.urls import include

from listings import views as listing_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/listings/payments/initiate/', listing_views.InitiatePaymentAPIView.as_view(), name='initiate-payment'),
    path('api/listings/payments/verify/<int:payment_id>/', listing_views.VerifyPaymentAPIView.as_view(), name='verify-payment'),
]
