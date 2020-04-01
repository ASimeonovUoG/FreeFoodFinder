from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
User = get_user_model()
from finder.models import OwnerAccount, UserAccount


def isOwner(user):
    if OwnerAccount.objects.filter(user=user):
        # User is an owner
        return True
    return False

def isMortal(user):
    if UserAccount.objects.filter(user=user):
        # User is a mortal
        return True
    return False