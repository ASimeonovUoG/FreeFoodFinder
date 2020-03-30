from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth import get_user_model
User = get_user_model()
from django.conf import settings
from finder import distance

# the User model has five attributes: password, email, first name, last name
class OwnerAccount(models.Model):
    # link the OwnerAccount to a User model instance
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # driversLicense/OwnerPermitID...

    def __str__(self):
        return self.user.email
    
    @classmethod
    def create(cls, user):
        owner = cls(user=user)
        # do something with the book
        return owner


class Business(models.Model):
    owner = models.ForeignKey(OwnerAccount, on_delete=models.CASCADE)
    businessName = models.CharField(max_length=128)
    address = models.CharField(max_length=256)
    description = models.CharField(max_length=1024)
    workingTime = models.CharField(max_length=128)
    offersUntil = models.TimeField()
    tags = models.CharField(max_length=256)
    picture = models.ImageField(upload_to='businesses', blank=True)

    lat = models.FloatField()
    long = models.FloatField()
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.businessName)
        #the get_coords function returns a tuple with latitude and longitude
        coords = distance.get_coords(self.address)
        self.lat = coords[0]
        self.long = coords[1]
        super(Business, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Businesses'

    def __str__(self):
        return self.businessName


# offer is a weak entity, in spite of what the ER diagram says..
class Offer(models.Model):
    business = models.OneToOneField(Business, on_delete=models.CASCADE)
    portionAmount = models.IntegerField()

    def save(self, *args, **kwargs):
        if self.portionAmount < 0:
            self.portionAmount = 0
        super(Offer, self).save(*args, **kwargs)

    def __str__(self):
        return self.business.businessName + " ( " + str(self.portionAmount) + " )"


class UserAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # a foreign key so that it is possible to trace with which business the user made a reservation
    reservation = models.ForeignKey(Offer, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.user.email