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
import xml.etree.ElementTree as ET

import tkinter
import tkinter.ttk
import tkinter.messagebox

import lib.constantes
import grammalecte

class DialogWorkInfos(tkinter.Toplevel):
    """Dialog for edit and update work"""

    def __init__(self, app, index_item, project, work):
        """Initialize dialog"""

        self.project = project
        self.work = work
        self.app = app # It's main windows
        self.parent = app.tree_project # It's the treeview
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
        self.page_work_description = DialogDescription(self, self.index_item, self.work)

        notebook.add(self.page_work_infos, text='Infos')
        notebook.add(self.page_work_quantity, text='Quantité')
        notebook.add(self.page_work_description, text='Description')

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
        quantity = ET.Element("quantity")
        for sub_measurement in list_quantity:
            if sub_measurement == "":
                pass
            else:
                sub_measurement_text = ET.Element("sub_measurement")
                sub_measurement_text.text = sub_measurement
                quantity.append(sub_measurement_text)
        self.work['quantity'] = quantity
        result = lib.fonctions.evalQuantiteNew(quantity)
        self.parent.set(self.index_item,\
                        column="#3",\
                        value= "%.3f" % float(result))
        self.parent.set(self.index_item,\
                        column="#5",\
                        value= "%.2f" % (float(result) * float(self.parent.item(self.index_item)['values'][3])))
        self.app.total_price_project.set("Prix total du projet = %.2f Euros HT" % (self.project.total_price_project()))

    def __update_work_description(self):
        """Update the work description, work description is an xml element object"""

        text = self.page_work_description.text_zone.get('0.0', 'end')
        list_paragraph = text.split("\n")
        description = ET.Element("description")
        for paragraph in list_paragraph:
            if paragraph == "":
                pass
            else:
                paragraph_text = ET.Element("p")
                paragraph_text.text = paragraph
                description.append(paragraph_text)
        self.work['description'] = description

    def __update_work_infos(self):
        """Update the work infos"""

        #update the name of work
        name = self.page_work_infos.text_var_title.get()
        self.work['name'] = name
        self.parent.item(self.index_item, text=name)

        #update the description Id of work
        code = self.page_work_infos.text_var_id.get()
        self.work['code'] = code
        #self.parent.set(self.index_item, column="#1", value=code)

        #update the status of work
        status = self.page_work_infos.choice_base_or_option.get()
        self.work['status'] = status

        #update the VAT rate of work
        vat_rate = self.page_work_infos.choice_vat_rate.get()
        self.work['vat'] = vat_rate

        #update the index BT of work
        index = self.page_work_infos.choice_id_bt.get()
        self.work['index'] = index

        #update localisation
        text = self.page_work_infos.text_zone.get('0.0', 'end')
        list_paragraph = text.split("\n")
        localisation = ET.Element("localisation")
        for paragraph in list_paragraph:
            if paragraph == "":
                pass
            else:
                paragraph_text = ET.Element("p")
                paragraph_text.text = paragraph
                localisation.append(paragraph_text)
        self.work['localisation'] = localisation

    def validate(self):
        """run the update methodes and close the dialog"""

        self.__update_work_quantity()
        self.__update_work_infos()
        self.__update_work_description()
        completed_field_information = self.parent.completed_field_info(self.work['description'],\
                                                                       self.work['localisation'])
        self.parent.set(self.index_item, column="#1", value=completed_field_information)
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
        self.text_var_title.set(self.work['name'])
        self.text_var_id = tkinter.StringVar()
        self.text_var_id.set(self.work['code'])

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
        if self.work['status'] == "":
            self.choice_base_or_option.set("Base")
        else:
            self.choice_base_or_option.set(self.work['status'])
        self.combo_base_or_option.grid(row=3, column=1, padx=5, pady=5, sticky="EW")

        self.vat_label = tkinter.Label(self, text="TVA", justify="center")
        self.vat_label.grid(row=2, column=2, padx=5, pady=10, sticky="WE")

        self.choice_vat_rate = tkinter.StringVar()
        self.vat_combo = tkinter.ttk.Combobox(self, textvariable=self.choice_vat_rate,\
                                             width=10, values=lib.constantes.TVA,\
                                             state="readonly")
        self.vat_combo.grid(row=3, column=2, padx=5, pady=5, sticky="EW")
        if self.work['vat'] == "":
            self.choice_vat_rate.set(lib.constantes.TVA[2])
        else:
            self.choice_vat_rate.set(self.work['vat'])

        label_id_bt = tkinter.Label(self, text="Index BT", justify="center")
        label_id_bt.grid(row=2, column=3, columnspan=2, padx=5, pady=10, sticky="WE")

        self.choice_id_bt = tkinter.StringVar()
        combo_id_bt = tkinter.ttk.Combobox(self, textvariable=self.choice_id_bt,\
                                                 values=lib.constantes.INDEXBT, width=10,\
                                                 state="readonly")
        combo_id_bt.grid(row=3, column=3, columnspan=2, padx=5, pady=5, sticky="EW")
        if self.work['index'] == "":
            self.choice_id_bt.set(lib.constantes.INDEXBT[0])
        else:
            for id_bt in lib.constantes.INDEXBT:
                if self.work['index'] == id_bt:
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

        if self.work['localisation'] is None:
            pass
        #else:
            #localisation_lines = self.work['localisation'].split("$")
            #for line in localisation_lines:
                #self.text_zone.insert("end", "%s\n" %(line))
                #self.text_zone.yview("moveto", 1)
        else:
            for paragraph in self.work['localisation']:
                self.text_zone.insert("end", "%s\n" %(paragraph.text))
                self.text_zone.yview("moveto", 1)

    def open_cctp(self):
        """Opening the description file in .odt format of the work"""
        if self.text_var_id.get() == "" or self.text_var_id.get() == "None":
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

        if self.work['quantity'] is None:
            pass
        else :
            #sub_measurement_list = self.work['quantity'].getchildren()
            sub_measurement_list = list(self.work['quantity'])
            if sub_measurement_list == []:
                try:
                    quantity_lines = self.work['quantity'].text.split("$")
                    for line in quantity_lines:
                        self.text_zone.insert("end", "%s\n" %(line))
                        self.text_zone.yview("moveto", 1)
                except AttributeError:
                    pass
            else:
                for sub_measurement in sub_measurement_list:
                    self.text_zone.insert("end", "%s\n" %(sub_measurement.text))
                    self.text_zone.yview("moveto", 1)

        bottom_frame = tkinter.Frame(self, padx=2, pady=2)
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky="EW")

        self.result_label = tkinter.Label(bottom_frame, textvariable=self.text_var)
        self.result_label.pack(side="left")

        if self.work['unit'] is None:
            unite = ""
        else:
            unite = self.work['unit']

        if self.work['quantity'] is None:
            resultat = 0.0
            self.text_var.set("Total = %s %s" % (resultat, unite))
        else:
            try:
                resultat = lib.fonctions.evalQuantiteNew(self.work['quantity'])
            except TypeError:
                resultat = lib.fonctions.evalQuantite(self.work['quantity'])
            self.text_var.set("Total = %.3f %s" % (resultat, unite))

        self.parent.bind("<KeyPress-F9>", self.__update_quantity)
        self.parent.bind("<Return>", self.__update_quantity)

    def __update_quantity(self, event):
        #texte = self.text_zone.get('0.0', 'end')
        #quantity_lines = texte.split("\n")
        #quantite = ""
        #for line in quantity_lines:
            #quantite = quantite + "%s$" %(line)
        #total = lib.fonctions.evalQuantite(quantite)
        #self.text_var.set("Total = %s %s" % (total, self.work['unit']))
        text = self.text_zone.get('0.0', 'end')
        list_quantity = text.split("\n")
        quantity = ET.Element("quantity")
        for sub_measurement in list_quantity:
            if sub_measurement == "":
                pass
            else:
                sub_measurement_text = ET.Element("sub_measurement")
                sub_measurement_text.text = sub_measurement
                quantity.append(sub_measurement_text)
        self.work['quantity'] = quantity
        result = lib.fonctions.evalQuantiteNew(quantity)
        self.text_var.set("Total = %.3f %s" % (result, self.work['unit']))

