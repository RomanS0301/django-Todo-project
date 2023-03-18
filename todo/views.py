from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from django.utils import timezone
from .forms import TodoForm
from .models import Todo
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'todo/home.html')


def signupuser(request):
    """
    Регистрация нового пользователя со страницы регистрации и добавление его в базу. Проверяется соответствие паролей и
    уникального имени пользователя. После регистрации на сайте, пользователь не может входить через админ панель

    """
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')  # переход на страницу пользователя

            except IntegrityError:
                return render(request, 'todo/signupuser.html',
                              {'form': UserCreationForm(), 'error': "Такое имя пользователя уже используется. "
                                                                    "Задайте новое имя пользователя."})

        else:
            return render(request, 'todo/signupuser.html', {'form': UserCreationForm(), 'error': "Пароли не совпадают"})


def loginuser(request):
    """
    Вход пользователя
    """
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        """ Проверка логина и пароля пользователя, если нет соответствия - возврат на страницу аутификации"""
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html', {'form': AuthenticationForm(), 'error': 'Введено неверное '
                                                                                                  'имя или пароль'})
        else:
            """При соответствии логина и пароля переход на страницу пользователя"""
            login(request, user)
            return redirect('currenttodo')


@login_required
def logoutuser(request):
    """
    Выход пользователя с личного кабинета
    """
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required
def currenttodo(request):
    """Страница пользователя"""
    todos = Todo.objects.filter(user=request.user,
                                datecompleted__isnull=True)  # при завершении задачи заметка пропадает
    return render(request, 'todo/currenttodo.html', {'todos': todos})


@login_required
def createtodo(request):
    """Создание задач в личном кабинете пользователя"""
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'form': TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'form': TodoForm(), 'error': 'Переданы неверные данные'})


@login_required
def viewtodo(request, todo_pk):
    """Получение информации о конкретной записи  автора, просмотр и изменение записей, """
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)  # Добавление формы для изменения записей
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form, 'error': "Неверая информация"})


@login_required
def complitetodo(request, todo_pk):
    """Отметка о выполнени задачи ставится тем пользователем, который её создал"""
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodo')


@login_required
def deletetodo(request, todo_pk):
    """Удаление записей созданных конкретным пользователем"""
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodo')


@login_required
def complitedtodo(request):
    """Страница пользователя"""
    todos = Todo.objects.filter(user=request.user,
                                datecompleted__isnull=False).order_by('-datecompleted')  # при завершении задачи заметка пропадает
    return render(request, 'todo/completedtodo.html', {'todos': todos})


