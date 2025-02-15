from django.urls import path

from expenses.views import *

app_name = 'expenses'

urlpatterns = [
    path('', home,name="home"),
    path('page/<int:page>', home,name="home"),
    path('get/report/list-expenses-by-category/', list_expenses_by_category, name="list_expenses_by_category"),
    path('report/', report, name="report"),
    path('about/', about, name="about"),

    path('get-total-expenses/',get_total_expenses_ajax,name="get_total_expenses_ajax"),


    #gerenciamento de modais
    path('new/expense/', create_expense, name="create_expense"),
    path('handle/limit', handle_limit, name="handle_limit"),
    path('handle/payment', handle_payment, name="handle_payment"),
    path('handle/category', handle_category, name="handle_category"),
    path('delete/expense', delete_expense, name="delete_expense"),


    path('edit/expense',edit_expense,name="edit_expense"),
    path('delete/payment', delete_payment, name="delete_payment"),

    #report
    path('report/expenses-by-period', expenses_by_period,name="expenses_by_period"),
    path('report/expenses-by-period/<str:dates>', expenses_by_period,name="expenses_by_period"),

    
]