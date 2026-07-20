from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Movie, MovieList
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
import re


@login_required(login_url='login')
def index(request):
    movies = Movie.objects.all()
    featured_movie = Movie.objects.filter(is_featured=True).first()
    if not featured_movie and movies:
        featured_movie = movies.first()

    genre_sections = []
    for slug, label in Movie.GENRE_CHOICES:
        genre_movies = movies.filter(genre=slug)
        if genre_movies.exists():
            genre_sections.append({
                'slug': slug,
                'label': label,
                'movies': genre_movies,
            })

    recently_added = movies.order_by('-release_date')[:20]

    context = {
        'movies': movies,
        'featured_movie': featured_movie,
        'genre_sections': genre_sections,
        'recently_added': recently_added,
    }
    return render(request, 'index.html', context)


@login_required(login_url='login')
def movie(request, pk):
    movie_details = Movie.objects.get(uu_id=pk)
    movie_details.movie_views += 1
    movie_details.save()

    context = {
        'movie_details': movie_details
    }

    return render(request, 'movie.html', context)


@login_required(login_url='login')
def genre(request, pk):
    movie_genre = pk
    movies_list = Movie.objects.filter(genre=movie_genre)

    paginator = Paginator(movies_list.order_by('title'), 12)
    page_number = request.GET.get('page')
    movies = paginator.get_page(page_number)

    context = {
        'movies': movies,
        'movie_genre': movie_genre,
        'is_paginated': movies.has_other_pages(),
        'page_obj': movies,
    }
    return render(request, 'genre.html', context)


@login_required(login_url='login')
def search(request):
    search_term = request.GET.get('q', '').strip()
    if not search_term:
        return render(request, 'search.html', {'movies': [], 'search_term': ''})

    movies_list = Movie.objects.filter(title__icontains=search_term)

    paginator = Paginator(movies_list.order_by('title'), 12)
    page_number = request.GET.get('page')
    movies = paginator.get_page(page_number)

    context = {
        'movies': movies,
        'search_term': search_term,
        'is_paginated': movies.has_other_pages(),
        'page_obj': movies,
    }
    return render(request, 'search.html', context)


@login_required(login_url='login')
def my_list(request):
    movie_list = MovieList.objects.filter(owner_user=request.user).select_related('movie')
    user_movie_list = [item.movie for item in movie_list]

    context = {
        'movies': user_movie_list
    }
    return render(request, 'my_list.html', context)


@login_required(login_url='login')
def add_to_list(request):
    if request.method == 'POST':
        movie_url_id = request.POST.get('movie_id')
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        match = re.search(uuid_pattern, movie_url_id)
        movie_id = match.group() if match else None

        movie = get_object_or_404(Movie, uu_id=movie_id)
        movie_list, created = MovieList.objects.get_or_create(owner_user=request.user, movie=movie)

        if created:
            response_data = {'status': 'success', 'message': 'Added ✓'}
        else:
            response_data = {'status': 'info', 'message': 'Movie already in list'}

        return JsonResponse(response_data)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('login')

    return render(request, 'login.html')


def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                return redirect('/')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
    else:
        return render(request, 'signup.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')
