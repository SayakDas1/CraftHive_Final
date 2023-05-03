from django.contrib import admin
from .models import Product, Contact, Orders, OrderUpdate, User, Review

# Register your models here(To show model in admin!)
admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(Orders)
admin.site.register(OrderUpdate)
admin.site.register(User)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display=['id','user','product','rate','created_at']
    readonly_fields = ['created_at',]
