#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  main.py

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

import tkinter
import tkinter.ttk
import tkinter.filedialog
import tkinter.messagebox
import xml.etree.ElementTree as ET
import os
import opb
import fonctions
import constantes

class Main():
	"""Fenetre principale creee lorsque le programme est lance"""

	def __init__(self):
		
		self.root = tkinter.Tk()
		self.root.title("opb - sans nom")
				
		#pour rendre la fenetre etirable
		self.root.geometry("1500x900+20+20")
		self.root.rowconfigure(2, weight=1)
		self.root.columnconfigure(0, weight=1)
		
		#par défaut création d'une nouvelle affaire
		self.affaire = opb.Affaire(None)
		self.affaire.xml.getroot()
		self.root.title("opb - sans nom")
		
		################
		#ajout du menu #
		################
		
		menu = tkinter.Frame(self.root, borderwidth =2)
		menu.grid(row=0, column=0, sticky="WE", padx=5, pady=5)
		
		################
		# menu fichier #
		################
		
		menu_fichier = tkinter.Menubutton(menu, text="Fichier")
		menu_fichier.pack(side="left")
		
		# partie deroulante
		deroul_menu_fichier = tkinter.Menu(menu_fichier)
				
		# integration du menu
		menu_fichier.configure(menu = deroul_menu_fichier)
		
		# ajout des commandes
		deroul_menu_fichier.add_command(label="Nouveau", underline=0, command = self.nouvelleAffaire)
		deroul_menu_fichier.add_command(label="Ouvrir", underline=0, command = self.ouvrirAffaire)
		deroul_menu_fichier.add_command(label="Enregister", underline=0, command = self.enregistrerAffaire)
		deroul_menu_fichier.add_command(label="Enregister Sous", underline=0, command = self.enregisterAffaireSous)
		
		################
		# menu edition #
		################
		
		menu_edition = tkinter.Menubutton(menu, text="Edition")
		menu_edition.pack(side="left")
		
		# partie deroulante
		deroul_menu_edition = tkinter.Menu(menu_edition)
				
		# integration du menu
		menu_edition.configure(menu = deroul_menu_edition)
		
		# ajout des commandes
		deroul_menu_edition.add_command(label="Annuler", underline=0, command = self.annuler)
		deroul_menu_edition.add_command(label="Rétablir", underline=0, command = self.retablir)
		
		################
		# menu canevas #
		################
		
		menu_canevas = tkinter.Menubutton(menu, text="Canevas")
		menu_canevas.pack(side="left")
		
		# partie deroulante
		deroul_menu_canevas = tkinter.Menu(menu_canevas)
				
		# integration du menu
		menu_canevas.configure(menu = deroul_menu_canevas)
		
		# ajout des commandes
		deroul_menu_canevas.add_command(label="Ajouter un titre", underline=0, command = self.ajouterTitre)
		deroul_menu_canevas.add_command(label="Ajouter un ouvrage", underline=0, command = self.ajouterOuvrage)
		deroul_menu_canevas.add_command(label="Supprimer un item", underline=0, command = self.supprimerItem)
		deroul_menu_canevas.add_command(label="Détail de l'ouvrage", underline=0, command = self.infos)
		
		##################
		# barre d outils #
		##################
		
		# ajout d un cadre conteneur des boutons
		
		cadreOutils = tkinter.Frame(self.root)
		cadreOutils.grid(row=1, column=0, sticky='WN', padx=5, pady=5)
		
		# ajout des boutons
		
		self.imagePng_fleche_bas = tkinter.PhotoImage(file = "./img/fleche_bas_24x24.png")
		bouton_fleche_bas = tkinter.Button(cadreOutils, image = self.imagePng_fleche_bas, height=25, width=25, relief='flat', command = self.descendreItem)
		bouton_fleche_bas.pack(side='left')
		
		self.imagePng_fleche_haut = tkinter.PhotoImage(file = "./img/fleche_haut_24x24.png")
		bouton_fleche_haut = tkinter.Button(cadreOutils, image = self.imagePng_fleche_haut, height=25, width=25, relief='flat', command = self.monterItem)
		bouton_fleche_haut.pack(side='left')
		
		self.imagePng_fleche_droite = tkinter.PhotoImage(file = "./img/fleche_droite_24x24.png")
		bouton_fleche_droite = tkinter.Button(cadreOutils, image = self.imagePng_fleche_droite, height=25, width=25, relief='flat', command = self.indenterItem)
		bouton_fleche_droite.pack(side='left')
		
		self.imagePng_fleche_gauche = tkinter.PhotoImage(file = "./img/fleche_gauche_24x24.png")
		bouton_fleche_gauche = tkinter.Button(cadreOutils, image = self.imagePng_fleche_gauche, height=25, width=25, relief='flat', command = self.desindenterItem)
		bouton_fleche_gauche.pack(side='left')
		
		self.imagePng_infos = tkinter.PhotoImage(file = "./img/infos_24x24.png")
		bouton_infos = tkinter.Button(cadreOutils, image = self.imagePng_infos, height=25, width=25, relief='flat', command = self.infos)
		bouton_infos.pack(side='left')
		
		####################
		# treeview affaire #
		####################
		
		#ajout d'un cadre conteneur du treeview
		#self.cadreTreeview = tkinter.Frame(self.root, height=700, width=1200)
		self.cadreTreeview = tkinter.Frame(self.root)
		self.cadreTreeview.grid(row=2, column=0, sticky='WENS', padx=5, pady=5)
		#self.cadreTreeview.grid_propagate(0)
		self.cadreTreeview.rowconfigure(0, weight=1)
		self.cadreTreeview.columnconfigure(0, weight=1)
		
		#ajout de l'arbre de l'affaire
		self.arbreAffaire = ArbreAffaire(self.cadreTreeview)
		#pour rendre le treeview etirable sur l'ensemble de la fenêtre
		self.arbreAffaire.grid(row=0, column=0, sticky='WENS')
		
		self.arbreAffaire.bind("<Double-Button-1>", self.widgetPourModification)
		self.arbreAffaire.bind("<Control-KeyPress-KP_8>", self.monterItemEvent)
		self.arbreAffaire.bind("<Control-KeyPress-KP_2>", self.descendreItemEvent)
		self.arbreAffaire.bind("<Control-KeyPress-KP_6>", self.indenterItemEvent)
		self.arbreAffaire.bind("<Control-KeyPress-KP_4>", self.desindenterItemEvent)
		
		#################
		# treeview base #
		#################
		
		#ajout de l'arbre de l'affaire
		self.arbreBase = ArbreBase(self.cadreTreeview)
		#pour rendre le treeview etirable sur l'ensemble de la fenêtre
		self.arbreBase.grid(row=0, column=1, sticky='WENS')
		
		self.arbreAffaire.bind("<Double-Button-1>", self.widgetPourModification)
		self.arbreAffaire.bind("<Control-KeyPress-KP_8>", self.monterItemEvent)
		self.arbreAffaire.bind("<Control-KeyPress-KP_2>", self.descendreItemEvent)
		self.arbreAffaire.bind("<Control-KeyPress-KP_6>", self.indenterItemEvent)
		self.arbreAffaire.bind("<Control-KeyPress-KP_4>", self.desindenterItemEvent)
		
		###################
		# barre de status #
		###################
		
		# ajout d un cadre conteneur des notifications de status
		
		cadreStatus = tkinter.Frame(self.root)
		cadreStatus.grid(row=3, column=0, sticky='WN', padx=5, pady=5)
		
		texteStatus = tkinter.Label(cadreStatus, text="Status")
		texteStatus.grid(row=0, column=0, sticky='WENS')
	
	def nouvelleAffaire(self):
		"""Lancement de la methode nouvelleAffaire de la classe ArbreAffaire"""
		self.affaire = opb.Affaire(None)
		self.affaire.xml.getroot()
		self.arbreAffaire.remiseZeroTreeview()
		self.root.title("opb - sans nom")
	
	def ouvrirAffaire(self):
		"""Lancement de la methode ouvrirAffaire de la classe ArbreAffaire"""
		url = tkinter.filedialog.askopenfilename(filetypes=[('Fichier xml','*.xml')], title="Fichier de sauvegarde ...")
		self.arbreAffaire.remiseZeroTreeview()
		#self.arbreAffaire.ouvrirAffaire(url)
		self.root.title("opb - %s" %(url))
		
		# Creation d une nouvelle instance affaire du module opb
		self.affaire = opb.Affaire(url)
		racine = self.affaire.xml.getroot()
		
		# Creation d une liste d items (verifier l utilite)
		self.arbreAffaire.items = []
		
		# Parcours du fichier xml pour representation dans le treeview
		for lot in racine.findall("lot"):
			name = lot.get('name')
			n1 = self.arbreAffaire.insert("","end", text= name)
			self.arbreAffaire.items.append(n1)
			
			for t2 in lot.findall('element'):
				if t2.get('id') == "chapitre":
					name = t2.get('name')
					n2 = self.arbreAffaire.insert(n1,"end", text= name)
					self.arbreAffaire.items.append(n2)
				if t2.get('id') == "ouvrage":
					name = t2.get('name')
					ref = t2.get('ref')
					unite = t2.get('unite')
					try:
						quant = float(fonctions.evalQuantite(t2.get('quant')))
					except:
						quant = 0.0
					try:
						prix = float(t2.get('prix'))
					except:
						prix = 0.0
					desclien = t2.get('desclien')
					loclien = t2.get('loclien')
					bt = t2.get('bt')
					n2 = self.arbreAffaire.insert(n1,"end", text= name, values=(ref, unite, quant, prix, quant*prix))
					self.arbreAffaire.items.append(n2)
					ouvrage = opb.Ouvrage(n2, ref, unite, t2.get('quant'), prix, desclien, loclien, bt)
					self.affaire.ajouterOuvrage(ouvrage)
					
				
				for t3 in t2.findall('element'):
					if t3.get('id') == "chapitre":
						name = t3.get('name')
						n3 = self.arbreAffaire.insert(n2,"end", text= name)
						self.arbreAffaire.items.append(n3)
					if t3.get('id') == "ouvrage":
						name = t3.get('name')
						ref = t3.get('ref')
						unite = t3.get('unite')
						try:
							quant = float(fonctions.evalQuantite(t3.get('quant')))
						except:
							quant = 0.0
						try:
							prix = float(t3.get('prix'))
						except:
							prix = 0.0
						desclien = t3.get('desclien')
						loclien = t3.get('loclien')
						bt = t3.get('bt')
						n3 = self.arbreAffaire.insert(n2,"end", text= name, values=(ref, unite, quant, prix, quant*prix))
						self.arbreAffaire.items.append(n3)
						ouvrage = opb.Ouvrage(n3, ref, unite, t3.get('quant'), prix, desclien, loclien, bt)
						self.affaire.ajouterOuvrage(ouvrage)
				
					for t4 in t3.findall('element'):
						if t4.get('id') == "chapitre":
							name = t4.get('name')
							n4 = self.arbreAffaire.insert(n3,"end", text= name)
							self.arbreAffaire.items.append(n4)
						if t4.get('id') == "ouvrage":
							name = t4.get('name')
							ref = t4.get('ref')
							unite = t4.get('unite')
							try:
								quant = float(fonctions.evalQuantite(t4.get('quant')))
							except:
								quant = 0.0
							try:
								prix = float(t4.get('prix'))
							except:
								prix = 0.0
							desclien = t4.get('desclien')
							loclien = t4.get('loclien')
							bt = t4.get('bt')
							n4 = self.arbreAffaire.insert(n3,"end", text= name, values=(ref, unite, quant, prix, quant*prix))
							self.arbreAffaire.items.append(n4)
							ouvrage = opb.Ouvrage(n4, ref, unite, t4.get('quant'), prix, desclien, loclien, bt)
							self.affaire.ajouterOuvrage(ouvrage)
						
						for t5 in t4.findall('element'):
							if t5.get('id') == "chapitre":
								name = t4.get('name')
								n5 = self.arbreAffaire.insert(n4,"end", text= name)
								self.arbreAffaire.items.append(n5)
							if t5.get('id') == "ouvrage":
								name = t5.get('name')
								ref = t5.get('ref')
								unite = t5.get('unite')
								try:
									quant = float(fonctions.evalQuantite(t5.get('quant')))
								except:
									quant = 0.0
								try:
									prix = float(t5.get('prix'))
								except:
									prix = 0.0
								desclien = t5.get('desclien')
								loclien = t5.get('loclien')
								bt = t5.get('bt')
								n5 = self.arbreAffaire.insert(n4,"end", text= name, values=(ref, unite, quant, prix, quant*prix))
								self.arbreAffaire.items.append(n5)
								ouvrage = opb.Ouvrage(n5, ref, unite, t5.get('quant'), prix, desclien, loclien, bt)
								self.affaire.ajouterOuvrage(ouvrage)
	
	def enregistrerAffaire(self):
		"""Lancement de la methode miseAjourXML de la classe ArbreAffaire"""
		if self.affaire.url == None:
			url = tkinter.filedialog.asksaveasfilename(filetypes=[('Fichier xml','*.xml')], title="Fichier de sauvegarde ...")
		else:
			url = self.affaire.url
				
		xml = ET.ElementTree(ET.fromstring(constantes.XMLTEMPLATE))
		root = xml.getroot()
		
		lots = self.arbreAffaire.get_children()
		
		for i in lots :
			lot = ET.SubElement(root, "lot", name=self.arbreAffaire.item(i)['text'])
			t1 = self.arbreAffaire.get_children(i)
			test = False
			for j in t1 :
				for ouv in self.affaire.ouvrages:
					if ouv.iid == j:
						test = True
						n2 = ET.SubElement(lot, "element", id = "ouvrage", name=self.arbreAffaire.item(j)['text'], ref=ouv.ref, unite=ouv.unite, prix=str(ouv.prix), desclien=ouv.desclien, loclien=ouv.loclien, bt=ouv.bt, quant=ouv.quant)
				if test == True :
					test = False
				else :
					n2 = ET.SubElement(lot, "element", id = "chapitre", name=self.arbreAffaire.item(j)['text'])
				t2 = self.arbreAffaire.get_children(j)
				for k in t2 :
					for ouv in self.affaire.ouvrages:
						if ouv.iid == k:
							test = True
							n3 = ET.SubElement(n2, "element", id = "ouvrage", name=self.arbreAffaire.item(k)['text'], ref=ouv.ref, unite=ouv.unite, prix=str(ouv.prix), desclien=ouv.desclien, loclien=ouv.loclien, bt=ouv.bt, quant=ouv.quant)
					if test == True :
						test = False
					else :
						n3 = ET.SubElement(n2, "element", id = "chapitre", name=self.arbreAffaire.item(k)['text'])
					t3 = self.arbreAffaire.get_children(k)
					for l in t3 :
						for ouv in self.affaire.ouvrages:
							if ouv.iid == l:
								test = True
								n4 = ET.SubElement(n3, "element", id = "ouvrage", name=self.arbreAffaire.item(l)['text'], ref=ouv.ref, unite=ouv.unite, prix=str(ouv.prix), desclien=ouv.desclien, loclien=ouv.loclien, bt=ouv.bt, quant=ouv.quant)
						if test == True:
							test = False
						else :
							n4 = ET.SubElement(n3, "element", id = "chapitre", name=self.arbreAffaire.item(l)['text'])
						t4 = self.arbreAffaire.get_children(l)
						for m in t4 :
							for ouv in self.affaire.ouvrages:
								if ouv.iid == m:
									n5 = ET.SubElement(n4, "element", id = "ouvrage", name=self.arbreAffaire.item(m)['text'], ref=ouv.ref, unite=ouv.unite, prix=str(ouv.prix), desclien=ouv.desclien, loclien=ouv.loclien, bt=ouv.bt, quant=ouv.quant)
		
		fonctions.indent(root)
		xml.write(url, encoding="UTF-8", xml_declaration=True)
		self.root.title("opb - %s" %(url))
	
	def enregisterAffaireSous(self):
		"""Lancement de la methode miseAjourXML de la classe ArbreAffaire"""
		self.affaire.url = None
		self.enregistrerAffaire()
		
	def ajouterTitre(self):
		"""Ajoute un nouveau titre sous l item qui a le focus"""
		select = self.arbreAffaire.focus()
		parent = self.arbreAffaire.parent(select)
		position = self.arbreAffaire.index(select)+1
		item = self.arbreAffaire.insert(parent, position, text= "_Titre_")
		self.arbreAffaire.items.append(item)
		
	def ajouterOuvrage(self):
		"""Ajoute un nouvel ouvrage sous l item qui a le focus"""
		select = self.arbreAffaire.focus()
		parent = self.arbreAffaire.parent(select)
		position = self.arbreAffaire.index(select)+1
		item = self.arbreAffaire.insert(parent, position, text= "_Ouvrage_", values=("", "", 0.0, 0.0, ""))
		self.arbreAffaire.items.append(item)
		ouvrage = opb.Ouvrage(item)
		self.affaire.ajouterOuvrage(ouvrage)
	
	def descendreItem(self):
		"""Descendre l item qui a le focus lors de l action du bouton dans la barre d outils"""
		select = self.arbreAffaire.focus()
		parent = self.arbreAffaire.parent(select)
		position = self.arbreAffaire.index(select)
		self.arbreAffaire.move(select, parent, position+1)
	
	def descendreItemEvent(self, event):
		"""Descendre l item qui a le focus lors de l evennement ctrl+2"""
		self.descendreItem()
	
	def monterItem(self):
		"""Monter l item qui a le focus lors de l action du bouton dans la barre d outils"""
		select = self.arbreAffaire.focus()
		parent = self.arbreAffaire.parent(select)
		position = self.arbreAffaire.index(select)
		self.arbreAffaire.move(select, parent, position-1)
	
	def monterItemEvent(self, event):
		"""Monter l item qui a le focus lors de l evennement ctrl+8"""
		self.monterItem()
	
	def indenterItem(self):
		"""Indenter l item qui a le focus lors de l action du bouton dans la barre d outils"""
		select = self.arbreAffaire.focus()
		# si l'item est un ouvrage, indentation maxi = 5
		if self.affaire.retourneOuvrage(select) == None:
			if len(self.arbreAffaire.parentsItem()) < 4:
				precedent = self.arbreAffaire.prev(select)
				enfants_precedents = self.arbreAffaire.get_children(precedent)
				self.arbreAffaire.move(select, precedent, len(enfants_precedents))
		# sinon c'est un chapitre, donc indentation maxi = 4
		else :
			if len(self.arbreAffaire.parentsItem()) < 3:
				precedent = self.arbreAffaire.prev(select)
				enfants_precedents = self.arbreAffaire.get_children(precedent)
				self.arbreAffaire.move(select, precedent, len(enfants_precedents))
	
	def indenterItemEvent(self, event):
		"""Indenter l item qui a le focus lors de l evennement ctrl+6"""
		self.indenterItem()
	
	def desindenterItem(self):
		"""Desindenter l item qui a le focus lors de l action du bouton dans la barre d outils"""
		select = self.arbreAffaire.focus()
		parent = self.arbreAffaire.parent(select)
		grand_parent = self.arbreAffaire.parent(parent)
		position = self.arbreAffaire.index(parent)
		self.arbreAffaire.move(select, grand_parent, position+1)
		
	def desindenterItemEvent(self, event):
		"""Desindenter l item qui a le focus lors de l evennement ctrl+4"""
		self.desindenterItem()
	
	def supprimerItem(self):
		"""Supprime l item qui a le focus"""
		select = self.arbreAffaire.focus()
		self.arbreAffaire.delete(select)
		self.arbreAffaire.items.remove(select)

	def annuler(self):
		pass
		# TO DO
		
	def retablir(self):
		pass
		# TO DO
	
	def infos(self):
		select = self.arbreAffaire.focus()
		ouvrage = self.affaire.retourneOuvrage(select)
		if ouvrage == None :
			pass
		else :
			dialog = DialogInfos(self.arbreAffaire, select, self.affaire, ouvrage)
	
	def widgetPourModification(self, event):
		"""Positionnement d un entry sur le treeview pour modifier une valeur ou creation d un dialogue pour modifier la colonne quantite"""
		if self.arbreAffaire.winfo_children() == []:
			pass
		else : # suppression des widgets enfant pour qu un seul soit actif
			for widget in self.arbreAffaire.winfo_children():
				widget.destroy()
		select = self.arbreAffaire.focus()
		item = self.arbreAffaire.item(select)
		colonne = self.arbreAffaire.identify_column(event.x)
		position = self.arbreAffaire.bbox(select, column=colonne)
		ouvrage = self.affaire.retourneOuvrage(select)
		if colonne == "#0":
			texte = item["text"]
			entry = EntryTreeview(self.arbreAffaire, position, texte, colonne, select, ouvrage)
			self.arbreAffaire.enfants.append(entry)
		else:
			if colonne == "#1":
				texte = item["values"][0]
				entry = EntryTreeview(self.arbreAffaire, position, texte, colonne, select, ouvrage)
				self.arbreAffaire.enfants.append(entry)
			if colonne == "#2":
				texte = item["values"][1]
				entry = EntryTreeview(self.arbreAffaire, position, texte, colonne, select, ouvrage)
				self.arbreAffaire.enfants.append(entry)
			if colonne == "#3":
				texte = item["values"][2]
				entry = EntryTreeview(self.arbreAffaire, position, texte, colonne, select, ouvrage)
				self.arbreAffaire.enfants.append(entry)
			if colonne == "#4":
				texte = item["values"][3]
				entry = EntryTreeview(self.arbreAffaire, position, texte, colonne, select, ouvrage)
				self.arbreAffaire.enfants.append(entry)

