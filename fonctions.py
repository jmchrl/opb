#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  fonctions.py

#  Copyright 2016 Jean-Michel <Jean-Michel@PC-JM>

#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.  

import math
import decimal

def evalQuantite(texte):
	# definition des variables mathematiques pour interpretation par eval
	pi = math.pi
	# calcul de la quantite
	try:
		s = texte.split("$")
		total = 0.0
		for ligne in s:
			if ligne == "":
				pass
			else:
				if ligne[0] == "#":
					pass
				else:
					st=eval(ligne)
					total = total + st
		totalArrondi = decimal.Decimal(str(total)).quantize(decimal.Decimal('0.001'), rounding = 'ROUND_HALF_UP')
		return totalArrondi
	except:
		return str(0.0)

def indent(elem, level=0):
    """Indentation du xml pour le module etree"""
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
