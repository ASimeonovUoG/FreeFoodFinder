from django.contrib.auth.decorators import user_passes_test

def dec_test(user):
    print(user)
    return True