class DialogDescription(tkinter.Frame):
    """Class for editing quantity of work"""

    def __init__(self, parent, select, work):

        self.parent = parent
        self.select = select
        self.work = work
        self.text_var = tkinter.StringVar()

        tkinter.Frame.__init__(self, self.parent, padx=2, pady=2)
        self.grid(row=0, column=0, sticky="WNES", padx=5, pady=5)
        
        frame_tools_bar = tkinter.Frame(self, padx=2, pady=2)
        frame_tools_bar.grid(row=0, column=0, columnspan=2, sticky="W")
        
        self.img_orthographe = tkinter.PhotoImage(file="./img/orthographe_24x24.png")
        button_orthographe = tkinter.Button(frame_tools_bar,\
                                           image=self.img_orthographe,\
                                           height=25, width=25,\
                                           relief='flat',\
                                           command=self.orthographe)
        button_orthographe.pack(side="left")
        
        self.img_undo = tkinter.PhotoImage(file="./img/undo_24x24.png")
        button_undo = tkinter.Button(frame_tools_bar,\
                                           image=self.img_undo,\
                                           height=25, width=25,\
                                           relief='flat',\
                                           command=self.undo)
        button_undo.pack(side="left")

        self.img_redo = tkinter.PhotoImage(file="./img/redo_24x24.png")
        button_redo = tkinter.Button(frame_tools_bar,\
                                           image=self.img_redo,\
                                           height=25, width=25,\
                                           relief='flat',\
                                           command=self.redo)
        button_redo.pack(side="left")

        self.text_zone = tkinter.Text(self, padx=2, pady=2, relief="flat", highlightthickness=0,\
                                            undo=True)
        self.text_zone_scroll = tkinter.Scrollbar(self, command=self.text_zone.yview, relief="flat")
        self.text_zone.configure(yscrollcommand=self.text_zone_scroll.set)
        self.text_zone.grid(row=1, column=0, sticky="WNES")
        self.text_zone_scroll.grid(row=1, column=1, sticky="NS")

        if self.work['description'] is None:
            pass
        else:
            for paragraph in self.work['description']:
                self.text_zone.insert("end", "%s\n" %(paragraph.text))
                self.text_zone.yview("moveto", 1)

    def orthographe(self):
        """Mise en évidence des erreurs de grammaire et d'orthographe"""
        tags = self.text_zone.tag_names()
        Err_tags = []
        for tag in tags:
            if tag[0:3]=="Err":
                Err_tags.append(tag)
        self.text_zone.tag_delete(Err_tags)
        oGrammarChecker = grammalecte.GrammarChecker("fr")
        text = self.text_zone.get('0.0', 'end')
        list_paragraph = text.split("\n")
        id_error = 0
        for paragraph in list_paragraph:
            aGrammErrs, aSpellErrs = oGrammarChecker.getParagraphErrors(paragraph)
            id_line = list_paragraph.index(paragraph)+1
            for Err in aGrammErrs:
                id_error = id_error+1
                if Err['sRuleId'] == "apostrophe_typographique":
                    self.text_zone.delete("%s.%s"%(id_line,Err['nEnd']-1))
                    self.text_zone.insert("%s.%s"%(id_line,Err['nEnd']-1),"’")
                else:
                    self.text_zone.tag_add("Err%s"%(id_error), "%s.%s"%(id_line,Err['nStart']), "%s.%s"%(id_line,Err['nEnd']))
                    self.text_zone.tag_config("Err%s"%(id_error), background="blue")
                print(Err['sLineId'])
                print(Err['sRuleId']) #Faire une fonction pour résoudre automatiquement les problèmes d'apostrophe typographiques, etc.    apostrophe_typographique
                print(Err['sType'])
                print(Err["aSuggestions"])
            for Err in aSpellErrs:
                id_error = id_error+1
                self.text_zone.tag_add("Err%s"%(id_error), "%s.%s"%(id_line,Err['nStart']), "%s.%s"%(id_line,Err['nEnd']))
                self.text_zone.tag_config("Err%s"%(id_error), background="red")

    def undo(self):
        self.text_zone.edit_undo()

    def redo(self):
        self.text_zone.edit_redo()

