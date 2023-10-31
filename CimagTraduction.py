# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 18:16:04 2023

@author: ppagaud
"""

import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

import xml.etree.ElementTree as ET
import deep_translator
import pandas as pd
import re
        

class tkFct():
    
    def traduction():
        
        messagebox.showinfo("Fichier à traduire","Sélectionnez le fichier TMX à traduire.")
        tmx_old = filedialog.askopenfilename(filetypes=[('Fichiers TMX', '.tmx')])
        if tmx_old == "": return
        
        messagebox.showinfo("Nouveau fichier","Saisir l'emplacement et le nom du fichier TMX qui sera enregistré après la traduction.")
        tmx_new = filedialog.asksaveasfilename(filetypes=[('Fichiers TMX', '.tmx')])
        if tmx_new == "": return
        
        if tmx_new[-4:] != ".tmx": tmx_new += ".tmx"
        
        child_w= tkinter.Toplevel(window)
        child_w.title("Sélection de la langue")
        label_child = tkinter.Label(child_w, text= "Sléectionnez la langue cible :")
        label_child.pack()
        current_var = tkinter.StringVar()
        combo_child = ttk.Combobox(child_w, textvariable=current_var)
        combo_child['values'] = ('BG - Bulgarian',
                                 'CS - Czech',
                                 'DA - Danish',
                                 'DE - German',
                                 'EL - Greek',
                                 'EN - English',
                                 'ES - Spanish',
                                 'ET - Estonian',
                                 'FI - Finnish',
                                 'FR - French',
                                 'HU - Hungarian',
                                 'ID - Indonesian',
                                 'IT - Italian',
                                 'JA - Japanese',
                                 'KO - Korean',
                                 'LT - Lithuanian',
                                 'LV - Latvian',
                                 'NB - Norwegian (Bokmål)',
                                 'NL - Dutch',
                                 'PL - Polish',
                                 'PT - Portuguese',
                                 'RO - Romanian',
                                 'RU - Russian',
                                 'SK - Slovak',
                                 'SL - Slovenian',
                                 'SV - Swedish',
                                 'TR - Turkish',
                                 'UK - Ukrainian',
                                 'ZH - Chinese')
        combo_child.pack()
        btn_ok = tkinter.Button(child_w, text = "OK", command=child_w.destroy)
        btn_ok.pack()
        
        window.wait_window(child_w)
        
        langChoix = current_var.get().split(" - ")[0].lower()
        
        tree = ET.parse(tmx_old)
        root = tree.getroot()[0]
        
        i=0

        for prop in root:
            
            i += 1
            
            tradEn = False
            tradChoix = False
            
            # 1 - Traduction de la langue détectée
            for child in prop:
                if list(child.attrib.keys())[0] == '{http://www.w3.org/XML/1998/namespace}lang':
                    
                    langDetect = list(child.attrib.values())[0].split("-")[0].lower()
                    if langDetect == "en": tradEn = True
                    if langDetect == langChoix: tradChoix = True
                    
                    if child[0].text != "":
                        traduction = deep_translator.GoogleTranslator(source='auto', target=langDetect).translate(prop[0].text)
                        child[0].text = traduction
                    
            # 2 - Traduction de la partie EN si pas encore faite
            if tradEn == False:
                traduction = deep_translator.GoogleTranslator(source='auto', target='en').translate(prop[0].text)
                child = ET.Element("tuv",{'{http://www.w3.org/XML/1998/namespace}lang':"EN-US"})
                prop.append(child)
                grandchild = ET.Element("seg")
                grandchild.text = traduction
                child.append(grandchild)
                
            # 3 - Traduction dans la langue choisie si pas encore faite
            if tradChoix == False:
                traduction = deep_translator.GoogleTranslator(source='auto', target=langChoix).translate(prop[0].text)
                child = ET.Element("tuv",{'{http://www.w3.org/XML/1998/namespace}lang':langChoix.upper()+"-"+langChoix.upper()})
                prop.append(child)
                grandchild = ET.Element("seg")
                grandchild.text = traduction
                child.append(grandchild)
                
            print(str(i) + " / " + str(len(root)) + " (" + str(int(i/len(root))) + "%)")

        ET.indent(tree)
        with open(tmx_new, 'wb'):
            tree.write(tmx_new, encoding="UTF-8", xml_declaration=True)
        
        messagebox.showinfo("Opération terminée","Le fichier traduit est enregistré à l'emplacement : " + tmx_new)
        
    def tmx_vers_csv():
        cols = ["Trad (FR-FR)"]
        rows = []

        messagebox.showinfo("Fichier TMX","Sélectionnez le fichier TMX à exporter en CSV.")
        tmx_file = filedialog.askopenfilename(filetypes=[('Fichiers TMX', '.tmx')])
        if tmx_file == "": return
        
        messagebox.showinfo("Nouveau fichier CSV","Saisir l'emplacement et le nom du fichier CSV qui sera exporté à partir du fichier XLM.")
        csv_file = filedialog.asksaveasfilename(filetypes=[('Fichiers Excel', '.csv')])
        if csv_file == "": return
        
        if csv_file[-4:] != ".csv": csv_file += ".csv"
        
        tree = ET.parse(tmx_file)
        root = tree.getroot()[0]

        for prop in root:
            
            trad = []
            
            for child in prop:
                
                if child.tag == 'prop' and list(child.attrib.keys())[0]=="domain":
                    trad.append(child.text)
                
                if list(child.attrib.keys())[0] == '{http://www.w3.org/XML/1998/namespace}lang':
                    lang = list(child.attrib.values())[0]
                    if not "Trad ("+lang+")" in cols:
                        cols.append("Trad ("+lang+")")
                    
                    trad.append(child[0].text)
                    
            # Contrôle du format des infos
            
            Valid = True
            for i in range(0,len(trad)):
                if trad[i] is None:
                    Valid = False                                                           # Vérif si c'est une valeur nulle (qui génère une variable None)
                else:
                    if trad[i][0] == "+": Valid = False                                     # Vérif si le 1er caractère est un "+"
                    if trad[i].replace(".","").replace(",","").isdigit(): Valid = False     # Vérif si c'est une valeur numérique
                    
            if Valid: rows.append(dict(zip(cols, trad)))
                
        df = pd.DataFrame(rows, columns=cols)
        df.to_csv(csv_file,sep=";",index=False,encoding="utf-8-sig")
        
        messagebox.showinfo("Opération terminée","Le fichier CSV est enregistré à l'emplacement : " + csv_file)
        
    def csv_vers_tmx():
        
        messagebox.showinfo("Fichier CSV","Sélectionnez le fichier CSV à exporter en TMX.")
        csv_file = filedialog.askopenfilename(filetypes=[('Fichiers CSV', '.csv')])
        if csv_file == "": return
        
        messagebox.showinfo("Nouveau fichier TMX","Saisir l'emplacement et le nom du fichier TMX qui sera exporté à partir du fichier CSV.")
        tmx_file = filedialog.asksaveasfilename(filetypes=[('Fichiers TMX', '.tmx')])
        if tmx_file == "": return
        
        if tmx_file[-4:] != ".tmx": tmx_file += ".tmx"
        
        df = pd.read_csv(csv_file,sep=";",encoding="utf-8-sig")

        root = ET.Element("body")
        tree = ET.ElementTree(root)
        tmx = ET.SubElement(root, "tmx")
        tmx.attrib = {'version':'1.00'}

        for index, row in df.iterrows():
            
            tu = ET.SubElement(tmx, "tu")
            
            prop = ET.SubElement(tu, "prop")
            prop.attrib = {'domain':''}
            if str(row[0]) == "nan":
                prop.text = ""
            else:
                prop.text = row[0]
            
            for i in range(1,len(df.columns)):
                
                lang = row.index[i].split("(")[1].replace(")","")
                
                tuv = ET.SubElement(tu, "tuv")
                tuv.attrib = {'{http://www.w3.org/XML/1998/namespace}lang':lang}
                
                seg = ET.SubElement(tuv, "seg")
                if str(row[i]) == "nan":
                    seg.text = ""
                else:
                    seg.text = row[i]
            
        ET.indent(tree)
        tree.write(tmx_file, encoding="UTF-8", xml_declaration=True)
        
        messagebox.showinfo("Opération terminée","Le fichier TMX est enregistré à l'emplacement : " + tmx_file)
        
## 1 ## Initialisation de la fenêtre Tkinter ##

window = tkinter.Tk()
window.geometry("500x200")
window.title('Traduction des fichiers CIMAG')
window.config(background = "white") 

## 2 ## Création des fonctions et éléments à afficher ##

btn_trad = tkinter.Button(window, text = "Traduire un TMX", command = tkFct.traduction)
btn_tmx_csv = tkinter.Button(window, text = "TMX vers CSV", command = tkFct.tmx_vers_csv)
btn_csv_tmx = tkinter.Button(window, text = "CSV vers TMX", command = tkFct.csv_vers_tmx)

## 3 ## Ancrage des éléments ##

btn_trad.pack(pady = 10)
btn_tmx_csv.pack(pady = 10)
btn_csv_tmx.pack(pady = 10)

## 4 ## Lancement de la boucle Tkinter ##

window.mainloop()