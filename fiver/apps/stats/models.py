import json

from collections import Counter
from datetime import date, datetime

from django.db import models


class League(models.Model):
    league_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    roster_size = models.IntegerField()
    injured_reserve = models.IntegerField()
    taxi_squad = models.IntegerField()
    start_year = models.IntegerField()


class Division(models.Model):
    division_id = models.CharField(max_length=255)
    league = models.ForeignKey(League)
    name = models.CharField(max_length=255)


class Player(models.Model):
    player_id = models.IntegerField(primary_key=True)
    birthdate = models.IntegerField(blank=True, null=True)
    college = models.CharField(max_length=255, blank=True, null=True)
    draft_pick = models.IntegerField(blank=True, null=True)
    draft_round = models.IntegerField(blank=True, null=True)
    draft_team = models.CharField(max_length=255, blank=True, null=True)
    draft_year = models.IntegerField(blank=True, null=True)
    espn_id = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    jersey = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    team = models.CharField(max_length=255, blank=True, null=True)
    twitter_username = models.CharField(max_length=255, blank=True, null=True)
    adp = models.FloatField(blank=True, null=True)
    dynasty_adp = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.name

    def franchise(self, league_id):
        try:
            fp = FranchisePlayer.objects.get(
                franchise__league__league_id=league_id,
                player=self,
            )
            return fp.franchise
        except FranchisePlayer.DoesNotExist:
            return None

    @property
    def height_cm(self):
        return self.height * 2.54

    @property
    def weight_kg(self):
        return self.weight * 0.453592

    @property
    def draft_round_or_undrafter(self):
        return self.draft_round or "Undrafted"

    @property
    def age(self):
        today = date.today()
        if self.birthdate:
            born = datetime.fromtimestamp(float(self.birthdate))
            age = (
                today.year -
                born.year -
                ((today.month, today.day) < (born.month, born.day))
            )
            return age
        return None


class Franchise(models.Model):
    franchise_id = models.CharField(max_length=4)
    name = models.CharField(max_length=255)
    division = models.ForeignKey(Division)
    league = models.ForeignKey(League)
    players = models.ManyToManyField(Player, through="FranchisePlayer")

    def __str__(self):
        return self.name

    def player(self, position, rank, ordering='-average_points'):
        try:
            return FranchisePlayerPoints.objects.filter(
                franchise_player__player__position=position
            ).order_by(
                ordering
            )[rank]
        except IndexError:
            return None

    def place(self, position, rank, ordering='-average_points'):
        ids = [f.player(
            position, rank, ordering
        ).franchise_player.player.player_id for f in Franchise.objects.all()]
        players = FranchisePlayerPoints.objects.filter(
            franchise_player__player__player_id__in=ids
        ).order_by(ordering)
        field = ''.join(ordering.split('-'))
        kwargs = {field + '__gte': getattr(
            self.player(position, rank, ordering), field
        )}
        index = players.filter(**kwargs).count()
        return index

    def age_distribution(self, position=None):
        """
        Returns the age distribution for the franchise
        """
        player_stats = []
        players = self.franchise_players.exclude(
            player__birthdate__isnull=True
        )
        if position:
            players = players.filter(player__position=position)
        for player in players:
            player_stats.append(player.player.age)
        age_distribution = Counter(player_stats).most_common()
        for i in range(20):
            if i + 20 not in dict(age_distribution):
                age_distribution.append((i + 20, 0))
        return json.dumps(sorted(age_distribution))

    def college_distribution(self, position=None):
        player_stats = []
        players = self.franchise_players.exclude(player__college__isnull=True)
        if position:
            players = players.filter(player__position=position)
        for player in players:
            college = player.player.college
            player_stats.append(college)
        college_distribution = Counter(player_stats).most_common()
        return json.dumps(sorted(college_distribution))

    def draft_round_distribution(self, position=None):
        player_stats = []
        players = self.franchise_players.exclude(player__position="DEF")
        if position:
            players = players.filter(player__position=position)
        for player in players:
            if player.player.draft_round:
                draft_round = str(player.player.draft_round)
            else:
                draft_round = "Undrafted"
            player_stats.append(draft_round)
        draft_round_distribution = Counter(player_stats).most_common()
        for i in range(7):
            if str(i + 1) not in dict(draft_round_distribution):
                draft_round_distribution.append((str(i + 1), 0))
        if "Undrafted" not in dict(draft_round_distribution):
            draft_round_distribution.append(("Undrafted", 0))
        return json.dumps(sorted(draft_round_distribution))

    def weight_height_distribution(self, position=None):
        player_stats = []
        players = self.franchise_players.exclude(player__weight__isnull=True)
        if position:
            players = players.filter(player__position=position)
        for player in players:
            try:
                weight = player.player.weight * 0.453592
                height = player.player.height * 2.54
            except KeyError:
                continue
            player_stats.append({'x': weight, 'y': height, 'r': 5})
        return json.dumps(player_stats)


