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
import tkinter.filedialog
import tkinter.messagebox

from lib.project import Project, Work
import lib.fonctions
import lib.constantes


class Main():
    """Main window class"""

    def __init__(self):
        """Initialize main window"""

        self.root = tkinter.Tk()
        self.root.title("opb - sans nom")
        self.root.wm_iconphoto(True, tkinter.PhotoImage(file="./img/icone.png"))

        #to make the window stretchable
        self.root.geometry("1500x900+20+20")
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)

        #by default creating a new project
        self.project = Project(None)
        self.project.xml.getroot()

        #initilize clipboard
        self.clipboard = []

        ###############
        # adding menu #
        ###############

        menu = tkinter.Frame(self.root, borderwidth=2)
        menu.grid(row=0, column=0, sticky="WE", padx=5, pady=5)

        #file menu
        file_menu = tkinter.Menubutton(menu, text="Fichier")
        file_menu.pack(side="left")

        #drop down file menu
        drop_down_file_menu = tkinter.Menu(file_menu)

        #menu integration
        file_menu.configure(menu=drop_down_file_menu)

        #adding commands
        drop_down_file_menu.add_command(label="Nouveau",\
                                     underline=0,\
                                     command=self.new_project)
        drop_down_file_menu.add_command(label="Ouvrir",\
                                     underline=0,\
                                     command=self.open_project)
        drop_down_file_menu.add_command(label="Enregister",\
                                      underline=0,\
                                      command=self.save_project)
        drop_down_file_menu.add_command(label="Enregister Sous",\
                                     underline=0,\
                                     command=self.save_project_as)

        #edit menu
        edit_menu = tkinter.Menubutton(menu, text="Edition")
        edit_menu.pack(side="left")

        #drop down edit menu
        drop_down_edit_menu = tkinter.Menu(edit_menu)

        #menu integration
        edit_menu.configure(menu=drop_down_edit_menu)

        #adding commands
        drop_down_edit_menu.add_command(label="Annuler", underline=0,\
                                     command=self.undo)
        drop_down_edit_menu.add_command(label="Rétablir", underline=0,\
                                     command=self.redo)
        drop_down_edit_menu.add_command(label="Copier", underline=0,\
                                     command=self.copy)
        drop_down_edit_menu.add_command(label="Coller", underline=0,\
                                     command=self.paste)

        #groundwork menu
        groundwork_menu = tkinter.Menubutton(menu, text="Canevas")
        groundwork_menu.pack(side="left")

        #drop down groundwork menu
        drop_down_groundwork_menu = tkinter.Menu(groundwork_menu)

        #menu integration
        groundwork_menu.configure(menu=drop_down_groundwork_menu)

        #adding commands
        drop_down_groundwork_menu.add_command(label="Ajouter un titre",\
                                           underline=0,\
                                           command=self.add_title)
        drop_down_groundwork_menu.add_command(label="Ajouter un ouvrage",\
                                           underline=0,\
                                           command=self.add_work)
        drop_down_groundwork_menu.add_command(label="Supprimer un item",\
                                           underline=0,\
                                           command=self.remove_item)
        drop_down_groundwork_menu.add_command(label="Détail de l'ouvrage",\
                                           underline=0,\
                                           command=self.infos)

        ####################
        # adding tools bar #
        ####################

        # adding a frame container buttons
        tools_frame = tkinter.Frame(self.root)
        tools_frame.grid(row=1, column=0, sticky='WN', padx=5, pady=5)

        # adding buttons
        self.image_down_arrow = tkinter.PhotoImage(file="./img/fleche_bas_24x24.png")
        down_arrow_button = tkinter.Button(tools_frame,\
                                           image=self.image_down_arrow,\
                                           height=25, width=25,\
                                           relief='flat',\
                                           command=self.go_down_item)
        down_arrow_button.pack(side='left')

        self.image_up_arrow = tkinter.PhotoImage(file="./img/fleche_haut_24x24.png")
        up_arrow_button = tkinter.Button(tools_frame,\
                                         image=self.image_up_arrow,\
                                         height=25, width=25,\
                                         relief='flat',\
                                         command=self.go_up_item)
        up_arrow_button.pack(side='left')

        self.image_right_arrow = tkinter.PhotoImage(file="./img/fleche_droite_24x24.png")
        right_arrow_button = tkinter.Button(tools_frame,\
                                            image=self.image_right_arrow,\
                                            height=25, width=25,\
                                            relief='flat',\
                                            command=self.indenting_item)
        right_arrow_button.pack(side='left')

        self.image_left_arrow = tkinter.PhotoImage(file="./img/fleche_gauche_24x24.png")
        left_arrow_button = tkinter.Button(tools_frame,\
                                           image=self.image_left_arrow,\
                                           height=25, width=25,\
                                           relief='flat',\
                                           command=self.unindent_intem)
        left_arrow_button.pack(side='left')

        self.image_infos = tkinter.PhotoImage(file="./img/infos_24x24.png")
        infos_button = tkinter.Button(tools_frame,\
                                      image=self.image_infos,\
                                      height=25, width=25,\
                                      relief='flat',\
                                      command=self.infos)
        infos_button.pack(side='left')

        ####################
        # project treeview #
        ####################

        #adding a frame container treeview
        tree_frame = tkinter.Frame(self.root)
        tree_frame.grid(row=2, column=0, sticky='WENS', padx=5, pady=5)
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        #adding treeview project
        self.tree_project = ProjectTreeview(tree_frame)

        #to make the treeview stretchable on the entire window
        self.tree_project.grid(row=0, column=0, sticky='WENS')

        #connect functions to events
        self.tree_project.bind("<Double-Button-1>", self.widget_for_editing_treeview)
        self.tree_project.bind("<Control-KeyPress-KP_8>", self.go_up_item_event)
        self.tree_project.bind("<Control-KeyPress-KP_2>", self.go_down_item_event)
        self.tree_project.bind("<Control-KeyPress-KP_6>", self.indenting_item_event)
        self.tree_project.bind("<Control-KeyPress-KP_4>", self.unindent_intem_event)

        #####################
        # database treeview #
        #####################

        #adding treeview for database
        self.tree_base = DataBaseTreeview(tree_frame)

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

        self.project = Project(None)
        self.project.xml.getroot()
        self.tree_project.reset_treeview()
        self.root.title("opb - sans nom")

    def open_project(self):
        """Open zip file, create a new project instance and transcript
           data.xml file in the treeview"""

        url = tkinter.filedialog.askopenfilename(filetypes=[('Fichier zip', '*.zip')],\
                                                 title="Fichier de sauvegarde ...")
        self.tree_project.reset_treeview()
        self.root.title("opb - %s" %(url))

        #Creating a new project instance of the project module
        self.project = Project(url)
        root = self.project.xml.getroot()

        #Creating a list of items (checking the utility)
        self.tree_project.items = []

        #xml file path for representation in the treeview
        self.browse_xml_branch(root.findall("element"), "")

    def browse_xml_branch(self, childrens_xml, parent_tree):
        """browse xml file branch, when the node have childrens this
           fonction is recursive"""

        if childrens_xml != []:
            for children in childrens_xml:
                if children.get("id") == "lot":
                    item = self.tree_project.insert(parent_tree, "end",\
                                                   text=children.get("name"))
                    self.tree_project.items.append(item)
                    self.browse_xml_branch(children.findall("element"), item)
                if children.get("id") == "chapitre":
                    item = self.tree_project.insert(parent_tree, "end",\
                                                   text=children.get("name"))
                    self.tree_project.items.append(item)
                    self.browse_xml_branch(children.findall("element"), item)
                if children.get("id") == "ouvrage":
                    quant = float(lib.fonctions.evalQuantite(children.get('quant')))
                    try:
                        prix = float(children.get('prix'))
                    except:
                        prix = 0.0
                    item = self.tree_project.insert(parent_tree, "end",\
                                                   text=children.get('name'),\
                                                   values=(children.get('descId'),\
                                                   children.get('unite'),\
                                                   quant, prix, quant*prix))
                    self.tree_project.items.append(item)
                    work = Work(item, children.get('name'),\
                                   children.get('status'),\
                                   children.get('unite'),\
                                   children.get('quant'),\
                                   prix, children.get('descId'),\
                                   children.get('loc'),\
                                   children.get('tva'),\
                                   children.get('bt'))
                    self.project.add_work(work)

    def save_project(self):
        """save project in zip file"""

        if self.project.url is None:
            self.project.url = tkinter.filedialog.asksaveasfilename(\
                               filetypes=[('Fichier zip', '*.zip')],\
                               title="Fichier de sauvegarde ...")

        # update project xml file
        self.project.xml = self.groundwork_to_xml_object()

        # create or update the backup zip file
        self.project.saveZip()

        # update the main window title
        self.root.title("opb - %s" %(self.project.url))

    def save_project_as(self):
        """Save project in a new zip file"""

        self.project.url = None
        self.save_project()

    def groundwork_to_xml_object(self):
        """Create an image of the treeview to an xml object"""

        xml = ET.ElementTree(ET.fromstring(lib.constantes.XMLTEMPLATE))
        #to do : try to built an xml object with an addition of some another xml object
        root = xml.getroot()
        self.browse_treeview_branch(self.tree_project.get_children(), root)
        lib.fonctions.indent(root)
        return xml

    def browse_treeview_branch(self, childrens, parent):
        """browse treeview branch, when the node have childrens this
           fonction is recursive"""

        if childrens != []:
            for children in childrens:
                work = self.project.return_work(children)
                if work is None:
                    if len(self.tree_project.parents_item(children)) != 0:
                        node = ET.SubElement(parent, "element",\
                                            id="chapitre",\
                                            name=self.tree_project.item(children)['text'])
                    else:
                        node = ET.SubElement(parent, "element",\
                                             id="lot",\
                                             name=self.tree_project.item(children)['text'])
                    self.browse_treeview_branch(self.tree_project.get_children(children), node)
                else:
                    node = ET.SubElement(parent, "element",\
                                         id="ouvrage",\
                                         name=work.name,\
                                         status=work.status,\
                                         unite=work.unite,\
                                         prix=str(work.prix),\
                                         desc_id=work.desc_id,\
                                         loc=work.loc,\
                                         bt=work.bt,\
                                         quant=work.quant,\
                                         tva=work.tva)

    def add_title(self):
        """Adds a new title under the item that has the focus"""

        select = self.tree_project.focus()
        parent = self.tree_project.parent(select)
        position = self.tree_project.index(select)+1
        item = self.tree_project.insert(parent, position, text="_Titre_")
        self.tree_project.items.append(item)

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

    def go_down_item(self):
        """Move down the item that has the focus when the button is
           pressed on the toolbar"""

        select = self.tree_project.focus()
        parent = self.tree_project.parent(select)
        position = self.tree_project.index(select)
        self.tree_project.move(select, parent, position+1)

    def go_down_item_event(self, event):
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

    def go_up_item_event(self, event):
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

    def indenting_item_event(self, event):
        """Indenting the item that has the focus when the Ctrl+6 is
           pressed"""

        self.indenting_item()

    def unindent_intem(self):
        """Unindent the item that has the focus when the button is
           pressed on the toolbar"""

        select = self.tree_project.focus()
        parent = self.tree_project.parent(select)
        grand_parent = self.tree_project.parent(parent)
        position = self.tree_project.index(parent)
        self.tree_project.move(select, grand_parent, position+1)

    def unindent_intem_event(self, event):
        """Unindent the item that has the focus when the Ctrl+4 is
           pressed"""

        self.unindent_intem()

    def remove_item(self):
        """Remove the item that has the focus"""

        select = self.tree_project.focus()
        self.tree_project.delete(select)
        self.tree_project.items.remove(select)

    def undo(self):
        """To do"""

        pass
        # TO DO

    def redo(self):
        """To do"""

        pass
        # TO DO

    def copy(self):
        """Adding the selection in the clipboard"""

        self.empty_clipboard()
        selection = self.tree_project.selection()
        for item in selection:
            self.clipboard.append(item)

    def paste(self):
        """Paste the selection under the item that has the focus"""

        select = self.tree_project.focus()
        self.__recursive_paste(self.clipboard, self.tree_project.parent(select),\
                            self.tree_project.index(select)+1)

    def __recursive_paste(self, childrens, parent, position):
        """It's a recursive used to paste selection"""

        if childrens != []:
            for children in childrens:
                work = self.project.return_work(children)
                if work is None:
                    item = self.tree_project.insert(parent, position,\
                                                   text=self.tree_project.item(children)['text'])
                    self.tree_project.items.append(item)
                    self.__recursive_paste(self.tree_project.get_children(children), item, "end")
                else:
                    quant = float(lib.fonctions.evalQuantite(work.quant))
                    try:
                        prix = float(work.prix)
                    except:
                        prix = 0.0
                    item = self.tree_project.insert(parent, position, text=work.name,\
                                                   values=(work.desc_id,\
                                                           work.unite,\
                                                           quant, prix, quant*prix))
                    self.tree_project.items.append(item)
                    new_work = Work(item, work.name,\
                                         work.status,\
                                         work.unite,\
                                         work.quant,\
                                         work.prix,\
                                         work.desc_id,\
                                         work.loc,\
                                         work.tva,\
                                         work.bt)
                    self.project.add_work(new_work)

    def empty_clipboard(self):
        """Empty the clipboard, it's used before adding a new selection"""

        while len(self.clipboard) != 0:
            del self.clipboard[len(self.clipboard)-1]

    def infos(self):
        """Open the dialog for edit the work"""

        select = self.tree_project.focus()
        work = self.project.return_work(select)
        if work is None:
            pass
        else:
            DialogWorkInfos(self.tree_project, select, self.project, work)

    def widget_for_editing_treeview(self, event):
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
        position = self.tree_project.bbox(select, column=column)
        work = self.project.return_work(select)
        if column == "#0":
            text = item["text"]
            entry = EntryTreeview(self.tree_project,\
                                  position, text, column, select, work)
            self.tree_project.enfants.append(entry)
        else:
            if column == "#1":
                text = item["values"][0]
                entry = EntryTreeview(self.tree_project,\
                                      position, text, column, select, work)
                self.tree_project.enfants.append(entry)
            if column == "#2":
                text = item["values"][1]
                entry = EntryTreeview(self.tree_project,\
                                      position, text, column, select, work)
                self.tree_project.enfants.append(entry)
            if column == "#3":
                text = item["values"][2]
                entry = EntryTreeview(self.tree_project,\
                                      position, text, column, select, work)
                self.tree_project.enfants.append(entry)
            if column == "#4":
                text = item["values"][3]
                entry = EntryTreeview(self.tree_project,\
                                      position, text, column, select, work)
                self.tree_project.enfants.append(entry)


