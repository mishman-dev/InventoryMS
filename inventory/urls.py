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
    # path('issues/<int:pk>/', views.view_issue, name='view_issue'),
    # path('issues/<int:pk>/edit/', views.edit_issue, name='edit_issue'),

]
