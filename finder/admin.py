from django.contrib import admin
from finder.models import Business, OwnerAccount, Offer, UserAccount
# Register your models here.

admin.site.register(Business)
admin.site.register(OwnerAccount)
admin.site.register(Offer)
admin.site.register(UserAccount)