import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
import yfinance as yf
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objects as go
from model import prediction

#Stock Graph
def get_stock_graph(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(mode='lines', x=df.index, y=df['Close'], name='Close'))
    return fig

_BOOTSWATCH_BASE = "https://cdn.jsdelivr.net/npm/bootswatch@5.1.3/dist/"

QUARTZ = _BOOTSWATCH_BASE + "quartz/bootstrap.min.css"

app = dash.Dash(external_stylesheets=[QUARTZ])

server = app.server

app.layout = html.Div([
    
    html.Div([
    
        html.H1('Stock Prediction', className='start'),
        
        #Input Stock
        html.Div([
            html.P('Enter a stock symbol:'),
            dbc.Input(id="ticker_input", type="text", placeholder='Eg: AAPL'),
            html.Div([
                dbc.Button("Submit", id='ticker-btn', color='primary', className='btn-div')
            ], className="d-grid gap-2 col-6 mx-auto"),            
        ], className="form"),

        #Prediction
        html.Div([
            dbc.Input(id="n_days",  type="text",  placeholder="number of days"),
            html.Div([
                dbc.Button("Forecast", id='forecast', color='secondary')
            ], className="d-grid gap-2 col-6 mx-auto"),

        ], className="forecast"),
        
    ], className='navigation'),
    
    html.Div([
        html.Div([
            html.P(id='ticker'),
            html.Img(id='logo'),
        ], className='header'),
        
        html.Div(id='rmp', className='description-div'),
        html.Div([], id='stock-graph', className='graph'),
        html.Div([], id="forecast-content"),
        
    ], className='content'),
    
], className='container')

#Company info
@app.callback(
    [Output("ticker", "children"), 
     Output('logo', 'src'), 
     Output('rmp', 'children'), 
     Output('stock-graph', 'children'),
     Output("forecast", "n_clicks")],
    [Input('ticker-btn', 'n_clicks')],
    [State('ticker_input', 'value')])

def update_data(n, val):
    if n == None:
        return "Hey there! Please enter a legitimate stock code to get details.", None, None, None, "Please submit a ticker and no. of days to forecast"
        # raise PreventUpdate
    else:
        if val==None:
            return PreventUpdate
        else:
            stock = yf.Ticker(val)
            logo = stock.info['logo_url']
            rmp = stock.info['regularMarketPrice']
            df = yf.download(val, period='max')
            fig = get_stock_graph(df)
            return stock.info['shortName'], logo, rmp, [dcc.Graph(figure=fig)], None

# callback for forecast
@app.callback([Output("forecast-content", "children")],
              [Input("forecast", "n_clicks")],
              [State("n_days", "value"),
               State("ticker_input", "value")])
def forecast(n, n_days, val):
    if n == None:
        return [""]
    if val == None:
        raise PreventUpdate
    fig = prediction(val, int(n_days) + 1)
    return [dcc.Graph(figure=fig)]


app.run_server(debug=True, port=8057)