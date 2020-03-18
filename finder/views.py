from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.urls import reverse
from finder.models import Business, Offer
from finder.distance import calculate_distance
from finder.forms import UserForm, UserAccountForm, UserLoginForm

# Create your views here.

def about(request):
    return render(request, 'finder/about.html')


def contact(request):
    return render(request, 'finder/contact.html')

def home(request):
    close_businesses = []
    invalid = False
    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            businesses = Business.objects.all()

            for b in businesses:
                try:
                    if calculate_distance(b.address, query) < 10:
                        close_businesses.append(b)
                except:
                    invalid = True
                    close_businesses = []
                    break

    featured_offers = []
    offers = Offer.objects.all()
    for o in offers:
        if o.portionAmount > 50:
            featured_offers.append(o)
            print(featured_offers)
    return render(request, 'finder/home.html', {'business_list': close_businesses, 'invalid': invalid, 'featured_offers': featured_offers})
  
def signUp(request):
    registered = False

    if request.method == "POST":
        user_form = UserForm(request.POST)
        account_form = UserAccountForm(request.POST)

        print(user_form)
        print("_______________________")
        print(account_form)

        
        if user_form.is_valid():
            user = user_form.save()
            # Branching logic as to if we want to create an Owner
            # or a Mortal user.
            if request.POST.get("isOwner") == "True":
                print("User is owner")
                user.set_password(user.password)
                user.save()

                    
                owner = owner_form.save(commit=False)
                owner.user = user
                print()
            else:
                print("User is mortal")

                account = account_form.save(commit=False)
                account.user = user

                account.save()

                registered = True
            '''
            user.set_password(user.password)
            user.save()

            account = account_form.save(commit=False)
            account.user = user
            
            account.save()

            registered = True
            '''
        else:
            print(user_form.errors, account_form.errors)
    else:
        print("Ooops form invalid ??")
        user_form = UserForm()
        account_form = UserAccountForm()

    context_dict =  {'user_form':user_form, 'account_form':account_form, 'registered':registered}

    return render(request, 'finder/signUp.html', context_dict)

def user_login(request):

    if request.method == "POST":
        username = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        #print(user)
        # If user is an owner or a mortal - we have different 
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
    
def show_business(request, business_name_slug):
    
    context_dicts = {}
    
    try:
        business = Business.objects.get(slug = business_name_slug)
        
        
        context_dict['Business'] = business
        
    except Business.DoesNotExist:
        
        context_dict['Business'] = None
        
    return render(request, 'finder/find_food.html', context_dict)
    
    
def user_logout(request):
    logout(request)
    return redirect(reverse('finder:home'))


def support(request):
	return render(request, 'finder/support.html')
	
def myBusinesses(request):
	return render(request, 'finder/myBusinesses.html')
	
def account(request):
	return render(request, 'finder/account.html')


def adminPanel(request):		
	return render(request, 'finder/adminPanel.html')

def settings(request):
	return render(request, 'finder/settings.html')