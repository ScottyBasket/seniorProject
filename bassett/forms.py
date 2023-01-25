from django import forms
from django.conf import settings
from django.contrib.auth.forms import ValidationError, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe  # to add blank line in forms
from django.utils.translation import gettext, gettext_lazy as _
from django.utils.timezone import now

from .models import *

from eli.settings import LEAGUE_GENDER_CHOICES as LEAGUE_GENDER_CHOICES


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = '__all__'
        exclude = ['score1', 'score2', 'color1', 'color2']

    def __init__(self, *args, **kwargs):
        super(GameForm, self).__init__(*args, **kwargs)

        self.fields['date'] = forms.DateField(
            label=mark_safe(_('Game date')),
            widget=forms.SelectDateWidget(years=range(2020, 2060)),
            initial=now
        )
        self.fields['time'] = forms.TimeField(
            label=mark_safe(_('Game time')),
            widget=forms.TimeInput(format='%H:%M'),
            initial=now
        )
        self.fields['league'] = forms.ModelChoiceField(queryset=League.get_leagues(), required=True)
        self.fields['location'] = forms.ModelChoiceField(queryset=Location.get_all_locations(), required=True)

    def clean(self):
        self.cleaned_data = super().clean()

        this_league: League = self.cleaned_data.get('league')
        location: Location = self.cleaned_data.get('location')
        team1: Team = self.cleaned_data.get('team1')
        team2: Team = self.cleaned_data.get('team2')
        game_date = self.cleaned_data.get('date')

        # the location must be valid for the sport
        if not this_league.sport.location_in_sport(location):
            raise ValidationError("The location must be available for that sport")

        # the teams can't match
        if team1 == team2:
            raise ValidationError("A team can't play against itself")

        # the teams must be apart of the same league as the game
        if (this_league != team1.league) or (this_league != team2.league):
            raise ValidationError("The teams should be in the same league as the game")

        # the date must be a valid date
        if game_date == None:
            raise ValidationError("Invalid date")
        
        # the game must start between the league season start and end date
        if game_date < this_league.start_date or game_date >= this_league.end_date:
            raise ValidationError("Game must happed during the league season")
        
        return self.cleaned_data

class GameUpdateScoreForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['score1', 'score2']

    def clean(self):
        self.cleaned_data = super().clean() # make sure the attributes of the parent class are available

        score1: int = int(self.cleaned_data.get('score1'))
        score2: int = int(self.cleaned_data.get('score2'))

        if (score1 != 0 and score2 != 0) and (score1 == score2):
            raise ValidationError("Games can't end in a tie")
        return self.cleaned_data


