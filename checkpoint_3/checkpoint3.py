import sqlite3 
from sqlite3 import Error

def openConnection(_dbFile):
    print("++++++++++++++++++++++++++++++++++")
    print("Open Database: ", _dbFile)

    conn = None
    try:
        conn = sqlite3.connect(_dbFile)
        print ("Connection Established!")

    except Error as e:
        print(e)
    
    return conn

def closeConnection(_conn, _dbFile):
    print("++++++++++++++++++++++++++++++++++")
    print("Close database: ", _dbFile)

    try:
        _conn.close()
        print("Connection Closed!")
    except Error as e:
        print(e)

    print("++++++++++++++++++++++++++++++++++")

def view_all_players(_conn):
    print("++++++++++++++++++++++++++++++++++")
    print("All Players: ")

def view_specific_player(_conn, player_name):
    print("++++++++++++++++++++++++++++++++++")
    print(f"Player Details for: {player_name}")
    try:
        cur = _conn.cursor()
        
        sql = """
            SELECT 
                p.name, 
                p.sport, 
                p.number,
                ps.points_per_game, 
                ps.assists_per_game, 
                ps.rebounds_per_game, 
                ps.batting_avg, 
                ps.lifetime_hits, 
                ps.lifetime_rbi, 
                ps.lifetime_yards, 
                ps.lifetime_td, 
                ps.lifetime_intercept, 
                ps.goals_scored, 
                ps.lifetime_assists, 
                ps.shots_on_target
            FROM Player p
            LEFT JOIN PlayerStats ps ON p.player_id = ps.player_id
            WHERE p.name = ?;
        """
        cur.execute(sql, (player_name,))
        row = cur.fetchone()

        if row:
            print(f"Name: {row[0]}")
            print(f"Sport: {row[1]}")
            print(f"Number: {row[2]}")
            sport = row[1].lower()

            if sport == 'basketball':
                print(f"Points/Game: {row[3]}")
                print(f"Assists/Game: {row[4]}")
                print(f"Rebounds/Game: {row[5]}")
            elif sport == 'baseball':
                print(f"Batting Average: {row[6]}")
                print(f"Lifetime Hits: {row[7]}")
                print(f"Lifetime RBI: {row[8]}")
            elif sport == 'football':
                print(f"Lifetime Yards: {row[9]}")
                print(f"Lifetime Touchdowns: {row[10]}")
                print(f"Lifetime Interceptions: {row[11]}")
            elif sport == 'soccer':
                print(f"Goals Scored: {row[12]}")
                print(f"Lifetime Assists: {row[13]}")
                print(f"Shots on Target: {row[14]}")
            else:
                print("No specific stats available for this sport.")
        else:
            print("Player not found.")

    except Error as e:
        print("Error viewing player:", e)

    print("++++++++++++++++++++++++++++++++++")

def view_all_players_on_team(_conn, team_name):
    print("++++++++++++++++++++++++++++++++++")
    print(f"Players on the {team_name}")
    print("--------------------------------------")
    try:
        cur = _conn.cursor()

        # Query to get players on the specified team
        sql2 = """
            SELECT p.player_id, p.name, p.sport, p.number
            FROM Player p
            JOIN Team t ON p.team_id = t.team_id
            WHERE t.team_name = ?;
        """
        cur.execute(sql2, (team_name,))
        player_rows = cur.fetchall()

        if player_rows:
            print("Name         | Number")
            print("--------------------------------------")
            for row in player_rows:
                print(f"{row[1]:<12} | {row[3]:<13}")
        else:
            print("No players found for this team.")

        # Query to get the coach of the specified team
        sql3 = """
            SELECT c.coach_id, c.name
            FROM Coach c
            JOIN Team t ON t.team_id = c.team_id
            WHERE t.team_name = ?;
        """
        cur.execute(sql3, (team_name,))
        coach_row = cur.fetchone()  # Expect only one coach per team

        if coach_row:
            print("\nCoach:")
            print("--------------------------------------")
            print(f"Name: {coach_row[1]}")
        else:
            print("\nNo associated coach for this team.")

    except Error as e:
        print("Error viewing players and coach:", e)

    print("++++++++++++++++++++++++++++++++++")


def main():
    database = r"Checkpoint2-dbase.db"
    conn = openConnection(database)

    while True:
        print("Options:\n")
        print("1 - View Players, Teams, and Coaches\n")
        print("2 - Add a Player\n")
        print("3 - Remove a Player\n")
        print("4 - Update Player Stats\n")
        print("5 - Close Connection\n")

        input_1 = input("Please Select an option: ")
        if (input_1 == '1'):
            print("Viewing Options: \n")
            print("1 - Specific Player\n")
            print("2 - Team Roster\n")

            view_input = input("Please select an option: ")
            if (view_input == '1'):
                player_input = input("Who would you like to view? ")
                view_specific_player(conn, player_input)
            
            elif (view_input == '2'):
                player_input2 = input("Which team would you like to view? ")
                view_all_players_on_team(conn, player_input2)

        else:
            if ( input_1 == '5'):
                closeConnection(conn, database)
                break


if __name__ == '__main__':
    main()