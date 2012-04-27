## signup


A Django App for doing email only signup.

# Overview
Signup is a layer on top of django auth which makes it easy to set up a system
where people just use their email as the mail way to login as described [here](http://blog.headspin.com/?p=352).

The basic flow is that when someone goes to the login page they can use a normal django.auth username/password or just give
an email address. This email address will be used to authenticate them in the same way that a password recovery email works but
without the password in the first place.

A user can also create a normal username/password if they prefer.


## Setting it up

In settings.py you probably want:

     AUTHENTICATION_BACKENDS = ('signup.views.SignupBackEnd', 'django.contrib.auth.backends.ModelBackend',)

     LOGIN_URL = '/signup/login/'
     LOGOUT_URL = '/signup/logout/'

And add signup to INSTALLED_APPS

Also you need to include the URLs

     url(r'^signup/', include('signup.urls')),

Note:

* Your django server needs to be configured to be able send mail
* You should edit the templates to your liking




## License

MIT , see the `LICENSE` file for details.