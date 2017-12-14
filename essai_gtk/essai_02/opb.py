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
import math
import decimal
import zipfile
import xml.etree.ElementTree as ET
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def eval_quantity(text):
    """eval quantity text and return a float"""
    # definition of mathematical variables for interpretation by eval
    pi = math.pi
    # calculation of the quantity
    try:
        text_split = text.split("$")
        total = 0.0
        for line in text_split:
            if line == "":
                pass
            else:
                if line[0] == "#":
                    pass
                else:
                    sub_total = eval(line)
                    total = total + sub_total
        total_rounded = decimal.Decimal(str(total)).quantize(decimal.Decimal('0.001'),\
                                        rounding='ROUND_HALF_UP')
        return total_rounded
    except AttributeError:
        return str(0.0)

class TreeStore(Gtk.TreeStore):
    """Contain the data for show in the treeview project"""

    def __init__(self, xml):
        Gtk.TreeStore.__init__(self, str, str, str, str, str, str, str, str, str, str, str, str)
        # ID / NAME / CODE / DESCRIPTION / LOCALISATION / INDEX / PRICE
        # QUANTITY / TOTAL / STATUS / VAT / UNIT
        groundwork = xml.find("groundwork")
        self.__browse_xml_branch(groundwork.findall("element"), "")

    def __browse_xml_branch(self, childrens_xml, parent_tree):
        """browse xml file branch, when the node have childrens this
           fonction is recursive"""

        if childrens_xml != []:
            for children in childrens_xml:
                if children.get("id") == "batch":
                    item = self.append(None, ['batch',\
                                              children.find("name").text,\
                                              None,\
                                              None,\
                                              None,\
                                              None,\
                                              None,\
                                              None,\
                                              None,\
                                              None,\
                                              None,\
                                              None])
                    self.__browse_xml_branch(children.findall("element"), item)
                if children.get("id") == "chapter":
                    item = self.append(parent_tree, ['chapter',\
                                                     children.find("name").text,\
                                                     None,\
                                                     None,\
                                                     None,\
                                                     None,\
                                                     None,\
                                                     None,\
                                                     None,\
                                                     None,\
                                                     None,\
                                                     None])
                    self.__browse_xml_branch(children.findall("element"), item)
                if children.get("id") == "work":
                    item = self.append(parent_tree, ['work',\
                                              children.find("name").text,\
                                              children.find('code').text,\
                                              children.find('description').text,\
                                              children.find('localisation').text,\
                                              children.find('index').text,\
                                              str(children.find('price').text),\
                                              str(eval_quantity(children.find('quantity').text)),\
                                              str(float(eval_quantity(children.find('quantity').text))\
                                                  * float(children.find('price').text)),\
                                              children.find('status').text,\
                                              children.find('vat').text,\
                                              children.find('unit').text])

class TreeColumn(Gtk.TreeViewColumn):
    """This is the class for create a column in a treeview"""

    def __init__(self, treeview, tree_model, attributes):
        """Initialize the column"""
        self.tree_model = tree_model
        self.attributes = attributes
        Gtk.TreeViewColumn.__init__(self, self.attributes['name'])
        treeview.append_column(self)
        cell = Gtk.CellRendererText()
        cell.set_property("height", self.attributes['height'])
        cell.set_property("width", self.attributes['width'])
        cell.set_property("editable", self.attributes['editable'])
        cell.connect("edited", self.text_edited)
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', self.attributes['column_tree_model'])

    def text_edited(self, widget, path, text):
        self.tree_model[path][self.attributes['column_tree_model']] = text


class TreeProject(Gtk.TreeView):
    """This is the class for the treeview project"""

    def __init__(self, application, xml):
        """Initialize the treeview"""
        self.tree_model = TreeStore(xml)
        Gtk.TreeView.__init__(self, self.tree_model)
        application.box.pack_start(self, True, True, 0)
        self.column_description = TreeColumn(self, self.tree_model,\
                                  {"name": "Description",\
                                  "height": 25,\
                                  "width": 400,\
                                  "editable": True,\
                                  "column_tree_model": 1})
        self.column_unit = TreeColumn(self, self.tree_model,\
                                  {"name": "Unité",\
                                  "height": 25,\
                                  "width": 100,\
                                  "editable": True,\
                                  "column_tree_model": 11})
        self.column_quantity = TreeColumn(self, self.tree_model,\
                                  {"name": "Quantité",\
                                  "height": 25,\
                                  "width": 150,\
                                  "editable": True,\
                                  "column_tree_model": 7})
        self.column_price = TreeColumn(self, self.tree_model,\
                                  {"name": "Prix",\
                                  "height": 25,\
                                  "width": 150,\
                                  "editable": True,\
                                  "column_tree_model": 6})
        self.column_total = TreeColumn(self, self.tree_model,\
                                  {"name": "Total",\
                                  "height": 25,\
                                  "width": 150,\
                                  "editable": True,\
                                  "column_tree_model": 8})
        application.window.show_all()

class Application(object):
    """This is the main window of the application"""

    def __init__(self):
        """Initialize application"""
        builder = Gtk.Builder()
        builder.add_from_file("main.glade")
        self.window = builder.get_object("applicationwindow")
        self.box = builder.get_object("hbox")
        self.tree_project = None
        builder.connect_signals(self)
        self.window.show_all()

    def open_file(self, widget):
        """open existing project"""
        dialog = Gtk.FileChooserDialog(title="Choisir un fichier à ouvrir...",\
                                       action=Gtk.FileChooserAction.OPEN,\
                                       buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,\
                                       Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            fichier_zip = zipfile.ZipFile(dialog.get_filename(), "r")
            fichier_zip.extractall("./temp")
            fichier_zip.close()
            xml = ET.parse("./temp/data.xml")
            self.tree_project = TreeProject(self, xml)
        elif response == Gtk.ResponseType.CANCEL:
            pass
        dialog.destroy()

    def go_down(self, widget):
        """Move down the item that has the focus when the button is
           pressed on the toolbar"""
        selection = self.tree_project.get_selection()
        treeiter_a = selection.get_selected()
        print(treeiter_a)
        treeiter_b = self.tree_project.tree_model.iter_next(treeiter_a)
        self.tree_projet.tree_model.swap(treeiter_a, treeiter_b)
        


if __name__ == '__main__':
    application = Application()
    Gtk.main()
