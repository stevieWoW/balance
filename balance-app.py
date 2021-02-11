import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import *
import dash_daq as daq
import configparser
import MySQLdb
import pandas.io.sql as psql
import numpy as np
import datetime
import logging
import pandas as pd
import databaseapp as db
import queryapp as query

logging.basicConfig(format = '%(asctime)s ' + "[%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s", filename='/var/log/dash/balance.log', level = logging.DEBUG)

# load balance data and add Total column
dfbalance = query.queryapp.LoadData('dfbalance')
# load income data
dfincome = query.queryapp.LoadData('dfincome')
# load bank accounts
bank_accounts = query.queryapp.LoadData('BankAccount')

app = dash.Dash(__name__, meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])

app.layout = html.Div(children=[
    ####### Container #######
    html.Div(
        id='container',
        className='col-10 container',
        children=[
            ####### sidemenu #######
            html.Div(
                id='sidemenu',
                className='col-2 frozen sidenav',
                children=[
                    html.H1('Settings',
                        id='settingshead',
                    ),
                    html.Hr(
                        id='graphhr',
                        style={'border-color':'rgb(17,17,17)'}
                    ),
                    html.H4('Year',
                        id='year',
                    ),
                    dcc.RangeSlider(
                        id='year-rangeslider',
                        min=int(dfbalance['YEAR'].min()),
                        # max is always the current year
                        max=int(datetime.datetime.now().year),
                        allowCross=False,
                        updatemode='mouseup',
                        # set marks in the slider. Starts with the min Year -1 so Dash starts with the min year
                        # and ends with the current year. 
                        marks={i + 1: '{}'.format(i + 1) for i in range(int(dfbalance['YEAR'].min()) -1 ,int(datetime.datetime.now().year),1)},
                        step=1,
                        # value = previous year and this year
                        value=[int(datetime.datetime.now().year) - 1, int(datetime.datetime.now().year)]
                    ),
                    html.H4('account',
                        id='account',
                    ),
                    dcc.Dropdown(
                        id='dropdown-bankaccount',
                        className='dropdown bankaccount',
                        options=bank_accounts,
                        value=['Total'],
                        #value=bank_account_options.BNR,
                        multi=True
                    )
                ]
            ), ####### close sidemenu #######
            ####### Graph-1 #######
            html.Div(
                id='graph-1',
                className='col-7 frozen',
                children=[
                    dcc.Graph(
                        id='balance-graph-1',
                        figure={
                            'layout' :{
                                'title':'Balance',
                                'paper_bgcolor': 'rgba(0,0,0,0)',
                                'plot_bgcolor': 'rgba(0,0,0,0)',
                            }
                        }
                    )
                ]  
            ), ####### close Graph-1 #######
            ####### Graph-1 #######
            html.Div(
                id='graph-2',
                className='col-5 frozen',
                children=[
                    dcc.Checklist(
                        id='income-checklist',
                        options=[
                            {'label':'INCOME', 'value':'INCOME'},
                            {'label':'STATUTORY LEVIES', 'value':'STATUTORY_LEVIES'},
                            {'label':'NET INCOME', 'value':'NET_INCOME'}
                        ],
                        value=['NET_INCOME','INCOME'],
                        labelStyle={'display': 'inline-block'}
                    ),
                    dcc.Graph(
                        id='income-graph-2',
                        figure={
                            'layout' :{
                                'title':'Income',
                                'paper_bgcolor': 'rgba(0,0,0,0)',
                                'plot_bgcolor': 'rgba(0,0,0,0)',
                            }
                        }
                    )
                ]  
            ), ####### close Graph-1 #######
            ####### Tank-1 #######
            html.Div(
                id='tank-1',
                className='col-1 frozen',
                children=[
                    daq.Tank(
                        id='money-tank-1',
                        className='tank',
                        showCurrentValue=True,
                        units='€',
                        label='- Goal -',
                        labelPosition='top',
                        # get last of total column and define as value
                        value=int(dfbalance["Total"].tail(1)),
                        min=0,
                        max=100000
                    ),
                ]
            ) ####### Close Tank-1 #######
           
        ]
    ) ####### Close Container #######
    
]) ####### close root div #######

@app.callback(
    Output('dropdown-bankaccount','options'),
    [Input('year-rangeslider','value')]
)
def UpdateDropDown(year):
    # update Dropdown, so new or deleted bankaccounts are taking into account
    return query.queryapp.LoadData('BankAccount')

@app.callback(
    (Output('balance-graph-1','figure')),
    [Input('dropdown-bankaccount','value'),
     Input('year-rangeslider','value')]
)
def UpdateBalanceGraph(bankaccount,year):
    # load balance data and add Total column
    dfbalance = query.queryapp.LoadData('dfbalance')

    data=[]
    
    #iterates over each bankaccount
    for account in bankaccount:
        #get the data for each year
        for y in range(year[0],year[1] + 1):
            #append the data to a list
            data.append({'x':dfbalance.loc[dfbalance['YEAR'] == y,"MONTH" ],'y':dfbalance.loc[dfbalance['YEAR'] == y,account ],'type': 'scatter', 'name':'{0}({1})'.format(account,y)})
    
    figure = {
        'data':data,
            'layout': {
                'title': 'Balance',
                'paper_bgcolor': 'rgba(0,0,0,0)',
                'plot_bgcolor': 'rgba(0,0,0,0)',
            }
            
    }

    return figure

@app.callback(
    (Output('income-graph-2','figure')),
    [Input('year-rangeslider','value'),
     Input('income-checklist','value')]
)
def UpdateIncomeGraph(year,checklist):
    # load income data
    dfincome = query.queryapp.LoadData('dfincome')
    data=[]
    # fetch income for those selected in the checklist
    for row in checklist:
        # only get data for picked years
        for y in range(year[0], year[1] + 1):
            data.append({'x':dfincome.loc[dfincome['YEAR'] == y, "MONTH" ], 'y':dfincome.loc[dfincome['YEAR'] == y, row],'type': 'scatter', 'name':'{0}({1})'.format(str(row),y) })

    figure = {
        'data':data,
        'layout': {
            'title':'Income',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)'
        }
    }

    return figure

@app.callback(
    (Output('money-tank-1','value')),
     [Input('year-rangeslider','value')]
)
def UpdateTank(year):
    # load balance data with total
    dfbalance = query.queryapp.LoadData('dfbalance') 
    # return total 
    return int(dfbalance["Total"].tail(1))


#server = app.server # for production
if __name__ == '__main__':
    app.run_server(debug=True)