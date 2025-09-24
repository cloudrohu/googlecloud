from django.urls import path,include
from app import views,user_login
from django.conf import settings
from django.conf.urls.static import static
from app.views import MyLogoutView



urlpatterns = [    
    path('', views.HOME, name='home'),
    path('base', views.BASE, name='base'),
    path('about', views.ABOUT_US,name='about'),
    path('contact', views.CONTCAT,name='contact'),
    path('404', views.PAGE_NOTFOUND,name='404'),

    
    path('coureses', views.SINGLE_COURS,name='coureses'),
    path('courese/filter-data',views.filter_data,name="filter-data"),
    path('search',views.SEARCH_COURSE,name='search_course'),    
    path('course/<slug:slug>',views.COURSE_DETAILS,name='course_details'),

    path('checkout/<slug:slug>', views.CHECKOUT, name='checkout'),
    path('my_course', views.MY_COURSE, name='my_course'),
    path('course/watch_course/<slug:slug>', views.WATCH_COURSE, name='watch_course'),
    path('order_received', views.order_received, name='order_received'),



    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register', user_login.REGISTER,name='register'),
    path('do_login', user_login.DO_LOGIN,name='do_login'),
    path('accounts/logout/', MyLogoutView.as_view(), name='logout'),
    
    path('accounts/profile', user_login.PROFILE,name='profile'),
    path('accounts/profile_update', user_login.Profile_Update,name='profile_update'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path("save-purchase/", views.save_purchase, name="save_purchase"),
    path("thank-you/<int:purchase_id>/", views.thank_you, name="thank_you"),
    path("dashboard/", views.user_dashboard, name="dashboard"),
    path("purchases/", views.purchase_list, name="purchases"),
    path("profile/", views.user_profile, name="profile"),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)