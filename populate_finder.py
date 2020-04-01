import os
import datetime
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'FreeFoodFinder.settings')

import django

django.setup()

from finder.models import OwnerAccount, UserAccount, Offer, Business
from django.contrib.auth import get_user_model
User = get_user_model()

def populate():
    owners = [{
            'email': "trevi_italian@gmail.com",
            'first_name': "Antonio",
            'last_name': "Trevi",
            'password': "Password123"
        },
        {
            'email': "alberta.stevenson@googlemail.com",
            'first_name': "Alberta",
            'last_name': "Stevenson",
            'password': "123Password"
        },
        {
            'email': "flora.smith@outlook.com",
            'first_name': "Flora",
            'last_name': "Smith",
            'password': "MyPassword123"
        },
        {
            'email': "jonanthan.harding@gmail.com",
            'first_name': "Jonathan",
            'last_name': "Harding",
            'password': "MyPassword289"
        },
    ]

    #initialise the owners
    for owner_data in owners:
        u = User.objects.get_or_create(email= owner_data['email'], first_name= owner_data['first_name'], last_name=owner_data['last_name'])[0]
        u.set_password(owner_data['password'])
        u.save()
        c = OwnerAccount.objects.get_or_create(user=u)[0]
        c.save()

    businesses = [
    {
    'owner': OwnerAccount.objects.get(user=User.objects.get(email="trevi_italian@gmail.com")),
    'name': "Trevi Italian Cuisine",
     'address': "92 George Street, Glasgow, G1 1AB",
     'description': "A unique Italian restaurant which has recently decided to reduce waste and donate leftover food to people in need instead",
    'workingTime':"12:00 - 22:00",
    'offersUntil': datetime.time(22, 0, 0),
    'tags':"Italian, dinner",
    'picture': "businesses/trevi-italian.jpg"
    },
    {
    'owner': OwnerAccount.objects.get(user=User.objects.get(email="flora.smith@outlook.com")),
    'name': "West End Bakery",
    'address': "141 Byres Road, Glasgow, G12 8TT",
    'description': "This family-run bakery close to the University of Glasgow sells fresh bread and pastries throughout the day.",
    'workingTime':"7:00 - 17:00",
    'offersUntil': datetime.time(17, 30, 0),
    'tags':"bakery, bread, cake, pastries",
    'picture': "businesses/west-end-bakery.jpeg"
    },
    {
    'owner': OwnerAccount.objects.get(user=User.objects.get(email="flora.smith@outlook.com")),
    'name': "Botanic Bakery",
     'address': "32 Clouston Street, Glasgow, G20 8QU",
     'description': "We specialise in organic bread using traditional methods and ingredients. Help us reduce waste by reserving now!",
     'workingTime': "7:00 - 17:00",
     'offersUntil': datetime.time(17, 30, 0),
     'tags': "bakery, bread, traditional, organic",
     'picture': "businesses/botanic-bakery.jpeg"
     },
    {
    'owner': OwnerAccount.objects.get(user=User.objects.get(email="alberta.stevenson@googlemail.com")),
    'name': "Woodlands Vegan Café",
     'address': "216 Woodlands Road, Glasgow, Glasgow, G3 6LN",
     'description': "We sell vegan cakes and sandwiches to suit all tastes, and would like to reduce waste by donating leftovers. Order now to reserve a FREE meal!",
     'workingTime': "9:00 - 16:00",
     'offersUntil': datetime.time(16, 30, 0),
     'tags': "vegan, cafe",
     'picture': "businesses/woodlands-vegan.jpeg"
     },
    {
    'owner' : OwnerAccount.objects.get(user=User.objects.get(email="jonanthan.harding@gmail.com")),
    'name': "Bath Street Burgers",
     'address': "212 Bath Street, Glasgow, G2 4HZ",
     'description': "An award-winning burger restaurant with something for everyone. Free leftover food every day!",
     'workingTime': "11:00 - 22:00",
     'offersUntil': datetime.time(22, 0, 0),
     'tags': "burgers, dinner",
     'picture': "businesses/bath-street-burgers.jpeg"
     },
    ]

    for b in businesses:

            b = Business.objects.get_or_create(
                                            owner=b['owner'],
                                            businessName= b['name'],
                                           address=b['address'],
                                           description=b['description'],
                                           workingTime=b['workingTime'],
                                           offersUntil=b['offersUntil'],
                                           tags=b['tags'],
                                           picture=b['picture'])[0]
            b.save()

    Offer.objects.get_or_create(business = Business.objects.get(businessName = "Bath Street Burgers"), portionAmount=51)[0].save()
    Offer.objects.get_or_create(business = Business.objects.get(businessName = "Trevi Italian Cuisine"), portionAmount=100)[0].save()
    Offer.objects.get_or_create(business = Business.objects.get(businessName = "West End Bakery"), portionAmount=20)[0].save()



    users = [{
            'email': "jack.frost@outlook.org",
            'password': "1234password",
            'reservation' : Offer.objects.get(business = Business.objects.get(businessName = "Bath Street Burgers"))
        },
        {
            'email': "jude.quinn@gmail.com",
            'password': "password99"
        },
        {
            'email' : "mary.louise@gmail.com",
            'password': "432password",
            'reservation': Offer.objects.get(business =  Business.objects.get(businessName = "West End Bakery"))
        },
        {
            'email': "don.lewis@gmx.de",
            'password': "password987"
        },
        {
            'email': "kerry.johnstone@googlemail.com",
            'password': "mypassword123"
        }
        ]

    for user_data in users:
        u = User.objects.get_or_create(email= user_data['email'])[0]
        u.set_password(user_data['password'])
        u.save()
        if user_data.get('reservation', False):
            c = UserAccount.objects.get_or_create(user=u, reservation = user_data['reservation'])[0]
        else:
            c = UserAccount.objects.get_or_create(user=u)[0]
        c.save()



if __name__ == '__main__':
    print('Starting population script...')
    populate()