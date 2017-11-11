#!/usr/bin/env python3
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

import sys
import os
import shutil

import tkinter
import tkinter.ttk
import tkinter.messagebox

import lib.constantes

class DialogWorkInfos(tkinter.Toplevel):
    """Dialog for edit and update work"""

    def __init__(self, parent, index_item, project, work):
        """Initialize dialog"""

        self.project = project
        self.work = work
        self.parent = parent # It's the treeview
        self.index_item = index_item #It's the index of the item selected in the treeview

        tkinter.Toplevel.__init__(self, self.parent)
        self.resizable(width=False, height=False)
        self.transient(self.master) # pour ne pas creer de nouvel icone dans la barre de lancement
        #self.overrideredirect(1) # pour enlever le bandeau supérieur propre a l os

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        notebook = tkinter.ttk.Notebook(self)
        notebook.grid(row=0, column=0, sticky="WNES", padx=5, pady=5)

        self.page_work_infos = DescDialog(self, self.index_item, self.project, self.work)
        self.page_work_quantity = DialogQt(self, self.index_item, self.work)

        notebook.add(self.page_work_infos, text='Description')
        notebook.add(self.page_work_quantity, text='Quantité')

        bottom_frame = tkinter.Frame(self, padx=2, pady=2)
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky="EW")

        button_validate = tkinter.Button(bottom_frame, text="Valider",\
                                        height=1, width=10,\
                                        command=self.validate)
        button_validate.pack(side="right")

        button_cancel = tkinter.Button(bottom_frame, text="Annuler",\
                                      height=1, width=10,\
                                      command=self.cancel)
        button_cancel.pack(side="right")

    def __update_work_quantity(self):
        """Update the work quantity"""

        text = self.page_work_quantity.text_zone.get('0.0', 'end')
        list_quantity = text.split("\n")
        quantity = ""
        for line in list_quantity:
            if line == "":
                pass
            else:
                quantity = quantity + "%s$" %(line)
        #deleting the last character ;
        quantity = quantity[:len(quantity)-1]

        result = lib.fonctions.evalQuantite(quantity)
        self.work.quant = quantity
        self.parent.set(self.index_item,\
                        column="#3",\
                        value=float(result))
        self.parent.set(self.index_item,\
                        column="#5",\
                        value=float(result) * float(self.parent.item(self.index_item)['values'][3]))

    def __update_work_infos(self):
        """Update the work infos"""

        #update the name of work
        name = self.page_work_infos.text_var_title.get()
        self.work.name = name
        self.parent.item(self.index_item, text=name)

        #update the description Id of work
        desc_id = self.page_work_infos.text_var_id.get()
        self.work.desc_id = desc_id
        self.parent.set(self.index_item, column="#1", value=desc_id)

        #update the status of work
        status = self.page_work_infos.choice_base_or_option.get()
        self.work.status = status

        #update the VAT rate of work
        vat_rate = self.page_work_infos.choice_vat_rate.get()
        self.work.tva = vat_rate

        #update the index BT of work
        id_bt = self.page_work_infos.choice_id_bt.get()
        self.work.bt = id_bt

        #update the localisation of work
        text = self.page_work_infos.text_zone.get('0.0', 'end')
        list_quantity = text.split("\n")
        localisation = ""
        for line in list_quantity:
            if line == "":
                pass
            else:
                localisation = localisation + "%s$" %(line)
        # deleting the last character $ of the string localisation
        localisation = localisation[:len(localisation)-1]
        self.work.loc = localisation

    def validate(self):
        """run the update methodes and close the dialog"""

        self.__update_work_quantity()
        self.__update_work_infos()
        self.destroy()

    def cancel(self):
        """Close the dialog"""

        self.destroy()

