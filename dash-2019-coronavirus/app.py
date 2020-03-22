# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math
import os

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

###################################
# Private function
###################################

def make_country_table(countryName):
    '''This is the function for building df for Province/State of a given country'''
    countryTable = df_latest.loc[df_latest['Country/Region'] == countryName]
    # Suppress SettingWithCopyWarning
    pd.options.mode.chained_assignment = None
    countryTable['Remaining'] = countryTable['Confirmed'] - \
        countryTable['Recovered'] - countryTable['Deaths']
    countryTable = countryTable[[
        'Province/State', 'Remaining', 'Confirmed', 'Recovered', 'Deaths', 'lat', 'lon']]
    countryTable = countryTable.sort_values(
        by=['Remaining', 'Confirmed'], ascending=False).reset_index(drop=True)
    # Set row ids pass to selected_row_ids
    countryTable['id'] = countryTable['Province/State']
    countryTable.set_index('id', inplace=True, drop=False)
    # Turn on SettingWithCopyWarning
    pd.options.mode.chained_assignment = 'warn'
    return countryTable


def make_dcc_country_tab(countryName, dataframe):
    '''This is for generating tab component for country table'''
    return dcc.Tab(label=countryName,
            value=countryName,
            className='custom-tab',
            selected_className='custom-tab--selected',
            children=[dash_table.DataTable(
                    # Don't show coordinates
                    columns=[{"name": i, "id": i}
                        for i in dataframe.columns[0:5]],
                    # But still store coordinates in the table for interactivity
                    data=dataframe.to_dict("rows"),
                    # row_selectable="single",
                    sort_action="native",
                    style_as_list_view=True,
                    style_cell={'font_family': 'Arial',
                                  'font_size': '1.2rem',
                                  'padding': '.1rem',
                                  'backgroundColor': '#f4f4f2', },
                    fixed_rows={'headers': True, 'data': 0},
                    style_table={'minHeight': '1050px',
                                   'height': '1050px',
                                   'maxHeight': '1050px'},
                    style_header={'backgroundColor': '#f4f4f2',
                                    'fontWeight': 'bold'},
                    style_cell_conditional=[{'if': {'column_id': 'Province/State'}, 'width': '28%'},
                                              {'if': {'column_id': 'Remaining'},
                                                  'width': '18%'},
                                              {'if': {'column_id': 'Confirmed'},
                                                  'width': '18%'},
                                              {'if': {'column_id': 'Recovered'},
                                                  'width': '18%'},
                                              {'if': {'column_id': 'Deaths'},
                                                  'width': '18%'},
                                              {'if': {'column_id': 'Confirmed'},
                                                  'color': '#d7191c'},
                                              {'if': {'column_id': 'Recovered'},
                                                  'color': '#1a9622'},
                                              {'if': {'column_id': 'Deaths'},
                                                  'color': '#6c6c6c'},
                                              {'textAlign': 'center'}],
                        )
            ]
          )


################################################################################
# Data processing
################################################################################
# Method #1
# Import csv file and store each csv in to a df list
# NOTE all following steps really rely on the correct order of these csv files in folder raw_data
filename = os.listdir('./raw_data/')
sheet_name = [i.replace('.csv', '')
                        for i in filename if 'data' not in i and i.endswith('.csv')]
sheet_name.sort(reverse=True)

# dfs = {sheet_name: pd.read_csv('./raw_data/{}.csv'.format(sheet_name))
#          for sheet_name in sheet_name}

# Method #2
# Import xls file and store each sheet in to a df list
# xl_file = pd.ExcelFile('./data.xls')

# dfs = {sheet_name: xl_file.parse(sheet_name)
#          for sheet_name in xl_file.sheet_names}

# Data from each sheet can be accessed via key
# keyList = list(dfs.keys())

# Data cleansing
# for key, df in dfs.items():
#    dfs[key].loc[:,'Confirmed'].fillna(value=0, inplace=True)
#    dfs[key].loc[:,'Deaths'].fillna(value=0, inplace=True)
#    dfs[key].loc[:,'Recovered'].fillna(value=0, inplace=True)
#    dfs[key]=dfs[key].astype({'Confirmed':'int64', 'Deaths':'int64', 'Recovered':'int64'})
#    # Change as China for coordinate search
#    dfs[key]=dfs[key].replace({'Country/Region':'Mainland China'}, 'China')
#    # Add a zero to the date so can be convert by datetime.strptime as 0-padded date
#    dfs[key]['Last Update'] = '0' + dfs[key]['Last Update']
#    # Convert time as Australian eastern daylight time
#    dfs[key]['Date_last_updated_AEDT'] = [datetime.strptime(d, '%m/%d/%Y %H:%M') for d in dfs[key]['Last Update']]
#    dfs[key]['Date_last_updated_AEDT'] = dfs[key]['Date_last_updated_AEDT'] + timedelta(hours=16)
#   #dfs[key]['Remaining'] = dfs[key]['Confirmed'] - dfs[key]['Recovered'] - dfs[key]['Deaths']

# Add coordinates for each area in the list for the latest table sheet
# To save time, coordinates calling was done seperately
# Import the data with coordinates
df_latest = pd.read_csv('{}_data.csv'.format(sheet_name[0]))
df_latest = df_latest.astype({'Date_last_updated_AEDT': 'datetime64'})

# Save numbers into variables to use in the app
confirmedCases = df_latest['Confirmed'].sum()
deathsCases = df_latest['Deaths'].sum()
recoveredCases = df_latest['Recovered'].sum()

# Construct confirmed cases dataframe for line plot and 24-hour window case difference
df_confirmed = pd.read_csv('./lineplot_data/df_confirmed.csv')
df_confirmed = df_confirmed.astype({'Date': 'datetime64'})
plusConfirmedNum = df_confirmed['plusNum'][0]
plusPercentNum1 = df_confirmed['plusPercentNum'][0]

# Construct recovered cases dataframe for line plot and 24-hour window case difference
df_recovered = pd.read_csv('./lineplot_data/df_recovered.csv')
df_recovered = df_recovered.astype({'Date': 'datetime64'})
plusRecoveredNum = df_recovered['plusNum'][0]
plusPercentNum2 = df_recovered['plusPercentNum'][0]

