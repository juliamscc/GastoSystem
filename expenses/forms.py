from django import forms
from django.core.exceptions import ValidationError

#from expenses.models import Category

#class SelectCategoryForm(forms.Form):
   # category = forms.ModelChoiceField(label="Categoria",queryset=Category.objects.all())

from expenses.models import Expense
from expenses.models import Limit
from expenses.models import Payment
from expenses.models import Category 

from django.core.exceptions import ValidationError

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category','payment','description','value','date']
        labels = {
            'category': 'Categoria',
            'payment': 'Pagamento'
        }
        #exclude = ['',...]

    # def clean_coach(self):
    #     data = self.cleaned_data['coach']
    #     if not (data):
    #         raise ValidationError("É obrigatório adicionar o treinador.")

    #     return data
    
class LimitForm(forms.ModelForm):
    class Meta:
        model = Limit
        fields = ['year','month','value']
        labels = {
            'year': 'Ano',
            'value': 'Valor'
        }

class PaymentForm(forms.ModelForm): 
    #formulário da classe payment
    class Meta:
        model = Payment
        fields = '__all__'