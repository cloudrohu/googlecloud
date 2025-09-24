from multiprocessing import context
from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from time import time
from django.contrib.auth.views import LogoutView
from django.urls import path
from product.models import *
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect



class MyLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    
# Create your views here.
def BASE(request):
    return render(request,'base.html', )


def order_received(request):
    return render(request,'Main/order_received.html', )

def HOME(request):
    cotegory = Categories.objects.all().order_by('id')[:7]
    product = Product.objects.filter(status='PUBLISH').order_by('id')[:50]
    regions = Region.objects.all()

    context = {
        'cotegory': cotegory,
        'product': product,
        'regions': regions,
    }
    return render(request, 'Main/home.html', context)


def ABOUT_US(request):    
    cotegory = Categories.objects.all().order_by('id')[0:5]

    context = {
        'cotegory' : cotegory,
    }
    return render(request,'Main/about_us.html',context)

def CONTCAT(request):
    cotegory = Categories.objects.all().order_by('id')[0:5]

    context = {
        'cotegory' : cotegory,
    }
    return render(request,'Main/contact_us.html',context)

#-------------------------------------------------------------------------------------------------------------
def SINGLE_COURS(request):
    cotegory = Categories.objects.all().order_by('id')[0:5]
    course = Course.objects.filter(status = 'PUBLISH').order_by('-id')
    FreeCourse_count = Course.objects.filter(price = 0).count()
    PaidCourse_count = Course.objects.filter(price__gte=1).count()
    related_products = Course.objects.filter(category=course.categories).exclude(id=id)[:4]
    


    context = {
        'cotegory' : cotegory,
        'course' : course,
        'FreeCourse_count': FreeCourse_count,
        'PaidCourse_count': PaidCourse_count,
        'related_products': related_products,
    }
    return render(request, 'Main/single_course.html',context)



#-----------------------------------------------------------------------------------------------------
def filter_data(request):
    categories = request.GET.getlist('category[]')
    level = request.GET.getlist('level[]')
    price = request.GET.getlist('price[]')
    


    if price == ['pricefree']:
       course = Course.objects.filter(price=0)

    elif price == ['pricepaid']:
       course = Course.objects.filter(price__gte=1)
       
    elif price == ['priceall']:
       course = Course.objects.all()


    elif categories:
       course = Course.objects.filter(category__id__in=categories).order_by('-id')

    elif level:
       course = Course.objects.filter(level__id__in = level).order_by('-id')

    else:
       course = Course.objects.all().order_by('-id')


    t = render_to_string('ajax/course.html', {'course': course})

    return JsonResponse({'data': t})

#-----------------------------------------------------------------------------------------
@login_required(login_url='/accounts/login/')

def COURSE_DETAILS(request,slug):
    cotegory = Categories.get_all_category(Categories)
    

    course_id = Course.objects.get(slug = slug)   

    try:
        enroll_status = UserCourse.objects.get(user=request.user, course=course_id)
    except UserCourse.DoesNotExist:
        enroll_status = None

    course = Course.objects.filter(slug = slug)
    if course.exists():
        course = course.first()
    else:
        return redirect('404')

    context = {
        'course':course,
        'cotegory':cotegory,
        'enroll_status':enroll_status
    }
    return render(request,'course/course_details.html', context)

#--------------------------------------------------------------------------------------------------

def SEARCH_COURSE(request):
    query = request.GET['query']
    course = Course.objects.filter(title__icontains = query)
    context = {
        'course':course,
    }
    return render(request,'search/search.html',context)



#----------------------------------------------------------------------------------------------------------
def PAGE_NOTFOUND(request):
    cotegory = Categories.objects.all()    
    context = {        
        'cotegory' : cotegory,       
        
    }
    return render(request, 'error/error404.html',context)


