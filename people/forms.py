from django import forms
from django.core.exceptions import ValidationError
from .models import Star


class StarForm(forms.ModelForm):
    """Форма для добавления знаменитости"""

    class Meta:
        model = Star
        fields = ['name', 'country', 'categories', 'birth_date', 'death_date', 'content', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '3'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'death_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        birth_date = cleaned_data.get('birth_date')
        death_date = cleaned_data.get('death_date')

        if death_date and birth_date and death_date < birth_date:
            raise ValidationError("Дата смерти не может быть раньше даты рождения")
        return cleaned_data