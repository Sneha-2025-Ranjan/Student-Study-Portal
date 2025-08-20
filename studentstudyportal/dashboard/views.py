from django.shortcuts import render,redirect
from django.contrib import messages
from . forms import *
from django.views import generic
from youtubesearchpython import VideosSearch
import requests
import wikipedia
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from wikipedia.exceptions import DisambiguationError, PageError

# Create your views here.

def home(request):
    return render(request, 'dashboard/home.html')

# Notes
@login_required
def notes(request):
    if request.method=="POST":
        form=NotesForm(request.POST)
        if form.is_valid():
            notes=Notes(user=request.user, title=request.POST['title'], description=request.POST['description'])
            notes.save()
        messages.success(request,f"Notes Added from {request.user.username} Successfully!")
    else:
        form = NotesForm()
    notes=Notes.objects.filter(user=request.user)
    context={'notes':notes, 'form':form}
    return render(request, 'dashboard/notes.html',context )

@login_required
def delete_notes(request, pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")

class NotesDetailView(generic.DetailView):
    model=Notes


# Homework
@login_required
def homework(request):
    if request.method=="POST":
        form=HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished=request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            homeworks= Homework(
                user=request.user,
                subject=request.POST['subject'],
                title=request.POST['title'],
                description=request.POST['description'],
                due=request.POST['due'],
                is_finished=finished
            )
            homeworks.save()
            messages.success(request, f'Homework Added from {request.user.username}!')
    else:
        form=HomeworkForm()
    homework=Homework.objects.filter(user=request.user)
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False
    context={
            'homeworks':homework,
            'homeworks_done':homework_done,
            'form':form,
    }
    return render(request, 'dashboard/homework.html',context)

@login_required
def update_homework(request, pk=None):
    homework=Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished=True
    homework.save()
    return redirect('homework')

@login_required
def delete_homework(request, pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")


#youtube
def youtube(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text, limit=10)
        result_list = []
        for i in video.result()['result']:
            result_dict ={
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnail':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'views':i['viewCount']['short'],
                'published':i['publishedTime']
            }
            desc = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc += j['text']
            result_dict['description'] = desc
            result_list.append(result_dict ) 
            context ={
                'form':form,
                'results':result_list
            }
        return render(request, 'dashboard/youtube.html', context)
    else:
        form = DashboardForm()
    form=DashboardForm()
    context={'form': form}
    return render(request, "dashboard/youtube.html", context)


#todo
@login_required
def todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST["is_finished"]
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todos = Todo(
                user = request.user,
                title = request.POST['title'],
                is_finished = finished 
            )
            todos.save()
            messages.success(request, f" Todo Added from {request.user.username}!!")
    else:
        form = TodoForm()
    todo = Todo.objects.filter(user = request.user)
    if len(todo)==0:
        todos_done = True
    else:
        todos_done = False
    context = {
        'form' :form,
        'todos' :todo,
        'todos_done' :todos_done
    }
    return render(request,"dashboard/todo.html", context)

@login_required
def update_todo(request, pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect('todo') 

@login_required
def delete_todo(request, pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect('todo')

# books
def books(request):
    if request.method == 'GET' and 'book_name' in request.GET:
        book_name = request.GET['book_name']
        results = search_books(book_name)
    else:
        results = []  

    context = {
        'results': results,
    }
    return render(request, 'dashboard/books.html', context)

def search_books(query):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=10"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])

        results = []
        for item in items:
            volume_info = item.get('volumeInfo', {})
            title = volume_info.get('title', 'Unknown Title')
            subtitle = volume_info.get('subtitle', '')
            description = volume_info.get('description', 'No description available.')
            thumbnail = volume_info.get('imageLinks', {}).get('thumbnail', '')
            categories = volume_info.get('categories', [])
            pageCount = volume_info.get('pageCount', '')
            averageRating = volume_info.get('averageRating', '')

            book_data = {
                'title': title,
                'subtitle': subtitle,
                'description': description,
                'thumbnail': thumbnail,
                'categories': categories,
                'pageCount': pageCount,
                'averageRating': averageRating,
                'preview': volume_info.get('previewLink', ''),
            }
            results.append(book_data)
        
        return results
    else:
        return [] 
    

# Dictionary
def dictionary(request):
    input_word = None
    phonetics = None
    definition = None
    example = None
    audio = None

    input_word = None
    word_data = None

    if request.method == 'POST':
        input_word = request.POST.get('word')
        if input_word:
            api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{input_word}"
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                if data:
                    word_data = data[0]

    context = {
        'input': input_word,
        'word_data': word_data,
    }
    return render(request, 'dashboard/dictionary.html', context)


# wikipedia
def wiki(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            try:
                search = wikipedia.page(text)
                context = {
                    'form':form,
                    'title': search.title,
                    'link': search.url,
                    'details':search.summary
                }
                return render(request, 'dashboard/wiki.html', context)
            except DisambiguationError as e:
                options = e.options[:10]  # Limiting to 10 options for simplicity
                context = {
                    'form': form,
                    'options': options,
                    'error_message': f"Disambiguation Error: Multiple results found for '{text}'."
                }
                return render(request, 'dashboard/disambiguation_error.html', context)
            except  wikipedia.exceptions.PageError:
                error_message = f"Page not found for '{text}'."
                context = {
                    'form': form,
                    'error_message': error_message
                }
                return render(request, 'dashboard/wiki.html', context)
    else:
        form = DashboardForm()
        context={
            'form': form
        }
    return render(request, 'dashboard/wiki.html', context)

# conversion
def conversion(request):
    if request.method == 'POST':
        form = ConversionForm(request.POST)
        if request.POST['measurement'] == 'length':
            measurement_form = ConversionLengthForm()
            context = {
                'form': form,
                'm_form': measurement_form,
                'input': True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input) >=0:
                    if first == 'yard' and second == 'foot':
                        answer = f'{input} yard = {int (input)*3} foot'
                    if first == 'foot' and second == 'yard':
                        answer = f'{input} foot = {int (input)/3} yard'
                context = {
                'form': form,
                'm_form': measurement_form,
                'input': True,
                'answer': answer
                }
        if request.POST['measurement'] == 'mass':
            measurement_form = ConversionMassForm()
            context = {
                'form': form,
                'm_form': measurement_form,
                'input': True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input) >=0:
                    if first == 'ponud' and second == 'kilogram':
                        answer = f'{input} pound = {int (input)*0.453592} kilogram'
                    if first == 'kilogram' and second == 'pound':
                        answer = f'{input} kilogram = {int (input)*2.20462} pound'
                context = {
                'form': form,
                'm_form': measurement_form,
                'input': True,
                'answer': answer
               }
    else:
        form = ConversionForm()
        context ={
            'form': form,
            'input': False
        } 
    return render(request, 'dashboard/conversion.html',context)

#register 
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created for {username}!!")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    context ={
        'form': form
        }
    return render(request, 'dashboard/register.html',context)

# profile
@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False,user=request.user)
    todos = Todo.objects.filter(is_finished=False,user=request.user)
    if len(homeworks)==0:
        homework_done = True
    else:
        homework_done = False
    if len(todos)==0:
        todos_done = True
    else:
        todos_done = False
    context = {
        'homeworks': homeworks,
        'todos': todos,
        'homework_done': homework_done,
        'todos_done': todos_done
    }
    return render(request, 'dashboard/profile.html', context)


