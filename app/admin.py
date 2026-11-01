from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import *

class CourseAdmin(ImportExportModelAdmin):
    list_display = [
        'id',
        'title',
        'product',
        'category',
        'price',
        'discount',
        'disk_space'
    ]

class CategoriesAdmin(ImportExportModelAdmin):
    pass

class ProductAdmin(ImportExportModelAdmin):
    pass

class UserCourseAdmin(ImportExportModelAdmin):
    pass

class PaymentAdmin(ImportExportModelAdmin):
    pass

admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(UserCourse, UserCourseAdmin)
admin.site.register(Payment, PaymentAdmin)