# Construct death case dataframe for line plot and 24-hour window case difference
df_deaths = pd.read_csv('./lineplot_data/df_deaths.csv')
df_deaths = df_deaths.astype({'Date': 'datetime64'})
plusDeathNum = df_deaths['plusNum'][0]
plusPercentNum3 = df_deaths['plusPercentNum'][0]

# Construct remaining case dataframe for line plot and 24-hour window case difference
df_remaining = pd.read_csv('./lineplot_data/df_remaining.csv')
df_remaining = df_remaining.astype({'Date': 'datetime64'})
plusRemainNum = df_remaining['plusNum'][0]
plusRemainNum3 = df_remaining['plusPercentNum'][0]

# Create data table to show in app
# Generate sum values for Country/Region level
dfCase = df_latest.groupby(by='Country/Region', sort=False).sum().reset_index()
dfCase = dfCase.sort_values(
    by=['Confirmed'], ascending=False).reset_index(drop=True)
# As lat and lon also underwent sum(), which is not desired, remove from this table.
dfCase = dfCase.drop(columns=['lat', 'lon'])

# Grep lat and lon by the first instance to represent its Country/Region
dfGPS = df_latest.groupby(
    by='Country/Region', sort=False).first().reset_index()
dfGPS = dfGPS[['Country/Region', 'lat', 'lon']]

# Merge two dataframes
dfSum = pd.merge(dfCase, dfGPS, how='inner', on='Country/Region')
dfSum = dfSum.replace({'Country/Region': 'China'}, 'Mainland China')
dfSum['Remaining'] = dfSum['Confirmed'] - dfSum['Recovered'] - dfSum['Deaths']
# Rearrange columns to correspond to the number plate order
dfSum = dfSum[['Country/Region', 'Remaining',
    'Confirmed', 'Recovered', 'Deaths', 'lat', 'lon']]
# Sort value based on Remaining cases and then Confirmed cases
dfSum = dfSum.sort_values(
    by=['Remaining', 'Confirmed'], ascending=False).reset_index(drop=True)
# Set row ids pass to selected_row_ids
dfSum['id'] = dfSum['Country/Region']
dfSum.set_index('id', inplace=True, drop=False)

# Create tables for tabs
CNTable = make_country_table('China')
AUSTable = make_country_table('Australia')
USTable = make_country_table('US')
CANTable = make_country_table('Canada')

# Remove dummy row of recovered case number in USTable
USTable = USTable.dropna(subset=['Province/State'])

# Save numbers into variables to use in the app
latestDate = datetime.strftime(df_confirmed['Date'][0], '%b %d, %Y %H:%M AEDT')
secondLastDate = datetime.strftime(df_confirmed['Date'][1], '%b %d')
daysOutbreak = (df_confirmed['Date'][0] - datetime.strptime('12/31/2019', '%m/%d/%Y')).days

# Read cumulative data of a given region from ./cumulative_data folder
dfs_curve = pd.read_csv('./lineplot_data/dfs_curve.csv')

# Pseduo data for logplot
pseduoDay = np.arange(1, daysOutbreak+1)
y1 = 100*(1.85)**(pseduoDay-1)  # 85% growth rate
y2 = 100*(1.35)**(pseduoDay-1)  # 35% growth rate
y3 = 100*(1.15)**(pseduoDay-1)  # 15% growth rate
y4 = 100*(1.05)**(pseduoDay-1)  # 5% growth rate

#############################################################################################
# Start to make plots
#############################################################################################
# Line plot for confirmed cases
# Set up tick scale based on confirmed case number
tickList = np.arange(0, df_confirmed['Other locations'].max()+5000, 20000)

# Create empty figure canvas
fig_confirmed = go.Figure()
# Add trace to the figure
fig_confirmed.add_trace(go.Scatter(x=df_confirmed['Date'], y=df_confirmed['Mainland China'],
                                   mode='lines+markers',
                                   line_shape='spline',
                                   name='Mainland China',
                                   line=dict(color='#921113', width=4),
                                   marker=dict(size=4, color='#f4f4f2',
                                               line=dict(width=1, color='#921113')),
                                   text=[datetime.strftime(
                                       d, '%b %d %Y AEDT') for d in df_confirmed['Date']],
                                   hovertext=['Mainland China confirmed<br>{:,d} cases<br>'.format(
                                       i) for i in df_confirmed['Mainland China']],
                                   hovertemplate='<b>%{text}</b><br></br>' +
                                                 '%{hovertext}' +
                                                 '<extra></extra>'))
fig_confirmed.add_trace(go.Scatter(x=df_confirmed['Date'], y=df_confirmed['Other locations'],
                                   mode='lines+markers',
                                   line_shape='spline',
                                   name='Other Region',
                                   line=dict(color='#eb5254', width=4),
                                   marker=dict(size=4, color='#f4f4f2',
                                               line=dict(width=1, color='#eb5254')),
                                   text=[datetime.strftime(
                                       d, '%b %d %Y AEDT') for d in df_confirmed['Date']],
                                   hovertext=['Other region confirmed<br>{:,d} cases<br>'.format(
                                       i) for i in df_confirmed['Other locations']],
                                   hovertemplate='<b>%{text}</b><br></br>' +
                                                 '%{hovertext}' +
                                                 '<extra></extra>'))
# Customise layout
fig_confirmed.update_layout(
#    title=dict(
#    text="<b>Confirmed Cases Timeline<b>",
#    y=0.96, x=0.5, xanchor='center', yanchor='top',
#    font=dict(size=20, color="#292929", family="Playfair Display")
#   ),
    margin=go.layout.Margin(
        l=10,
        r=10,
        b=10,
        t=5,
        pad=0
    ),
    yaxis=dict(
        showline=False, linecolor='#272e3e',
        zeroline=False,
        # showgrid=False,
        gridcolor='rgba(203, 210, 211,.3)',
        gridwidth=.1,
        tickmode='array',
        # Set tick range based on the maximum number
        tickvals=tickList,
        # Set tick label accordingly
        ticktext=["{:.0f}k".format(i/1000) for i in tickList]
    ),
#   yaxis_title="Total Confirmed Case Number",
    xaxis=dict(
        showline=False, linecolor='#272e3e',
        showgrid=False,
        gridcolor='rgba(203, 210, 211,.3)',
        gridwidth=.1,
        zeroline=False
    ),
    xaxis_tickformat='%b %d',
    hovermode='x',
    legend_orientation="h",
#   legend=dict(x=.02, y=.95, bgcolor="rgba(0,0,0,0)",),
    plot_bgcolor='#f4f4f2',
    paper_bgcolor='#cbd2d3',
    font=dict(color='#292929', size=10)
)

