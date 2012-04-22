signup
======

A Django App for doing email only signup. A layer on top of django auth which makes it easy to set up a system
where people just use their email as the mail way to login.

Setting it up
=============

AUTHENTICATION_BACKENDS = ('signup.views.SignupBackEnd', 'django.contrib.auth.backends.ModelBackend',)

LOGIN_URL = '/signup/login/'
LOGOUT_URL = '/signup/logout/'

And add signup to INSTALLED_APPS

Also you need to include the URLs

  url(r'^signup/', include('signup.urls')),

Your django server needs to be configured to send mail and you should edit the templates to your liking.

