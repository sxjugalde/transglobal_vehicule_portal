from django.contrib.auth.tokens import PasswordResetTokenGenerator


# Account confirmation token gen
class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.email_confirmed}"


account_activation_token = AccountActivationTokenGenerator()
