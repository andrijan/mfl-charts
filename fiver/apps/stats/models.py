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
        kwargs = {field + '__gte': getattr(self.player(position, rank), field)}
        index = players.filter(**kwargs).count()
        return index


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
    franchise = models.ForeignKey(Franchise, related_name="players")

    @property
    def games(self):
        return int(round(self.total_points / self.average_points))
