# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 16:47:31 2023

@author: cpilo
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from pandasql import sqldf
import time
import pandas as pd
import numpy as np

%run C:\Users\cpilo\.spyder-py3\autosave\nfl_data_preperation_final_draft.py

df = df_all_season_final_matched

df_team_data = pd.get_dummies(df.team_abbr)

model_vars = ['Date',
              'Spread', 'OverUnder', 'Streak_W', 'Streak_L',
              'Season_Wins', 'Season_spread_wins', 'Season_over_wins', 'Season_points_off',
              'Season_points_def', 'Season_Yds_off', 'Season_Yds_def', 'Season_TO_off',
              'Opp_season_pnt_off', 'Opp_season_pnt_def',  'Opp_season_yds_off', 
              'Opp_season_yds_def', 'Opp_season_TO_off', 'Opp_season_TO_def', 'Opp_Season_Wins',
              'Opp_Season_Losses', 'Season_Losses',
              'Season_TO_def', 'Yds_off', 'Yds_def', 'Pts_off', 'Pts_def', 'TO_off', 'TO_def']

df_rfc_data = df[model_vars]
df_final_data = pd.concat([df_rfc_data, df_team_data], axis = 'columns')
df_final_data = df_final_data.dropna(axis = 'index')
df_final_data.index = df_final_data.Date
df_final_data = df_final_data.drop('Date', axis = 'columns')

Team_abbr = ['crd', 'atl', 'rav', 'buf', 'car', 'chi', 'cin', 'cle', 'dal', 'den', 'det', 
             'gnb', 'htx', 'clt', 'jax', 'kan', 'rai', 'rai', 'sdg', 'sdg', 'ram', 'ram', 'mia', 'min', 'nwe', 
             'nor', 'nyg', 'nyj', 'phi', 'pit', 'sfo', 'sea', 'tam', 'oti', 'was', 'was', 
             'was']

%run C:\Users\cpilo\.spyder-py3\autosave\Time_Series_Class.py

def model_saver(team, model_vars, folder_path):
    #create time series for each team
    df_series = df_final_data[df_final_data[team]==1]
    #filter on our model variables
    df_series = df_series[model_vars]
    #create a time_series_model object fit to our data
    var_model = time_series_model(Ravens_series, nobs = 1, max_lags = 5)
    #save our model object
    model = var_model.get_var_model()
    #save our forcested series
    forecasted_series = var_model.get_var_forecasted_data()
    #save our accuracy
    accuracy = var_model.get_accuracy_matrix()
    #save the number of times we differenced our data
    num_differences = var_model.get_number_of_differences()
    #save the initial values
    initial_vals = var_model.get_initial_values()
    #save our training data
    stationary_series = var_model.get_stationary_series()
    df = {"team": team,
          "variables": model_vars,
          "model": model,
          "forecast": forecasted_series,
          "accuracy": accuracy,
          "number of times differenced": num_differences,
          "initial series values": initial_vals,
          "stationary input series": stationary_series
         }
    file_path = folder_path + team + '.pkl'
    #dump the file to a pickel file
    pickle.dump(df, open(file_path, 'wb'))
    return df

for i in Team_abbr:
    #remove Date variable from model_vars and call model_saver
    model_saver(i, model_vars[1:], r"C:\Users\cpilo\Downloads\my_nfl_var_model\var_model_072023_")