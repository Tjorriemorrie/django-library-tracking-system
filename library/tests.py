import random
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.timezone import now

from library.models import Loan, Author, Book, Member
from library.tasks import check_overdue_loans


def get_author():
    params = {
        'first_name': 'John',
        'last_name': 'Doe',
        'biography': 'bio',
    }
    return Author.objects.create(**params)


def get_book():
    author = get_author()
    params = {
        'title': 'Big Book',
        'author': author,
        'isbn': '234klj',
        'genre': random.choice(Book.GENRE_CHOICES),
    }
    return Book.objects.create(**params)


def get_member():
    params = {
        'user': User.objects.create_user(username='john123')
    }
    return Member.objects.create(**params)


def get_loan(**kwargs):
    book = get_book()
    member = get_member()
    params = {
        'book': book,
        'member': member,
        'loan_date': now(),
        'return_date': now(),
    }
    params.update(kwargs)
    return Loan.objects.create(**params)


class LoanTests(TestCase):

    @patch('library.tasks.send_mail', autospec=True)
    def test_check_overdue_loans(self, m_send_email):
        """Checks overdue book loans."""
        loan = get_loan(due_at=(now() - timedelta(days=20)))

        check_overdue_loans()

        assert m_send_email.called
