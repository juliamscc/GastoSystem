from calendar import month
from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import JsonResponse
from expenses.forms import ExpenseForm, LimitForm, PaymentForm, CategoryForm
from django.template.loader import render_to_string

from django.views.decorators.csrf import csrf_exempt

from expenses.forms import CategoryForm
from expenses.models import *

from datetime import datetime
from django.db.models import Sum, Max, Min
import math 
NUMBER_ITENS = 6

def get_month_by_number(month):
  dict_month = {
    1: "janeiro",
    2: "fevereiro",
    3: "março",
    4: "abril",
    5: "maio",
    6: "junho",
    7: "julho",
    8: "agosto",
    9: "setembro",
    10: "outubro",
    11: "novembro",
    12: "dezembro",
  }
  return dict_month[month]


def return_list_of_months_and_years_formated():
      today = datetime.now()
      expense_first = Expense.objects.all().order_by('date').first()
      list_month_year_select = build_list_month_year(expense_first.date,today)

      return list_month_year_select


def build_list_month_year(start_date, end_date):
  diff_month = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
  diff_month += 1
  month_init = start_date.month
  year_init = start_date.year
  list_month_year = []
  for i in range(diff_month):
    if(month_init>12):
      month_init = 1
      year_init += 1
    list_month_year.append(
      {
        'month':get_month_by_number(month_init),
        'year':year_init,
        'month_number':month_init,
      }
    )
    month_init += 1
  list_month_year.reverse()
  return list_month_year

def home(request,page=None):
  global NUMBER_ITENS
  today = datetime.now()
  current_month = today.month
  current_year = today.year
  expense_first = Expense.objects.all().order_by('date').first()
  list_month_year_select = build_list_month_year(expense_first.date,today)
  count_expenses = Expense.objects.all().count()
  current_page = 1
  if page or page==0:
    current_page = page
  elif request.session.get('session_page', False):
    current_page = request.session.get('session_page')

  num_pages = math.ceil(count_expenses/NUMBER_ITENS)
  if(current_page>num_pages):
    return redirect(reverse('expenses:home', kwargs={'page': num_pages}))
  if (current_page<1):
    return redirect(reverse('expenses:home', kwargs={'page': 1}))
  request.session['session_page'] = current_page

  

  list_item_expenses = []
  if (num_pages == current_page) and Expense.objects.all().exists():
    list_item_expenses = Expense.objects.all()[NUMBER_ITENS*(current_page-1):]
  elif Expense.objects.all().exists():
    list_item_expenses = Expense.objects.all()[NUMBER_ITENS*(current_page-1):NUMBER_ITENS*current_page-1]

  # if(count_expenses>=NUMBER_ITENS):
  #   list_item_expenses = Expense.objects.all()[:NUMBER_ITENS]
  # else:
  #   list_item_expenses = Expense.objects.all()
  
  
  # para ja vir com a porcentagem de limite utilizado definida no primeiro load da tela
  first_date_in_list_of_dates = return_list_of_months_and_years_formated()[0]
  _month = first_date_in_list_of_dates['month_number']
  _year = first_date_in_list_of_dates['year']

  total = Expense.objects.filter(date__month=_month,date__year=_year).aggregate(total=Sum('value'))
  limit = None
  if Limit.objects.filter(month=_month,year=_year).exists():
    limit = Limit.objects.get(month=_month,year=_year).value
  total_expenses = total['total']
  percent = int(100*total_expenses/limit) if limit is not None and total_expenses is not None else '??'
  
  total_current_month = total
    
  context = {
     'page_selected': "home",
     'total_current_month': total_current_month['total'],
     'current_month_number': current_month,
     'current_month': get_month_by_number(current_month),
     'current_year': current_year,
     'list_month_year_select': list_month_year_select,
     'list_item_expenses': list_item_expenses,
     'num_pages': num_pages,
     'current_page': current_page,
     'percent': percent
  }
  return render(request,"expenses/main.html", context)
  # return render(request,"base.html", context={})

def about(request):
  context = {
     'page_selected': "about",
  }
  return render(request,"expenses/about.html", context)

def report(request):
  context = {
     'page_selected': "report",
  }
  return render(request,"expenses/report.html", context)

