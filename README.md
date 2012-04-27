## signup


A Django App for doing email only signup.
A layer on top of django auth which makes it easy to set up a system
where people just use their email as the mail way to login as described [here](http://blog.headspin.com/?p=352)

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