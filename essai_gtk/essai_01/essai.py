#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  essai.py
#  
#  Copyright 2017 jmcherel <jmcherel@PC_ASUSPRO>
#  
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
#  
#  

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def main():
	builder = Gtk.Builder()
	builder.add_from_file("glade/main.glade")
	window = builder.get_object("window1")
	treestore = Gtk.TreeStore(str, str)
	iter0 = treestore.append(None, ["Nom", "Prénom"])
	iter1 = treestore.append(iter0, ["Nom", "Prénom"])
	tree = builder.get_object("treeview1")
	tree.set_model(treestore)
		
	column = Gtk.TreeViewColumn("Title and Author")
	title = Gtk.CellRendererText()
	author = Gtk.CellRendererText()
	column.pack_start(title, True)
	column.pack_start(author, True)
	column.add_attribute(title, "text", 0)
	column.add_attribute(author, "text", 1)
	tree.append_column(column)
	
	window.show_all()
	Gtk.main()
    

if __name__ == '__main__':
    main()
