from celery import shared_task
from django.utils import timezone

from borrowings.models import Borrowing
from borrowings.notifications.telegram import send_telegram_message


@shared_task
def check_overdue_borrowings():
    today = timezone.localdate()

    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today,
        actual_return_date__isnull=True,
    ).select_related("book", "user")

    if not overdue_borrowings.exists():
        send_telegram_message("No borrowings overdue today!")
        return

    for borrowing in overdue_borrowings:
        days_overdue = (today - borrowing.expected_return_date).days
        message = (
            f"⚠️ *Overdue borrowing*\n"
            f"Borrowing ID: {borrowing.id}\n"
            f"Book: {borrowing.book.title}\n"
            f"User: {borrowing.user.email}\n"
            f"Expected return date: {borrowing.expected_return_date}\n"
            f"Days overdue: {days_overdue}"
        )
        send_telegram_message(message)
