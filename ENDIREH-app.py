import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import json



# Configuration of the page
st.set_page_config(layout='wide')
# Setting the Roboto font
with open( "style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

#------------- 0. Leer el conjunto de datos
df = pd.read_csv("data/raw/TSDem.csv",encoding='latin1').rename(columns=str.lower)
df['cve_ent'] = df['cve_ent'].astype(str).str.zfill(2)


# Dejar solo las observaciones de los jefes del hogar
df1 = df.query('paren == 1')[['id_viv','viv_sel','sexo','cve_ent','nom_ent','fac_viv','dominio']].copy()
df1.drop_duplicates(inplace=True)
df1['obs'] = df1.groupby('id_viv')['id_viv'].transform('size')
# Crear la nueva categoria de jefatura
df1['new_jefe'] = np.where(df1['obs'] == 2, 0,df1['sexo'])
# Eliminar una observación de los que estan en esa categoría
df1.drop('sexo',axis=1,inplace=True)
df1.drop_duplicates(inplace=True)


# Crear las variables de totales de viviendas con factor de expansión
df1['viv_dom_jef'] = df1.groupby(['dominio','new_jefe'])['fac_viv'].transform('sum')
df1['viv_dom'] = df1.groupby(['dominio'])['fac_viv'].transform('sum')
df1['viv_jef'] = df1.groupby(['new_jefe'])['fac_viv'].transform('sum')
df1['viv_ent_dom_jef'] = df1.groupby(['cve_ent','dominio','new_jefe'])['fac_viv'].transform('sum')


# Titulo
st.header('''Análisis de la jefatura de los hogares en México según el sexo y localización urbana-conurbada-rural''')
st.markdown("<p style='margin-top: 1cm;line-height:0;'>April 4, 2025</p>",True)
st.markdown("<p style='margin-bottom: 1cm;'>Andrea Del Pilar Guerrero Jimenez</p>",True)

col = st.columns((4,6),gap='medium')

with col[1]:
  st.subheader(':red-background[Distribución nacional por jefatura y dominio]')

# Inicio de herramienta
col = st.columns((4,4,2), gap='medium')

with col[0]:
  #------------- 1. Title and description

  st.markdown('''Los análisis exploratorios, mediante el uso de estadísticos descriptivos y visualizaciones, son valuables herramientas para la identificación de comportamientos en los datos. ''')

  st.markdown('''En el tratamiento de la información y desarrollo de esta *herramienta*, utilicé **Python**, junto con los paquetes **Streamlit**, **NumPy**, **Pandas** y **Geopandas**. La fuente de datos corresponde a los microdatos de uso público del módulo de **características sociodemográficas** de la **Encuesta Nacional sobre la Dinámica de las Relaciones de los Hogares** (ENDIREH) 2021. Ejercicio estadístico realizado por el Instituto Nacional de Estadística y Geográfia (INEGI) en México desde 2003.''')

  st.markdown('''El objetivo es responder ¿Cuál es la proporción de hogares con jefaturas de mujeres y hombres? ¿Este porcentaje, en los hogares con liderazgo femenino, presenta diferencias entre areas urbanas y rurales? ''')

  st.markdown(f'''La encuesta fue respondida por 36,006,932 viviendas. Al segmentar los datos según el sexo del jefe del hogar, 435,967 viviendas indicaron compartir la jefatura entre sexos.''')




with col[1]:
#------------- 2. Descripción del universo

  #------------- 2. Gráfico:

  # Calcular los totales para calcular los porcentajes
  tb1 = df1.groupby('new_jefe')['fac_viv'].sum().to_frame('total_viv')
  tb1['porc'] = ((tb1['total_viv'] / tb1['total_viv'].sum())*100)


  # Para la categoria de ambos sexos
  st.markdown("<p style='border-bottom: 1px solid #5d6d7e;font-weight: 630;'>compartida</p>",True)
  box1, box2 = st.columns(2)
  box1.metric(label='viviendas',border=True,
              value=f"{tb1.query('new_jefe == 0')['total_viv'].iloc[0]:,.0f}")
  box2.metric(label='proporción',border=True,
              value=f"{tb1.query('new_jefe == 0')['porc'].iloc[0]:,.2f}%")

  # Para las categorias de solo mujer o hombre

  # Mujeres
  st.markdown("<p style='border-bottom: 1px solid #5d6d7e;font-weight: 630;'>mujer</p>",True)

  box11, box12 = st.columns(2)
  box11.metric(label='viviendas',border=True,
              value=f"{tb1.query('new_jefe == 2')['total_viv'].iloc[0]:,.0f}")
  box12.metric(label='proporción',border=True,
              value=f"{tb1.query('new_jefe == 2')['porc'].iloc[0]:,.2f}%")


  # Hombres
  st.markdown("<p style='border-bottom: 1px dashed #5d6d7e;font-weight: 630;'>hombre</p>",True)

  box21, box22 = st.columns(2)
  box21.metric(label='viviendas',border=True,
              value=f"{tb1.query('new_jefe == 1')['total_viv'].iloc[0]:,.0f}")
  box22.metric(label='proporción',border=True,
              value=f"{tb1.query('new_jefe == 1')['porc'].iloc[0]:,.2f}%")


  prop_hous = (tb1.query('new_jefe == 1')['total_viv'].iloc[0]/tb1.query('new_jefe == 2')['total_viv'].iloc[0]).round(0)
  


with col[2]:

  tb1 = df1[['dominio','viv_dom']].copy()
  tb1.drop_duplicates(inplace=True)
  tb1['por_tot'] = (tb1['viv_dom'] / tb1['viv_dom'].sum())*100
  tb1.replace({'U':'urbano','C':'conurbado','R':'rural'},inplace=True)

  fig = px.pie(tb1,values='por_tot',names='dominio',hover_data='viv_dom',color_discrete_sequence=px.colors.qualitative.Antique)
  fig.update_traces(textposition='inside', textinfo='percent+label')
  fig.update_layout(showlegend=False)
  st.plotly_chart(fig)










#------------- Segunda gran fila

st.subheader(''':red-background[Distribución de tipo de jefaturas por dominio]''')


# Hago una copia de mis datos base, no elimino duplicados porque necesito ver el factor de expansion
tb1 = df1[['new_jefe','dominio','viv_dom_jef','viv_dom','viv_jef']].copy()
# Ahora si eliminar los duplicados porque ya calcule los totales antes
tb1.drop_duplicates(inplace=True)
# Esta variable me cuenta el total, que deben ser los 30 millones
tb1['viv_tot'] = tb1.groupby(['dominio'])['viv_jef'].transform('sum')
# Calcular el porcentaje de dom_je dentro del total dominio
tb1['por_dom_jef'] = (tb1['viv_dom_jef']/tb1['viv_dom'])*100


# boton para seleccionar el dominio
dom = st.selectbox('Selecciona uno de los tres dominios de la lista desplegable para ver su definición, distribución por jefatura y distribución espacial:',('urbano','conurbado','rural'), label_visibility='visible')


if dom == 'urbano':
  dominio = 'U'
  st.markdown('El dominio urbano integra a las viviendas localizadas en ciudades con más de 100 mil habitantes.')

if dom == 'conurbado':
  dominio = 'C'
  st.markdown('El dominio conurbano integra a las viviendas localizadas en zonas con más de 2,500 habitantes y hasta 99,999 habitantes.')

if dom == 'rural':
  dominio = 'R'
  st.markdown('El dominio rural integra a las viviendas localizadas en zonas con menos de 2,500 habitantes.')



col = st.columns((2.5,7),gap='medium')

with col[0]:

  st.subheader('Dsitribución por jefatura')

  # Para la categoria de ambos sexos
  st.markdown("<p style='border-bottom: 1px solid #5d6d7e;font-weight: 630;'>compartida</p>",True)
  box1, box2 = st.columns(2)
  box1.metric(label='viviendas',border=True,
              value=f"{tb1[tb1['dominio']==dominio].query('new_jefe == 0')['viv_dom_jef'].iloc[0]:,.0f}")
  box2.metric(label='proporción',border=True,
              value=f"{tb1[tb1['dominio']==dominio].query('new_jefe == 0')['por_dom_jef'].iloc[0]:,.2f}%")

  # Para las categorias de solo mujer o hombre

  # Mujeres
  st.markdown("<p style='border-bottom: 1px solid #5d6d7e;font-weight: 630;'>mujer</p>",True)

  box11, box12 = st.columns(2)
  box11.metric(label='viviendas',border=True,
              value=f"{tb1[tb1['dominio']==dominio].query('new_jefe == 2')['viv_dom_jef'].iloc[0]:,.0f}")
  box12.metric(label='proporción',border=True,
              value=f"{tb1[tb1['dominio']==dominio].query('new_jefe == 2')['por_dom_jef'].iloc[0]:,.2f}%")


  # Hombres
  st.markdown("<p style='border-bottom: 1px dashed #5d6d7e;font-weight: 630;'>hombre</p>",True)

  box21, box22 = st.columns(2)
  box21.metric(label='viviendas',border=True,
              value=f"{tb1[tb1['dominio']==dominio].query('new_jefe == 1')['viv_dom_jef'].iloc[0]:,.0f}")
  box22.metric(label='proporción',border=True,
              value=f"{tb1[tb1['dominio']==dominio].query('new_jefe == 1')['por_dom_jef'].iloc[0]:,.2f}%")



# Base de datos para los mapas

# 1. Crear el conjunto de datos por entidad federativa
tb1 = df1[['cve_ent','nom_ent','dominio','new_jefe','viv_ent_dom_jef']].copy()
tb1.drop_duplicates(inplace=True)

# 2. Cargar la capa JSON
# Upload the json file
with open('data/raw/MGN/00ent.json') as f:
  mex_states = json.load(f)

# 2. Hacer una función para crear el mapa
def hacer_mapa(base,col,label,escala_color):
  fig = px.choropleth(base,geojson=mex_states,locations='cve_ent',featureidkey='properties.CVE_ENT',
                    color=col,hover_data='nom_ent',
                    labels=label,
                    color_continuous_scale=escala_color)
  fig.update_geos(fitbounds="locations", visible=False)
  fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
  fig.update_traces(marker_line_width=0.5, hoverinfo="location+z")
  return fig



# Poner los mapas
with col[1]:

  tab = st.tabs(["Viviendas con jefatura de hombres","Viviendas con jefatura de mujeres","Viviendas con jefatura compartida"])

  with tab[0]:
    mapa = tb1[(tb1['dominio']==dominio)&(tb1['new_jefe']==1)].copy()
    mapa.drop_duplicates(inplace=True)

    fig = hacer_mapa(mapa,'viv_ent_dom_jef',
                     {'nom_ent':'Entidad federativa','cve_ent':'Clave entidad','viv_ent_dom_jef':'Número de viviendas'},
                     'amp')
    st.plotly_chart(fig)
  with tab[1]:
    mapa = tb1[(tb1['dominio']==dominio)&(tb1['new_jefe']==2)].copy()
    mapa.drop_duplicates(inplace=True)

    fig = hacer_mapa(mapa,'viv_ent_dom_jef',
                     {'nom_ent':'Entidad federativa','cve_ent':'Clave entidad','viv_ent_dom_jef':'Número de viviendas'},
                     'blues')
    st.plotly_chart(fig)

  with tab[2]:
    mapa = tb1[(tb1['dominio']==dominio)&(tb1['new_jefe']==0)].copy()
    mapa.drop_duplicates(inplace=True)

    fig = hacer_mapa(mapa,'viv_ent_dom_jef',
                     {'nom_ent':'Entidad federativa','cve_ent':'Clave entidad','viv_ent_dom_jef':'Número de viviendas'},
                     'greens')
    st.plotly_chart(fig)


# Conclusiones clave
st.subheader(':red-background[Conclusiones clave]')

left, middle, right = st.columns(3)
if left.button("insight", icon=":material/looks_one:", use_container_width=True):
    left.markdown("Es importante distinguir los hogares donde la jefatura es compartida por hombres y mujeres, porque en ellos existe **algún grado de distribución de la autoridad y responsabilidad** de dicho hogar.")
if middle.button("insight", icon=":material/looks_two:", use_container_width=True):
    middle.markdown('La participación de los hogares con jefatura **masculina, desde el domino urbano pasando por el conurbado y siguiendo al rural, es mayor**. Por el contario, para aquellos con liderazgo femenino o compartido, esta proporción disminuye.')
if right.button("insight", icon=":material/looks_3:", use_container_width=True):
    right.markdown('En México, durante el año 2021, **por cada hogar encabezado por una mujer hay dos encabezados por el sexo opuesto**.')
