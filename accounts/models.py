from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

from eli.settings import HUMAN_GENDER_CHOICES as HUMAN_GENDER_CHOICES
from eli.settings import EMAIL_HOST_USER as EMAIL_HOST_USER
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower


class UserProfileManager(BaseUserManager):
    """ Manager for user profiles """

    def create_user(self, email, name, password=None):
        """ Create a new user profile """
        if not email:
            raise ValueError('User must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, password):
        """ Create a new superuser profile """
        user = self.create_user(email, name, password)
        user.is_superuser = True
        user.is_staff = True

        user.save(using=self._db)

        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """ Database model for users in the system """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    gender = models.CharField(max_length=7, null=True, blank=False, choices=HUMAN_GENDER_CHOICES)

    objects = UserProfileManager()

    # this is where we change from using username to email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower("email"),
                name="user_email_lowercase",
            ),
        ]
    def __str__(self):
        """ Return string representation of our user """
        return  self.name + " " + self.email.lower()

    def clean(self):
        super().clean()
        self.email = self.email.lower()
        return self.email
    @classmethod
    def get_president_email(cls):
        """
        :return: email of first president user found
        """
        users = UserProfile.objects.all()
        for user in users:
            if user.is_president():
                return user.email
        return EMAIL_HOST_USER

    def is_a(self, group):
        """
        :return: True if user is in the group argument sent to this method.

        :param group: String of a group name
        """
        if group == 'Captain':
            return self.groups.filter(name='Captain').exists()
        if group == 'Player':
            return self.groups.filter(name='Player').exists()
        if group == 'President':
            return self.groups.filter(name='President').exists()
        if group == 'Referee':
            return self.groups.filter(name='Referee').exists()
        return False

    def is_active_player(self):
        from bassett.models import Team  # import here to prevent circular reasoning
        query = Team.get_player_teams(self, active=True,all_teams=True)
        if len(query) > 0:
            return True
        return False

    def is_captain(self):
        return self.groups.filter(name='Captain').exists()

    def is_player(self):
        return self.groups.filter(name='Player').exists()

    def is_president(self):
        return self.groups.filter(name='President').exists()

    def is_referee(self):
        return self.groups.filter(name='Referee').exists()

    @classmethod
    def is_user(cls, email):
        """
        :return: True if the email given is a current user.

        :param email:
        """
        email = email.lower()
        users = UserProfile.objects.all()
        for user in users:
            if user.email == email:
                return True
        return False


    ### HERE FOR examples -  delete this section when no longer needed
    # def does_not_have_permission(self,page):
    #     '''
    #     Return True if the person does not have permission on the give page. Otherwise, return False.
    #
    #     ~~~ consider using a list of the permissions needed on that page rather than the page as the parameter
    #     '''
    #     # ~~~ write code using the permissions system of django
    #     return False

    # def is_customer(self):
    #     return self.groups.filter(name='Customer').exists()
    #
    # def is_manager(self):
    #     # left this for an example
    #     # if self.has_perm('order.add_tabledetail'):
    #     #     print('has tabledetail in is_manager')
    #     # else:
    #     #     print('nnnnnnnnnnnnnnnnnnnnnnnnnnnno way')
    #     return self.groups.filter(name='Manager').exists()
    #
    # def is_owner(self):
    #     return self.groups.filter(name='Owner').exists()
    #
    # def is_sales_manager(self):
    #     return self.groups.filter(name='Sales Manager').exists()
    #
    # def is_team(self):
    #     return self.groups.filter(name='Team').exists()
    #
    # def menu_access(self,context):
    #     '''
    #     :return: Set the context for the menu options to show
    #     '''
    #
    #     if self.is_customer():
    #         for group in GROUPS['Customer']:
    #             context[group] = 'show'
    #     if self.is_team():
    #         for group in GROUPS['Team']:
    #             context[group] = 'show'
    #     if self.is_manager():
    #         for group in GROUPS['Manager']:
    #             context[group] = 'show'
    #     if self.is_owner():
    #         for group in GROUPS['Owner']:
    #             context[group] = 'show'
    #     if self.is_sales_manager():
    #         for group in GROUPS['Sales Manager']:
    #             context[group] = 'show'
    #
    # def management_access(self):
    #     '''
    #     :return: True or False if the person will have a management button on the customer site
    #     '''
    #     if not self.is_authenticated:
    #         return False
    #     groups = self.groups.all()
    #     for group in groups:
    #         if str(group) in MANAGEMENT_GROUPS:
    #             return True
    #     return False