class DialogSaveBeforeClose(tkinter.Toplevel):
    """Dialog for propose to save the project before closing application"""

    def __init__(self, application, method):
        """Initialize dialog"""

        self.application = application # It's the application
        self.method = method # It's the method that called this class

        tkinter.Toplevel.__init__(self, self.application.root)
        self.resizable(width=False, height=False)
        self.transient(self.master) # for not creating a new icon in the loading bar
        self.title("Sauvegarde du projet...")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        label = tkinter.Label(self, text="Voulez-vous sauvegarder les modifications apportées \nau projet avant de quitter l'application ?",\
                              justify="center")
        label.grid(row=0, column=0, sticky="WNES", padx=10, pady=10)
        label.configure(font="TkHeadingFont")

        bottom_frame = tkinter.Frame(self, padx=10, pady=10)
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
        if self.method == "new_project":
            self.application.modifications_dictionary['flag'] = False
            self.application.new_project()
        if self.method == "open_project":
            self.application.modifications_dictionary['flag'] = False
            self.application.open_project()
        else:
            self.application.root.destroy()

    def no(self):
        """Close the dialog"""

        self.destroy()
        if self.method == "new_project":
            self.application.modifications_dictionary['flag'] = False
            self.application.new_project()
        if self.method == "open_project":
            self.application.modifications_dictionary['flag'] = False
            self.application.open_project()
        #else:
            #self.application.root.destroy()

