from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth import get_user_model
User = get_user_model()
from django.conf import settings

# the User model has five attributes: username, password, email, first name, last name
class OwnerAccount(models.Model):
    # link the OwnerAccount to a User model instance
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email


class Business(models.Model):
    owner = models.ForeignKey(OwnerAccount, on_delete=models.CASCADE)
    businessName = models.CharField(max_length=128)
    address = models.CharField(max_length=256)
    description = models.CharField(max_length=1024)
    workingTime = models.CharField(max_length=128)
    offersUntil = models.TimeField()
    # it might be possible to make tags an actual list by implementing a new field type
    # (https://docs.djangoproject.com/en/3.0/howto/custom-model-fields/).
    # But this seems to be enough.
    tags = models.CharField(max_length=256)

    picture = models.ImageField(upload_to='businesses', blank=True)

    slug=models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.businessName)
        super(Business, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Businesses'

    def __str__(self):
        return self.businessName


# offer is a weak entity, in spite of what the ER diagram says..
class Offer(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE)
    portionAmount = models.IntegerField()

    def __str__(self):
        return self.business.businessName + " ( " + str(self.portionAmount) + " )"


class UserAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # a foreign key so that it is possible to trace with which business the user made a reservation
    reservation = models.ForeignKey(Offer, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.user.email