class ArbreAffaire(tkinter.ttk.Treeview):
	"""Treeview de l affaire et methodes associees"""

	def __init__(self, parentGUI):
	
		tkinter.ttk.Treeview.__init__(self, parentGUI)
		
		self.enfants = []
		self.items = []
		
		self["columns"]=("ref","U" , "Q", "PU", "PT")
		self.column("#1", width=150, stretch=False)
		self.column("#2", width=100, stretch=False)
		self.column("#3", width=100, stretch=False)
		self.column("#4", width=100, stretch=False)
		self.column("#5", width=100, stretch=False)
		
		self.heading("#1", text="ref")
		self.heading("#2", text="U")
		self.heading("#3", text="Q")
		self.heading("#4", text="PU")
		self.heading("#5", text="PT")
	
	def remiseZeroTreeview(self):
		"""Remise a zero du treeview avant de charger une nouvelle affaire"""
		
		if self.items is not []:
			for item in self.items:
				try:
					self.delete(item)
				except:
					pass
	
	def parentsItem(self):
		"""Retourne la liste des parents d un item selectionne"""
		select = self.focus()
		liste = self.get_children() # creation de la liste des enfants de root
		# creation d un arbre des parents
		arbre_parent = []
		test = False
		# on verifie si le focus est un enfant de root
		for enfant in liste:
			if enfant == select :
				test = True
		while test == False:
			parent = self.parent(select)
			# on verifie si le parent est un enfant de root
			for enfant in liste:
				if enfant == parent:
					test = True
			select = parent
			arbre_parent.append(parent)
		return arbre_parent