class DialogPricePerBatch(tkinter.Toplevel):
    """Dialog for display price per batch"""

    def __init__(self, app):
        """Initialize dialog"""

        #self.project = project
        self.app = app # It's main windows
        self.treeview = app.tree_project # It's the treeview
        print(self.treeview.get_children)

        for batch in self.treeview.get_children():
            total = self.__browse_batch_for_total_price_per_batch(batch.get_children, 0.00)
            print(self.treeview.item(batch)['text'] + "----" + total)

        #tkinter.Toplevel.__init__(self, self.parent)
        #self.resizable(width=False, height=False)
        #self.transient(self.master) # pour ne pas creer de nouvel icone dans la barre de lancement
        #self.overrideredirect(1) # pour enlever le bandeau supérieur propre a l os

    def __browse_batch_for_total_price_per_batch(self, node, total):
        """Calculate the total price of a batch, browse treeview batch, when the node have childrens this
           fonction is recursive"""

        if node.get_children() != []:
            for children in node.get_children():
                work = self.project.return_work(children)
                if work is None:
                    self.__browse_batch_for_total_price_per_batch(children.get_children(), total)
                else:
                    if work['quantity'] is None:
                        pass
                    elif work['price'] is None:
                        pass
                    else:
                        total = total + float(work['price'])*float(lib.fonctions.evalQuantiteNew(work['quantity']))
        return total

