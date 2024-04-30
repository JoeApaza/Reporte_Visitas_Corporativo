import logging
import os
import cx_Oracle #puedes usar oracledb
import pandas as pd
import polars as pl
from dotenv import load_dotenv
from src.database.db_oracle import close_connection_db,read_database_db,leer_sql,get_connection,Insert_dataframe_db,read_database_db
from src.routes.Rutas import ruta_Visitas_Corporativas,ruta_env,ruta_html,ruta_libro_Formato
from src.models.Fun_Excel import Macros,Eliminar_Excel,leer_html,enviar_correo
from datetime import datetime, timedelta
from openpyxl import load_workbook
# Obtén la fecha actual
fecha_actual = datetime.now()
fecha_ayer = fecha_actual - timedelta(days=1)
año = fecha_ayer.strftime('%Y')
mes = fecha_ayer.strftime('%m')
dia = fecha_ayer.strftime('%d')


logging.basicConfig(format="%(asctime)s::%(levelname)s::%(message)s",   
                    datefmt="%d-%m-%Y %H:%M:%S",    
                    level=10,   
                    filename='.//src//utils//log//app.log',filemode='a')


load_dotenv(ruta_env)

Conexion_Opercom=get_connection(os.getenv('USER_DB'),os.getenv('PASSWORD_DB'),os.getenv('DNS_DB'))

print('Crea un cursor')
destino_cursor = Conexion_Opercom.cursor()

Df_Visitas_Corporativas=pd.read_sql(leer_sql(ruta_Visitas_Corporativas), Conexion_Opercom)

Ruta_libro = "./src/models/Reporte Visitas Corportivas al "+dia+"."+mes+"."+año+".xlsx"  # Reemplaza con la ruta y nombre de tu archivo Excel
Df_Visitas_Corporativas.to_excel(Ruta_libro, index=False)


df_1 = Df_Visitas_Corporativas.pivot_table(index=['PERIODO'], columns='GESTOR', values='RUC_DNI', aggfunc='nunique').reset_index().fillna(0)
df_2 = Df_Visitas_Corporativas.pivot_table(index=['PERIODO'], columns='REGION', values='RUC_DNI', aggfunc='nunique').reset_index().fillna(0)
total_columna =  Df_Visitas_Corporativas.pivot_table(index=['PERIODO'], values='RUC_DNI', aggfunc='nunique').reset_index().fillna(0)

columnas_nuevas = ['REGION','PERIODO','LIMA','CENTRO','SUR','NORTE']
for col in columnas_nuevas:
    if col not in df_2.columns:
        df_2[col] = 0
df_2 = df_2[columnas_nuevas]


df_s = Df_Visitas_Corporativas.pivot_table(index=['PERIODO'], columns='SEGMENTO_CORP', values='RUC_DNI', aggfunc='nunique').reset_index().fillna(0)
columnas_nuevas = ['REGION','PERIODO','SEGMENTO1','SEGMENTO2']
for col in columnas_nuevas:
    if col not in df_s.columns:
        df_s[col] = 0
df_s = df_s[columnas_nuevas]

df_1_2 =pd.merge(df_s,pd.merge(df_1, df_2, on=['PERIODO'], how='outer'), on=['PERIODO'], how='outer')
df_1_2 =pd.merge(df_1_2, total_columna, on=['PERIODO'], how='outer')

columnas_enteros=['EMPRESA1','EMPRESA2','EMPRESA3','EMPRESA4','LIMA','CENTRO','SUR','NORTE','SEGMENTO1','SEGMENTO2','RUC_DNI']
df_1_2[columnas_enteros]=df_1_2[columnas_enteros].astype(int)
df_1_2=df_1_2.apply(lambda x: x.astype(str).str.capitalize())


Periodo_max=max(Df_Visitas_Corporativas['PERIODO'],key=int)
df_3_i=Df_Visitas_Corporativas[Df_Visitas_Corporativas['PERIODO']==Periodo_max]
df_3 = df_3_i.pivot_table(index=['NOMBRE_CARTERA'], columns='GESTOR', values='RUC_DNI', aggfunc='nunique').reset_index().fillna(0)
total_columna =  df_3_i.pivot_table(index=['NOMBRE_CARTERA'], values='RUC_DNI', aggfunc='nunique').reset_index().fillna(0)
columnas_nuevas = ['NOMBRE_CARTERA','EMPRESA1','EMPRESA2','EMPRESA3','EMPRESA4']
for col in columnas_nuevas:
    if col not in df_3.columns:
        df_3[col] = 0
df_3 = df_3[columnas_nuevas]

df_4=Df_Visitas_Corporativas[Df_Visitas_Corporativas['PERIODO']==Periodo_max]
df_4 = df_4.pivot_table(index=['NOMBRE_CARTERA'], columns='REGION', values='RUC_DNI', aggfunc='nunique').reset_index().fillna(0)
columnas_nuevas = ['NOMBRE_CARTERA','LIMA','CENTRO','SUR','NORTE']

for col in columnas_nuevas:
    if col not in df_4.columns:
        df_4[col] = 0

df_4 = df_4[columnas_nuevas]

df_s_4=Df_Visitas_Corporativas[Df_Visitas_Corporativas['PERIODO']==Periodo_max]
df_s_4 = df_s_4.pivot_table(index=['NOMBRE_CARTERA'], columns='SEGMENTO_CORP', values='RUC_DNI', aggfunc='nunique').reset_index().fillna(0)
columnas_nuevas = ['NOMBRE_CARTERA','SEGMENTO1','SEGMENTO2']
for col in columnas_nuevas:
    if col not in df_s_4.columns:
        df_s_4[col] = 0

df_s_4 = df_s_4[columnas_nuevas]

df_3_4 =pd.merge(df_s_4,pd.merge(df_3, df_4, on=['NOMBRE_CARTERA'], how='outer'), on=['NOMBRE_CARTERA'], how='outer')
df_3_4 =pd.merge(df_3_4, total_columna, on=['NOMBRE_CARTERA'], how='outer')

columnas_enteros=['SEGMENTO1','SEGMENTO2','EMPRESA1','EMPRESA2','EMPRESA3','EMPRESA4','LIMA','CENTRO','SUR','NORTE']
df_3_4[columnas_enteros]=df_3_4[columnas_enteros].astype(int)
df_3_4=df_3_4.apply(lambda x: x.astype(str).str.capitalize())


df_5 = Df_Visitas_Corporativas.pivot_table(index=['PERIODO','GESTOR'], columns='DIA', values='RUC_DNI', aggfunc='nunique').reset_index().fillna(0)
columnas_nuevas = ['PERIODO','DIA','GESTOR','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
for col in columnas_nuevas:
    if col not in df_5.columns:
        df_5[col] = 0
columnas_enteros=['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
df_5[columnas_enteros]=df_5[columnas_enteros].astype(int)
df_5 = df_5[columnas_nuevas]
df_5=df_5.apply(lambda x: x.astype(str).str.capitalize())


html=leer_html(ruta_html,df_1_2,df_3_4,df_5)
enviar_correo(html,Ruta_libro)
Eliminar_Excel(Ruta_libro)
destino_cursor.close
close_connection_db(Conexion_Opercom)
