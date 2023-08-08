from datetime import datetime

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Section(models.Model):
    section_name = models.CharField(max_length=120)

    def __str__(self):
        return self.section_name

    class Meta:
        verbose_name = "Секція"
        verbose_name_plural = "Секції"


class UserRole(models.Model):
    role_name = models.CharField(verbose_name="Назва ролі", max_length=20)

    def __str__(self):
        return self.role_name

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Ролі"


class User(models.Model):
    name = models.CharField(verbose_name="Ім'я", max_length=40)
    surname = models.CharField(verbose_name="Прізвище", max_length=40)
    patronymic = models.CharField(verbose_name="Ім'я по батькові", max_length=40)
    login = models.CharField(verbose_name="Логін", max_length=40, unique=True)
    password = models.CharField(verbose_name="Пароль", max_length=40)
    role = models.ForeignKey(UserRole, blank=True, null=True, verbose_name="Роль користувача", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.surname} {self.name} {self.patronymic}"

    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"


class SubjectType(models.Model):
    subject_type_name = models.CharField(max_length=120, verbose_name="Тип предмета")

    def __str__(self):
        return self.subject_type_name

    class Meta:
        verbose_name = "Тип предмета"
        verbose_name_plural = "Типи предметів"


class Subject(models.Model):
    subject_type = models.ForeignKey(SubjectType, on_delete=models.CASCADE, verbose_name="Тип предмета")
    subject_name = models.CharField(max_length=120, verbose_name="Назва предмета")
    subjects = models.ManyToManyField(User, verbose_name="Вчитель")

    def __str__(self):
        return self.subject_name

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предмети"


class Sex(models.Model):
    sex_name = models.CharField(verbose_name="Назва статі", max_length=6)

    def __str__(self):
        return self.sex_name

    class Meta:
        verbose_name = "Стать"
        verbose_name_plural = "Статі"


class Form(models.Model):
    form_name = models.CharField(verbose_name="Назва класу", max_length=10)
    forms = models.ManyToManyField(Subject, verbose_name="Предмети")
    form_start = models.DateField(verbose_name="Дата створення класу")

    def __str__(self):
        return f"{datetime.now().year - self.form_start.year}-{self.form_name}"

    class Meta:
        verbose_name = "Клас"
        verbose_name_plural = "Класи"


class StudentInfo(models.Model):
    name = models.CharField(verbose_name="Ім'я", max_length=40)
    surname = models.CharField(verbose_name="Прізвище", max_length=40)
    patronymic = models.CharField(verbose_name="Ім'я по батькові", max_length=40)
    sex = models.ForeignKey(Sex, on_delete=models.CASCADE, verbose_name="Стать")
    birthday = models.DateField(verbose_name="Дата народження")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, verbose_name="Секція")
    form = models.ForeignKey(Form, on_delete=models.CASCADE, verbose_name="Клас")
    study_assessment = models.FloatField(verbose_name="Оцінка за навчання", default=0)
    sport_assessment = models.FloatField(verbose_name="Оцінка за спорт", default=0)
    violation_assessment = models.FloatField(verbose_name="Штрафна оцінка", default=0)

    @property
    def calculate_general_assessment(self):
        study = self.study_assessment
        sport = self.sport_assessment
        viol = self.violation_assessment
        general_assessment = study * 0.3 + sport * 0.7 - viol * 0.5
        return round(general_assessment, 3)
    def get_age(self):
        today = datetime.today()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))

    def __str__(self):
        return f"{self.surname} {self.name} {self.patronymic}"

    class Meta:
        verbose_name = "Учень"
        verbose_name_plural = "Учні"


class Violation(models.Model):
    student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    violation_date = models.DateTimeField(verbose_name="Дата порушення")
    violation_text = models.CharField(verbose_name="Текст порушення", max_length=500)

    class Meta:
        verbose_name = "Порушення"
        verbose_name_plural = "Порушення"


class MarkValue(models.Model):
    mark_value = models.IntegerField(verbose_name="Оцінка", validators=[MinValueValidator(1), MaxValueValidator(12)])

    class Meta:
        verbose_name = "Значення оцінки"
        verbose_name_plural = "Значення оцінок"

    def __str__(self):
        return str(self.mark_value)


class StudentHealth(models.Model):
    student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    health_date = models.DateField(verbose_name="Дата перевірки", auto_now_add=True)
    temperature = models.IntegerField(verbose_name="Температура")
    pressure = models.IntegerField(verbose_name="Тиск")
    pulse = models.IntegerField(verbose_name="Пульс")
    breath = models.IntegerField(verbose_name="Частота дихання")

    class Meta:
        verbose_name = "Стан здоров'я"
        verbose_name_plural = "Стани здоров'я"


class MarkType(models.Model):
    mark_type_name = models.CharField(max_length=120)

    def __str__(self):
        return self.mark_type_name

    class Meta:
        verbose_name = "Тип оцінки"
        verbose_name_plural = "Типи оцінок"


class StudentMark(models.Model):
    student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    mark_type = models.ForeignKey(MarkType, on_delete=models.CASCADE)
    mark_value = models.ForeignKey(MarkValue, on_delete=models.CASCADE)
    mark_date = models.DateField(verbose_name="Дата отримання оцінки", auto_now_add=True)

    class Meta:
        verbose_name = "Оцінка"
        verbose_name_plural = "Оцінки"


class RatingType(models.Model):
    rating_type_name = models.CharField(max_length=120)

    def __str__(self):
        return self.rating_type_name

    class Meta:
        verbose_name = "Тип рейтингу"
        verbose_name_plural = "Типи рейтенгу"


class Rating(models.Model):
    rating_type = models.ForeignKey(RatingType, on_delete=models.CASCADE)
    rating_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Рейтинг"
        verbose_name_plural = "Рейтенги"


class StudentRating(models.Model):
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Учень-рейтинг"
        verbose_name_plural = "Учень-рейтинг"


class Team(models.Model):
    members = models.ManyToManyField(StudentInfo, verbose_name="учень")