class ArbreBase(tkinter.ttk.Treeview):
	"""Treeview de l affaire et methodes associees"""

	def __init__(self, parentGUI):
	
		tkinter.ttk.Treeview.__init__(self, parentGUI)
		
		self.enfants = []
		self.items = []
		
		self["columns"]=("ref","U", "PU")
		self.column("#1", width=150, stretch=False)
		self.column("#2", width=100, stretch=False)
		self.column("#3", width=100, stretch=False)
		
		self.heading("#1", text="ref")
		self.heading("#2", text="U")
		self.heading("#3", text="PU")
	
	def remiseZeroTreeview(self):
		"""Remise a zero du treeview avant de charger une nouvelle affaire"""
		
		if self.items is not []:
			for item in self.items:
				try:
					self.delete(item)
				except:
					pass
	
	def parentsItem(self):
		"""Retourne la liste des parents d un item selectionne"""
		select = self.focus()
		liste = self.get_children() # creation de la liste des enfants de root
		# creation d un arbre des parents
		arbre_parent = []
		test = False
		# on verifie si le focus est un enfant de root
		for enfant in liste:
			if enfant == select :
				test = True
		while test == False:
			parent = self.parent(select)
			# on verifie si le parent est un enfant de root
			for enfant in liste:
				if enfant == parent:
					test = True
			select = parent
			arbre_parent.append(parent)
		return arbre_parent

