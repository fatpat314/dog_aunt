from django.shortcuts import redirect, render
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from django.http import HttpResponseRedirect
from .models import Event, Venue
from django.contrib.auth.models import User
from .forms import VenueForm, EventForm, EventFormAdmin
from django.contrib import messages

from django.core.paginator import Paginator

# Create your views here.

def delete_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue.delete()
    return redirect('list_venue')

def delete_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.user == event.manager:
        event.delete()
        messages.success(request, ("Event Deleted!"))
        return redirect('list_events')
    else:
        messages.success(request, ("You are not authorized to delete this event."))
        return redirect('list-events')

def update_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.user.is_superuser:
        form = EventFormAdmin(request.POST or None, instance=event)
    else:
        form = EventForm(request.POST or None, instance=event)

    if form.is_valid():
        form.save()
        return redirect('list_events')

    return render(request, 'events/update_event.html', {'event': event, 'form': form})

def add_event(request):
    submitted = False
    if request.method == "POST":
        if request.user.is_superuser:
            form = EventFormAdmin(request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/add_event?submitted=True')
        else:
            form = EventForm(request.POST)
            if form.is_valid():
                event = form.save(commit=False)
                event.manager = request.user
                event.save()
                return HttpResponseRedirect('/add_event?submitted=True')
    else:
        if request.user.is_superuser:
            form = EventFormAdmin
        else:
            form = EventForm
        form = EventForm
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'events/add_event.html', {'form': form, 'submitted': submitted})

def update_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    form = VenueForm(request.POST or None, instance=venue)
    if form.is_valid():
        form.save()
        return redirect('list_venue')

    return render(request, 'events/update_venue.html', {'venue': venue, 'form': form})

def search_venues(request):
    if request.method == "POST":
        searched = request.POST['searched']
        venues = Venue.objects.filter(name__contains=searched)
        return render(request, 'events/search_venues.html',{'searched': searched, 'venues': venues})
    else:
        return render(request, 'events/search_venues.html',{})

def show_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue_owner = User.objects.get(pk=venue.owner)
    return render(request, 'events/show_venue.html', {'venue': venue, 'venue_owner': venue_owner})


def list_venues(request):
    list_venue = Venue.objects.all().order_by('name')

    p = Paginator(Venue.objects.all(), 5)
    page = request.GET.get('page')
    venues = p.get_page(page)
    nums = "a" * venues.paginator.num_pages
    return render(request, 'events/venue.html', {'list_venue': list_venue, 'venues': venues, "nums": nums})

def add_venue(request):
    submitted = False
    if request.method == "POST":
        form =  VenueForm(request.POST)
        if form.is_valid():
            venue = form.save(commit=False)
            venue.owner = request.user.id
            venue.save()
            return HttpResponseRedirect('/add_venue?submitted=True')
    else:
        form = VenueForm
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'events/add_venue.html', {'form': form, 'submitted': submitted})

def all_events(request):
    event_list = Event.objects.all().order_by('event_date')
    return render(request, 'events/event_list.html', {'event_list': event_list})

def home(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
    name = request.user
    month = month.capitalize()
    # Convert month from name to number
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number) 

    # create a calendar
    cal = HTMLCalendar().formatmonth(year, month_number)

    # get current year
    now = datetime.now()
    current_year = now.year

    # get current time
    time = now.strftime('%I:%M %p') 

    return render(request, 
        'events/home.html', {
            "name": name,
            "year": year,
            "month": month,
            "month_number": month_number,
            "cal": cal,
            "current_year": current_year,
            "time": time,
            })