def expenses_by_period(request, dates= None):
  list_month_year_select = return_list_of_months_and_years_formated()
  start_month = list_month_year_select[0]['month_number']
  start_year = list_month_year_select[0]['year']
  end_month = list_month_year_select[0]['month_number']
  end_year = list_month_year_select[0]['year']
  expenses = []
  selected_start_date = None
  selected_end_date = None

  if dates is not None:
    _dates = dates.split('-')
    start_month = _dates[0]
    start_year = _dates[1]
    end_month = _dates[2]
    end_year = _dates[3]
    
    selected_start_date = f'{_dates[0]}-{_dates[1]}'
    selected_end_date = f'{_dates[2]}-{_dates[3]}'

    expenses = Expense.objects.filter(date__gte=f'{start_year}-{start_month}-01')

    expenses = expenses.filter(date__lte=f'{end_year}-{end_month}-28')
  else :
    expenses = Expense.objects.filter(date__gte=f'{start_year}-{start_month}-01')

    expenses = expenses.filter(date__lte=f'{end_year}-{end_month}-28')

  context = {
    'page_selected': "report",
    'list_month_year_select': list_month_year_select,
    'expenses': expenses,
    'selected_start_date': selected_start_date,
    'selected_end_date': selected_end_date
  }
  
  return render(request, "expenses/reports/expenses-by-period.html", context)

@csrf_exempt
def list_expenses_by_category(request):
  if request.method == 'POST':
    form = SelectCategoryForm(request.POST)
    if form.is_valid():
      category = form.cleaned_data['category']
      list = Expense.list_expenses_by_category(category)
      context = {
        'form': form,
        'category_selected': category,
        'list':list
      }
      return render(request,'expenses/list-expenses-by-category.html',context)
  form = SelectCategoryForm()
  context = {
    'form': form,
  }
  return render(request,'expenses/list-expenses-by-category.html',context)

@csrf_exempt
def get_total_expenses_ajax(request):
  if (request.method == 'GET'):
    values = request.GET['value'].split('-')
    month_selected = values[0]
    year_selected = values[1]
    total = Expense.objects.filter(date__month=int(month_selected),date__year=int(year_selected)).aggregate(total=Sum('value'))
    total_expenses = total['total']
    percent = '??'
    if Limit.objects.filter(month=month_selected,year=year_selected).exists() and total_expenses is not None:
      limit = Limit.objects.get(month=month_selected,year=year_selected).value
      percent = int(100*total_expenses/limit)
    
    response = {
      'data':total_expenses,
      'percent':f'{percent} %'
    }
    return JsonResponse(response, status = 200)

@csrf_exempt
def create_expense(request):
  title = 'Inserir Gasto'
  context_extra = {}
  if request.POST.get('action') == 'post':
    form = ExpenseForm(request.POST)
    
    if form.is_valid():
      model = form.save(commit=False)
      model.save()
      context_extra = {
          'response' : 'Criado com sucesso!',
          'error': False,
      }
    else:
      context_extra = {
          'response' : 'Erros ocorreram!',
          'error': True
      }
   
  else:
        form = ExpenseForm()
  context = {
    'form': form,
  }
  html_page = render_to_string('expenses/form/new-expense.html', context)
  response = {
    'title' : title,
    'html' : html_page,
    'response' : context_extra['response'] if 'response' in context_extra else None,
    'error': context_extra['error'] if 'error' in context_extra else None,
  }
  return JsonResponse(response, status = 200)

@csrf_exempt
def handle_category(request):
  title = 'Inserir Categoria'
  context_extra = {}
  lista_category = Category.objects.all()

  if request.POST.get('action') == 'post':
    form = CategoryForm(request.POST)
    
    if form.is_valid():
      model = form.save(commit=False)
      model.save()
      context_extra = {
          'response' : 'Criado com sucesso!',
          'error': False,
      }
    else:
      context_extra = {
          'response' : 'Erros ocorreram!',
          'error': True
      }
   
  else:
        form = CategoryForm()
  context = {
    'form': form,
    'lista_category':  lista_category
  }

  html_page = render_to_string('expenses/form/new-category.html', context)
  response = {
    'title' : title,
    'html' : html_page,
    'response' : context_extra['response'] if 'response' in context_extra else None,
    'error': context_extra['error'] if 'error' in context_extra else None,
  }

  return JsonResponse(response, status = 200)

