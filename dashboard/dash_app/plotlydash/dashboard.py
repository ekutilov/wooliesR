import io
import pandas as pd

from flask import request

from dash import Dash, dcc, html, callback_context
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from dash_app.plotlydash.wwhelpers import get_ww
from dash_app.plotlydash.wwhelpers import content_blocks, delete_data


def init_dashboard(server):
    """Create a Plotly Dash dashboard."""

    # constants go here
    external_stylesheets = [dbc.themes.YETI, ]

    # APP Initialisation
    dash_app = Dash(
        server=server,
        serve_locally=False,
        assets_folder='static',
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=external_stylesheets,
        meta_tags=[{'name': 'google-site-verification',
                    'content': 'm6dx4irpkQZ1oyugeCiK6g7LkQQ8_OmoGUoWOLhErKM'}],
    )

    dash_app.title = 'myShopDash for Everyday Rewards (aka Woolworth Rewards)'
    dash_app._favicon = 'favicon32.png'

    def layout_function():
        if request:
            session_id = request.cookies.get('sessionID')
        else:
            session_id = 0

        return content_blocks(session_id)

    # ===========================
    # ===== DASH CALLBACKS ======
    # ===========================
    @dash_app.callback(Output('table_items', 'data'),
                       Input('table_trans', 'selected_rows'),
                       Input('session-id', 'data'))
    def update_ereceipt_window(input_value, session_id):
        try:
            ww = get_ww(session_id)
            filtered = ww.items.loc[(ww.index[input_value[0]])]
        except:
            filtered = pd.DataFrame()

        return filtered.to_dict('records')

    @dash_app.callback(Output("download-xlsx", "data"),
                       Input('xlsx_button', 'n_clicks'),
                       State('session-id', 'data'),
                       prevent_initial_call=True)
    def downloader_xlsx(n_clicks, session_id):
        buffer = io.BytesIO()
        ww = get_ww(session_id)
        with pd.ExcelWriter(buffer) as writer:
            ww.transactions.to_excel(writer, sheet_name='Transactions')
            ww.items.to_excel(writer, sheet_name='Items')
        return dcc.send_bytes(buffer.getvalue(), 'ereceipts.xlsx')

    @dash_app.callback(Output('download-json', 'data'),
                       Input('json_button', 'n_clicks'),
                       State('session-id', 'data'),
                       prevent_initial_call=True)
    def downloader_json(n_clicks, session_id):
        return dict(content=get_ww(session_id).json_string,
                    filename='ww_dump.json',
                    type='application/json')

    @dash_app.callback(Output("delete-button", "disabled"),
                       Output('session-id', 'data'),
                       Output('url', 'search'),
                       Input('delete-button', 'n_clicks'),
                       State('session-id', 'data'),
                       prevent_initial_call=True)
    def deleter(n_clicks, session_id):
        #todo: add popup confirmation before deletion
        if (session_id != 'demo'):
            delete_data(session_id)
        callback_context.response.set_cookie('sessionID', '', expires=0)
        return True, 'demo', '?refresh'

    ### === DO not touch - APP Launch ===
    dash_app.layout = layout_function
    return dash_app.server