class ProjectTreeview(tkinter.ttk.Treeview):
    """Treeview of the project and associated methods"""

    def __init__(self, parent_gui):
        """Initialize treeview"""

        tkinter.ttk.Treeview.__init__(self, parent_gui)

        self.childs = []
        self.items = []

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

    def reset_treeview(self):
        """Reset treeview before loading a new project"""

        if self.items is not []:
            for item in self.items:
                try:
                    self.delete(item)
                except:
                    pass

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

    def __init__(self, parent, position, text, column, select, work):
        """Initialize treeview"""

        self.parent = parent
        self.column = column
        self.select = select
        self.text_var = tkinter.StringVar()
        self.text_var.set(text)
        self.work = work

        tkinter.Entry.__init__(self, self.parent,\
                               textvariable=self.text_var, selectborderwidth=2)
        self.place(x=position[0], y=position[1],\
                   width=position[2], height=position[3])

        self.bind("<Return>", self.update_item)
        self.bind("<KP_Enter>", self.update_item)

    def update_item(self, event):
        """Update the item"""

        value = self.text_var.get()
        if self.column == "#0":
            self.parent.item(self.select, text=value)
            if self.work != None:
                self.work.name = value
        else:
            if self.column == "#1":
                self.parent.set(self.select,\
                                column=self.column, value=value)
                if self.work != None:
                    self.work.desc_id = value
            if self.column == "#2":
                self.parent.set(self.select,\
                                column=self.column, value=value)
                if self.work != None:
                    self.work.unite = value
            if self.column == "#3":
                try:
                    value = float(value)
                    self.parent.set(self.select,\
                                    column=self.column, value=value)
                    if self.work != None:
                        self.work.quant = str(value)
                    self.parent.set(self.select,\
                                    column="#5",\
                                    value=value * float(self.parent.item(self.select)['values'][3]))
                except:
                    tkinter.messagebox.showwarning("Erreur de saisie",\
                                                   "La valeur saisie doit être un nombre")
            if self.column == "#4":
                try:
                    value = float(value)
                    self.parent.set(self.select,\
                                    column=self.column, value=value)
                    if self.work != None:
                        self.work.prix = value
                    self.parent.set(self.select,\
                                    column="#5",\
                                    value=value * float(self.parent.item(self.select)['values'][2]))
                except:
                    tkinter.messagebox.showwarning("Erreur de saisie",\
                                                   "La valeur saisie doit être un nombre")
        self.destroy()


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

        self.page_work_infos = DescDialog(self, index_item, self.project, self.work)
        self.page_work_quantity = DialogQt(self, index_item, self.work)

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

    def update_work_quantity(self):
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

    def update_work_infos(self):
        """Update the work infos"""

        #update the name of work
        name = self.page_work_infos.text_var_title.get()
        self.work.name = name
        self.parent.item(self.index_item, text=name)

        #update the description Id of work
        desc_id = self.page_work_infos.textVarId.get()
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
        text = self.page_work_infos.zoneText.get('0.0', 'end')
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

        self.update_work_quantity()
        self.update_work_infos()
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



if __name__ == '__main__':
    APPLICATION = Main()
    APPLICATION.root.mainloop()



# to do
# couper/coller
# documenter et nettoyer le code
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


