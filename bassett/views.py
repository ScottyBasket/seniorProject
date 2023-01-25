from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect, get_object_or_404
from django.template import loader
from django.urls import reverse_lazy, reverse
from django.views.generic import View
from django.utils.safestring import mark_safe  # to add blank line in forms
from django.utils.translation import gettext, gettext_lazy as _

import random

from .forms import *

from eli.settings import EMAIL_HOST_USER as EMAIL_HOST_USER

templates = "static/css/style.css"


#
# HOME
#

class HomeView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')   # give login location
    template_name = 'home.html'
    
    def get(self, request):
        context = {}
        context['user_name'] = request.user.name
        # ### TESTING
        # upcoming_games = team.get_upcoming_games()
        # for g in upcoming_games:
        #     print(g,upcoming_games[g])
        # current_games = team.get_current_games()
        # print('current gamesssssssssssssssss',type(current_games), current_games)
        # for g in current_games:
        #     print(g, type(g)) #,current_games[g])
        # c_loss = team.get_current_losses()
        # ### END TESTING

        team = Team.get_first_player_team(request.user)
        teamName = UserProfile.objects.get(id=request.user.id)

        

        if team != None:
            teamNames = team.league.get_teams_per_league()
            context['topTeams'] = team.league.get_teams_per_league()
        else:
            teamNames = None
        context['teamNames'] = teamNames

        context['myTeam'] = team
        
        if team:
            context['nextGame'] = team.get_next_game()
        else:
            context['nextGame'] = None


        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)

class TestView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')   # give login location
    template_name = 'test.html'
    
    def get(self, request):
        context = {}
        league = League.get_leagues().first()


        
        context['testData'] = 'pizza' #league.sport.get_sport_rules() #team_list
        return render(request, self.template_name, context)

class SchedulingView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')   # give login location
    template_name = 'scheduling.html'
    
    def get(self, request):
        context = {}
        context['user_name'] = request.user.name
        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)

#
# GAME
#

class GameAddView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login') # give login location
    template_name = 'scheduling.html'
    h1 = 'Add Game'

    def get(self, request):
        form = GameForm()
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        context['user_name'] = request.user.name
        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = GameForm(request.POST)
        if form.is_valid():
            instance = form.save()

            # get a random color
            # color1 = random.choice(SHIRTCOLOR)[0]
            color1 = random.choice(ShirtColor.choices)[0]
            color2 = None
            if color1 == ShirtColor.BLACK[0]:
                color2 = ShirtColor.WHITE[0]
            else:
                color2 = ShirtColor.BLACK[0]
            
            instance.color1 = color1
            instance.color2 = color2
            instance.save()
            return HttpResponseRedirect(reverse('home'))
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)

class GameEditView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login') # give login location
    template_name = 'scheduling.html'
    h1 = 'Edit Game'

    def get(self, request, id=0):
        data = get_object_or_404(Game, id=id)
        # edit is actually important here to decide what locations to choose
        form = GameForm(instance=data, edit=True)
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        context['user_name'] = request.user.name
        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        id = kwargs['id'] # that was passed on the URL
        data = get_object_or_404(Game, id=id)
        form = GameForm(request.POST, instance=data, edit=True)
        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(reverse('home'))
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        return render(request, self.template_name, context)

class GamesView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login') # give login location
    template_name = 'list.html'
    h1 = 'List Games'
    
    def get(self, request):
        data = Game.objects.all().order_by('date', 'time')
        context = {}
        context['h1'] = self.h1
        context['data'] = data
        context['user_name'] = request.user.name
        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)

class GameUpdateScoreView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login') # give login location
    template_name = 'scheduling.html'
    h1 = 'Update Game Score'

    def get(self, request, id=0):
        data = get_object_or_404(Game, id=id)
        print(data)
        form = GameUpdateScoreForm(instance=data)
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        id = kwargs['id'] # that was passed on the URL
        data = get_object_or_404(Game, id=id)
        form = GameUpdateScoreForm(request.POST, instance=data)
        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(reverse('home'))
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        return render(request, self.template_name, context)