class EntryTreeview(tkinter.Entry):
	
	def __init__(self, parent, position, texte, colonne, select, ouvrage):
		
		self.parent = parent
		self.colonne = colonne
		self.select = select
		self.texteVar = tkinter.StringVar()
		self.texteVar.set(texte)
		self.ouvrage = ouvrage
		
		tkinter.Entry.__init__(self, self.parent, textvariable=self.texteVar, selectborderwidth=2)
		self.place(x=position[0], y=position[1], width=position[2], height=position[3])
		
		self.bind("<Return>", self.miseAjourItem)
		self.bind("<KP_Enter>", self.miseAjourItem)
		
	def miseAjourItem(self, event):
		valeur = self.texteVar.get()
		if self.colonne == "#0":
			self.parent.item(self.select, text= valeur)
		else:
			if self.colonne == "#1":
				self.parent.set(self.select, column=self.colonne, value=valeur)
				if self.ouvrage != None:
					self.ouvrage.ref = valeur
			if self.colonne == "#2":
				self.parent.set(self.select, column=self.colonne, value=valeur)
				if self.ouvrage != None:
					self.ouvrage.unite = valeur
			if self.colonne == "#3":
				try :
					valeur=float(valeur)
					self.parent.set(self.select, column=self.colonne, value=valeur)
					if self.ouvrage != None:
						self.ouvrage.quant = str(valeur)
					self.parent.set(self.select, column="#5", value = valeur * float(self.parent.item(self.select)['values'][3]))
				except:
					tkinter.messagebox.showwarning("Erreur de saisie", "La valeur saisie doit être un nombre")
			if self.colonne == "#4":
				try :
					valeur=float(valeur)
					self.parent.set(self.select, column=self.colonne, value=valeur)
					if self.ouvrage != None:
						self.ouvrage.prix = valeur
					self.parent.set(self.select, column="#5", value = valeur * float(self.parent.item(self.select)['values'][2]))
				except:
					tkinter.messagebox.showwarning("Erreur de saisie", "La valeur saisie doit être un nombre")
		self.destroy()

