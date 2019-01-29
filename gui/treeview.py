#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  opb.py

#  Copyright 2018 Jean-Michel <Jean-Michel@PC-JM>

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

"""
This is the module for gui treeview.
"""

import tkinter
import tkinter.ttk
import lib.fonctions
import xml.etree.ElementTree as ET

class OpbTreeview(tkinter.ttk.Treeview):
    """Main class for treeview in opb"""

    def __init__(self, application, parent_gui):
        """Initilise tkinter.ttk.Treeview"""

        tkinter.ttk.Treeview.__init__(self, parent_gui)

    def go_down_item(self):
        """Move down the item that has the focus when the button is
           pressed on the toolbar"""

        select = self.focus()
        parent = self.parent(select)
        position = self.index(select)
        self.move(select, parent, position+1)
        self.application.add_modification()

    def go_down_item_event(self, event):
        """Move down the item that has the focus when the Ctrl+2 is
           pressed"""

        self.go_down_item()

    def go_up_item(self):
        """Move up the item that has the focus when the button is
           pressed on the toolbar"""

        select = self.focus()
        parent = self.parent(select)
        position = self.index(select)
        self.move(select, parent, position-1)
        self.application.add_modification()

    def go_up_item_event(self, event):
        """Move down the item that has the focus when the Ctrl+8 is
           pressed"""

        self.go_up_item()

class ProjectTreeview(OpbTreeview):
    """Treeview of the project and associated methods"""

    def __init__(self, application, parent_gui):
        """Initialize treeview"""

        OpbTreeview.__init__(self, application, parent_gui)

        self.childs = []
        self.items = []
        self.application = application

        self["columns"] = ("infos", "U", "Q", "PU", "PT")
        self.column("#1", width=150, stretch=False, anchor='center')
        self.column("#2", width=100, stretch=False, anchor='center')
        self.column("#3", width=100, stretch=False, anchor='e')
        self.column("#4", width=100, stretch=False, anchor='e')
        self.column("#5", width=100, stretch=False, anchor='e')

        self.heading("#1", text="infos")
        self.heading("#2", text="U")
        self.heading("#3", text="Q")
        self.heading("#4", text="PU")
        self.heading("#5", text="PT")

    def refresh(self, application, xml):
        """Refreshing treeview before loading a new project or  undo/redo instance"""

        for item in self.get_children():
            self.delete(item)
        groundwork = xml.find("groundwork")
        #xml file path for representation in the treeview
        self.browse_xml_branch(groundwork.findall("element"), "", "end")
        self.application.total_price_project.set("Prix total du projet = %.2f Euros HT"\
                                                  % (self.application.project.total_price_project()))
        
    def browse_xml_branch(self, childrens_xml, parent_node, position):
        """browse xml file branch, when the node have childrens this
           fonction is recursive"""

        if childrens_xml != []:
            for children in childrens_xml:
                if position == "end":
                    pass
                else:
                    position = position+1
                if children.get("id") == "batch":
                    if children.get("open") == "true":
                        item = self.insert(parent_node, position,\
                                           text=children.find("name").text,\
                                           open=True)
                    else:
                        item = self.insert(parent_node, position,\
                                           text=children.find("name").text,\
                                           open=False)
                    self.items.append(item)
                    self.browse_xml_branch(children.findall("element"), item, position)
                if children.get("id") == "chapter":
                    if children.get("open") == "true":
                        item = self.insert(parent_node, position,\
                                           text=children.find("name").text,\
                                           open=True)
                    else:
                        item = self.insert(parent_node, position,\
                                           text=children.find("name").text,\
                                           open=False)
                    self.items.append(item)
                    self.browse_xml_branch(children.findall("element"), item, position)
                if children.get("id") == "work":
                    work = {}
                    work['name'] = children.find('name').text
                    work['code'] = children.find('code').text
                    work['description'] = children.find('description') #it's xml node
                    work['localisation'] = children.find('localisation') #it's xml node
                    work['index'] = children.find('index').text
                    work['price'] = children.find('price').text
                    work['quantity'] = children.find('quantity') #it's xml node
                    work['status'] = children.find('status').text
                    work['vat'] = children.find('vat').text
                    work['unit'] = children.find('unit').text
                    completed_field_information = self.completed_field_info(work['description'], work['localisation'])
                    #if work['description'].getchildren() != [] and work['localisation'].getchildren() != []:
                        #completed_field_information ="TL"
                    #elif work['description'].getchildren() == [] and work['localisation'].getchildren() != []:
                        #completed_field_information ="L"
                    #elif work['description'].getchildren() != [] and work['localisation'].getchildren() == []:
                        #completed_field_information ="T"
                    #else:
                        #completed_field_information =""
                    #item = self.insert(parent_node, position,\
                                       #text=children.find('name').text,\
                                       #values=(children.find('code').text,\
                                       #children.find('unit').text,\
                                       #"%.3f" % lib.fonctions.evalQuantiteNew(children.find('quantity')),\
                                       #"%.2f" % float(children.find('price').text),\
                                       #"%.2f" % (lib.fonctions.evalQuantiteNew(children.find('quantity'))\
                                                 #*float(children.find('price').text))))
                    item = self.insert(parent_node, position,\
                                       text=work['name'],\
                                       values=(completed_field_information,\
                                       work['unit'],\
                                       "%.3f" % lib.fonctions.evalQuantiteNew(work['quantity']),\
                                       "%.2f" % float(work['price']),\
                                       "%.2f" % (lib.fonctions.evalQuantiteNew(work['quantity'])*float(work['price']))))
                    work['iid'] = item
                    self.items.append(item)
                    self.application.project.add_work(work)
    
    def completed_field_info(self, work_description, work_localisation):
        """Returns a string indicating status of work description and work localisation
        work_description and work_localisation are xml nodes"""

        if work_description.getchildren() != [] and work_localisation.getchildren() != []:
            completed_field_information ="TL"
        elif work_description.getchildren() == [] and work_localisation.getchildren() != []:
            completed_field_information ="L"
        elif work_description.getchildren() != [] and work_localisation.getchildren() == []:
            completed_field_information ="T"
        else:
            completed_field_information =""
        return completed_field_information
                    
    def parents_item(self, select=None):
        """Returns the parent list of a selected item"""

        if select is None:
            select = self.focus()

        #creation of root children list
        children_list = self.get_children()

        #creation of a tree of parents
        parent_tree = []
        test = False

        #we check if the focus is a child of root
        for child in children_list:
            if child == select:
                test = True
        while test is False:
            parent = self.parent(select)

            #we check if the parent is a child of root
            for child in children_list:
                if child == parent:
                    test = True
            select = parent
            parent_tree.append(parent)
        return parent_tree


