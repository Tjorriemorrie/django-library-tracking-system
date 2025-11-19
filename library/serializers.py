from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Author, Book, Member, Loan
from django.contrib.auth.models import User


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(), source='author', write_only=True
    )

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'author_id', 'isbn', 'genre', 'available_copies']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = Member
        fields = ['id', 'user', 'user_id', 'membership_date']


class LoanSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), source='book', write_only=True
    )
    member = MemberSerializer(read_only=True)
    member_id = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(), source='member', write_only=True
    )

    class Meta:
        model = Loan
        fields = ['id', 'book', 'book_id', 'member', 'member_id', 'loan_date', 'return_date',
                  'is_returned']


class ExtendDueDateSerializer(serializers.ModelSerializer):
    additional_days = serializers.IntegerField(required=True, min_value=1)

    class Meta:
        model = Loan
        fields = ['additional_days']

    def validate(self, data):
        if self.instance.due_at < now():
            raise ValidationError('Book is already overdue.')
