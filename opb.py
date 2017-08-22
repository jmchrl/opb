#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  opb.py

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

import xml.etree.ElementTree as ET
import math
import decimal
import os
import zipfile
import constantes

def emplacementFichier(urlFichier):
	"""Retourne l'url de l'emplacement d'un fichier à partir de l'url du fichier"""
	emplacementFichier = os.path.dirname(urlFichier)
	return emplacementFichier

class Affaire():
	"""Classe contenant l'affaire"""
	
	def __init__(self, url= None):
		
		self.url = url
		
		if self.url == None:
			self.xml = ET.ElementTree(ET.fromstring(constantes.XMLTEMPLATE))
		else :
			#self.xml = ET.parse(self.url)
			fichierZip = zipfile.ZipFile(self.url,"r")
			#contenuXML = fichierZip.open("data.xml","r")
			contenuXML = fichierZip.read("data.xml")
			self.xml = ET.ElementTree(ET.fromstring(contenuXML))
			fichierZip.close()
			
		
		self.lots = []
		self.ouvrages = []
	
	def ajouterOuvrage(self, ouvrage):
		"""Creation d un dictionnaire pour chaque ouvrage et ajout a la liste des ouvrages"""
		self.ouvrages.append(ouvrage)
	
	def retourneOuvrage(self, iid):
		"""Verifie si l index donne en argument correspond a un ouvrage. Retourne l ouvrage ou None si il n a pas ete trouve"""
		ouv = None
		for ouvrage in self.ouvrages:
			if ouvrage.iid == iid:
				ouv = ouvrage				
				break
		return ouv
	
	def zipSauvegarde(self):
		"""Création d'un fichier de sauvegarde au format zip et enregistrement du fichier data.xml"""
		try:
			fichierZip = zipfile.ZipFile(self.url, mode='w') # création de l'archive zip !!!!! A revoir car cela écrase l'archive existante si elle existe
			self.xml.write("data.xml", encoding="UTF-8", xml_declaration=True) # création du fichier data.xml dans le répertoire de main.py
			fichierZip.write("data.xml") # ajout du fichier créé à l'archive zip
			fichierZip.close() # fermeture de l'archive zip
			os.remove("data.xml") # suppression du fichier xml temporaire
			print("Enregistrement réalisé avec succès")
		except:
			print("Erreur lors de la création du fichier zip")
		
		

class Ouvrage():
	"""Classe définissant un ouvrage"""
	
	def __init__(self, iid, ref="", unite="", quant="", prix="0.0", desclien="", loclien="", bt=""):
		
		self.iid = iid
		self.ref = ref
		self.unite = unite
		self.quant = quant
		self.prix = prix
		self.desclien = desclien
		self.loclien = loclien
		self.bt = bt
	
	def evalQuantiteOuvrage(self):
		"""Interpretation du resultat quantite issue de la chaine de caractere"""
		pass
