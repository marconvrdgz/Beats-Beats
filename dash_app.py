import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np
from collections import deque
import plotly.express as px


# Cargar el DataFrame de spfy desde GitHub
url_spfy_reducido_csv = 'https://raw.githubusercontent.com/marconvrdgz/DEV.F/main/spfy_reducido.csv'
dfspfy = pd.read_csv(url_spfy_reducido_csv)
print(dfspfy.head())

# Cargar el DataFrame de corazón desde GitHub
url_heart_csv = 'https://raw.githubusercontent.com/marconvrdgz/DEV.F/main/heart.csv'
dfheart = pd.read_csv(url_heart_csv)
print(dfheart.head())

# URLs de las imágenes
frame1_url = 'https://lh3.googleusercontent.com/u/0/drive-viewer/AKGpihbTSPx6bxh_6M-8hovNGQj_4Hr38lsQYifZZZETuaxUskDZdQ1cZVuHSnj-3EkANq-xvN2RVfMQ_PcaYWDdue679iOwsYdyo5o=w1920-h878'
frame2_url = 'https://lh3.googleusercontent.com/u/0/drive-viewer/AKGpihYvclHMRBnOnZLCN0n8Hq3wVoF1TXURo2HghrUbA8Glf6IfyGqZRPAEJBy96L20PlWRNQ3rNFdXM3g97FKhK9crhQlze3tA6w=w1920-h878'
frame3_url = 'https://lh3.googleusercontent.com/u/0/drive-viewer/AKGpihYSwNOKLAQz0_zWVJCc-61Qkkg9i9StvGYT-XbCVei2xcPH_KuCcIK22KLZR-HyyTH_I1yaPRqlM4wg0qPOP6m9pVnMX83XUYw=w823-h878'

# URL de la imagen para la máscara
background_url = 'https://lh3.googleusercontent.com/drive-viewer/AKGpihb1SulRABBo8VE6P4L5fAN0hJNsV2oZiKKPhb89ImgP9k9mSF-iFoNND_95P40UfUUoBGcl1Pzl_0ujNiAWNyO45WHGfk2r4YM=w1920-h878'

# Lista de URLs de las imágenes
image_urls = [frame1_url, frame2_url, frame3_url]

# Duraciones relativas (proporcionales) en milisegundos
durations = [100, 300, 400]

# BPM inicial
initial_bpm = 60

# Variable global para el índice del fotograma actual
frame_index = 0

# Datos iniciales del electrocardiograma
time = np.linspace(0, 1, 100)
voltage = [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.40, 0.50, 0.60, 0.65, 0.70, 0.75, 0.70, 0.60, 0.40, 0.20, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, -0.30, -0.60, -0.90, -1.20, -1.50, -1.80, -2.10, -2.40, -0.90, 0.60, 2.10, 3.60, 5.10, 6.60, 8.10, 4.10, 0.10, -4.00, -3.43, -2.86, -2.29, -1.72, -1.15, -0.58, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.40, 0.80, 1.00, 1.20, 1.40, 1.53, 1.65, 1.73, 1.80, 1.85, 1.80, 1.70, 1.55, 1.42, 1.30, 1.10, 0.90, 0.70, 0.50, 0.30, 0.24, 0.18, 0.12, 0.06, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00]

# Variables para la simulación en tiempo real
current_time = 0
start = 0  # Definir el inicio de la ventana de visualización
end = 10  # Definir el final de la ventana de visualización
buffer_time = deque()
buffer_voltage = deque()

# Crear la aplicación Dash
app = dash.Dash(__name__)

# Agrega estilos globales
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <title>B&B v1.0</title>
        <style>
            body {
                background-color: #000032;  /* Cambia a tu color preferido */
                display: flex;
                flex-direction: row;
                justify-content: flex-start;
                align-items: flex-start;
                height: 95vh;
                margin: 0;
            }

            #react-entry-point {
                width: 90%; /* Ajusta según sea necesario */
                max-width: 1600px; /* Ajusta el ancho máximo según sea necesario */
                height: auto;
            }

            /* Estilos para las barras de desplazamiento */
            /* Estilos para navegadores basados en WebKit (Chrome, Safari) */
            ::-webkit-scrollbar {
                width: 30px;  /* Ancho de la barra de desplazamiento */
            }

            ::-webkit-scrollbar-track {
                background: #00000000;  /* Color de fondo de la pista */
                margin-top: 20px;  /* Margen superior */
                margin-bottom: 20px;  /* Margen inferior */
            }

            ::-webkit-scrollbar-thumb {
                background-color: #00FFFF;  /* Color del "thumb" */
                border-radius: 30px;  /* Bordes redondeados del "thumb" */
                border: 8px solid #000000;  /* Borde del "thumb" */
                width: 30px;  /* Ancho de la barra de desplazamiento */
            }

            ::-webkit-scrollbar-thumb:hover {
                background: #f53d64;  /* Color del "thumb" al pasar el ratón */
            }

            /* Estilos para Firefox */
            @-moz-document url-prefix() {
                html {
                    scrollbar-width: thin;  /* Ancho de la barra de desplazamiento */
                    scrollbar-color: #00FFFF #000000;  /* Color del "thumb" y de la pista */
                }
            }
        </style>
        <script>
            window.onload = function() {
                // Obtener la resolución de pantalla
                var screenWidth = window.innerWidth;
                var screenHeight = window.innerHeight;
                
                // Dimensiones deseadas del dashboard
                var desiredWidth = 250; // Ancho deseado en píxeles
                var desiredHeight = 140; // Altura deseada en píxeles
                
                // Calcular el zoom deseado basado en ambas dimensiones
                var zoomLevelWidth = screenWidth / desiredWidth;
                var zoomLevelHeight = screenHeight / desiredHeight;
                
                // Tomar el nivel de zoom más pequeño para asegurar que todo el contenido quepa en la pantalla
                var zoomLevel = Math.min(zoomLevelWidth, zoomLevelHeight);
                
                // Ajustar el zoom máximo a 1 para evitar zoom excesivo
                if (zoomLevel > 1) {
                    zoomLevel = 1;
                }
                
                // Aplicar el zoom de manera compatible con diferentes navegadores
                document.body.style.zoom = zoomLevel;
                document.documentElement.style.zoom = zoomLevel;
            }
        </script>
    </head>
    <body>
        <div id="react-entry-point">
            {%app_entry%}
        </div>
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


