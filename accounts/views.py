from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.views.generic import View
from django.urls import reverse_lazy, reverse
from django.utils.safestring import mark_safe # to add labels in forms
from django.utils.translation import gettext, gettext_lazy as _

import random
from .forms import *

from eli.settings import EMAIL_HOST_USER as EMAIL_HOST_USER

class EmailCodeView(View):
    #login_url = reverse_lazy('login')  # give login location
    template_name = "easy.html"

    def get(self, request):
        form = EmailCodeForm()
        context = {}
        context['h1'] = 'Enter Taylor Email Here'
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self,request):
        context = {}
        form = EmailCodeForm(request.POST)

        if form.is_valid():
            email = form.get_email()

            if not request.session.session_key:
                # a logged-in user has a key an anonymous user has None so get one for the anonymous user
                request.session.save()
            request.session['email'] = email

            request.session['code'] = self.send_new_account_email(email)
            return HttpResponseRedirect(reverse('verify_code'))
        context['form'] = form
        return render(request, self.template_name, context)

    def send_new_account_email(self, email) -> str:
        '''
        Send email that someone signed up.
        '''
        subject: str = 'Taylor Intramural Email Verification Code'
        from_email = EMAIL_HOST_USER
        recipient_list = [email]
        randomNumber: str = randstr()
        print('put this code in hehe:', randomNumber)
        message: str = "Here's your code: " + randomNumber
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return randomNumber

class ForgotPasswordView(View):
    template_name = 'forgotpassword.html'
    def get(self, request):
        form = ForgotPasswordForm()
        context = {}
        context['title'] = 'Forgot Password'
        context['name'] = 'Forgot Password'
        context['form'] = form
        msg = "* enter your email<br>"
        msg += "* click OK<br>"
        msg += "* then see your email for a reset password"
        context['message'] = _(mark_safe(msg))
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = ForgotPasswordForm(request.POST)
        email = request.POST.get('email')
        is_user = UserProfile.is_user(email)
        print("is_user",is_user)
        if not is_user:
            return HttpResponseRedirect(reverse('message', args=('nonuser',)))
        if form.is_valid():
            email = request.POST.get('email')
            new_password = randstr(length=17)
            u = UserProfile.objects.get(email=email)
            u.set_password(new_password)
            u.save()
            send_email('Password Reset', new_password, [email])
            return HttpResponseRedirect(reverse('message', args=('fpwd',)))
        context = {}
        context['title'] = 'Forgot Password'
        context['name'] = 'Forgot Password'
        context['form'] = form
        msg = "* enter your email<br>"
        msg += "* click OK<br>"
        msg += "* then see your email for a reset password"
        context['message'] = _(mark_safe(msg))
        return render(request, self.template_name, context)

class MailView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')  # give login location

    template_name = 'scheduling.html'
    def get(self, request):
        form = MailForm()
        context = {}
        context['user_name'] = request.user.name
        context['browser_bar_title'] = 'Mass Mailer'
        context['h1'] = 'Mass Mailer'
        context['form'] = form
        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = MailForm(request.POST)
        if form.is_valid():
            president_email = UserProfile.get_president_email()
            users = UserProfile.objects.all()
            group = request.POST.get('group')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            send_email(subject+'-sent to '+group, message, [president_email])
            if group == 'Player':
                for user in users:
                    if user.is_active_player():
                        send_email(subject, message, [user.email])
                return HttpResponseRedirect(reverse('home'))
            if group == 'All':
                for user in users:
                    if user.is_referee() or user.is_captain() or user.is_active_player():
                        send_email(subject, message, [user.email])
                return HttpResponseRedirect(reverse('home'))
            # all other groups
            for user in users:
                if user.is_a(group):
                    send_email(subject, message, [user.email])
            return HttpResponseRedirect(reverse('home'))
        context = {}
        context['browser_bar_title'] = 'Mass Mailer'
        context['h1'] = 'Mass Mailer'
        context['form'] = form
        return render(request, self.template_name, context)

class MessageView(View):
    """
    This is a canned messaging page to send messages via preset codes rather than sending via the URL.
    """
    template_name = 'message.html'
    def get(self, request, code='fpwd'):
        preset_messages = {
            'fpwd': "Go to your email and get your password and then click the link below.",
            'nonuser': " You are not a registered user. Please check the email or use the Sign Up link. ",
        }
        preset_link_message = {
            'fpwd': "Return to login page.",
            'nonuser': "Return to login page.",
        }
        preset_h1 = {
            'fpwd': "Forgotten Password Help",
            'nonuser': "Non-Registered User Message",
        }
        form = ForgotPasswordForm()
        context = {}
        context['h1'] = preset_h1[code]
        context['message'] = preset_messages[code]
        context['link_text'] = preset_link_message[code]
        return render(request, self.template_name, context)


class PasswordView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')  # give login location

    template_name = 'easy.html'
    def get(self, request):
        context = {}
        context['title'] = 'Password Update'
        context['name'] = 'Password Update'
        context['form'] = PasswordForm(user=request.user)
        context['h2'] = "Reset Password"
        msg = "Warning: You will be logged out when you submit, so make sure you type the new password into a notepad,"
        msg += " so you can use it to get back into your account."
        context['warning'] = msg
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = PasswordForm(request.POST,user=request.user)
        if form.is_valid():
            #user = User.objects.get(id=request.user.id)
            password = request.POST['password']
            u = request.user
            u.set_password(password)
            u.save()
            return HttpResponseRedirect(reverse('home'))
        else:
            context = {}
            context['title'] = 'Password Update'
            context['name'] = 'Password Update'
            context['form'] = PasswordForm(request.POST,user=request.user)
            return render(request, self.template_name, context)

def randstr(length: int = 6) -> str:
    '''
    Produce a random string of numbers and letters with optional prefix and postfix and the given length.
    '''
    letnum = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
              'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
              '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    x: str = ''
    for y in range(length):
        x += random.choice(letnum)
    return x

def send_email(subject, message, recipient_list,fail_silently=True):
    '''
    Send email
    '''
    from_email = EMAIL_HOST_USER
    send_mail(subject, message, from_email, recipient_list, fail_silently=fail_silently)

class SignUpView(CreateView):
    # form_class = CustomUserCreationForm
    # success_url = reverse_lazy("sign-up")
    template_name = "registration/signup.html"

    # def get_form_kwargs(self):
    #     kwargs=super().get_form_kwargs()
    #     kwargs['email'] = request.sessions['email']
    #     return kwargs

    def get(self, request):
        # should I super the CreateView's get?
        print('request',request)
        if not request.session.session_key:
            # a logged-in user has a key an anonymous user has None so get one for the anonymous user
            request.session.save()
        print('request',request.session)

        context = {}
        email = request.session['email']
        data = {'email': email}
        form = CustomUserCreationForm(email=email,initial = data)
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request):
        context = {}
        form = CustomUserCreationForm(request.POST,email=request.session['email'])
        if form.is_valid():
            print('valid')
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse('home'))
        context['form'] = form
        print('not valid')
        print(form.errors.as_data())
        return render(request, self.template_name, context)

class VerifyCodeView(View):
    login_url = reverse_lazy('login')  # give login location
    template_name = 'easy.html'

    def get(self, request):
        form = VerifyCodeForm(request=request)
        context = {}
        context['form'] = form
        context['h1'] = "Enter the code that was sent to your email"
        return render(request, self.template_name, context)

    def post(self,request):
        context = {}
        form = VerifyCodeForm(request.POST,request=request)
        if form.is_valid():
            return HttpResponseRedirect(reverse('sign_up'))
        context['form'] = form
        return render(request, self.template_name, context)
