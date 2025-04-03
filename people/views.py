from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from datetime import date, timedelta

from django.contrib import messages

from .models import Star, Country, Category
from django.contrib.auth.forms import UserCreationForm


def index(request):
    """
    Главная страница: выводим все звёзды + выделяем, у кого сегодня/завтра/послезавтра день рождения.
    """
    # Получаем все опубликованные звезды
    all_stars = Star.objects.filter(is_published=True)

    # Получаем текущую дату
    today = date.today()
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)

    # Находим звезд с днями рождения
    today_stars = []
    tomorrow_stars = []
    day_after_tomorrow_stars = []

    for star in all_stars:
        # Проверяем месяц и день (без учета года)
        if star.birth_date.month == today.month and star.birth_date.day == today.day:
            today_stars.append(star)
        elif star.birth_date.month == tomorrow.month and star.birth_date.day == tomorrow.day:
            tomorrow_stars.append(star)
        elif star.birth_date.month == day_after_tomorrow.month and star.birth_date.day == day_after_tomorrow.day:
            day_after_tomorrow_stars.append(star)

    # Получаем все страны и категории для меню
    countries = Country.objects.all()
    categories = Category.objects.all()

    context = {
        'stars': all_stars,
        'today_stars': today_stars,
        'tomorrow_stars': tomorrow_stars,
        'day_after_tomorrow_stars': day_after_tomorrow_stars,
        'today_date': today,
        'tomorrow_date': tomorrow,
        'day_after_tomorrow_date': day_after_tomorrow,
        'star_countries': countries,
        'star_categories': categories,
        'title': 'Дни рождения звезд'
    }
    return render(request, 'people/index.html', context)


def show_person(request, slug):
    """
    Детальная страница конкретной звезды: /person/<person_id>/
    """
    # Используем get_object_or_404 для получения объекта или выброса 404 ошибки
    star = get_object_or_404(Star, slug=slug, is_published=True)

    # Получаем все страны и категории для меню
    countries = Country.objects.all()
    categories = Category.objects.all()

    context = {
        'star': star,
        'star_countries': countries,
        'star_categories': categories,
    }

    return render(request, 'people/star-detail.html', context)


def about(request):
    """
    Страница «О сайте».
    """
    stats = {
        'stars_count': Star.objects.filter(is_published=True).count(),
        'countries_count': Country.objects.count(),
        'categories_count': Category.objects.count(),
    }
    # Получаем все страны и категории для меню
    countries = Country.objects.all()
    categories = Category.objects.all()

    context = {
        'title': 'О сайте',
        'description': 'Сайт создан в учебных целях. Данные сгенерированы нейросетью.',
        'stats': stats,
        'star_countries': countries,
        'star_categories': categories,
    }
    return render(request, 'people/about.html', context)


def stars_by_country(request, slug):
    country = get_object_or_404(Country, slug=slug)
    filtered_stars = Star.objects.filter(country=country, is_published=True)

    countries = Country.objects.all()
    categories = Category.objects.all()

    context = {
        'stars': filtered_stars,
        'country_name': country.name,
        'star_countries': countries,
        'star_categories': categories,
        'title_template': 'Знаменитости из страны'
    }
    return render(request, 'people/country.html', context)


def stars_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    filtered_stars = Star.objects.filter(categories=category, is_published=True)

    countries = Country.objects.all()
    categories = Category.objects.all()

    context = {
        'stars': filtered_stars,
        'category_name': category.title,
        'star_countries': countries,
        'star_categories': categories,
        'title_template': 'Знаменитости из отрасли',
    }
    return render(request, 'people/industry.html', context)


from .forms import StarForm

def add_star(request):
    """
    Представление для добавления новой знаменитости
    """
    if request.method == 'POST':
        form = StarForm(request.POST, request.FILES)
        if form.is_valid():
            star = form.save(commit=False)
            star.is_published = True
            star.save()
            form.save_m2m()  # Сохраняем связи many-to-many
            messages.success(request, f'Знаменитость "{star.name}" успешно добавлена!')
            return redirect('person', slug=star.slug)
    else:
        form = StarForm()

    # Получаем все страны и категории для меню
    countries = Country.objects.all()
    categories = Category.objects.all()

    context = {
        'form': form,
        'title': 'Добавление знаменитости',
        'star_countries': countries,
        'star_categories': categories,
    }
    return render(request, 'people/add-star.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт {username} успешно создан! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'people/register.html', {'form': form})

RUSSIAN_ALPHABET = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ'

def get_available_letters():
    available_letters = []
    for letter in RUSSIAN_ALPHABET:
        if Star.objects.filter(is_published=True, name__istartswith=letter).exists():
            available_letters.append(letter)
    return available_letters

def sitemap(request):
    #Карта сайта со списком всех знаменитостей
    stars = Star.objects.filter(is_published=True).order_by('name')
    available_letters = get_available_letters()

    # Получаем все страны и категории для меню
    countries = Country.objects.all()
    categories = Category.objects.all()

    context = {
        'stars': stars,
        'alphabet': RUSSIAN_ALPHABET,
        'available_letters': available_letters,
        'star_countries': countries,
        'star_categories': categories,
        'title': 'Карта сайта'
    }
    return render(request, 'people/sitemap.html', context)


def sitemap_letter(request, letter):
    #Карта сайта с фильтрацией по первой букве имени
    letter = letter.upper()  # Приводим к верхнему регистру
    stars = Star.objects.filter(
        is_published=True,
        name__istartswith=letter
    ).order_by('name')

    available_letters = get_available_letters()
    countries = Country.objects.all()
    categories = Category.objects.all()

    context = {
        'stars': stars,
        'current_letter': letter,
        'alphabet': RUSSIAN_ALPHABET,
        'available_letters': available_letters,
        'star_countries': countries,
        'star_categories': categories,
        'title': f'Знаменитости на букву {letter}'
    }
    return render(request, 'people/sitemap_letter.html', context)