# Definir el layout de la aplicación
app.layout = html.Div(
    children=[
        # (0) Título del dashboard
        html.Div(
            children=[
                html.H1("❤ Beats&Beats ♪", style={'textAlign': 'center', 'color': '#f53d64', 'fontFamily': 'Calibri', 'fontSize': '60pt', 'margin': '10px'})  # Cambiar el color del título a rojo
            ],
            style={'padding': '0px', 'marginTop': '0px', 'textAlign': 'center'}  # Ajustar margen superior para el título
        ),
        # Contenedor principal del cuerpo del dashboard
        html.Div(
            children=[
                # Contenedor de los divs para la animacion y los filtros
                html.Div(
                    id='content-container',
                    children=[
                        
                        # (1) Div de la animación del corazón y las BPM
                        html.Div(
                            children=[
                                # Div general que contiene los frames y la máscara
                                html.Div(
                                    children=[
                                        # Imagen de fondo
                                        html.Img(src=background_url, style={'position': 'absolute', 'width': '400px', 'height': '290px', 'zIndex': '1', 'top': '50%', 'left': '50%', 'transform': 'translate(-50%, -50%)', 'mixBlendMode': 'screen'}),
                                        # Frame
                                        html.Img(id='frame', src=image_urls[0], style={'position': 'absolute', 'width': '140px', 'height': 'auto', 'zIndex': '2', 'top': '50%', 'left': '50%', 'transform': 'translate(-50%, -50%)'}),
                                    ],
                                    id='frame-container',
                                    style={'width': '100%', 'height': '100%', 'position': 'relative', 'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 'borderRadius': '15px', 'overflow': 'hidden'}
                                ),
                                # Intervalo para cambiar las imágenes cada segundo
                                dcc.Interval(id='interval', interval=1000, n_intervals=0),

                                # Nuevo Div para el electrocardiograma
                                html.Div(
                                    children=[
                                        dcc.Graph(id='live-ecg', config={'displayModeBar': False}),
                                        dcc.Interval(id='interval-component', interval=10, n_intervals=0)
                                    ],
                                     style={'width': '80%', 'height': 'auto', 'margin': '5px auto', 'zIndex': '1'}
                                ),

                                # Contenedor del slider y para mostrar el valor de las BPM
                                html.Div(
                                    children=[
                                        html.Div(
                                            children=[
                                                dcc.Slider(id='bpm-slider', min=20, max=180, step=1, value=initial_bpm, marks={i: str(i) for i in range(0, 201, 40)}, tooltip={'always_visible': True, 'placement': 'bottom'}),
                                                html.Div(id='bpm-output-container', style={'marginTop': '20px', 'fontSize': '200%', 'color': 'white', 'textAlign': 'center', 'fontFamily': 'Calibri'})
                                            ],
                                            style={'width': '500px', 'margin': 'auto', 'position': 'relative', 'zIndex': '1', 'top': '10px', 'backgroundColor': 'transparent'}
                                        )
                                    ],
                                    style={'marginTop': '0px', 'padding-bottom': '20px', 'backgroundColor': 'transparent'}
                                )
                            ],
                            style={'padding': '10px', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center', 'alignItems': 'center', 'width': '600px','height': '600px', 'margin-bottom': '60px', 'backgroundColor': 'black', 'borderRadius': '25px', 'border': '2px solid #00FFFF'}
                        ),
                        
                        # (2) Div para los filtros
                        html.Div(
                            id='filters',
                            children=[
                                # Estilos personalizados para los filtros
                                html.Div(
                                    '''
                                    <style>
                                    .custom-filter .custom-label-1 {
                                        gap: 20px;
                                    }
                                    </style>
                                    ''',
                                    style={"display": "none"}
                                ),
                                
                                # Filtros
                                html.Div([
                                    html.Label(
                                        children=[
                                            html.Div([
                                                html.Label("Age:",
                                                style={'marginBottom': '20px', 'marginTop': '20px', 'fontSize': '220%', 'color': 'white', 'textAlign': 'left', 'fontFamily': 'Calibri'},
                                                )], style={'marginBottom': '20px', 'marginTop': '20px'},
                                            ),
                                            
                                        ],
                                    ),
                                    dcc.RangeSlider(
                                        id='v_age',
                                        min=0,
                                        max=100,
                                        step=1,
                                        value=[10, 90],
                                        marks={i: str(i) for i in range(0, 101, 10)},
                                        tooltip={"placement": "bottom", "always_visible": True},
                                        allowCross=False
                                    )
                                ],
                                style={'margin-bottom': '0px', 'padding-bottom': '10px'}),

                                html.Div([
                                    html.Label("Gender:", style={'padding': '0px', 'fontSize': '220%', 'color': 'white', 'textAlign': 'center', 'fontFamily': 'Calibri'}),
                                    dcc.Checklist(
                                        id='v_sex',
                                        options=[
                                            {'label': 'MALE\u2003\u2003\u2003', 'value': 'M'},
                                            {'label': 'FEMALE\u2003', 'value': 'F'}
                                        ],
                                        inline=True,
                                        value=['M', 'F'],
                                        style={'margin-top': '15px','fontSize': '180%', 'color': '#8898A4', 'textAlign': 'center', 'fontFamily': 'Calibri', 'backgroundColor': '#23292D', 'borderRadius': '0px', 'padding': '10px', 'cursor': 'pointer'}
                                    )                            
                                ], style={'margin-bottom': '20px'}),

                                html.Div([
                                    html.Label("Heart Disease:", style={'padding': '0px', 'fontSize': '220%', 'color': 'white', 'textAlign': 'center', 'fontFamily': 'Calibri'}),
                                    dcc.Checklist(
                                        id='v_HD',
                                        options=[
                                            {'label': 'NO\u2003\u2003', 'value': 0},
                                            {'label': 'YES\u2003', 'value': 1}
                                        ],
                                        inline=True,
                                        value=[0, 1],
                                        style={'margin-top': '15px','fontSize': '180%', 'color': '#8898A4', 'textAlign': 'center', 'fontFamily': 'Calibri', 'backgroundColor': '#23292D', 'borderRadius': '0px', 'padding': '10px', 'cursor': 'pointer'}
                                    )
                                ], style={'margin-bottom': '20px'}),

                                html.Div([
                                    html.Label("Chest Pain Type:", style={'padding': '0px', 'fontSize': '220%', 'color': 'white', 'textAlign': 'center', 'fontFamily': 'Calibri'}),
                                    dcc.Checklist(
                                        id='v_CP',
                                        options=[
                                            {'label': 'ATA\u2003', 'value': 'ATA'},
                                            {'label': 'NAP\u2003', 'value': 'NAP'},
                                            {'label': 'ASY\u2003', 'value': 'ASY'},
                                            {'label': 'TA\u2003\u2003', 'value': 'TA'}
                                        ],
                                        inline=True,
                                        value=['ATA', 'NAP', 'ASY', 'TA'],
                                        style={'margin-top': '15px','fontSize': '180%', 'color': '#8898A4', 'textAlign': 'center', 'fontFamily': 'Calibri', 'backgroundColor': '#23292D', 'borderRadius': '0px', 'padding': '10px', 'cursor': 'pointer'}
                                    )
                                ], style={'margin-bottom': '20px'}),

                                html.Div([
                                    html.Label("Electrocardiographic Results:", style={'padding': '0px', 'fontSize': '220%', 'color': 'white', 'textAlign': 'center', 'fontFamily': 'Calibri'}),
                                    dcc.Checklist(
                                        id='v_elec',
                                        options=[
                                            {'label': 'Normal\u2003\u2003', 'value': 'Normal'},
                                            {'label': 'ST\u2003\u2003\u2003\u2003', 'value': 'ST'},
                                            {'label': 'LVH\u2003\u2003\u2003', 'value': 'LVH'}
                                        ],
                                        inline=True,
                                        value=['Normal', 'ST', 'LVH'],
                                        style={'margin-top': '15px','fontSize': '180%', 'color': '#8898A4', 'textAlign': 'center', 'fontFamily': 'Calibri', 'backgroundColor': '#23292D', 'borderRadius': '0px', 'padding': '10px', 'cursor': 'pointer'}
                                    )
                                ], style={'margin-bottom': '20px'}),

                                html.Div([
                                    # Botón para limpiar los filtros
                                    html.Button("\u00A0\u2715\u00A0\u00A0Clear\u00A0\u00A0", id='clear-filters', n_clicks=0, style={'margin-right': '40px','fontSize': '190%', 'color': '#aaa', 'backgroundColor': '#33007E', 'border': 'none', 'borderRadius': '15px', 'padding': '10px', 'cursor': 'pointer'}),
                                    # Botón para restablecer valores por defecto
                                    html.Button("\u00A0\u27F2\u00A0\u00A0Default\u00A0\u00A0", id='default-filters', n_clicks=0, style={'margin-left': '40px','fontSize': '190%', 'color': '#aaa', 'backgroundColor': '#33007E', 'border': 'none', 'borderRadius': '15px', 'padding': '10px', 'cursor': 'pointer'}),
                                ], style={'display': 'flex', 'justifyContent': 'center'})                            
                            ],
                            style={'padding-left': '50px', 'padding-right': '50px', 'backgroundColor': '#000000', 'borderRadius': '25px', 'border': '2px solid #00FFFF', 'width': '520px', 'height': '750px'}  # Aumentar el ancho del contenedor de filtros
                        )
                    ],
                    style={'display': 'start', 'flexDirection': 'column', 'justifyContent': 'center', 'alignItems': 'start', 'padding': '10px', 'gap': '50px', 'margin-right': '40px', 'margin-top': '20px'}  # Añadir un espacio entre los divs

                ),

                # (3) Contenedor de los divs para los analytics
                html.Div(
                    id='analytics-container',
                    children=[

                        # Div general con los analytics
                        html.Div(
                            id='analytics',
                            children=[
                                # Primer div
                                html.Div(
                                    children=[
                                        dcc.Interval(
                                            #id='interval-component',
                                            #interval=10000,  # Intervalo de actualización en milisegundos (1 segundo)
                                            #n_intervals=0
                                        ),
                                        dcc.Graph(id='maxhr-boxplot', config={'displayModeBar': True})
                                    ],
                                    style={'height': '300px', 'width': '90%', 'margin': '40px auto', 'padding-bottom': '150px'}
                                ),

                                # Segundo div 
                                html.Div(
                                    children=[
                                        dcc.Interval(
                                            #id='interval-component',
                                            #interval=10000,  # Intervalo de actualización en milisegundos (1 segundo)
                                            #n_intervals=0
                                        ),
                                        dcc.Graph(id='cholesterol-boxplot', config={'displayModeBar': True})
                                    ],
                                    style={'height': '300px', 'width': '90%', 'margin': '40px auto', 'padding-bottom': '150px'}
                                ),

                                # Tercer div
                                html.Div(
                                    children=[
                                        dcc.Graph(id='fastingbs-boxplot', config={'displayModeBar': True}),
                                    ],
                                    style={'height': '300px', 'width': '90%', 'margin': '40px auto', 'padding-bottom': '150px'}
                                ),

                                # Cuarto div
                                html.Div(
                                    children=[
                                        dcc.Graph(id='restingbp-boxplot', config={'displayModeBar': True}),
                                    ],
                                    style={'height': '300px', 'width': '90%', 'margin': '40px auto', 'padding-bottom': '150px'}
                                ),

                                # Quinto div con dos sub-divs
                                html.Div([
                                    # Primer div
                                    html.Div(
                                        children=[
                                            dcc.Graph(id='energy-probability-bar', config={'displayModeBar': True}),
                                        ],
                                        style={'height': '300px', 'width': '50%', 'margin': '20px'}
                                    ),
                                    # Segundo div
                                    html.Div(
                                        children=[
                                            dcc.Graph(id='danceability-probability-bar', config={'displayModeBar': True}),
                                        ],
                                        style={'height': '300px', 'width': '50%', 'margin': '20px'}
                                    ),
                                ], style={'display': 'flex','height': '300px', 'width': '90%', 'margin': '40px auto', 'padding-bottom': '150px'}),  # Hacer que los divs inferiores estén en línea


                                # Sexto div con dos sub-divs
                                html.Div([
                                    # Primer div 
                                    html.Div(
                                        children=[
                                            dcc.Graph(id='restingecg-probability-bar', config={'displayModeBar': True}),
                                        ],
                                        style={'height': '300px', 'width': '50%', 'margin': '20px'}
                                    ),
                                    # Segundo div 
                                    html.Div(
                                        children=[
                                            dcc.Graph(id='chestpaintype-probability-bar', config={'displayModeBar': True}),
                                        ],
                                        style={'height': '300px', 'width': '50%', 'margin': '20px'}
                                    ),
                                ], style={'display': 'flex','height': '300px', 'width': '90%', 'margin': '40px auto', 'padding-bottom': '150px'}),  # Hacer que los divs inferiores estén en línea

                            ],
                            style={
                                'width': '60%',
                            }  # Aumentar el ancho del contenedor de los analytics
                        ),

                        # Div de analytics con descripciones
                        html.Div(
                            id='analytics-descriptions',
                            children=[
                                # Primer div
                                html.Div(
                                    children=[
                                        html.H1("MaxHR\u00A0\u00A0[ BPM ]", 
                                                style={
                                                    'margin': '20px',
                                                    'padding': '20px', 
                                                    'fontSize': '230%', 
                                                    'color': '#CCC', 
                                                    'textAlign': 'left', 
                                                    'fontFamily': 'Helvetica'
                                                }),
                                        html.P(
                                            "This chart illustrates the distribution of MaxHR (maximum heart rate achieved in beats per minute [BPM]), depicting the minimum, maximum, median, first quartile (Q1), and third quartile (Q3) values.",
                                            style={
                                                'margin': '20px',
                                                'padding': '20px', 
                                                'fontSize': '200%', 
                                                'color': '#A2C2C2', 
                                                'textAlign': 'left', 
                                                'fontFamily': 'Helvetica'
                                            }
                                        )
                                    ],
                                    style={
                                        'height': '300px', 
                                        'width': '90%', 
                                        'margin': '40px', 
                                        'paddingBottom': '150px',
                                        'backgroundColor': '#111111',
                                    }
                                ),


                                # Segundo div 
                                html.Div(
                                    children=[
                                        html.H1("Cholesterol\u00A0\u00A0[ mg/dl ]", 
                                                style={
                                                    'margin': '20px',
                                                    'padding': '20px', 
                                                    'fontSize': '230%', 
                                                    'color': '#CCC', 
                                                    'textAlign': 'left', 
                                                    'fontFamily': 'Helvetica'
                                                }),
                                        html.P(
                                            "This chart displays the distribution of Cholesterol (serum cholesterol in mg/dl), showing the minimum, maximum, median, first quartile (Q1), and third quartile (Q3) values.",
                                            style={
                                                'margin': '20px',
                                                'padding': '20px', 
                                                'fontSize': '200%', 
                                                'color': '#A2C2C2', 
                                                'textAlign': 'left', 
                                                'fontFamily': 'Helvetica'
                                            }
                                        )
                                    ],
                                    style={
                                        'height': '300px', 
                                        'width': '90%', 
                                        'margin': '40px', 
                                        'paddingBottom': '150px',
                                        'backgroundColor': '#111111',
                                    }
                                ),

                                # Tercer div
                                html.Div(
                                    children=[
                                        html.H1("FastingBS\u00A0\u00A0[ > 120 mg/dl ]", 
                                                style={
                                                    'margin': '20px',
                                                    'padding': '20px', 
                                                    'fontSize': '230%', 
                                                    'color': '#CCC', 
                                                    'textAlign': 'left', 
                                                    'fontFamily': 'Helvetica'
                                                }),
                                        html.P(
                                            "This chart illustrates the distribution of FastingBS (fasting blood sugar in mg/dl), indicating the minimum, maximum, median, first quartile (Q1), and third quartile (Q3) values, with FastingBS > 120 mg/dl highlighted.",
                                            style={
                                                'margin': '20px',
                                                'padding': '20px', 
                                                'fontSize': '200%', 
                                                'color': '#A2C2C2', 
                                                'textAlign': 'left', 
                                                'fontFamily': 'Helvetica'
                                            }
                                        )
                                    ],
                                    style={
                                        'height': '300px', 
                                        'width': '90%', 
                                        'margin': '40px', 
                                        'paddingBottom': '150px',
                                        'backgroundColor': '#111111',
                                    }
                                ),

                                # Cuarto div
                                html.Div(
                                    children=[
                                        html.H1("RestingBP\u00A0\u00A0[ mm Hg ]", 
                                                style={
                                                    'margin': '20px',
                                                    'padding': '20px', 
                                                    'fontSize': '230%', 
                                                    'color': '#CCC', 
                                                    'textAlign': 'left', 
                                                    'fontFamily': 'Helvetica'
                                                }),
                                        html.P(
                                            "This chart displays the distribution of RestingBP (resting blood pressure in mm Hg), highlighting the minimum, maximum, median, first quartile (Q1), and third quartile (Q3) values.",
                                            style={
                                                'margin': '20px',
                                                'padding': '20px', 
                                                'fontSize': '200%', 
                                                'color': '#A2C2C2', 
                                                'textAlign': 'left', 
                                                'fontFamily': 'Helvetica'
                                            }
                                        )
                                    ],
                                    style={
                                        'height': '300px', 
                                        'width': '90%', 
                                        'margin': '40px', 
                                        'paddingBottom': '150px',
                                        'backgroundColor': '#111111',
                                    }
                                ),

                                # Quinto div 
                                html.Div(
                                    children=[
                                        html.H1("Energy & Danceability\u00A0\u00A0[ % ]", 
                                                style={
                                                    'margin': '20px',
                                                    'padding': '20px', 
                                                    'fontSize': '230%', 
                                                    'color': '#CCC', 
                                                    'textAlign': 'left', 
                                                    'fontFamily': 'Helvetica'
                                                }),
                                        html.P(
                                            "These figures depict the probability distributions of Energy and Danceability, plotted for confidence levels exceeding 60 percent and 80 percent respectively.",
                                            style={
                                                'margin': '20px',
                                                'padding': '20px', 
                                                'fontSize': '200%', 
                                                'color': '#A2C2C2', 
                                                'textAlign': 'left', 
                                                'fontFamily': 'Helvetica'
                                            }
                                        )
                                    ],
                                    style={
                                        'height': '300px', 
                                        'width': '90%', 
                                        'margin': '40px', 
                                        'paddingBottom': '150px',
                                        'backgroundColor': '#111111',
                                    }
                                ),
                                
                                # Sexto div con los últimos cuatro sub-divs
                                html.Div(
                                    children=[
                                        html.H1("RestingECG & ChestPainType\u00A0\u00A0[ % ]", 
                                                style={
                                                    'margin': '20px',
                                                    'padding': '20px', 
                                                    'fontSize': '230%', 
                                                    'color': '#CCC', 
                                                    'textAlign': 'left', 
                                                    'fontFamily': 'Helvetica'
                                                }),
                                        html.P(
                                            "RestingECG displays probability distributions for categories: Normal (normal ECG), ST (ST-T wave abnormality), and LVH (left ventricular hypertrophy by Estes' criteria). ChestPainType displays likelihood distributions for categories: TA (Typical Angina), ATA (Atypical Angina), NAP (Non-Anginal Pain), and ASY (Asymptomatic).",
                                            style={
                                                'margin': '20px',
                                                'padding': '20px', 
                                                'fontSize': '200%', 
                                                'color': '#A2C2C2', 
                                                'textAlign': 'left', 
                                                'fontFamily': 'Helvetica'
                                            }
                                        )
                                    ],
                                    style={
                                        'height': '300px', 
                                        'width': '90%', 
                                        'margin': '40px', 
                                        'paddingBottom': '150px',
                                        'backgroundColor': '#111111',
                                    }
                                ),
                            ],
                            style={
                                'width': '40%',
                            }  # Aumentar el ancho del contenedor de los analytics
                        ),
                    ],
                    style={
                        'padding': '10px',
                        'backgroundColor': '#000000',
                        'borderRadius': '25px',
                        'border': '2px solid #00FFFF',
                        'width': '100%',
                        'height': '1413px',
                        'margin-top': '30px',
                        'margin-right': '40px', 
                        'display': 'flex', 
                        'justifyContent': 'center', 
                        'alignItems': 'stretch',
                        'overflow': 'auto',
                        },
                ),
            ],
            style={'display': 'flex', 'justifyContent': 'center', 'padding': '0px', 'margin': '0px', 'width': '100%'}
        )
    ],
    style={'backgroundColor': '#000032', 'padding': '0px', 'justifyContent': 'center', 'position': 'relative', 'width': '3000px', 'height': '100%', 'overflow': 'auto'}
)


# Función para generar datos en tiempo real con ventana desplazada
def generate_ecg_data(bpm, duration=None, sampling_frequency=100):
    if duration is None:
            duration = int(10 * (bpm / 60))  # Calcula la duración basada en las BPM

    global current_time, buffer_time, buffer_voltage, start, end
    
    # Factor de conversión para ajustar el tiempo basado en las BPM
    conversion_factor = 60 / bpm
    total_samples = int(duration * sampling_frequency)
    extended_pattern = np.tile(voltage, int(np.ceil(total_samples / len(voltage))))
    
    # Agregar los nuevos datos al buffer
    if buffer_time:
        adjusted_time = buffer_time[-1] + conversion_factor / sampling_frequency
    else:
        adjusted_time = 0

    buffer_time.append(adjusted_time)
    buffer_voltage.append(extended_pattern[int(current_time * sampling_frequency) % len(extended_pattern)])
    
    # Limitar el buffer a los últimos 10 segundos
    if len(buffer_time) > sampling_frequency * duration:
        buffer_time = deque(list(buffer_time)[-sampling_frequency * duration:])
        buffer_voltage = deque(list(buffer_voltage)[-sampling_frequency * duration:])
    
    # Actualizar el tiempo actual
    current_time += 1 / sampling_frequency
    
    # Actualizar la escala del eje x para la ventana de 10 segundos
    if adjusted_time > (end - 2.5):
        start += conversion_factor / sampling_frequency
        end += conversion_factor / sampling_frequency
    
    return buffer_time, buffer_voltage


# Callback para actualizar la animación del corazón y el intervalo
@app.callback(
    [Output('frame', 'src'), Output('interval', 'interval')],
    [Input('interval', 'n_intervals'), Input('bpm-slider', 'value')]
)
def update_image_and_interval(n_intervals, bpm):
    global frame_index
    frame_index = (frame_index + 1) % len(image_urls)
    interval = int((60 / bpm) * 1000 / 3)  # Ajusta el intervalo de la animación
    return image_urls[frame_index], interval

# Callback para actualizar el electrocardiograma
@app.callback(
    Output('live-ecg', 'figure'),
    [Input('bpm-slider', 'value'), Input('interval-component', 'n_intervals')]
)
def update_ecg(bpm, n_intervals):
    time_values, ecg_data = generate_ecg_data(bpm)
    
    # Crear la figura de Plotly
    figure = {
        'data': [
            go.Scatter(
                x=list(time_values),
                y=list(ecg_data),
                mode='lines',
                line={'color': '#f53d64'}
            )
        ],
        'layout': go.Layout(
            autosize=True,
            margin=dict(l=10, r=10, t=10, b=40),
            height=150,  # Ajusta la altura de la gráfica según sea necesario
            paper_bgcolor='black',
            plot_bgcolor='black',
            font={'color': '#00ffff'},
            xaxis=dict(
                showgrid=True,
                zeroline=True,
                gridcolor='#222',
                range=[start, end]  # Mostrar los últimos 10 segundos
            ),
            yaxis=dict(
                showgrid=True,
                zeroline=True,
                gridcolor='#222',
                range=[-6, 10]  # Ajustar la escala del eje y
            )
        )
    }
    return figure

# Callback para mostrar el valor actual de las BPM
@app.callback(
    Output('bpm-output-container', 'children'),
    [Input('bpm-slider', 'value')]
)
def update_bpm_output(value):
    global initial_bpm
    initial_bpm = value
    return f'BPM: {value}'

# Callback para limpiar los filtros y restablecer los valores predeterminados
@app.callback(
    [
        Output('v_age', 'value'),
        Output('v_sex', 'value'),
        Output('v_HD', 'value'),
        Output('v_CP', 'value'),
        Output('v_elec', 'value')
    ],
    [
        Input('clear-filters', 'n_clicks'),
        Input('default-filters', 'n_clicks')
    ],
    prevent_initial_call=True
)
def handle_filters(clear_clicks, default_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'clear-filters':
        return [10, 90], [], [], [], []
    elif triggered_id == 'default-filters':
        return [10, 90], ['M', 'F'], [0, 1], ['ATA', 'NAP', 'ASY', 'TA'], ['Normal', 'ST', 'LVH']

# Callback para actualizar el gráfico MaxHR
@app.callback(
    Output('maxhr-boxplot', 'figure'),
    [
        Input('v_age', 'value'),  # Capturar cambios en los filtros
        Input('v_sex', 'value'),
        Input('v_HD', 'value'),
        Input('v_CP', 'value'),
        Input('v_elec', 'value')
    ]
)
def update_graph(v_age, v_sex, v_HD, v_CP, v_elec):
    # Filtrar el DataFrame según los filtros seleccionados
    filtered_df = dfheart[
        (dfheart['Age'].between(v_age[0], v_age[1])) &
        (dfheart['Sex'].isin(v_sex)) &
        (dfheart['HeartDisease'].isin(v_HD)) &
        (dfheart['ChestPainType'].isin(v_CP)) &
        (dfheart['RestingECG'].isin(v_elec))
    ]

    # Calcular estadísticas para el DataFrame filtrado
    Q1 = filtered_df['MaxHR'].quantile(0.25)
    Q3 = filtered_df['MaxHR'].quantile(0.75)
    min_value = filtered_df['MaxHR'].min()
    max_value = filtered_df['MaxHR'].max()
    median_value = filtered_df['MaxHR'].median()

    # Crear el gráfico de caja con Plotly Express
    fig = px.box(filtered_df, x='MaxHR', points='all', orientation='h', template='plotly_dark')
    
    # Añadir líneas para Q1, Q3, mínimo, máximo y mediana
    fig.update_traces(marker=dict(color='cyan'), line=dict(color='cyan'))
    fig.add_vline(x=Q1, line_dash='dash', line_color='blue', annotation_text=f'Q1: {Q1:.2f}')
    fig.add_vline(x=Q3, line_dash='dash', line_color='green', annotation_text=f'Q3: {Q3:.2f}')
    fig.add_vline(x=min_value, line_dash='dash', line_color='purple', annotation_text=f'Min: {min_value:.2f}')
    fig.add_vline(x=max_value, line_dash='dash', line_color='orange', annotation_text=f'Max: {max_value:.2f}')
    fig.add_vline(x=median_value, line_dash='dash', line_color='red', annotation_text=f'Median: {median_value:.2f}')
    
    # Personalizar el diseño del gráfico
    fig.update_layout(
        title="Distribution of MaxHR [BPM]",
        xaxis_title="",
        yaxis_title="MaxHR",
        showlegend=False
    )

    return fig

# Callback para actualizar el gráfico Cholesterol
@app.callback(
    Output('cholesterol-boxplot', 'figure'),
    [
        Input('v_age', 'value'),  # Capturar cambios en los filtros
        Input('v_sex', 'value'),
        Input('v_HD', 'value'),
        Input('v_CP', 'value'),
        Input('v_elec', 'value')
    ]
)
def update_cholesterol_graph(v_age, v_sex, v_HD, v_CP, v_elec):
    # Filtrar el DataFrame según los filtros seleccionados
    filtered_df = dfheart[
        (dfheart['Age'].between(v_age[0], v_age[1])) &
        (dfheart['Sex'].isin(v_sex)) &
        (dfheart['HeartDisease'].isin(v_HD)) &
        (dfheart['ChestPainType'].isin(v_CP)) &
        (dfheart['RestingECG'].isin(v_elec))
    ]

    # Calcular estadísticas para el DataFrame filtrado
    Q1 = filtered_df['Cholesterol'].quantile(0.25)
    Q3 = filtered_df['Cholesterol'].quantile(0.75)
    min_value = filtered_df['Cholesterol'].min()
    max_value = filtered_df['Cholesterol'].max()
    median_value = filtered_df['Cholesterol'].median()

    # Crear el gráfico de caja con Plotly Express
    fig = px.box(filtered_df, x='Cholesterol', points='all', orientation='h', template='plotly_dark')
    
    # Añadir líneas para Q1, Q3, mínimo, máximo y mediana
    fig.update_traces(marker=dict(color='cyan'), line=dict(color='cyan'))
    fig.add_vline(x=Q1, line_dash='dash', line_color='blue', annotation_text=f'Q1: {Q1:.2f}')
    fig.add_vline(x=Q3, line_dash='dash', line_color='green', annotation_text=f'Q3: {Q3:.2f}')
    fig.add_vline(x=min_value, line_dash='dash', line_color='purple', annotation_text=f'Min: {min_value:.2f}')
    fig.add_vline(x=max_value, line_dash='dash', line_color='orange', annotation_text=f'Max: {max_value:.2f}')
    fig.add_vline(x=median_value, line_dash='dash', line_color='red', annotation_text=f'Median: {median_value:.2f}')
    
    # Personalizar el diseño del gráfico
    fig.update_layout(
        title="Distribution of Cholesterol [mg/dl]",
        xaxis_title="Cholesterol",
        yaxis_title="",
        showlegend=False
    )

    return fig

# Callback para actualizar el gráfico FastingBS
@app.callback(
    Output('fastingbs-boxplot', 'figure'),
    [
        Input('v_age', 'value'),  # Capturar cambios en los filtros
        Input('v_sex', 'value'),
        Input('v_HD', 'value'),
        Input('v_CP', 'value'),
        Input('v_elec', 'value')
    ]
)
def update_fastingbs_graph(v_age, v_sex, v_HD, v_CP, v_elec):
    # Filtrar el DataFrame según los filtros seleccionados
    filtered_df = dfheart[
        (dfheart['Age'].between(v_age[0], v_age[1])) &
        (dfheart['Sex'].isin(v_sex)) &
        (dfheart['HeartDisease'].isin(v_HD)) &
        (dfheart['ChestPainType'].isin(v_CP)) &
        (dfheart['RestingECG'].isin(v_elec))
    ]

    # Calcular estadísticas para el DataFrame filtrado
    Q1 = filtered_df['FastingBS'].quantile(0.25)
    Q3 = filtered_df['FastingBS'].quantile(0.75)
    min_value = filtered_df['FastingBS'].min()
    max_value = filtered_df['FastingBS'].max()
    median_value = filtered_df['FastingBS'].median()

    # Crear el gráfico de caja con Plotly Express
    fig = px.box(filtered_df, x='FastingBS', points='all', orientation='h', template='plotly_dark')
    
    # Añadir líneas para Q1, Q3, mínimo, máximo y mediana
    fig.update_traces(marker=dict(color='cyan'), line=dict(color='cyan'))
    fig.add_vline(x=Q1, line_dash='dash', line_color='blue', annotation_text=f'Q1: {Q1:.2f}')
    fig.add_vline(x=Q3, line_dash='dash', line_color='green', annotation_text=f'Q3: {Q3:.2f}')
    fig.add_vline(x=min_value, line_dash='dash', line_color='purple', annotation_text=f'Min: {min_value:.2f}')
    fig.add_vline(x=max_value, line_dash='dash', line_color='orange', annotation_text=f'Max: {max_value:.2f}')
    fig.add_vline(x=median_value, line_dash='dash', line_color='red', annotation_text=f'Median: {median_value:.2f}')
    
    # Personalizar el diseño del gráfico
    fig.update_layout(
        title="Distribution of FastingBS [> 120 mg/dl]",
        xaxis_title="FastingBS",
        yaxis_title="",
        showlegend=False
    )

    return fig

# Callback para actualizar el gráfico RestingBP
@app.callback(
    Output('restingbp-boxplot', 'figure'),
    [
        Input('v_age', 'value'),  # Capturar cambios en los filtros
        Input('v_sex', 'value'),
        Input('v_HD', 'value'),
        Input('v_CP', 'value'),
        Input('v_elec', 'value')
    ]
)
def update_restingbp_graph(v_age, v_sex, v_HD, v_CP, v_elec):
    # Filtrar el DataFrame según los filtros seleccionados
    filtered_df = dfheart[
        (dfheart['Age'].between(v_age[0], v_age[1])) &
        (dfheart['Sex'].isin(v_sex)) &
        (dfheart['HeartDisease'].isin(v_HD)) &
        (dfheart['ChestPainType'].isin(v_CP)) &
        (dfheart['RestingECG'].isin(v_elec))
    ]

    # Calcular estadísticas para el DataFrame filtrado
    Q1 = filtered_df['RestingBP'].quantile(0.25)
    Q3 = filtered_df['RestingBP'].quantile(0.75)
    min_value = filtered_df['RestingBP'].min()
    max_value = filtered_df['RestingBP'].max()
    median_value = filtered_df['RestingBP'].median()

    # Crear el gráfico de caja con Plotly Express
    fig = px.box(filtered_df, x='RestingBP', points='all', orientation='h', template='plotly_dark')
    
    # Añadir líneas para Q1, Q3, mínimo, máximo y mediana
    fig.update_traces(marker=dict(color='cyan'), line=dict(color='cyan'))
    fig.add_vline(x=Q1, line_dash='dash', line_color='blue', annotation_text=f'Q1: {Q1:.2f}')
    fig.add_vline(x=Q3, line_dash='dash', line_color='green', annotation_text=f'Q3: {Q3:.2f}')
    fig.add_vline(x=min_value, line_dash='dash', line_color='purple', annotation_text=f'Min: {min_value:.2f}')
    fig.add_vline(x=max_value, line_dash='dash', line_color='orange', annotation_text=f'Max: {max_value:.2f}')
    fig.add_vline(x=median_value, line_dash='dash', line_color='red', annotation_text=f'Median: {median_value:.2f}')
    
    # Personalizar el diseño del gráfico
    fig.update_layout(
        title="Distribution of RestingBP [mm Hg]",
        xaxis_title="RestingBP",
        yaxis_title="",
        showlegend=False
    )

    return fig

# Función para calcular la probabilidad de energía en un rango de BPM
def calculate_energy_probability(df, lower_limit, upper_limit, threshold1, threshold2):
    # Filtrar el DataFrame según los límites de BPM
    filt_df = df[df['Tempo'].between(lower_limit, upper_limit)]
    
    # Contar el número de registros
    total_registros = len(filt_df)
    
    if total_registros == 0:
        return 0.0, 0.0
    
    # Contar el número de registros con energía mayor o igual a cada umbral
    energia_cumple_threshold1 = len(filt_df[filt_df['Energy'] >= threshold1])
    energia_cumple_threshold2 = len(filt_df[filt_df['Energy'] >= threshold2])
    
    # Calcular las probabilidades
    probabilidad1 = energia_cumple_threshold1 / total_registros
    probabilidad2 = energia_cumple_threshold2 / total_registros
    
    return probabilidad1, probabilidad2

# Callback para actualizar el gráfico Energy
@app.callback(
    Output('energy-probability-bar', 'figure'),
    [Input('bpm-slider', 'value')]  # Capturar cambios en los filtros
)
def update_energy_probability_graph(value):
    # Calcular límites superior e inferior del rango de BPM
    upper_limit = round(value / 10) * 10
    lower_limit = upper_limit - 5
    
    # Calcular la probabilidad de energía para los umbrales 60% y 80%
    probabilidad_energia60, probabilidad_energia80 = calculate_energy_probability(dfspfy, lower_limit, upper_limit, 0.60, 0.80)
    
    # Crear el gráfico de barras con Plotly
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=['Probability > 60%'],
        y=[probabilidad_energia60 * 100],  # Convertir la probabilidad a porcentaje
        name='Energy > 60%',
        marker_color='rgba(230, 0, 240, 0.35)',  # Color morado semi-transparente (relleno)
        marker_line_color='rgb(230, 0, 240)',  # Color morado sólido (borde)
        marker_line_width=3,  # Ancho del borde del rectángulo
    ))
    
    fig.add_trace(go.Bar(
        x=['Probability > 80%'],
        y=[probabilidad_energia80 * 100],  # Convertir la probabilidad a porcentaje
        name='Energy > 80%',
        marker_color='rgba(150, 0, 255, 0.35)',  # Otro color semi-transparente para la segunda barra
        marker_line_color='rgb(150, 0, 255)',  # Color sólido para el borde de la segunda barra
        marker_line_width=3,  # Ancho del borde del rectángulo
    ))

    # Personalizar el diseño del gráfico
    fig.update_layout(
        xaxis=dict(tickmode='array', tickvals=[]),  # Eliminar etiquetas en el eje x
        yaxis=dict(title='Probability (%)', range=[0, 100]),  # Título del eje y con rango fijo
        title=f'Probability of Energy at {value} BPM',  # Título del gráfico con valor de BPM actual
        barmode='group',  # Agrupar las barras juntas
        showlegend=True,  # Mostrar leyenda
        template='plotly_dark'  # Tema oscuro
    )

    return fig

# Función para calcular la probabilidad de danceability en un rango de BPM
def calculate_danceability_probability(df, lower_limit, upper_limit, threshold1, threshold2):
    # Filtrar el DataFrame según los límites de BPM
    filt_df = df[df['Tempo'].between(lower_limit, upper_limit)]
    
    # Contar el número de registros
    total_registros = len(filt_df)
    
    if total_registros == 0:
        return 0.0, 0.0
    
    # Contar el número de registros con danceability mayor o igual a cada umbral
    danceability_cumple_threshold1 = len(filt_df[filt_df['Danceability'] >= threshold1])
    danceability_cumple_threshold2 = len(filt_df[filt_df['Danceability'] >= threshold2])
    
    # Calcular las probabilidades
    probabilidad1 = danceability_cumple_threshold1 / total_registros
    probabilidad2 = danceability_cumple_threshold2 / total_registros
    
    return probabilidad1, probabilidad2

# Callback para actualizar el gráfico Danceability
@app.callback(
    Output('danceability-probability-bar', 'figure'),
    [Input('bpm-slider', 'value')]  # Capturar cambios en los filtros
)
def update_danceability_probability_graph(value):
    # Calcular límites superior e inferior del rango de BPM
    upper_limit = round(value / 10) * 10
    lower_limit = upper_limit - 5
    
    # Calcular la probabilidad de danceability para los umbrales 60% y 80%
    probabilidad_danceability60, probabilidad_danceability80 = calculate_danceability_probability(dfspfy, lower_limit, upper_limit, 0.60, 0.80)
    
    # Crear el gráfico de barras con Plotly
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=['Probability > 60%'],
        y=[probabilidad_danceability60 * 100],  # Convertir la probabilidad a porcentaje
        name='Danceability > 60%',
        marker_color='rgba(255, 220, 0, 0.45)',  # Color amarillo semi-transparente (relleno)
        marker_line_color='rgb(255, 220, 0)',  # Color amarillo sólido (borde)
        marker_line_width=3,  # Ancho del borde del rectángulo
    ))
    
    fig.add_trace(go.Bar(
        x=['Probability > 80%'],
        y=[probabilidad_danceability80 * 100],  # Convertir la probabilidad a porcentaje
        name='Danceability > 80%',
        marker_color='rgba(255, 142, 0, 0.35)',  # Otro color semi-transparente para la segunda barra
        marker_line_color='rgb(255, 142, 0)',  # Color sólido para el borde de la segunda barra
        marker_line_width=3,  # Ancho del borde del rectángulo
    ))

    # Personalizar el diseño del gráfico
    fig.update_layout(
        xaxis=dict(tickmode='array', tickvals=[]),  # Eliminar etiquetas en el eje x
        yaxis=dict(title='Probability (%)', range=[0, 100]),  # Título del eje y con rango fijo
        title=f'Probability of Danceability at {value} BPM',  # Título del gráfico con valor de BPM actual
        barmode='group',  # Agrupar las barras juntas
        showlegend=True,  # Mostrar leyenda
        template='plotly_dark'  # Tema oscuro
    )

    return fig

