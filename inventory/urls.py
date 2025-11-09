from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('item_list/', views.item_tab, name='item_tab'),
    path('admin/', admin.site.urls),
    path('items/add/', views.add_item, name='add_item'),


    path('issues/', views.issue_list, name='issue_list'),
    path('issues/export/', views.export_issues_excel, name='export_issues_excel'),
    path('issues/create/', views.add_issue, name='add_issue'),
    path("categories/", views.category_list, name="category_list"),
    path("categories/delete/<int:pk>/", views.category_delete, name="category_delete"),
    path("categories/edit/<int:pk>/", views.category_edit, name="category_edit"),

    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('suppliers/edit/<int:supplier_id>/', views.edit_supplier, name='edit_supplier'),
    path('suppliers/delete/<int:supplier_id>/', views.delete_supplier, name='delete_supplier'),

    path('projects/', views.project_list, name='project_list'),
    path('projects/edit/<int:pk>/', views.project_edit, name='project_edit'),
    path('projects/delete/<int:pk>/', views.project_delete, name='project_delete'),


    path('purchases/', views.purchase_list, name='purchase_list'),
    path('purchases/add/', views.add_purchase, name='add_purchase'),
    path('get-item-price/', views.get_item_price, name='get_item_price'),

    path('employees/', views.employee_list, name='employee_list'),
    path('add-employee/', views.add_employee, name='add_employee'),





    # path('issues/<int:pk>/', views.view_issue, name='view_issue'),
    # path('issues/<int:pk>/edit/', views.edit_issue, name='edit_issue'),

]
