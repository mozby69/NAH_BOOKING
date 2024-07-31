from django.shortcuts import render,redirect
from django.http import JsonResponse
from myapp.models import Event_booking
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.csrf import csrf_exempt
from myapp.forms import EventForm
import logging
from django.utils.dateparse import parse_datetime
from django.contrib import messages
from django.contrib.messages import get_messages
from django.http import HttpResponseRedirect, HttpResponse
from datetime import timedelta,datetime,date,time
from django.db.models import Count
from django.utils import timezone
from dateutil.parser import parse





def booking_reports(request):
    today = date.today()
    bookings = Event_booking.objects.filter(
      date_start__lte=today,  # Start date is less than or equal to today
      date_end__gte=today,  # End date is greater than or equal to today
    ).order_by('start_time')

    current_month_display = datetime.now().strftime("%B")
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Count bookings per category for the current month
    bookings_current_month = Event_booking.objects.filter(date_start__year=current_year, date_start__month=current_month).values('category').annotate(total=Count('id'))

    colors = []
    category_colors = {
        'function_hall': 'green',
        'pavilion': 'red',
        'hostel': 'purple',
        'basketball_court': '#F7850B',
        'cabana': '#CCA103',
        'camp_site': 'brown',
        'big_pool': '#406F70',
        'kidney_pool': 'blue'
    }

    # Prepare data for the current month chart
    chart_data_current_month = [['Category', 'Bookings']]
    total_bookings = 0

    for booking in bookings_current_month:
        category = booking['category']
        chart_data_current_month.append([category, booking['total']])
        colors.append(category_colors.get(category, 'grey'))
        total_bookings += booking['total']

    # Count bookings per category for each month of the current year
    bookings_per_month = Event_booking.objects.filter(date_start__year=current_year).values('category', 'date_start__month').annotate(total=Count('id'))

    # Prepare data for the monthly chart
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    categories = ['function_hall', 'pavilion', 'hostel', 'basketball_court', 'cabana', 'camp_site', 'big_pool', 'kidney_pool']
    monthly_data = {month: {category: 0 for category in categories} for month in months}

    for booking in bookings_per_month:
        month_index = booking['date_start__month'] - 1
        month = months[month_index]
        category = booking['category']
        if category in monthly_data[month]:
            monthly_data[month][category] = booking['total']

    # Prepare chart data for the stacked column chart with total annotations
    chart_data_monthly = [['Month'] + categories + [{ 'role': 'annotation' }]]
    for month in months:
        monthly_totals = [monthly_data[month][category] for category in categories]
        total = sum(monthly_totals)
        row = [month] + monthly_totals + [str(total)]
        chart_data_monthly.append(row)

    return render(request, "nah_template/nah_reports.html", {
        'chart_data_current_month': chart_data_current_month,
        'total_bookings': total_bookings,
        'colors': colors,
        'chart_data_monthly': chart_data_monthly,
        'current_month_display':current_month_display,
        'bookings':bookings
    })


def notify_booking(request):
    messages = get_messages(request)
    filtered_messages = [
        {'text': message.message, 'tags': message.tags} for message in messages if 'edit_booking' in message.tags
        or 'added_booking' in message.tags or 'delete_booking' in message.tags or 'drag_update' in message.tags
    ]
    return JsonResponse({'messages': filtered_messages})



def drag_update(request):
    date_start_str = request.GET.get("date_start", None)
    date_end_str = request.GET.get("date_end", None)
    #name = request.GET.get("name", None)
    id = request.GET.get("id", None)
    
    if date_start_str:
        date_start = parse_datetime(date_start_str)
    else:
        date_start = None

    if date_end_str:
        date_end = parse_datetime(date_end_str)
    else:
        date_end = None

    event = Event_booking.objects.get(id=id)
    event.date_start = date_start
    event.date_end = date_end
    # event.name = name
    event.save()
    messages.success(request, f'{event.name}', extra_tags='drag_update')
    data = {}
    return JsonResponse(data)


# weekly
def get_week_dates(date):
    start = date - timedelta(days=date.weekday())  # Monday
    end = start + timedelta(days=6)  # Sunday
    return start, end

def group_events_by_day(events):
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    grouped_events = {day: [] for day in days_of_week}
    
    for event in events:
        event_day = event.date_start.strftime('%A')  # Get the day of the week
        if event_day in grouped_events:
            grouped_events[event_day].append(event)
    
    return grouped_events

def pspmi_monthly_page(request):
    week_start_str = request.GET.get('week_start')
    week_end_str = request.GET.get('week_end')
    category = request.GET.get('category')

    if week_start_str and week_end_str:
        week_start = datetime.strptime(week_start_str, "%B %d, %Y").date()
        week_end = datetime.strptime(week_end_str, "%B %d, %Y").date()
    else:
        today = timezone.now().date()
        week_start, week_end = get_week_dates(today)

    events = Event_booking.objects.filter(date_start__gte=week_start, date_end__lte=week_end)
    if category:
        events = events.filter(category=category)
        
    grouped_events = group_events_by_day(events)

    context = {
        "grouped_events": grouped_events,
        "week_start": week_start,
        "week_end": week_end,
        "selected_category": category,
    }
    return render(request, "nah_template/pspmi_weekly.html", context)