# Callback para actualizar el gráfico RestingECG
@app.callback(
    Output('restingecg-probability-bar', 'figure'),
    [
        Input('v_age', 'value'),  # Capturar cambios en los filtros
        Input('v_sex', 'value'),
        Input('v_HD', 'value'),
        Input('v_CP', 'value'),
        Input('v_elec', 'value')
    ]
)
def update_restingecg_probability_graph(v_age, v_sex, v_HD, v_CP, v_elec):
    # Filtrar el DataFrame según los filtros seleccionados
    filtered_df = dfheart[
        (dfheart['Age'].between(v_age[0], v_age[1])) &
        (dfheart['Sex'].isin(v_sex)) &
        (dfheart['HeartDisease'].isin(v_HD)) &
        (dfheart['ChestPainType'].isin(v_CP)) &
        (dfheart['RestingECG'].isin(v_elec))
    ]

    # Calcular la probabilidad de cada categoría de RestingECG
    probabilities = (filtered_df['RestingECG'].value_counts() / len(filtered_df)) * 100

    # Crear el gráfico de barras con Plotly
    fig = go.Figure(go.Bar(
        x=probabilities.index,
        y=probabilities.values,
        marker_color='rgba(0, 255, 255, 0.45)',  # Color cyan semi-transparente (relleno)
        marker_line_color='rgb(0, 255, 255)',  # Color cyan sólido (borde)
        marker_line_width=3,  # Ancho del borde del rectángulo
    ))

    # Personalizar el diseño del gráfico
    fig.update_layout(
        xaxis=dict(title='RestingECG'),  # Título del eje x
        yaxis=dict(title='Probability (%)'),  # Título del eje y
        title='Probability of RestingECG',  # Título del gráfico
        showlegend=False,  # Ocultar leyenda
        template='plotly_dark'  # Tema oscuro
    )

    return fig