class DialogInfos(tkinter.Toplevel):
	
	def __init__(self, parent, indexItem, affaire, ouvrage):
		
		self.affaire = affaire
		self.ouvrage = ouvrage
		self.parent = parent
		self.indexItem = indexItem
		
		tkinter.Toplevel.__init__(self, self.parent)
		self.resizable(width=False, height=False)
		self.transient(self.master) # pour ne pas creer de nouvel icone dans la barre de lancement
		#self.overrideredirect(1) # pour enlever le bandeau supérieur propre a l os
		
		self.rowconfigure(0, weight=1)
		self.columnconfigure(0, weight=1)
		
		self.notebook = tkinter.ttk.Notebook(self)
		self.notebook.grid(row=0, column=0, sticky="WNES", padx=5, pady=5)
		
		self.pageDescription = DialogDesc(self, indexItem, self.affaire, self.ouvrage)
		self.pageQuantite = DialogQt(self, indexItem, self.ouvrage)
		
		self.notebook.add(self.pageDescription, text = 'Description')
		self.notebook.add(self.pageQuantite, text = 'Quantité')
		
		frameBas = tkinter.Frame(self, padx=2, pady=2)
		frameBas.grid(row=1, column=0, columnspan=2, sticky="EW")
		
		self.boutonValider = tkinter.Button(frameBas, text="Valider", height=1, width=10, command = self.valider)
		self.boutonValider.pack(side="right")
		
		self.boutonAnnuler = tkinter.Button(frameBas, text="Annuler", height=1, width=10, command = self.annuler)
		self.boutonAnnuler.pack(side="right")
	
	def miseAjourQuant(self):
		texte = self.pageQuantite.zoneTexte.get('0.0', 'end')
		liste = texte.split("\n")
		quantite = ""
		for ligne in liste:
			if ligne == "":
				pass
			else:
				quantite = quantite + "%s;" %(ligne)
		# suppression du dernier ;
		quantite = quantite[:len(quantite)-1]
		
		total = fonctions.evalQuantite(quantite)
		self.ouvrage.quant = quantite
		self.parent.set(self.indexItem, column="#3", value=float(total))
		self.parent.set(self.indexItem, column="#5", value = float(total) * float(self.parent.item(self.indexItem)['values'][3]))
	
	def valider(self):
		self.miseAjourQuant()
		self.destroy()
		
	def annuler(self):
		self.destroy()