# Line plot for combine recovered cases
# Set up tick scale based on total recovered case number
tickList = np.arange(0, df_remaining['Total'].max()+10000, 20000)

# Create empty figure canvas
fig_combine = go.Figure()
# Add trace to the figure
fig_combine.add_trace(go.Scatter(x=df_recovered['Date'], y=df_recovered['Total'],
                                   mode='lines+markers',
                                   line_shape='spline',
                                   name='Total Recovered Cases',
                                   line=dict(color='#168038', width=4),
                                   marker=dict(size=4, color='#f4f4f2',
                                               line=dict(width=1, color='#168038')),
                                   text=[datetime.strftime(
                                       d, '%b %d %Y AEDT') for d in df_recovered['Date']],
                                   hovertext=['Total recovered<br>{:,d} cases<br>'.format(
                                       i) for i in df_recovered['Total']],
                                   hovertemplate='<b>%{text}</b><br></br>' +
                                                 '%{hovertext}' +
                                                 '<extra></extra>'))
fig_combine.add_trace(go.Scatter(x=df_deaths['Date'], y=df_deaths['Total'],
                                mode='lines+markers',
                                line_shape='spline',
                                name='Total Death Cases',
                                line=dict(color='#626262', width=4),
                                marker=dict(size=4, color='#f4f4f2',
                                            line=dict(width=1, color='#626262')),
                                text=[datetime.strftime(
                                    d, '%b %d %Y AEDT') for d in df_deaths['Date']],
                                hovertext=['Total death<br>{:,d} cases<br>'.format(
                                    i) for i in df_deaths['Total']],
                                hovertemplate='<b>%{text}</b><br></br>' +
                                              '%{hovertext}' +
                                              '<extra></extra>'))
fig_combine.add_trace(go.Scatter(x=df_remaining['Date'], y=df_remaining['Total'],
                                mode='lines+markers',
                                line_shape='spline',
                                name='Total Remaining Cases',
                                line=dict(color='#e36209', width=4),
                                marker=dict(size=4, color='#f4f4f2',
                                            line=dict(width=1, color='#e36209')),
                                text=[datetime.strftime(
                                    d, '%b %d %Y AEDT') for d in df_deaths['Date']],
                                hovertext=['Total remaining<br>{:,d} cases<br>'.format(
                                    i) for i in df_remaining['Total']],
                                hovertemplate='<b>%{text}</b><br></br>' +
                                              '%{hovertext}' +
                                              '<extra></extra>'))
# Customise layout
fig_combine.update_layout(
    margin=go.layout.Margin(
        l=10,
        r=10,
        b=10,
        t=5,
        pad=0
    ),
    yaxis=dict(
        showline=False, linecolor='#272e3e',
        zeroline=False,
        # showgrid=False,
        gridcolor='rgba(203, 210, 211,.3)',
        gridwidth=.1,
        tickmode='array',
        # Set tick range based on the maximum number
        tickvals=tickList,
        # Set tick label accordingly
        ticktext=["{:.0f}k".format(i/1000) for i in tickList]
    ),
#    yaxis_title="Total Confirmed Case Number",
    xaxis=dict(
        showline=False, linecolor='#272e3e',
        showgrid=False,
        gridcolor='rgba(203, 210, 211,.3)',
        gridwidth=.1,
        zeroline=False
    ),
    xaxis_tickformat='%b %d',
    hovermode='x',
    legend_orientation="h",
    # legend=dict(x=.02, y=.95, bgcolor="rgba(0,0,0,0)",),
    plot_bgcolor='#f4f4f2',
    paper_bgcolor='#cbd2d3',
    font=dict(color='#292929', size=10)
)

# Line plot for death rate cases
# Set up tick scale based on death case number of Mainland China
tickList = np.arange(0, (df_deaths['Mainland China']/df_confirmed['Mainland China']*100).max()+0.2, 0.5)

# Create empty figure canvas
fig_rate = go.Figure()
# Add trace to the figure
fig_rate.add_trace(go.Scatter(x=df_deaths['Date'], y=df_deaths['Mainland China']/df_confirmed['Mainland China']*100,
                                mode='lines+markers',
                                line_shape='spline',
                                name='Mainland China',
                                line=dict(color='#626262', width=4),
                                marker=dict(size=4, color='#f4f4f2',
                                            line=dict(width=1, color='#626262')),
                                text=[datetime.strftime(
                                    d, '%b %d %Y AEDT') for d in df_deaths['Date']],
                                hovertext=['Mainland China death rate<br>{:.2f}%'.format(
                                    i) for i in df_deaths['Mainland China']/df_confirmed['Mainland China']*100],
                                hovertemplate='<b>%{text}</b><br></br>' +
                                              '%{hovertext}' +
                                              '<extra></extra>'))
fig_rate.add_trace(go.Scatter(x=df_deaths['Date'], y=df_deaths['Other locations']/df_confirmed['Other locations']*100,
                                mode='lines+markers',
                                line_shape='spline',
                                name='Other Region',
                                line=dict(color='#a7a7a7', width=4),
                                marker=dict(size=4, color='#f4f4f2',
                                            line=dict(width=1, color='#a7a7a7')),
                                text=[datetime.strftime(
                                    d, '%b %d %Y AEDT') for d in df_deaths['Date']],
                                hovertext=['Other region death rate<br>{:.2f}%'.format(
                                    i) for i in df_deaths['Other locations']/df_confirmed['Other locations']*100],
                                hovertemplate='<b>%{text}</b><br></br>' +
                                              '%{hovertext}' +
                                              '<extra></extra>'))

