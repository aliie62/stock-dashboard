import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from pandas_datareader.nasdaq_trader import get_nasdaq_symbols
from pandas_datareader.stooq import StooqDailyReader

import requests
from datetime import datetime as dt


#Instantiate Dash app
app = dash.Dash(__name__)
server = app.server

#Get the tickers from NASDAQ
nsdq_symbols = get_nasdaq_symbols()
options = [dict(label = code, value = code) for code in nsdq_symbols.index]

app.layout = html.Div([
    html.Div([
            html.H1('NASDAQ Stocks',
                    style={'textAlign': 'center'})
            ]),
    html.Div([
            html.H3('Enter a stock symbol(s):'),
            dcc.Dropdown(id='dropdown', options=options,
                         value = options[0]['value'], multi=True)
            ],
            style = {'display':'inline-block', 'width' : '30%', 'verticalAlign':'top'}
            ),
        html.Div(style = {'display':'inline-block', 'width' : '30%', 'verticalAlign':'top'}
                 ),
    html.Div([
            html.H3('Select start and end dates:'),
            dcc.DatePickerRange(id='datepicker',
                                min_date_allowed = dt(2015,8,27),
                                max_date_allowed = dt.today(),
                                start_date = dt(2019,8,10),
                                end_date = dt.today()
                                ),
            html.Button(id='submit-button',
                        n_clicks=0,
                        children='Submit',
                        style={'marginLeft':'30px'})
            ],
            style = {'display':'inline-block','marginLeft':'5px'}
            ),    
    html.Div(
            [dcc.Graph(id='my_graph',
                      figure=dict(data= [{'x': [1,2], 'y': [3,1]}])
                      )]
            )
    ])

@app.callback(
        Output('my_graph','figure'),
        [Input('submit-button', 'n_clicks')],
        [State('datepicker', 'start_date'),
        State('datepicker', 'end_date'),
        State('dropdown', 'value')])
def update_graph(n_clicks, start_date , end_date, stock_ticker):
    #Convert passed date variables to date type since they change to string when they are paased to this function.
    start = dt.strptime(start_date[:10], '%Y-%m-%d')
    end = dt.strptime(end_date[:10], '%Y-%m-%d')
    #Create session variable for StooqDailyReader just in case if you got stuck behind company firewall.
    session = requests.Session()
    session.verify = False
    #Query each selected tick from Nasdaq and append its trace to traces list 
    traces = []
    for tic in stock_ticker:
        data = StooqDailyReader(tic,start=start,end=end, session=session)
        df = data.read()
        traces.append({'x':df.index, 'y': df['Close'], 'name':tic, 'hoverinfo':'text','text':df['Close']})
    #Create figure object to pass to main layout
    stocks = ['<b>'+stock+'</b>' for stock in stock_ticker]
    fig = {
        'data': traces,
        'layout': {'title':', '.join(stocks)+' Closing Prices',
                   'hovermode': 'closest',
                   'xaxis':{'title':'Time', 'showline':True},
                   'yaxis':{'title':'Price (USD)', 'showline':True}
                   }
    }
    return fig
    

if __name__ == '__main__':
    app.run_server()
