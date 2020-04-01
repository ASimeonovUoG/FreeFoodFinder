from django.test import TestCase
from django.test import Client
from django.urls import reverse
from .models import Business, Offer, OwnerAccount, User, UserAccount
from .forms import BusinessForm


#helper functions
def create_test_business():
    business = Business(owner = OwnerAccount.objects.get_or_create(user=User.objects.get_or_create(email="trevi_italian@gmail.com")[0])[0],
                            businessName = "A Long Name For A Business!",
                            address =  "92 George Street, Glasgow, G1 1AB",
                            description =  "test",
                            workingTime = "12:00 - 22:00",
                            offersUntil = "22:00",
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
    u.set_password("MySecurePassword")
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


#tests
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

    def test_home_search_shows_featured_offers_if_none_are_available(self):
        c = Client()
        #this service is meant to be used in the UK, with UK postcodes. By supplying a foreign address we can
        #be sure that there won't be any offers in the area.
        response = c.post(reverse('finder:home'), {'query': "Sickingenstraße 41, 54296 Trier"})
        self.assertContains(response, "featured")

#similar to home view tests
class Find_food_tests(TestCase):
    def test_find_food_detects_false_postcode(self):
        c = Client()
        response = c.post(reverse('finder:find_food'), {'query': "???????", 'radius':'10'})
        #check if search error div is rendered
        self.assertContains(response, "search_error")

    def test_find_food_works_with_proper_postcode(self):
        c = Client()
        response = c.post(reverse('finder:find_food'), {'query': 'G12 8QQ','radius':'10'})
        self.assertFalse(self.assertContains(response, "search_error"))

    def test_find_food_shows_featured_offers_if_none_are_available(self):
        c = Client()
        #this service is meant to be used in the UK, with UK postcodes. By supplying a foreign address we can
        #be sure that there won't be any offers in the area.
        response = c.post(reverse('finder:find_food'), {'query': "Sickingenstr 41, 54296 Trier", 'radius':'10'})
        self.assertContains(response, "featured")


class ReservationTests(TestCase):
    def test_UserAccount_with_no_reservation_can_reserve(self):
        c = Client()
        user = create_test_userAccount()
        c.login(username=user.user.email, password="MySecurePassword")
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
        c.login(username=user.user.email, password="MySecurePassword")
        response = c.post(reverse('finder:reserve'), {'reserve_meal': offer_id})
        self.assertContains(response, "Something went wrong")


    def test_OwnerAccount_cannot_reserve(self):
        c = Client()
        owner = create_test_ownerAccount()
        c.login(username=owner.user.email, password="123password")
        offer_id = create_test_offer().id
        response = c.post(reverse('finder:reserve'), {'reserve_meal': offer_id})
        self.assertContains(response, "Something went wrong")

    def test_reserve_not_logged_in_gets_redirected(self):
        c = Client()
        offer_id = create_test_offer().id
        response = c.post(reverse('finder:reserve'), {'reserve_meal': offer_id})
        self.assertRedirects(response, reverse('finder:user_login'))


class AccountSettingsTests(TestCase):
    def test_password_change_fails_if_passwords_dont_match(self):
        c = Client()
        # tests are only done with userAccount because UserAccount and OwnerAccount use the same custom user model anyway
        user = create_test_userAccount()
        c.login(username=user.user.email, password="MySecurePassword")
        response = c.post(reverse('finder:settings'), {'email':user.user.email, 'new_password1':"myNewSecurePassword",'new_password2':"mynewSecurePassword!"})
        self.assertContains(response, "The two password fields didn&#39;t match")

    def test_email_change_fails_if_passwords_dont_match(self):
        c = Client()
        #tests are only done with userAccount because UserAccount and OwnerAccount use the same custom user model anyway
        user = create_test_userAccount()
        c.login(username=user.user.email, password="MySecurePassword")
        response = c.post(reverse('finder:settings'), {'email':"new_email@example.org", 'new_password1':"mySecurePassword",'new_password2':"mysecurePassword!"})
        self.assertContains(response, "The two password fields didn&#39;t match")

    def test_email_change_succeeds_with_matching_passwords(self):
        c = Client()
        #tests are only done with userAccount because UserAccount and OwnerAccount use the same custom user model anyway
        user = create_test_userAccount()
        c.login(username=user.user.email, password="MySecurePassword")
        response = c.post(reverse('finder:settings'), {'email':"new_email@example.org", 'new_password1':"MySecurePassword",'new_password2':"MySecurePassword"})
        self.assertRedirects(response, reverse('finder:account'))

    def test_password_change_succeeds_with_matching_passwords(self):
        c = Client()
        #tests are only done with userAccount because UserAccount and OwnerAccount use the same custom user model anyway
        user = create_test_userAccount()
        c.login(username=user.user.email, password="MySecurePassword")
        response = c.post(reverse('finder:settings'), {'email':user.user.email, 'new_password1':"mySecurePassword",'new_password2':"mySecurePassword"})
        self.assertRedirects(response, reverse('finder:account'))

    def test_email_and_password_change_succeed_with_matching_passwords(self):
        c = Client()
        #tests are only done with userAccount because UserAccount and OwnerAccount use the same custom user model anyway
        user = create_test_userAccount()
        c.login(username=user.user.email, password="MySecurePassword")
        response = c.post(reverse('finder:settings'), {'email':"new_email@example.org", 'new_password1':"mySecurePassword",'new_password2':"mySecurePassword"})
        self.assertRedirects(response, reverse('finder:account'))


#https://test-driven-django-development.readthedocs.io/en/latest/05-forms.html
class BusinessFormTests(TestCase):
    def test_business_form_accepts_correct_input(self):
        business_form = BusinessForm({
            "businessName" : "test business",
            "address" : "18 Lilybank Gardens, Glasgow G12 8RZ",
            "description" : "a test business for testing",
            "workingTime" : "9:00am - 18:00pm",
            "offersUntil" : "14:00",
            "tags" : "testing, test, business",
            "picture" : "trevi-italian.jpg"
        })
        self.assertTrue(business_form.is_valid())

    def test_business_form_detects_invalid_address(self):
        business_form = BusinessForm({
            "businessName" : "test business",
            "address" : "uiewfbiurbfouwebhfowrbhfuipbrgwipfgbadef'fi[aewfa]awefa[ew#fekapiho",
            "description" : "a test business for testing",
            "workingTime" : "9:00am - 18:00pm",
            "offersUntil" : "14:00",
            "tags" : "testing, test, business",
            "picture" : "trevi-italian.jpg"
        })
        self.assertFalse(business_form.is_valid())
        self.assertEqual(business_form.errors, {
            'address': ['invalid address']
        })

    def test_business_form_detects_invalid_offers_until_time(self):
        business_form = BusinessForm({
            "businessName" : "test business",
            "address" : "18 Lilybank Gardens, Glasgow G12 8RZ",
            "description" : "a test business for testing",
            "workingTime" : "9:00am - 18:00pm",
            "offersUntil" : "oidfhadihfoiheoih",
            "tags" : "testing, test, business",
            "picture" : "trevi-italian.jpg"
        })
        self.assertFalse(business_form.is_valid())
        self.assertEqual(business_form.errors, {'offersUntil': ['Enter a valid time.']})