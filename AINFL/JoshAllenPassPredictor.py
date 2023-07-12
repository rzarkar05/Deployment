# Imports
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import warnings
from sklearn import model_selection
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings("ignore")

def pass_predictor(week_num, link):
  warnings.filterwarnings("ignore")
  toReturn = []
  week = week_num
  #Reading the Player Data and setting week value
  player_url = link
  player_html = urlopen(player_url)
  player_stats_page = BeautifulSoup(player_html, features="html.parser")
  player_column_headers = player_stats_page.findAll('tr')[0]
  player_column_headers = [i.getText() for i in player_column_headers.findAll('th')]
  player_rows = player_stats_page.findAll('tr')[1:]
  qb_stats = []
  for i in range(len(player_rows)):
    row_data = [col.getText().strip() or '0' for col in player_rows[i].findAll('td')]
    qb_stats.append(row_data)
  qb_stats = qb_stats[:week]
  player_data = pd.DataFrame(qb_stats, columns=player_column_headers)
  data_selected = player_data[["WK", "OPP", "YDS"]].copy()
  data_selected["AT_HOME"] = data_selected["OPP"].apply(lambda x: 1 if x and x.startswith("@") else 0)
  data_selected["OPP"] = data_selected["OPP"].str.replace("@", "")
  player_data = data_selected
  player_data["WK"] = player_data["WK"].astype(float)
  player_data["YDS"] = player_data["YDS"].astype(float)
  player_data["avg_yds3"] = ((player_data["YDS"].rolling(window=3).mean()).iloc[:, :1]).fillna(250)

  #Reading the Defenses Data and cleaning it
  def_url = 'https://www.nfl.com/stats/team-stats/defense/passing/2022/reg/all'
  def_html = urlopen(def_url)
  def_stats_page = BeautifulSoup(def_html, features="html.parser")
  def_column_headers = def_stats_page.findAll('tr')[0]
  def_column_headers = [i.getText() for i in def_column_headers.findAll('th')]
  def_rows = def_stats_page.findAll('tr')[1:]
  def_stats = []
  for i in range(len(def_rows)):
    def_stats.append([col.getText() for col in def_rows[i].findAll('td')])
  def_data = pd.DataFrame(def_stats, columns=def_column_headers)
  def_data = def_data.add_prefix('def_')
  def_data['def_Team'] = def_data['def_Team'].apply(lambda x: x[:len(x)//2])

  #Merges based on def_team and OPP and then drops those cols
  merged_data = player_data.merge(def_data, left_on='OPP', right_on='def_Team')
  final_data = merged_data.sort_values(by='WK')
  final_data = final_data.drop('def_Team', axis=1)
  final_data = final_data.drop('OPP', axis=1)
  column_to_move = 'YDS'
  other_columns = final_data.columns.difference([column_to_move])
  new_order = [*other_columns, column_to_move]
  df_reordered = final_data[new_order]
  df_updated = df_reordered.iloc[:, :-1]
  data = df_updated.astype(float)
  temp = data
  data = data.drop('WK', axis=1)

  # Split-out validation dataset
  array = data.values
  X = array[:,0:12]
  y = array[:,12]
  kfold= model_selection.KFold(n_splits=week, random_state=7, shuffle=True)
  linear_regression = LinearRegression()
  mse_scores = []
  mae_scores = []
  rmse_scores = []
  r2_scores = []

  #Train and find accuracy of model
  for train_index, test_index in kfold.split(X):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]

    # Training the model
    linear_regression.fit(X_train, y_train)

    # Making predictions on the test set
    y_pred = linear_regression.predict(X_test)

    #Individual Evals
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    r2 = r2_score(y_test, y_pred)
    mse_scores.append(mse)
    mae_scores.append(mae)
    rmse_scores.append(rmse)
    r2_scores.append(r2)

  #EVALS
  eval = round(np.sqrt(np.mean(mse_scores)))
  toReturn.append(eval)
  eval = round(np.mean(mae_scores))
  toReturn.append(eval)
  eval = round(np.sqrt(mean_squared_error(y_test, y_pred)))
  toReturn.append(eval)
  eval = np.mean(r2_scores)
  toReturn.append(eval)

  #Returning user request
  user_request = ((temp[temp['WK'] == week].copy()).iloc[:, :-1]).drop('WK', axis=1)
  if user_request.empty:
        return "Player has a bye week"
  final_prediction = linear_regression.predict(user_request)
  toReturn.append(round(final_prediction[0]))
  return toReturn