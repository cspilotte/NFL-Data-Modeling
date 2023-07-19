# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from pandasql import sqldf
import time

example_dict = {
  "Team": ['Arizona Cardinals', 'Atlanta Falcons', 'Baltimore Ravens', 'Buffalo Bills', 
           'Carolina Panthers', 'Chicago Bears', 'Cincinnati Bengals', 'Cleveland Browns', 
           'Dallas Cowboys', 'Denver Broncos', 'Detroit Lions', 'Green Bay Packers', 
           'Houston Texans', 'Indianapolis Colts', 'Jacksonville Jaguars', 
           'Kansas City Chiefs', 'Las Vegas Raiders', 'Oakland Raiders', 'Los Angeles Chargers',
           'San Diego Chargers', 'Los Angeles Rams',
           'Miami Dolphins', 'Minnesota Vikings', 'New England Patriots', 'New Orleans Saints', 
           'New York Giants', 'New York Jets', 'Philadelphia Eagles', 'Pittsburgh Steelers', 
           'San Francisco 49ers', 'Seattle Seahawks', 'Tampa Bay Buccaneers', 'Tennessee Titans', 
           'Washington Commanders', 'Washington Football Team', 'Washington Redskins'],
    
  "Team_Abbrev": ['crd', 'atl', 'rav', 'buf', 'car', 'chi', 'cin', 'cle', 'dal', 'den', 'det', 
                  'gnb', 'htx', 'clt', 'jax', 'kan', 'rai', 'rai', 'sdg', 'sdg', 'ram', 'mia', 'min', 'nwe', 
                  'nor', 'nyg', 'nyj', 'phi', 'pit', 'sfo', 'sea', 'tam', 'oti', 'was', 'was', 
                  'was'],
    
  "City_Abbrev": ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 'DET', 
                  'GNB', 'HOU', 'IND', 'JAX', 'KAN', 'LVR', 'OAK', 'LAC', 'SD', 'LAR', 'MIA', 
                  'MIN', 'NWE', 'NOR', 'NYG', 'NYJ', 'PHI', 'PIT', 'SFO', 'SEA', 'TAM', 'TEN', 
                  'WAS', 'WAS', 'WAS']
    
}

df_names = pd.concat([pd.Series(example_dict['Team'], name = 'Team'),
                      pd.Series(example_dict['Team_Abbrev'], name = 'Team_abbr'), 
                      pd.Series(example_dict['City_Abbrev'], name = 'City_abbr')], 
                      axis = 'columns')

def schedule_scraper(year):
    url = 'https://www.pro-football-reference.com/years/{}/games.htm'.format(year)
    html = urlopen(url)
    soup = BeautifulSoup(html)
    headers = [th.getText().replace('/', '_') for th in soup.findAll('tr')[0].findAll('th')] #Find the second table row tag, find every table header column within it and extract the html text via the get_text method.
    headers = headers[1:] #Do not need the first (0 index) column header
    print(headers[:5])
    rows = soup.findAll('tr', class_ = lambda table_rows: table_rows != "thead") #Here we grab all rows that are not classed as table header rows - football reference throws in a table header row everyy 30 rows 
    player_stats = [[td.getText() for td in rows[i].findAll('td')] # get the table data cell text from each table data cell
                    for i in range(len(rows))] #for each row
    player_stats = player_stats[1:]
    df_sched = pd.DataFrame(player_stats, columns = headers)
    day = []
    month = []
    year = []
    for i in df_sched['Date']:
        try:
            x = i.split('-')
            day.append(x[2])
            month.append(x[1])
            year.append(x[0])
        except:
            day.append('')
            month.append('')
            year.append('')
    df_sched['date_day'] = day
    df_sched['date_month'] = month
    df_sched['date_year'] = year
    df_sched = df_sched.drop('', axis = 'columns')
    return df_sched

def spread_scraper(team, year):
    url = 'https://www.pro-football-reference.com/teams/{team}/{year}_lines.htm'.format(team = team, year = year)
    html = urlopen(url)
    soup = BeautifulSoup(html)
    headers = [th.getText().replace('/', '') for th in soup.findAll('tr')[0].findAll('th')] #Find the second table row tag, find every table header column within it and extract the html text via the get_text method.
    headers = headers[1:] #Do not need the first (0 index) column header
    rows = soup.findAll('tr', class_ = lambda table_rows: table_rows != "thead") #Here we grab all rows that are not classed as table header rows - football reference throws in a table header row everyy 30 rows 
    player_stats = [[td.getText() for td in rows[i].findAll('td')] # get the table data cell text from each table data cell
                    for i in range(len(rows))] #for each row
    player_stats = player_stats[1:]
    df_rav = pd.DataFrame(player_stats, columns = headers)
    name = soup.findAll('h1')[0].findAll('span')[1].getText() #pull in team name
    result_w_or_l = []
    winning_score = []
    losing_score = []
    team_full = []
    team_abbr = []
    for i in df_rav['Result']:
        team_full.append(name)
        team_abbr.append(team)
        res = i.split(',')
        result_w_or_l.append(res[0])
        res1 = res[1].split('-')
        if res[0] == 'W':
            winning_score.append(res1[0])
            losing_score.append(res1[1])
        else:
            winning_score.append(res1[1])
            losing_score.append(res1[0])
    df_rav['team_abbr'] = team_abbr
    df_rav['team'] = team_full
    df_rav['result_w_or_l'] = result_w_or_l
    df_rav['winning_score'] = winning_score
    df_rav['losing_score'] = losing_score
    return (df_rav)

