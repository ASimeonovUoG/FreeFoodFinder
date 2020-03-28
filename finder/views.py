from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.urls import reverse
from finder.models import Business, Offer, OwnerAccount
from finder.distance import calculate_distance
from finder.forms import UserForm, UserAccountForm, UserLoginForm, BusinessForm
from django.contrib.auth.decorators import user_passes_test, login_required
from finder.decorators import isOwner

# Create your views here.

def about(request):
    return render(request, 'finder/about.html')


def contact(request):
    return render(request, 'finder/contact.html')

def home(request):
    distance_threshold = 10
    FEATURED_THRESHOLD = 50
    close_businesses = []
    invalid = False
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            businesses = Business.objects.all()

            for b in businesses:
                try:
                    if calculate_distance(b.lat, b.long, query) < distance_threshold:
                        close_businesses.append(b)
                except:
                    invalid = True
                    close_businesses = []
                    break
            if not invalid:
                return render(request, 'finder/find_food.html', {'invalid': invalid, 'businesses': close_businesses})

    featured_offers = []
    offers = Offer.objects.all()
    for o in offers:
        if o.portionAmount > FEATURED_THRESHOLD:
            featured_offers.append(o)
    return render(request, 'finder/home.html', {'invalid': invalid, 'featured_offers': featured_offers})


def find_food(request):
    distance_threshold = 10
    close_businesses = []
    invalid = False
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            businesses = Business.objects.all()

            for b in businesses:
                try:
                    if calculate_distance(b.lat, b.long, query) < distance_threshold:
                        close_businesses.append(b)
                except:
                    invalid = True
                    close_businesses = []
                    break
            if not invalid:
                return render(request, 'finder/find_food.html', {'invalid': invalid, 'businesses': close_businesses})

    # business_list = Business.objects.order_by('businessName')
    #
    # context_dict = {}
    # context_dict['businesses'] = business_list
    #
    return render(request, 'finder/find_food.html', {})


def show_business(request, business_name_slug):
    context_dict = {}

    try:
        business = Business.objects.get(slug=business_name_slug)

        context_dict['business'] = business

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
            print(user_form.errors, account_form.errors)
    else:
        user_form = UserForm()
        account_form = UserAccountForm()

    context_dict =  {'user_form':user_form, 'account_form':account_form, 'registered':registered}

    return render(request, 'finder/signUp.html', context_dict)

def user_login(request):

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
        context_dict =  {'login_form':login_form}
        return render(request, 'finder/user_login.html',context_dict)



def user_logout(request):
    logout(request)
    return redirect(reverse('finder:home'))

@login_required
def support(request):
	return render(request, 'finder/support.html')
	
@login_required
@user_passes_test(isOwner)
def myBusinesses(request):
    all_businesses = []
    businesses = Business.objects.values('businessName','description','picture')
    for b in businesses:
        all_businesses.append(b)
        
    return render(request, 'finder/myBusinesses.html', {'all_businesses':all_businesses})
	
@login_required
def account(request):
	return render(request, 'finder/account.html')

@login_required
@user_passes_test(isOwner)
def adminPanel(request):
    if request.method == 'POST':
        business_form = BusinessForm(request.POST)

        print(business_form)

        if business_form.is_valid():
            business = business_form.save()
            return redirect('finder:myBusinesses')

    else:
        business_form = BusinessForm()

    context_dict = {'business_form':business_form}
    return render(request, 'finder/adminPanel.html',context_dict)

@login_required
def settings(request):
    if request.method == 'POST':
        settings_form = UserForm(request.POST)

        print(settings_form)

        if settings_form.is_valid():
            user = settings_form.save()
            return redirect('finder:account')

    else:
        settings_form = UserForm()

    context_dict = {'settings_form':settings_form}
    return render(request, 'finder/settings.html',context_dict) 