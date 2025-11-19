import logging

from celery import shared_task
from django.utils.timezone import now

from .models import Loan
from django.core.mail import send_mail
from django.conf import settings


logger = logging.getLogger(__name__)

@shared_task
def send_loan_notification(loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
        member_email = loan.member.user.email
        book_title = loan.book.title
        send_mail(
            subject='Book Loaned Successfully',
            message=f'Hello {loan.member.user.username},\n\nYou have successfully loaned "{book_title}".\nPlease return it by the due date.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
    except Loan.DoesNotExist:
        pass


@shared_task
def check_overdue_loans():
    """Checks overdue book loans."""
    overdue = Loan.objects.filter(
        is_returned=False,
        due_at__lt=now()
    )
    for loan in overdue:
        send_mail(
            subject=f'Reminder: Book Overdue - {loan.book.title}',
            message=f'To {loan.member.user.username}. You have the following book overdue.\n'
                    f'Book: {loan.book.title}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[loan.member.user.email],
            fail_silently=False,
        )
        logger.info(f'Notified overdue loan {loan} to user.')
