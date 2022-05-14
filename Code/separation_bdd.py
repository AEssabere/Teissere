"""Importation des bibliotheques"""
import pandas as pd
import xlsxwriter

"""Recuperation des donnees"""
wb = pd.read_excel('Base_donnees_triee.xlsx', sheet_name=0, index_col = None)

"""Valeurs utiles"""
mc = wb.shape[1] # nombre de colonnes
mr = wb.shape[0] # nombre de lignes de la feuille de calcul sans l'entete 
list_values = wb.columns[4:] # on recupere la premiere ligne du tableau, de la 4ieme colonne a la derniere 

"""Remise en forme des donnees"""
wbdata = xlsxwriter.Workbook('data_sirops.xlsx') # cree un nouveau fichier Excel
wsdata = wbdata.add_worksheet() # cree une nouvelle feuille dans le fichier

row = 0
wsdata.write(0, 0, 'Années\Identifiants')
# ecriture des dates dans la nouvelle feuille de calcul : 
for value in list_values: 
    row = row+1
    wsdata.write(row, 0, value)

# liste des identifiants : 
for i in range (0, mr): 
    wsdata.write(0, i+1, i+1)
    
# reecriture des valeurs de vente 
for i in range (0, mr): 
    for j in range (4, mc):   
        c = wb.iloc[i, j]
        wsdata.write(j-3, i+1, c)

wbdata.close()

"""Ensemble des identifiants"""
wbid = xlsxwriter.Workbook('identifiants_sirops.xlsx') # cree un nouveau fichier excel
wsid = wbid.add_worksheet() # cree une nouvelle feuille dans le fichier
  
# noms des colonnes : 
wsid.write(0,0, 'Identifiants')
wsid.write(0, 1, 'Marque-Enseigne')
wsid.write(0, 2, 'Gamme')
wsid.write(0, 3, 'Parfum')
wsid.write(0, 4, 'Ventes en litres') 
 
# liste des identifiants : 
for i in range (0, mr): 
    wsid.write(i+1, 0, i+1)

# reecriture des marques-Enseignes, Gammes, Parfums et Ventes en litres
for i in range (0, mr): 
    for j in range (0, 4):   
        c = wb.iloc[i, j]
        wsid.write(i+1, j+1, c)

wbid.close()

"""Passage en .csv"""
read_file = pd.read_excel("data_sirops.xlsx") 
read_file.to_csv("data_sirops.csv", index = None, header=True) 
read_file = pd.read_excel("identifiants_sirops.xlsx") 
read_file.to_csv("identifiants_sirops.csv", index = None, header=True)