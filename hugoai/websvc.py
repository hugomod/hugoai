import os
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html, ctx
#from dash.dependencies import Input, Output, State
import json
import random
from dash_extensions.enrich import Output, DashProxy, Input, MultiplexerTransform, html, State
from hugoai.chains import respond

from hugoai.rules import RULES

import time

#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.YETI, dbc.icons.FONT_AWESOME])
app = DashProxy(__name__,
                external_stylesheets=[dbc.themes.YETI, dbc.icons.FONT_AWESOME],
                transforms=[MultiplexerTransform()])
server = app.server #nee

LINE_BREAK = dbc.Row(html.Br())

# Top heading and logo
heading = [html.H2("HUGO-AI"),html.H5("Prosocial AI Content Moderation Tool")]
HEADER_ROW = dbc.Row(dbc.Col(heading, width={'size':5, 'offset':1}, align="center"))

# Chat area
chat = dbc.Textarea(id="chat",style={"width": "100%", "height": "570px"})

# Users

user1 = dbc.InputGroup(
            [
                dbc.InputGroupText("User 1"),
                dbc.Textarea(id="user1-text"),
                dbc.Button(">>", id="user1-button")
            ],
        )

user2 = dbc.InputGroup(
            [
                dbc.InputGroupText("User 2"),
                dbc.Textarea(id="user2-text"),
                dbc.Button(">>", id="user2-button")
            ],
        )


user3 = dbc.InputGroup(
            [
                dbc.InputGroupText("User 3"),
                dbc.Textarea(id="user3-text"),
                dbc.Button(">>", id="user3-button")
            ],
        )

moderate_button = dbc.Button("Moderate", id="moderate-button")

spinner = dbc.Spinner(html.Div(id="spinner"))


analysis = dbc.Col([dbc.Textarea(id="analysis",style={"width": "100%", "height": "570px"})])
chat_column = dbc.Col([chat, analysis], width={'size':6, 'offset':1})
rules = dbc.Textarea(id="rules", value=RULES, style={"width": "100%", "height": "570px"})

users_column = dbc.Col([user1, LINE_BREAK, user2, LINE_BREAK, user3, LINE_BREAK, moderate_button, spinner, LINE_BREAK, rules], width={'size':3, 'offset':0})


CHAT_ROW = dbc.Row([chat_column, users_column])




RULES_ROW = dbc.Row(dbc.Col([rules], width={'size':6, 'offset':1}))

ANALYSIS_ROW = dbc.Row([analysis])

# DASH APP LAYOUT
app.layout = html.Div([LINE_BREAK,
                       HEADER_ROW,
                       LINE_BREAK,
                       CHAT_ROW,
                       LINE_BREAK,
                       dcc.Store(id='chat-history', storage_type='memory', data=[])
                       ])


############# CALLBACKS ############################


@app.callback([Output('chat', 'value'),
               Output('chat-history', 'data'),
               Output('user1-text', 'value'),
               Output('user2-text', 'value'),
               Output('user3-text', 'value')],
              [Input('user1-button', 'n_clicks'),
               Input('user2-button', 'n_clicks'),
               Input('user3-button', 'n_clicks'),
               State('user1-text', 'value'),
               State('user2-text', 'value'),
               State('user3-text', 'value'),
               State('chat-history', 'data')])
def chatroom(n1, n2, n3, text1, text2, text3, chat_history):

    button_clicked = ctx.triggered_id
    if button_clicked == "user1-button":
        if text1:
            chat_history.append({"user": "USER1", "text": text1})
            printable = "\n".join([f"[{item['user']}]: {item['text']}" for item in chat_history])
            return printable, chat_history, "", "", ""
        else:
            raise dash.exceptions.PreventUpdate

    elif button_clicked == "user2-button":
        if text2:
            chat_history.append({"user": "USER2", "text": text2})
            printable = "\n".join([f"[{item['user']}]: {item['text']}" for item in chat_history])
            return printable, chat_history, "", "", ""
        else:
            raise dash.exceptions.PreventUpdate
    elif button_clicked == "user3-button":
        if text3:
            chat_history.append({"user": "USER3", "text": text3})
            printable = "\n".join([f"[{item['user']}]: {item['text']}" for item in chat_history])
            return printable, chat_history, "", "", ""
        else:
            raise dash.exceptions.PreventUpdate
    else:
        raise dash.exceptions.PreventUpdate


@app.callback([Output('chat', 'value'),
               Output('analysis', 'value'),
               Output('chat-history', 'data'),
               Output('spinner', 'value')],
              [Input('moderate-button', 'n_clicks'),
               State('chat-history', 'data'),
               State('rules', 'value')])
def trigger_response(n, chat_history, rules):
    print("triggered")
    if n and chat_history and rules:
        output = respond(chat_history, rules)
        chat_history.append({"user": "HUGO", "text": "\t"+output['response']})
        printable = "\n".join([f"[{item['user']}]: {item['text']}" for item in chat_history])
        return printable, json.dumps(output, indent=2), chat_history, ""
    else:
        dash.exceptions.PreventUpdate()



#########################

def main():
    server.run(debug=True, port=8010)

if __name__ == "__main__":
    app.run_server(debug=True)
