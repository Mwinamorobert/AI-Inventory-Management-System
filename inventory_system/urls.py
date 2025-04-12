from django.contrib import admin
from django.urls import path
from core import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard_view, name='dashboard'),
    path('api/get_dashboard_data/', views.get_dashboard_data_api, name='get_dashboard_data'),
    path('api/add_item/', views.add_item_api, name='add_item'),
    path('locations/', views.locations_view, name='locations'),
    path('api/add_location/', views.add_location_api, name='add_location_api'),
    path('edit_location/<int:location_id>/', views.edit_location, name='edit_location'),
    path('delete_location/<int:location_id>/', views.delete_location, name='delete_location'),
    path('suppliers/', views.suppliers_view, name='suppliers'),
    path('api/add_supplier/', views.add_supplier_api, name='add_supplier_api'),
    path('edit_supplier/<int:supplier_id>/', views.edit_supplier, name='edit_supplier'),
    path('delete_supplier/<int:supplier_id>/', views.delete_supplier, name='delete_supplier'),
    path('insights/', views.insights_view, name='insights'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('api/delete_item/', views.delete_item_api, name='delete_item_api'),
    path('api/get_item/<int:id>/', views.get_item_api, name='get_item_api'),
    path('api/edit_item/', views.edit_item_api, name='edit_item_api'),
    path('export/', views.export_inventory, name='export_inventory'),
]