# Customise layout
fig_rate.update_layout(
    margin=go.layout.Margin(
        l=10,
        r=10,
        b=10,
        t=5,
        pad=0
    ),
    yaxis=dict(
        showline=False, linecolor='#272e3e',
        zeroline=False,
        # showgrid=False,
        gridcolor='rgba(203, 210, 211,.3)',
        gridwidth=.1,
        tickmode='array',
        # Set tick range based on the maximum number
        tickvals=tickList,
        # Set tick label accordingly
        ticktext=['{:.1f}'.format(i) for i in tickList]
    ),
#    yaxis_title="Total Confirmed Case Number",
    xaxis=dict(
        showline=False, linecolor='#272e3e',
        showgrid=False,
        gridcolor='rgba(203, 210, 211,.3)',
        gridwidth=.1,
        zeroline=False
    ),
    xaxis_tickformat='%b %d',
    hovermode='x',
    legend_orientation="h",
    # legend=dict(x=.02, y=.95, bgcolor="rgba(0,0,0,0)",),
    plot_bgcolor='#f4f4f2',
    paper_bgcolor='#cbd2d3',
    font=dict(color='#292929', size=10)
)

##################################################################################################
# Start dash app
##################################################################################################

app = dash.Dash(__name__,
                assets_folder='./assets/',
                meta_tags=[
                    {"name": "author", "content": "Jun Ye"},
                    {"name": "description", "content": "The coronavirus COVID-19 monitor provides up-to-date data for the global spread of coronavirus."},
                    {"property": "og:title",
                        "content": "Coronavirus COVID-19 Outbreak Global Cases Monitor"},
                    {"property": "og:type", "content": "website"},
                    {"property": "og:image", "content": "https://junye0798.com/post/build-a-dashboard-to-track-the-spread-of-coronavirus-using-dash/featured_hu031431b9019186307c923e911320563b_1304417_1200x0_resize_lanczos_2.png"},
                    {"property": "og:url",
                        "content": "https://dash-coronavirus-2020.herokuapp.com/"},
                    {"property": "og:description",
                        "content": "The coronavirus COVID-19 monitor provides up-to-date data for the global spread of coronavirus."},
                    {"name": "twitter:card", "content": "summary_large_image"},
                    {"name": "twitter:site", "content": "@perishleaf"},
                    {"name": "twitter:title",
                        "content": "Coronavirus COVID-19 Outbreak Global Cases Monitor"},
                    {"name": "twitter:description",
                        "content": "The coronavirus COVID-19 monitor provides up-to-date data for the global spread of coronavirus."},
                    {"name": "twitter:image", "content": "https://junye0798.com/post/build-a-dashboard-to-track-the-spread-of-coronavirus-using-dash/featured_hu031431b9019186307c923e911320563b_1304417_1200x0_resize_lanczos_2.png"},
                    {"name": "viewport",
                        "content": "width=device-width, height=device-height, initial-scale=1.0"}
                ]
      )

app.title = 'Coronavirus COVID-19 Global Monitor'

# Section for Google annlytic and donation #
app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <script data-name="BMC-Widget" src="https://cdnjs.buymeacoffee.com/1.0.0/widget.prod.min.js" data-id="qPsBJAV" data-description="Support the app server for running!" data-message="Please support the app server for running!" data-color="#FF813F" data-position="right" data-x_margin="18" data-y_margin="18"></script>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-154901818-2"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          gtag('config', 'UA-154901818-2');
        </script>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <script type='text/javascript' src='https://platform-api.sharethis.com/js/sharethis.js#property=5e5e32508d3a3d0019ee3ecb&product=sticky-share-buttons&cms=website' async='async'></script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

server = app.server

