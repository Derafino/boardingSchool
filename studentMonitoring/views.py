import csv
import datetime

from django.contrib.auth import logout, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from studentMonitoring.models import StudentInfo, Subject, StudentMark, Rating, StudentRating, RatingType, Team
from studentMonitoring.forms import SelectSubjectFormForm, AddMarkForm, SelectFormForm, AddHealthForm, AddViolationForm, \
    MyAuthenticationForm
from django.contrib import messages
from .filters import StudentFilterTeam, StudentFilterRating


def login_view(request):
    if request.method == "POST":
        form = MyAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
    else:
        form = MyAuthenticationForm(request)
    return render(request, "studentMonitoring/login.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("/")
    return render(request, "studentMonitoring/logout.html", {})


def main_tab(request):
    print(request.content_params)
    print(request.path_info)
    if 'exit' in request.POST:
        logout(request)
        return redirect("/")
    return render(request, "studentMonitoring/main_tab.html")


def add_health(request, pk_st=None):
    if request.method == "POST":
        select_form = SelectFormForm(data=request.POST)
        if select_form.is_valid():
            students = StudentInfo.objects.filter(form=select_form.cleaned_data['form']).order_by('surname')
            context = {'select_form': select_form, 'students': students}

    else:
        context = {}
        if pk_st:
            student = StudentInfo.objects.get(pk=pk_st)
            context['student'] = student
            if request.method == "POST":
                add_health_form = AddHealthForm(data=request.POST)

                if add_health_form.is_valid():
                    context['add_health_form'] = add_health_form
            else:
                add_health_form = AddHealthForm()
                context['add_health_form'] = add_health_form
        else:
            select_form = SelectFormForm()
            context = {'select_form': select_form}
    return render(request, "studentMonitoring/add_health.html", context, )


def generate_rating(request):
    context = {}
    all_students = StudentInfo.objects.all().order_by('-sport_assessment', '-study_assessment', 'violation_assessment')
    student_filter = StudentFilterRating(request.GET, queryset=all_students)
    students_qs = student_filter.qs
    students = sorted(students_qs, key=lambda t: t.calculate_general_assessment, reverse=True)
    context['students'] = students
    # request.session['rating'] = [s for s in student_filter.qs]
    context['student_filter'] = student_filter
    if request.method == "POST":
        rating_type = RatingType.objects.get(pk=1)
        my_rating = Rating(rating_type=rating_type)
        my_rating.save()
        for student in students:
            sr = StudentRating(rating=my_rating, student=student)
            sr.save()
        return redirect('display_rating', pk_rt=my_rating.id)
    return render(request, "studentMonitoring/generate_rating.html", context)


def display_rating(request, pk_rt):
    context = {}
    rating = Rating.objects.get(pk=pk_rt)
    st_rt = StudentRating.objects.filter(rating=rating)
    st = [r.student.id for r in st_rt]
    students = StudentInfo.objects.filter(id__in=st).order_by('-sport_assessment', '-study_assessment',
                                                              'violation_assessment')
    students = sorted(students, key=lambda t: t.calculate_general_assessment, reverse=True)
    context['students'] = students
    # students = StudentInfo.objects.filter()

    return render(request, "studentMonitoring/display_rating.html", context)


def add_violation(request, pk_st=None):
    if request.method == "POST":
        select_form = SelectFormForm(data=request.POST)
        if select_form.is_valid():
            students = StudentInfo.objects.filter(form=select_form.cleaned_data['form']).order_by('surname')
            context = {'select_form': select_form, 'students': students}

    else:
        context = {}
        if pk_st:
            student = StudentInfo.objects.get(pk=pk_st)
            context['student'] = student
            if request.method == "POST":
                add_violation_form = AddViolationForm(data=request.POST)

                if add_violation_form.is_valid():
                    context['add_violation_form'] = add_violation_form
            else:
                add_violation_form = AddViolationForm()
                context['add_violation_form'] = add_violation_form
        else:
            select_form = SelectFormForm()
            context = {'select_form': select_form}
    return render(request, "studentMonitoring/add_violation.html", context, )


def students_view(request):
    if request.method == "POST":
        select_subject_form = SelectSubjectFormForm(data=request.POST)
        if select_subject_form.is_valid():
            subject_id = select_subject_form.cleaned_data['subject'].id
            students = StudentInfo.objects.filter(form=select_subject_form.cleaned_data['form']).order_by('surname')
            context = {'select_subject_form': select_subject_form, 'students': students, 'subject_id': subject_id}

    else:
        select_subject_form = SelectSubjectFormForm()
        context = {'select_subject_form': select_subject_form}
    return render(request, "studentMonitoring/students.html", context, )


def add_mark(request, pk_subj, pk_st):
    student = StudentInfo.objects.get(pk=pk_st)
    subject = Subject.objects.get(pk=pk_subj)
    # subject_mark = StudentMark.objects.get(student=pk_st, subject=pk_subj)
    form = AddMarkForm()
    student_subject = StudentMark(student=student, subject=subject)

    if request.method == 'POST':
        # print('Printing POST:', request.POST)
        form = AddMarkForm(request.POST, instance=student_subject)
        if form.is_valid():
            form.save()
    context = {'student': student, 'subject': subject, 'form': form}
    return render(request, "studentMonitoring/add_mark.html", context)


def save_rating(request):
    rating = request.session.get('rating', None)
    print(rating)
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    print(writer)
    # writer.writerow()


def create_team(request):
    context = {}
    all_students = StudentInfo.objects.all()
    student_filter = StudentFilterTeam(request.GET, queryset=all_students)
    students_qs = student_filter.qs
    students = sorted(students_qs, key=lambda t: t.calculate_general_assessment, reverse=True)
    students_viol = [s for s in students if s.violation_assessment != 0]
    students = [s for s in students if s.violation_assessment == 0]
    context['students'] = students
    context['students_viol'] = students_viol
    # request.session['rating'] = [s for s in student_filter.qs]
    context['student_filter'] = student_filter
    if request.method == "POST":
        rating_type = RatingType.objects.get(pk=2)
        my_rating = Rating(rating_type=rating_type)
        my_rating.save()
        for student in students_qs:
            sr = StudentRating(rating=my_rating, student=student)
            sr.save()
        return redirect('display_team', pk_rt=my_rating.id)
    return render(request, "studentMonitoring/create_team.html", context)


def display_team(request, pk_rt):
    context = {}
    # rating = Rating.objects.get(pk=pk_rt)
    # st_rt = StudentRating.objects.filter(rating=rating)
    # st = [r.student.id for r in st_rt]
    # students = StudentInfo.objects.filter(id__in=st).order_by('-sport_assessment')
    team = Team.objects.get(pk=pk_rt)

    students = team.members.all().order_by('-sport_assessment', '-study_assessment', 'violation_assessment')
    students = sorted(students, key=lambda t: t.calculate_general_assessment, reverse=True)
    context['students'] = students
    # students = StudentInfo.objects.filter()

    return render(request, "studentMonitoring/display_team.html", context)
