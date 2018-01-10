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

"""
This is the main module of the application.
"""

import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
import tkinter
import tkinter.ttk
import tkinter.filedialog
import tkinter.messagebox

import lib.fonctions
import lib.constantes
import gui.main_dialogs
import gui.treeview

class Main():
    """Main window class"""

    def __init__(self):
        """Initialize main window"""

        self.root = tkinter.Tk()
        self.root.title("opb - sans nom")
        self.root.wm_iconphoto(True, tkinter.PhotoImage(file="./img/icone.png"))

        #to make the window stretchable
        self.root.geometry("1500x800+100+100")
        self.root.minsize(width=1500, height=800)
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)

        #by default creating a new project
        self.project = Project(None)
        self.project.data.getroot()

        #initialize clipboard
        self.clipboard = []

        #initialize modifications dictionary
        self.modifications_dictionary = {}
        self.modifications_dictionary['undo'] = []
        self.modifications_dictionary['redo'] = []
        self.modifications_dictionary['flag'] = False

        # adding menu
        MenuBar(self, self.root)

        # adding tools bar
        ToolBar(self, self.root)


        ####################
        # project treeview #
        ####################

        #adding a frame container treeview
        tree_frame = tkinter.Frame(self.root)
        tree_frame.grid(row=2, column=0, sticky='WENS', padx=5, pady=5)
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        #adding treeview project
        self.tree_project = gui.treeview.ProjectTreeview(self, tree_frame)

        #to make the treeview stretchable on the entire window
        self.tree_project.grid(row=0, column=0, sticky='WENS')

        #connect functions to events
        self.tree_project.bind("<Double-Button-1>", self.__widget_for_editing_treeview)
        self.tree_project.bind("<Control-KeyPress-KP_8>", self.__go_up_item_event)
        self.tree_project.bind("<Control-KeyPress-KP_2>", self.__go_down_item_event)
        self.tree_project.bind("<Control-KeyPress-KP_6>", self.__indenting_item_event)
        self.tree_project.bind("<Control-KeyPress-KP_4>", self.__unindent_item_event)

        #####################
        # database treeview #
        #####################

        #adding treeview for database
        self.tree_base = gui.treeview.DataBaseTreeview(tree_frame)

        #to make the treeview stretchable on the entire window
        self.tree_base.grid(row=0, column=1, sticky='WENS')

        ##############
        # status bar #
        ##############

        #adding a frame for status bar
        status_frame = tkinter.Frame(self.root)
        status_frame.grid(row=3, column=0, sticky='WN', padx=5, pady=5)
        status_text = tkinter.Label(status_frame, text="R.A.S.")
        status_text.grid(row=0, column=0, sticky='WENS')

    def new_project(self):
        """Create a new project instance and set the main windows title"""

        if self.modifications_dictionary['flag'] is True:
            gui.main_dialogs.DialogSaveBeforeClose(self, "new_project")
        else:
            self.project = Project(None)
            root = self.project.data.getroot()
            self.tree_project.refresh(self, root)
            self.root.title("opb - sans nom")

    def open_project(self):
        """Open zip file, create a new project instance and transcript
           data.xml file in the treeview"""

        if self.modifications_dictionary['flag'] is True:
            gui.main_dialogs.DialogSaveBeforeClose(self, "open_project")
        else:
            url = tkinter.filedialog.askopenfilename(filetypes=[('Fichier zip', '*.zip')],\
                                                     title="Ouvrir un fichier ...")
            self.root.title("opb - %s" %(url))
            #Creating a new project instance of the project module
            self.project = Project(url)
            root = self.project.data.getroot()
            #Refreshing treeview
            self.tree_project.refresh(self, root)

    def __browse_xml_branch(self, childrens_xml, parent_tree, position):
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
                        item = self.tree_project.insert(parent_tree, position,\
                                                        text=children.find("name").text,\
                                                        open=True)
                    else:
                        item = self.tree_project.insert(parent_tree, position,\
                                                        text=children.find("name").text,\
                                                        open=False)
                    self.tree_project.items.append(item)
                    self.__browse_xml_branch(children.findall("element"), item, position)
                if children.get("id") == "chapter":
                    if children.get("open") == "true":
                        item = self.tree_project.insert(parent_tree, position,\
                                                        text=children.find("name").text,\
                                                        open=True)
                    else:
                        item = self.tree_project.insert(parent_tree, position,\
                                                        text=children.find("name").text,\
                                                        open=False)
                    self.tree_project.items.append(item)
                    self.__browse_xml_branch(children.findall("element"), item, position)
                if children.get("id") == "work":
                    quant = float(lib.fonctions.evalQuantite(children.find('quantity').text))
                    prix = float(children.find('price').text)
                    item = self.tree_project.insert(parent_tree, position,\
                                                   text=children.find('name').text,\
                                                   values=(children.find('code').text,\
                                                   children.find('unit').text,\
                                                   quant, prix, quant*prix))
                    self.tree_project.items.append(item)
                    work = Work(item, children.find('name').text,\
                                   children.find('status').text,\
                                   children.find('unit').text,\
                                   children.find('quantity').text,\
                                   prix, children.find('code').text,\
                                   children.find('localisation').text,\
                                   children.find('vat').text,\
                                   children.find('index').text)
                    self.project.add_work(work)

    def save_project(self):
        """save project in zip file"""

        if self.project.url is None:
            self.project.url = tkinter.filedialog.asksaveasfilename(\
                               filetypes=[('Fichier zip', '*.zip')],\
                               title="Fichier de sauvegarde ...")

        # update project xml file
        self.project.data = self.__groundwork_to_xml_object()

        # create or update the backup zip file
        self.project.saveZip()

        # update the main window title
        self.root.title("opb - %s" %(self.project.url))

        # add function for empty the undo and redo list
        self.__empty_undo_redo_lists()
        self.modifications_dictionary['flag'] = False

    def save_project_as(self):
        """Save project in a new zip file"""

        self.project.url = None
        self.save_project()

    def close(self):
        """Close the application and propose to save the changes"""

        if self.modifications_dictionary['flag'] is True:
            gui.main_dialogs.DialogSaveBeforeClose(self, "close")
        else:
            self.root.destroy()

    def __groundwork_to_xml_object(self):
        """Create an image of the treeview to an xml object"""

        xml = ET.ElementTree(ET.fromstring(lib.constantes.XMLTEMPLATE))
        #to do : try to built an xml object with an addition of some another xml object
        root = xml.getroot()
        groundwork = root.find("groundwork")
        self.__browse_treeview_branch(self.tree_project.get_children(), groundwork)
        lib.fonctions.indent(root)
        return xml

    def __browse_treeview_branch(self, childrens, parent):
        """browse treeview branch, when the node have childrens this
           fonction is recursive"""

        if childrens != []:
            for children in childrens:
                work = self.project.return_work(children)
                if work is None:
                    if len(self.tree_project.parents_item(children)) != 0:
                        if self.tree_project.item(children)['open'] is True:
                            node = ET.SubElement(parent, "element", id="chapter", open="true")
                        else:
                            node = ET.SubElement(parent, "element", id="chapter", open="false")
                        name = ET.SubElement(node, "name")
                        name.text = self.tree_project.item(children)['text']
                    else:
                        if self.tree_project.item(children)['open'] is True:
                            node = ET.SubElement(parent, "element", id="batch", open="true")
                        else:
                            node = ET.SubElement(parent, "element", id="batch", open="false")
                        name = ET.SubElement(node, "name")
                        name.text = self.tree_project.item(children)['text']
                    self.__browse_treeview_branch(self.tree_project.get_children(children), node)
                else:
                    node = ET.SubElement(parent, "element", id="work")
                    name = ET.SubElement(node, "name")
                    name.text = work.name
                    code = ET.SubElement(node, "code")
                    code.text = work.desc_id
                    description = ET.SubElement(node, "description") # not useful at the moment
                    localisation = ET.SubElement(node, "localisation")
                    localisation.text = work.loc
                    index = ET.SubElement(node, "index")
                    index.text = work.bt
                    price = ET.SubElement(node, "price")
                    price.text = str(work.prix)
                    quantity = ET.SubElement(node, "quantity")
                    quantity.text = work.quant
                    status = ET.SubElement(node, "status")
                    status.text = work.status
                    vat = ET.SubElement(node, "vat")
                    vat.text = work.tva
                    unit = ET.SubElement(node, "unit")
                    unit.text = work.unite

    def add_title(self):
        """Adds a new title under the item that has the focus"""

        select = self.tree_project.focus()
        parent = self.tree_project.parent(select)
        position = self.tree_project.index(select)+1
        item = self.tree_project.insert(parent, position, text="_Titre_")
        self.tree_project.items.append(item)
        self.add_modification()

    def add_work(self):
        """Adds a new work under the item that has the focus"""

        select = self.tree_project.focus()
        parent = self.tree_project.parent(select)
        position = self.tree_project.index(select)+1
        item = self.tree_project.insert(parent, position, text="_Ouvrage_",\
                                       values=("", "", 0.0, 0.0, ""))
        self.tree_project.items.append(item)
        work = Work(item)
        self.project.add_work(work)
        self.add_modification()

    def go_down_item(self):
        """Move down the item that has the focus when the button is
           pressed on the toolbar"""

        select = self.tree_project.focus()
        parent = self.tree_project.parent(select)
        position = self.tree_project.index(select)
        self.tree_project.move(select, parent, position+1)
        self.add_modification()

    def __go_down_item_event(self, event):
        """Move down the item that has the focus when the Ctrl+2 is
           pressed"""

        self.go_down_item()

    def go_up_item(self):
        """Move up the item that has the focus when the button is
           pressed on the toolbar"""

        select = self.tree_project.focus()
        parent = self.tree_project.parent(select)
        position = self.tree_project.index(select)
        self.tree_project.move(select, parent, position-1)
        self.add_modification()

    def __go_up_item_event(self, event):
        """Move down the item that has the focus when the Ctrl+8 is
           pressed"""

        self.go_up_item()

    def indenting_item(self):
        """Indent the item that has the focus when the button is
           pressed on the toolbar"""

        select = self.tree_project.focus()

        #if the item is a work, indentation maxi = 5
        if self.project.return_work(select) is None:
            if len(self.tree_project.parents_item()) < 4:
                previous = self.tree_project.prev(select)
                previous_childrens = self.tree_project.get_children(previous)
                self.tree_project.move(select, previous, len(previous_childrens))

        #if not, it's à chapter, so indentation maxi = 4
        else:
            if len(self.tree_project.parents_item()) < 3:
                previous = self.tree_project.prev(select)
                previous_childrens = self.tree_project.get_children(previous)
                self.tree_project.move(select, previous, len(previous_childrens))
        self.add_modification()

    def __indenting_item_event(self, event):
        """Indenting the item that has the focus when the Ctrl+6 is
           pressed"""

        self.indenting_item()

    def unindent_item(self):
        """Unindent the item that has the focus when the button is
           pressed on the toolbar"""

        select = self.tree_project.focus()
        parent = self.tree_project.parent(select)
        grand_parent = self.tree_project.parent(parent)
        position = self.tree_project.index(parent)
        self.tree_project.move(select, grand_parent, position+1)
        self.add_modification()

    def __unindent_item_event(self, event):
        """Unindent the item that has the focus when the Ctrl+4 is
           pressed"""

        self.unindent_item()

    def remove_item(self):
        """Remove the item that has the focus"""

        select = self.tree_project.focus()
        self.tree_project.delete(select)
        self.tree_project.items.remove(select)
        self.add_modification()

    def add_modification(self):
        """adding item in undo list and adding "*" before the root title name"""

        xml = self.__groundwork_to_xml_object()
        self.modifications_dictionary['undo'].append(xml)
        if self.modifications_dictionary['flag'] is False:
            self.modifications_dictionary['flag'] = True
            self.root.title("*opb - %s" % (self.project.url))

    def undo(self):
        """To do"""

        try:
            _id = len(self.modifications_dictionary['undo'])-1
            xml_cancelded = self.modifications_dictionary['undo'][_id]
            xml_restored = self.modifications_dictionary['undo'][_id-1]
            self.modifications_dictionary['redo'].append(xml_cancelded)
            del self.modifications_dictionary['undo'][_id]
            self.tree_project.refresh(self, xml_restored)
        except IndexError:
            print("Annulation not possible : the undo list is empty")

    def redo(self):
        """To do"""

        _id = len(self.modifications_dictionary['redo'])-1
        xml_restored = self.modifications_dictionary['redo'][_id]
        self.modifications_dictionary['undo'].append(xml_restored)
        del self.modifications_dictionary['redo'][_id]
        self.tree_project.refresh(self, xml_restored)

    def copy(self):
        """Adding the selection in the clipboard"""

        self.__empty_clipboard()
        xml = ET.ElementTree(ET.fromstring(lib.constantes.XMLSELECTION))
        root = xml.getroot()
        self.__browse_treeview_branch(self.tree_project.selection(), root)
        self.clipboard.append(xml)

    def paste(self):
        """Paste the selection under the item that has the focus"""

        select = self.tree_project.focus()
        xml = self.clipboard[0]
        self.__browse_xml_branch(xml.findall("element"), self.tree_project.parent(select),\
                            self.tree_project.index(select))
        self.add_modification()

    def __empty_clipboard(self):
        """Empty the clipboard, it's used before adding a new selection"""

        while len(self.clipboard) != 0:
            del self.clipboard[len(self.clipboard)-1]

    def __empty_undo_redo_lists(self):
        """Empty the undo and redo list when the project was saved"""

        while len(self.modifications_dictionary['undo']) != 0:
            del self.modifications_dictionary['undo'][len(self.modifications_dictionary['undo'])-1]
        while len(self.modifications_dictionary['redo']) != 0:
            del self.modifications_dictionary['redo'][len(self.modifications_dictionary['redo'])-1]

    def infos(self):
        """Open the dialog for edit the work"""

        select = self.tree_project.focus()
        work = self.project.return_work(select)
        if work is None:
            pass
        else:
            gui.main_dialogs.DialogWorkInfos(self, select, self.project, work)

    def __widget_for_editing_treeview(self, event):
        """Positioning an entry on the treeview to modify a value or
           creating a dialog to modify the quantity column"""

        if self.tree_project.winfo_children() == []:
            pass
        else: # deleting child widgets for only one child to be active
            for widget in self.tree_project.winfo_children():
                widget.destroy()
        select = self.tree_project.focus()
        item = self.tree_project.item(select)
        column = self.tree_project.identify_column(event.x)
        if column == "#0":
            text = item["text"]
            entry = EntryTreeview(self, text, column)
            self.tree_project.childs.append(entry)
        else:
            if column == "#1":
                text = item["values"][0]
                entry = EntryTreeview(self, text, column)
                self.tree_project.childs.append(entry)
            if column == "#2":
                text = item["values"][1]
                entry = EntryTreeview(self, text, column)
                self.tree_project.childs.append(entry)
            if column == "#3":
                text = item["values"][2]
                entry = EntryTreeview(self, text, column)
                self.tree_project.childs.append(entry)
            if column == "#4":
                text = item["values"][3]
                entry = EntryTreeview(self, text, column)
                self.tree_project.childs.append(entry)

