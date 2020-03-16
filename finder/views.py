from django.shortcuts import render
from finder.models import Business, Offer
from finder.distance import calculate_distance
from finder.forms import UserForm, UserAccountForm

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
        if user_form.is_valid() and account_form.is_valid():
            user = user_form.save()

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

def login(request):
    return render(request, 'finder/login.html')