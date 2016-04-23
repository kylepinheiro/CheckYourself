from django.shortcuts import render
from django.utils import timezone
from .models import Item, User, Checkout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import re

from django.http import HttpResponse
# Create your views here.

def index(request):
    return render(request, 'checkout/index.html', {})

@login_required
def items(request):
    checkouts = {checkout.item.item_id: checkout for checkout in Checkout.objects.filter(checkin_date__isnull=True)}

    items = []
    for item in Item.objects.all().order_by('category'):
        checkout = checkouts.get(item.item_id)
        items.append((item, checkout))

    return render(request, 'checkout/listItems.html', {'items': items})


def checkin(request, checkout_id):
    checkout_object = Checkout.objects.get(pk=checkout_id)
    checkout_object.checkin_date = timezone.now()
    checkout_object.item.checked_out = False
    checkout_object.save()
    print("checkin")
    return HttpResponse(status=204)


def students(request):
    student_list = [student for student in User.objects.filter(user_type="STUDENT")]
    print(student for student in student_list)
    return render(request, 'checkout/listStudents.html', {'students': student_list})


def users(request):
    return HttpResponse("<html><b>This will be the users page")

def checkoutHistory(request):
  
    if (request.GET.get('mybtn')):
        checkouts = Checkout.objects.all().order_by('-checkout_date')
        return render(request, 'checkout/checkoutHistory.html', {'checkouts': checkouts})
    else :
        checkouts = Checkout.objects.all().order_by('checkout_date')
    
    return render(request, 'checkout/checkoutHistory.html',{'checkouts': checkouts})

# code from http://julienphalip.com/post/2825034077/adding-search-to-a-django-site-in-a-snap
def normalize_query(query_string, findterms=re.compile(r'"([^"]+)"|(\S+)').findall, normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in individual keywords, getting rid of unnecessary spaces
        and grouping quoted words together.
        Example:
        
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

# code from http://julienphalip.com/post/2825034077/adding-search-to-a-django-site-in-a-snap
def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    
    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query
  
# code partially from http://julienphalip.com/post/2825034077/adding-search-to-a-django-site-in-a-snap
def search_items(request):
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        
        entry_query = get_query(query_string, ['category', 'model_number', 'kit_number', 'description', 'serial_number'])
        
        entry_query_checkout = get_query(query_string, ['borrower__first_name', 'borrower__last_name', 'checkout_date'])
        
        found_entries = Item.objects.filter(entry_query)
        found_entries_checkout = Checkout.objects.filter(entry_query_checkout)
        
    all_results = []        
    checkouts = {checkout.item.item_id: checkout for checkout in Checkout.objects.filter(checkin_date__isnull=True)}
    items = {item.item_id: item for item in Item.objects.all()}
    resultsArray = list(found_entries)
    checkoutResultsArray = list(found_entries_checkout)
    
    for item in resultsArray:
        checkout = checkouts.get(item.item_id)
        all_results.append((item, checkout))
        
    for checkout in checkoutResultsArray:
        item = items.get(checkout.item_id)
        all_results.append((item, checkout))

    return render(request, 'search/search_items.html',
                          { 'query_string': query_string, 'found_entries': all_results },) 

# code partially from http://julienphalip.com/post/2825034077/adding-search-to-a-django-site-in-a-snap
def search_students(request):
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        
        entry_query = get_query(query_string, ['first_name', 'last_name', 'student_id', 'email'])
        
        found_entries = User.objects.filter(entry_query).filter(user_type="STUDENT")

    return render(request, 'search/search_students.html',
                          { 'query_string': query_string, 'students': found_entries },)    

def search_history(request):
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        
        entry_query = get_query(query_string, ['item__category', 'borrower__first_name', 'borrower__last_name', 'authorizer__first_name', 'authorizer__last_name', 'checkin_date', 'checkout_date', 'item__serial_number', 'item__description', 'item__model_number', 'item__kit_number'])
        
        found_entries = Checkout.objects.filter(entry_query)

    return render(request, 'search/search_history.html',
                          { 'query_string': query_string, 'found_entries': found_entries },)                           