class MenuBar(object):
    """Creating the menu bar at the top of main window"""

    def __init__(self, application, parent_gui):
        """Creating menu bar"""

        self.parent_gui = parent_gui
        self.application = application
        self.menu_bar = tkinter.Menu(self.parent_gui)
        self.menu_bar.configure(relief="flat")
        self.parent_gui.config(menu=self.menu_bar)
        self.__add_file_menu()
        self.__add_edit_menu()
        self.__add_groundwork_menu()

    def __add_file_menu(self):
        """Adding file menu in the menu bar"""

        #drop down file menu
        drop_down_file_menu = tkinter.Menu(self.menu_bar)

        #adding commands
        drop_down_file_menu.add_command(label="Nouveau",\
                                     underline=0,\
                                     command=self.application.new_project)
        drop_down_file_menu.add_command(label="Ouvrir",\
                                     underline=0,\
                                     command=self.application.open_project)
        drop_down_file_menu.add_separator()
        drop_down_file_menu.add_command(label="Enregister",\
                                      underline=0,\
                                      command=self.application.save_project)
        drop_down_file_menu.add_command(label="Enregister Sous",\
                                     underline=0,\
                                     command=self.application.save_project_as)
        drop_down_file_menu.add_separator()
        drop_down_file_menu.add_command(label="Quitter",\
                                     underline=0,\
                                     command=self.application.close)

        #adding the drop_down_file_menu to the menu bar
        self.menu_bar.add_cascade(label="Fichier", menu=drop_down_file_menu)

    def __add_edit_menu(self):
        """Adding edit menu in the menu bar"""

        #drop down edit menu
        drop_down_edit_menu = tkinter.Menu(self.menu_bar)

        #adding commands
        drop_down_edit_menu.add_command(label="Annuler", underline=0,\
                                     command=self.application.undo)
        drop_down_edit_menu.add_command(label="Rétablir", underline=0,\
                                     command=self.application.redo)
        drop_down_edit_menu.add_separator()
        drop_down_edit_menu.add_command(label="Copier", underline=0,\
                                     command=self.application.copy)
        drop_down_edit_menu.add_command(label="Coller", underline=0,\
                                     command=self.application.paste)

        #adding the drop_down_edit_menu to the menu bar
        self.menu_bar.add_cascade(label="Edition", menu=drop_down_edit_menu)

    def __add_groundwork_menu(self):
        """Adding groundwork menu in the menu bar"""

        #drop down groundwork menu
        drop_down_groundwork_menu = tkinter.Menu(self.menu_bar)

        #adding commands
        drop_down_groundwork_menu.add_command(label="Ajouter un titre",\
                                           underline=0,\
                                           command=self.application.add_title)
        drop_down_groundwork_menu.add_command(label="Ajouter un ouvrage",\
                                           underline=0,\
                                           command=self.application.add_work)
        drop_down_groundwork_menu.add_command(label="Supprimer un item",\
                                           underline=0,\
                                           command=self.application.remove_item)
        drop_down_groundwork_menu.add_command(label="Détail de l'ouvrage",\
                                           underline=0,\
                                           command=self.application.infos)

        #adding the drop_down_groundwork_menu to the menu bar
        self.menu_bar.add_cascade(label="Canevas", menu=drop_down_groundwork_menu)

