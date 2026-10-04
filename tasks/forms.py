from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Category, Task


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Логин"
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Подтверждение пароля"


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("title", "description", "category", "due_date", "completed")
        labels = {
            "title": "Название",
            "description": "Описание",
            "category": "Категория",
            "due_date": "Срок",
            "completed": "Выполнено",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["category"].queryset = Category.objects.filter(user=user)
        else:
            self.fields["category"].queryset = Category.objects.none()

    def clean_title(self):
        title = self.cleaned_data.get("title", "")
        if title is not None:
            title = title.strip()
        if not title:
            raise forms.ValidationError("Название не может быть пустым.")
        return title