app.layout = html.Div(style={'backgroundColor': '#f4f4f2'},
    children=[
        html.Div(
            id="header",
            children=[
                html.H4(
                    children="Coronavirus (COVID-19) Outbreak Global Cases Monitor"),
                html.P(
                    id="description",
                    children="On Dec 31, 2019, the World Health Organization (WHO) was informed of \
                    an outbreak of “pneumonia of unknown cause” detected in Wuhan City, Hubei Province, China – the \
                    seventh-largest city in China with 11 million residents. As of {}, there are over {:,d} cases \
                    of COVID-19 confirmed globally.\
                    This dash board is developed to visualise and track the recent reported \
                    cases on a hourly timescale.".format(latestDate, confirmedCases),
                ),
 #              html.P(
 #                id="note",
 #                children=['⚠️ Source from ',
 #                html.A('The National Health Commission of China', href='http://www.nhc.gov.cn/yjb/s7860/202002/553ff43ca29d4fe88f3837d49d6b6ef1.shtml'),
 #                ': in its February 14 official report, deducted \
 #                 108 previously reported deaths and 1,043 previously reported cases from the total in Hubei Province due to "repeated counting." \
 #                Data have been corrected for these changes.']
 #               ),
 #              html.P(
 #                id="note",
 #                children=['⚠️ Source from ',
 #                html.A('读卖新闻', href='https://www.yomiuri.co.jp/national/20200216-OYT1T50089/'),
 #                ': Diamond Princess cruise confirmed 70 new infections, bringing the total infected cases to 355.']
 #               ),
 #                html.P(
 #                 id="note",
 #                 children=['⚠️ Source from ',
 #                           html.A('anews', href='http://www.anews.com.tr/world/2020/02/21/iran-says-two-more-deaths-among-13-new-coronavirus-cases'),
 #                           ': Iran\'s health ministry Friday reported two more deaths among 13 new cases of coronavirus in the Islamic republic, bringing the total number of deaths to four and infections to 18.']
 #               ),
 #               html.P(
 #                 id="note",
 #                 children=['⚠️ Source from ',
 #                           html.A('The New York Times', href='https://www.nytimes.com/2020/03/01/world/coronavirus-news.html'),
 #                           ': New York State Reports First Case.']
 #                ),
                html.P(
                  id='time-stamp',
                  # style={'fontWeight':'bold'},
                       children="🔴 Last update: {} (Sorry, the app server may experience a short period of interruption while updating data)".format(latestDate))
                    ]
                ),
        html.Div(
            id="number-plate",
            style={'marginLeft': '1.5%',
                'marginRight': '1.5%', 'marginBottom': '.5%'},
                 children=[
                     html.Div(
                         style={'width': '24.4%', 'backgroundColor': '#cbd2d3', 'display': 'inline-block',
                                'marginRight': '.8%', 'verticalAlign': 'top'},
                              children=[
                                  html.H3(style={'textAlign': 'center',
                                                 'fontWeight': 'bold', 'color': '#2674f6'},
                                               children=[
                                                   html.P(style={'color': '#cbd2d3', 'padding': '.5rem'},
                                                              children='xxxx xx xxx xxxx xxx xxxxx'),
                                                   '{}'.format(daysOutbreak),
                                               ]),
                                  html.H5(style={'textAlign': 'center', 'color': '#2674f6', 'padding': '.1rem'},
                                               children="Days Since Outbreak")
                                       ]),
                     html.Div(
                         style={'width': '24.4%', 'backgroundColor': '#cbd2d3', 'display': 'inline-block',
                                'marginRight': '.8%', 'verticalAlign': 'top'},
                              children=[
                                  html.H3(style={'textAlign': 'center',
                                                 'fontWeight': 'bold', 'color': '#d7191c'},
                                                children=[
                                                    html.P(style={'padding': '.5rem'},
                                                              children='+ {:,d} in the past 24h ({:.1%})'.format(plusConfirmedNum, plusPercentNum1)),
                                                    '{:,d}'.format(
                                                        confirmedCases)
                                                         ]),
                                  html.H5(style={'textAlign': 'center', 'color': '#d7191c', 'padding': '.1rem'},
                                               children="Confirmed Cases")
                                       ]),
                     html.Div(
                         style={'width': '24.4%', 'backgroundColor': '#cbd2d3', 'display': 'inline-block',
                                'marginRight': '.8%', 'verticalAlign': 'top'},
                              children=[
                                  html.H3(style={'textAlign': 'center',
                                                       'fontWeight': 'bold', 'color': '#1a9622'},
                                               children=[
                                                   html.P(style={'padding': '.5rem'},
                                                              children='+ {:,d} in the past 24h ({:.1%})'.format(plusRecoveredNum, plusPercentNum2)),
                                                   '{:,d}'.format(
                                                       recoveredCases),
                                               ]),
                                  html.H5(style={'textAlign': 'center', 'color': '#1a9622', 'padding': '.1rem'},
                                               children="Recovered Cases")
                                       ]),
                     html.Div(
                         style={'width': '24.4%', 'backgroundColor': '#cbd2d3', 'display': 'inline-block',
                                'verticalAlign': 'top'},
                              children=[
                                  html.H3(style={'textAlign': 'center',
                                                       'fontWeight': 'bold', 'color': '#6c6c6c'},
                                                children=[
                                                    html.P(style={'padding': '.5rem'},
                                                              children='+ {:,d} in the past 24h ({:.1%})'.format(plusDeathNum, plusPercentNum3)),
                                                    '{:,d}'.format(deathsCases)
                                                ]),
                                  html.H5(style={'textAlign': 'center', 'color': '#6c6c6c', 'padding': '.1rem'},
                                               children="Death Cases")
                                       ])
                          ]),
        html.Div(
            id='dcc-plot',
            style={'marginLeft': '1.5%', 'marginRight': '1.5%',
                'marginBottom': '.35%', 'marginTop': '.5%'},
                 children=[
                     html.Div(
                         style={'width': '32.79%', 'display': 'inline-block',
                             'marginRight': '.8%', 'verticalAlign': 'top'},
                              children=[
                                  html.H5(style={'textAlign': 'center', 'backgroundColor': '#cbd2d3',
                                                 'color': '#292929', 'padding': '1rem', 'marginBottom': '0'},
                                               children='Confirmed Case Timeline'),
                                  dcc.Graph(style={'height': '300px'}, figure=fig_confirmed)]),
                     html.Div(
                         style={'width': '32.79%', 'display': 'inline-block',
                             'marginRight': '.8%', 'verticalAlign': 'top'},
                              children=[
                                  html.H5(style={'textAlign': 'center', 'backgroundColor': '#cbd2d3',
                                                 'color': '#292929', 'padding': '1rem', 'marginBottom': '0'},
                                               children='Remaining/Recovered/Death Case Timeline'),
                                  dcc.Graph(style={'height': '300px'}, figure=fig_combine)]),
                     html.Div(
                         style={'width': '32.79%', 'display': 'inline-block',
                             'verticalAlign': 'top'},
                              children=[
                                  html.H5(style={'textAlign': 'center', 'backgroundColor': '#cbd2d3',
                                                 'color': '#292929', 'padding': '1rem', 'marginBottom': '0'},
                                               children='Death Rate (%) Timeline'),
                                  dcc.Graph(style={'height': '300px'}, figure=fig_rate)])]),
        html.Div(
            id='dcc-map',
            style={'marginLeft': '1.5%',
                'marginRight': '1.5%', 'marginBottom': '.5%'},
                 children=[
                     html.Div(style={'width': '66.41%', 'marginRight': '.8%', 'display': 'inline-block', 'verticalAlign': 'top'},
                              children=[
                                  html.H5(style={'textAlign': 'center', 'backgroundColor': '#cbd2d3',
                                                 'color': '#292929', 'padding': '1rem', 'marginBottom': '0'},
                                               children='Latest Coronavirus Outbreak Map'),
                                  dcc.Graph(
                                      id='datatable-interact-map',
                                      style={'height': '500px'},),
                                  dcc.Graph(
                                      id='datatable-interact-lineplot',
                                      style={'height': '300px'},),
                                  dcc.Graph(
                                      id='datatable-interact-logplot',
                                      style={'height': '300px'},),
                              ]),
                     html.Div(style={'width': '32.79%', 'display': 'inline-block', 'verticalAlign': 'top'},
                              children=[
                                  html.H5(style={'textAlign': 'center', 'backgroundColor': '#cbd2d3',
                                                 'color': '#292929', 'padding': '1rem', 'marginBottom': '0'},
                                               children='Cases by Country/Region'),
                                  dcc.Tabs(
                                      id="tabs-table",
                                      value='tab-1',
                                      parent_className='custom-tabs',
                                      className='custom-tabs-container',
                                      children=[
                                          dcc.Tab(label='The World',
                                              value='tab-1',
                                              className='custom-tab',
                                              selected_className='custom-tab--selected',
                                              children=[
                                                  dash_table.DataTable(
                                                      id='datatable-interact-location',
                                                      # Don't show coordinates
                                                      columns=[{"name": i, "id": i}
                                                          for i in dfSum.columns[0:5]],
                                                      # But still store coordinates in the table for interactivity
                                                      data=dfSum.to_dict(
                                                          "rows"),
                                                      row_selectable="single",
                                                      sort_action="native",
                                                      style_as_list_view=True,
                                                      style_cell={'font_family': 'Arial',
                                                                  'font_size': '1.2rem',
                                                                  'padding': '.1rem',
                                                                  'backgroundColor': '#f4f4f2', },
                                                      fixed_rows={
                                                          'headers': True, 'data': 0},
                                                      style_table={'minHeight': '1050px',
                                                                   'height': '1050px',
                                                                   'maxHeight': '1050px'},
                                                      style_header={'backgroundColor': '#f4f4f2',
                                                                    'fontWeight': 'bold'},
                                                      style_cell_conditional=[{'if': {'column_id': 'Country/Regions'}, 'width': '28%'},
                                                                              {'if': {
                                                                                  'column_id': 'Remaining'}, 'width': '18%'},
                                                                              {'if': {
                                                                                  'column_id': 'Confirmed'}, 'width': '18%'},
                                                                              {'if': {
                                                                                  'column_id': 'Recovered'}, 'width': '18%'},
                                                                              {'if': {
                                                                                  'column_id': 'Deaths'}, 'width': '18%'},
                                                                              {'if': {
                                                                                  'column_id': 'Confirmed'}, 'color': '#d7191c'},
                                                                              {'if': {
                                                                                  'column_id': 'Recovered'}, 'color': '#1a9622'},
                                                                              {'if': {
                                                                                  'column_id': 'Deaths'}, 'color': '#6c6c6c'},
                                                                              {'textAlign': 'center'}],
                                                  )
                                          ]),
                                          make_dcc_country_tab(
                                              'Australia', AUSTable),
                                          make_dcc_country_tab(
                                              'Canada', CANTable),
                                          make_dcc_country_tab(
                                              'Mainland China', CNTable),
                                          make_dcc_country_tab(
                                              'United States', USTable),
                                      ]
                                  )
                              ])
                 ]),
        html.Div(
          id='my-footer',
          style={'marginLeft': '1.5%', 'marginRight': '1.5%'},
                 children=[
                     html.P(style={'textAlign': 'center', 'margin': 'auto'},
                            children=[" 🙏 God Bless the World 🙏 |",
                                      " Developed by ", html.A('Jun', href='https://junye0798.com/'), " with ❤️ in Sydney"])]),
        ])


