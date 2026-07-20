from django.contrib import admin
from .models import Movie, MovieList


class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'release_date', 'age_rating', 'movie_views', 'is_featured')
    list_filter = ('genre', 'age_rating', 'is_featured')
    search_fields = ('title', 'description')
    list_editable = ('is_featured',)
    ordering = ('-release_date',)


class MovieListAdmin(admin.ModelAdmin):
    list_display = ('owner_user', 'movie')
    list_filter = ('owner_user',)


admin.site.register(Movie, MovieAdmin)
admin.site.register(MovieList, MovieListAdmin)