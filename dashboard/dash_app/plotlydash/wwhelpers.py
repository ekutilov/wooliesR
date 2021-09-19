import json
import pandas as pd
from google.cloud import storage
import os
from functools import cache
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table


### === MAIN CLASS ===
class WWData:
    """ Read files from the cloud and provides parsed ww data back.
    Normally you just pass session_id to the constructor.
    Returns:
        .transactions (pandas) - list of all transactions
        .items (pandas) - list of all items bought (grouped by transactions
            through basketKey index level - one basket = one transaction)
        .index - index for transactions (basketKeys)
        .json - parsed (but not normalized into a dataframe) raw data
        .json_string - same as json but serialised into a string
        ._as_pandas - raw (not cleaned) data parsed into dataframe """

    # Constants
    DIVISIONS = {'SO1010': 'BWS',
                 'SO1005': 'Supermarkets',
                 'SO1030': 'WW Metro'}

    def __init__(self, session_id='', filepath='', debug=False):
        exit_message = 'ok'

        if (debug):  # only for debugging/testing - in this case pass filepath
            with open(filepath) as json_file:
                json_data = json.load(json_file)
        else:
            bucket = os.environ['STORAGE_BUCKET']
            json_file, exit_message = self.download_blob(bucket, session_id)

        # There are a few stages an exception can happen - while reading,
        # while parsing json and while extracting data:
        if (exit_message == 'ok'):
            try:
                json_data = json.loads(json_file)
            except json.JSONDecodeError:
                exit_message = 'JSON parse error'

        if (exit_message == 'ok'):
            pd_tbl = pd.json_normalize(json_data)
            if 'basketKey' in pd_tbl.columns:
                pd_tbl.set_index('basketKey', inplace=True)

            try:
                pd_tbl = self._ww_parse_ereceipts_column(pd_tbl)
                self.__transactions = self._transactions_extractor(pd_tbl)
                self.__items = self._items_extractor(pd_tbl)
                self.__index = self.__transactions.index
            except:
                exit_message = 'WooliesR parse error.'

        if (exit_message != 'ok'):
            session_id = 'demo'
            json_file, _ = self.download_blob(bucket, session_id)
            json_data = json.loads(json_file)
            pd_tbl = pd.json_normalize(json_data)
            pd_tbl.set_index('basketKey', inplace=True)
            pd_tbl = self._ww_parse_ereceipts_column(pd_tbl)
            self.__transactions = self._transactions_extractor(pd_tbl)
            self.__items = self._items_extractor(pd_tbl)
            self.__index = self.__transactions.index
            self.demo = True

        self._as_pandas = pd_tbl
        self.__json = json_data
        self.session_id = session_id
        self.status = exit_message

    @property
    def items(self):
        return self.__items

    @property
    def transactions(self):
        return self.__transactions

    @property
    def index(self):
        return self.__index

    @property
    def json(self):
        return self.__json

    @property
    def json_string(self):
        return str(self.__json)

    @staticmethod
    def download_blob(bucket_name, session_id):
        """Downloads a blob from the bucket."""
        if ((session_id is None) or (type(session_id) != str)):
            return None, 'Session is not started'

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(session_id + '_json.json')

        if not blob.exists():
            return None, 'User data has not been found'

        json = blob.download_as_bytes(raw_download=True).decode()

        return json, 'ok'

    @staticmethod
    def _ww_parse_ereceipts_column(data):
        """Source-specific helper extractor function (see comments)"""
        # '__typename' chunks of data parsing here (non-standard json notation) in
        # receiptDetails.details column (most of important info on ereceipts there)
        ereceipts_details = data['ereceipt.receiptDetails.details']

        ereceipts_details_parsed = pd.DataFrame(index=ereceipts_details.index)

        for i, typename_list in ereceipts_details.dropna().items():
            duplicate_names = {}
            for val in typename_list:
                json_content = val.copy()
                key = json_content.pop('__typename')

                if key in duplicate_names.keys():
                    ereceipts_details_parsed.loc[i, key+'.'
                                                 + str(duplicate_names[key])] = [json_content, ]
                    duplicate_names[key] += 1
                else:
                    ereceipts_details_parsed.loc[i, key] = [json_content, ]
                    duplicate_names[key] = 1

        return data.join(ereceipts_details_parsed)

    @staticmethod
    def _transactions_extractor(data):
        '''Main method extracting/cleaning/interpreting data _for transactions_ -
        very source-specific. Extract (column by column) list of transactions
        (individual shop visits) from raw data.
        Add a code block here if you want an extra column in the transactions
        table. '''

        index = data.index
        output = pd.DataFrame(index=index)

        # remove/process 'miscellaneous' rows
        # 'AllStores' seems correspond to bonus transactions, we don't need it for viz
        rows_to_drop = index[(data['storeName'] == 'AllStores')]

        # rows with label (Bonus) are should be glued with corresponding in-shop transactions.
        bonus_rows = index[data.storeName.str.contains('\\(Bonus\\)')]
        c_bonusPoints = pd.Series(index=index, dtype=float)
        for i, row in data.loc[bonus_rows].iterrows():
            i_t = i[:14] + '0' + i[15:]
            c_bonusPoints[i_t] = float(row['pointEarn'])
        output['Extra Bonus Points'] = c_bonusPoints.fillna(0)

        rows_to_drop = rows_to_drop.union(bonus_rows)

        # Parse Date column (inc. time)
        c_Date = pd.to_datetime(data['transactionDate'])
        output['Date'] = c_Date

        # parse CardNumber
        c_CardNumber = data['cardNo'].combine_first(data['card'])
        output['Card Number'] = c_CardNumber

        # parse division - bws, bigw or supermarket - based on Banner field

        c_Division = data['banner'].replace(WWData.DIVISIONS).fillna('Other')
        output['Brand'] = c_Division

        # parse store number
        c_StoreNumber = data['storeNo']
        output['Store Number'] = c_StoreNumber

        # parse store name (earlier in time it was combined with store number, cleaning it up)
        c_StoreName = data['storeName'].str.replace(
            '^[0-9]{4}\\s', '', regex=True)
        output['Store'] = c_StoreName

        # parse store address TODO - prettify addressess
        # c_StoreAddress = data['ReceiptDetailsHeader']
        #     res = []
        #     for e in column:
        #         if type(e)==float:
        #             res.append('-')
        #         elif type(e)==list:
        #             res.append(e[0]['content'])
        #         else:
        #             res.append(e['content'])
        #     return pd.Series(res, dtype=str)

        # receipt Total
        c_Total = data['totalSpent'].str.replace(
            '\\$', '', regex=True).astype('float')
        output['Receipt Total'] = c_Total

        # PointsEarned
        # TODO: try to retrieve point from ereceipts where points are not available (old transactions)
        c_PointsEarned = data['totalPointsEarned'].replace(
            '', '0', ).astype(float)
        output['Rewards Points'] = c_PointsEarned

        output['Total Points'] = output.apply(
            lambda x: x['Rewards Points'] + x['Extra Bonus Points'], axis=1)

        return_columns = ['Date', 'Card Number', 'Brand', 'Store', 'Store Number', 'Receipt Total',
                          'Rewards Points', 'Extra Bonus Points', 'Total Points', ]

        return output[return_columns].drop(rows_to_drop)

    @staticmethod
    def _items_extractor(data):
        '''Similar extractor function but for the items table.
        Add a core block here if you want another column in the item table.
        It mostly uses ReceiptDetailsItems column in pandas raw data.'''
        # in the input file the ereceipts data is stored in columns with names
        # starting 'ReceiptDetails' in particular, items from ereceipts are in
        # ReceiptDetailsItems. It has (had?) random dtypes, so need to
        # correct for this.
        # Index (basketKey) that we want to preserve for future use (i.e.
        # joins with transaction-level data)
        # We are dropping transactions data where ereceipts unavailable
        # then correct for the fact that some jsons in this column stored
        # as dict within lists (while some - just as dicts)
        # append basketKey to cell's content for later use
        # (because pandas function 'json_normalize' doesn't carry over these
        # index values)

        items_json_column = data['ReceiptDetailsItems'].dropna().\
            apply(lambda x: x[0] if type(x) == list else x).\
            reset_index().\
            apply(lambda x: x[1] | {'basketKey': x[0]}, axis=1)

        items_expand = pd.json_normalize(items_json_column, record_path=[
                                         'items', ], meta=['basketKey', ])

        # Some items can occupy 2-3 lines in the file: i.e. weighted items,
        # multiple items in one line, also notes
        # like 'price reduces' are put on a separate lines. Tidying it:

        for row_n, row_values in items_expand.iloc[0:, :].iterrows():
            if row_values['amount'] != '':
                items_expand.loc[row_n,
                                 '_description_clean_1'] = row_values['description']
                if (row_n != 0):
                    if ((items_expand.loc[row_n-1, 'amount'] == '')
                            and (not('PRICE REDUCED' in items_expand.loc[row_n-1, 'description']))):
                        items_expand.loc[row_n, '_description_clean_1'] =\
                            items_expand.loc[row_n-1, 'description'] + \
                            ' ' + row_values['description']