class ToolBar():
    """Creating the tool bar at the top of main window"""

    def __init__(self, application, parent_gui):
        """Creating tool bar"""

        self.tools_frame = tkinter.Frame(parent_gui)
        self.tools_frame.grid(row=1, column=0, sticky='WN', padx=5, pady=5)
        self.application = application

        self.application.image_down_arrow = tkinter.PhotoImage(file="./img/fleche_bas_24x24.png")
        self.__add_button(self.application.image_down_arrow, self.application.go_down_item)
        self.__add_button(self.application.image_down_arrow, self.application.go_down_item)
        self.application.image_up_arrow = tkinter.PhotoImage(file="./img/fleche_haut_24x24.png")
        self.__add_button(self.application.image_up_arrow, self.application.go_up_item)
        self.application.image_right_arrow = tkinter.PhotoImage(file="./img/fleche_droite_24x24.png")
        self.__add_button(self.application.image_right_arrow, self.application.indenting_item)
        self.application.image_left_arrow = tkinter.PhotoImage(file="./img/fleche_gauche_24x24.png")
        self.__add_button(self.application.image_left_arrow, self.application.unindent_item)
        self.application.image_infos = tkinter.PhotoImage(file="./img/infos_24x24.png")
        self.__add_button(self.application.image_infos, self.application.infos)

    def __add_button(self, img, comm):
        """Adding down arrow button in the tool bar"""
        button = tkinter.Button(self.tools_frame,\
                                           image=img,\
                                           height=25, width=25,\
                                           relief='flat',\
                                           command=comm)
        button.pack(side='left')

    def hide(self):
        """Hide toolbar"""
        pass

    def show(self):
        """Show toolbar"""
        pass