def depth_chart_scraper(team, year):
    url = 'https://www.pro-football-reference.com/teams/{team}/{year}_roster.htm'.format(team = team, year = year)
    html = urlopen(url)
    soup = BeautifulSoup(html)
    headers = [th.getText() for th in soup.findAll('tr')[0].findAll('th')] #Find the second table row tag, find every table header column within it and extract the html text via the get_text method.
    headers = ['Player', 'Age', 'Yrs', 'GS', 'Summary of Player Stats', 'Drafted (tm/rnd/yr)']
    print(headers[:5])
    rows = soup.findAll('tr', class_ = lambda table_rows: table_rows != "thead") #Here we grab all rows that are not classed as table header rows - football reference throws in a table header row everyy 30 rows 
    player_stats = [[td.getText() for td in rows[i].findAll('td')] # get the table data cell text from each table data cell
                    for i in range(len(rows))] #for each row
    player_stats = player_stats[2:]
    stats = pd.DataFrame(player_stats, columns = headers)
    return(stats)

def injury_report_scraper(team, year):
    url = 'https://www.pro-football-reference.com/teams/{team}/{year}_injuries.htm'.format(year = year, team = team)
    html = urlopen(url)
    soup = BeautifulSoup(html)
    headers = [th.getText() for th in soup.findAll('tr')[0].findAll('th')] #Find the second table row tag, find every table header column within it and extract the html text via the get_text method.
    player = headers[0]
    headers = headers[1:] #Do not need the first (0 index) column header
    headers1 = []
    for i in range(0, len(headers)):
        headers1.append('Week'+str(i+1))
    rows = soup.findAll('tr', class_ = lambda table_rows: table_rows != "thead") #Here we grab all rows that are not classed as table header rows - football reference throws in a table header row everyy 30 rows 
    player_stats = [[td.getText() for td in rows[i].findAll('td')] # get the table data cell text from each table data cell
                    for i in range(len(rows))] #for each row
    player_stats = player_stats[1:]
    players = []
    
    for i in soup.findAll('tr'):

        players.append(i.findAll('th')[0].getText())
    players = players[1:]
    stats = pd.DataFrame(player_stats, columns = headers1)
    stats.head()
    stats.index = players
    stats['player'] = players
    stats = stats.replace('C19', 'O')
    stats = stats.replace('//', 'O')
    return(stats)

def ir_counter(df):
    Q_season = []
    P_season = []
    O_season = []
    A_season = []
    for i in df.columns:
        Q = 0
        P = 0
        O = 0
        A = 0
        if i != 'player':
            for j in df[i]:
                if j == 'Q':
                    Q += 1
                elif j == 'P':
                    P += 1
                elif j != '':
                    O += 1
                else:
                    A += 1
            Q_season.append(Q)
            P_season.append(P)
            O_season.append(O)
            A_season.append(A)
    df_counts = pd.concat([pd.Series(Q_season, name = 'Q_count'), pd.Series(P_season, name = 'P_count'), 
                           pd.Series(O_season, name = 'O_count'), pd.Series(A_season, name = 'A_count')], 
                          axis = 'columns')
    return(df_counts)


def team_injury_report(team, year):
    time.sleep(5)
    df = depth_chart_scraper(team, year)
    players = ['Team', 'QB1', 'Skill1', 'Skill2', 'Skill3', 'Skill4', 'Skill5', 
               'Oline1', 'Oline2', 'Oline3', 'Oline4', 'Oline5',
               'Dline1', 'Dline2', 'Dline3',
               'LB1', 'LB2', 'LB3', 'LB4',
               'CB1', 'CB2', 'SS', 'FS']
    team_players = [team]
    name = [team]
    for i in df.Player:
        if i != 'Defensive Starters':
            x = i.replace('*', '')
            x = x.replace('+', '')
            team_players.append(x)
    df_depth = pd.concat([pd.Series(players, name = 'Position'), pd.Series(team_players, name = 'Player')], axis = 'columns')
    
    time.sleep(5)
    df_ir = injury_report_scraper(team, year)
    df_ir_counts = ir_counter(df_ir)

    test = sqldf('''SELECT a.Position, a.Player, 
                CASE WHEN b.Week1 IS NOT NULL THEN b.Week1 ELSE '' END AS Week1
                FROM df_depth a
                LEFT JOIN df_ir b
                on a.Player = b.Player''')
    for i in df_ir.columns:
        if i != 'Week1' and i != 'player':
            test = sqldf('''SELECT a.*, 
                     CASE WHEN b.{week} IS NOT NULL THEN b.{week} ELSE '' END AS {week}
                     FROM test a
                     LEFT JOIN df_ir b
                     on a.Player = b.Player'''.format(week = i))

    df_sub = test.transpose()
    df_sub.columns = test['Position']
    df_sub = df_sub.drop('Team', axis = 'columns')
    df_sub['Team'] = team
    df_sub = df_sub.drop(['Position', 'Player'], axis = 'index')
    df_ir_counts.index = df_sub.index
    df_sub = pd.concat([df_sub, df_ir_counts], axis = 'columns')
    return(df_sub)