def pspmi_yearly_page(request):
    return render(request, "nah_template/pspmi_yearly.html")

def pspmi_view_page(request):
    return render(request, "nah_template/pspmi_view.html")


def pspmi_main_page(request):
    all_events = Event_booking.objects.all()
    context = {
        "events":all_events,
    }
    return render(request, "nah_template/pspmi_booking.html", context)

@csrf_exempt
def save_event(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            event_name = data.get('name')
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            date_start = data.get('date_start')
            date_end = data.get('date_end')
            categories = data.get('categories')  # This is a list of categories
            contactnumber = data.get('contactnumber')
            numberofpersons = data.get('numberofpersons')
            reservationdate = data.get('reservationdate', None) 
            
            if not categories:
                return JsonResponse({'status': 'fail', 'message': 'No categories selected'})
            
            created_event_ids = []
            for category in categories:
                event = Event_booking(
                    name=event_name,
                    start_time=start_time,
                    end_time=end_time,
                    date_start=date_start,
                    date_end=date_end,
                    category=category,
                    contactnumber=contactnumber,
                    numberofpersons=numberofpersons,
                    reservationdate=reservationdate,
                )
                messages.success(request, f'{event.name}', extra_tags='added_booking')
                event.save()
                created_event_ids.append(event.id)

            return JsonResponse({'status': 'success', 'event_ids': created_event_ids})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'fail', 'message': 'Invalid data format'})
    return JsonResponse({'status': 'fail'})     



def get_events(request):
    events = Event_booking.objects.all()
    events_list = []
    for event in events:
        events_list.append({
            'id': event.id,
            'name': event.name,
            'start_time': event.start_time,
            'end_time': event.end_time,
            'date_start': event.date_start,
            'date_end': event.date_end,
            'category': event.category,
            'contactnumber':event.contactnumber,
            'numberofpersons': event.numberofpersons,
            'reservationdate': event.reservationdate,
        })
    return JsonResponse(events_list, safe=False)


 


logger = logging.getLogger(__name__)

def update_event(request):
    if request.method == 'POST':
        event_id = request.POST.get('id')
        if not event_id:
            return JsonResponse({'status': 'fail', 'message': 'Event ID not provided'})

        try:
            event = Event_booking.objects.get(id=event_id)
            event.name = request.POST.get('name')
            event.start_time = request.POST.get('start_time')
            event.end_time = request.POST.get('end_time')
            event.date_start = request.POST.get('date_start')
            event.date_end = request.POST.get('date_end')
            event.category = request.POST.get('category')
            event.contactnumber = request.POST.get('contactnumber')
            event.numberofpersons = request.POST.get('numberofpersons')
            reservationdate = request.POST.get('reservationdate')
            event.reservationdate = reservationdate if reservationdate else None
    

            messages.success(request, f'{event.name}', extra_tags='edit_booking')
            event.save()
            return JsonResponse({'status': 'success'})
        except Event_booking.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Event not found'})
    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'})



def get_event_details(request):
    event_id = request.GET.get('event_id')
    if event_id:
        try:
            event = Event_booking.objects.get(id=event_id)
            event_details = {
                'id': event.id,
                'name': event.name,
                'start_time': event.start_time,
                'end_time': event.end_time,
                'date_start': event.date_start,
                'date_end': event.date_end,
                'category': event.category,
                'contactnumber': event.contactnumber,
                'numberofpersons': event.numberofpersons,
                'reservationdate': event.reservationdate,
            }
            return JsonResponse(event_details)
        except Event_booking.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)
    else:
        return JsonResponse({'error': 'Event ID not provided'}, status=400)
    


def delete_event(request):
    if request.method == 'POST':
        event_id = request.POST.get('id')
        try:
            event = Event_booking.objects.get(id=event_id)
            event.delete()
            messages.success(request, f'{event.name}', extra_tags='delete_booking')
            return JsonResponse({'status': 'success'})
        except Event_booking.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Event not found'})
    return JsonResponse({'status': 'fail', 'message': 'Invalid request method'})



def pspmi_print_page(request):
    current_month_display = datetime.now().strftime("%B")
    week_start_str = request.GET.get('week_start')
    week_end_str = request.GET.get('week_end')
    category = request.GET.get('category')

    if week_start_str and week_end_str:
        week_start = datetime.strptime(week_start_str, "%B %d, %Y").date()
        week_end = datetime.strptime(week_end_str, "%B %d, %Y").date()
    else:
        today = timezone.now().date()
        week_start, week_end = get_week_dates(today)
    
    events = Event_booking.objects.filter(date_start__gte=week_start, date_end__lte=week_end)
    if category:
        events = events.filter(category=category)
        
    grouped_events = group_events_by_day(events)
    
    context = {
        "grouped_events": grouped_events,
        "week_start": week_start,
        "week_end": week_end,
        'current_month_display': current_month_display,
        "week_start_display": week_start.strftime("%B %d, %Y"),
        "week_end_display": week_end.strftime("%B %d, %Y"),
        "selected_category": category,
    }
    return render(request, "nah_template/print_weekly.html", context)