#  lines below work but excluded for timebeing as are not used
#                 if (row_n < items_expand.shape[0]-1):
#                     if ((items_expand.loc[row_n+1, 'amount']=='') and ('PRICE REDUCED' in items_expand.loc[row_n+1, 'description'])):
#                         items_expand.loc[row_n, 'reducedNote'] = items_expand.loc[row_n+1, 'description']

#        items_expand.fillna({'reducedNote': ''}, inplace=True)

        items = items_expand[items_expand.amount != ''].copy()

# hash symbol prefix means specials, wipe it out of description
#        items['hashCharFlag'] = items['_description_clean_1'].str.startswith('#')
        _description_clean_2 = items['_description_clean_1'].str.replace(
            '^#', '', regex=True)

        # extract info from description field (i.e. per unit price).
        weighted_items = _description_clean_2.\
            str.extract(
                '^(?P<productname>.+)\\s(?P<quantity>[0-9]+\\.[0-9]+) (?P<unit>[a-y]+) NET @ \\$(?P<price>[0-9]+\\.[0-9]+)/[a-y]+')

        multiple_items = _description_clean_2.\
            str.extract(
                "^(?P<productname>.+) Qty (?P<quantity>[0-9]+) @ \\$(?P<price>[0-9]+\\.[0-9]+) each")

        items['Price Per Unit'] = weighted_items['price'].combine_first(
            multiple_items['price']).combine_first(items['amount']).astype('float')
        items['Unit'] = weighted_items['unit'].fillna('pc')
        items['Quantity'] = weighted_items['quantity'].combine_first(
            multiple_items['quantity']).fillna(1).astype('float')
        items['Product'] = weighted_items['productname'].combine_first(
            multiple_items['productname']).combine_first(_description_clean_2)
        items['Price Total'] = items['amount'].astype('float')

        items.set_index(keys=[items['basketKey'],
                              (items[['basketKey']].groupby('basketKey').cumcount()+1).rename('nn'), ], inplace=True)

        return_columns = ['Product', 'Price Per Unit',
                          'Quantity', 'Unit', 'Price Total', ]

        return items[return_columns]

