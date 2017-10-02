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


import tkinter
import tkinter.ttk
import tkinter.filedialog
import tkinter.messagebox
import xml.etree.ElementTree as ET
import sys
import os
import shutil

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
        self.root.title("opb - sans nom")
        
        #initilize clipboard
        self.clipboard = []
        
        ###############
        # adding menu #
        ###############
        
        menu = tkinter.Frame(self.root, borderwidth=2)
        menu.grid(row=0, column=0, sticky="WE", padx=5, pady=5)
        
        #file menu
        fileMenu = tkinter.Menubutton(menu, text="Fichier")
        fileMenu.pack(side="left")
        
        #drop down file menu
        dropDownFileMenu = tkinter.Menu(fileMenu)
                
        #menu integration
        fileMenu.configure(menu = dropDownFileMenu)
        
        #adding commands
        dropDownFileMenu.add_command(label="Nouveau",\
                                     underline=0,\
                                     command = self.new_project)
        dropDownFileMenu.add_command(label="Ouvrir",\
                                     underline=0,\
                                     command = self.open_project)
        dropDownFileMenu.add_command(label="Enregister",\
                                      underline=0,\
                                      command = self.save_project)
        dropDownFileMenu.add_command(label="Enregister Sous",\
                                     underline=0,\
                                     command = self.save_project_as)
        
        #edit menu
        editMenu = tkinter.Menubutton(menu, text="Edition")
        editMenu.pack(side="left")
        
        #drop down edit menu
        dropDownEditMenu = tkinter.Menu(editMenu)
                
        #menu integration
        editMenu.configure(menu = dropDownEditMenu)
        
        #adding commands
        dropDownEditMenu.add_command(label="Annuler", underline=0,\
                                     command = self.undo)
        dropDownEditMenu.add_command(label="Rétablir", underline=0,\
                                     command = self.redo)
        dropDownEditMenu.add_command(label="Copier", underline=0,\
                                     command=self.copy)
        dropDownEditMenu.add_command(label="Coller", underline=0,\
                                     command=self.paste)
        
        #groundwork menu
        groundWorkMenu = tkinter.Menubutton(menu, text="Canevas")
        groundWorkMenu.pack(side="left")
        
        #drop down groundwork menu
        dropDownGroundWorkMenu = tkinter.Menu(groundWorkMenu)
                
        #menu integration
        groundWorkMenu.configure(menu = dropDownGroundWorkMenu)
        
        #adding commands
        dropDownGroundWorkMenu.add_command(label="Ajouter un titre",\
                                           underline=0,\
                                           command = self.add_title)
        dropDownGroundWorkMenu.add_command(label="Ajouter un ouvrage",\
                                           underline=0,\
                                           command = self.add_work)
        dropDownGroundWorkMenu.add_command(label="Supprimer un item",\
                                           underline=0,\
                                           command = self.remove_item)
        dropDownGroundWorkMenu.add_command(label="Détail de l'ouvrage",\
                                           underline=0,\
                                           command = self.infos)
        
        ####################
        # adding tools bar #
        ####################
        
        # adding a frame container buttons
        toolsFrame = tkinter.Frame(self.root)
        toolsFrame.grid(row=1, column=0, sticky='WN', padx=5, pady=5)
        
        # adding buttons
        self.image_down_arrow = tkinter.PhotoImage(file="./img/fleche_bas_24x24.png")
        down_arrow_button = tkinter.Button(toolsFrame,\
                                           image = self.image_down_arrow,\
                                           height=25, width=25,\
                                           relief='flat',\
                                           command = self.go_down_item)
        down_arrow_button.pack(side='left')
        
        self.image_up_arrow = tkinter.PhotoImage(file="./img/fleche_haut_24x24.png")
        up_arrow_button = tkinter.Button(toolsFrame,\
                                         image = self.image_up_arrow,\
                                         height=25, width=25,\
                                         relief='flat',\
                                         command = self.go_up_item)
        up_arrow_button.pack(side='left')
        
        self.image_right_arrow = tkinter.PhotoImage(file="./img/fleche_droite_24x24.png")
        right_arrow_button = tkinter.Button(toolsFrame,\
                                            image = self.image_right_arrow,\
                                            height=25, width=25,\
                                            relief='flat',\
                                            command = self.indenting_item)
        right_arrow_button.pack(side='left')
        
        self.image_left_arrow = tkinter.PhotoImage(file="./img/fleche_gauche_24x24.png")
        left_arrow_button = tkinter.Button(toolsFrame,\
                                           image = self.image_left_arrow,\
                                           height=25, width=25,\
                                           relief='flat',\
                                           command = self.unindent_intem)
        left_arrow_button.pack(side='left')
        
        self.image_infos = tkinter.PhotoImage(file="./img/infos_24x24.png")
        infos_button = tkinter.Button(toolsFrame,\
                                      image = self.image_infos,\
                                      height=25, width=25,\
                                      relief='flat',\
                                      command = self.infos)
        infos_button.pack(side='left')
        
        ####################
        # project treeview #
        ####################
        
        #adding a frame container treeview
        self.treeviewFrame = tkinter.Frame(self.root)
        self.treeviewFrame.grid(row=2, column=0, sticky='WENS', padx=5, pady=5)
        self.treeviewFrame.rowconfigure(0, weight=1)
        self.treeviewFrame.columnconfigure(0, weight=1)
        
        #adding treeview project
        self.treeProject = ProjectTreeview(self.treeviewFrame)
        
        #to make the treeview stretchable on the entire window
        self.treeProject.grid(row=0, column=0, sticky='WENS')
        
        #connect functions to events
        self.treeProject.bind("<Double-Button-1>", self.widget_for_editing_treeview)
        self.treeProject.bind("<Control-KeyPress-KP_8>", self.go_up_item_event)
        self.treeProject.bind("<Control-KeyPress-KP_2>", self.go_down_item_event)
        self.treeProject.bind("<Control-KeyPress-KP_6>", self.indenting_item_event)
        self.treeProject.bind("<Control-KeyPress-KP_4>", self.unindent_intem_event)
        
        #####################
        # database treeview #
        #####################
        
        #adding treeview for database
        self.treeBase = DataBaseTreeview(self.treeviewFrame)
        
        #to make the treeview stretchable on the entire window
        self.treeBase.grid(row=0, column=1, sticky='WENS')
        
        ##############
        # status bar #
        ##############
        
        #adding a frame for status bar
        statusFrame = tkinter.Frame(self.root)
        statusFrame.grid(row=3, column=0, sticky='WN', padx=5, pady=5)
        statusText = tkinter.Label(statusFrame, text="R.A.S.")
        statusText.grid(row=0, column=0, sticky='WENS')
    
    def new_project(self):
        """Create a new project instance and set the main windows title"""
        
        self.project = Project(None)
        self.project.xml.getroot()
        self.treeProject.reset_treeview()
        self.root.title("opb - sans nom")
    
    def open_project(self):
        """Open zip file, create a new project instance and transcript
           data.xml file in the treeview"""
        
        url = tkinter.filedialog.askopenfilename(filetypes=[('Fichier zip','*.zip')],\
                                                 title="Fichier de sauvegarde ...")
        self.treeProject.reset_treeview()
        self.root.title("opb - %s" %(url))
        
        #Creating a new project instance of the project module
        self.project = Project(url)
        root = self.project.xml.getroot()
        
        #Creating a list of items (checking the utility)
        self.treeProject.items = []
        
        #xml file path for representation in the treeview
        self.browse_xml_branch(root.findall("element"), "")
    
    def browse_xml_branch(self, childrensXML, parentTreeview):
        """browse xml file branch, when the node have childrens this
           fonction is recursive"""
        
        if childrensXML != []:
            for children in childrensXML:
                if children.get("id") == "lot":
                    item = self.treeProject.insert(parentTreeview,"end",\
                                                   text=children.get("name"))
                    self.treeProject.items.append(item)
                    self.browse_xml_branch(children.findall("element"), item)
                if children.get("id") == "chapitre":
                    item = self.treeProject.insert(parentTreeview,"end",\
                                                   text=children.get("name"))
                    self.treeProject.items.append(item)
                    self.browse_xml_branch(children.findall("element"), item)
                if children.get("id") == "ouvrage":
                    quant = float(lib.fonctions.evalQuantite(children.get('quant')))
                    try:
                        prix = float(children.get('prix'))
                    except:
                        prix = 0.0
                    item = self.treeProject.insert(parentTreeview,"end",\
                                                   text= children.get('name'),\
                                                   values=(children.get('descId'),\
                                                   children.get('unite'),\
                                                   quant, prix, quant*prix))
                    self.treeProject.items.append(item)
                    ouvrage = Work(item, children.get('name'),\
                                   children.get('status'),\
                                   children.get('unite'),\
                                   children.get('quant'),\
                                   prix, children.get('descId'),\
                                   children.get('loc'),\
                                   children.get('tva'),\
                                   children.get('bt'))
                    self.project.add_work(ouvrage)
    
    def save_project(self):
        """save project in zip file"""
        
        if self.project.url == None:
            self.project.url = tkinter.filedialog.asksaveasfilename(\
                               filetypes=[('Fichier zip','*.zip')],\
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
        self.browse_treeview_branch(self.treeProject.get_children(), root)
        lib.fonctions.indent(root)
        return xml
    
    def browse_treeview_branch(self, childrens, parent):
        """browse treeview branch, when the node have childrens this
           fonction is recursive"""
        
        if childrens != []:
            for children in childrens:
                work = self.project.return_work(children)
                if work == None :
                    if len(self.treeProject.parents_item(children)) != 0:
                        node = ET.SubElement(parent, "element",\
                                            id="chapitre",\
                                            name=self.treeProject.item(children)['text'])
                    else:
                        node = ET.SubElement(parent, "element",\
                                             id="lot",\
                                             name=self.treeProject.item(children)['text'])
                    self.browse_treeview_branch(self.treeProject.get_children(children), node)
                else:
                    node = ET.SubElement(parent, "element",\
                                         id="ouvrage",\
                                         name=work.name,\
                                         status=work.status,\
                                         unite=work.unite,\
                                         prix=str(work.prix),\
                                         descId=work.descId,\
                                         loc=work.loc,\
                                         bt=work.bt,\
                                         quant=work.quant,\
                                         tva=work.tva)
    
    def add_title(self):
        """Adds a new title under the item that has the focus"""
        
        select = self.treeProject.focus()
        parent = self.treeProject.parent(select)
        position = self.treeProject.index(select)+1
        item = self.treeProject.insert(parent, position, text="_Titre_")
        self.treeProject.items.append(item)
    
    def add_work(self):
        """Adds a new work under the item that has the focus"""
        
        select = self.treeProject.focus()
        parent = self.treeProject.parent(select)
        position = self.treeProject.index(select)+1
        item = self.treeProject.insert(parent, position, text="_Ouvrage_",\
                                       values=("", "", 0.0, 0.0, ""))
        self.treeProject.items.append(item)
        ouvrage = Work(item)
        self.project.add_work(ouvrage)
    
    def go_down_item(self):
        """Move down the item that has the focus when the button is
           pressed on the toolbar"""
        
        select = self.treeProject.focus()
        parent = self.treeProject.parent(select)
        position = self.treeProject.index(select)
        self.treeProject.move(select, parent, position+1)
    
    def go_down_item_event(self, event):
        """Move down the item that has the focus when the Ctrl+2 is
           pressed"""
        
        self.go_down_item()
    
    def go_up_item(self):
        """Move up the item that has the focus when the button is
           pressed on the toolbar"""
        
        select = self.treeProject.focus()
        parent = self.treeProject.parent(select)
        position = self.treeProject.index(select)
        self.treeProject.move(select, parent, position-1)
    
    def go_up_item_event(self, event):
        """Move down the item that has the focus when the Ctrl+8 is
           pressed"""
        
        self.go_up_item()
    
    def indenting_item(self):
        """Indent the item that has the focus when the button is
           pressed on the toolbar"""
        
        select = self.treeProject.focus()
        
        #if the item is a work, indentation maxi = 5
        if self.project.return_work(select) == None:
            if len(self.treeProject.parents_item()) < 4:
                previous = self.treeProject.prev(select)
                previousChildrens = self.treeProject.get_children(previous)
                self.treeProject.move(select, previous, len(previousChildrens))
        
        #if not, it's à chapter, so indentation maxi = 4
        else :
            if len(self.treeProject.parents_item()) < 3:
                previous = self.treeProject.prev(select)
                previousChildrens = self.treeProject.get_children(previous)
                self.treeProject.move(select, previous, len(previousChildrens))
    
    def indenting_item_event(self, event):
        """Indenting the item that has the focus when the Ctrl+6 is
           pressed"""
        
        self.indenting_item()
    
    def unindent_intem(self):
        """Unindent the item that has the focus when the button is
           pressed on the toolbar"""
        
        select = self.treeProject.focus()
        parent = self.treeProject.parent(select)
        grand_parent = self.treeProject.parent(parent)
        position = self.treeProject.index(parent)
        self.treeProject.move(select, grand_parent, position+1)
    
    def unindent_intem_event(self, event):
        """Unindent the item that has the focus when the Ctrl+4 is
           pressed"""
        
        self.unindent_intem()
    
    def remove_item(self):
        """Remove the item that has the focus"""
        
        select = self.treeProject.focus()
        self.treeProject.delete(select)
        self.treeProject.items.remove(select)
    
    def undo(self):
        
        pass
        # TO DO
    
    def redo(self):
        
        pass
        # TO DO
    
    def copy(self):
        """Adding the selection in the clipboard"""
        
        self.empty_clipboard()
        selection = self.treeProject.selection()
        for item in selection:
            self.clipboard.append(item)
    
    def paste(self):
        """Paste the selection under the item that has the focus"""
        
        select = self.treeProject.focus()
        self.__recursive_paste(self.clipboard, self.treeProject.parent(select),\
                            self.treeProject.index(select)+1)
    
    def __recursive_paste(self, childrens, parent, position):
        """It's a recursive used to paste selection"""
        
        if childrens != []:
            for children in childrens:
                work = self.project.return_work(children)
                if work == None :
                    item = self.treeProject.insert(parent, position,\
                                                   text= self.treeProject.item(children)['text'])
                    self.treeProject.items.append(item)
                    self.__recursive_paste(self.treeProject.get_children(children), item, "end")
                else:
                    quant = float(lib.fonctions.evalQuantite(work.quant))
                    try:
                        prix = float(work.prix)
                    except:
                        prix = 0.0
                    item = self.treeProject.insert(parent, position, text= work.name,\
                                                   values=(work.descId,\
                                                           work.unite,\
                                                           quant, prix, quant*prix))
                    self.treeProject.items.append(item)
                    newWork = Work(item, work.name,\
                                         work.status,\
                                         work.unite,\
                                         work.quant,\
                                         work.prix,\
                                         work.descId,\
                                         work.loc,\
                                         work.tva,\
                                         work.bt)
                    self.project.add_work(newWork)
    
    def empty_clipboard(self):
        """Empty the clipboard, it's used before adding a new selection"""
        
        while len(self.clipboard) != 0:
            del self.clipboard[len(self.clipboard)-1]
    
    def infos(self):
        """Open the dialog for edit the work"""
        
        select = self.treeProject.focus()
        ouvrage = self.project.return_work(select)
        if ouvrage == None :
            pass
        else :
            dialog = DialogWorkInfos(self.treeProject, select,\
                                     self.project, ouvrage)
    
    def widget_for_editing_treeview(self, event):
        """Positioning an entry on the treeview to modify a value or
           creating a dialog to modify the quantity column"""
        
        if self.treeProject.winfo_children() == []:
            pass
        else : # deleting child widgets for only one child to be active
            for widget in self.treeProject.winfo_children():
                widget.destroy()
        select = self.treeProject.focus()
        item = self.treeProject.item(select)
        column = self.treeProject.identify_column(event.x)
        position = self.treeProject.bbox(select, column=column)
        work = self.project.return_work(select)
        if column == "#0":
            text = item["text"]
            entry = EntryTreeview(self.treeProject,\
                                  position, text, column, select, work)
            self.treeProject.enfants.append(entry)
        else:
            if column == "#1":
                text = item["values"][0]
                entry = EntryTreeview(self.treeProject,\
                                      position, text, column, select, work)
                self.treeProject.enfants.append(entry)
            if column == "#2":
                text = item["values"][1]
                entry = EntryTreeview(self.treeProject,\
                                      position, text, column, select, work)
                self.treeProject.enfants.append(entry)
            if column == "#3":
                text = item["values"][2]
                entry = EntryTreeview(self.treeProject,\
                                      position, text, column, select, work)
                self.treeProject.enfants.append(entry)
            if column == "#4":
                text = item["values"][3]
                entry = EntryTreeview(self.treeProject,\
                                      position, text, column, select, work)
                self.treeProject.enfants.append(entry)


class ProjectTreeview(tkinter.ttk.Treeview):
    """Treeview of the project and associated methods"""

    def __init__(self, parentGUI):
         """Initialize treeview"""
         
         tkinter.ttk.Treeview.__init__(self, parentGUI)
         
         self.childs = []
         self.items = []
         
         self["columns"]=("IdCCTP","U" , "Q", "PU", "PT")
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
        
        if select == None:
            select = self.focus()
        
        #creation of root children list
        list = self.get_children()
        
        #creation of a tree of parents
        parentTree = []
        test = False
        
        #we check if the focus is a child of root
        for child in list:
            if child == select :
                test = True
        while test == False:
            parent = self.parent(select)
            
            #we check if the parent is a child of root
            for child in list:
                if child == parent:
                    test = True
            select = parent
            parentTree.append(parent)
        return parentTree


class DataBaseTreeview(tkinter.ttk.Treeview):
    """Treeview of the data base and associated methods"""

    def __init__(self, parentGUI):
        """Initialize treeview"""
    
        tkinter.ttk.Treeview.__init__(self, parentGUI)
        
        self.childs = []
        self.items = []
        
        self["columns"]=("IdCCTP","U", "PU")
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
        self.texteVar = tkinter.StringVar()
        self.texteVar.set(text)
        self.work = work
        
        tkinter.Entry.__init__(self, self.parent,\
                               textvariable=self.texteVar, selectborderwidth=2)
        self.place(x=position[0], y=position[1],\
                   width=position[2], height=position[3])
        
        self.bind("<Return>", self.update_item)
        self.bind("<KP_Enter>", self.update_item)
        
    def update_item(self, event):
        """Update the item"""
        
        value = self.texteVar.get()
        if self.column == "#0":
            self.parent.item(self.select, text= value)
            if self.work != None:
                self.work.name = value
        else:
            if self.column == "#1":
                self.parent.set(self.select,\
                                column=self.column, value=value)
                if self.work != None:
                    self.work.descId = value
            if self.column == "#2":
                self.parent.set(self.select,\
                                column=self.column, value=value)
                if self.work != None:
                    self.work.unite = value
            if self.column == "#3":
                try :
                    value=float(value)
                    self.parent.set(self.select,\
                                    column=self.column, value=value)
                    if self.work != None:
                        self.work.quant = str(value)
                    self.parent.set(self.select,\
                                    column="#5",\
                                    value = value * float(self.parent.item(self.select)['values'][3]))
                except:
                    tkinter.messagebox.showwarning("Erreur de saisie", "La valeur saisie doit être un nombre")
            if self.column == "#4":
                try :
                    value=float(value)
                    self.parent.set(self.select,\
                                    column=self.column, value=value)
                    if self.work != None:
                        self.work.prix = value
                    self.parent.set(self.select,\
                                    column="#5",\
                                    value = value * float(self.parent.item(self.select)['values'][2]))
                except:
                    tkinter.messagebox.showwarning("Erreur de saisie", "La valeur saisie doit être un nombre")
        self.destroy()


class DialogWorkInfos(tkinter.Toplevel):
    """Dialog for edit and update work"""
    
    def __init__(self, parent, indexItem, project, work):
        """Initialize dialog"""
        
        self.project = project
        self.work = work
        self.parent = parent # It's the treeview
        self.indexItem = indexItem #It's the index of the item selected in the treeview
        
        tkinter.Toplevel.__init__(self, self.parent)
        self.resizable(width=False, height=False)
        self.transient(self.master) # pour ne pas creer de nouvel icone dans la barre de lancement
        #self.overrideredirect(1) # pour enlever le bandeau supérieur propre a l os
        
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        notebook = tkinter.ttk.Notebook(self)
        notebook.grid(row=0, column=0, sticky="WNES", padx=5, pady=5)
        
        self.pageWorkInfos = DialogDesc(self, indexItem, self.project, self.work)
        self.pageWorkQuantity = DialogQt(self, indexItem, self.work)
        
        notebook.add(self.pageWorkInfos, text = 'Description')
        notebook.add(self.pageWorkQuantity, text = 'Quantité')
        
        bottomFrame = tkinter.Frame(self, padx=2, pady=2)
        bottomFrame.grid(row=1, column=0, columnspan=2, sticky="EW")
        
        buttonValidate = tkinter.Button(bottomFrame, text="Valider",\
                                        height=1, width=10,\
                                        command = self.validate)
        buttonValidate.pack(side="right")
        
        buttonCancel = tkinter.Button(bottomFrame, text="Annuler",\
                                      height=1, width=10,\
                                      command = self.cancel)
        buttonCancel.pack(side="right")
    
    def update_work_quantity(self):
        """Update the work quantity"""
        
        text = self.pageWorkQuantity.zoneTexte.get('0.0', 'end')
        list = text.split("\n")
        quantity = ""
        for line in list:
            if line == "":
                pass
            else:
                quantity = quantity + "%s$" %(line)
        #deleting the last character ;
        quantity = quantity[:len(quantity)-1]
        
        result = lib.fonctions.evalQuantite(quantity)
        self.work.quant = quantity
        self.parent.set(self.indexItem,\
                        column="#3",\
                        value=float(result))
        self.parent.set(self.indexItem,\
                        column="#5",\
                        value = float(result) * float(self.parent.item(self.indexItem)['values'][3]))
    
    def update_work_infos(self):
        """Update the work infos"""
        
        #update the name of work
        name = self.pageWorkInfos.textVarTitle.get()
        self.work.name = name
        self.parent.item(self.indexItem, text=name)
        
        #update the description Id of work
        descId = self.pageWorkInfos.textVarId.get()
        self.work.descId = descId
        self.parent.set(self.indexItem, column="#1", value=descId)
        
        #update the status of work
        status = self.pageWorkInfos.choiceBaseOption.get()
        self.work.status = status
        
        #update the VAT rate of work
        vatRate = self.pageWorkInfos.choiceVATrate.get()
        self.work.tva = vatRate
        
        #update the index BT of work
        bt = self.pageWorkInfos.choiceIndexBT.get()
        self.work.bt = bt
        
        #update the localisation of work
        text = self.pageWorkInfos.zoneText.get('0.0', 'end')
        list = text.split("\n")
        localisation = ""
        for line in list:
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

#################################################################################################################################
class DialogDesc(tkinter.Frame):
    
    def __init__(self, parent, select, affaire, ouvrage):
        
        self.project = affaire
        self.ouvrage = ouvrage
        self.parent = parent
        self.select = select
        self.textVarTitle = tkinter.StringVar()
        self.textVarTitle.set(self.ouvrage.name)
        self.textVarId = tkinter.StringVar()
        self.textVarId.set(self.ouvrage.descId)
        
        tkinter.Frame.__init__(self, self.parent, padx=2, pady=2)
        self.grid(row=0, column=0, sticky="WNES", padx=5, pady=5)
        
        self.labelTitle = tkinter.Label(self, text= "Titre", justify="left")
        self.labelTitle.grid(row=0, column=0, padx=5, pady=10, sticky="W")
        
        self.entryTitle = tkinter.Entry(self, textvariable=self.textVarTitle, selectborderwidth=0)
        self.entryTitle.grid(row=1, column=0, columnspan=3, sticky="WE")
        
        self.buttonCCTP = tkinter.Button(self, text="CCTP", height=1, width=10, command = self.openCCTP)
        self.buttonCCTP.grid(row=1, column=3, columnspan=2, padx=10, sticky="WE")
        
        self.labelId = tkinter.Label(self, text= "Identifiant", justify="center")
        self.labelId.grid(row=2, column=0, padx=5, pady=10, sticky="WE")
        
        self.entryId = tkinter.Entry(self, textvariable=self.textVarId, selectborderwidth=0, width=10)
        self.entryId.grid(row=3, column=0, sticky="WE")
        
        self.labelOption = tkinter.Label(self, text= "Base/Option", justify="center")
        self.labelOption.grid(row=2, column=1, padx=5, pady=10, sticky="WE")
        
        self.choiceBaseOption = tkinter.StringVar()
        self.tupleBaseOption = ("Base", "Option")
        self.comboBaseOption = tkinter.ttk.Combobox(self, textvariable = self.choiceBaseOption, values = self.tupleBaseOption, width=10, state = "readonly")
        if self.ouvrage.status == "" or self.ouvrage.status != self.tupleBaseOption[0] or self.ouvrage.status != self.tupleBaseOption[0]:
            self.choiceBaseOption.set("Base")
        else:
            self.choiceBaseOption.set(self.ouvrage.status)
        self.comboBaseOption.grid(row =3, column =1, padx=5, pady=5, sticky="EW")
        
        self.labelTVA = tkinter.Label(self, text= "TVA", justify="center")
        self.labelTVA.grid(row=2, column=2, padx=5, pady=10, sticky="WE")
        
        self.choiceVATrate = tkinter.StringVar()
        self.comboTVA = tkinter.ttk.Combobox(self, textvariable = self.choiceVATrate, width=10, values = lib.constantes.TVA, state = "readonly")
        self.comboTVA.grid(row =3, column =2, padx=5, pady=5, sticky="EW")
        if self.ouvrage.tva == "" or self.ouvrage.tva != lib.constantes.TVA[0] or self.ouvrage.tva != lib.constantes.TVA[1] or self.ouvrage.tva != lib.constantes.TVA[2] :
            self.choiceVATrate.set(lib.constantes.TVA[2])
        else:
            self.choiceVATrate.set(self.ouvrage.tva)        
        
        self.labelIndexBT = tkinter.Label(self, text= "Index BT", justify="center")
        self.labelIndexBT.grid(row=2, column=3, columnspan=2, padx=5, pady=10, sticky="WE")
        
        self.choiceIndexBT = tkinter.StringVar()
        self.comboIndexBT = tkinter.ttk.Combobox(self, textvariable = self.choiceIndexBT, values = lib.constantes.INDEXBT, width=10, state = "readonly")
        self.comboIndexBT.grid(row =3, column =3, columnspan=2, padx=5, pady=5, sticky="EW")
        if self.ouvrage.bt == "" :
            self.choiceIndexBT.set(lib.constantes.INDEXBT[0])
        else :
            for bt in lib.constantes.INDEXBT:
                if self.ouvrage.bt == bt:
                    self.choiceIndexBT.set(bt)
                    break
                else:
                    self.choiceIndexBT.set(lib.constantes.INDEXBT[0])
        
        self.labelLocalisation = tkinter.Label(self, text= "Localisation", justify="left")
        self.labelLocalisation.grid(row=4, column=0, padx=5, pady=15, sticky="W")
            
        self.zoneText = tkinter.Text(self, padx=2, pady=2, height=12, relief= "flat", highlightthickness= 0)
        self.zoneText_scroll = tkinter.Scrollbar(self, command = self.zoneText.yview, relief="flat")
        self.zoneText.configure(yscrollcommand =self.zoneText_scroll.set)
        self.zoneText.grid(row=5, column=0, columnspan=4, sticky="WNES")
        self.zoneText_scroll.grid(row=5, column=4, sticky="NS")
        
        if self.ouvrage.loc == None:
            pass
        else:
            s = self.ouvrage.loc.split("$")
            for line in s:
                self.zoneText.insert("end", "%s\n" %(line))
                self.zoneText.yview("moveto", 1)
    
    def openCCTP(self):
        if self.textVarId.get() == "":
            tkinter.messagebox.showwarning("Attention", "Veuillez saisir un identifiant pour l'ouvrage")
        else:
            try:
                os.mkdir(os.getcwd() + "/temp/ref")
            except:
                pass
            files = os.listdir(os.getcwd() + "/temp/ref")
            test= False
            for file in files:
                split = file.split("/")
                fileOdt = split[-1]
                if fileOdt[0:-4] == self.textVarId.get():
                    if sys.platform == 'win32':
                        description = os.system('start ' + lib.constantes.SOFFICEPATH + " " + os.getcwd() + "\\temp\\ref\\"+ fileOdt)
                    else:
                        description = os.system('soffice %s' %(os.getcwd() + "/temp/ref/"+ fileOdt))
                    test= True
                    break
            if test == False:
                shutil.copy(os.getcwd() + "/templates/workTemplate.odt", os.getcwd() + "/temp/ref/"+ self.textVarId.get() + ".odt")
                if sys.platform == 'win32':
                    description = os.system('start ' + lib.constantes.SOFFICEPATH + " " + os.getcwd() + "\\temp\\ref\\"+ self.textVarId.get() + ".odt")
                else:
                    description = os.system('soffice %s' %(os.getcwd() + "/temp/ref/"+ self.textVarId.get() + ".odt"))
        
        

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
            s = self.ouvrage.quant.split("$")
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
            resultat = lib.fonctions.evalQuantite(self.ouvrage.quant)
            self.texteVar.set("Total = %s %s" % (resultat, unite))
        
        self.parent.bind("<KeyPress-F9>", self._miseAjourQt)
        self.parent.bind("<Return>", self._miseAjourQt)
    
    def _miseAjourQt(self, event):
        texte = self.zoneTexte.get('0.0', 'end')
        list = texte.split("\n")
        quantite = ""
        for ligne in list:
            quantite = quantite + "%s$" %(ligne)
        total = lib.fonctions.evalQuantite(quantite)
        self.texteVar.set("Total = %s %s" % (total, self.ouvrage.unite))
        
        

if __name__ == '__main__':
    Application = Main()
    #Application.nouvelleAffaire()
    #Application.root.option_readfile("gui.cfg", priority=40)
    Application.root.mainloop()



# to do
# couper/coller
# documenter et nettoyer le code
# implementer la lecture des fichiers dxf dans l evaluation des quantites
# voir pour creation d une pile undo/redo
# ajouter une fonction pour connaitre l etat d enregistrement afin de proposer l enregistrement avant de quitter, creer un nouveau document ou ouvrir un autre document
# bug : lorsque qu'un nouveau fichier est créé puis enregistré sous, lors des enregistrements suivants c'est la fenêtre enregistrer sous qui s'ouvre, le programme ne dois pas savoir quel est le nom de fichier à enregistrer, à voir...
# voir pour ajouter dans data.xml la possibilite d ajouter des varaintes par lot
# voir pour ajouter dans data.xml le coefficient de marge pour les estimations
# voir pour fichier base de donnee configuration de l application
# rendre impossible l'indentation d'un titre après un ouvrage