class LeagueForm(forms.ModelForm):
    class Meta:
        model = League
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(LeagueForm, self).__init__(*args, **kwargs)

        self.fields['start_date'] = forms.DateField(
            label=mark_safe(_('League starting date')),
            widget=forms.SelectDateWidget(years=range(2020, 2060)),
            initial=now
        )
        self.fields['end_date'] = forms.DateField(
            label=mark_safe(_('League ending date')),
            widget=forms.SelectDateWidget(years=range(2020, 2060)),
            initial=now
        )
        self.fields['last_signup_date'] = forms.DateField(
            label=mark_safe(_('Last signup date')),
            widget=forms.SelectDateWidget(years=range(2020, 2060)),
            initial=now
        )
        self.fields['sport'].queryset = Sport.objects.all().order_by('name')

    def clean(self):
        self.cleaned_data = super().clean()  # make sure the attributes of parent class are available

        last_signup_date = self.cleaned_data.get("last_signup_date")
        start_date = self.cleaned_data.get("start_date")
        end_date = self.cleaned_data.get("end_date")
        gender = self.cleaned_data.get("gender")
        min_men: int = int(self.cleaned_data.get("min_men"))
        min_women: int = int(self.cleaned_data.get("min_women"))
        sport: Sport = self.cleaned_data.get("sport")

        # signup can't be after start
        if last_signup_date > start_date:
            raise ValidationError("The last signup date shouldn't be after the start date")
        
        # start can't be after end
        if start_date > end_date:
            raise ValidationError("The start date shouldn't be after the end date")
        
        # co-ed requires a minimum men and minimum women, and other things.
        if gender == LEAGUE_GENDER_CHOICES[2][0]:
            # neither can be equal to zero
            if min_men == 0 or min_women == 0:
                raise ValidationError("Minimum men/women number required for co-ed")

            # adding them together, they can't be more than the sport's max player count
            if min_men + min_women > sport.max_players:
                raise ValidationError("Minimum men/women number larger than the sport's max player count")

        return self.cleaned_data

    def clean_name(self):
        name: str = self.cleaned_data.get("name")
        
        # make sure the name is unique for this season
        league_with_name = League.get_leagues(active=True).filter(name__iexact=name)
        if league_with_name.exists():
            raise ValidationError("That league currently exists")
        return name

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.edit: bool = kwargs.pop('edit', False)
        self.location_name = kwargs.pop('location_name', None)
        super(LocationForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name: str = self.cleaned_data.get("name")
        if self.edit and self.location_name == name:
            return name

        location_with_name = Location.objects.filter(name__iexact=name)
        if location_with_name.exists():
            raise ValidationError("That location already exists.")
        return name


class SportForm(forms.ModelForm):
    class Meta:
        model = Sport
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.edit: bool = kwargs.pop('edit', False)
        self.sport_name = kwargs.pop('sport_name', None)
        super(SportForm, self).__init__(*args, **kwargs)
        self.fields['valid_locations'] = forms.ModelMultipleChoiceField(
            queryset=Location.get_all_locations(),
            widget=forms.CheckboxSelectMultiple,
            required=True
        )
        

    def clean(self):
        self.cleaned_data = super().clean()  # make sure the attributes of parent class are available
        min_players: int = int(self.cleaned_data.get("min_players"))
        max_players: int = int(self.cleaned_data.get("max_players"))

        if max_players < min_players:
            raise ValidationError("You can't have more min players than max players")
        return self.cleaned_data

    def clean_name(self):
        name: str = self.cleaned_data.get("name")
        if self.edit and self.sport_name == name:
            return name

        sport_with_name = Sport.objects.filter(name__iexact=name)
        if sport_with_name.exists():
            raise ValidationError("That sport already exists")
        return name

#
# TEAMS
#

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = '__all__'
        exclude = ['player', 'wins', 'losses']

    def __init__(self, *args, **kwargs):
        self.edit: bool = kwargs.pop('edit', False)
        self.player: UserProfile = kwargs.pop('player', None)
        self.team_name = kwargs.pop('team_name', None)
        super(TeamForm, self).__init__(*args, **kwargs)

        self.fields['league'] = forms.ModelChoiceField(queryset=League.get_leagues(), required=True)

    def clean(self):
        self.cleaned_data = super().clean()  # make sure the attributes of parent class are available
        name: str = self.cleaned_data.get("name")
        league: League = self.cleaned_data.get("league")
        
        if self.edit and self.team_name == name:
            return self.cleaned_data
        teams_in_league = league.get_teams_per_league()
        team_in_league_with_name = teams_in_league.filter(name__iexact=name)
        if team_in_league_with_name.exists():
            raise ValidationError("That team already exists")

        # if player was passed, make sure that they can join the team they created
        if self.player != None:

            # if you are already in a team in this league
            for t in teams_in_league:
                if t.player_in_team(self.player):
                    raise ValidationError("You are already in a team in this league")
    
            # make sure they are in the right gender
            if self.player.gender == LEAGUE_GENDER_CHOICES[0][0]:
                if league.gender == LEAGUE_GENDER_CHOICES[1][0]:
                    raise ValidationError("You can't join a Men's leauge")
            elif self.player.gender == LEAGUE_GENDER_CHOICES[1][0]:
                if league.gender == LEAGUE_GENDER_CHOICES[0][0]:
                    raise ValidationError("You can't join a Women's league")

        return self.cleaned_data

class JoinTeamForm(forms.Form):
    class Meta:
        fields = ['teams']

    def __init__(self, *args, **kwargs):
        self.player = kwargs.pop('player', None)
        super(JoinTeamForm, self).__init__(*args, **kwargs)

        self.fields['teams'] = forms.ModelChoiceField(queryset=Team.get_teams(), required=True)

    def clean(self):
        self.cleaned_data = super().clean() # make sure the attributes of parent class are available.
        team: Team = self.cleaned_data.get("teams")

        # if you are already in the team
        if team.player_in_team(self.player):
            raise ValidationError("You are already in this team")

        # if you are already in a team in this league
        teams_in_league = team.league.get_teams_per_league()
        for t in teams_in_league:
            if t.player_in_team(self.player):
                raise ValidationError("You are already in a team in this league")
        
        # make sure the team size limit has not been reached
        if team.number_of_players() >= team.league.sport.max_players:
            raise ValidationError("This team is full")

        # make sure they are in the right gender
        if self.player.gender == LEAGUE_GENDER_CHOICES[0][0]:
            if team.league.gender == LEAGUE_GENDER_CHOICES[1][0]:
                raise ValidationError("You can't join a Men's leauge")
        elif self.player.gender == LEAGUE_GENDER_CHOICES[1][0]:
            if team.league.gender == LEAGUE_GENDER_CHOICES[0][0]:
                raise ValidationError("You can't join a Women's league")

        return self.cleaned_data

    def get_chosen_team(self) -> Team:
        return self.cleaned_data.get('teams')