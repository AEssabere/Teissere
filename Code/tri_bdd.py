"""Importation des bibliotheques"""
import pandas as pd
import numpy as np

"""Recuperation des donnees"""
all_sheets = pd.read_excel('Base donnees ventes sirops fond de rayon.xlsx', sheet_name=None, index_col = None)
all_sheets.keys() # les noms des feuilles

# Pour le header : 
premiere_feuille = list(all_sheets.values())[0] # la premiere feuille
list_values = premiere_feuille.columns[0:] # on recupere la premiere ligne du tableau, de la 4ieme colonne a la derniere
newlist_values = ['Marque_Enseigne']
for i in range (1, 4):
    newlist_values.append(list_values[i])
# on recupere les valeurs des mois et annees
for i in range (4,len(list_values)):
    newlist_values.append(str(list_values[i].month) + ' / ' + str(list_values[i].year)) 

"""Concatenation de toutes les feuilles de calcul Excel"""
cdf = pd.concat(all_sheets ,ignore_index=True) 
cdf = cdf.drop(cdf.columns[len(list_values):], axis=1)
cdf.columns = newlist_values

"""Mauvaise recuperation de la 2eme colonne qui est remplie de valeurs NaN.
   Remplacement par une concatenation manuelle des 2emes colonnes de chaque feuille"""
lst_sheets = []
n = len(all_sheets.keys()) # nombre de feuilles
for k in range (n) :
    sh = pd.read_excel('Base donnees ventes sirops fond de rayon.xlsx',sheet_name=k, index_col = None)
    lst_sheets.append(sh.iloc[:,0])
cdf['Marque_Enseigne'] = pd.concat(lst_sheets, ignore_index=True)

"""Valeurs utiles"""
mc = cdf.shape[1] # nombre de colonnes
mr = cdf.shape[0] # nombre de lignes de la feuille de calcul sans l'entete 

"""Concatenation des produits ayant evolue"""
for i in range (0,mr):
    if(cdf.iloc[i, 1] == 'CLASSIQUES 60CL' or cdf.iloc[i, 1] == 'CLASSIQUES 75CL'):
        cdf.iloc[i, 1] = 'CLASSIQUES'
    if(cdf.iloc[i, 1] == 'MEGA 130CL' or cdf.iloc[i, 1] == 'MEGA 150cl'):
        cdf.iloc[i, 1] = 'MEGA'
    if(cdf.iloc[i, 0] == 'Galec' and (cdf.iloc[i, 1] == 'BIO (BID PUR SUCRE CANNE)' or cdf.iloc[i, 1] == 'BIO BIDON' or cdf.iloc[i, 1] == 'BIO')):
        cdf.iloc[i, 1] = 'BIO'
cdf = cdf.groupby(['Marque_Enseigne', 'Gamme', 'Parfum', 'Ventes en litres']).sum().reset_index()

"""Valeurs utiles"""
mc = cdf.shape[1] # nombre de colonnes
mr = cdf.shape[0] # nombre de lignes de la feuille de calcul sans l'entete

""" On garde uniquement les produits pour lequels on a plus de 15 mois de donnees"""
cdf = cdf.replace({'0':np.nan, 0:np.nan}) # on remplace tous les zeros par des Null
index_names = cdf[cdf.count (axis = 1) < 15+4].index # le +4 correspond a nos 4 colonnes de marques, gammes, ...
cdf.drop(index_names , inplace = True) # on supprime toutes les lignes dont les index sont dans index_names
cdf.fillna(0 , inplace = True) # on remplace les Null par des zeros 

# On utilise la colonne intitulee 'Marque_Enseigne' comme index
cdf.set_index('Marque_Enseigne' , inplace = True)

"""Conversion du dataframe en un fichier Excel"""
writer = pd.ExcelWriter('Base_donnees_triee.xlsx', engine='xlsxwriter')
cdf.to_excel(writer, sheet_name='Base GMS', index=True)
writer.close()