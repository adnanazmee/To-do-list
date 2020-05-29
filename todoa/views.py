from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required


# Create your views here.
def home(request):
    return render(request,'todoa/home.html')

def about(request):
    return render(request,'todoa/about.html')


def signupuser(request):
    if request.method == 'GET':
        return render(request,'todoa/signupuser.html',{'form':UserCreationForm()})

    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password = request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request,'todoa/signupuser.html',{'form':UserCreationForm(),'error':'Username already taken,try another one'})

        else:
            return render(request,'todoa/signupuser.html',{'form':UserCreationForm(),'error':'Passwords did not match'})

            # tell password didn't match

def loginuser(request):
    if request.method == 'GET':
        return render(request,'todoa/loginuser.html',{'form':AuthenticationForm()})

    else:
        user = authenticate(request, username= request.POST['username'], password = request.POST['password'])
        if user is None:
            return render(request,'todoa/loginuser.html',{'form':AuthenticationForm(),'error':'Username or password did not match'})
        else:
            login(request, user)
            return redirect('currenttodos')



@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def createtodos(request):
    if request.method == 'GET':
        return render(request,'todoa/createtodos.html',{'form':TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request,'todoa/createtodos.html',{'form':TodoForm(), 'error':'Bad data passed. Try again.'})



@login_required
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user,datecompleted__isnull=True)

    return render(request,'todoa/currenttodos.html',{'todos':todos})

@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user,datecompleted__isnull=False).order_by('-datecompleted')

    return render(request,'todoa/completedtodos.html',{'todos':todos})

@login_required
def viewtodos(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request,'todoa/viewtodos.html',{'todo':todo, 'form':form})
    else:
        try:
            form = TodoForm(request.POST,instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request,'todoa/viewtodos.html',{'todo':todo, 'form':form, 'error':'Bad data passed. Try again.'})

@login_required
def completetodos(request,todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')

@login_required
def deletetodos(request,todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')
