import json

from collections import Counter
from datetime import date, datetime

from django.db import models


class Franchise(models.Model):
    franchise_id = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=255)

    def player(self, position, rank, ordering='-average_points'):
        try:
            return self.players.filter(
                position=position
            ).order_by(
                ordering
            )[rank]
        except IndexError:
            return None

    def place(self, position, rank, ordering='-average_points'):
        ids = [
            f.player(
                position, rank, ordering
            ).player_id for f in Franchise.objects.all()
        ]
        players = Player.objects.filter(
            player_id__in=ids
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
        players = self.players.exclude(birthdate__isnull=True)
        if position:
            players = players.filter(position=position)
        for player in players:
            player_stats.append(player.age)
        age_distribution = Counter(player_stats).most_common()
        for i in range(20):
            if i + 20 not in dict(age_distribution):
                age_distribution.append((i + 20, 0))
        return json.dumps(sorted(age_distribution))

    def college_distribution(self, position=None):
        player_stats = []
        players = self.players.exclude(college__isnull=True)
        if position:
            players = players.filter(position=position)
        for player in players:
            college = player.college
            player_stats.append(college)
        college_distribution = Counter(player_stats).most_common()
        return json.dumps(sorted(college_distribution))

    def draft_round_distribution(self, position=None):
        player_stats = []
        players = self.players.exclude(position="DEF")
        if position:
            players = players.filter(position=position)
        for player in players:
            if player.draft_round:
                draft_round = str(player.draft_round)
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
        players = self.players.exclude(weight__isnull=True)
        if position:
            players = players.filter(position=position)
        for player in players:
            try:
                weight = player.weight * 0.453592
                height = player.height * 2.54
            except KeyError:
                continue
            player_stats.append({'x': weight, 'y': height, 'r': 5})
        return json.dumps(player_stats)


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
    average_points = models.FloatField(blank=True, null=True)
    total_points = models.FloatField(blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    team = models.CharField(max_length=255, blank=True, null=True)
    twitter_username = models.CharField(max_length=255, blank=True, null=True)
    franchise = models.ForeignKey(
        Franchise,
        related_name="players",
        blank=True,
        null=True
    )
    adp = models.FloatField(blank=True, null=True)
    dynasty_adp = models.FloatField(blank=True, null=True)

    @property
    def games(self):
        return int(round(self.total_points / self.average_points))

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

    @property
    def readable_name(self):
        return " ".join(self.name.split(", ")[::-1])


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
    players = models.ManyToManyField(Player)
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
    player = models.ForeignKey(Player)
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
    player = models.ForeignKey(Player)
    timestamp = models.IntegerField()
    amount = models.IntegerField(default=0)
    free_agent = models.BooleanField()
    adding = models.BooleanField()

    @property
    def date(self):
        return datetime.fromtimestamp(float(self.timestamp))

    class Meta:
        ordering = ('-timestamp', )