#
# LEAGUE
#

class LeagueAddView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login') # give login location
    template_name = 'scheduling.html'
    h1 = 'Add League'

    def get(self, request):
        form = LeagueForm()
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        context['user_name'] = request.user.name
        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = LeagueForm(request.POST)
        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(reverse('home'))
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)

class LeagueEditView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login') # give login location
    template_name = 'scheduling.html'
    h1 = 'Edit League'

    def get(self, request, id=0):
        data = get_object_or_404(League, id=id)
        data.get_leagues()
        form = LeagueForm(instance=data)
        context = {}
        context['h1'] = self.h1
        context['user_name'] = request.user.name
        context['form'] = form
        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        id = kwargs['id'] # that was passed on the URL
        data = get_object_or_404(League, id=id)
        form = LeagueForm(request.POST, instance=data)
        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(reverse('home'))
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        return render(request, self.template_name, context)

class LeaguesView(LoginRequiredMixin, View): 
    login_url = reverse_lazy('login')  # give login location
    template_name = 'list.html'
    h1 = 'List Leagues'

    def get(self, request):
        data = League.objects.all().order_by('name')
        context = {}
        context['h1'] = self.h1
        context['data'] = data
        context['user_name'] = request.user.name
        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)

#
# LOCATION
#

class LocationAddView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login') # give login location
    template_name = 'scheduling.html'
    h1 = 'Add Location'

    def get(self, request):
        form = LocationForm()
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        context['user_name'] = request.user.name
        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = LocationForm(request.POST)
        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(reverse('home'))
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        return render(request, self.template_name, context)

class LocationEditView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')   # give login location
    template_name = 'scheduling.html'
    h1 = 'Edit Location'

    def get(self, request, id=0):
        location: Location = get_object_or_404(Location, id=id)
        
        if not request.session.session_key:
            # a logged-in user has a key, an anonymous user has None. So get one for the anonymous user.
            request.session.save()
        request.session['location_name'] = location.name
        form = LocationForm(instance=location)
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        context['user_name'] = request.user.name
        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        id = kwargs['id'] # that was passed on the URL
        location: Location = get_object_or_404(Location, id=id)
        form = LocationForm(request.POST, instance=location, edit=True, location_name=request.session.pop('location_name', None))
        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(reverse('home'))
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        return render(request, self.template_name, context)

class LocationsView(LoginRequiredMixin, View): 
    login_url = reverse_lazy('login')  # give login location
    template_name = 'list.html'
    h1 = 'List Locations'

    def get(self, request):
        data = Location.get_all_locations()
        context = {}
        context['h1'] = self.h1
        context['data'] = data
        context['user_name'] = request.user.name
        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)

#
# SPORT
#

class SportAddView(LoginRequiredMixin, View): 
    login_url = reverse_lazy('login')  # give login location
    template_name = 'scheduling.html'
    h1 = 'Add Sport'

    def get(self, request):
        form = SportForm()
        context = {}
        context['h1'] = self.h1
        context['form'] = form 
        context['user_name'] = request.user.name
        if request.user.is_president():
            context['is_president'] = True
        return render(request,self.template_name, context)
   
    def post(self, request, *args, **kwargs):
        form = SportForm(request.POST)
        if form.is_valid():# and other_location_form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(reverse('home'))
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        return render(request,self.template_name, context)
        

class SportEditView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')   # give login location
    template_name = 'scheduling.html'
    h1 = 'Edit Sport'

    def get(self, request, id=0):
        sport: Sport = get_object_or_404(Sport, id=id)

        if not request.session.session_key:
            # a logged-in user has a key, an anonymous user has None. So get one for the anonymous user.
            request.session.save()
        request.session['sport_name'] = sport.name

        form = SportForm(instance=sport)

        context = {}
        context['h1'] = self.h1
        context['user_name'] = request.user.name
        context['form'] = form
        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        id = kwargs['id'] # that was passed on the URL
        sport: Sport = get_object_or_404(Sport, id=id)
        form = SportForm(request.POST, instance=sport, edit=True, sport_name=request.session.pop('sport_name', None))
        
        if form.is_valid():# and other_location_form.is_valid() and current_location_form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(reverse('home'))
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)

