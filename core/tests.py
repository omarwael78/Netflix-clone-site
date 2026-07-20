from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Movie, MovieList
from datetime import date
import uuid
import tempfile


def _create_movie(**kwargs):
    defaults = {
        'title': 'Test Movie',
        'description': 'A test movie',
        'release_date': date(2024, 1, 1),
        'genre': 'action',
        'length': 120,
        'age_rating': 'PG-13',
        'image_card': SimpleUploadedFile('card.png', b'fake-image-content', content_type='image/png'),
        'image_cover': SimpleUploadedFile('cover.png', b'fake-image-content', content_type='image/png'),
        'video': SimpleUploadedFile('movie.mp4', b'fake-video-content', content_type='video/mp4'),
    }
    defaults.update(kwargs)
    return Movie.objects.create(**defaults)


class MovieModelTest(TestCase):
    def setUp(self):
        self.movie = _create_movie(
            title='Test Movie',
            description='A test movie description',
            age_rating='PG-13',
            is_featured=True,
        )

    def test_movie_str(self):
        self.assertEqual(str(self.movie), 'Test Movie')

    def test_movie_defaults(self):
        self.assertFalse(self.movie.movie_views)
        self.assertEqual(self.movie.age_rating, 'PG-13')

    def test_movie_uuid_auto_generated(self):
        self.assertIsInstance(self.movie.uu_id, uuid.UUID)

    def test_movie_list_choices_contain_genres(self):
        genres = dict(Movie.GENRE_CHOICES)
        self.assertIn('action', genres)
        self.assertIn('comedy', genres)
        self.assertEqual(genres['science_fiction'], 'Science Fiction')


class MovieListModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.movie = _create_movie(
            title='List Movie',
            description='Desc',
            genre='drama',
            length=90,
        )

    def test_movie_list_creation(self):
        entry = MovieList.objects.create(owner_user=self.user, movie=self.movie)
        self.assertEqual(entry.owner_user, self.user)
        self.assertEqual(entry.movie, self.movie)

    def test_movie_list_get_or_create_prevents_duplicates(self):
        created1, _ = MovieList.objects.get_or_create(owner_user=self.user, movie=self.movie)
        created2, is_new = MovieList.objects.get_or_create(owner_user=self.user, movie=self.movie)
        self.assertTrue(created1)
        self.assertFalse(is_new)
        self.assertEqual(MovieList.objects.filter(owner_user=self.user, movie=self.movie).count(), 1)


class AuthViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.index_url = reverse('index')
        self.user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }

    def test_signup_page_loads(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')

    def test_login_page_loads(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_signup_creates_user_and_logs_in(self):
        response = self.client.post(self.signup_url, self.user_data, follow=True)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertRedirects(response, self.index_url)

    def test_signup_password_mismatch(self):
        data = {**self.user_data, 'password2': 'DifferentPass123!'}
        response = self.client.post(self.signup_url, data, follow=True)
        self.assertFalse(User.objects.filter(username='newuser').exists())
        self.assertContains(response, 'Password Not Matching')

    def test_signup_duplicate_username(self):
        User.objects.create_user(username='newuser', password='testpass123')
        response = self.client.post(self.signup_url, self.user_data, follow=True)
        self.assertContains(response, 'Username Taken')

    def test_signup_duplicate_email(self):
        User.objects.create_user(username='other', email='new@example.com', password='testpass123')
        response = self.client.post(self.signup_url, self.user_data, follow=True)
        self.assertContains(response, 'Email Taken')

    def test_login_valid_credentials(self):
        User.objects.create_user(username='validuser', password='CorrectPass1')
        response = self.client.post(self.login_url, {
            'username': 'validuser',
            'password': 'CorrectPass1',
        }, follow=True)
        self.assertRedirects(response, self.index_url)

    def test_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': 'nobody',
            'password': 'wrong',
        }, follow=True)
        self.assertContains(response, 'Credentials Invalid')

    def test_logout(self):
        User.objects.create_user(username='logoutuser', password='testpass123')
        self.client.login(username='logoutuser', password='testpass123')
        response = self.client.get(reverse('logout'), follow=True)
        self.assertRedirects(response, self.login_url)

    def test_index_redirects_when_not_logged_in(self):
        response = self.client.get(self.index_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.index_url}')


class MovieViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='movieuser', password='testpass123')
        self.client.login(username='movieuser', password='testpass123')
        self.movie = _create_movie(
            title='Unique Action Movie',
            description='An action-packed film',
            release_date=date(2024, 6, 15),
            genre='action',
            length=135,
            age_rating='R',
        )

    def test_index_lists_movies(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unique Action Movie')

    def test_genre_filter(self):
        response = self.client.get(reverse('genre', args=['action']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unique Action Movie')

    def test_genre_filter_excludes_other_genres(self):
        response = self.client.get(reverse('genre', args=['comedy']))
        self.assertNotContains(response, 'Unique Action Movie')

    def test_genre_pagination(self):
        for i in range(15):
            _create_movie(
                title=f'Action Movie {i}',
                description='desc',
                genre='action',
                length=90,
            )
        response = self.client.get(reverse('genre', args=['action']))
        self.assertContains(response, 'Page 1 of 2')

    def test_movie_detail_page(self):
        response = self.client.get(reverse('movie', args=[self.movie.uu_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unique Action Movie')
        self.assertContains(response, '135 min')

    def test_movie_detail_increments_views(self):
        initial_views = self.movie.movie_views
        self.client.get(reverse('movie', args=[self.movie.uu_id]))
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.movie_views, initial_views + 1)

    def test_search_found(self):
        response = self.client.get(reverse('search'), {'q': 'Action'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unique Action Movie')

    def test_search_not_found(self):
        response = self.client.get(reverse('search'), {'q': 'NonExistentXYZ'})
        self.assertContains(response, 'No movies found')

    def test_search_empty_query(self):
        response = self.client.get(reverse('search'), {'q': ''})
        self.assertEqual(response.status_code, 200)

    def test_search_pagination(self):
        for i in range(15):
            _create_movie(
                title=f'Findable Movie {i}',
                description='desc',
                genre='drama',
                length=90,
            )
        response = self.client.get(reverse('search'), {'q': 'Findable'})
        self.assertContains(response, 'Page 1 of 2')


class MyListViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='listuser', password='testpass123')
        self.client.login(username='listuser', password='testpass123')
        self.movie = _create_movie(
            title='Listable Movie',
            description='desc',
            genre='drama',
            length=90,
        )

    def test_my_list_empty(self):
        response = self.client.get(reverse('my-list'))
        self.assertContains(response, 'Your list is empty')

    def test_add_to_list(self):
        response = self.client.post(reverse('add-to-list'), {
            'movie_id': str(self.movie.uu_id),
        })
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success', 'message': 'Added ✓'})
        self.assertTrue(MovieList.objects.filter(owner_user=self.user, movie=self.movie).exists())

    def test_add_to_list_duplicate(self):
        MovieList.objects.create(owner_user=self.user, movie=self.movie)
        response = self.client.post(reverse('add-to-list'), {
            'movie_id': str(self.movie.uu_id),
        })
        self.assertJSONEqual(response.content, {'status': 'info', 'message': 'Movie already in list'})

    def test_add_to_list_get_returns_error(self):
        response = self.client.get(reverse('add-to-list'))
        self.assertEqual(response.status_code, 400)

    def test_my_list_shows_added_movies(self):
        MovieList.objects.create(owner_user=self.user, movie=self.movie)
        response = self.client.get(reverse('my-list'))
        self.assertContains(response, 'Listable Movie')
