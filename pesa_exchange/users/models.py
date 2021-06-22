import uuid
import jwt

from datetime import timedelta

from django.core.validators import validate_email
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token

from .user_manager import UserManager


GENDER_CHOICES = (
    ('MA', 'Male'),
    ('FM', 'Female')
)

# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class User(PermissionsMixin, AbstractBaseUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', ]
    objects = UserManager()

    guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone_number = models.CharField(db_index=True, max_length=32, unique=True, 
        null=True, blank= True)
    username = models.CharField(db_index=True, max_length=255, unique=True,
        null=True, blank= True)
    email = models.EmailField(unique=True, validators=[validate_email])
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, blank=False, null=False)
    other_names = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(null=True, blank=True, choices=GENDER_CHOICES, max_length=2)
    # profile_image = models.ImageField(null=True, blank=True, upload_to='avatars/')


    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        'self', on_delete=models.PROTECT, related_name='user_created_by',
        null=True, blank=True)
    updated_by = models.ForeignKey(
        'self', on_delete=models.PROTECT, related_name='user_updated_by',
        null=True, blank=True)

    def get_short_name(self):
        return self.short_name

    def get_full_name(self):
        return self.full_name

    @property
    def short_name(self):
        return self.first_name

    @property
    def full_name(self):
        if self.other_names:
            return " ".join(
                [self.first_name, self.other_names, self.last_name])
        return " ".join([self.first_name, self.last_name])

    def save(self, *args, **kwargs):
        self.full_clean(exclude=None)
        super(User, self).save(*args, **kwargs)

    def set_password(self, password):
        if self.id is not None and \
                self.password is not None and \
                self.has_usable_password():

            super(User, self).set_password(password)
    
    @property
    def token(self):
        """
        Allows us to get a user's token by calling `user.token` instead of
        `user._generate_jwt_token().
        """
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        """
        Generates a JSON Web Token that stores this user's ID and has an expiry
        date set to 60 days into the future.
        """
        dt = timezone.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token

    class Meta:
        ordering = ('first_name', 'last_name', )
