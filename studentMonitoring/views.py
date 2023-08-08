from django.contrib.auth import logout, login
from django.shortcuts import render, redirect

from studentMonitoring.models import StudentInfo, Rating, StudentRating, RatingType, Team, Subject, StudentMark
from studentMonitoring.forms import MyAuthenticationForm, SelectFormForm, AddHealthForm, AddViolationForm, \
    SelectSubjectFormForm, AddMarkForm
from studentMonitoring.filters import StudentFilterTeam, StudentFilterRating


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
    return render(request, "studentMonitoring/logout.html")


def main_tab(request):
    if 'exit' in request.POST:
        logout(request)
        return redirect("/")
    return render(request, "studentMonitoring/main_tab.html")


def add_health(request, pk_st=None):
    context = {}
    if request.method == "POST":
        select_form = SelectFormForm(data=request.POST)
        if select_form.is_valid():
            students = StudentInfo.objects.filter(form=select_form.cleaned_data['form']).order_by('surname')
            context = {'select_form': select_form, 'students': students}
    elif pk_st:
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
        context['select_form'] = SelectFormForm()
    return render(request, "studentMonitoring/add_health.html", context)


def generate_rating(request):
    context = {}
    all_students = StudentInfo.objects.all().order_by('-sport_assessment', '-study_assessment', 'violation_assessment')
    student_filter = StudentFilterRating(request.GET, queryset=all_students)
    students = sorted(student_filter.qs, key=lambda t: t.calculate_general_assessment, reverse=True)
    context['students'] = students
    context['student_filter'] = student_filter
    if request.method == "POST":
        rating_type = RatingType.objects.get(pk=1)
        my_rating = Rating(rating_type=rating_type)
        my_rating.save()
        for student in students:
            StudentRating(rating=my_rating, student=student).save()
        return redirect('display_rating', pk_rt=my_rating.id)
    return render(request, "studentMonitoring/generate_rating.html", context)


def display_rating(request, pk_rt):
    context = {}
    rating = Rating.objects.get(pk=pk_rt)
    students = [r.student for r in StudentRating.objects.filter(rating=rating)]
    students = sorted(students, key=lambda t: t.calculate_general_assessment, reverse=True)
    context['students'] = students
    return render(request, "studentMonitoring/display_rating.html", context)


def add_violation(request, pk_st=None):
    context = {}
    if request.method == "POST":
        select_form = SelectFormForm(data=request.POST)
        if select_form.is_valid():
            students = StudentInfo.objects.filter(form=select_form.cleaned_data['form']).order_by('surname')
            context = {'select_form': select_form, 'students': students}
    elif pk_st:
        student = StudentInfo.objects.get(pk=pk_st)
        context['student'] = student
        if request.method == "POST":
            add_violation_form = AddViolationForm(data=request.POST)
            if add_violation_form.is_valid():
                context['add_violation_form'] = add_violation_form
        else:
            context['add_violation_form'] = AddViolationForm()
    else:
        context['select_form'] = SelectFormForm()
    return render(request, "studentMonitoring/add_violation.html", context)


def students_view(request):
    context = {}
    if request.method == "POST":
        select_subject_form = SelectSubjectFormForm(data=request.POST)
        if select_subject_form.is_valid():
            subject_id = select_subject_form.cleaned_data['subject'].id
            students = StudentInfo.objects.filter(form=select_subject_form.cleaned_data['form']).order_by('surname')
            context = {'select_subject_form': select_subject_form, 'students': students, 'subject_id': subject_id}
    else:
        context['select_subject_form'] = SelectSubjectFormForm()
    return render(request, "studentMonitoring/students.html", context)


def add_mark(request, pk_subj, pk_st):
    student = StudentInfo.objects.get(pk=pk_st)
    subject = Subject.objects.get(pk=pk_subj)
    if request.method == 'POST':
        form = AddMarkForm(request.POST, instance=StudentMark(student=student, subject=subject))
        if form.is_valid():
            form.save()
    else:
        form = AddMarkForm()
    context = {'student': student, 'subject': subject, 'form': form}
    return render(request, "studentMonitoring/add_mark.html", context)


def create_team(request):
    context = {}
    all_students = StudentInfo.objects.all()
    student_filter = StudentFilterTeam(request.GET, queryset=all_students)
    students = sorted(student_filter.qs, key=lambda t: t.calculate_general_assessment, reverse=True)
    students_viol = [s for s in students if s.violation_assessment != 0]
    students = [s for s in students if s.violation_assessment == 0]
    context['students'] = students
    context['students_viol'] = students_viol
    context['student_filter'] = student_filter
    if request.method == "POST":
        rating_type = RatingType.objects.get(pk=2)
        my_rating = Rating(rating_type=rating_type)
        my_rating.save()
        for student in student_filter.qs:
            StudentRating(rating=my_rating, student=student).save()
        return redirect('display_team', pk_rt=my_rating.id)
    return render(request, "studentMonitoring/create_team.html", context)


def display_team(request, pk_rt):
    context = {}
    team = Team.objects.get(pk=pk_rt)
    students = team.members.all().order_by('-sport_assessment', '-study_assessment', 'violation_assessment')
    students = sorted(students, key=lambda t: t.calculate_general_assessment, reverse=True)
    context['students'] = students
    return render(request, "studentMonitoring/display_team.html", context)