class SportsView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')  # give login location
    template_name = 'list.html'
    h1 = 'List Sports'

    def get(self, request):
        data = Sport.objects.all().order_by('name')
        context = {}
        context['h1'] = self.h1
        context['data'] = data
        context['user_name'] = request.user.name
        if request.user.is_president():
            context['is_president'] = True
        return render(request,self.template_name, context)

#
# TEAM
#

class TeamAddView(LoginRequiredMixin, View): 
    login_url = reverse_lazy('login')  # give login location
    template_name = 'scheduling.html'
    h1 = 'Add Team'

    def get(self, request):
        form = TeamForm()
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        context['user_name'] = request.user.name
        if request.user.is_president():
            context['is_president'] = True
        return render(request,self.template_name, context)
    
    def post(self, request,*args, **kwargs):
        form = TeamForm(request.POST, player=request.user)
        if form.is_valid():
            team = form.save()
            team.join_team(user=request.user)
            return HttpResponseRedirect(reverse('home'))
                
        context = {}
        context['form'] = form
        context['h1'] = self.h1
        return render(request,self.template_name, context)

class TeamEditView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')   # give login location
    template_name = 'scheduling.html'
    h1 = 'Edit Team'

    def get(self, request, id=0):
        team: Team = get_object_or_404(Team, id=id)
        
        if not request.session.session_key:
            # a logged-in user has a key, an anonymous user has None. So get one for the anonymous user.
            request.session.save()
        request.session['team_name'] = team.name

        form = TeamForm(instance=team)
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        context['user_name'] = request.user.name
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        id = kwargs.get('id') # that was passed on the URL
        team: Team = get_object_or_404(Team, id=id)
        form = TeamForm(request.POST, instance=team, edit=True, team_name=request.session.pop('team_name', None))
        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(reverse('home'))
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        return render(request, self.template_name, context)

class TeamsView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')  # give login location
    template_name = 'list.html'
    h1 = 'List Teams'

    def get(self, request):
        teams = Team.objects.all().order_by('name')
        context = {}
        context['h1'] = self.h1
        context['data'] = teams
        context['user_name'] = request.user.name
        return render(request, self.template_name, context)

class JoinTeamView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')   # give login location
    template_name = 'scheduling.html'
    h1 = 'Join Team'

    def get(self, request):
        form = JoinTeamForm()
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        context['user_name'] = request.user.name
        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = JoinTeamForm(request.POST, player=request.user)
        if form.is_valid():
            team = form.get_chosen_team()
            team.join_team(request.user)
            return HttpResponseRedirect(reverse('home'))
        context = {}
        context['h1'] = self.h1
        context['form'] = form
        return render(request, self.template_name, context)

#
# Personal Info
#

class TeamInfo(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')
    template_name = 'teamInfo.html'

    def get(self, request):
        context = {}
        context['user_name'] = request.user.name
        team = Team.get_first_player_team(request.user)
        if team != None:
            teamMembers = team.get_team_members()
            teamName = UserProfile.objects.get(id=request.user.id)
            context['teamMembers'] = teamMembers
            context['upcomingGames'] = team.get_upcoming_games()
            context['nextGame'] = team.get_next_game()
            context['myTeam'] = team
        else:
            teamNames = None

        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)

class Schedule(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')
    template_name = 'schedule.html'

    def get(self, request):
        context = {}
        team = Team.get_first_player_team(request.user)
        

        if team != None:
            context['user_name'] = request.user.name
            league = team.league
            context['upcomingGames'] = league.get_games_per_league()
        else:
            league = None
        

        if request.user.is_president():
            context['is_president'] = True
        return render(request, self.template_name, context)