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

        ####################
        # project treeview #
        ####################

        #adding a frame container treeview
        tree_frame = tkinter.Frame(self.root)
        tree_frame.grid(row=2, column=0, sticky='WENS', padx=5, pady=5)
        tree_frame.rowconfigure(1, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        #adding treeview project
        self.tree_project = gui.treeview.ProjectTreeview(self, tree_frame)

        #to make the treeview stretchable on the entire window
        self.tree_project.grid(row=0, rowspan=2, column=0, sticky='WENS')

        #connect functions to events
        self.tree_project.bind("<Double-Button-1>", self.__widget_for_editing_treeview)
        self.tree_project.bind("<Control-KeyPress-KP_8>", self.tree_project.go_up_item_event)
        self.tree_project.bind("<Control-KeyPress-KP_2>", self.tree_project.go_down_item_event)
        self.tree_project.bind("<Control-KeyPress-KP_6>", self.__indenting_item_event)
        self.tree_project.bind("<Control-KeyPress-KP_4>", self.__unindent_item_event)

        #####################
        # database treeview #
        #####################
        
        #adding treeview for database
        self.tree_base = gui.treeview.DataBaseTreeview(tree_frame)

        #to make the treeview stretchable on the entire window
        #self.tree_base.grid(row=1, column=1, sticky='WENS')
        
        ##############
        # status bar #
        ##############

        #adding a frame for status bar
        status_frame = tkinter.Frame(self.root)
        status_frame.grid(row=3, column=0, sticky='WN', padx=5, pady=5)
        self.total_price_project = tkinter.StringVar()
        self.total_price_project_label = tkinter.Label(status_frame, textvariable=self.total_price_project)
        self.total_price_project_label.grid(row=0, column=0, sticky='WENS')

        ########
        # menu #
        ########

        # adding menu
        MenuBar(self, self.root)

        # adding tools bar
        ToolBar(self, self.root)

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
        xml = self.__groundwork_to_xml_object()
        self.modifications_dictionary['undo'].append(xml)

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
                    if self.tree_project.item(children)['open'] is True\
                    or self.tree_project.item(children)['open'] == 1:
                        displayed = "true"
                    else:
                        displayed = "false"
                    if len(self.tree_project.parents_item(children)) != 0:
                        node = ET.SubElement(parent, "element", id="chapter", open=displayed)
                        name = ET.SubElement(node, "name")
                        name.text = self.tree_project.item(children)['text']
                    else:
                        node = ET.SubElement(parent, "element", id="batch", open=displayed)
                        name = ET.SubElement(node, "name")
                        name.text = self.tree_project.item(children)['text']
                    self.__browse_treeview_branch(self.tree_project.get_children(children), node)
                else:
                    node = ET.SubElement(parent, "element", id="work")
                    name = ET.SubElement(node, "name")
                    name.text = work['name']
                    code = ET.SubElement(node, "code")
                    code.text = work['code']
                    if work['description'] is None:
                        description = ET.SubElement(node, "description")
                    else:
                        node.append(work['description'])
                    localisation = ET.SubElement(node, "localisation")
                    localisation.text = work['localisation']
                    index = ET.SubElement(node, "index")
                    index.text = work['index']
                    price = ET.SubElement(node, "price")
                    price.text = (work['price'])
                    if work['quantity'] is None:
                        quantity = ET.SubElement(node, "quantity")
                    else:
                        node.append(work['quantity'])
                    status = ET.SubElement(node, "status")
                    status.text = work['status']
                    vat = ET.SubElement(node, "vat")
                    vat.text = work['vat']
                    unit = ET.SubElement(node, "unit")
                    unit.text = work['unit']

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
        work = {}
        work['iid'] = item
        work['name'] = "_Ouvrage_"
        work['code'] = ""
        work['description'] = ""
        work['localisation'] = ""
        work['index'] = "BT01"
        work['price'] = "0.00"
        work['quantity'] = ""
        work['status'] = "base"
        work['vat'] = "20.0"
        work['unit'] = ""
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

        for item in self.tree_project.selection():
            self.tree_project.delete(item)
            self.tree_project.items.remove(item)
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

        try:
            _id = len(self.modifications_dictionary['redo'])-1
            xml_restored = self.modifications_dictionary['redo'][_id]
            self.modifications_dictionary['undo'].append(xml_restored)
            del self.modifications_dictionary['redo'][_id]
            self.tree_project.refresh(self, xml_restored)
        except IndexError:
            print("Recovery not possible : the redo list is empty")

    def cut(self):
        """Adding selection in the clipboard and deleting items in the treeview"""

        self.__empty_clipboard()
        xml = ET.ElementTree(ET.fromstring(lib.constantes.XMLSELECTION))
        root = xml.getroot()
        self.__browse_treeview_branch(self.tree_project.selection(), root)
        self.clipboard.append(xml)
        for item in self.tree_project.selection():
            self.tree_project.delete(item)
            self.tree_project.items.remove(item)
        self.clipboard.append(xml)

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
        self.tree_project.browse_xml_branch(xml.findall("element"), self.tree_project.parent(select),\
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
            self.add_modification()

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
            entry = gui.treeview.EntryTreeview(self, text, column)
            self.tree_project.childs.append(entry)
        else:
            if column == "#1":
                text = item["values"][0]
                entry = gui.treeview.EntryTreeview(self, text, column)
                self.tree_project.childs.append(entry)
            if column == "#2":
                text = item["values"][1]
                entry = gui.treeview.EntryTreeview(self, text, column)
                self.tree_project.childs.append(entry)
            if column == "#3":
                text = item["values"][2]
                entry = gui.treeview.EntryTreeview(self, text, column)
                self.tree_project.childs.append(entry)
            if column == "#4":
                text = item["values"][3]
                entry = gui.treeview.EntryTreeview(self, text, column)
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
        self.__add_display_menu()
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
        drop_down_edit_menu.add_command(label="Couper", underline=0,\
                                     command=self.application.cut)
        drop_down_edit_menu.add_command(label="Copier", underline=0,\
                                     command=self.application.copy)
        drop_down_edit_menu.add_command(label="Coller", underline=0,\
                                     command=self.application.paste)
        
        #adding the drop_down_edit_menu to the menu bar
        self.menu_bar.add_cascade(label="Edition", menu=drop_down_edit_menu)
    
    def __add_display_menu(self):
        """Adding display menu in the menu bar"""

        #drop down edit menu
        drop_down_display_menu = tkinter.Menu(self.menu_bar)

        #adding commands
        drop_down_display_menu.add_command(label="Masquer le panneau latéral", underline=0,\
                                           command=self.application.tree_base.hide_treeview)
        drop_down_display_menu.add_command(label="Afficher le panneau latéral", underline=0,\
                                           command=self.application.tree_base.show_treeview)

        #adding the drop_down_display_menu to the menu bar
        self.menu_bar.add_cascade(label="Affichage", menu=drop_down_display_menu)

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
        self.__add_button(self.application.image_down_arrow, self.application.tree_project.go_down_item)
        self.application.image_up_arrow = tkinter.PhotoImage(file="./img/fleche_haut_24x24.png")
        self.__add_button(self.application.image_up_arrow, self.application.tree_project.go_up_item)
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
        self.works = []

    def add_work(self, work):
        """Adding dictionary work in works list"""
        self.works.append(work)

    def return_work(self, iid):
        """Returns the dictionary of the work if the index given in argument was found in the list of works"""
        test = None
        for work in self.works:
            if work['iid'] == iid:
                test = work
                break
        return test
    
    def total_price_project(self):
        """Calculation the total price of the project without VAT"""
        total = 0.00
        for work in self.works:
            if work['quantity'] is None:
                pass
            elif work['price'] is None:
                pass
            else:
                total = total + float(work['price'])*float(lib.fonctions.evalQuantiteNew(work['quantity']))
        return total

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

if __name__ == '__main__':
    APPLICATION = Main()
    APPLICATION.root.mainloop()



# to do
# implementer la lecture des fichiers dxf dans l evaluation des quantites
# voir pour ajouter dans data.xml la possibilite d ajouter des variantes par lot
# voir pour ajouter dans data.xml le coefficient de marge pour les estimations
# rendre impossible l'indentation d'un titre après un ouvrage
# sur le treeview, prévoir contrôle pour vérifier qu'une description et une localisation sont bien associées à un ouvrage