class FranchisePlayer(models.Model):
    franchise = models.ForeignKey(Franchise, related_name="franchise_players")
    player = models.ForeignKey(Player)

    @property
    def name(self):
        return self.player.name

    @property
    def height_cm(self):
        return self.player.height_cm

    @property
    def weight_kg(self):
        return self.player.weight_kg

    @property
    def average_points(self):
        return self.points.last().average_points

    @property
    def total_points(self):
        return self.points.last().total_points

    @property
    def games(self):
        return int(round(self.total_points / self.average_points))


class FranchisePlayerPoints(models.Model):
    franchise_player = models.ForeignKey(
        FranchisePlayer,
        related_name="points"
    )
    year = models.IntegerField()
    average_points = models.FloatField(blank=True, null=True)
    total_points = models.FloatField(blank=True, null=True)

    @property
    def name(self):
        return self.franchise_player.player.name

    @property
    def games(self):
        return int(round(self.total_points / self.average_points))


class Pick(models.Model):
    draft_year = models.IntegerField()
    draft_round = models.IntegerField()
    franchise = models.ForeignKey(Franchise, related_name="original_picks")
    current_franchise = models.ForeignKey(
        Franchise,
        related_name="current_picks"
    )
    draft_pick = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return '{} ({}) ({})'.format(
            self.draft_year,
            self.draft_round,
            self.franchise.name
        )


class Trade(models.Model):
    franchises = models.ManyToManyField(Franchise, through="TradeOffer")
    timestamp = models.IntegerField()
    accepted = models.BooleanField()


class TradeOffer(models.Model):
    franchise = models.ForeignKey(Franchise, related_name="tradeoffers")
    trade = models.ForeignKey(Trade)
    players = models.ManyToManyField(Player, related_name="trades")
    picks = models.ManyToManyField(Pick)
    is_initiator = models.BooleanField()

    @property
    def other_franchise(self):
        return TradeOffer.objects.get(
            trade=self.trade,
            is_initiator=not self.is_initiator
        )

    @property
    def giving_up(self):
        players_and_picks = []
        for player in self.players.all():
            players_and_picks.append(player.name)
        for pick in self.picks.all():
            players_and_picks.append(pick.__str__())
        return players_and_picks

    @property
    def receiving(self):
        players_and_picks = []
        for player in self.other_franchise.players.all():
            players_and_picks.append(player.name)
        for pick in self.other_franchise.picks.all():
            players_and_picks.append(pick.__str__())
        return players_and_picks

    @property
    def date(self):
        return datetime.fromtimestamp(float(self.trade.timestamp))

    class Meta:
        ordering = ('trade__timestamp', )


class Result(models.Model):
    franchise = models.ForeignKey(Franchise, related_name='results')
    players = models.ManyToManyField(Player, through="PlayerResult")
    opponent = models.ForeignKey(Franchise, blank=True, null=True)
    week = models.IntegerField()
    year = models.IntegerField()
    result = models.CharField(max_length=10)
    points = models.FloatField(blank=True, null=True)


class PlayerResult(models.Model):
    result = models.ForeignKey(Result)
    player = models.ForeignKey(Player)
    started = models.BooleanField()
    should_have_started = models.BooleanField()
    points = models.FloatField(default=0.0)


class PlayerDraft(models.Model):
    franchise = models.ForeignKey(Franchise)
    player = models.ForeignKey(Player, related_name="drafts")
    timestamp = models.IntegerField(blank=True, null=True)
    bid_amount = models.IntegerField(blank=True, null=True)
    draft_round = models.IntegerField(blank=True, null=True)
    draft_pick = models.IntegerField(blank=True, null=True)
    draft_year = models.IntegerField()

    @property
    def date(self):
        return datetime.fromtimestamp(float(self.timestamp))

    class Meta:
        ordering = ('-bid_amount', 'draft_round', 'draft_pick')


class Waiver(models.Model):
    franchise = models.ForeignKey(Franchise)
    player = models.ForeignKey(Player, related_name="waivers")
    timestamp = models.IntegerField()
    amount = models.IntegerField(default=0)
    free_agent = models.BooleanField()
    adding = models.BooleanField()

    @property
    def date(self):
        return datetime.fromtimestamp(float(self.timestamp))

    class Meta:
        ordering = ('-timestamp', )