#-------------------------------------------------------------------------------------------------------------
def CHECKOUT(request,slug):
    cotegory = Categories.objects.all() 
    course = Course.objects.get(slug = slug)
    action = request.GET.get('action')
    
    if  course.price == 0:
        course = UserCourse(
            user = request.user,
            course = course,
        )
        course.save()
        messages.success(request,'Course are successfully Enrolles !')
        return redirect('my_course')
    
    elif action == 'create_payment':
        if request.method == "POST":
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            country = request.POST.get('country')
            address_1 = request.POST.get('address_1')
            address_2 = request.POST.get('address_2')
            city = request.POST.get('city')
            postcode = request.POST.get('postcode')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            order_comments = request.POST.get('order_comments')

            amount = course.price * 100
            currency = "INR"

            notes = {
                "Name": first_name,
                "last_name": last_name,
                "country": country,
                "address_1": address_1,
                "address_2": address_2,
                "city": city,
                "postcode": postcode,
                "phone": phone,
                "email": email,
                "order_comments": order_comments,

            }
            receipt = " BCS {int(time())}"
            order = client.order.create(
                {
                    'receipt': receipt,
                    'notes': notes,
                    'amount': amount,
                    'currency': currency,

                }
            )
            payment = Payment(
                course=course,
                use=request.user,
                order_id=order.get('id')
            )
            payment.save()



    context = {        
        'cotegory' : cotegory,  
        'course'  : course,    
        'order'  : order,    
        
    }
    return render(request, 'checkout/checkout.html',context)
#--------------------------------------------------------------------------------------------------------------------------
@login_required(login_url='/accounts/login/')
def MY_COURSE(request):
    cotegory = Categories.objects.all()
    course = UserCourse.objects.filter(user = request.user)
    
    
    context = {        
        'cotegory' : cotegory,
        'course' : course,       
        
    }
    return render(request, 'course/my_course.html',context)
    
#-------------------------------------------------------------------------------------------------------------------------------
@login_required(login_url='/accounts/login/')
def WATCH_COURSE(request,slug):
    course = Course.objects.filter(slug = slug)  
    lecture =  request.GET.get('lecture')
    
    
    video = Video.objects.get(id = lecture)
        

    if course.exists():
        course = course.first()
    else:
        return redirect('404')

    context = {       
        'course' : course,
        'video'  : video,
        
        }
        
    return render(request, 'course/watch-course.html',context)



@login_required(login_url='/accounts/login/')
def product_detail(request, slug):
    product = Product.objects.prefetch_related('prices').get(slug=slug)
    return render(request, 'product_detail.html', {'product': product})



@csrf_exempt
def save_purchase(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            product_id = data.get("product")
            region = data.get("region")
            duration = data.get("duration")
            final_price = data.get("final_price")
            utr_id = data.get("utr_id")

            product = get_object_or_404(Product, id=product_id)

            purchase = Purchase.objects.create(
                user=request.user if request.user.is_authenticated else None,
                product=product,
                region=region,
                duration=duration,
                final_price=final_price,
                utr_id=utr_id
            )

            return JsonResponse({
                "success": True,
                "message": "Purchase saved successfully",
                "redirect_url": f"/thank-you/{purchase.id}/"
            })

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


def thank_you(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    return render(request, "thank_you.html", {"purchase": purchase})


def thank_you(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    return render(request, "thank_you.html", {"purchase": purchase})


@login_required
def user_dashboard(request):
    purchases = Purchase.objects.filter(user=request.user)
    total_spent = sum(p.final_price for p in purchases)
    return render(request, "dashboard.html", {
        "purchases": purchases,
        "total_spent": total_spent,
    })

@login_required
def purchase_list(request):
    purchases = Purchase.objects.filter(user=request.user)
    return render(request, "purchases.html", {"purchases": purchases})

@login_required
def user_profile(request):
    purchases = Purchase.objects.filter(user=request.user)
    total_spent = sum(p.final_price for p in purchases)
    return render(request, "profile.html", {
        "user": request.user,
        "purchases": purchases,
        "total_spent": total_spent,
    })

@login_required
def expire_packages():
    purchases = Purchase.objects.filter(status="PAID", expiry_date__lt=date.today())
    for purchase in purchases:
        purchase.status = "EXPIRED"
        purchase.save()