class DescDialog(tkinter.Frame):
    """Class to edit description and infos of work"""

    def __init__(self, parent, select, project, work):

        self.project = project
        self.work = work
        self.parent = parent
        self.select = select
        self.text_var_title = tkinter.StringVar()
        self.text_var_title.set(self.work.name)
        self.text_var_id = tkinter.StringVar()
        self.text_var_id.set(self.work.desc_id)

        tkinter.Frame.__init__(self, self.parent, padx=2, pady=2)
        self.grid(row=0, column=0, sticky="WNES", padx=5, pady=5)

        title_label = tkinter.Label(self, text="Titre", justify="left")
        title_label.grid(row=0, column=0, padx=5, pady=10, sticky="W")

        entry_title = tkinter.Entry(self, textvariable=self.text_var_title, selectborderwidth=0)
        entry_title.grid(row=1, column=0, columnspan=3, sticky="WE")

        button_cctp = tkinter.Button(self, text="CCTP",\
                                         height=1, width=10,\
                                         command=self.open_cctp)
        button_cctp.grid(row=1, column=3, columnspan=2, padx=10, sticky="WE")

        label_id = tkinter.Label(self, text="Identifiant", justify="center")
        label_id.grid(row=2, column=0, padx=5, pady=10, sticky="WE")

        self.entry_id = tkinter.Entry(self, textvariable=self.text_var_id,\
                                     selectborderwidth=0, width=10)
        self.entry_id.grid(row=3, column=0, sticky="WE")

        self.option_label = tkinter.Label(self, text="Base/Option", justify="center")
        self.option_label.grid(row=2, column=1, padx=5, pady=10, sticky="WE")

        self.choice_base_or_option = tkinter.StringVar()
        self.tuple_base_option = ("Base", "Option")
        self.combo_base_or_option = tkinter.ttk.Combobox(self,\
                                                    textvariable=self.choice_base_or_option,\
                                                    values=self.tuple_base_option, width=10,\
                                                    state="readonly")
        if self.work.status == "" or self.work.status != self.tuple_base_option[0]\
                                  or self.work.status != self.tuple_base_option[0]:
            self.choice_base_or_option.set("Base")
        else:
            self.choice_base_or_option.set(self.work.status)
        self.combo_base_or_option.grid(row=3, column=1, padx=5, pady=5, sticky="EW")

        self.vat_label = tkinter.Label(self, text="TVA", justify="center")
        self.vat_label.grid(row=2, column=2, padx=5, pady=10, sticky="WE")

        self.choice_vat_rate = tkinter.StringVar()
        self.vat_combo = tkinter.ttk.Combobox(self, textvariable=self.choice_vat_rate,\
                                             width=10, values=lib.constantes.TVA,\
                                             state="readonly")
        self.vat_combo.grid(row=3, column=2, padx=5, pady=5, sticky="EW")
        if self.work.tva == "" or self.work.tva != lib.constantes.TVA[0]\
                               or self.work.tva != lib.constantes.TVA[1]\
                               or self.work.tva != lib.constantes.TVA[2]:
            self.choice_vat_rate.set(lib.constantes.TVA[2])
        else:
            self.choice_vat_rate.set(self.work.tva)

        label_id_bt = tkinter.Label(self, text="Index BT", justify="center")
        label_id_bt.grid(row=2, column=3, columnspan=2, padx=5, pady=10, sticky="WE")

        self.choice_id_bt = tkinter.StringVar()
        combo_id_bt = tkinter.ttk.Combobox(self, textvariable=self.choice_id_bt,\
                                                 values=lib.constantes.INDEXBT, width=10,\
                                                 state="readonly")
        combo_id_bt.grid(row=3, column=3, columnspan=2, padx=5, pady=5, sticky="EW")
        if self.work.bt == "":
            self.choice_id_bt.set(lib.constantes.INDEXBT[0])
        else:
            for id_bt in lib.constantes.INDEXBT:
                if self.work.bt == id_bt:
                    self.choice_id_bt.set(id_bt)
                    break
                else:
                    self.choice_id_bt.set(lib.constantes.INDEXBT[0])

        localisation_label = tkinter.Label(self, text="Localisation", justify="left")
        localisation_label.grid(row=4, column=0, padx=5, pady=15, sticky="W")

        self.text_zone = tkinter.Text(self, padx=2, pady=2, height=12, relief="flat",\
                                     highlightthickness=0)
        self.text_zone_scroll = tkinter.Scrollbar(self, command=self.text_zone.yview, relief="flat")
        self.text_zone.configure(yscrollcommand=self.text_zone_scroll.set)
        self.text_zone.grid(row=5, column=0, columnspan=4, sticky="WNES")
        self.text_zone_scroll.grid(row=5, column=4, sticky="NS")

        if self.work.loc is None:
            pass
        else:
            localisation_lines = self.work.loc.split("$")
            for line in localisation_lines:
                self.text_zone.insert("end", "%s\n" %(line))
                self.text_zone.yview("moveto", 1)

    def open_cctp(self):
        """Opening the description file in .odt format of the work"""
        if self.text_var_id.get() == "":
            tkinter.messagebox.showwarning("Attention",\
                                           "Veuillez saisir un identifiant pour l'ouvrage")
        else:
            try:
                os.mkdir(os.getcwd() + "/temp/ref")
            except:
                pass
            files = os.listdir(os.getcwd() + "/temp/ref")
            test = False
            for file_ in files:
                split = file_.split("/")
                odt_file = split[-1]
                if odt_file[0:-4] == self.text_var_id.get():
                    if sys.platform == 'win32':
                        description = os.system('start '\
                                                +lib.constantes.SOFFICEPATH
                                                +" "\
                                                +os.getcwd()\
                                                +"\\temp\\ref\\"\
                                                +odt_file)
                    else:
                        os.system('soffice %s' %(os.getcwd()\
                                                 +"/temp/ref/"\
                                                 +odt_file))
                    test = True
                    break
            if test is False:
                shutil.copy(os.getcwd()+"/templates/workTemplate.odt",\
                            os.getcwd()+"/temp/ref/"+self.text_var_id.get()+".odt")
                if sys.platform == 'win32':
                    os.system('start '\
                              +lib.constantes.SOFFICEPATH\
                              +" "\
                              +os.getcwd()\
                              +"\\temp\\ref\\"\
                              +self.text_var_id.get()\
                              +".odt")
                else:
                    os.system('soffice %s' %(os.getcwd()\
                              +"/temp/ref/"\
                              +self.text_var_id.get()\
                              +".odt"))

