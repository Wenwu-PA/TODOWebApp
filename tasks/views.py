from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import RegistrationForm, TaskForm
from .models import Task, create_default_categories


def home(request):
    if request.user.is_authenticated:
        return redirect("task_list")
    return redirect("login")


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            create_default_categories(user)
            messages.success(request, "Регистрация прошла успешно.")
            return redirect("task_list")
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user).select_related("category")
    status = request.GET.get("status", "all")

    if status == "active":
        tasks = tasks.filter(completed=False)
    elif status == "done":
        tasks = tasks.filter(completed=True)

    return render(request, "tasks/task_list.html", {"tasks": tasks, "status": status})


@login_required
def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, "Задача создана.")
            return redirect("task_list")
    else:
        form = TaskForm(user=request.user)

    return render(request, "tasks/task_form.html", {"form": form, "title": "Новая задача"})


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    return render(request, "tasks/task_detail.html", {"task": task})


@login_required
def task_update(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Задача обновлена.")
            return redirect("task_detail", task_id=task.pk)
    else:
        form = TaskForm(instance=task, user=request.user)

    return render(request, "tasks/task_form.html", {"form": form, "task": task, "title": "Редактирование"})


@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)

    if request.method == "POST":
        task.delete()
        messages.success(request, "Задача удалена.")
        return redirect("task_list")

    return render(request, "tasks/task_confirm_delete.html", {"task": task})


@login_required
@require_POST
def task_toggle(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    task.completed = not task.completed
    task.save(update_fields=["completed"])
    messages.success(request, "Статус задачи изменён.")
    return redirect("task_list")
