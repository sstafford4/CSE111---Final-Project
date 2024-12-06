from config import app, db

class League(db.Model):
    __tablename__ = 'league'

    league_id = db.Column(db.Integer, primary_key=True)
    league_name = db.Column(db.String(50), nullable=False)
    sport = db.Column(db.String(50), nullable=False)

    teams = db.relationship("Team", back_populates="league", cascade="all, delete", lazy=True)

class Team(db.Model):
    __tablename__ = 'team'

    team_id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    league_id = db.Column(db.Integer, db.ForeignKey('league.league_id', ondelete="CASCADE"))

    league = db.relationship("League", back_populates="teams")
    players = db.relationship("Player", back_populates="team", cascade="all, delete", lazy=True)
    coach = db.relationship("Coach", back_populates="team", uselist=False)

class Player(db.Model):
    __tablename__ = 'player'

    player_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    sport = db.Column(db.String(50), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.team_id', ondelete="CASCADE"))
    number = db.Column(db.Integer, nullable=False)

    team = db.relationship("Team", back_populates="players")
    stats = db.relationship("PlayerStats", back_populates="player", cascade='all, delete-orphan', uselist=False)

class Coach(db.Model):
    __tablename__ = 'coach'

    coach_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.team_id', ondelete="SET NULL"), unique=True)
    experience_years = db.Column(db.Integer, nullable=False)

    team = db.relationship("Team", back_populates="coach")

class PlayerStats(db.Model):
    __tablename__ = 'player_stats'

    player_id = db.Column(db.Integer, db.ForeignKey('player.player_id', ondelete="CASCADE"), primary_key=True)
    points_per_game = db.Column(db.DECIMAL(4, 2))
    assists_per_game = db.Column(db.DECIMAL(4, 2))
    rebounds_per_game = db.Column(db.DECIMAL(4, 2))
    batting_avg = db.Column(db.DECIMAL(3, 3))
    lifetime_hits = db.Column(db.Integer)
    lifetime_rbi = db.Column(db.Integer)
    lifetime_yards = db.Column(db.Integer)
    lifetime_td = db.Column(db.Integer)
    lifetime_intercept = db.Column(db.Integer)
    goals_scored = db.Column(db.Integer)
    lifetime_assists = db.Column(db.Integer)
    shots_on_target = db.Column(db.Integer)

    player = db.relationship("Player", back_populates="stats")

class Sport(db.Model):
    __tablename__ = 'sport'

    sport_id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.player_id', ondelete="CASCADE"))
    sport_name = db.Column(db.String(50), nullable=False)
    player_name = db.Column(db.String(50), nullable=False)

    player = db.relationship("Player")

class SportCoaches(db.Model):
    __tablename__ = 'sport_coaches'

    sport_id = db.Column(db.Integer, db.ForeignKey('sport.sport_id', ondelete="CASCADE"), primary_key=True)
    coach_id = db.Column(db.Integer, db.ForeignKey('coach.coach_id', ondelete="CASCADE"), primary_key=True)
    sport_name = db.Column(db.String(50), nullable=False)
    coach_name = db.Column(db.String(50), nullable=False)

    sport = db.relationship("Sport")
    coach = db.relationship("Coach", lazy="joined")