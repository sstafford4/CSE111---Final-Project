from flask import request, url_for, render_template, redirect, flash
from config import app, db
from models import League, Team, Player, PlayerStats, Coach, Sport, SportCoaches
from sqlalchemy.orm import joinedload

app.secret_key = 'my_secret_key'

# this first route will take the user to the main hub
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/basketball_view', methods=['GET', 'POST'])
def basketball_view():
    leagues = League.query.filter_by(sport="Basketball").all()
    print (leagues)

    return render_template("basketball_view.html", leagues=leagues)

@app.route('/baseball_view', methods=['GET', 'POST'])
def baseball_view():
    leagues = League.query.filter_by(sport="Baseball").all()

    return render_template("baseball_view.html", leagues=leagues)


@app.route('/football_view', methods=['GET', 'POST'])
def football_view():
    leagues = League.query.filter_by(sport="Football").all()

    return render_template("football_view.html", leagues=leagues)

@app.route('/add_new_league', methods=['GET', 'POST'])
def add_new_league():
    if request.method == 'POST':
        league_name = request.form.get('league_name')
        league_sport = request.form.get('league_sport')

        existing_league = League.query.filter_by(league_name=league_name).first()
        if existing_league:
            flash("League already exists in database", "error")
        else:
            new_league = League(league_name=league_name, sport=league_sport)
            db.session.add(new_league)  # Add the new league
            db.session.commit()  # Commit changes to the database
            flash("League Created!", "success")

            return redirect(url_for('index'))  # Redirect after processing

    return render_template("add_new_league.html")  # Render form for GET requests 

@app.route('/league_teams/<int:league_id>')
def league_teams(league_id):
    league = League.query.get_or_404(league_id)
    teams = Team.query.filter_by(league_id=league_id).all()
    return render_template("league_view.html", league=league, teams=teams)

@app.route('/add_new_team/<int:league_id>', methods=['GET', 'POST'])
def add_new_team(league_id):
    league = League.query.get_or_404(league_id)
    
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        team_city = request.form.get('team_city')

        # Check if the team already exists
        existing_team = Team.query.filter_by(team_name=team_name, league_id=league_id).first()
        if existing_team:
            flash("Team Already Exists!", "error")
            return redirect(f"/add_new_team/{league_id}")
        else:
            # Create a new team
            new_team = Team(team_name=team_name, city=team_city, league_id=league_id)
            db.session.add(new_team)
            db.session.commit()
            flash("New Team Added!", "success")
            return redirect(f"/league_teams/{league_id}")
    
    # Render the form page for GET requests
    return render_template("add_new_team.html", league=league)

@app.route('/team_view/<int:team_id>')
def team_view(team_id):
    # Use joinedload to eagerly load the coach relationship
    team = Team.query.options(joinedload(Team.coach)).get_or_404(team_id)
    players = Player.query.filter_by(team_id=team_id).all()
    player_data = []

    for player in players:
        stats = player.stats  # Access the relationship to PlayerStats
        player_data.append({
            'name': player.name,
            'number': player.number,
            'stats': stats,  # Can be None if no stats exist
            'player_id': player.player_id
        })

    return render_template(
        "team_view.html",
        team=team,
        player_data=player_data,
        sport=team.league.sport
    )


@app.route('/add_new_player/<int:team_id>', methods=['GET', 'POST'])
def add_new_player(team_id):
    team = Team.query.get_or_404(team_id)

    if request.method == 'POST':
        player_name = request.form.get('player_name')
        player_number = request.form.get('player_number')
        sport = team.league.sport

        # Create the new player
        new_player = Player(name=player_name, sport=sport, team_id=team_id, number=player_number)
        db.session.add(new_player)
        db.session.commit()

        # Add a new entry to the Sport table for the player
        new_player_sport = Sport(player_id=new_player.player_id, sport_name=sport, player_name=player_name)
        db.session.add(new_player_sport)
        db.session.commit()

        # Add sport-specific stats if provided
        stats_data = {
            'Basketball': ['points_per_game', 'assists_per_game', 'rebounds_per_game'],
            'Baseball': ['batting_avg', 'lifetime_hits', 'lifetime_rbi'],
            'Football': ['lifetime_yards', 'lifetime_td', 'lifetime_intercept'],
            'Soccer': ['goals_scored', 'assists', 'shots_on_target']
        }
        stat_fields = stats_data.get(sport, [])
        player_stats = {field: request.form.get(field) for field in stat_fields if request.form.get(field)}

        if player_stats:
            new_stats = PlayerStats(player_id=new_player.player_id, **player_stats)
            db.session.add(new_stats)
            db.session.commit()

        flash(f"{player_name} added to {team.team_name}!", "success")
        return redirect(url_for('team_view', team_id=team_id))

    return render_template("add_new_player.html", team=team, sport=team.league.sport)


