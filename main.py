import dash  # (version 1.12.0)
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import os
from datetime import datetime

# -------------------------------------------------------------------------------------
# Import the cleaned data (importing csv into pandas)
masternodes = pd.read_json('http://defichain-node.de/api/v1/listmasternodes/').transpose()
masternodes['Address'] = masternodes['ownerAuthAddress']
masternodes = masternodes[['ownerAuthAddress', 'Address', 'state', 'mintedBlocks']]

cakenodes = pd.read_json('https://poolapi.cakedefi.com/nodes?order=status&orderBy=DESC')
cakenodes = cakenodes[cakenodes['coin'] == "DeFi"]
cakenodes = cakenodes[['address']]
cakenodes['Owner'] = "Cakedefi"

masternodes = masternodes.set_index('ownerAuthAddress').join(cakenodes.set_index('address'))
masternodes = masternodes.fillna({'Owner': "Other"})
masternodes_enabled = masternodes[masternodes['state'] == "ENABLED"]
querytime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# -------------------------------------------------------------------------------------
# App layout
app = dash.Dash(__name__, prevent_initial_callbacks=True)  # this was introduced in Dash version 1.12.0

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# Sorting operators (https://dash.plotly.com/datatable/filtering)
app.layout = html.Div([
    dash_table.DataTable(
        id='datatable-interactivity',
        columns=[
            {"name": i, "id": i}
            for i in masternodes.columns
        ],
        data=masternodes.to_dict('records'),  # the contents of the table
        editable=True,  # allow editing of data inside all cells
        filter_action="native",  # allow filtering of data by user ('native') or not ('none')
        sort_action="native",  # enables data to be sorted per-column by user or not ('none')
        sort_mode="single",  # sort across 'multi' or 'single' columns
        selected_columns=[],  # ids of columns that user selects
        selected_rows=[],  # indices of rows that user selects
        page_action="native",  # all data is passed to the table up-front or not ('none')
        page_current=0,  # page number that user is on
        page_size=20,  # number of rows visible per page
        style_cell={  # ensure adequate header width when text is shorter than cell's text
            'minWidth': 95, 'maxWidth': 95, 'width': 95
        },

        style_data={  # overflow cells' content into multiple lines
            'whiteSpace': 'normal',
            'height': 'auto'
        }
    ),

    html.Br(),
    html.Br(),
    #    html.Div(id='bar-container'),
    #    html.Div(id='choromap-container')
    html.Div([
        html.P(f'Query-Time: {querytime}'),
        html.P(f'Query-Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    ]),
    html.Div(
        dcc.Graph(
            id='Graph1',
            figure={
                'data': [
                    {'values': [len(masternodes_enabled[masternodes_enabled['Owner'] == "Cakedefi"]),
                                len(masternodes_enabled[masternodes_enabled['Owner'] != "Cakedefi"])],
                     'labels': ["Cakedefi", "Others"],
                     'type': 'pie',
                      'pull': [0.0, 0.1]
                     }
                ],
            }
        )
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
