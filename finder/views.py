from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.urls import reverse
from finder.models import Business, Offer, OwnerAccount, UserAccount

from finder.distance import calculate_distance, read_google_key
from finder.forms import UserForm, UserAccountForm, UserLoginForm, BusinessForm, Update_form, OfferForm

from django.contrib.auth.decorators import user_passes_test, login_required
from finder.decorators import isOwner
from django.contrib.auth.forms import PasswordChangeForm, UserChangeForm
from django.contrib.auth import update_session_auth_hash

# Create your views here.


def about(request):
    return render(request, 'finder/about.html')


def contact(request):
    return render(request, 'finder/contact.html')


def reserve(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            this_user = UserAccount.objects.filter(user=request.user)

        #no UserAccount was found where request.user is the user. That is, the user is an owner.
            if len(this_user) == 0:
                reserved_business = None
            else:
                this_user = this_user[0]
                if this_user.reservation is None:
                    offer_id = request.POST['reserve_meal'].strip()
                    offer = Offer.objects.get(id=offer_id)
                    this_user.reservation = offer
                    offer.portionAmount = offer.portionAmount - 1
                    this_user.save()
                    offer.save()
                    reserved_business = offer.business
                else:
                    reserved_business = None
            return render(request, 'finder/reserve.html',
                      {"reserved_business": reserved_business})
    return render(request, 'finder/reserve.html', {})


def home(request):
    distance_threshold = 10
    FEATURED_THRESHOLD = 50
    offers = []
    invalid = False
    no_results = False
    # note that everything in this if-clause also appears in find_food. It would be possible to first validate the input and then either display an
    # error message on home.html or call find_food(). However if the input is valid that would require two calls to the maps API (one to validate
    # the input, one to calculate the distance). Calls to the maps API are expensive (as in, they charge money for great amounts of calls). So it
    # makes sense to limit the amount of calls to this API. Of course it would also be possible to just load the find_food template either way
    # and display the error message there, but that can be confusing.
    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            businesses = Business.objects.all()
            for b in businesses:
                try:
                    if calculate_distance(b.lat, b.long,
                                          query) < distance_threshold:
                        offer = Offer.objects.filter(business=b)
                        # appends the offer because offers are associated with businesses. And a business should only appear
                        # in the search results if it has an offer
                        if len(offer) > 0:
                            offers.append(offer[0])
                # calculate_distance raises ValueError if it can't parse the data
                except ValueError:
                    invalid = True
                    offers = []
                    break

            if not invalid:
                # if the input is valid but there are no close offers, generate the list of featured offers instead, to send to find_food
                if len(offers) == 0:
                    no_results = True
                    all_offers = Offer.objects.all()
                    for o in all_offers:
                        if o.portionAmount > FEATURED_THRESHOLD:
                            offers.append(o)

                return render(request, 'finder/find_food.html', {
                    'invalid': invalid,
                    'no_results': no_results,
                    'offers': offers
                })

    featured_offers = []
    offers = Offer.objects.all()
    for o in offers:
        if o.portionAmount > FEATURED_THRESHOLD:
            featured_offers.append(o)

    return render(request, 'finder/home.html', {
        'invalid': invalid,
        'featured_offers': featured_offers
    })


def find_food(request):
    FEATURED_THRESHOLD = 50
    distance_threshold = 10
    offers = []
    invalid = False
    no_results = False
    if request.method == 'POST':
        query = request.POST['query'].strip()
        radius = request.POST['radius'].strip()
        if radius:
            distance_threshold = int(radius)

        if query:
            businesses = Business.objects.all()
            for b in businesses:
                try:
                    if calculate_distance(b.lat, b.long,
                                          query) < distance_threshold:
                        offer = Offer.objects.filter(business=b)

                        if len(offer) > 0:
                            offers.append(offer[0])

                except ValueError:
                    invalid = True
                    offers = []
                    break
            if not invalid:

                if len(offers) == 0:
                    no_results = True
                    all_offers = Offer.objects.all()
                    for o in all_offers:
                        if o.portionAmount > FEATURED_THRESHOLD:
                            offers.append(o)

            return render(request, 'finder/find_food.html', {
                'invalid': invalid,
                'no_results': no_results,
                'offers': offers
            })
    else:
        return render(request, 'finder/find_food.html', {})


def show_business(request, business_name_slug):
    context_dict = {}

    try:
        business = Business.objects.get(slug=business_name_slug)
        context_dict['business'] = business
        context_dict['key'] = read_google_key()

        #if the restaurant currently has an offer, put that in the context dict as well
        offer = Offer.objects.filter(business=business)
        if len(offer) != 0:
            context_dict['offer'] = offer[0]

    except Business.DoesNotExist:

        context_dict['business'] = None

    return render(request, 'finder/individualBusiness.html', context_dict)


def signUp(request):
    registered = False
    if request.method == "POST":
        user_form = UserForm(request.POST)
        account_form = UserAccountForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            # Branching logic as to if we want to create an Owner
            # or a Mortal user.
            if request.POST.get("isOwner") == "True":
                user.set_password(user.password)
                user.save()

                owner = OwnerAccount.create(user)
                owner.save()

                registered = True
            else:
                user.set_password(user.password)
                user.save()

                account = account_form.save(commit=False)
                account.user = user

                account.save()

                registered = True

        else:
            None
            #print(user_form.errors, account_form.errors)
    else:
        user_form = UserForm()
        account_form = UserAccountForm()

    context_dict = {
        'user_form': user_form,
        'account_form': account_form,
        'registered': registered
    }

    return render(request, 'finder/signUp.html', context_dict)


def user_loginOLD(request):
    if request.method == "POST":
        username = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(email=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('finder:home'))
            else:
                return HttpResponse("Your account is disabled")
        else:
            return HttpResponse("Your credentials are invalid")
    else:
        login_form = UserLoginForm()
        context_dict = {'login_form': login_form}
        return render(request, 'finder/user_login.html', context_dict)


def user_login(request):
    login_form = UserLoginForm(request.POST or None)
    if request.POST and login_form.is_valid():
        user = login_form.login(request)
        if user:
            login(request, user)
            return redirect(reverse('finder:home'))  # Redirect to a success page.
    context_dict = {'login_form': login_form}
    return render(request, 'finder/user_login.html', context_dict)


def user_logout(request):
    logout(request)
    return redirect(reverse('finder:home'))


@login_required
@user_passes_test(isOwner)
def support(request):
    return render(request, 'finder/support.html')


@login_required
@user_passes_test(isOwner)
def myBusinesses(request):
    this_owner = OwnerAccount.objects.get(user=request.user)
    owner_businesses = list(Business.objects.filter(owner=this_owner))
    return render(request, 'finder/myBusinesses.html',
                  {'user_businesses': owner_businesses})


@login_required
def account(request):
    return render(request, 'finder/account.html')


@login_required
@user_passes_test(isOwner)
def adminPanel(request, business_name_slug):
    current_offer = None
    business = None
    business = get_object_or_404(Business, slug = business_name_slug)

    #if an owner types in the business name slug of a business that they do not own
    #they can still access its admin panel because the decorator only checks if the
    #user is an owner. This is a simple way of preventing that.
    if business.owner != get_object_or_404(OwnerAccount, user=request.user):
        return HttpResponse("You do not have permission to view this site.")

    business_offer = Offer.objects.filter(business=business)
    if len(business_offer) != 0:
        current_offer = business_offer[0]

    if request.method == 'POST':
        #check if the button with name "submit_form" was clicked
        if "submit_form" in request.POST:
            #need request.FILES so that the user can upload a new picture
            business_form = BusinessForm(request.POST, request.FILES, instance=business)

            if business_form.is_valid():
                business = business_form.save(commit=False)
                business.owner = get_object_or_404(OwnerAccount, user=request.user)
                business.save()
                return redirect('finder:myBusinesses')

        #ending an offer
        elif "end_offer" in request.POST:
            end_offer_id = request.POST['end_offer'].strip()
            if end_offer_id:
                end_offer(end_offer_id)
            return redirect('finder:myBusinesses')

        #adding an offer
        elif "add_offer" in request.POST:
            add_offer_form = OfferForm(request.POST)
            if add_offer_form.is_valid():
                offer = add_offer_form.save(commit=False)
                offer.business = business
                offer.save()
                return redirect('finder:myBusinesses')


    #prepopulate the fields
    business_form = BusinessForm(data = {'businessName' : business.businessName,
                                             'address': business.address,
                                             'description': business.description,
                                             'workingTime': business.workingTime,
                                             'offersUntil': business.offersUntil,
                                             'tags': business.tags,
                                             'picture': business.picture})

    add_offer_form = OfferForm()

    context_dict = {'business_form': business_form, 'add_offer_form': add_offer_form, 'current_offer':current_offer, 'business':business}
    return render(request, 'finder/adminPanel.html', context_dict)

#helper function for adminPanel
def end_offer(end_offer_id):
    offer = Offer.objects.get(id=end_offer_id)
    users_with_reservation = list(UserAccount.objects.filter(reservation=offer))
    for u in users_with_reservation:
        u.reservation = None
        u.save()
    offer.delete()

@login_required
def settings(request):
    if request.method == 'POST':
        password_form = PasswordChangeForm(data=request.POST,
                                           user=request.user)
        email_form = Update_form(request.POST, instance=request.user)

        #print(password_form)

        if password_form.is_valid() and email_form.is_valid():
            user = password_form.save()
            email_form.save()
            update_session_auth_hash(request, password_form.user)
            return redirect('finder:account')

    else:
        password_form = PasswordChangeForm(user=request.user)
        email_form = Update_form(instance=request.user)

    context_dict = {'password_form': password_form, 'email_form': email_form}
    return render(request, 'finder/settings.html', context_dict)