@app.callback(
    Output('datatable-interact-map', 'figure'),
    [Input('datatable-interact-location', 'derived_virtual_selected_rows'),
     Input('datatable-interact-location', 'selected_row_ids')]
)
def update_figures(derived_virtual_selected_rows, selected_row_ids):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncracy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.

    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = dfSum

    mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"

    # Generate a list for hover text display
    textList = []
    for area, region in zip(df_latest['Province/State'], df_latest['Country/Region']):

        if type(area) is str:
            if region == "Hong Kong" or region == "Macau" or region == "Taiwan":
                textList.append(area)
            else:
                textList.append(area+', '+region)
        else:
            textList.append(region)

    # Generate a list for color gradient display
    colorList = []

    for comfirmed, recovered, deaths in zip(df_latest['Confirmed'], df_latest['Recovered'], df_latest['Deaths']):
        remaining = comfirmed - deaths - recovered
        colorList.append(remaining)

    fig2 = go.Figure(go.Scattermapbox(
        lat=df_latest['lat'],
        lon=df_latest['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            color=['#d7191c' if i > 0 else '#1a9622' for i in colorList],
            size=[i**(1/3) for i in df_latest['Confirmed']],
            sizemin=1,
            sizemode='area',
            sizeref=2.*max([math.sqrt(i)
                           for i in df_latest['Confirmed']])/(100.**2),
        ),
        text=textList,
        hovertext=['Confirmed: {:,d}<br>Recovered: {:,d}<br>Death: {:,d}'.format(i, j, k) for i, j, k in zip(df_latest['Confirmed'],
                                                                                                             df_latest['Recovered'],
                                                                                                             df_latest['Deaths'])],
        hovertemplate="<b>%{text}</b><br><br>" +
                        "%{hovertext}<br>" +
                        "<extra></extra>")
    )
    fig2.update_layout(
        plot_bgcolor='#151920',
        paper_bgcolor='#cbd2d3',
        margin=go.layout.Margin(l=10, r=10, b=10, t=0, pad=40),
        hovermode='closest',
        transition={'duration': 50},
        annotations=[
        dict(
            x=.5,
            y=-.01,
            align='center',
            showarrow=False,
            text="Points are placed based on data geolocation levels.<br>Province/State level - Australia, China, Canada, and United States; Country level- other countries.",
            xref="paper",
            yref="paper",
            font=dict(size=10, color='#292929'),
        )],
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            style="light",
            # The direction you're facing, measured clockwise as an angle from true north on a compass
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=14.056159 if len(
                    derived_virtual_selected_rows) == 0 else dff.loc[selected_row_ids[0]].lat,
                lon=6.395626 if len(
                    derived_virtual_selected_rows) == 0 else dff.loc[selected_row_ids[0]].lon
            ),
            pitch=0,
            zoom=1.02 if len(derived_virtual_selected_rows) == 0 else 4
        )
    )

    return fig2