class DialogSpellingCheck(tkinter.Toplevel):
    """Dialog for splelling and grammar check"""
    
    def __init__(self, parent):
        """Initialize dialog"""
        
        self.parent = parent
        tkinter.Toplevel.__init__(self, self.parent)
        self.resizable(width=False, height=False)
        self.transient(self.master) # for not creating a new icon in the loading bar
        self.title("Vérification de la grammaire et de l'orthographe...")
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        
        self.text_type_of_error = tkinter.StringVar()
        self.text_type_of_error.set(" ")
        type_of_error_label = tkinter.Label(self, textvariable=self.text_type_of_error)
        type_of_error_label.grid(row=0, column=0, sticky="W", padx=5, pady=10)
        
        frame_text = tkinter.Frame(self, padx=2, pady=2)
        frame_text.grid(row=1, column=0, sticky="WNES", padx=5, pady=5)
        frame_text.rowconfigure(0, weight=1)
        frame_text.columnconfigure(0, weight=1)

        self.text_zone = tkinter.Text(frame_text, padx=2, pady=2, relief="flat",\
                                      highlightthickness=0, height=7, width=40)
        self.text_zone_scroll = tkinter.Scrollbar(frame_text, command=self.text_zone.yview,\
                                                  relief="flat")
        self.text_zone.configure(yscrollcommand=self.text_zone_scroll.set)
        self.text_zone.grid(row=0, column=0, sticky="WNES")
        self.text_zone_scroll.grid(row=0, column=1, sticky="NS")
        
        button_ignore = tkinter.Button(self, text="Ignorer",\
                                      height=1, width=10,\
                                      command=self.ignore)
        button_ignore.grid(row=1, column=1, sticky="N", padx=5, pady=5)
        
        suggestions_label = tkinter.Label(self, text="Suggestions")
        suggestions_label.grid(row=3, column=0, sticky="W", padx=5, pady=10)
        
        frame_list = tkinter.Frame(self, padx=2, pady=2)
        frame_list.grid(row=4, column=0, sticky="WNES", padx=5, pady=5)
        frame_list.rowconfigure(0, weight=1)
        frame_list.columnconfigure(0, weight=1)
        
        self.suggestions_list = tkinter.StringVar()
        #self.suggestions_list.set("Suggestion01 Suggestion02 Suggestion03")
        self.list_zone = tkinter.Listbox(frame_list, relief="flat",\
                                      highlightthickness=0, height=7, width=40,\
                                      listvariable=self.suggestions_list)
        self.list_zone_scroll = tkinter.Scrollbar(frame_list, command=self.list_zone.yview,\
                                                  relief="flat")
        self.list_zone.configure(yscrollcommand=self.text_zone_scroll.set)
        self.list_zone.grid(row=0, column=0, sticky="WNES")
        self.list_zone_scroll.grid(row=0, column=1, sticky="NS")
        
        button_replace = tkinter.Button(self, text="Remplacer",\
                                      height=1, width=10,\
                                      command=self.replace)
        button_replace.grid(row=4, column=1, sticky="N", padx=5, pady=5)
        
        button_replace_all = tkinter.Button(self, text="Remplacer tout",\
                                      height=1, width=10,\
                                      command=self.replace_all)
        button_replace_all.grid(row=4, column=1, sticky="N", padx=5, pady=5)
        
    
    def spelling_check(self):
        """Mise en évidence des erreurs de grammaire et d'orthographe"""
        tags = self.text_zone.tag_names()
        Err_tags = []
        for tag in tags:
            if tag[0:3]=="Err":
                Err_tags.append(tag)
        self.text_zone.tag_delete(Err_tags)
        oGrammarChecker = grammalecte.GrammarChecker("fr")
        text = self.text_zone.get('0.0', 'end')
        list_paragraph = text.split("\n")
        id_error = 0
        for paragraph in list_paragraph:
            aGrammErrs, aSpellErrs = oGrammarChecker.getParagraphErrors(paragraph)
            id_line = list_paragraph.index(paragraph)+1
            for Err in aGrammErrs:
                id_error = id_error+1
                if Err['sRuleId'] == "apostrophe_typographique":
                    self.text_zone.delete("%s.%s"%(id_line,Err['nEnd']-1))
                    self.text_zone.insert("%s.%s"%(id_line,Err['nEnd']-1),"’")
                else:
                    self.text_zone.tag_add("Err%s"%(id_error), "%s.%s"%(id_line,Err['nStart']), "%s.%s"%(id_line,Err['nEnd']))
                    self.text_zone.tag_config("Err%s"%(id_error), background="blue")
                print(Err['sLineId'])
                print(Err['sRuleId']) #Faire une fonction pour résoudre automatiquement les problèmes d'apostrophe typographiques, etc.    apostrophe_typographique
                print(Err['sType'])
                print(Err["aSuggestions"])
            for Err in aSpellErrs:
                id_error = id_error+1
                self.text_zone.tag_add("Err%s"%(id_error), "%s.%s"%(id_line,Err['nStart']), "%s.%s"%(id_line,Err['nEnd']))
                self.text_zone.tag_config("Err%s"%(id_error), background="red")

    def ignore(self):
        """to do"""
        
        pass

    def replace(self):
        """to do"""
        
        pass
        
        
