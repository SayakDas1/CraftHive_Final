from django.urls import path
from . import views

urlpatterns = [
    path("", views.index,name="ShopHome"),
    path("about/", views.about, name="AboutUs"),
    path('contact/', views.contact,name="ContactUs"),
    path('productreg/',views.productReg,name="ProductReg"),
    path("tracker/", views.tracker, name="TrackingStatus"),
    path("search/", views.search, name="Search"),
    path("products/<int:myid>", views.productView, name="ProductView"),
    path("checkout/", views.checkout, name="Checkout"),
    path("login",views.loginUser, name="login"),
    path("logout",views.logoutUser, name="logout"),
    path("register",views.register, name="register"),
    path("order-status/",views.orderStatus,name="orderStatus"),
    path("success/",views.success,name="success"),
    path("failure/",views.failure,name="failure"),
    path("seller",views.seller, name="seller"),
    path("category/<str:cat>",views.category, name="category"),
    path("review",views.review,name="review")
]