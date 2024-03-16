import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
pd.set_option('display.max_columns', None)

data = pd.read_excel('nba_player_data.xlsx')

#Data cleaning and preparation 

data.drop(columns = ['RANK', 'EFF'], inplace =True)

data['season_start_year'] = data['Year'].str[:4].astype(int)

data['TEAM'].replace(to_replace=['NOP','NOH'], value = 'NO', inplace = True)
data['Season_type'].replace('Regular%20Season', 'RS', inplace = True)

rs_df = data[data['Season_type'] =='RS']
playoffs_df = data[data['Season_type'] =='RS']

total_cols = ['MIN', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']

#Stat correlations

data_per_min = data.groupby(['PLAYER', 'PLAYER_ID', 'Year'])[total_cols].sum().reset_index()
for col in data_per_min.columns[4:]:
    data_per_min[col] = data_per_min[col]/data_per_min['MIN']

data_per_min['FG%'] = data_per_min['FGM']/data_per_min['FGA']
data_per_min['3PT%'] = data_per_min['FG3M']/data_per_min['FG3A']
data_per_min['FT%'] = data_per_min['FTM']/data_per_min['FTA']
data_per_min['FG3A%'] = data_per_min['FG3A']/data_per_min['FGA']
data_per_min['PTS/FGA'] = data_per_min['PTS']/data_per_min['FGA']
data_per_min['FG3M/FGM'] = data_per_min['FG3M']/data_per_min['FGM']
data_per_min['FTA/FGA'] = data_per_min['FTA']/data_per_min['FGA']
data_per_min['TRU%'] = 0.5*data_per_min['PTS']/data_per_min['TOV']+0.475*data_per_min['FTA']
data_per_min['AST_TOV'] = data_per_min['AST']/data_per_min['TOV']

data_per_min = data_per_min[data_per_min['MIN'] >= 50]
data_per_min.drop(columns='PLAYER_ID', inplace=True)


#Distribution of Minutes Played

def hist_data(df=rs_df, min_MIN = 0, min_GP=0):
    df.loc[(df['MIN']>=min_MIN) & (df['GP']>=min_GP), 'MIN']/df.loc[(df['MIN']>=min_MIN) & (df['GP']>=min_GP), 'GP']

fig = go.Figure()
fig.add_trace(go.Histogram(x=hist_data(rs_df,50,5), histnorm='percent', name = 'RS', xbins={'start': 0, 'end': 38, 'size':1}))
fig.add_trace(go.Histogram(x=hist_data(playoffs_df,5,1), histnorm='percent', name ='Playoffs', xbins={'start': 0, 'end': 38, 'size':1}))
fig.update_layout(barmode='overlay')
fig.update_traces(opacity=0.5)
fig.show()                 

((hist_data(rs_df,50,5)>=12)&(hist_data(rs_df,50,5)<=34)).mean()
((hist_data(playoffs_df,5,1)>=12)&(hist_data(playoffs_df,5,1)<=34)).mean()

#How the game has changed

change_df = data.groupby('season_start_year')[total_cols].sum().reset_index()
change_df['POSS_est'] = change_df['FGA']-change_df['OREB']+change_df['TOV']+0.44*change_df['FTA']
change_df = change_df[list(change_df.columns[0:2])+['POSS_est']+list(change_df.columns[2:-1])]  

change_df['FG%'] = change_df['FGM']/change_df['FGA']
change_df['3PT%'] = change_df['FG3M']/change_df['FG3A']
change_df['FT%'] = change_df['FTM']/change_df['FTA']
change_df['FG3A%'] = change_df['FG3A']/change_df['FGA']
change_df['PTS/FGA'] = change_df['PTS']/change_df['FGA']
change_df['FG3M/FGM'] = change_df['FG3M']/change_df['FGM']
change_df['FTA/FGA'] = change_df['FTA']/change_df['FGA']
change_df['TRU%'] = 0.5*change_df['PTS']/change_df['TOV']+0.475*change_df['FTA']
change_df['AST_TOV'] = change_df['AST']/change_df['TOV']

change_per48_df = change_df.copy()

for col in change_per48_df.colums[2:18]:
    change_per48_df[col] = (change_per48_df[col]/change_per48_df['MIN'])*48*5

change_per48_df.drop(columns='MIN',inplace=True)

fig = go.Figure()
for col in change_per48_df.columns[1:]:
    fig.add_trace(go.Scatter(x=change_per48_df['season_start_year'], y = change_per48_df[col], name = col))

fig.show()

change_per100_df = change_df.copy()

for col in change_per100_df.colums[3:18]:
    change_per100_df[col] = (change_per100_df[col]/change_per100_df['POSS_est'])*100

change_per100_df.drop(columns=['MIN','POSS_est'],inplace=True)

fig = go.Figure()
for col in change_per100_df.columns[1:]:
    fig.add_trace(go.Scatter(x=change_per48_df['season_start_year'], y = change_per100_df[col], name = col))

fig.show()

#Regular Season versus Playoffs

rs_change_df = rs_df.groupby('season_start_year')[total_cols].sum().reset_index()
playoffs_change_df = playoffs_df.groupby('season_start_year')[total_cols].sum().reset_index()

for i in [rs_change_df, playoffs_change_df]:
    i['POSS_est'] = i['FGM']/i['FGA']
    i['POSS_per_48'] = (i['POSS_est']/i['MIN'])*48*5

    i['FG%'] = i['FGM']/i['FGA']
    i['3PT%'] = i['FG3M']/i['FG3A']
    i['FT%'] = i['FTM']/i['FTA']
    i['AST%'] = i['AST']/i['FGM']
    i['FG3A%'] = i['FG3A']/i['FGA']
    i['PTS/FGA'] = i['PTS']/i['FGA']
    i['FG3M/FGM'] = i['FG3M']/i['FGM']
    i['FTA/FGA'] = i['FTA']/i['FGA']
    i['TRU%'] = 0.5*i['PTS']/(i['FGA']+0.475*i['FTA'])
    i['AST_TOV'] = i['AST']/i['TOV']

    for col in total_cols:
        i[col] = 100*i[col]/i['POSS_est']

    i.drop(columns=['MIN', 'POSS_est'], inplace = True)

comp_change_df = round(100*(playoffs_change_df-rs_change_df)/rs_change_df, 3)
comp_change_df['season_start_year'] = list(range(2012,2022))

fig = go.Figure()
for col in comp_change_df.columns[1:]:
    fig.add_trace(go.Scatter(x=comp_change_df['season_start_year'], y = comp_change_df[col], name = col))

fig.show()