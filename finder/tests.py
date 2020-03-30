from django.test import TestCase
from django.test import Client
from django.urls import reverse
from .models import Business, Offer, OwnerAccount, User, UserAccount
import datetime

#helper functions
def create_test_business():
    business = Business(owner = OwnerAccount.objects.get_or_create(user=User.objects.get_or_create(email="trevi_italian@gmail.com")[0])[0],
                            businessName = "A Long Name For A Business!",
                            address =  "92 George Street, Glasgow, G1 1AB",
                            description =  "test",
                            workingTime = "12:00 - 22:00",
                            offersUntil = datetime.time(22, 0, 0),
                            tags = "Italian, dinner",
                            picture = "businesses/trevi-italian.jpg"
    )
    business.save()
    return business

def create_test_offer():
    offer = Offer(business = create_test_business(), portionAmount=100)
    offer.save()
    return offer

def create_test_userAccount():
    u = User.objects.get_or_create(email="a@a.com")[0]
    u.set_password("password123")
    u.save()
    user = UserAccount.objects.get_or_create(user=u)[0]
    user.save()
    return user

def create_test_ownerAccount():
    u = User.objects.get_or_create(email="trevi_italian@gmail.com")[0]
    u.set_password("123password")
    u.save()
    owner = OwnerAccount.objects.get_or_create(user=u)[0]
    owner.save()
    return owner

class BusinessModelTests(TestCase):
    def test_business_has_proper_slug(self):
        business = create_test_business()

        self.assertEqual(business.slug, 'a-long-name-for-a-business')


class OfferModelTests(TestCase):
    def test_portion_amount_is_positive(self):
        business = create_test_business()
        offer = Offer(business = business, portionAmount = -1)
        offer.save()

        self.assertTrue(offer.portionAmount >= 0)


class HomeViewTests(TestCase):
    def test_home_search_detects_false_postcode(self):
        c = Client()
        response = c.post(reverse('finder:home'), {'query': "???????"})

        #check if search error div is rendered
        self.assertContains(response, "search_error")


    def test_home_search_works_with_proper_postcode(self):
        c = Client()
        response = c.post(reverse('finder:home'), {'query': 'G12 8QQ'})

        self.assertFalse(self.assertContains(response, "search_error"))



class ReservationTests(TestCase):
    def test_UserAccount_with_no_reservation_can_reserve(self):
        c = Client()
        user = create_test_userAccount()
        c.login(username=user.user.email, password="password123")
        offer_id = create_test_offer().id
        response = c.post(reverse('finder:reserve'), {'reserve_meal': offer_id})
        self.assertContains(response, "Success!")


    def test_UserAccount_with_reservation_cannot_reserve(self):
        c = Client()
        user = create_test_userAccount()
        offer = create_test_offer()
        offer_id = offer.id
        user.reservation = offer
        user.save()
        c.login(username=user.user.email, password="password123")
        response = c.post(reverse('finder:reserve'), {'reserve_meal': offer_id})
        self.assertContains(response, "Something went wrong")


    def test_OwnerAccount_cannot_reserve(self):
        c = Client()
        owner = create_test_ownerAccount()
        c.login(username=owner.user.email, password="Password123")
        offer_id = create_test_offer().id
        response = c.post(reverse('finder:reserve'), {'reserve_meal': offer_id})
        self.assertContains(response, "Something went wrong")

