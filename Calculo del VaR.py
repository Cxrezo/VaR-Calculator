import pandas as pd
import numpy as np
import yfinance as yf
import time
import tkinter as tk
from tkinter import filedialog
import warnings

warnings.filterwarnings("ignore")


def carga_datos(ruta):
    data = pd.read_csv(str(ruta),index_col=0)
    return data

def calculo_var(data,portafolio):
    #Calculo de los escenarios
    Escenarios = pd.DataFrame(columns=data.columns)
    for i in range(0,data.shape[1]): #columnas
        esc = []
        for j in range(0,data.shape[0]-1): #filas
            x = data.iloc[j+1,i]/data.iloc[j,i]*data.iloc[-1,i]
            esc.append(x)
        Escenarios[data.columns[i]] = esc

    #Calculo de las gannacias/perdidas
    valores = []
    for i in range(0,Escenarios.shape[0]): #filas
        v = 0
        for j in range(0,Escenarios.shape[1]): #columnas
            x = Escenarios.iloc[i,j]/data.iloc[-1,j]*portafolio[j]
            v = v + x
        valores.append(v)
    valor_port_ini = np.sum(portafolio)
    gp = []
    for i in range(0,len(valores)):
        gp.append(- valor_port_ini + valores[i])
    ganper = pd.DataFrame({"Ganancias/Perdidas" : gp})

    #Ordenamos las g/p
    ganper = ganper.sort_values(by="Ganancias/Perdidas", ascending=True)

    VAR = ganper.iloc[4,0] * -1
    VAR10 = VAR * np.sqrt(10) 
    CVAR = ganper["Ganancias/Perdidas"].head(5).mean() * -1
    CVAR10 = CVAR * np.sqrt(10)
    Merc = 3 * VAR
    Merc10 = 3 * VAR10

    # Impresión de resultados
    print("\n")
    print("\n")
    print("------------------------------------------------------------------------------------------")
    print(f"VaR a 1 día: {VAR:.4f} | VaR a 10 dias: {VAR:.4f}")  
    print("------------------------------------------------------------------------------------------")
    print(f"C-VaR a 1 día: {CVAR:.4f} | C-VaR a 10 dias: {CVAR10:.4f}")
    print("------------------------------------------------------------------------------------------")
    print(f"Capital de mercado a 1 día: {Merc:.4f} | Capital de mercado a 10 dias: {Merc10:.4f}")
    print("------------------------------------------------------------------------------------------")



def descarga():
    print("Usted va a descargar los datos de Yahoo Finance")
    print("Por favor, ingrese los tickers de los activos que desea descargar siguiendo el ejemplo ----> AAPL,MSFT,GOOGL")
    tickers = input("Ingrese los tickers de los activos que desea descargar (Utilice datos que coticen en la misma moneda): ")
    print("Ingrese la fecha de inicio y fin de los datos que desea descargar")
    print("Formato: 'YYYY-MM-DD'")
    inicio = input("Fecha de inicio: ")
    fin = input("Fecha de fin: ")
    tickers = tickers.split(",")

    print("\n")
    datos = yf.download(tickers, start=inicio, end=fin)["Close"]

    datos_nan = []
    print("Verificando datos descargados")
    print("\n")
    for i in range(0,datos.shape[1]):
        nan = False
        nan = datos[datos.columns[i]].isnull().any()
        if nan == True:
            datos_nan.append(datos.columns[i])
    datos = datos.drop(columns = datos_nan)
    if datos.shape[1] <= 0:
        print("No se pudo descargar ningun dato, porfavor verifique los tickers y fechas e intente nuevamente o ingreselos mediante un archivo csv")
        exit()
    if len(datos_nan) > 0:
        print(f"Los datos de los siguientes activos no se pudieron descargar: {datos_nan}.")
        print("Se eliminaron del calculo")
        print("Si desea descargar estos datos, porfavor verifique el ticker y vuelva a intentarlo o ingrese los datos mediante un archivo csv")
        time.sleep(3)
    else:
        print("Datos descargados correctamente")
        print(datos)
    return datos


def carga():
    print("Usted va a cargar los datos desde un archivo csv")
    root = tk.Tk()
    root.withdraw()
    ruta = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")]) 
    if not ruta:
        print("No se seleccionó ningún archivo")
        exit()
    datos = carga_datos(ruta)
    datos_nofloat = []
    no_es_float = False
    for i in range(0,datos.shape[1]):
        if datos.dtypes[i] != "float64":
            datos_nofloat.append(datos.columns[i])
            no_es_float = True
        if no_es_float == True:
            print(f"Los datos de los siguientes activos no son numericos o tiene datos faltantes: {datos_nofloat}.")
            print("Porfavor verifique los datos y vuelva a intentarlo")
            exit()
    return datos

def main():
    print("Calculo del VaR, C-VaR y Capital de mercado")
    print("Seleccione una opción")
    print("1. Descargar datos de Yahoo Finance")
    print("2. Cargar datos desde un archivo csv")
    opcion = input("Ingrese la opción: ")
    if opcion == "1":
        datos = descarga()
    elif opcion == "2":
        datos = carga()
    else:
        print("Opción no válida")
        exit()
    print("\n")
    print("Se utilizaran los datos de los siguientes activos")
    print(datos.columns)
    print("\n")
    print("Ingrese el portafolio que desea analizar")
    print("Por favor, ingrese los pesos de los activos siguiendo el ejemplo ----> 2000,4000,9000")
    portafolio = input("Ingrese los pesos: ")
    portafolio = portafolio.split(",")
    try:
        portafolio = [float(i) for i in portafolio]
    except:
        print("Verifique los datos del portafolio e intente nuevamente")
        exit()
    if len(portafolio) != datos.shape[1]:
        print("El número de pesos no coincide con el número de activos")
        exit()
    calculo_var(datos,portafolio)


# Ejecución del programa   
main()