class ProjectTreeview(tkinter.ttk.Treeview):
    """Treeview of the project and associated methods"""

    def __init__(self, application, parent_gui):
        """Initialize treeview"""

        tkinter.ttk.Treeview.__init__(self, parent_gui)

        self.childs = []
        self.items = []
        self.application = application

        self["columns"] = ("IdCCTP", "U", "Q", "PU", "PT")
        self.column("#1", width=150, stretch=False)
        self.column("#2", width=100, stretch=False)
        self.column("#3", width=100, stretch=False)
        self.column("#4", width=100, stretch=False)
        self.column("#5", width=100, stretch=False)

        self.heading("#1", text="IdCCTP")
        self.heading("#2", text="U")
        self.heading("#3", text="Q")
        self.heading("#4", text="PU")
        self.heading("#5", text="PT")
    
    def refresh(self, application, xml):
        """Refreshing treeview before loading a new project or  undo/redo instance"""
        
        for item in self.get_children():
            self.delete(item)
        #Get groundwork in xml object
        #xml = application.project.xml.getroot()
        groundwork = xml.find("groundwork")
        #xml file path for representation in the treeview
        self.__browse_xml_branch(groundwork.findall("element"), "", "end")
        
    
    def __browse_xml_branch(self, childrens_xml, parent_node, position):
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
                        item = self.application.tree_project.insert(parent_node, position,\
                                                        text=children.find("name").text,\
                                                        open=True)
                    else:
                        item = self.application.tree_project.insert(parent_node, position,\
                                                        text=children.find("name").text,\
                                                        open=False)
                    self.application.tree_project.items.append(item)
                    self.__browse_xml_branch(children.findall("element"), item, position)
                if children.get("id") == "chapter":
                    if children.get("open") == "true":
                        item = self.application.tree_project.insert(parent_node, position,\
                                                        text=children.find("name").text,\
                                                        open=True)
                    else:
                        item = self.application.tree_project.insert(parent_node, position,\
                                                        text=children.find("name").text,\
                                                        open=False)
                    self.application.tree_project.items.append(item)
                    self.__browse_xml_branch(children.findall("element"), item, position)
                if children.get("id") == "work":
                    quant = float(lib.fonctions.evalQuantite(children.find('quantity').text))
                    prix = float(children.find('price').text)
                    item = self.application.tree_project.insert(parent_node, position,\
                                                   text=children.find('name').text,\
                                                   values=(children.find('code').text,\
                                                   children.find('unit').text,\
                                                   quant, prix, quant*prix))
                    work = Work(item, children.find('name').text,\
                                   children.find('status').text,\
                                   children.find('unit').text,\
                                   children.find('quantity').text,\
                                   prix, children.find('code').text,\
                                   children.find('localisation').text,\
                                   children.find('vat').text,\
                                   children.find('index').text)
                    self.application.project.add_work(work)
        

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
                self.work.name = value
        if self.column == "#1":
            self.application.tree_project.set(self.select,\
                                              column=self.column, value=value)
            if self.work != None:
                self.work.desc_id = value
        if self.column == "#2":
            self.application.tree_project.set(self.select,\
                                              column=self.column, value=value)
            if self.work != None:
                self.work.unite = value
        if self.column == "#3":
            try:
                value = float(value)
                self.application.tree_project.set(self.select,\
                                                  column=self.column, value=value)
                if self.work != None:
                    self.work.quant = str(value)
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
                    self.work.prix = value
                self.application.tree_project.set(self.select,\
                                                  column="#5",\
                                                  value=\
                                                  value *\
                                                  float(self.application.tree_project.item(self.select)['values'][2]))
            except ValueError:
                tkinter.messagebox.showwarning("Erreur de saisie",\
                                               "La valeur saisie doit être un nombre")
        self.application.add_modification()
        self.destroy()