# === OTHER FUNCTIONS ===
def delete_data(session_id):
    """Just delete user data by SessionID """
    bucket_name = os.environ['STORAGE_BUCKET']
    blob_name = session_id + '_json.json'
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()


# === DATA ANALYSIS and VIZ PART of the Dashboard ===
@cache
def get_ww(session_id):
    """Helper function for providing clean data to all dashboard parts"""
    ww = WWData(session_id)
    return ww


@cache
def data_summary(ww):
    """This function provides summarised data and visual objects for
    presenting them at the dashboard. Takes WWobject and returns a dictionary
    with various summary metrics and visual objects (plotly plots)."""
    # Add blocks here if we need mode summarised data plotted on the dashboad

    # Data Preparation
    today = pd.Timestamp.today()
    filter1year = ww.transactions["Date"] > today.replace(year=today.year-1)

    favstores_groups = ww.transactions.\
        groupby('Store')['Receipt Total']

    favstores = pd.DataFrame(
                        {'Spent $': favstores_groups.sum().round(2),
                         'Visits': favstores_groups.count(),
                         }
                        ).sort_values(by=['Spent $',], ascending=False)[0:9]

    fav_product_count = ww.items.groupby(by='Product', axis=0)["Quantity"].\
        sum().sort_values(ascending=False)[0:9].rename('Ea')

    fav_product_spent = ww.items.groupby(by='Product', axis=0)["Price Total"].\
        sum().sort_values(ascending=False).round(2)[0:9].rename('$$').\
        apply(lambda x:  "{:,.2f}".format(x))

    data_content = {
        'Year Total': ww.transactions.loc[filter1year,
                                          "Receipt Total"].sum().round(2),
        'Average Bill': ww.transactions["Receipt Total"].mean().round(2),
        "Top Bill": ww.transactions["Receipt Total"].max().round(2),
        "Favourite Stores": favstores.reset_index(),
        "Favorite Products Count": pd.DataFrame(fav_product_count).reset_index(),
        'Favorite Products Spent': pd.DataFrame(fav_product_spent).reset_index(),
        }

    # PLOTS
    # Plot 1
    st_date_w = ww.transactions['Date'].dt.to_period('w').dt.start_time.min()
    fi_date_w = ww.transactions['Date'].dt.to_period(
        'w').dt.start_time.max() + pd.Timedelta('1W')
    st_date_m = ww.transactions['Date'].dt.to_period('M').dt.start_time.min()
    fi_date_m = (ww.transactions['Date'].dt.to_period(
        'M').dt.start_time.max() + pd.Timedelta('32D')).replace(day=1)
    xbins = {'weeks': {'start': st_date_w, 'size': 6.048e8, 'end': fi_date_w},
             'months': {'start': st_date_m, 'size': 'M1', 'end': fi_date_m}, }

    fig = px.histogram(ww.transactions, x='Date', y='Receipt Total',
                       histfunc="sum",
                       color='Brand',
                       template='seaborn',
                       height=700,
                       )

    fig.update_xaxes(showgrid=True,
                     ticklabelmode="period",
                     rangeslider_visible=True,
                     tick0=st_date_w,
                     dtick=6.048e8,
                     tickfont={'size': 11, 'color': 'gray'},
                     tickformat="%d.%m.%y",
                     title_text=None)

    fig.update_traces(xbins=xbins['weeks'],)

    fig.update_layout(bargap=0.1,
                      yaxis_title='Total Spent',
                      updatemenus=[
                          dict(
                              buttons=list([
                                  dict(
                                      args=[{'xbins': xbins['weeks']},
                                            {'xaxis.tick0': st_date_w,
                                             'xaxis.dtick': 6.048e8,
                                             'xaxis.tickformat': "%d.%m.%y",
                                             'shapes[1].visible': False,
                                             'shapes[0].visible': True,
                                             'annotations[0].visible': True,
                                             'annotations[1].visible': False},
                                            ],
                                      label="Weekly",
                                      method="update"
                                      ),
                                  dict(
                                      args=[{'xbins': xbins['months']},
                                            {'xaxis.tick0': st_date_m,
                                             'xaxis.dtick': 'M1',
                                             'xaxis.tickformat': '%b\n%Y',
                                             'shapes[1].visible': True,
                                             'shapes[0].visible': False,
                                             'annotations[1].visible': True,
                                             'annotations[0].visible': False
                                             }
                                            ],
                                      label="Monthly",
                                      method="update"
                                      ),
                                  ]),
                              type="buttons",
                              direction="left",
                              pad={"r": 5, "t": 5},
                              showactive=True,
                              x=0.50,
                              xanchor="center",
                              y=1.02,
                              yanchor="bottom"
                              ), ])
    data_content['Plot Timeline'] = fig

    #  Plot 2
    fig_2 = px.bar(data_frame=ww.transactions,
                   y='Card Number',
                   x='Receipt Total',
                   color='Brand',
                   orientation='h',
                   template='seaborn',
                   height=300,
                   )

    fig_2.update_layout(showlegend=True)
    fig_2.update_yaxes(title_text=None, showticklabels=False)
    fig_2.update_xaxes(title_text=None)

    data_content['Plot Brands'] = fig_2

    return data_content