class DataBaseTreeview(tkinter.ttk.Treeview):
    """Treeview of the data base and associated methods"""

    def __init__(self, parent_gui):
        """Initialize treeview"""

        tkinter.ttk.Treeview.__init__(self, parent_gui)

        self.childs = []
        self.items = []

        self["columns"] = ("IdCCTP", "U", "PU")
        self.column("#1", width=150, stretch=False)
        self.column("#2", width=100, stretch=False)
        self.column("#3", width=100, stretch=False)

        self.heading("#1", text="IdCCTP")
        self.heading("#2", text="U")
        self.heading("#3", text="PU")

    def reset_treeview(self):
        """Reset treeview before loading a new data base"""

        if self.items is not []:
            for item in self.items:
                try:
                    self.delete(item)
                except:
                    pass
    
    def hide_treeview(self):
        """Hide treeview"""
        
        self.destroy()
    
    def show_treeview(self):
        """Show treeview"""
        
        self.grid(row=1, column=1, sticky='WENS')


class EntryTreeview(tkinter.Entry):
    """Creating entry in a treeview line for editing"""

    def __init__(self, application, text, column):
        """Initialize treeview"""

        self.application = application
        self.column = column
        self.select = application.tree_project.focus()
        self.position = application.tree_project.bbox(self.select, column=self.column)
        self.work = application.project.return_work(self.select)
        self.text_var = tkinter.StringVar()
        self.text_var.set(text)

        tkinter.Entry.__init__(self, self.application.tree_project,\
                               textvariable=self.text_var, selectborderwidth=2)
        self.place(x=self.position[0], y=self.position[1],\
                   width=self.position[2], height=self.position[3])

        self.bind("<Return>", self.update_item)
        self.bind("<KP_Enter>", self.update_item)

    def update_item(self, event):
        """Update the item"""

        value = self.text_var.get()
        if self.column == "#0":
            self.application.tree_project.item(self.select, text=value)
            if self.work != None:
                self.work['name'] = value
        if self.column == "#1":
            self.application.tree_project.set(self.select,\
                                              column=self.column, value=value)
            if self.work != None:
                self.work['code'] = value
        if self.column == "#2":
            self.application.tree_project.set(self.select,\
                                              column=self.column, value=value)
            if self.work != None:
                self.work['unit'] = value
        if self.column == "#3":
            try:
                value = float(value)
                self.application.tree_project.set(self.select,\
                                                  column=self.column, value="%.3f" % value)
                if self.work != None:
                    sub_measurement_text = ET.Element("sub_measurement")
                    sub_measurement_text.text = str(value)
                    quantity = ET.Element("quantity")
                    quantity.append(sub_measurement_text)
                    self.work['quantity'] = quantity
                self.application.tree_project.set(self.select,\
                                                  column="#5",\
                                                  value=\
                                                  value *\
                                                  float(self.application.tree_project.item(self.select)['values'][3]))
            except ValueError:
                tkinter.messagebox.showwarning("Erreur de saisie",\
                                               "La valeur saisie doit être un nombre")
        if self.column == "#4":
            try:
                value = float(value)
                self.application.tree_project.set(self.select,\
                                                  column=self.column, value=value)
                if self.work != None:
                    self.work['price'] = str(value)
                self.application.tree_project.set(self.select,\
                                                  column="#5",\
                                                  value=\
                                                  value *\
                                                  float(self.application.tree_project.item(self.select)['values'][2]))
            except ValueError:
                tkinter.messagebox.showwarning("Erreur de saisie",\
                                               "La valeur saisie doit être un nombre")
        self.application.add_modification()
        self.application.total_price_project.set("Prix total du projet = %.2f Euros HT"\
                                                  % (self.application.project.total_price_project()))
        self.destroy()
