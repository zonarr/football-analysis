import pandas as pd

def get_club_id(club_df,club): 
    restart = False
    while True:
        if restart: #Triggers if user have to input club name again
            club=input('Input name of the club')
        id = club_df[club_df.name.str.contains(club)].reset_index() #Sees if team name contains input value
        if len(id)==0:
            print('No clubs found')
            restart=True
            continue
        if len(id)>1: #Multiple clubs found
            for name in id.name.tolist():
                print(name)
            club = input("Multiple clubs found. Input the specific name of the club or input 'q' to search for a club that is not in the following list")
            if club == 'q':
                restart=True
                continue
            while club not in id.name.tolist(): #Some club names may not be in ASCII,so have to copy and paste
                club = input('Incorrect club name. Input the name again')
        return club_df[club_df.name.str.contains(club)].reset_index().loc[0,'club_id'] #Returns club_id. Used for many functions

def tl(): #Prints out the teams in a specific league
    league_domestic ={}
    clubs = pd.read_csv('clubs.csv')
    domestic_id = clubs.domestic_competition_id.unique().tolist()
    leagues = ['Bundesliga','Russian Premier League','Turkish Super Lig','Serie A','English Premier League','Belgian Pro League','Danish Superliga','Eredivisie','Super League Greece','Primeira Liga','Scottish Premiership','La Liga','Ukranian Premier League','Ligue 1']
    for i in range(len(leagues)):
        league_domestic[leagues[i]] = domestic_id[i] #Adds relationship between domestic_id and league name
    print('Input league that you wish to see the teams of. Available leagues include:')
    for l in leagues:
        print(l)
    league = input()
    while league not in league_domestic:
        league = input('Incorrect league name. Input a league name')
    return clubs[clubs.domestic_competition_id == league_domestic[league]].name #Filteres based on league id and then returns name of football teams

def tsc(year,club,n): #Outputs the n top goal scorers for a specific year for a club (tsc = Top Scorer Club)
    restart = False
    while True:
        if restart: #If user requested to restart to input values
            year = input('Input year')
            club = input('Input name of the club')
            n = int(input('input number of scorers'))
        clubs_data = pd.read_csv('clubs.csv')
        app = pd.read_csv('appearances.csv')
        club_id = get_club_id(clubs_data,club)
        app = app[(app.player_club_id == club_id) & (app.date.str.contains(year))] #Filters data based on club and date selected by user
        app = app.groupby('player_name').goals.sum().reset_index() #Sums all goals for each player
        app = app.sort_values(by='goals',ascending = False) #Sort based on goals
        if len(app)==0: #Check if there are no rows in the series
            print("Data doesn't exist")
            restart = True
            continue
        players = app.player_name.tolist()[0:n] #Chooses n rows of data to output
        goals = app.goals.tolist()[:n]
        for i in range(n):
            print(f'{players[i]} : {goals[i]} goals scored')
        break

def h2h(): #Outputs the game statistics between two teams
    clubs = pd.read_csv('clubs.csv')
    club_games = pd.read_csv('club_games.csv')
    club_1 = input('Input name for club 1')
    club_id1 = get_club_id(clubs,club_1)
    club_2 = input('Input name for club 2')
    club_id2 = get_club_id(clubs,club_2)
    club_games = club_games[(club_games.club_id == club_id1) & (club_games.opponent_id == club_id2)] #Filters matche to 2 selected teams
    club1wins = club_games[club_games.is_win == 1].game_id.count() #Counts number of wins of club 1
    club2wins = club_games[club_games.is_win == 0].game_id.count() #Counts number of wins of club 2
    goal_scored = club_games.own_goals.sum() #Sums total goals scored for club 1
    enemy_scored = club_games.opponent_goals.sum() #Sum total goals scored for club 2
    draw = len(club_games[club_games.own_goals == club_games.opponent_goals]) #Filter by goals scored by both teams are equal, then count number of occurences
    return f'''\n{club_1}:
    Wins = {club1wins}
    Total Goals Scored = {int(goal_scored)}
{club_2}:
    Wins = {club2wins}
    Total Goals Scored = {int(enemy_scored)}
    
Number of draws for games played between the two clubs : {draw}\n''' #Returns data in easy to read format

def club_market_value(df): #df is player_valuations.csv. Used in cs() function
    df = df.groupby('current_club_id').market_value_in_eur.sum().reset_index() #Groups by club, then sums value of all players with for a club. reset index to prepare merging with another dataframe
    df = df.rename(columns={'current_club_id':'club_id'}) #rename column to prepare merging
    return df

def cs():
    clubs = pd.read_csv('clubs.csv')
    player_valuation = pd.read_csv('player_valuations.csv')
    player_valuation = club_market_value(player_valuation)
    combine = clubs.merge(player_valuation,how = 'inner') #Merges both dataframes to allow easier filtering
    combine = combine.drop(['coach_name','filename','url','total_market_value'],axis=1) # Drops columns with no/irreleveant data
    combine.rename(columns={'market_value_in_eur':'total_market_value_eur',},inplace=True) #makes column name more accurate
    combine = combine.set_index('club_id') #allows data to be obtained easier
    stat = combine.columns.tolist()
    request ={}
    n = input('How many clubs do you want to view')
    for i in range(int(n)):
        club_id = get_club_id(clubs,input('Enter the name of the club'))
        request[club_id] = {'name':None,'last_season':None} #automatically obtains name of club and data of statistics for the club
        print(' the avaliable statistics that can be viewed are as follow:')
        for s in stat:
            if s=='name' or s=='last_season' or s=='club_code' or s=='domestic_competition_id': #Hides info that is necessary but isn't accessible to user
                continue
            print(s)
        print('q (done adding statistics for team)')
        req = input()
        while req!='q': #checks if input is valid for a specific statistic
            if req not in stat:
                print('Incorrect statistic input. Enter statistic input again')
                req=input()
                continue
            request[club_id][req] = None #Assign statistic to None, which will then be replaced with statistics from data
            req=input()
    for k in request:
        for r in request[k]:
            request[k][r] = combine.loc[k,r] #Searches for data by using name of index and column
    return request
    
def nice_arrangement(d): #Function that arranges two parts of the text nicely with 'Input Function'by aligning the beginning of each word together and capitalsing
    for k in d:
        d[k] = (' '*(6-len(k))+d[k].capitalize())
    return d

print('Data as of 12/11/2024')
while True: #Used to loop so that users can run as many functions as they want, until they are done which then they can input 'q'
    user_manual = nice_arrangement({'tl':'outputs teams from a specific league','tsc':'outputs the n top goal scorers for a specific year for a club',\
                   'h2h':'outputs the game statistics between two teams','cs':'gives the requested statistics for each club','q':'quits the program'}) #Gives info for functions and what to input into program
    print('Input Function')
    for k in user_manual:
        print(f'{k}{user_manual[k]}')
    decision = input()
    if decision == 'q': #If and elifs below used to run function that user wants to run
        print('Ending program')
        break
    elif decision == 'tl':
        print(tl())
    elif decision == 'tsc':
        year = input('Input year')
        club = input('Input name of the club')
        num = int(input('input number of scorers'))
        tsc(year,club,num)
    elif decision == 'h2h':
        print(h2h())
    elif decision == 'cs':
        club_stat = cs()
        for d in club_stat.values():
            for k in d:
                if k == 'last_season':
                    print(f'Data from year : {d[k]}')
                    continue
                print(f'{k} : {d[k]}')
            print('\n') #Allows output to be easier to read by seprarting lines
    else: #if input doesn't match with required keywords
        print('invalid input')

