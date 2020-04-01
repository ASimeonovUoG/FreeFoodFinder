from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.urls import reverse
from finder.models import Business, Offer, OwnerAccount, UserAccount

from finder.distance import calculate_distance, read_google_key
from finder.forms import UserForm, UserAccountForm, UserLoginForm, BusinessForm, Update_form, OfferForm

from django.contrib.auth.decorators import user_passes_test, login_required
from finder.decorators import isOwner
from django.contrib.auth.forms import UserChangeForm, SetPasswordForm
from django.contrib.auth import update_session_auth_hash
# Create your views here.


def about(request):
    # Simply render a page
    return render(request, 'finder/about.html')


def contact(request):
    # Simply render a page
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
        else:
            return redirect(reverse('finder:user_login'))
    #this site should only be accessed following a POST request
    else:
        return redirect(reverse('finder:home'))


def home(request):
    FEATURED_THRESHOLD = 50
    invalid = False

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            return render_list_of_offers(request, query)
    else:
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
    distance_threshold = 10

    if request.method == 'POST':
        query = request.POST['query'].strip()
        radius = request.POST['radius'].strip()
        if radius:
            distance_threshold = int(radius)
        if query:
            return render_list_of_offers(request, query, distance_threshold)

    else:
        return render(request, 'finder/find_food.html', {})


#helper function for home and find_food. Generates a list of offers close to query,
#or a list of featured offers if there are no close offers, and returns the appropriate
#HTTPResponse object
def render_list_of_offers(request, query, distance_threshold=10):
    offers = []
    FEATURED_THRESHOLD = 50
    invalid = False
    no_results = False
    businesses = Business.objects.all()
    for b in businesses:
        try:
            if calculate_distance(b.lat, b.long, query) < distance_threshold:
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
    # Use this flag to indicate success in template
    registered = False
    if request.method == "POST":
        # Init both forms - used if we have mortal users.
        user_form = UserForm(request.POST)
        account_form = UserAccountForm(request.POST)
        if user_form.is_valid():
            # Init user object
            user = user_form.save()
            # By the hidden field in the form we recognize if we want to create an Owner or a Mortal user.
            if request.POST.get("isOwner") == "True":
                # Set password and save user object
                user.set_password(user.password)
                user.save()
                # Create owner account object passing the user
                owner = OwnerAccount.create(user)
                owner.save()
                # Indicate success
                registered = True
            else:
                # Set password and save user object
                user.set_password(user.password)
                user.save()
                # Init account form object and pass the object then save.
                account = account_form.save(commit=False)
                account.user = user
                account.save()
                # Indicate success
                registered = True

        else:
            None
            # If form is not valid, it will be automatically included in the form and passed
            # to the template via the context dictionary.
    else:
        # If not a POST - just render two empty forms
        user_form = UserForm()
        account_form = UserAccountForm()
    # Pass forms and flag to template
    context_dict = {
        'user_form': user_form,
        'account_form': account_form,
        'registered': registered
    }

    return render(request, 'finder/signUp.html', context_dict)


def user_login(request):
    # Init an empty form or with the POST data if any
    login_form = UserLoginForm(request.POST or None)
    # If we have a POST request
    if request.POST and login_form.is_valid():
        # Login is an additional method in the form.
        user = login_form.login(request)
        if user:
            login(request, user)
            return redirect(
                reverse('finder:home'))  # Redirect to a success page.
    # If we do not have POST request - return an empty form to render
    context_dict = {'login_form': login_form}
    return render(request, 'finder/user_login.html', context_dict)


def user_logout(request):
    # Take the user form the request and log them out.
    logout(request)
    return redirect(reverse('finder:home'))


@login_required
@user_passes_test(isOwner)
def support(request):
    return render(request, 'finder/support.html', {'is_owner': True})


@login_required
@user_passes_test(isOwner)
def myBusinesses(request):
    this_owner = OwnerAccount.objects.get(user=request.user)
    owner_businesses = list(Business.objects.filter(owner=this_owner))
    return render(request, 'finder/myBusinesses.html', {
        'user_businesses': owner_businesses,
        'is_owner': True
    })


@login_required
def account(request):
    #affects rendering of the side bar
    is_owner = OwnerAccount.objects.filter(user=request.user).exists()
    return render(request, 'finder/account.html', {'is_owner': is_owner})