def sched_spread_merge(df1, df2): 
    df1a = sqldf('''SELECT a.*, b.City_abbr  
                   FROM df1 a JOIN df_names b on a.Team = b.team''')
    
    home_game = []
    game_city = []
    opponent_city = []
    for i in range(0, len(df1a['Opp'])):
        opponent_city.append(df1['Opp'][i].replace('@', ''))
        if df1a['Opp'][i].startswith('@'):
            game_city.append(df1a['Opp'][i].replace('@', ''))
            home_game.append(0)
        else:
            game_city.append(df1a['City_abbr'][i])
            home_game.append(1)
    df1a['home_game'] = home_game
    df1a['game_city'] = game_city
    df1a['opponent_city'] = opponent_city
    
    df1b = sqldf('''SELECT DISTINCT a.*, b.Team as opponent_team, b.Team_abbr as opponent_abbr 
         FROM df1a AS a
         JOIN df_names AS b ON a.opponent_city = b.City_abbr''')
        
    df2w = df2[df2['Winner_tie'] == df1['team'][0]]
    df2l = df2[df2['Loser_tie'] == df1['team'][0]]
    df2 = sqldf('''SELECT distinct *
             FROM df2w
             UNION 
             SELECT distinct *
             FROM df2l''')
    
    df3 = sqldf('''SELECT a.*, b.*
         FROM (SELECT * FROM df1b WHERE result_w_or_l = "W") a
         JOIN df2 b on a.team = b.Winner_tie
         AND a.opponent_team = b.Loser_tie
         AND CAST(a.winning_score AS INT) = CAST(b.PtsW AS INT)
         AND CAST(a.losing_score AS INT) = CAST(b.PtsL AS INT)
         UNION 
         SELECT a.*, b.*
         FROM (SELECT * FROM df1b WHERE result_w_or_l = "L") a
         JOIN df2 b on a.team = b.Loser_tie
         AND a.opponent_team = b.Winner_tie
         AND CAST(a.winning_score AS INT) = CAST(b.PtsW AS INT)
         AND CAST(a.losing_score AS INT) = CAST(b.PtsL AS INT)''')
    df4 = sqldf('''SELECT * FROM df3 ORDER BY Date''')
    week = []
    for i in df4.index:
        week.append(i+1)
    df4['Week'] = week
    df5 = sqldf('''SELECT DISTINCT *,
                   PtsW + PtsL AS Pts_Total,
                   CASE WHEN result_w_or_l = "W" then 1 else 0 end as Win,
                   CASE WHEN result_w_or_l = "L" then 1 else 0 end as Loss,
                   CASE WHEN [vs. Line] = "Won" then 1 else 0 end as spread_win,
                   CASE WHEN [vs. Line] = "Lost" then 1 else 0 end as spread_loss,
                   CASE WHEN [vs. Line] = "Push" then 1 else 0 end as spread_tie,
                   CASE WHEN [OU Result] = "Over" then 1 else 0 end as Over_win,
                   CASE WHEN [OU Result] = "Under" then 1 else 0 end as Over_loss,
                   CASE WHEN [OU Result] = "Push" then 1 else 0 end as Over_tie,
                   CASE WHEN result_w_or_l = "W" then (winning_score - losing_score)+Spread
                   ELSE (losing_score-winning_score)+Spread END AS spread_diff,
                   PtsW+PtsL-OverUnder AS Over_diff,
                   CASE WHEN result_w_or_l = "W" then winning_score - losing_score
                   ELSE losing_score-winning_score END AS point_diff,
                   CASE WHEN result_w_or_l = "W" then YdsW
                   ELSE YdsL END AS Yds_off,
                   CASE WHEN result_w_or_l = "W" then YdsL
                   ELSE YdsW END AS Yds_def,
                   CASE WHEN result_w_or_l = "W" then PtsW
                   ELSE PtsL END AS Pts_off,
                   CASE WHEN result_w_or_l = "W" then PtsL
                   ELSE PtsW END AS Pts_def,
                   CASE WHEN result_w_or_l = "W" then TOW
                   ELSE TOL END AS TO_off,
                   CASE WHEN result_w_or_l = "W" then TOL
                   ELSE TOW END AS TO_def
                   FROM df4 t1 ORDER BY Date''')
    df6 = sqldf('''SELECT *,
             CASE WHEN result_w_or_l = "W" 
             THEN 
                 (SELECT 1 + COUNT(*)
                 FROM df5 t2
                 WHERE t1.Win = t2.Win
                 AND t1.team = t2.team
                 AND t1.Date > t2.Date
                 AND NOT EXISTS (
                     SELECT *
                     FROM df5 t3
                     WHERE
                         t2.Win <> t3.Win
                         AND t1.team = t3.team
                         and t3.Date BETWEEN t2.Date AND t1.Date))
             ELSE 0 END AS Streak_W,
             CASE WHEN result_w_or_l = "L" 
             THEN 
                 (SELECT 1 + COUNT(*)
                 FROM df5 t2
                 WHERE t1.Loss = t2.Loss
                 AND t1.team = t2.team
                 AND t1.Date > t2.Date
                 AND NOT EXISTS (
                     SELECT *
                     FROM df5 t3
                     WHERE
                         t2.Loss <> t3.Loss
                         AND t1.team = t3.team
                         and t3.Date BETWEEN t2.Date AND t1.Date))
             ELSE 0 END AS Streak_L,
             CASE WHEN [vs. Line] = "Won" 
             THEN 
                 (SELECT 1 + COUNT(*)
                 FROM df5 t2
                 WHERE t1.[vs. Line] = t2.[vs. Line]
                 AND t1.team = t2.team
                 AND t1.Date > t2.Date
                 AND NOT EXISTS (
                     SELECT *
                     FROM df5 t3
                     WHERE
                         t2.[vs. Line] <> t3.[vs. Line]
                         AND t1.team = t3.team
                         and t3.Date BETWEEN t2.Date AND t1.Date))
             ELSE 0 END AS Streak_spread_W,
             CASE WHEN [vs. Line] = "Lost" 
             THEN 
                 (SELECT 1 + COUNT(*)
                 FROM df5 t2
                 WHERE t1.[vs. Line] = t2.[vs. Line]
                 AND t1.team = t2.team
                 AND t1.Date > t2.Date
                 AND NOT EXISTS (
                     SELECT *
                     FROM df5 t3
                     WHERE
                         t2.[vs. Line] <> t3.[vs. Line]
                         AND t1.team = t3.team
                         and t3.Date BETWEEN t2.Date AND t1.Date))
                 ELSE 0 END AS Streak_spread_L,
             CASE WHEN [OU Result] = "Over" 
             THEN 
                 (SELECT 1 + COUNT(*)
                 FROM df5 t2
                 WHERE t1.[OU Result] = t2.[OU Result]
                 AND t1.team = t2.team
                 AND t1.Date > t2.Date
                 AND NOT EXISTS (
                     SELECT *
                     FROM df5 t3
                     WHERE
                         t2.[OU Result] <> t3.[OU Result]
                         AND t1.team = t3.team
                         and t3.Date BETWEEN t2.Date AND t1.Date))
             ELSE 0 END AS Streak_over_W,
             CASE WHEN [OU Result] = "Under" 
             THEN 
                 (SELECT 1 + COUNT(*)
                 FROM df5 t2
                 WHERE t1.[OU Result] = t2.[OU Result]
                 AND t1.team = t2.team
                 AND t1.Date > t2.Date
                 AND NOT EXISTS (
                     SELECT *
                     FROM df5 t3
                     WHERE
                         t2.[OU Result] <> t3.[OU Result]
                         AND t1.team = t3.team
                         and t3.Date BETWEEN t2.Date AND t1.Date))
             ELSE 0 END AS Streak_over_L    
             FROM df5 t1''')
    return df6


