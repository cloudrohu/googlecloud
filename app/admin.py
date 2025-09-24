from django.contrib import admin

from .models import *

# Register your models here.



class course_admin(admin.ModelAdmin):
    list_display = ['id', 'title','product','category','price','discount','disk_space']
    



admin.site.register(Categories)
admin.site.register(Product)
admin.site.register(Course,course_admin)

admin.site.register(UserCourse)
admin.site.register(Payment)