#!/usr/bin/python 

#from splinter import Browser
import numpy as np
import splinterfun

#br = splinterfun.InicializoBrowser()
#splinterfun.br = br #para que splinterfun vea el browser

myids = [8]#1+np.array(range(30))
for myid in myids:
    url = 'http://www.greetersba.com/aeropuerto12.php?id=%02d' % (myid)
    data = splinterfun.DescargoDatosNorber(url, myid)