class DialogDesc(tkinter.Frame):
	
	def __init__(self, parent, select, affaire, ouvrage):
		
		self.affaire = affaire
		self.ouvrage = ouvrage
		self.parent = parent
		self.select = select
		self.texteVarTitre = tkinter.StringVar()
		self.texteVarId = tkinter.StringVar()
		
		tkinter.Frame.__init__(self, self.parent, padx=2, pady=2)
		self.grid(row=0, column=0, sticky="WNES", padx=5, pady=5)
		
		self.labelTitre = tkinter.Label(self, text= "Titre", justify="left")
		self.labelTitre.grid(row=0, column=0, padx=5, pady=10, sticky="W")
		
		self.entryTitre = tkinter.Entry(self, textvariable=self.texteVarTitre, selectborderwidth=0)
		self.entryTitre.grid(row=1, column=0, columnspan=3, sticky="WE")
		
		self.boutonCCTP = tkinter.Button(self, text="CCTP", height=1, width=10, command = self.ouvrirCCTP)
		self.boutonCCTP.grid(row=1, column=3, columnspan=2, padx=10, sticky="WE")
		
		self.labelId = tkinter.Label(self, text= "Identifiant", justify="center")
		self.labelId.grid(row=2, column=0, padx=5, pady=10, sticky="WE")
		
		self.entryId = tkinter.Entry(self, textvariable=self.texteVarId, selectborderwidth=0, width=10)
		self.entryId.grid(row=3, column=0, sticky="WE")
		
		self.labelOption = tkinter.Label(self, text= "Base/Option", justify="center")
		self.labelOption.grid(row=2, column=1, padx=5, pady=10, sticky="WE")
		
		self.choixBaseOption = tkinter.StringVar()
		self.tupleBaseOption = ("Base", "Option")
		self.comboBaseOption = tkinter.ttk.Combobox(self, textvariable = self.choixBaseOption, values = self.tupleBaseOption, width=10, state = "readonly")
		self.comboBaseOption.grid(row =3, column =1, padx=5, pady=5, sticky="EW")
		
		self.labelTVA = tkinter.Label(self, text= "TVA", justify="center")
		self.labelTVA.grid(row=2, column=2, padx=5, pady=10, sticky="WE")
		
		self.choixTVA = tkinter.StringVar()
		self.comboTVA = tkinter.ttk.Combobox(self, textvariable = self.choixTVA, width=10, values = constantes.TVA, state = "readonly")
		self.comboTVA.grid(row =3, column =2, padx=5, pady=5, sticky="EW")
		
		self.labelIndexBT = tkinter.Label(self, text= "Index BT", justify="center")
		self.labelIndexBT.grid(row=2, column=3, columnspan=2, padx=5, pady=10, sticky="WE")
		
		self.choixIndexBT = tkinter.StringVar()
		self.comboIndexBT = tkinter.ttk.Combobox(self, textvariable = self.choixIndexBT, values = constantes.INDEXBT, width=10, state = "readonly")
		self.comboIndexBT.grid(row =3, column =3, columnspan=2, padx=5, pady=5, sticky="EW")
		
		self.labelLocalisation = tkinter.Label(self, text= "Localisation", justify="left")
		self.labelLocalisation.grid(row=4, column=0, padx=5, pady=15, sticky="W")
			
		self.zoneTexte = tkinter.Text(self, padx=2, pady=2, height=12, relief= "flat", highlightthickness= 0)
		self.zoneTexte_scroll = tkinter.Scrollbar(self, command = self.zoneTexte.yview, relief="flat")
		self.zoneTexte.configure(yscrollcommand =self.zoneTexte_scroll.set)
		self.zoneTexte.grid(row=5, column=0, columnspan=4, sticky="WNES")
		self.zoneTexte_scroll.grid(row=5, column=4, sticky="NS")
	
	def ouvrirCCTP(self):
		chemin = os.path.dirname(self.affaire.url) + "/bibli/essai.odt" #attention, ne fonctionne pour le moment que si une afaire est créé
		print(chemin)
		cctp = os.system('soffice %s' %(chemin))
		

