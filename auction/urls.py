from django.urls import path
from . import views

urlpatterns = [
    path('', views.auction, name='auction'),
    path('auc_product/<int:myid>', views.auc_product, name='auc_product'),
    path('user/register/', views.register, name="register"),
    path('user/login/', views.login, name="login"),
    path('contact/', views.contact, name="contact"),
    path('winner',views.winner, name="winner"),
    path('product_upload', views.prod_upload, name='prod_upload'),
    path('payment/<int:id>/<str:email>',views.payment,name='pay'),
    path("order-status/<int:id>",views.orderStatus,name="orderStatus"),
    path("live/<int:id>",views.live,name="viewLive")
]