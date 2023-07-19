# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 11:16:41 2023

@author: cpilo
"""

import pandas as pd
import numpy as np
import statistics as stat
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
from statsmodels.tools.eval_measures import rmse, aic
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from statsmodels.tsa.stattools import acf

class time_series_model():
    def __init__(self, series, nobs, max_lags):
        self.series = series
        self.nobs = nobs
        self.max_lags = max_lags
    
    def ad_fuller_test(self, df):
        series_name = []
        series_test = []
        series_pval = []
        for name, column in df.iteritems():
            x = adfuller(column)
            series_name.append(name)
            series_test.append(x[0])
            series_pval.append(x[1])
        df_ad_test = pd.concat([pd.Series(series_name, name = 'Series'), 
                                pd.Series(series_test, name = 'Test_Statistic'), 
                                pd.Series(series_pval, name = 'P_Value')], axis = 'columns')
        return df_ad_test
    
    def get_ad_fuller_results(self):
        return self.ad_fuller_test(self.series)
    
    def differencer(self, df):
        test_pass = False
        number_of_differences = 0
        initial_values = []
        while test_pass == False:
            x = self.ad_fuller_test(df)
            if max(x.P_Value) > 0.05:
                initial_values.append(df.iloc[0,:].values)
                df = df.diff().dropna()
                number_of_differences += 1
            else:
                test_pass = True
        return df, number_of_differences, initial_values
    
    def get_stationary_series(self):
        return self.differencer(self.series)[0]
    
    def get_number_of_differences(self):
        return self.differencer(self.series)[1]
    
    def get_initial_values(self):
        return self.differencer(self.series)[2]
    
    #a function that takes a series and initial values and inverts the differencing
    def invert_differencing(self, initial_vals, df_differenced):
        df_differenced = df_differenced.reset_index(drop = True)
        df_differenced.loc[-1] = initial_vals
        df_differenced.index = df_differenced.index + 1
        df_differenced.sort_index(inplace = True)
        df_inverse = df_differenced.cumsum()
        return df_inverse
    
    #function that inverses a series that has been differenced multiple times
    def full_diff_inversion(self, df_forecasted, num_differences, initial_values):
        if num_differences == 0:
            df_final = df_forecasted
        else:
            df_final = self.invert_differencing(initial_values[-1], df_forecasted)
            for i in range(2, len(initial_values)+1):
                df_final = self.invert_differencing(initial_values[len(initial_values)-i], df_final)
        return df_final
    
    def var_train(self, df_differenced, max_lags):
        model = VAR(df_differenced)
        x = model.select_order(maxlags=max_lags)
        model_fitted = model.fit(x.aic)
        return model_fitted
    
    def var_forecast(self, model, df_diff, df_orig, nobs):
        lag_order = model.k_ar
        # Input data for forecasting
        forecast_input = df_diff.values[-lag_order:]
        # Forecast
        fc = model.forecast(y=forecast_input, steps=nobs)
        df_forecast = pd.DataFrame(fc, index=df_orig.index[-nobs:], columns=df_orig.columns)
        return df_forecast
    
    def full_var_model(self, df, nobs, max_lags):
        df_train, df_test = df[0:-nobs], df[-nobs:]
        differenced_data = self.differencer(df_train)
        model = self.var_train(differenced_data[0], max_lags)
        df_forecast = self.var_forecast(model, differenced_data[0], df, nobs)
        df_forecast_final = pd.concat([differenced_data[0], df_forecast], axis = 'index')
        df_result = self.full_diff_inversion(df_forecast_final, differenced_data[1], differenced_data[2])
        return df_result, model
    
    def get_var_model(self):
        return self.full_var_model(self.series, self.nobs, self.max_lags)[1]
    
    def get_var_forecasted_data(self):
        return self.full_var_model(self.series, self.nobs, self.max_lags)[0][-self.nobs:]
    
    def forecast_accuracy(self, forecast, actual):
        mape = np.mean(np.abs(forecast - actual)/np.abs(actual))  # MAPE
        me = np.mean(forecast - actual)             # ME
        mae = np.mean(np.abs(forecast - actual))    # MAE
        mpe = np.mean((forecast - actual)/actual)   # MPE
        pe = (np.sum(forecast)-np.sum(actual))/np.sum(actual)
        rmse = np.mean((forecast - actual)**2)**.5  # RMSE
        corr = np.corrcoef(forecast, actual)[0,1]   # corr
        mins = np.amin(np.hstack([forecast[:,None], 
                                  actual[:,None]]), axis=1)
        maxs = np.amax(np.hstack([forecast[:,None], 
                                  actual[:,None]]), axis=1)
        minmax = 1 - np.mean(mins/maxs)             # minmax
        return pd.DataFrame([mape, me, mae, mpe, rmse, corr, minmax], 
                            index = ['mape', 'me', 'mae', 'mpe', 'rmse', 'corr', 'minmax'])
        
    def get_accuracy(self):
        df_actual = self.series[-self.nobs:]
        df_forecast = self.get_var_forecasted_data()
        accuracy_matrix = pd.DataFrame([], index = ['mape', 'me', 'mae', 'mpe', 'rmse', 'corr', 'minmax'])
        for col in df_actual.columns:
            accuracy_matrix = pd.concat([accuracy_matrix, 
                                         self.forecast_accuracy(df_forecast[col], df_actual[col])], 
                                        axis = 'columns')
        accuracy_matrix.columns = df_actual.columns
        return accuracy_matrix