@app.callback(
    Output('datatable-interact-lineplot', 'figure'),
    [Input('datatable-interact-location', 'derived_virtual_selected_rows'),
     Input('datatable-interact-location', 'selected_row_ids')]
)
def update_lineplot(derived_virtual_selected_rows, selected_row_ids):

    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = dfSum

    if selected_row_ids:
        if dff.loc[selected_row_ids[0]]['Country/Region'] == 'Mainland China':
            Region = 'China'
        else:
            Region = dff.loc[selected_row_ids[0]]['Country/Region']
    else:
        Region = 'Australia'

    # Read cumulative data of a given region from ./cumulative_data folder
    df_region = pd.read_csv('./cumulative_data/{}.csv'.format(Region))
    df_region = df_region.astype(
        {'Date_last_updated_AEDT': 'datetime64', 'date_day': 'datetime64'})

    # Line plot for confirmed cases
    # Set up tick scale based on confirmed case number
    # tickList = list(np.arange(0, df_confirmed['Mainland China'].max()+1000, 10000))

    # Create empty figure canvas
    fig3 = go.Figure()
    # Add trace to the figure
    fig3.add_trace(go.Scatter(x=df_region['date_day'],
                             y=df_region['Confirmed'],
                             mode='lines+markers',
                             # line_shape='spline',
                             name='Confirmed case',
                             line=dict(color='#d7191c', width=2),
                             # marker=dict(size=4, color='#f4f4f2',
                             #            line=dict(width=1,color='#921113')),
                             text=[datetime.strftime(d, '%b %d %Y AEDT')
                                                     for d in df_region['date_day']],
                             hovertext=['{} Confirmed<br>{:,d} cases<br>'.format(
                                 Region, i) for i in df_region['Confirmed']],
                             hovertemplate='<b>%{text}</b><br></br>' +
                                                     '%{hovertext}' +
                                                     '<extra></extra>'))
    fig3.add_trace(go.Scatter(x=df_region['date_day'],
                             y=df_region['Recovered'],
                             mode='lines+markers',
                             # line_shape='spline',
                             name='Recovered case',
                             line=dict(color='#1a9622', width=2),
                             # marker=dict(size=4, color='#f4f4f2',
                             #            line=dict(width=1,color='#168038')),
                             text=[datetime.strftime(d, '%b %d %Y AEDT')
                                                     for d in df_region['date_day']],
                             hovertext=['{} Recovered<br>{:,d} cases<br>'.format(
                                 Region, i) for i in df_region['Recovered']],
                             hovertemplate='<b>%{text}</b><br></br>' +
                                                     '%{hovertext}' +
                                                     '<extra></extra>'))
    fig3.add_trace(go.Scatter(x=df_region['date_day'],
                             y=df_region['Deaths'],
                             mode='lines+markers',
                             # line_shape='spline',
                             name='Death case',
                             line=dict(color='#626262', width=2),
                             # marker=dict(size=4, color='#f4f4f2',
                             #            line=dict(width=1,color='#626262')),
                             text=[datetime.strftime(d, '%b %d %Y AEDT')
                                                     for d in df_region['date_day']],
                             hovertext=['{} Deaths<br>{:,d} cases<br>'.format(
                                 Region, i) for i in df_region['Deaths']],
                             hovertemplate='<b>%{text}</b><br></br>' +
                                                     '%{hovertext}' +
                                                     '<extra></extra>'))

    # Customise layout
    fig3.update_layout(
        margin=go.layout.Margin(
            l=10,
            r=10,
            b=10,
            t=5,
            pad=0
        ),
        annotations=[
            dict(
                x=.5,
                y=.4,
                xref="paper",
                yref="paper",
                text=Region,
                opacity=0.5,
                font=dict(family='Arial, sans-serif',
                          size=60,
                          color="grey"),
            )
        ],
        yaxis_title="Cumulative cases numbers",
        yaxis=dict(
            showline=False, linecolor='#272e3e',
            zeroline=False,
            # showgrid=False,
            gridcolor='rgba(203, 210, 211,.3)',
            gridwidth=.1,
            tickmode='array',
            # Set tick range based on the maximum number
            # tickvals=tickList,
            # Set tick label accordingly
            # ticktext=["{:.0f}k".format(i/1000) for i in tickList]
        ),
        xaxis_title="Select Country/Region From Table",
        xaxis=dict(
            showline=False, linecolor='#272e3e',
            showgrid=False,
            gridcolor='rgba(203, 210, 211,.3)',
            gridwidth=.1,
            zeroline=False
        ),
        xaxis_tickformat='%b %d',
        # transition = {'duration':500},
        hovermode='x',
        legend_orientation="h",
        legend=dict(x=.02, y=.95, bgcolor="rgba(0,0,0,0)",),
        plot_bgcolor='#f4f4f2',
        paper_bgcolor='#cbd2d3',
        font=dict(color='#292929', size=10)
    )

    return fig3