# Callback para actualizar el gráfico chestpaintype
@app.callback(
    Output('chestpaintype-probability-bar', 'figure'),
    [
        Input('v_age', 'value'),  # Capturar cambios en los filtros
        Input('v_sex', 'value'),
        Input('v_HD', 'value'),
        Input('v_CP', 'value'),
        Input('v_elec', 'value')
    ]
)
def update_chestpaintype_probability_graph(v_age, v_sex, v_HD, v_CP, v_elec):
    # Filtrar el DataFrame según los filtros seleccionados
    filtered_df = dfheart[
        (dfheart['Age'].between(v_age[0], v_age[1])) &
        (dfheart['Sex'].isin(v_sex)) &
        (dfheart['HeartDisease'].isin(v_HD)) &
        (dfheart['ChestPainType'].isin(v_CP)) &
        (dfheart['RestingECG'].isin(v_elec))
    ]

    # Calcular la probabilidad de cada categoría de ChestPainType
    probabilities = (filtered_df['ChestPainType'].value_counts() / len(filtered_df)) * 100

    # Crear el gráfico de barras con Plotly
    fig = go.Figure(go.Bar(
        x=probabilities.index,
        y=probabilities.values,
        marker_color='rgba(0, 255, 255, 0.45)',  # Color cyan semi-transparente (relleno)
        marker_line_color='rgb(0, 255, 255)',  # Color cyan sólido (borde)
        marker_line_width=3,  # Ancho del borde del rectángulo
    ))

    # Personalizar el diseño del gráfico
    fig.update_layout(
        xaxis=dict(title='ChestPainType'),  # Título del eje x
        yaxis=dict(title='Probability (%)'),  # Título del eje y
        title='Probability of ChestPainType Categories',  # Título del gráfico
        showlegend=False,  # Ocultar leyenda
        template='plotly_dark'  # Tema oscuro
    )

    return fig

if __name__ == '__main__':
    # Ejecutar la aplicación
    app.run_server(debug=True, port=8050)