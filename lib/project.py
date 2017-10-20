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

import lib.constantes

def emplacementFichier(urlFichier):
	"""Retourne l'url de l'emplacement d'un fichier à partir de l'url du fichier"""
	emplacementFichier = os.path.dirname(urlFichier)
	return emplacementFichier

class Project():
	"""Classe contenant l'affaire"""
	
	def __init__(self, url= None):
		
		self.url = url
		
		if self.url == None:
			self.xml = ET.ElementTree(ET.fromstring(lib.constantes.XMLTEMPLATE))
		else :
			# nettoyage du dossier temp
			self.cleanDirTemp()
			# extraction de l'archive dans le dossier temp
			fichierZip = zipfile.ZipFile(self.url,"r")
			fichierZip.extractall("./temp")
			fichierZip.close()
			self.xml = ET.parse("./temp/data.xml")
			
		self.lots = []
		self.ouvrages = []
	
	def add_work(self, ouvrage):
		"""Creation d un dictionnaire pour chaque ouvrage et ajout a la liste des ouvrages"""
		self.ouvrages.append(ouvrage)
	
	def return_work(self, iid):
		"""Verifie si l index donne en argument correspond a un ouvrage. Retourne l ouvrage ou None si il n a pas ete trouve"""
		ouv = None
		for ouvrage in self.ouvrages:
			if ouvrage.iid == iid:
				ouv = ouvrage				
				break
		return ouv
	
	def cleanDirTemp(self):
		"""Clean tempory files in temp directory"""
		try:
			# deleting the xml file created into the temporary directory
			os.remove(os.getcwd() + "/temp/data.xml")
		except:
			pass
		try:
			# deleting the files located into the temporary directory
			shutil.rmtree(os.getcwd() + "/temp/ref")
		except:
			pass
		
	
	def saveZip(self):
		"""Create a backup file in zip format containing data.xml and ref directory"""
		try:
			fileZip = zipfile.ZipFile(self.url, mode='w')
			# creating the data.xml file into the working directory
			self.xml.write("data.xml", encoding="UTF-8", xml_declaration=True)
			# adding the file data.xml into the backup file in zip format
			fileZip.write("data.xml")
			# deleting the data.xml file created into the working directory
			os.remove("data.xml")
			try:
				# copying the ref folder located in temporary directory to the working directory
				shutil.copytree("./temp/ref","./ref")
				for file in os.listdir("ref"):
					# adding each file contained in the ref folder into the backup file in zip format
					fileZip.write("ref/" + file)
				shutil.rmtree(os.getcwd() + "/ref") # deleting the ref folder copied into the working directory
			except:
				pass
		finally :
			print("The backup file %s was succefully saved" %(self.url))
			fileZip.close() # closing backup file in zip format


class Work():
	"""Classe définissant un ouvrage"""
	
	def __init__(self, iid, name="_Ouvrage_", status="", unite="", quant="", prix="0.0", desc_id="", loc="", tva="", bt=""):
		
		self.iid = iid
		self.name = name
		self.status = status
		self.unite = unite
		self.quant = quant
		self.prix = prix
		self.desc_id = desc_id
		self.loc = loc
		self.tva = tva
		self.bt = bt
	
	def evalQuantiteOuvrage(self):
		"""Interpretation du resultat quantite issue de la chaine de caractere"""
		pass