class DialogQt(tkinter.Frame):
    """Class for editing quantity of work"""

    def __init__(self, parent, select, work):

        self.parent = parent
        self.select = select
        self.work = work
        self.text_var = tkinter.StringVar()

        tkinter.Frame.__init__(self, self.parent, padx=2, pady=2)
        self.grid(row=0, column=0, sticky="WNES", padx=5, pady=5)

        self.text_zone = tkinter.Text(self, padx=2, pady=2, relief="flat", highlightthickness=0)
        self.text_zone_scroll = tkinter.Scrollbar(self, command=self.text_zone.yview, relief="flat")
        self.text_zone.configure(yscrollcommand=self.text_zone_scroll.set)
        self.text_zone.grid(row=0, column=0, sticky="WNES")
        self.text_zone_scroll.grid(row=0, column=1, sticky="NS")

        if self.work.quant is None:
            pass
        else:
            quantity_lines = self.work.quant.split("$")
            for line in quantity_lines:
                self.text_zone.insert("end", "%s\n" %(line))
                self.text_zone.yview("moveto", 1)

        bottom_frame = tkinter.Frame(self, padx=2, pady=2)
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky="EW")

        self.result_label = tkinter.Label(bottom_frame, textvariable=self.text_var)
        self.result_label.pack(side="left")

        if self.work.unite is None:
            unite = ""
        else:
            unite = self.work.unite

        if self.work.quant is None:
            resultat = 0.0
            self.text_var.set("Total = %s %s" % (resultat, unite))
        else:
            resultat = lib.fonctions.evalQuantite(self.work.quant)
            self.text_var.set("Total = %s %s" % (resultat, unite))

        self.parent.bind("<KeyPress-F9>", self.__update_quantity)
        self.parent.bind("<Return>", self.__update_quantity)

    def __update_quantity(self, event):
        texte = self.text_zone.get('0.0', 'end')
        quantity_lines = texte.split("\n")
        quantite = ""
        for line in quantity_lines:
            quantite = quantite + "%s$" %(line)
        total = lib.fonctions.evalQuantite(quantite)
        self.text_var.set("Total = %s %s" % (total, self.work.unite))

class DialogSaveBeforeClose(tkinter.Toplevel):
    """Dialog for propose to save the project before closing application"""

    def __init__(self, application, parent_gui):
        """Initialize dialog"""

        self.application = application # It's the application
        self.parent_gui = parent_gui
        
        tkinter.Toplevel.__init__(self, self.parent_gui)
        self.resizable(width=False, height=False)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        label = tkinter.Label(self, text="Voulez-vous sauvegarder les modifications apportées au projet avant de quitter l'application ?",\
                              justify="center")
        label.grid(row=0, column=0, sticky="WNES", padx=5, pady=5)

        bottom_frame = tkinter.Frame(self, padx=2, pady=2)
        bottom_frame.grid(row=1, column=0, sticky="EW")

        button_yes = tkinter.Button(bottom_frame, text="Oui",\
                                        height=1, width=10,\
                                        command=self.yes)
        button_yes.pack(side="right")

        button_no = tkinter.Button(bottom_frame, text="Non",\
                                      height=1, width=10,\
                                      command=self.no)
        button_no.pack(side="right")

    def yes(self):
        """Save application and destroy fenêtre"""

        self.application.save_project()
        self.destroy()
        self.parent_gui.destroy()

    def no(self):
        """Close the dialog"""

        self.destroy()
        self.parent_gui.destroy()