@login_required
@user_passes_test(isOwner)
def adminPanel(request, business_name_slug):
    current_offer = None
    business = get_object_or_404(Business, slug=business_name_slug)

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
            business_form = BusinessForm(request.POST,
                                         request.FILES,
                                         instance=business)

            if business_form.is_valid():
                business = business_form.save(commit=False)
                business.owner = get_object_or_404(OwnerAccount,
                                                   user=request.user)
                business.save()
                return redirect('finder:myBusinesses')
            else:
                #render the entire page again, but with the same form, so the errors are displayed
                add_offer_form = OfferForm()
                context_dict = {
                    'business_form': business_form,
                    'add_offer_form': add_offer_form,
                    'current_offer': current_offer,
                    'business': business,
                    'is_owner': True
                }
                return render(request, 'finder/adminPanel.html', context_dict)

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

        elif "delete" in request.POST:
            business_id = request.POST['delete'].strip()
            if business_id:
                delete_business(business_id)
            return redirect('finder:myBusinesses')

    #prepopulate the fields
    business_form = BusinessForm(
        data={
            'businessName': business.businessName,
            'address': business.address,
            'description': business.description,
            'workingTime': business.workingTime,
            'offersUntil': business.offersUntil,
            'tags': business.tags,
            'picture': business.picture
        })

    add_offer_form = OfferForm()

    context_dict = {
        'business_form': business_form,
        'add_offer_form': add_offer_form,
        'current_offer': current_offer,
        'business': business,
        'is_owner': True,
    }
    return render(request, 'finder/adminPanel.html', context_dict)


#helper function for adminPanel
def end_offer(end_offer_id):
    offer = Offer.objects.get(id=end_offer_id)
    users_with_reservation = list(
        UserAccount.objects.filter(reservation=offer))
    for u in users_with_reservation:
        u.reservation = None
        u.save()
    offer.delete()


#helper function for adminPanel, deletes a business and ends all associated offers
def delete_business(business_id):
    business = Business.objects.get(id=business_id)
    offers = Offer.objects.filter(business=business)
    if len(offers) != 0:
        end_offer(offers[0].id)
    business.delete()


@login_required
@user_passes_test(isOwner)
def add_business(request):
    new_business_form = BusinessForm()

    if request.method == 'POST':
        new_business_form = BusinessForm(request.POST, request.FILES)

        if new_business_form.is_valid():
            business = new_business_form.save(commit=False)
            business.owner = OwnerAccount.objects.get(user=request.user)
            business.save()
            return redirect('finder:home')
        else:
            context_dict = {'new_business_form': new_business_form}
            return render(request, 'finder/addBusiness.html', context_dict)
    is_owner = OwnerAccount.objects.filter(user=request.user).exists()
    context_dict = {
        'new_business_form': new_business_form,
        'is_owner': is_owner
    }
    return render(request, 'finder/addBusiness.html', context_dict)


@login_required
def settings(request):
    if request.method == 'POST':
        password_form = SetPasswordForm(data=request.POST, user=request.user)
        email_form = Update_form(request.POST, instance=request.user)

        if password_form.is_valid() and email_form.is_valid():
            user = password_form.save()
            email_form.save()
            update_session_auth_hash(request, password_form.user)
            return redirect('finder:account')

    else:
        password_form = SetPasswordForm(user=request.user)
        email_form = Update_form(instance=request.user)

    #affects rendering of the side bar
    is_owner = OwnerAccount.objects.filter(user=request.user).exists()
    context_dict = {
        'password_form': password_form,
        'email_form': email_form,
        'is_owner': is_owner
    }
    return render(request, 'finder/settings.html', context_dict)


@login_required
def currentReservation(request):
    # Gives the template a reseravtion if the user has one.
    reservation = False
    cUser = UserAccount.objects.filter(user=request.user)[0]
    if cUser.reservation:
        reservation = cUser.reservation
    return render(request, 'finder/currentReservation.html',
                  {"reservation": reservation})


@login_required
def cancelOffer(request):
    # TODO : What if it's an owner account
    cancelled = False
    cUser = UserAccount.objects.filter(user=request.user)[0]
    if cUser.reservation:
        offer = Offer.objects.filter(business=cUser.reservation.business)[0]
        offer.portionAmount +=1
        offer.save()
        cUser.reservation = None
        cUser.save()
        cancelled = True
    return render(request, 'finder/currentReservation.html',
                  {'cancelled': cancelled})
