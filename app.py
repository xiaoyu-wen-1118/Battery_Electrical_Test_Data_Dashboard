import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash.dependencies import Input, Output
from dash import dash_table
from dash import html
import glob
import plotly.graph_objects as go


# Get all data files from the current directory
csv_files = glob.glob('*.csv')
file_cyclenumber = []
file_rowNumber = []
for file in csv_files:
    data = pd.read_csv(file)
    file_rowNumber.append(data.shape[0])
    file_cyclenumber.append(data['Cycle_Index'].max())
    
tmp = {'Cell id':range(1, len(csv_files)+1), 'Filename':csv_files, 'Number of rows': file_rowNumber, 'Number of cycles':file_cyclenumber}
file_df = pd.DataFrame(tmp)

# Create the components and layout
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Electrical Test Data Dashboard"

# Create navbar
navbar = dbc.Navbar(id = 'navbar', children = [
    dbc.Row([
        dbc.Col(dbc.NavbarBrand("Electrical Test Data Dashboard",
                                style = {'color':'white', 'fontSize':'25px','fontFamily':'Times New Roman'}))                
        ]
        , align = "center",)]
    , color = '#66cdaa')

# Create table
file_explorer = dash_table.DataTable(id='datafile_table',
                                     # columns=[{"index":i, "filename":csv_files[i]} for i in range(len(csv_files))],
                                     editable=True,
                                     page_size=10,
                                     data=file_df.to_dict('records'),
                                     column_selectable="single",
                                     row_selectable="multi",
                                     selected_columns=[],
                                     selected_rows=[],
                                     page_action="native",
                                     sort_action="native",)

# Create the dropdown menu options
options1 = ['Current', 'Voltage', 'Temperature','dV/dt']
options2 = ['Charge_Capacity', 'Discharge_Capacity','Charge_Energy','Discharge_Energy']

body_app = dbc.Container([    
    html.Br(),
    html.Br(),    
    dbc.Row([
        dbc.Col( 
            [dcc.Dropdown(id = 'dropdown1',
                                 options = [{'label':i, 'value':i } for i in options1],
                                 value = 'Current',        
                                 ),
             dbc.Card(id = 'card_num1',style={'height':'500px'})]),
        dbc.Col( 
            [dcc.Dropdown(id = 'dropdown2',
                                 options = [{'label':i, 'value':i } for i in options2],
                                 value = 'Charge_Capacity',        
                                 ),
             dbc.Card(id = 'card_num2',style={'height':'500px'})]),
        ]),    
    html.Br(),
    html.Br(),    
    dbc.Row([
        dbc.Col([dbc.Card(file_explorer,style={'height':'300px'})]),
        ]),    
    html.Br(),
    html.Br()        
    ], 
    style = {'backgroundColor':'#f7f7f7'},
    fluid = True)

app.layout = html.Div(id = 'parent', children = [navbar,body_app])

@app.callback([Output('card_num1', 'children'),
               Output('card_num2', 'children')
               ],
              [Input('datafile_table','selected_rows'),
               Input('dropdown1','value'),
               Input('dropdown2','value')])

def update_figure(rows, option1, option2):
    print(rows)
    colors = [  '#8ECFC9',
                '#FFBE7A',
                '#FA7F6F',
                '#82B0D2',
                '#BEB8DC',
                '#2878b5',
                '#9ac9db',
                '#f8ac8c',
                '#c82423',
                '#ff8884']

    fig1 = go.Figure()
    fig2 = go.Figure()
    for i in range(len(rows)):
        curr_filename = csv_files[rows[i]]
        curr_df = pd.read_csv(curr_filename)
        # df for fig1
        short_df = curr_df[curr_df['Test_Time'] < 200000]
        
        # df for fig2
        curr_cycle_df = curr_df.groupby(['Cycle_Index']).last().reset_index()
        curr_cycle_df.drop(curr_cycle_df.tail(1).index, inplace=True)
        
        fig1.add_trace(go.Scatter(x = short_df['Test_Time']/3600, y = short_df[option1],
                                       line = dict(color = colors[i], width = 1), name=curr_filename))
        fig2.add_trace(go.Scatter(x = curr_cycle_df['Cycle_Index'], y = curr_cycle_df[option2],
                                       line = dict(color = colors[i], width = 2), name=curr_filename))

    
    fig1.update_layout(plot_bgcolor = 'white',
                      margin=dict(l = 10, r = 10, t = 10, b = 10))
    fig1.update_xaxes(title_text="Time (h)", ticks="outside")
    if(option1=="Current"):
        fig1.update_yaxes(title_text="Current (A)")
    elif(option1=="Voltage"):
        fig1.update_yaxes(title_text="Voltage (V)")
    elif(option1=="Temperature"):
        fig1.update_yaxes(title_text="Temperature (C)")
    elif(option1=="dV/dt"):
        fig1.update_yaxes(title_text="dV/dt (V/s)")
    fig1.update_yaxes(ticks="outside")
    
    fig2.update_layout(plot_bgcolor = 'white',
                      margin=dict(l = 10, r = 10, t = 10, b = 10))
    fig2.update_xaxes(title_text="Cycle Number", ticks="outside")
    if(option2=="Discharge_Capacity" or option2=="Charge_Capacity"):
        fig2.update_yaxes(title_text=option2+" (Ah)")
    elif(option2=="Discharge_Energy" or option2=="Charge_Energy"):
        fig2.update_yaxes(title_text=option2+" (Wh)")
    fig2.update_yaxes(ticks="outside")
    
    card_content1 = [        
        dbc.CardBody(
            [
                html.H4('Test raw data', style = {'fontWeight':'bold', 'textAlign':'center'}),                 
                dcc.Graph(figure = fig1, style = {'height':'400px'}), 
                ]                   
            )  
        ]
    
    card_content2 = [        
        dbc.CardBody(
            [
                html.H4('Test cycle data', style = {'fontWeight':'bold', 'textAlign':'center'}),            
                dcc.Graph(figure = fig2, style = {'height':'400px'}), 
                ]                   
            )  
        ]
    return card_content1, card_content2
                                    

if __name__ == "__main__":
    app.run_server()