class DialogQt(tkinter.Frame):
	
	def __init__(self, parent, select, ouvrage):
		
		self.parent = parent
		self.select = select
		self.ouvrage = ouvrage
		self.texteVar = tkinter.StringVar()
		
		tkinter.Frame.__init__(self, self.parent, padx=2, pady=2)
		self.grid(row=0, column=0, sticky="WNES", padx=5, pady=5)
		
		self.zoneTexte = tkinter.Text(self, padx=2, pady=2, relief= "flat", highlightthickness= 0)
		self.zoneTexte_scroll = tkinter.Scrollbar(self, command = self.zoneTexte.yview, relief="flat")
		self.zoneTexte.configure(yscrollcommand =self.zoneTexte_scroll.set)
		self.zoneTexte.grid(row=0, column=0, sticky="WNES")
		self.zoneTexte_scroll.grid(row=0, column=1, sticky="NS")
				
		if self.ouvrage.quant == None:
			pass
		else:
			s = self.ouvrage.quant.split(";")
			for ligne in s:
				self.zoneTexte.insert("end", "%s\n" %(ligne))
				self.zoneTexte.yview("moveto", 1)
		
		frameBas = tkinter.Frame(self, padx=2, pady=2)
		frameBas.grid(row=1, column=0, columnspan=2, sticky="EW")
		
		self.labelResultat = tkinter.Label(frameBas, textvariable= self.texteVar)
		self.labelResultat.pack(side="left")
		
		if self.ouvrage.unite == None :
			unite = ""
		else:
			unite = self.ouvrage.unite
		
		if self.ouvrage.quant == None:
			resultat = 0.0
			self.texteVar.set("Total = %s %s" % (resultat, unite))
		else :
			resultat = fonctions.evalQuantite(self.ouvrage.quant)
			self.texteVar.set("Total = %s %s" % (resultat, unite))
		
		self.parent.bind("<KeyPress-F9>", self._miseAjourQt)
		self.parent.bind("<Return>", self._miseAjourQt)
	
	def _miseAjourQt(self, event):
		texte = self.zoneTexte.get('0.0', 'end')
		liste = texte.split("\n")
		quantite = ""
		for ligne in liste:
			quantite = quantite + "%s;" %(ligne)
		total = fonctions.evalQuantite(quantite)
		self.texteVar.set("Total = %s %s" % (total, self.ouvrage.unite))
		
		

if __name__ == '__main__':
	Application = Main()
	Application.nouvelleAffaire()
	#Application.root.option_readfile("gui.cfg", priority=40)
	Application.root.mainloop()



# to do
# documenter et nettoyer le code
# implementer la lecture des fichiers dxf dans l evaluation des quantites
# voir pour creation d une pile undo/redo
# ajouter une fonction pour connaitre l etat d enregistrement afin de proposer l enregistrement avant de quitter, creer un nouveau document ou ouvrir un autre document
# bug : lorsque qu'un nouveau fichier est créé puis enregistré sous, lors des enregistrements suivants c'est la fenêtre enregistrer sous qui s'ouvre, le programme ne dois pas savoir quel est le nom de fichier à enregistrer, à voir...
# voir pour ajouter dans data.xml la possibilite d ajouter des varaintes par lot
# voir pour ajouter dans data.xml le coefficient de marge pour les estimations
# voir pour fichier base de donnee configuration de l application


