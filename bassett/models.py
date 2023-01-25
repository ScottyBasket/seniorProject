from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from operator import itemgetter

from accounts.models import UserProfile
from eli.settings import LEAGUE_GENDER_CHOICES as LEAGUE_GENDER_CHOICES

MAX_NAME_LEN = 64

#
# ENUMS
#

class ShirtColor(models.TextChoices):
    BLACK = 'black', _('Black')
    WHITE = 'white', _('White')
BLACK = 0
WHITE = 1
SHIRTCOLOR = [
    ('black', 'Black'),
    ('white', 'White'),
]



class Game(models.Model):
    # The game should still happen at the game, and not be removed.
    location = models.ForeignKey('Location', on_delete=models.PROTECT)
    
    date = models.DateField(null=False, blank=False)
    time = models.TimeField(null=False, blank=False)
    
    # if a league is deleted, surely the game should be deleted.
    league = models.ForeignKey('League', on_delete=models.CASCADE)
    
    # you can't delete a team while it's in a game.
    team1 = models.ForeignKey('Team', on_delete=models.PROTECT, related_name='team1')
    team2 = models.ForeignKey('Team', on_delete=models.PROTECT, related_name='team2')

    score1 = models.PositiveIntegerField(null=False, blank=False, default=0)
    score2 = models.PositiveIntegerField(null=False, blank=False, default=0)

    color1 = models.CharField(
        max_length=7,
        choices=ShirtColor.choices,
        default=ShirtColor.BLACK[0]
    )
    color2 = models.CharField(
        max_length=7,
        choices=ShirtColor.choices,
        default=ShirtColor.BLACK[0]
    )

    def __str__(self) -> str:
        return self.team1.name + " VS " + self.team2.name + " @ " + str(self.date) + " " + str(self.time)


class League(models.Model):
    SEASON_RANGE = {  # This is used to determine what season the league is part of.
        'J-Term': [1, 1],
        'Spring': [2, 5],
        'Fall':   [8, 12],
    }

    name = models.CharField(null=False, blank=False, max_length=MAX_NAME_LEN)
    # if a sport is deleted, so are the leagues
    
    sport = models.ForeignKey('Sport', on_delete=models.CASCADE)
    
    gender = models.CharField(max_length=7, choices=LEAGUE_GENDER_CHOICES, blank=False)
    
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    last_signup_date = models.DateField(null=False, blank=False)
    msg = "minimum men players required for co-ed"
    min_men = models.PositiveIntegerField(null=True, blank=True, help_text=msg)
    msg = "minimum women players required for co-ed"
    min_women = models.PositiveIntegerField(null=True, blank=True, help_text=msg)

    def __str__(self) -> str:
        msg = str(self.name)
        msg += " (" + str(self.sport.name)
        msg += " " + str(self.start_date) + ")"
        return msg

    def get_season_name(month=0) -> str:
        """
        :return: Season name based on the month number.\
            If month number isn't passed, it uses the current month.\
            If month number passed isn't in a season, it returns 'Error'.
        
        Uses the month to determine the season.
        """
        if month == 0:
            month = now().month
        
        for season in League.SEASON_RANGE:
            if (month >= League.SEASON_RANGE[season][0]) and (month <= League.SEASON_RANGE[season][1]):
                return season
        return "Error"

    def get_league_season(self) -> str:
        """
        :return: Season name that this league is apart of.

        Uses the start_date to determine the season.
        """
        month = self.start_date.month
        return League.get_season_name(month)

    def is_active(self) -> bool:
        """
        :return: True if league is current year\
            and is between the start and end date.\
            False otherwise.
        
        Whether the league is active or not.
        """
        current_year = now().year
        league_season = League.get_season_name(self.start_date.month)
        current_season = League.get_season_name()
        # if it's within the same current year and within the same season.
        return (self.start_date.year == current_year) and (league_season == current_season)
    
    def get_teams_per_league(self):
        """
        :return: list of lists of teams in a league with interlist being [teams, wins, and losses]
            Ordered by wins DESC and losses ASC.
        """
        #                                order by with a `-` makes it descending, rather than ascending.
        teams = Team.objects.filter(league=self)#.order_by('-wins', 'losses') # wins, losses field no longer exist
        for team in teams:
            team.refresh_wins_losses()
        teams = Team.objects.filter(league=self).order_by('-wins', 'losses') # wins, losses field no longer exist
        return teams
        # team_list = []
        # for team in teams:
        #     wins, losses, ties = team.get_current_wins_and_losses_ties()
        #     team_list.append([team.name, wins, losses])
        # team_sorted = sorted(team_list, key=itemgetter(1)) # sort on wins of inner list
        # print('........ team sorted:', team_sorted)
        # return team_sorted

    def get_games_per_league(self):
        """
        :return: QuerySet of all games in a league.\
            Ordered by wins DESC and losses ASC.
        """
        return Game.objects.filter(league=self).order_by('date', 'time')

    @classmethod
    def get_leagues(cls, active=True):
        """
        :return: list of leagus for this current season.

        Use the year and month to determine if it is a current league
        """
        if active:
            year = now().year
            season = cls.get_season_name()
            
            if season == "Error":
                # If there's an error finding the season,
                # just return all leagues for this year.
                return cls.objects.filter(start_date__year=year).order_by('start_date')
            
            season_start = cls.SEASON_RANGE[season][0]
            season_end = cls.SEASON_RANGE[season][1]

            return cls.objects.filter(
                start_date__year=year,
                start_date__month__gte=season_start,
                start_date__month__lte=season_end
            ).order_by('start_date')
        
        return cls.objects.all().order_by('start_date')

