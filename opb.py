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
import shutil
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
			# extraction de l'archive dans le dossier temp
			fichierZip = zipfile.ZipFile(self.url,"r")
			fichierZip.extractall("./temp")
			fichierZip.close()
			self.xml = ET.parse("./temp/data.xml")
			
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
	
	def sauvegardeZip(self):
		"""Création d'un fichier de sauvegarde au format zip et enregistrement du fichier data.xml"""
		
		try:
			fichierZip = zipfile.ZipFile(self.url, mode='w')
			self.xml.write("data.xml", encoding="UTF-8", xml_declaration=True) # création du fichier data.xml dans le répertoire de main.py
			fichierZip.write("data.xml") # ajout du fichier créé à l'archive zip
			os.remove("data.xml") # suppression du fichier xml créé dans le répertoire de travail
			os.remove(os.getcwd() + "/temp/data.xml") # suppression du fichier xml créé dans le répertoire temp
			
			try:
				# copie du dossier ref situé dans temp vers le répertoire de travail
				shutil.copytree("./temp/ref","./ref")
				
				for fichier in os.listdir("ref"):
					fichierZip.write("ref/" + fichier) # ajout de chaque fichier contenu dans ref à l'archive
				
				shutil.rmtree(os.getcwd() + "/ref") # suppression du dossier ref copié dans le répertoire de travail
				shutil.rmtree(os.getcwd() + "/temp/ref") # Suppression des fichiers situés dans le dossier temp
			
			except:
				pass
				
		finally :
			print("Enregistrement réalisé avec succès")
			fichierZip.close() # fermeture de l'archive zip


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
