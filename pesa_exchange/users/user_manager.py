import uuid
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):

    def create_user(self, username, email, phone_number, first_name, last_name,
                    password=None, **extra_fields):
        now = timezone.now()
        if email is None:
            raise TypeError('Users must have an email address.')

        is_staff = extra_fields.pop('is_staff', False)
        is_active = extra_fields.pop('is_active', True)
        is_superuser = extra_fields.pop('is_superuser', False)
        last_login = extra_fields.pop('last_login', now)
        other_names = extra_fields.pop('other_names', None)

        user = self.model(
            username=username, email=email,
            phone_number=phone_number, first_name=first_name,
            last_name=last_name, other_names=other_names,
            is_staff=is_staff, is_active=is_active, is_superuser=is_superuser,
            last_login=last_login, **extra_fields)
        user.set_password(password)
        if extra_fields.get('guid', None) is None:
            user.guid = uuid.uuid4()

        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, phone_number, first_name, last_name,
                         password, **extra_fields):
        user = self.create_user(username, email, phone_number, first_name, last_name,
                                password, **extra_fields)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
