

from django.utils.http import int_to_base36, base36_to_int

from django.contrib.auth.tokens import PasswordResetTokenGenerator


def get_login_tokens(user):
    token_generator = PasswordResetTokenGenerator()

    return dict(user_token = int_to_base36(user.id),
                key_token = token_generator.make_token(user))

