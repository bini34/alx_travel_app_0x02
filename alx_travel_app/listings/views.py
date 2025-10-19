from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Booking, Payment
from .serializers import InitiatePaymentSerializer, PaymentSerializer
from .tasks import initiate_chapa_payment, verify_chapa_payment


class InitiatePaymentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking_id = serializer.validated_data['booking_id']
        amount = serializer.validated_data['amount']

        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

        # create or get existing payment
        payment, created = Payment.objects.get_or_create(booking=booking, defaults={'amount': amount})
        if not created:
            # update amount if needed
            payment.amount = amount
            payment.status = Payment.STATUS_PENDING
            payment.save()

        # enqueue task to create chapa transaction
        task = initiate_chapa_payment.delay(payment.id)

        return Response({'payment_id': payment.id, 'task_id': task.id, 'checkout_url': payment.chapa_checkout_url}, status=status.HTTP_202_ACCEPTED)


class VerifyPaymentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, payment_id=None):
        payment = get_object_or_404(Payment, id=payment_id, booking__user=request.user)
        task = verify_chapa_payment.delay(payment.id)
        return Response({'payment_id': payment.id, 'task_id': task.id, 'status': payment.status}, status=status.HTTP_202_ACCEPTED)
