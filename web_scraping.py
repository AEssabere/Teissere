"""
    Importation des bibliotheques
"""
import re
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd

def get_url(mois, annee):
    """ Recupere l'URL de la page a recuperer
        Entrees :
            le mois et l'annee des donnees a recuperer
        Sortie :
            URL du mois et de l'annee souhaite
    """
    return f"http://www.infoclimat.fr/stations-meteo/analyses-mensuelles.php?mois=0{mois:02d}&annee={annee}"

def supp_le(string):
    """ Supprime l'element "le"
        Entrees :
            string : chaine de charactere
        Sortie :
            dans le cas ou e contient "le", on retourne tout ce qui se trouve avant "le"
            sinon, on retourne string
    """
    if "le" in string:
        return string.split("le")[0]
    return string

def remplir_dict(temp, station, dic, departement):
    """ Verifie si le code postal recupere est bien dans la liste des departements de la
        France metropolitaine, si c'est le cas, on associe la temperature au numero du
        departement en l'ajoutant dans le dictionnaire.
        Entree :
            temp : liste des temperatures moyennes du mois (ttm), des moyennes des temperatures
                maximales du mois (txm) ou température maximale extreme du mois (txx)
            station : le nom de la station
            dic : un dictionnaire vide qui contiendra les temperatures
            departement : liste des departements
        Sortie : void
    """
    string = "".join(departement)   # met dans une seule chaine de caractere tous les departements
    for cel_temp, cel_station in zip(temp, station):
        if cel_temp == '' or cel_temp is None:
            continue
        try:
            #recuperation du departement
            num_dep = str(re.compile(r'(\d+|2A|2B).$').search(cel_station).group(1))
            if num_dep in string:
                dic[num_dep].append(float(cel_temp))
        except:
            pass

def cal_moy(dic):
    """ Calcule la moyenne des temperatures des stations appartenant au meme departements
        Entree :
            Dictionnaire qui contient les moyennes de chaque station
        Sortie :
            Renvoie une liste des moyennes calculees
    """
    list_moyenne = []
    for list_elem in dic.values():
        if len(list_elem) >= 1:
            list_moyenne.append(sum(list_elem)/len(list_elem))
        else:
            list_moyenne.append("Null")
    return list_moyenne

def creer_dft(departement):
    """ Creer la transposee d'une data frame
        Entree :
            Liste des departements
        Sortie :
            Retourne la transposee de la data frame
    """
    df = pd.DataFrame(columns=departement)
    return df.T

def get_data(deb_annee, fin_annee, deb_mois, fin_mois):
    """ Recupere les donnees meteorologique (temperatures moyennes, maximales et les moyennes des
    temperatures moyennes du mois) ainsi que les departementes et exporte toutes les donnees dans 
    des fichiers csv.
        Entree :
            deb_annee : l'annee a laquelle on souhaite commencer a recuperer les donnees
            fin_annee : l'annee a laquelle on souhaite terminer la recuperation des donnees
            deb_mois : le mois auquel on souhaite commencer a recuperer les donnees
            fin_mois : le mois auquel on souhaite terminer la recuperation des donnees
        Sortie :
            void
    """

    #creation de la liste des departements de la France metropolitaine
    departement = ["Date"]
    departement += [f"departement {i:02d}" for i in range(1, 96)]
    departement += ["departement 2A", "departement 2B"]

    # la dataframe de la moyenne des températures du mois
    df_tmm = creer_dft(departement)

    # la dataframe des moyennes des temperatures maximales du mois
    df_txm = creer_dft(departement)

    # la dataframe des température maximale extreme du mois
    df_txx = creer_dft(departement)

    print(f"Start parser for {deb_mois}/{deb_annee} to {fin_mois}/{fin_annee}.")

    for annee in range(deb_annee, fin_annee+1):
        for mois in range(deb_mois, fin_mois+1):

            # recuperation de la date
            date = f"{mois:02d}/{annee}"

            # recuperation de l'adresse url du site
            url = get_url(mois, annee)

            # copie la page du site
            page = requests.get(url)
            html = bs(page.text, "html.parser")

            # recuperation de la balise table
            tab = html.find("table", id="tableau-releves")

            # dictionnaire des temperatures moyennes du mois
            dic_tmm = {f"{i:02d}":[] for i in range(1, 96)}
            dic_tmm["2A"] = []
            dic_tmm["2B"] = []

            # dictionnaire des moyennes des temperatures maximales du mois
            dic_txm = {f"{i:02d}":[] for i in range(1, 96)}
            dic_txm["2A"] = []
            dic_txm["2B"] = []

            # dictionnaire des temperatures maximales extremes du mois
            dic_txx = {f"{i:02d}":[] for i in range(1, 96)}
            dic_txx["2A"] = []
            dic_txx["2B"] = []

            # recuperation des donnees (noms des stations, tmm, txm, txx)
            station = [j.find_all('td')[0].text for j in tab.find_all('tr')[1:]]
            tmm = [j.find_all('td')[3].text for j in tab.find_all('tr')[1:]]
            txm = [j.find_all('td')[4].text for j in tab.find_all('tr')[1:]]
            txx = [supp_le(j.find_all('td')[5].text) for j in tab.find_all('tr')[1:]]

            # remplissage des dictionnaires avec les donnees recuperees
            remplir_dict(tmm, station, dic_tmm, departement)
            remplir_dict(txm, station, dic_txm, departement)
            remplir_dict(txx, station, dic_txx, departement)

            # ajout des moyennes des temperatures calculees par departement dans les data frames
            df_tmm[date] = [date] + cal_moy(dic_tmm)
            df_txm[date] = [date] + cal_moy(dic_txm)
            df_txx[date] = [date] + cal_moy(dic_txx)

    # Mettre en indice les dates pour chacun des data frames
    df_tmm = df_tmm.T
    df_tmm.set_index('Date', inplace=True)

    df_txm = df_txm.T
    df_txm.set_index('Date', inplace=True)

    df_txx = df_txx.T
    df_txx.set_index('Date', inplace=True)

    # convertir les dataframes en trois fichiers csv
    df_tmm.to_csv("data_tmm.csv")
    df_txm.to_csv("data_txm.csv")
    df_txx.to_csv("data_txx.csv")

    print("File saved as data_tmm.csv. Job finished!")
    print("File saved as data_txm.csv. Job finished!")
    print("File saved as data_txx.csv. Job finished!")

if __name__ == "__main__":
    # recupere les donnees du 01/2018 au 12/2021
    get_data(2018, 2018, 1, 2)