@app.callback(
    Output('datatable-interact-logplot', 'figure'),
    [Input('datatable-interact-location', 'derived_virtual_selected_rows'),
     Input('datatable-interact-location', 'selected_row_ids')]
)
def update_logplot(derived_virtual_selected_rows, selected_row_ids):

    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = dfSum

    elapseDay = daysOutbreak

    if selected_row_ids:
        if dff.loc[selected_row_ids[0]]['Country/Region'] == 'Mainland China':
            Region = 'China'
        else:
            Region = dff.loc[selected_row_ids[0]]['Country/Region']
    else:
        Region = 'Australia'

    # Create empty figure canvas
    fig_curve = go.Figure()

    fig_curve.add_trace(go.Scatter(x=pseduoDay,
                                   y=y1,
                                   line=dict(color='rgba(0, 0, 0, .3)', width=1, dash='dot'),
                                   text=[
                                       '85% growth rate' for i in pseduoDay],
                                   hovertemplate='<b>%{text}</b><br>' +
                                                 '<extra></extra>'
                            )
    )
    fig_curve.add_trace(go.Scatter(x=pseduoDay,
                                   y=y2,
                                   line=dict(color='rgba(0, 0, 0, .3)', width=1, dash='dot'),
                                   text=[
                                        '35% growth rate' for i in pseduoDay],
                                   hovertemplate='<b>%{text}</b><br>' +
                                                 '<extra></extra>'
                            )
    )
    fig_curve.add_trace(go.Scatter(x=pseduoDay,
                                   y=y3,
                                   line=dict(color='rgba(0, 0, 0, .3)', width=1, dash='dot'),
                                   text=[
                                        '15% growth rate' for i in pseduoDay],
                                   hovertemplate='<b>%{text}</b><br>' +
                                                 '<extra></extra>'
                            )
    )
    fig_curve.add_trace(go.Scatter(x=pseduoDay,
                                   y=y4,
                                   line=dict(color='rgba(0, 0, 0, .3)', width=1, dash='dot'),
                                   text=[
                                        '5% growth rate' for i in pseduoDay],
                                   hovertemplate='<b>%{text}</b><br>' +
                                                 '<extra></extra>'
                            )
    )

    # Add trace to the figure
    if Region in set(dfs_curve['Region']):

        dotx = [np.array(dfs_curve.loc[dfs_curve['Region'] == Region,'DayElapsed'])[0]]
        doty = [np.array(dfs_curve.loc[dfs_curve['Region'] == Region,'Confirmed'])[0]]

        for regionName in ['China', 'Japan', 'Italy', 'South Korea', 'Singapore']:

          dotgrayx = [np.array(dfs_curve.loc[dfs_curve['Region'] == regionName, 'DayElapsed'])[0]]
          dotgrayy = [np.array(dfs_curve.loc[dfs_curve['Region'] == regionName, 'Confirmed'])[0]]


          fig_curve.add_trace(go.Scatter(x=dfs_curve.loc[dfs_curve['Region'] == regionName]['DayElapsed'],
                                         y=dfs_curve.loc[dfs_curve['Region'] == regionName]['Confirmed'],
                                         mode='lines',
                                         line_shape='spline',
                                         name=regionName,
                                         opacity=0.3,
                                         line=dict(color='#636363', width=1.5),
                                         text=[
                                            i for i in dfs_curve.loc[dfs_curve['Region'] == regionName]['Region']],
                                         hovertemplate='<b>%{text}</b><br>' +
                                                       '<br>%{x} days after 100 cases<br>' +
                                                       'with %{y:,d} cases<br>'
                                                       '<extra></extra>'
                             )
          )
          fig_curve.add_trace(go.Scatter(x=dotgrayx,
                                         y=dotgrayy,
                                         mode='markers',
                                         marker=dict(size=6, color='#636363',
                                         line=dict(width=1, color='#636363')),
                                         opacity=0.5,
                                         text=[regionName],
                                         hovertemplate='<b>%{text}</b><br>' +
                                                       '<br>%{x} days after 100 cases<br>' +
                                                       'with %{y:,d} cases<br>'
                                                       '<extra></extra>'
                            )
          )
          
        fig_curve.add_trace(go.Scatter(x=dfs_curve.loc[dfs_curve['Region'] == Region]['DayElapsed'],
                                       y=dfs_curve.loc[dfs_curve['Region'] == Region]['Confirmed'],
                                       mode='lines',
                                       line_shape='spline',
                                       name=Region,
                                       line=dict(color='#d7191c', width=3),
                                       text=[
                                           i for i in dfs_curve.loc[dfs_curve['Region'] == Region]['Region']],
                                       hovertemplate='<b>%{text}</b><br>' +
                                                     '<br>%{x} days after 100 cases<br>' +
                                                     'with %{y:,d} cases<br>'
                                                     '<extra></extra>'
                            )
          )
        fig_curve.add_trace(go.Scatter(x=dotx,
                                       y=doty,
                                       mode='markers',
                                       marker=dict(size=7, color='#d7191c',
                                       line=dict(width=1, color='#d7191c')),
                                       text=[Region],
                                       hovertemplate='<b>%{text}</b><br>' +
                                                     '<br>%{x} days after 100 cases<br>' +
                                                     'with %{y:,d} cases<br>'
                                                     '<extra></extra>'
                            )
        )

    else:
        for regionName in ['China', 'Japan', 'Italy', 'South Korea', 'Singapore']:

          dotgrayx = [np.array(dfs_curve.loc[dfs_curve['Region'] == regionName, 'DayElapsed'])[0]]
          dotgrayy = [np.array(dfs_curve.loc[dfs_curve['Region'] == regionName, 'Confirmed'])[0]]

          fig_curve.add_trace(go.Scatter(x=dfs_curve.loc[dfs_curve['Region'] == regionName]['DayElapsed'],
                                         y=dfs_curve.loc[dfs_curve['Region'] == regionName]['Confirmed'],
                                         mode='lines',
                                         line_shape='spline',
                                         name=regionName,
                                         opacity=0.3,
                                         line=dict(color='#636363', width=1.5),
                                         text=[
                                            i for i in dfs_curve.loc[dfs_curve['Region'] == regionName]['Region']],
                                         hovertemplate='<b>%{text}</b><br>' +
                                                       '<br>%{x} days after 100 cases<br>' +
                                                       'with %{y:,d} cases<br>'
                                                       '<extra></extra>'
                             )
          )

          fig_curve.add_trace(go.Scatter(x=dotgrayx,
                                         y=dotgrayy,
                                         mode='markers',
                                         marker=dict(size=6, color='#636363',
                                         line=dict(width=1, color='#636363')),
                                         opacity=0.5,
                                         text=[regionName],
                                         hovertemplate='<b>%{text}</b><br>' +
                                                       '<br>%{x} days after 100 cases<br>' +
                                                       'with %{y:,d} cases<br>'
                                                       '<extra></extra>'
                            )
          )

    # Customise layout
    fig_curve.update_xaxes(range=[0, elapseDay-19])
    fig_curve.update_yaxes(range=[1.9, 5.1])
    fig_curve.update_layout(
        xaxis_title="Number of day since 100th confirmed cases",
        yaxis_title="Confirmed cases (Logarithmic)",
        margin=go.layout.Margin(
            l=10,
            r=10,
            b=10,
            t=5,
            pad=0
            ),
        annotations=[dict(
            x=.5,
            y=.4,
            xref="paper",
            yref="paper",
            text=Region if Region in set(dfs_curve['Region']) else "Not over 100 cases",
            opacity=0.5,
            font=dict(family='Arial, sans-serif',
                      size=60,
                      color="grey"),
                    )
        ],
        yaxis_type="log",
        yaxis=dict(
            showline=False, 
            linecolor='#272e3e',
            zeroline=False,
            # showgrid=False,
            gridcolor='rgba(203, 210, 211,.3)',
            gridwidth = .1,
        ),
        xaxis=dict(
            showline=False, 
            linecolor='#272e3e',
            # showgrid=False,
            gridcolor='rgba(203, 210, 211,.3)',
            gridwidth = .1,
            zeroline=False
        ),
        showlegend=False,
        # hovermode = 'x',
        plot_bgcolor='#f4f4f2',
        paper_bgcolor='#cbd2d3',
        font=dict(color='#292929', size=10)
    )

    return fig_curve


if __name__ == "__main__":
    app.run_server(debug=True)

