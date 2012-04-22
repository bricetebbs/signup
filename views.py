
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django import forms
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template import loader, Context

from django.utils.http import int_to_base36, base36_to_int

from django.contrib.auth import login as login_user

from django.contrib.auth.views import login as login_view
from django.contrib.auth.views import logout as logout_view
from django.contrib.auth.views import password_change as password_change_view

from django.contrib.auth.forms import UserCreationForm
from django.conf import settings

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.translation import ugettext as _

from django.contrib.auth.decorators import login_required
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import authenticate

import logging

logger = logging.getLogger('signup')

class SignupBackEnd(ModelBackend):
    """
    Provide an authenticator for using the email signup.
    """
    def authenticate(self, user_token, key_token):
        logger.debug("Attempting auth: user token is (%s, %d) " % (user_token, base36_to_int(user_token)))
        try:
            token_generator=PasswordResetTokenGenerator()
            user = get_object_or_404(User, pk=base36_to_int(user_token))
            logger.debug("User: %s checking login token" % user.username)
            if token_generator.check_token( user, key_token) and user.is_active:
                logger.debug("User: %s authenticated via token" % user.username)
                return user
        except User.DoesNotExist:
            return None



class SignupEmailForm(forms.Form):
    """
    All we need to signup is an email address
    """
    email_address = forms.EmailField(widget=forms.TextInput(attrs={'size':'45'}))


def send_token_message(host, user, template, subject, new_user=False, extra_context=None):
    """
    Send an email to the the user with a new token
    """
    token_generator = PasswordResetTokenGenerator()
  
    t = loader.get_template(template)
    c = {
            'email': user.email,
            'host':  host,
            'user_token': int_to_base36(user.id),
            'user': user,
            'key_token': token_generator.make_token(user),
            'new_user' : new_user,
        }

    if extra_context:
        # If we have extra_content we need for the template
        for key in extra_context:
            c[key] = extra_context[key]

    # send the user an email with the template filled out
    # the actual link can be created using:
    # {% url signup_login_by_email user_token key_token %}
    send_mail(subject, t.render(Context(c)), settings.EMAIL_HOST_USER, [user.email])


def send_email_auth_token(request, user, new_user=False):
    """
    Send a new token
    """
    subject = _("New Login token for %s") % request.get_host()
    return send_token_message(request.get_host(), user, 'email_auth_form.html',subject, new_user=new_user )


def signup_email(request):
    """
    THis page is for signing in by email. THe user gives their email in a form via POST
    and the system will respond by sending them a new token via email.
    """
    email_form = SignupEmailForm(request.POST)
    if email_form.is_valid():
        email = email_form.cleaned_data['email_address']
        email = email.strip().lower()
        try:
            user =  User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
            
        new_user = True
        if user:
            # we had this guy before reset his password
            send_email_auth_token(request, user, new_user=False)
            logger.debug("User: %s getting new key." % user.username)
            new_user = False
        else:
            user =  User.objects.create_user(email, email, '')

            logger.debug("User: %s created sending email." % user.username)
            send_email_auth_token(request, user, new_user=True)

        return render(request, 'email_sent.html', dict(email=email, new_user=new_user))
    else:
         return login_view(request, template_name='login_main.html',
                    extra_context=dict(email_form=email_form))


def signup_login(request):
    """
    This is the GET method for loading the Signup form
    """
    if request.user.is_authenticated():
        return redirect(settings.LOGIN_REDIRECT_URL)
    email_form = SignupEmailForm
    return login_view(request, template_name='login_main.html',
                    extra_context=dict(email_form=email_form))

def signup_logout(request):
    """
    Just wrapping the built in
    """
    return logout_view(request, template_name='logged_out.html')


def signup_login_by_email(request, user_token, key_token):
    """
    This is the view which the login link will load
    """

    user = authenticate(user_token = user_token, key_token=key_token)
    if user:
        login_user(request, user)
        if 'next' in request.GET:
            return redirect(request.GET['next'])
        return redirect(settings.LOGIN_REDIRECT_URL)
    return HttpResponse('Sorry, Your login link has expired or is invalid. Please select a new one.')




class UserUpdateForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("username",)

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['autocomplete']='off'

    def clean_username(self):
        if self.cleaned_data["username"] == self.instance.email:

            raise forms.ValidationError(_("Choose something other than your email address for the username"))

        if self.instance.username != self.instance.email: # then we have set if before
            raise forms.ValidationError(_("We have already set the username for this user before."))

        return super(UserUpdateForm, self).clean_username()

@login_required
def signup_change_username_and_password(request):
    if request.method=='GET':
        user_form = UserUpdateForm(instance=request.user)
    else:
        user_form = UserUpdateForm(request.POST,instance=request.user)
        if user_form.is_valid():
            user_form.save()
            return redirect(settings.LOGIN_REDIRECT_URL)


    return render(request, 'change_username_and_password.html', dict(user_form=user_form))

@login_required
def signup_change_password(request):
    return password_change_view(request, template_name='change_password.html',
                                post_change_redirect=settings.LOGIN_REDIRECT_URL)