class Location(models.Model):
    name = models.CharField(null=False, blank=False, max_length=MAX_NAME_LEN)

    # we might want to add an image with a map describing each
    # location, but that's a future idea.

    def __str__(self) -> str:
        return self.name
    
    @classmethod
    def get_all_locations(cls):
        return cls.objects.all().order_by('name')


class Sport(models.Model):
    name = models.CharField(null=False, blank=False, max_length=MAX_NAME_LEN, unique=True)
    rules = models.TextField(null=False, blank=False)
    min_players = models.PositiveIntegerField(null=False, blank=False)
    max_players = models.PositiveIntegerField(null=False, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=False)
    valid_locations = models.ManyToManyField(Location)

    def __str__(self) -> str:
        return self.name

    def get_sport_locations(self):
        return self.valid_locations.all()

    def location_in_sport(self, location: Location) -> bool:
        return self.valid_locations.filter(id=location.id).exists()

class Team(models.Model):
    name = models.CharField(null=False, blank=False, max_length=MAX_NAME_LEN)
    
    # if a league is deleted, the team apart of that league should also be deleted.
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    player = models.ManyToManyField(UserProfile)
    wins = models.PositiveIntegerField(null=False, blank=False, default=0)
    losses = models.PositiveIntegerField(null=False, blank=False, default=0)

    def __str__(self) -> str:
        return self.name + ' (' + self.league.name + ')'

    def refresh_wins_losses(self):
        """
        This is an important method to use to make sure you have the proper wins and loses.

        We track the wins and losses via the games. Using this method refresh the wins & loses.
        """
        self.wins, self.losses, ties = self.get_current_wins_and_losses_ties()
        self.save()
        return self

    @classmethod
    def get_active_teams(cls):
        current_year = now().year
        current_season = League.get_season_name()
        range_start = League.SEASON_RANGE[current_season][0]
        range_end = League.SEASON_RANGE[current_season][1]

        # if it's within the same current year and within the same season.
        query = Q(league__start_date__year=current_year)

        query.add(Q(league__start_date__month__gte=range_start), Q.AND)
        query.add(Q(league__start_date__month__lte=range_end), Q.AND)

        return cls.objects.filter(query)

    def query_for_all_games(self) -> Q:
        return Q(team1=self) | Q(team2=self)

    def get_current_games(self):
        if self.is_active():
            query = self.query_for_all_games()
            return Game.objects.filter(query)
        return None
    
    def get_past_games(self):
        query = self.query_for_all_games()
        # query.add()
        
        return Game.objects.filter(query)

    def get_current_wins_and_losses_ties(self):
        loss_count = 0
        win_count = 0
        ties = 0
        if self.is_active():
            games = self.get_current_games()
            for game in games:
                if game.score1 == game.score2 == 0:
                    continue # skip future games
                if self == game.team1:
                    if game.score1 > game.score2:
                        win_count += 1
                    elif game.score1 == game.score2:
                        ties += 1
                    else:
                        loss_count += 1
                else:
                    if game.score2 > game.score1:
                        win_count += 1
                    elif game.score1 == game.score2:
                        ties += 1
                    else:
                        loss_count += 1
            return win_count, loss_count, ties
        return -1, -1, -1
    
    def get_current_losses(self):
        win, loss, tie = self.get_current_wins_and_losses_ties()
        return loss
    
    def get_current_wins(self):
        win, loss, tie = self.get_current_wins_and_losses_ties()
        return win

    def get_next_game(self):
        """
        FIXME THIS IS MESSED UP.
        """
        current_date = now().date()
        current_time = now().time()
        query = Q(team1=self) | Q(team2=self)
        query.add(Q(date__gte=current_date), Q.AND)
        game = Game.objects.filter(query).order_by('date').first()
        # print(self.get_past_games())
        # date_now = now().date
        # time = now().time
        return game#.filter(date__gte=date_now).order_by('date', 'time').first()
        #return self.league.get_games_per_league().first()

    @classmethod
    def get_teams(cls, active=True):
        if active:
            return cls.get_active_teams()
        return cls.objects.all()

    @classmethod
    def get_player_teams(cls, player: UserProfile, active=True):
        if active:
            return cls.get_teams(active).filter(player=player)
        return cls.objects.filter(player=player)

    @classmethod
    def get_first_player_team(cls, player: UserProfile, active=True):
        fp = cls.get_player_teams(player=player, active=active).first()
        if fp != None:
            fp.refresh_wins_losses()
        return fp

    def get_team_members(self):
        return self.player.all()

    def get_upcoming_games(self):
        """
        :return: dictionary of games in the future from now

        key: game object
            value: [win,lose]
        """
        current_date = now().date()
        current_time = now().time()
        query = Q(team1=self) | Q(team2=self)
        query.add(Q(date__gte=current_date), Q.AND)
        games = Game.objects.filter(query).order_by('date')
        upcoming_games = {}
        for game in games:
            if game.team1 == self:
                opponent_win_loss = [game.team2.name, game.team2.get_current_wins(), game.team2.get_current_losses()]
            else:
                opponent_win_loss = [game.team1.name, game.team1.get_current_wins(), game.team1.get_current_losses()]
            
            if game.date != current_date:
                upcoming_games[game] = opponent_win_loss
                continue
            if game.time >= current_time:
                upcoming_games[game] = opponent_win_loss
                
        return upcoming_games

    def is_active(self):
        current_year = now().year
        current_season = League.get_season_name()
        range_start = League.SEASON_RANGE[current_season][0]
        range_end = League.SEASON_RANGE[current_season][1]

        if self.league.start_date.year == current_year:
            if self.league.start_date.month >= range_start:
                if self.league.end_date.month <= range_end:
                    return True
        return False

    def join_team(self, user: UserProfile):
        self.player.add(user)
        self.save()

    def player_in_team(self, user: UserProfile) -> bool:
        return self.player.filter(id=user.id).exists()

    def number_of_players(self) -> int:
        return self.player.count()