### ===== DASHBOARD DESIGN PART =====
@cache
def content_blocks(session_id):
    """Provides layout function - dashboard design constructor."""
    # Add blocks here if you want new visual block at the dashboard
    # Make sure that data you want to add already made available through
    # data_summary function.

    # helper functions
    def card_block(card_header, card_title, card_text):
        a_card =\
                    dbc.Card(
                            [
                                dbc.CardHeader(
                                    card_header, className='font-weight-bold bg-light text-dark'),
                                dbc.CardBody(
                                    [
                                        html.H3(
                                            card_title, className="card-title text-success"),
                                        html.P(
                                            card_text, className="card-text")
                                        ],
                                    )
                            ], className='border-dark', outline=True
                            )

        return a_card

    # data retrieval
    ww = get_ww(session_id)
    data_content = data_summary(ww)

    # ==== Content blocks (each block takes at least one row) =====

    # Top Nav Menu
    block_navigation =\
        dbc.Row(dbc.Col(
            dbc.NavbarSimple(
                    brand='myShopDash for Everyday Rewards',
                    brand_href='/dashapp/',
                    color='dark',
                    dark=True,
                    fluid=True,
            )
        ))

    block_header_1 =\
        dbc.Row(
        [
            dbc.Col(
            [
                html.H1('Your ER Dashboard', id='header1',
                        className='text-primary mt-4'),
            ]
            )
        ])

    # Stat Cards
    cards_all = dbc.Row(dbc.Col(
        dbc.CardDeck(
                    [
                        card_block(
                            "Your total spent",
                            "$ "+str(data_content['Year Total']),
                            "over 12 months to the day in all stores"),
                        card_block(
                            "You spent",
                            "$ "+str(data_content['Average Bill']),
                            "in one shop on average"),
                        card_block(
                            "You paid",
                            "$ "+str(data_content['Top Bill']),
                            "for your biggest shop"),
                        ],
                )))

    # TODO here - selectors/filters
    # i.e. date start/finish, brand, include only ereceipts, cardnumber

    # Plots Blocks
    block_graph_1 =\
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2('Your spendings over time',
                                className='mt-4 text-primary'),
                        html.Div(
                            dcc.Loading(
                                dcc.Graph(
                                    figure=data_content['Plot Timeline']),
                                type="circle",
                            ), style={'height': '700px'}
                        ),
                    ]),
                ])

    block_graph_2 =\
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2('All your spendings by ER brands',
                                className='text-primary'),
                        html.Div(
                            dcc.Loading(
                                dcc.Graph(figure=data_content['Plot Brands']),
                                type="circle",
                            ), style={'height': '300px'}
                        ),
                    ]),
                ])

    # Top-10 tables
    block_tops =\
        dbc.Row([
            dbc.Col(
                [
                    html.H4('Products: most often bought',
                            className='text-primary'),
                    dbc.Table.from_dataframe(
                        data_content['Favorite Products Count'],
                        striped=True, bordered=False, hover=True,
                        className='table-sm'),
                    ]
            ),
            dbc.Col(
                [
                    html.H4('Products: most spent on',
                            className='text-primary'),
                    dbc.Table.from_dataframe(
                        data_content['Favorite Products Spent'],
                        striped=True, bordered=False, hover=True,
                        className='table-sm'),

                    ]
            ),
            dbc.Col(
                [
                    html.H4('Your stores', className='text-primary'),
                    dbc.Table.from_dataframe(
                        data_content['Favourite Stores'],
                        striped=True, bordered=False, hover=True,
                        className='table-sm'),
                    ]
            ),

        ])

    # Tables - statements and eReceipts Viewer
    # TODO - tidy up, make sorting, styling, pagination
    table_transactions =\
        dash_table.DataTable(id='table_trans',
               columns=[{"name": i, "id": i}
                        for i in ww.transactions.drop(['Card Number', 'Brand', 'Store Number', 'Rewards Points', 'Extra Bonus Points'], axis=1).columns],
               data=ww.transactions.to_dict('records'),
               page_action='none',
               style_table={'height': '80vh',
                            'overflowY': 'auto',
                            'overflowX': 'hidden',
                            },
               style_data={},
               style_header={'whiteSpace': 'normal',
                             'height': 'auto', },
               style_cell={
                   'font-family': '-apple-system, system-ui, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',
                   'font-size': '80%',
                   'overflow': 'hidden',
                   'textOverflow': 'ellipsis',
                   'maxWidth': 0,
                   },
               style_cell_conditional=[
                                  {'if': {'column_id': 'Date'},
                                   'width': '25%'},
                                   {'if': {'column_id': 'Store'},
                                    'width': '45%'},
                                    {'if': {'column_id': 'Receipt Total'},
                                     'width': '15%'},
                                  {'if': {'column_id': 'Total Points'},
                                   'width': '10%'},
                                  ],
               row_selectable='single'
               )

    table_items =\
        dash_table.DataTable(id='table_items',
               columns=[{"name": i, "id": i}
                        for i in ww.items.columns],
               data=ww.items.to_dict('records'),
               page_action='none',
               style_table={'height': '80vh',
                            'overflowY': 'auto',
                            },
               style_cell={
                   'font-family': '-apple-system, system-ui, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',
                   'font-size': '80%',
                   'overflow': 'hidden',
                   'textOverflow': 'ellipsis',
                   'maxWidth': 0
                   },
               css=[],
               row_selectable=False,
               )

    block_tables =\
        dbc.Container([
            dbc.Row(
                dbc.Col(
                    html.H3('Your eReceipts',
                            className='text-primary mt-4'),
                )
            ),
            dbc.Row(
            [
                    dbc.Col([
                        html.H4('Transactions',
                                className='text-secondary'),
                        dcc.Loading(table_transactions, type='circle'),
                    ], width=6
                    ),
                    dbc.Col([
                        html.H4('Items in the receipt',
                                className='text-secondary'),
                        dcc.Loading(table_items, type='circle'),
                    ]),
            ])
        ])

    # Data Downloader Interface

    downloads_card =\
        dbc.Card(
            dbc.CardBody(
            [
                html.H5("Download your data",
                        className='card-title text-primary'),
                dbc.Row(
                [
                    dbc.Col(
                    [
                        html.P('''Download your data as .xlsx file to
                                easily open and analyse in MS Excel or
                                elsewhere''',
                                className='card-text'
                        ),
                        dbc.Button(
                        [
                            dcc.Loading(dcc.Download(id="download-xlsx"),
                                        type='circle'),
                        "Download .xlsx"
                        ], color="info", id='xlsx_button'
                        ),
                    ],
                    ),
                    dbc.Col(
                    [
                        html.P('''Download your data as raw JSON dump.
                                This file will contain all the data we
                                downloaded from ER API, but it will not
                                open in Excel directly''',
                                className='card-text'
                        ),
                        dbc.Button(
                        [
                            dcc.Loading(dcc.Download(id="download-json")),
                            "Download JSON Dump"
                        ], color="info", id='json_button'),
                    ]
                    ),
                ],
                ),
            ]
            )
        )

    deleter_card =\
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5('Delete data',
                            className='card-title text-primary'),
                    html.P('''For your privacy: your can delete your
                            data from this website. Otherwise it will
                            be deleted from this server automatically
                            within 24hrs.'''),
                    dcc.Loading(dbc.Button("Delete data",
                                            color="danger",
                                            id='delete-button',
                                            disabled=False
                                            )
                                ),
                ]
                )
            )

    block_downloads =\
        dbc.Row(
            [
                dbc.Col([downloads_card,], width=8),
                dbc.Col([deleter_card,], width=4)
            ], className='mb-4'
            )

    # exception alerter
    alert_status = ww.status

    if (alert_status == 'Session is not started'):
        alert_text = ["""You see the demo data at the moment,
                because myShopDash hasn't been able to find your data. """,
                """If you didn't upload your shopping data yet, learn
                how to do it here: """,
                html.A('Getting started', href='/static/manual.html',
                    className='font-weight-bold text-light'),
                '. ',
                html.Br(),
                """If you tried myShopData Chrome Extension, but your data
                doesn't show up here, something is wrong.
                You can go to the Everyday Reward website and try
                one more time. If fault persists, drop me a message: """,
                html.A('Contacts', href='/static/contacts.html',
                    className='font-weight-bold text-light'),
                '.'
                ]
        alert_color = 'warning'
    elif (alert_status != 'ok'):
        alert_text = ["""You see the demo data at the moment,
                because myShopDash hasn't been able to process your data.
                Error status: {}, sessionID: {}, ts: {}. """.format(alert_status,
                session_id, pd.Timestamp.today()),
                html.Br(),
                """You can try it again, starting from running the Chrome
                extension on Everyday Rewards Account page. """,
                """If fault persists, drop me a message: """,
                html.A('Contacts', href='/static/contacts.html',
                    className='font-weight-bold text-light'),
                '. '
                ]
        alert_color = 'danger'
    else:
        alert_text = 'ok'
        alert_color = 'warning'

    block_alert =\
        dbc.Alert(
                alert_text,
                color=alert_color,
                is_open=(alert_text != 'ok'),
                className='mb-0 fixed-bottom rounded-0 border-0',
                id='demo-alert',
        )

    # Footer
    block_footer = dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                html.P(
                                [
                                html.A('About this site', href='/static/manual.html'),
                                ' - ',
                                html.A('Privacy', href='/static/privacy.html'),
                                ' - ',
                                html.A('Contacts', href='/static/contacts.html'),
                                ' - ',
                                html.A('Source code', href='https://github.com/ekutilov/wooliesR'),
                                html.Br(),
                                html.Span('SessionID: {}, ts: {}, alert_status: {} (include it in your message of you report an issue)'.format(session_id, pd.Timestamp.today(), alert_status), className='small text-secondary'),
                                html.Br(),
                                html.A(html.Img(src='/static/chromestoreicon.png'), href='https://chrome.google.com/webstore/detail/kjnoihdmllddkmfhikjlkbfcdcmghhji/'),
                                html.Br(), html.Br(), html.Br(),
                                ]
                                ), className='text-center'
                            )
                        )
                    ], className='mb-5'
                    )

    hidden_service_block = [
            dcc.Store(id='session-id', data=session_id),
            dcc.Location(id='url'),
            ]

    # ===== Final Layout Constructor =====
    layout =\
        dbc.Container(
        [
            block_navigation,
            block_alert,
            block_header_1,
            cards_all,
            block_graph_1,
            block_graph_2,
            block_tops,
            block_tables,
            html.Hr(),
            block_downloads,
            html.Hr(),
            block_footer,
        ] + hidden_service_block,
        )

    return layout