@csrf_exempt
def handle_limit(request):
  title = 'Inserir Limite'
  context_extra = {}
    
  if request.POST.get('action') == 'post':
    form = LimitForm(request.POST)
    
    if form.is_valid():
      model = form.save(commit=False)
      model.save()
      context_extra = {
          'response' : 'Criado com sucesso!',
          'error': False,
      }
    else:
      context_extra = {
          'response' : 'Erros ocorreram!',
          'error': True
      }   
  else: 
    exists = False
    year = request.GET['year']
    month = request.GET['month']

    _limit = Limit(month=month, year=year)

    # verificando se já existe limite para esse mês e ano para mandar os campos já preenchidos
    exists = Limit.objects.filter(month=month, year=year).exists()
    if exists:
      _limit = Limit.objects.get(month=month, year=year)

    form = LimitForm(instance=_limit)

  context = {
    'form': form,
  }
  html_page = render_to_string('expenses/form/handle-limit.html', context)
  
  response = {
    'title' : title,
    'html' : html_page,
    'response' : context_extra['response'] if 'response' in context_extra else None,
    'error': context_extra['error'] if 'error' in context_extra else None,
  }
  return JsonResponse(response, status = 200)

@csrf_exempt
def handle_payment(request):
  title = 'Inserir Forma de Pagamento'
  context_extra = {}
  response = {}

  list_item_payment = Payment.objects.all()
  try:
    if request.POST.get('action') == 'post':
      form = PaymentForm(request.POST)
      
      if form.is_valid():
        model = form.save(commit=False)
        model.save()
        context_extra = {
            'response' : 'Criado com sucesso!',
            'error': False,
        }
      else:
        context_extra = {
            'response' : 'Erros ocorreram!',
            'error': True
        }

    else:
          form = PaymentForm()
    context = {
      'form': form,
      'list_item_payment': list_item_payment,
    }
    html_page = render_to_string('expenses/form/new-payment.html', context)
    response = {
      'title' : title,
      'html' : html_page,
      'response' : context_extra['response'] if 'response' in context_extra else None,
      'error': context_extra['error'] if 'error' in context_extra else None,
    }
  except Exception as e:
    print(e)
  return JsonResponse(response, status = 200)

def edit_expense(request):
  title = 'Alterar Gasto'
  expense = Expense.objects.get(id=request.GET['id'])
  context = {
    'expense': expense,
  }
  html_page = render_to_string('expenses/form/edit-expense.html', context)
  response = {
    'title' : title,
    'html' : html_page,
    
  }
  return JsonResponse(response, status = 200)

def delete_payment(request):
  title = 'Deseja realmente deletar esta forma de pagamento?'
  context_extra = {}
  context = {
    'id': request.GET.get('id')
  }
  if request.GET.get('action') == 'delete':
    id = request.GET.get('id')

    Expense.objects.filter(id=id).delete()
    context_extra = {
          'response' : 'Deletado com sucesso!',
          'error': False,
    }

  html_page = render_to_string('expenses/form/delete-payment.html', context)
  response = {
    'title' : title,
    'html' : html_page,
    'response' : context_extra['response'] if 'response' in context_extra else None,
    'error': context_extra['error'] if 'error' in context_extra else None,
  }

  return JsonResponse(response, status = 200)

def delete_expense(request):
  title = 'Deseja relamente deletar o gasto?'
  context_extra = {}
  context = {
    'id': request.GET.get('id')
  }
  if request.GET.get('action') == 'delete':
     id = request.GET.get('id')

     Expense.objects.filter(id=id).delete()
     context_extra = {
          'response' : 'Deletado com sucesso!',
          'error': False,
     }

  html_page = render_to_string('expenses/form/delete-expense.html', context)
  response = {
    'title' : title,
    'html' : html_page,
    'response' : context_extra['response'] if 'response' in context_extra else None,
    'error': context_extra['error'] if 'error' in context_extra else None,
  }

  return JsonResponse(response, status = 200)
