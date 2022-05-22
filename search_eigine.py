from tkinter.tix import MAX
from sqlalchemy import Table, create_engine,MetaData, insert,Column,String,Integer,Float,Boolean,select,DateTime,update,and_,or_,not_,distinct
import pandas as pd
import dash
from dash import dcc,html,Dash
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
from dash.dash import no_update
import re

MAX_ROWS=25
engine = create_engine('sqlite:///main.db', echo=False)
metadata = MetaData()
words = Table('words', metadata,
            Column("word_ind",String(255),primary_key=True,unique=True),
            Column("word", String(255),nullable=False),
            Column("description",String()),
            Column("file", String(255),nullable=False),
            Column("tags",String(255)),
)
metadata.reflect(engine)
metadata.create_all(engine)
url_theme1 = dbc.themes.BOOTSTRAP
# set up dash app object
app = dash.Dash(__name__, title="keyword search",
                external_stylesheets=[url_theme1, dbc.icons.FONT_AWESOME],
)

app.layout=dbc.Container([
    html.H1("用語集検索",className="p-3"),
    dbc.Row([
        html.Span("Search Keyword"),dbc.Input(id="search_word",value="")
        ]),
    dbc.Row([
        html.Div(id="result")
    ])          
    ])

@app.callback(
    Output("result","children"),
    Input("search_word","value"),
    prevent_initialcall=True
)
def func1(word):
    if word:
        df=extract_data(word)
        length=len(df)
        df=df.head(MAX_ROWS)
        if len(df)==0:
            return("")
        output=[html.Div(f"{len(df)}/{length}")]
        for ind,row in df.iterrows():
            output.append(html.Div([
                dbc.Row([
                    html.Hr(),
                    dbc.Col(html.H5(row.word),width=10),
                    dbc.Col(html.H6(row.file))
                    ]),
                html.Div(row.description),
                ],className="p-0"),
                )
        return(output)


def extract_data(word):
    word=word.upper()
    keywords=re.split(r"\s+",word)
    s=select([words])
    for query in keywords:
        s=s.where(or_(words.c.word.contains(query),words.c.description.contains(query)))
    with engine.connect() as con:
        df = pd.read_sql_query(sql=s, con=con)
    return(df)
 
if __name__=="__main__":
    app.run_server(debug=True, host='0.0.0.0', port=8050,use_reloader=False)






