# -*- coding: utf-8 -*-
"""
Created on Sat Sep  1 17:17:33 2018

@author: Marcos
"""

from urllib.request import urlopen
from urllib.parse import urljoin
import bs4 as bs4
import time
from datetime import datetime
import pandas as pd
import os.path
import numpy as np


def DescargoDatosNorber(url, myid):

    # colnames = ['timefirst', 'timelast', 'dur', 'index', 'text', 'style', 'color', 'chofer', 'fecha', 'vuelo', 'hora', 'quien', 'plata', 'origen', 'destino']
    colnames = ['timefirst', 'timelast', 'dur', 'timetravel', 'index', 'text', 'style', 'color', 'chofer', 'fecha', 'vuelo', 'hora', 'quien', 'plata', 'origen', 'destino']
    csv_filename = 'out.csv'
    
    if os.path.isfile(csv_filename):
        #si existe, lo cargo
        dataold = pd.read_csv(csv_filename, encoding='cp1252')    
    else:
        #si no existe, creo el df vacio, y creo el archivo con los headers
        dataold = pd.DataFrame(columns=colnames)        
        
    l = len(dataold)
    print( "Había %d registros" % (l))

    print( "\tAbriendo url %s" % (url))
    f = urlopen(url)
    soup = bs4.BeautifulSoup(f, features="html.parser")
    tags = soup.findAll('span')
    
    
    # recs = soup.find_all("a", string="Recibo")
    # for rec in recs:
    #     recurl= urljoin(url, rec['href'])
    #     f2 = urlopen(recurl)
    #     recsoup = bs4.BeautifulSoup(f2, features="html.parser")
    #     a= recsoup.find_all('td')
    #     lista = [0, 1, 2, 4, 5, 6, 7, 8, 9, 10]
    #     print(a[-1].text)

    contnew = 0
    contmod = 0
    mytime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    for indt in range(len(tags)):
        texto = tags[indt].text

        loc = np.where(dataold['text'] ==texto)[0]
        if len(loc)==0: # si es nuevo
            tag  = tags[indt]
            temp = parsetext(tag, indt, mytime)
            temp.columns = colnames
            
            #agrego el nuevo dataframe
            dataold = dataold.append(temp)
            contnew+=1

        else: # si ya lo tenia, modifico timelast y dur            
            dataold.at[loc[0], 'timelast'] =  mytime

            secondslast = time.mktime(time.strptime(dataold.at[loc[0], 'timelast'],'%Y-%m-%d %H:%M:%S'))
            secondsfirst = time.mktime(time.strptime(dataold.at[loc[0], 'timefirst'],'%Y-%m-%d %H:%M:%S'))

            dur = round((secondslast - secondsfirst)/3600,2)
            
            dataold.at[loc[0], 'dur'] =  dur
            contmod+=1

    #Guardo el archivo completo
    dataold = dataold.sort_values(by=['timetravel', 'timelast'])
    SaveDataCSV(dataold, csv_filename, colnames)    

    print( "Encuentro %d registros, %d nuevos y %d modificados" % (len(tags), contnew, contmod)    )
    print( "Ahora hay %d registros" % (len(dataold))    )
    return dataold

def SaveDataCSV(data, csv_filename, colnames):
    df = pd.DataFrame(data, columns=colnames)
    # df.to_csv(csv_filename, sep=',', encoding='cp1252', index=False, mode='a', header=False)
    df.to_csv(csv_filename, sep=',', encoding='cp1252', index=False)

def parsetext(tag, indt, mytime):
    texto = tag.text
    temp = texto.split('//')

#         hay 4 formatos. los dos de id 01 a 08
#        NORBERTO SPIN // 03-11 // DI 7505 // 08:15 // MADDY MADELINE PICKUP (X1) // ARS 1150.00 // CIRCUS HOSTEL & HOTEL (CHACABUCO 1020) // EZE- Llamar · WhatsApp // Recibo
#        NORBERTO SPIN // 03-11 // 10:30 // OCTAVIA MARIA HUNOLD / YUKI TANAKA HUNOLD (X2) // ARS 0.00 // (TANGOL) HOTEL CONQUISTADOR (SUIPACHA 948) // AEP-TBC Llamar · WhatsApp // Recibo
#         y los dos de id 00
#        05-11 // AD 8770 // 02:50 // RUY BARROS RUY (X2) // ARS 1250.00 // ARC RECOLETA HOTEL (PEñA 2155) // EZE- Llamar · WhatsApp // Recibo
#        05-11 // 04:00 // DIANNE LAWSON (X1) // ARS 550.00 // ARC RECOLETA HOTEL (PEñA 2155) // AEP-S/N Llamar · WhatsApp // Recibo
#       la diferencia esta en que en unos hay numero de vuelo o no. y en otros hay nombre de chofer o no.
#        por ahora solo estoy manejando los dos que tienen chofer

    if len(temp) == 7:
        chofer = temp[0].strip()
        fecha = temp[1].strip()
        vuelo = ''
        hora = temp[2].strip()
        quien = temp[3].strip()
        plata = temp[4].strip()
        origen = temp[5].strip()
        destino = temp[6].strip()
    else:
        chofer = temp[0].strip()
        fecha = temp[1].strip()
        vuelo = temp[2].strip()
        hora = temp[3].strip()
        quien = temp[4].strip()
        plata = temp[5].strip()        
        destino = temp[6].strip()
        origen = temp[7].strip()

    timetravel = parsedatetime(fecha,hora)

#        if plata[0:3]=='ARS':
#            plata=float(plata[4:])

    style = tag["style"]
    d = {}
    for i in style.split(';'):
        if len(i) > 0:
            [key, val] = i.split(':')
            d[key] = val
    color = d['color']
    
    mytimefirst = mytime
    mytimelast = mytime
    dur = 0
    
    lista = [mytimefirst, mytimelast, dur, timetravel, indt, texto, style, color, chofer, fecha, vuelo, hora, quien, plata, origen, destino]
    
    #ya tengo todo listo, creo el nuevo dataframe
    temp = pd.DataFrame(lista).transpose()
    
    #agrego el nuevo dataframe
    return temp    

def parsedatetime(fecha,hora):
    listfecha = fecha.split('-')
    dia = int(listfecha[0])
    mes = int(listfecha[1])
    anio = datetime.today().year
    listhora = hora.split(':')
    hora = int(listhora[0])
    min = int(listhora[1])
    
    lista = (anio,mes,dia,hora,min,0,0,0,0)
    mytimestr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.mktime(lista)))
    return mytimestr

def add_column_timetravel(): 
    csv_filename = 'out.csv'    
    dataold = pd.read_csv(csv_filename, encoding='cp1252')    

    colnames = ['timefirst', 'timelast', 'dur', 'timetravel', 'index', 'text', 'style', 'color', 'chofer', 'fecha', 'vuelo', 'hora', 'quien', 'plata', 'origen', 'destino']
    datanew = pd.DataFrame(columns=colnames)
    for index,row in dataold.iterrows():
        timetravel = parsedatetime(row['fecha'],row['hora'])        
        lista = list(row[0:3]) + [timetravel] + list(row[3:])
        temp = pd.DataFrame(lista).transpose()
        temp.columns = colnames
        datanew = datanew.append(temp)
    
    csv_filename = 'out2.csv'
    SaveDataCSV(datanew, csv_filename, colnames)