def season_avg(df_season):
    df_avg = sqldf('''SELECT *,
             SUM(spread_win) OVER (ORDER BY Week) AS Season_spread_wins,
             SUM(spread_loss) OVER (ORDER BY Week) AS Season_spread_losses,
             SUM(spread_tie) OVER (ORDER BY Week) AS Season_spread_ties,
             SUM(Over_win) OVER (ORDER BY Week) AS Season_over_wins,
             SUM(Over_loss) OVER (ORDER BY Week) AS Season_over_losses,
             SUM(Over_tie) OVER (ORDER BY Week) AS Season_over_ties,
             SUM(spread_diff) OVER (ORDER BY Week) AS Season_spread_diff,
             SUM(Over_diff) OVER (ORDER BY Week) AS Season_over_diff,
             SUM(Spread) OVER (ORDER BY Week) AS Season_total_spread,
             SUM(OverUnder) OVER (ORDER BY Week) AS Season_total_over,
             SUM(Win) OVER (ORDER BY Week) AS Season_Wins,
             SUM(Loss) OVER (ORDER BY Week) AS Season_Losses,             
             SUM(Pts_Total) OVER (ORDER BY Week) AS Game_Total_Pts, 
             SUM(point_diff) OVER (ORDER BY Week) as Season_point_diff, 
             SUM(Pts_off) OVER (ORDER BY Week) as Season_points_off,
             SUM(Pts_def) OVER (ORDER BY Week) as Season_points_def,
             SUM(Yds_off) OVER (ORDER BY Week) as Season_Yds_off,
             SUM(Yds_def) OVER (ORDER BY Week) as Season_Yds_def,
             SUM(TO_off) OVER (ORDER BY Week) as Season_TO_off,
             SUM(TO_def) OVER (ORDER BY Week) as Season_TO_def
             FROM df_season''')
    df_avg['avg_spread_diff'] = df_avg['Season_spread_diff']/df_avg['Week']
    df_avg['avg_over_diff'] = df_avg['Season_over_diff']/df_avg['Week']
    df_avg['avg_spread'] = df_avg['Season_total_spread']/df_avg['Week']
    df_avg['avg_over'] = df_avg['Season_total_over']/df_avg['Week']
    df_avg['Avg_game_total_pts'] = df_avg['Game_Total_Pts']/df_avg['Week']
    df_avg['TO_diff'] = df_avg['Season_TO_def'] - df_avg['Season_TO_off']
    df_avg['Avg_TO_diff'] = df_avg['TO_diff']/df_avg['Week']
    df_avg['Avg_point_diff']= df_avg['Season_point_diff']/df_avg['Week']
    df_avg['Avg_pts_off']= df_avg['Season_points_off']/df_avg['Week']
    df_avg['Avg_pts_def']= df_avg['Season_points_def']/df_avg['Week']
    df_avg['Avg_yds_off']= df_avg['Season_Yds_off']/df_avg['Week']
    df_avg['Avg_yds_def']= df_avg['Season_Yds_def']/df_avg['Week']
    df_avg['Avg_TO_off']= df_avg['Season_TO_off']/df_avg['Week']
    df_avg['Avg_TO_def']= df_avg['Season_TO_def']/df_avg['Week']
    return(df_avg)

