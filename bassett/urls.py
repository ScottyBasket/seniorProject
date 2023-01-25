from django.urls import path

from . import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('scheduling/', views.SchedulingView.as_view(), name='scheduling'),
    path('teaminfo/', views.TeamInfo.as_view(), name='teamInfo'),
    path('schedule/', views.Schedule.as_view(), name='schedule'),
    path('test/', views.TestView.as_view(), name='test'),

    path('gameAdd/', views.GameAddView.as_view(), name='gameAdd'),
    path('gameEdit/<int:id>/', views.GameEditView.as_view(), name='gameEdit'),
    path('games/', views.GamesView.as_view(), name='games'),
    path('gameUpdateScore/<int:id>/', views.GameUpdateScoreView.as_view(), name='gameUpdateScore'),

    path('leagueAdd/', views.LeagueAddView.as_view(), name='leagueAdd'),
    path('leagueEdit/<int:id>/', views.LeagueEditView.as_view(), name='leagueEdit'),
    path('leagues/', views.LeaguesView.as_view(), name='leagues'),

    path('locationAdd/', views.LocationAddView.as_view(), name='locationAdd'),
    path('locationEdit/<int:id>/', views.LocationEditView.as_view(), name='locationEdit'),
    path('locations/', views.LocationsView.as_view(), name='locations'),

    path('sportAdd/', views.SportAddView.as_view(), name='sportAdd'),
    path('sportEdit/<int:id>/', views.SportEditView.as_view(), name='sportEdit'),
    path('sports/', views.SportsView.as_view(), name='sports'),
    
    path('teamAdd/', views.TeamAddView.as_view(), name='teamAdd'),
    path('teamEdit/<int:id>/', views.TeamEditView.as_view(), name='teamEdit'),
    path('teams/', views.TeamsView.as_view(), name='teams'),
    path('joinTeam/', views.JoinTeamView.as_view(), name='joinTeam'),
]