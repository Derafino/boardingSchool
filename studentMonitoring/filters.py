import datetime
import django_filters
from django import forms

from .models import StudentInfo
from dateutil.relativedelta import relativedelta


class StudentFilterTeam(django_filters.FilterSet):
    min_age = django_filters.NumberFilter(field_name='birthday', method='get_min_age', lookup_expr='gte',
                                          label="Мінімальний вік")
    max_age = django_filters.NumberFilter(field_name='birthday', method='get_max_age', lookup_expr='lte',
                                          label="Максимальний вік")

    def get_max_age(self, queryset, name, value):
        time_threshold = datetime.datetime.now() - relativedelta(years=int(value + 1))
        print(time_threshold)
        return queryset.filter(birthday__gte=time_threshold)

    def get_min_age(self, queryset, name, value):
        time_threshold = datetime.datetime.now() - relativedelta(years=int(value))
        return queryset.filter(birthday__lte=time_threshold)

    class Meta:
        model = StudentInfo
        fields = '__all__'
        exclude = ['name', 'surname', 'patronymic', 'birthday', 'study_assessment', 'sport_assessment',
                   'violation_assessment']


class StudentFilterRating(django_filters.FilterSet):
    class Meta:
        model = StudentInfo
        fields = '__all__'
        exclude = ['name', 'surname', 'patronymic', 'birthday', 'study_assessment', 'sex', 'sport_assessment',
                   'violation_assessment']