class Project():
	"""class defining the project"""
	
	def __init__(self, url= None):
		
		self.url = url
		
		if self.url == None:
			self.data = ET.ElementTree(ET.fromstring(lib.constantes.XMLTEMPLATE))
		else :
			# nettoyage du dossier temp
			self.cleanDirTemp()
			# extraction de l'archive dans le dossier temp
			fichierZip = zipfile.ZipFile(self.url,"r")
			fichierZip.extractall("./temp")
			fichierZip.close()
			self.data = ET.parse("./temp/data.xml")
			
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
			self.data.write("data.xml", encoding="UTF-8", xml_declaration=True)
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

if __name__ == '__main__':
    APPLICATION = Main()
    APPLICATION.root.mainloop()



# to do
# couper/coller
# implementer la lecture des fichiers dxf dans l evaluation des quantites
# voir pour creation d une pile undo/redo
# ajouter une fonction pour connaitre l etat d enregistrement afin de proposer l enregistrement
#   avant de quitter, creer un nouveau document ou ouvrir un autre document
# bug : lorsque qu'un nouveau fichier est créé puis enregistré sous, lors des enregistrements
#   suivants c'est la fenêtre enregistrer sous qui s'ouvre, le programme ne dois pas savoir
#   quel est le nom de fichier à enregistrer, à voir...
# voir pour ajouter dans data.xml la possibilite d ajouter des varaintes par lot
# voir pour ajouter dans data.xml le coefficient de marge pour les estimations
# voir pour fichier base de donnee configuration de l application
# rendre impossible l'indentation d'un titre après un ouvrage
# voir pour modification d'items multiples

