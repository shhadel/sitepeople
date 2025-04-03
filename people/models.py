from django.db import models
from datetime import date  # для работы с датами в методе get_age
from django.utils.text import slugify  # для преобразования строки в slug-формат (URL-безопасный)
from transliterate import translit  # для транслитерации русского текста в латиницу

class Country(models.Model):
   name = models.CharField(max_length=100, verbose_name="Название страны")  # Название страны
   slug = models.SlugField(max_length=255, unique=True, blank=True, db_index=True, verbose_name="URL")

   def __str__(self):
       return self.name

   def save(self, *args, **kwargs):
       if not self.slug:
           # Транслитерация имени с русского на английский
           translit_name = translit(self.name, 'ru', reversed=True)
           # Приведение к нижнему регистру и замена пробелов на дефисы
           base_slug = slugify(translit_name)

           # Проверка уникальности slug
           slug = base_slug
           n = 1
           while Star.objects.filter(slug=slug).exists():
               slug = f"{base_slug}-{n}"
               n += 1

           self.slug = slug

       super().save(*args, **kwargs)

class Category(models.Model):
   title = models.CharField(max_length=100, verbose_name="Название категории")  # Название категории
   slug = models.SlugField(max_length=255, blank=True, db_index=True, verbose_name="URL")

   def __str__(self):
       return self.title

   def save(self, *args, **kwargs):
       if not self.slug:
           # Транслитерация имени с русского на английский
           translit_name = translit(self.name, 'ru', reversed=True)
           # Приведение к нижнему регистру и замена пробелов на дефисы
           base_slug = slugify(translit_name)

           # Проверка уникальности slug
           slug = base_slug
           n = 1
           while Star.objects.filter(slug=slug).exists():
               slug = f"{base_slug}-{n}"
               n += 1

           self.slug = slug

       super().save(*args, **kwargs)

class Star(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")  # Имя звезды
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='stars', verbose_name="Страна")
    categories = models.ManyToManyField(Category, related_name='stars', verbose_name="Категории")
    birth_date = models.DateField(verbose_name="Дата рождения")  # Дата рождения
    content = models.TextField(verbose_name="Описание")  # Описание звезды
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True, null=True, verbose_name="Фотография")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")  # Флаг публикации
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")  # Дата создания (автоматически)
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")  # Дата обновления (автоматически)

    def __str__(self):
        return self.name

    death_date = models.DateField(
        'Дата смерти',
        null=True,
        blank=True,
        help_text='Оставьте пустым для живых знаменитостей'
    )

    def is_alive(self):
        return self.death_date is None

    def get_age(self):
        today = date.today()
        reference_date = self.death_date if not self.is_alive() else today

        age = reference_date.year - self.birth_date.year
        if (reference_date.month, reference_date.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    def get_lifespan(self):
        """Возвращает годы жизни в формате 'YYYY-YYYY' или 'YYYY-настоящее время'"""
        birth_year = self.birth_date.year
        if self.is_alive():
            return f"{birth_year}"
        return f"{birth_year}-{self.death_date.year}"

    def get_age_with_correct_word(self):
        """Возвращает возраст с правильно склоненным словом 'год'"""
        age = self.get_age()
        last_digit = age % 10
        last_two_digits = age % 100

        if 11 <= last_two_digits <= 14:
            return f"{age} лет"
        elif last_digit == 1:
            return f"{age} год"
        elif 2 <= last_digit <= 4:
            return f"{age} года"
        else:
            return f"{age} лет"

    def save(self, *args, **kwargs):
        if not self.slug:
            # Транслитерация имени с русского на английский
            translit_name = translit(self.name, 'ru', reversed=True)
            # Приведение к нижнему регистру и замена пробелов на дефисы
            base_slug = slugify(translit_name)

            # Проверка уникальности slug
            slug = base_slug
            n = 1
            while Star.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{n}"
                n += 1

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Знаменитость'
        verbose_name_plural = 'Знаменитости'
        # ordering = ['name']  # Сортировка по умолчанию по имени
        ordering = ['-time_create']  # Сортировка по убыванию времени создания
        indexes = [
            models.Index(fields=['-time_create']),  # Индекс для повышения производительности
        ]