@app.route('/edit_player/<int:player_id>', methods=['GET', 'POST'])
def edit_player(player_id):
    player = Player.query.filter_by(player_id=player_id).first()
    sport = player.team.league.sport

    if request.method == 'POST':
        player.name = request.form.get('player_name')
        player.number = request.form.get('player_number')
        
        if player.stats:
            if sport == "Basketball":
                player.stats.points_per_game = request.form.get('points_per_game')
                player.stats.assists_per_game = request.form.get('assists_per_game')
                player.stats.rebounds_per_game = request.form.get('rebounds_per_game')
            elif sport == "Baseball":
                player.stats.batting_avg = request.form.get('batting_avg')
                player.stats.lifetime_hits = request.form.get('lifetime_hits')
                player.stats.lifetime_rbi = request.form.get('lifetime_rbi')
            elif sport == "Football":
                player.stats.lifetime_yards = request.form.get('yards')
                player.stats.lifetime_td = request.form.get('touchdowns')
                player.stats.lifetime_intercept = request.form.get('interceptions')
            elif sport == "Soccer":
                player.stats.goals_scored = request.form.get('goals_scored')
                player.stats.lifetime_assists = request.form.get('assists')
                player.stats.shots_on_target = request.form.get('shots_on_target')

        db.session.commit()
        flash("Player information updated successfully!", "success")
        return redirect(url_for('team_view', team_id=player.team.team_id))

    return render_template("edit_player.html", player=player, sport=sport)

@app.route('/add_new_coach/<int:team_id>', methods=['GET', 'POST'])
def add_new_coach(team_id):
    team = Team.query.get_or_404(team_id)

    if request.method == 'POST':
        coach_name = request.form.get('coach_name')
        experience_years = request.form.get('experience_years')

        existing_coach = Coach.query.filter_by(team_id=team_id).first()
        if existing_coach:
            flash(f"{team.team_name} already has a coach assigned!", "error")
            return redirect(url_for('team_view', team_id=team_id))

        # Create a new coach
        new_coach = Coach(name=coach_name, experience_years=experience_years, team_id=team_id)
        db.session.add(new_coach)
        db.session.commit()

        league = team.league 
        if not league:
            flash(f"Team {team.team_name} does not belong to a league. Cannot assign sport.", "error")
            return redirect(url_for('team_view', team_id=team_id))

        sport_name = league.sport 
        sport = Sport.query.filter_by(sport_name=sport_name).first()

        if not sport:
            flash(f"Sport '{sport_name}' is not registered in the database.", "error")
            return redirect(url_for('team_view', team_id=team_id))

        # Add the coach to the SportCoaches table
        new_sport_coach = SportCoaches(
            sport_id=sport.sport_id,
            coach_id=new_coach.coach_id,
            sport_name=sport.sport_name,
            coach_name=coach_name
        )
        db.session.add(new_sport_coach)
        db.session.commit()

        flash(f"Coach {coach_name} assigned to {team.team_name} and added to SportCoaches!", "success")
        return redirect(url_for('team_view', team_id=team_id))

    return render_template("add_new_coach.html", team=team)


@app.route('/delete_player/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    player = Player.query.get_or_404(player_id)
    
    team_id = player.team.team_id

    db.session.delete(player)
    db.session.commit()

    flash("Player deleted successfully!", "success")
    return redirect(url_for('team_view', team_id=team_id))

@app.route('/search', methods=['GET', 'POST'])
def search():
    search_query = ""
    results = {
        'players': [],
        'teams': [],
        'leagues': [],
        'coaches': [],
        'sports': [],
        'sportcoaches': []
    }

    if request.method == 'POST':
        search_query = request.form.get('search_query')

        if (search_query and search_query.lower() in ['all players', 'players']) or (search_query and search_query.lower() in ['basketball coaches', 'coaches basketball']) or (search_query and search_query.lower() in ['football coaches', 'coaches football']):
            
            if search_query.lower() in ['all players', 'players']:
                results['players'] = (
                    db.session.query(Player, PlayerStats)
                    .outerjoin(PlayerStats, Player.player_id == PlayerStats.player_id)
                    .all()
                )
            elif search_query.lower() in ['basketball coaches', 'coaches basketball']:
                results['sportcoaches'] = (
                db.session.query(SportCoaches)
                .join(Coach, SportCoaches.coach_id == Coach.coach_id)
                .filter(SportCoaches.sport_name.ilike('Basketball')) 
                .all()
            )
            elif search_query.lower() in ['football coaches', 'coaches football']:
                results['sportcoaches'] = (
                db.session.query(SportCoaches)
                .join(Coach, SportCoaches.coach_id == Coach.coach_id)
                .filter(SportCoaches.sport_name.ilike('Football'))
                .all()
            )


        elif search_query:
            results['players'] = (
                db.session.query(Player, PlayerStats)
                .outerjoin(PlayerStats, Player.player_id == PlayerStats.player_id)
                .filter(Player.name.ilike(f"%{search_query}%"))
                .all()
            )
            results['teams'] = (
                db.session.query(Team, Coach, League)
                .outerjoin(Coach, Team.team_id == Coach.team_id)
                .outerjoin(League, Team.league_id == League.league_id)
                .filter(Team.team_name.ilike(f"%{search_query}%"))
                .all()
            )
            results['leagues'] = League.query.filter(League.league_name.ilike(f"%{search_query}%")).all()
            results['coaches'] = Coach.query.filter(Coach.name.ilike(f"%{search_query}%")).all()
            results['sports'] = Sport.query.filter(Sport.sport_name.ilike(f"%{search_query}%")).all()

    return render_template("search.html", results=results, search_query=search_query)


if __name__ == '__main__':
    with app.app_context():
        db.create_all() 

    app.run(debug=True)