def full_season_pull(year):
    teams = []
    df_season = schedule_scraper(year)
    df_final = pd.DataFrame(columns = ['Opp', 'Spread', 'OverUnder', 'Result', 'vs. Line', 
                                       'OU Result', 'team_abbr', 'team', 'result_w_or_l', 
                                       'winning_score', 'losing_score', 'City_abbr', 'home_game', 
                                       'game_city', 'opponent_city', 'opponent_team',
                                       'opponent_abbr', 'Day', 'Date', 'Time', 'Winner_tie', 
                                       'Loser_tie','PtsW', 'PtsL', 'YdsW', 'TOW', 'YdsL', 'TOL', 
                                       'date_day', 'date_month', 'date_year', 'Week', 'Pts_Total', 
                                       'point_diff', 'Yds_off', 'Yds_def', 'Pts_off', 'Pts_def', 
                                       'TO_off', 'TO_def'])
    for i in df_names['Team_abbr']:
        if i not in teams:
            print(i, year)
            time.sleep(5)
            #pull spread data
            df_spreads = spread_scraper(i, year)
            #pull Injury Report Data
            df_ir = team_injury_report(i, year)
            df_ir = df_ir.reset_index()
            df_ir = df_ir.drop('Team', axis = 'columns')
            #merge spread and injury data
            df_spreads = pd.concat([df_spreads, df_ir], axis = 'columns')
            #merge season and spread/injury data
            df_merged = sched_spread_merge(df_spreads, df_season)
            df_avg = season_avg(df_merged)
            df_final = pd.concat([df_final, df_avg], axis = 'index')
            teams.append(i)
    df_final = sqldf('''SELECT *,
                        JULIANDAY(Date) - JULIANDAY(LAG(Date, 1) OVER (PARTITION BY team ORDER BY Date)) as days_rest,
                        LAG(Season_Wins, 1) OVER (PARTITION BY team ORDER BY Date) AS team_season_wins,
                        LAG(Season_Losses, 1) OVER (PARTITION BY team ORDER BY  Date) AS team_season_losses,
                        LAG(Streak_W, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_streakw,
                        LAG(Streak_L, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_streakl,
                        LAG(Streak_spread_w, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_streakspreadw,
                        LAG(Streak_spread_l, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_streakspreadl,
                        LAG(Streak_over_w, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_streakoverw,
                        LAG(Streak_over_l, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_streakoverl,
                        LAG(Pts_Total, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_total, 
                        LAG(point_diff, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_ptsdiff, 
                        LAG(Yds_off, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_ydsoff, 
                        LAG(Yds_def, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_ydsdef, 
                        LAG(Pts_off, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_ptsoff, 
                        LAG(Pts_def, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_ptsdef, 
                        LAG(TO_off, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_TOoff, 
                        LAG(TO_def, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_TOdef,
                        LAG(Season_point_diff, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_seasptsdiff,
                        LAG(Season_points_off, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_seasptsoff, 
                        LAG(Season_points_def, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_seasptsdef, 
                        LAG(Season_Yds_off, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_seasydsoff,
                        LAG(Season_Yds_def, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_seasydsdef, 
                        LAG(Season_TO_off, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_seasTOoff, 
                        LAG(Season_TO_def, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_seasTOdef,
                        LAG(Avg_game_total_pts, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_avgpts, 
                        LAG(TO_diff, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_TOdiff, 
                        LAG(Avg_TO_diff, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_avgTOdiff, 
                        LAG(Avg_point_diff, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_avgptsdiff,
                        LAG(Avg_pts_off, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_avgptsoff, 
                        LAG(Avg_pts_def, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_avgptsdef, 
                        LAG(Avg_yds_off, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_avgydsoff, 
                        LAG(Avg_yds_def, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_avgydsdef,
                        LAG(Avg_TO_off, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_avgTOoff, 
                        LAG(Avg_TO_def, 1) OVER (PARTITION BY team ORDER BY  Date) AS prev_week_avgTOdef,
                        LAG(avg_spread_diff, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_avgspreaddif,
                        LAG(avg_over_diff, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_avgoverdif,
                        LAG(avg_spread, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_avgspread,
                        LAG(avg_over, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_avgover,
                        LAG(Season_spread_wins, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_seasspreadwin,
                        LAG(Season_spread_losses, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_seasspreadloss,
                        LAG(Season_spread_ties, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_seasspreadtie,
                        LAG(Season_over_wins, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_seasoverwin,
                        LAG(Season_over_losses, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_seasoverloss,
                        LAG(Season_over_ties, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_seasovertie,
                        LAG(Season_total_spread, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_seastotspread,
                        LAG(Season_total_over, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_seastotover,
                        LAG(spread_win, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_spreadwin,
                        LAG(spread_loss, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_spreadloss,
                        LAG(spread_tie, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_spreadtie,
                        LAG(Over_win, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_overwin,
                        LAG(Over_loss, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_overloss,
                        LAG(Over_tie, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_overtie,
                        LAG(spread_diff, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_spreaddiff,
                        LAG(Over_diff, 1) OVER (PARTITION BY team ORDER BY Date) AS prev_week_overdiff
                        FROM df_final''')
    return(df_final)

