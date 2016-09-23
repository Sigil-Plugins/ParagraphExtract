#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, absolute_import, print_function

try:
    from sigil_bs4 import BeautifulSoup
except:
    from bs4 import BeautifulSoup
import sys, urllib
import xml.etree.ElementTree as ET
import socket

PY2 = sys.version_info[0] == 2

if PY2:
    from Tkinter import Tk, BOTH, StringVar, IntVar, BooleanVar 
    from ttk import Frame, Button, Style, Label, Entry, Checkbutton
else:
    from tkinter import Tk, BOTH, StringVar, IntVar, BooleanVar 
    from tkinter.ttk import Frame, Button, Style, Label, Entry, Checkbutton

import re, os, inspect
iswindows = sys.platform.startswith('win')


class Dialog(Frame):
    global parameters
    parameters = {}

    def __init__(self, parent):
        # display the dialog box
        Frame.__init__(self, parent)   
        self.parent = parent
        self.initUI()

    def savevalues(self):
        fileName = self.fileName.get()
        if(fileName.endswith("xhtml") or fileName.endswith("html")):
            parameters['fileName'] = fileName
        else:
            parameters['fileName'] = fileName + ".xhtml"
        parameters['search'] = self.search.get()
        parameters['regex'] = self.UseRegex.get()
        self.master.destroy()
        
    def initUI(self):
        # define dialog box properties
        self.parent.title("ParagraphExtract")
        self.style = Style()
        # 'winnative', 'vista', 'xpnative' / 'clam', 'alt', 'default', 'classic'
        if iswindows:
            if 'xpnative' in self.style.theme_names():
                self.style.theme_use('xpnative')
            else:
                self.style.theme_use('default')
        else:
            self.style.theme_use('default')
        self.pack(fill=BOTH, expand=1)

       
        # tag attribute (optional)
        fileNameLabel = Label(self, text="Filename: ")
        fileNameLabel.place(x=10, y=10)
        self.fileName=StringVar(None)
        fileNameEntry=Entry(self, textvariable=self.fileName)
        fileNameEntry.place(x=70, y=10, width=230)
        # tag attribute value (optional)
        valueLabel = Label(self, text="Search: ")
        valueLabel.place(x=10, y=30)
        self.search=StringVar(None)
        searchEntry=Entry(self, textvariable=self.search)
        searchEntry.place(x=70, y=30, width=230)
        
        # Use Roman numerals check button
        self.UseRegex=BooleanVar(None)
        self.UseRegex.set(False)
        regexCheckbutton = Checkbutton(self, text="Use Regex", variable=self.UseRegex)
        regexCheckbutton.place(x=70, y=60)
        # OK and Cancel buttons
        cancelButton = Button(self, text="Cancel", command=self.quit)
        cancelButton.place(x=160, y=80)
        okButton = Button(self, text="OK", command=self.savevalues)
        okButton.place(x=70, y=80)

def run(bk):
    
    # set Tk parameters for dialog box
    root = Tk()
    root.geometry("320x110+300+300")
    # get plugin path (/sigil-ebook/sigil/plugins/)
    if iswindows:
        icon_path = os.path.join(bk._w.plugin_dir, 'ParagraphExtract', 'app.ico')
        root.wm_iconbitmap(icon_path)
    app = Dialog(root)
    root.mainloop()
    
    if parameters and len(parameters) > 1:
        #new file
        print(parameters['regex'])
        lastid = 0
        fnid = 0
        notes = '<?xml version="1.0" encoding="utf-8"?>\n'
        notes += '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"\n'
        notes += '"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n'
        notes += '<html xmlns="http://www.w3.org/1999/xhtml">\n'
        notes += '<head>\n'
        notes += '</head>\n'
        notes += '<body>\n'

        #get search string
        regexStr = parameters['search']
        regexStr = '<p>' + regexStr + '</p>';
        if parameters['regex']:
            regex = r"%s" % regexStr
        else:
            regex = regexStr
        print(regexStr)

        #get filename
        fileName = parameters['fileName']   
       
        # select files to be processed
        selected_files = []
        for file_name in list(bk.selected_iter()):
            if bk.id_to_mime(file_name[1]) == 'application/xhtml+xml':
                selected_files.append((file_name[1], bk.id_to_href(file_name[1]))) 
                
        all_files = list(bk.text_iter())

        if selected_files != []:
            print('Processing only selected files...\n')
            file_list = selected_files
        else:
            print('Processing all files...\n')
            file_list = all_files
        
        # process file list
        for (html_id, href) in file_list:
            html = bk.readfile(html_id)
            html_origin = html
            #regex = r'<p>\[(\d+)\] (.*?)</p>'
            found = re.search(regex, html)
            if found is not None:
                while found is not None:
                    fnid += 1
                    html= re.sub(regex, '', html, 1)
                    print (found.group(0))
                    notes += '  ' + found.group(0) + '\n\n'
                    found = re.search(regex, html)
            if not html == html_origin:
                bk.writefile(html_id, html)

        #write file
        if fnid > 0:
            notes += '</body>\n' + '</html>'
            uid = parameters['fileName']
            mime = "application/xhtml+xml"
            bk.addfile(uid, fileName, notes, mime)
            if uid in bk._w.id_to_mime.keys():
                print("Successfully added a file")

            # example of adding it to the end of the spine
            #bk.spine_insert_before(-1, uid, "yes")
            new_spine = bk.getspine()
            new_spine.append((uid,"yes"))
            bk.setspine(new_spine)
            
        
    # no values entered in dialog box
    else:
        print('No values selected.')
      
        
    print('\nPlease click OK to close the Plugin Runner window.')
    
    return 0


def main():
    print('I reached main when I should not have\n')
    return -1

if __name__ == "__main__":
    sys.exit(main())
