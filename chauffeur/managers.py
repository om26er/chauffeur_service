from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email or not password:
            raise ValueError('Email and Password are mandatory')
        user = self.model(email=email)
        user.set_password(raw_password=password)
        user.is_active = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email is mandatory')

        if not password:
            raise ValueError('Password is mandatory')
        user = self.model(email=email)
        user.set_password(raw_password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user
