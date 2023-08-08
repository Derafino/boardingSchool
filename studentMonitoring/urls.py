from django.urls import path
from . import views

urlpatterns = [
    path("", views.main_tab, name="main_tab"),
    path("add_marks/", views.students_view, name="students"),
    path("add_marks/<str:pk_subj>/<str:pk_st>/", views.add_mark, name="add_mark"),
    path("add_health/", views.add_health, name="add_health"),
    path("add_health/<str:pk_st>/", views.add_health, name="add_health"),
    path("add_violation/", views.add_violation, name="add_violation"),
    path("add_violation/<str:pk_st>/", views.add_violation, name="add_violation"),
    path("generate_rating/", views.generate_rating, name="generate_rating"),
    path("display_rating/<str:pk_rt>/", views.display_rating, name="display_rating"),
    path("create_team/", views.create_team, name="create_team"),
    path("display_team/<str:pk_rt>/", views.display_team, name="display_team"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