df_all_season_final = full_season_pull('2015')

#df_all_season_final.to_csv(r"C:\Users\cpilo\Downloads\df_all_teams_testing_testing1.csv")

df_all_season_final_matched = sqldf('''SELECT a.*, 
         b.Pts_Total as Opp_pts_total, 
         b.point_diff as Opp_pts_diff, 
         b.Yds_off as Opp_yds_off, 
         b.Yds_def as Opp_yds_def,
         b.Pts_off as Opp_pts_off, 
         b.Pts_def as Opp_pts_def, 
         b.TO_off as Opp_TO_off, 
         b.TO_def as Opp_TO_def, 
         b.Season_point_diff as Opp_season_pnt_diff, 
         b.Season_points_off as Opp_season_pnt_off, 
         b.Season_points_def as Opp_season_pnt_def,
         b.Season_Yds_off as Opp_season_yds_off, 
         b.Season_Yds_def as Opp_season_yds_def, 
         b.Season_TO_off as Opp_season_TO_off, 
         b.Season_TO_def as Opp_season_TO_def,
         b.Avg_game_total_pts as Opp_avg_game_total_pts, 
         b.TO_diff as Opp_to_diff, 
         b.Avg_TO_diff as Opp_TO_diff, 
         b.Avg_point_diff as Opp_avg_pnt_diff,
         b.Avg_pts_off as Opp_avg_pts_off, 
         b.Avg_pts_def as Opp_avg_pts_def, 
         b.Avg_yds_off as Opp_avg_yds_off, 
         b.Avg_yds_def as Opp_avg_yds_def,
         b.Avg_TO_off as Opp_TO_off, 
         b.Avg_TO_def as Opp_TO_def, 
         b.Season_Wins as Opp_Season_Wins, 
         b.Season_Losses as Opp_Season_Losses, 
         b.days_rest as Opp_days_rest,
         b.team_season_wins as Opp_team_season_wins,
         b.team_season_losses as Opp_team_season_losses,
         b.prev_week_total as opp_prev_week_total, 
         b.prev_week_ptsdiff as opp_prev_week_pts_diff, 
         b.prev_week_ydsoff as opp_prev_week_ydsoff, 
         b.prev_week_ydsdef as opp_prev_week_ydsdef, 
         b.prev_week_ptsoff as opp_prev_week_ptsoff, 
         b.prev_week_ptsdef as opp_prev_week_ptsdef, 
         b.prev_week_TOoff as opp_prev_week_TOoff, 
         b.prev_week_TOdef as opp_prev_week_TOdef,
         b.prev_week_seasptsdiff as opp_prev_week_seasptsdiff,
         b.prev_week_seasptsoff as opp_prev_week_seasptsoff, 
         b.prev_week_seasptsdef as opp_prev_week_seasptsdef, 
         b.prev_week_seasydsoff as opp_prev_week_seasydsoff,
         b.prev_week_seasydsdef as opp_prev_week_seasydsdef, 
         b.prev_week_seasTOoff as opp_prev_week_seasTOoff, 
         b.prev_week_seasTOdef as opp_prev_week_seasTOdef,
         b.prev_week_avgpts as opp_prev_week_avgpts, 
         b.prev_week_TOdiff as opp_prev_week_TOdiff, 
         b.prev_week_avgTOdiff as opp_prev_week_avgTOdiff, 
         b.prev_week_avgptsdiff as opp_prev_week_avgptsdiff,
         b.prev_week_avgptsoff as opp_prev_week_avgptsoff, 
         b.prev_week_avgptsdef as opp_prev_week_avgptsdef, 
         b.prev_week_avgydsoff as opp_prev_week_avgydsoff, 
         b.prev_week_avgydsdef as opp_prev_week_avgydsdef,
         b.prev_week_avgTOoff as opp_prev_week_avgTOoff, 
         b.prev_week_avgTOdef as opp_prev_week_avgTOdef, 
         b.prev_week_avgspreaddif as opp_prev_week_avgspreaddif,
         b.prev_week_avgoverdif as opp_prev_week_avgoverdif,
         b.prev_week_avgspread as opp_prev_week_avgspread,
         b.prev_week_avgover as opp_prev_week_avgover,
         b.prev_week_seasspreadwin as opp_prev_week_seasspreadwin,
         b.prev_week_seasspreadloss as opp_prev_week_seasspreadloss,
         b.prev_week_seasspreadtie as opp_prev_week_seasspreadtie,
         b.prev_week_seasoverwin as opp_prev_week_seasoverwin,
         b.prev_week_seasoverloss as opp_prev_week_seasoverloss,
         b.prev_week_seasovertie as opp_prev_week_seasovertie,
         b.prev_week_seastotspread as opp_prev_week_seastotspread,
         b.prev_week_seastotover as opp_prev_week_seastotover,
         b.prev_week_spreadwin as opp_prev_week_spreadwin,
         b.prev_week_spreadloss as opp_prev_week_spreadloss,
         b.prev_week_spreadtie as opp_prev_week_spreadtie,
         b.prev_week_overwin as opp_prev_week_overwin,
         b.prev_week_overloss as opp_prev_week_overloss,
         b.prev_week_overtie as opp_prev_week_overtie,
         b.prev_week_spreaddiff as opp_prev_week_spreaddiff,
         b.prev_week_overdiff as opp_prev_week_overdiff,
         b.prev_week_streakw as opp_prev_week_streakw,
         b.prev_week_streakl as opp_prev_week_streakl,
         b.prev_week_streakspreadw as opp_prev_week_streakspreadw,
         b.prev_week_streakspreadl as opp_prev_week_streakspreadl,
         b.prev_week_streakoverw as opp_prev_week_streakoverw,
         b.prev_week_streakoverl as opp_prev_week_streakoverl, 
         b.QB1 as opp_QB1,
         b.Skill1 as opp_skill1,
         b.Skill2 as opp_skill2,
         b.Skill3 as opp_skill3,
         b.Skill4 as opp_skill4,
         b.Skill5 as opp_skill5,
         b.Oline1 as opp_oline1,
         b.Oline2 as opp_oline2,
         b.Oline3 as opp_oline3,
         b.Oline4 as opp_oline4,
         b.Oline5 as opp_oline5,
         b.Dline1 as opp_dline1,
         b.Dline2 as opp_dline2,
         b.Dline3 as opp_dline3,
         b.LB1 as opp_lb1,
         b.LB2 as opp_lb2,
         b.LB3 as opp_lb3,
         b.LB4 as opp_lb4,
         b.CB1 as opp_cb1,
         b.CB2 as opp_cb2,
         b.SS as opp_ss,
         b.FS as opp_fs,
         b.Q_count as opp_Q_count,
         b.P_count as opp_P_count,
         b.O_count as opp_O_count,
         b.A_count as opp_A_count
         FROM df_all_season_final a
         JOIN df_all_season_final b
         ON a.team = b.opponent_team
         AND a.opponent_team = b.team
         AND a.Date = b.Date''')
         
         
