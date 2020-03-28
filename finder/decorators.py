from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
User = get_user_model()
from finder.models import OwnerAccount, UserAccount


def isOwner(user):
    '''
    print(isinstance(user, User))
    print(isinstance(user, OwnerAccount))
    print(isinstance(user, UserAccount))

    print(type(user))
    print(OwnerAccount.objects.filter(user=user))
    print("Users |")
    print(UserAccount.objects.filter(user=user))
    '''
    if OwnerAccount.objects.filter(user=user):
        # User is an owner
        return True
    return False