for i in ['2016', '2017','2018', '2019','2020', '2021']:
    df_season_final = full_season_pull(i)
    df_season_final_matched = sqldf('''SELECT a.*, 
         b.Pts_Total as Opp_pts_total, 
         b.point_diff as Opp_pts_diff, 
         b.Yds_off as Opp_yds_off, 
         b.Yds_def as Opp_yds_def,
         b.Pts_off as Opp_pts_off, 
         b.Pts_def as Opp_pts_def, 
         b.TO_off as Opp_TO_off, 
         b.TO_def as Opp_TO_def, 
         b.Season_point_diff as Opp_season_pnt_diff, 
         b.Season_points_off as Opp_season_pnt_off, 
         b.Season_points_def as Opp_season_pnt_def,
         b.Season_Yds_off as Opp_season_yds_off, 
         b.Season_Yds_def as Opp_season_yds_def, 
         b.Season_TO_off as Opp_season_TO_off, 
         b.Season_TO_def as Opp_season_TO_def,
         b.Avg_game_total_pts as Opp_avg_game_total_pts, 
         b.TO_diff as Opp_to_diff, 
         b.Avg_TO_diff as Opp_TO_diff, 
         b.Avg_point_diff as Opp_avg_pnt_diff,
         b.Avg_pts_off as Opp_avg_pts_off, 
         b.Avg_pts_def as Opp_avg_pts_def, 
         b.Avg_yds_off as Opp_avg_yds_off, 
         b.Avg_yds_def as Opp_avg_yds_def,
         b.Avg_TO_off as Opp_TO_off, 
         b.Avg_TO_def as Opp_TO_def, 
         b.Season_Wins as Opp_Season_Wins, 
         b.Season_Losses as Opp_Season_Losses, 
         b.days_rest as Opp_days_rest,
         b.team_season_wins as Opp_team_season_wins,
         b.team_season_losses as Opp_team_season_losses,
         b.prev_week_total as opp_prev_week_total, 
         b.prev_week_ptsdiff as opp_prev_week_pts_diff, 
         b.prev_week_ydsoff as opp_prev_week_ydsoff, 
         b.prev_week_ydsdef as opp_prev_week_ydsdef, 
         b.prev_week_ptsoff as opp_prev_week_ptsoff, 
         b.prev_week_ptsdef as opp_prev_week_ptsdef, 
         b.prev_week_TOoff as opp_prev_week_TOoff, 
         b.prev_week_TOdef as opp_prev_week_TOdef,
         b.prev_week_seasptsdiff as opp_prev_week_seasptsdiff,
         b.prev_week_seasptsoff as opp_prev_week_seasptsoff, 
         b.prev_week_seasptsdef as opp_prev_week_seasptsdef, 
         b.prev_week_seasydsoff as opp_prev_week_seasydsoff,
         b.prev_week_seasydsdef as opp_prev_week_seasydsdef, 
         b.prev_week_seasTOoff as opp_prev_week_seasTOoff, 
         b.prev_week_seasTOdef as opp_prev_week_seasTOdef,
         b.prev_week_avgpts as opp_prev_week_avgpts, 
         b.prev_week_TOdiff as opp_prev_week_TOdiff, 
         b.prev_week_avgTOdiff as opp_prev_week_avgTOdiff, 
         b.prev_week_avgptsdiff as opp_prev_week_avgptsdiff,
         b.prev_week_avgptsoff as opp_prev_week_avgptsoff, 
         b.prev_week_avgptsdef as opp_prev_week_avgptsdef, 
         b.prev_week_avgydsoff as opp_prev_week_avgydsoff, 
         b.prev_week_avgydsdef as opp_prev_week_avgydsdef,
         b.prev_week_avgTOoff as opp_prev_week_avgTOoff, 
         b.prev_week_avgTOdef as opp_prev_week_avgTOdef, 
         b.prev_week_avgspreaddif as opp_prev_week_avgspreaddif,
         b.prev_week_avgoverdif as opp_prev_week_avgoverdif,
         b.prev_week_avgspread as opp_prev_week_avgspread,
         b.prev_week_avgover as opp_prev_week_avgover,
         b.prev_week_seasspreadwin as opp_prev_week_seasspreadwin,
         b.prev_week_seasspreadloss as opp_prev_week_seasspreadloss,
         b.prev_week_seasspreadtie as opp_prev_week_seasspreadtie,
         b.prev_week_seasoverwin as opp_prev_week_seasoverwin,
         b.prev_week_seasoverloss as opp_prev_week_seasoverloss,
         b.prev_week_seasovertie as opp_prev_week_seasovertie,
         b.prev_week_seastotspread as opp_prev_week_seastotspread,
         b.prev_week_seastotover as opp_prev_week_seastotover,
         b.prev_week_spreadwin as opp_prev_week_spreadwin,
         b.prev_week_spreadloss as opp_prev_week_spreadloss,
         b.prev_week_spreadtie as opp_prev_week_spreadtie,
         b.prev_week_overwin as opp_prev_week_overwin,
         b.prev_week_overloss as opp_prev_week_overloss,
         b.prev_week_overtie as opp_prev_week_overtie,
         b.prev_week_spreaddiff as opp_prev_week_spreaddiff,
         b.prev_week_overdiff as opp_prev_week_overdiff,
         b.prev_week_streakw as opp_prev_week_streakw,
         b.prev_week_streakl as opp_prev_week_streakl,
         b.prev_week_streakspreadw as opp_prev_week_streakspreadw,
         b.prev_week_streakspreadl as opp_prev_week_streakspreadl,
         b.prev_week_streakoverw as opp_prev_week_streakoverw,
         b.prev_week_streakoverl as opp_prev_week_streakoverl,
         b.QB1 as opp_QB1,
         b.Skill1 as opp_skill1,
         b.Skill2 as opp_skill2,
         b.Skill3 as opp_skill3,
         b.Skill4 as opp_skill4,
         b.Skill5 as opp_skill5,
         b.Oline1 as opp_oline1,
         b.Oline2 as opp_oline2,
         b.Oline3 as opp_oline3,
         b.Oline4 as opp_oline4,
         b.Oline5 as opp_oline5,
         b.Dline1 as opp_dline1,
         b.Dline2 as opp_dline2,
         b.Dline3 as opp_dline3,
         b.LB1 as opp_lb1,
         b.LB2 as opp_lb2,
         b.LB3 as opp_lb3,
         b.LB4 as opp_lb4,
         b.CB1 as opp_cb1,
         b.CB2 as opp_cb2,
         b.SS as opp_ss,
         b.FS as opp_fs,  
         b.Q_count as opp_Q_count,
         b.P_count as opp_P_count,
         b.O_count as opp_O_count,
         b.A_count as opp_A_count
         FROM df_season_final a
         JOIN df_season_final b
         ON a.team = b.opponent_team
         AND a.opponent_team = b.team
         AND a.Date = b.Date''')

    try:
        df_all_season_final_matched = pd.concat([df_all_season_final_matched, df_season_final_matched], axis = 'index')
    except:
        extra_vars = []
        for p in df_season_final_matched.columns:
            if p not in df_all_season_final_matched.columns:
                extra_vars.append(p)
        df_season_final_matched = df_season_final_matched.drop(extra_vars, axis = 'columns')
        df_all_season_final_matched = pd.concat([df_all_season_final_matched, df_season_final_matched], axis = 'index')
print(df_all_season_final_matched)
df_all_season_final_matched.to_csv(r"C:\Users\cpilo\Downloads\df_all_teams.csv")