#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime as dt
import itertools
import os

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D

########################################################################################################################

FICHIER_EXCEL = 'Nouveau Feuille de calcul Microsoft Excel.xlsx'

FICHIERS_CSV = [
    'second_positive_system_n2.csv',
	'first_negative_system_n2_plus.csv',
	'H-Balmer Lines.csv',
	'Secondary Spectrum H2.csv',
	
]

NOMS_DES_SYSTEMES = [
    'N2',
	'first_negative_system_n2_plus',
	'H-Balmer Lines',
	'Secondary Spectrum H2',
	
]

########################################################################################################################
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'donnees'))
RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resultats'))
FICHIER_EXCEL = os.path.join(DATA_DIR, FICHIER_EXCEL)
FICHIERS_CSV = [os.path.join(DATA_DIR, f) for f in FICHIERS_CSV]


def trouver_lambdas(donnees: pd.DataFrame, systeme: pd.DataFrame, nom_du_systeme: str, decalage: float = 0.2):
    """Trouver les lambda de données dans un système"""

    # Créer les intervales autour les lambdas des système
    intervals = pd.DataFrame(data=[], columns=['lmin', 'lmax'])
    intervals['lmin'] = systeme['lambda'] - decalage
    intervals['lmax'] = systeme['lambda'] + decalage

    # Initialisation
    mask = pd.Series(index=donnees.index, data=False)
    nb_lamdas_trouvee = 0
    print('\nIdentification du système {!r} avec un décalage {}:\n'.format(nom_du_systeme, decalage))

    # Loop
    for row in intervals.iterrows():
        new_mask = (donnees['lambda'] >= row[1]['lmin']) & (donnees['lambda'] <= row[1]['lmax'])
        # noinspection PyUnresolvedReferences
        if new_mask.any():
            nb_lamdas_trouvee += 1
            ranges_trouves = donnees[new_mask]
            intensite_max = ranges_trouves['I'].max()
            lambda_max = ranges_trouves.loc[ranges_trouves['I'] == intensite_max, 'lambda'].values
            max_new_mask = ranges_trouves['I'] == intensite_max
            print("{}: lambda {} trouveé {} fois. I_max={} pour lambda_max={}".format(
                nb_lamdas_trouvee, systeme.iloc[row[0]]['lambda'], len(ranges_trouves), intensite_max, lambda_max))
            mask = mask | max_new_mask

    print('\nTotale trouvé lambdas {} pour {}'.format(nb_lamdas_trouvee, nom_du_systeme))
    print('*' * 80)
    return donnees[mask]


def plot(donnees: pd.DataFrame, resultats: dict = None, save_as: str = None):
    """Tracer les courbes avec le moyen de `y`"""
    if resultats is None:
        resultats = {}

    fig, ax = plt.subplots(nrows=1, ncols=1)
    ax.plot(donnees['lambda'], donnees['I'], linewidth=.4)
    ax.plot(donnees['lambda'], donnees['I moyen'], linewidth=.8)
    ax.set_xlabel('Lambda')
    ax.set_ylabel('Intensité')
    # ax.legend(loc='upper left')

    left, right = ax.get_xlim()
    bottom, top = ax.get_ylim()
    xspan = right - left
    yspan = top - bottom
    y_counter = itertools.count(round((top + bottom) // 2), 20)
    couleurs = mcolors.XKCD_COLORS
    noms_couleurs = list(couleurs)

    handles_systemes = []

    for nom_couleur, (nom, resultat) in zip(noms_couleurs, resultats.items()):
        handles_systemes.append(Line2D([0], [0], color=couleurs[nom_couleur], lw=1))
        xmin = (resultat['lambda'].min() - left) / xspan
        y = next(y_counter)
        ymax = (y - bottom) / yspan
        for row in resultat.iterrows():
            x = row[1]['lambda']
            # xmin = 0
            xmax = (x - left) / xspan
            ymin = (row[1]['I'] - bottom) / yspan
            ax.axvline(x=x, ymin=ymin, ymax=ymax, linewidth=.4, linestyle='--', color=couleurs[nom_couleur])
            ax.axhline(y=y, xmin=xmin, xmax=xmax, linewidth=.4, linestyle='--', color=couleurs[nom_couleur])

    # ajouter les handles et labels pour les systèmes
    handles, labels = ax.get_legend_handles_labels()
    handles.extend(handles_systemes)
    labels.extend(resultats.keys())
    ax.legend(handles=handles, labels=labels, loc='upper left')

    if save_as:
        os.makedirs(RESULTS_DIR, exist_ok=True)
        filename = os.path.join(RESULTS_DIR, 'Fig {:%Y-%m-%d %H:%M:%S}.{}'.format(dt.datetime.now(), save_as))
        fig.savefig(filename, dpi=fig.dpi)
    plt.show()


def main():
    # Lire le fichier excel
    # ---------------------
    donnees = pd.read_excel(FICHIER_EXCEL, header=None, names=['lambda', 'I'])

    # Calculer le moyen de l'intensité
    donnees['I moyen'] = donnees['I'].mean()

    # Filtrer les données par: I > moyen(I)
    donnees_filtres = donnees.loc[donnees['I'] > donnees['I moyen']]

    # Lire les systèmes (les fichier .csv)
    systemes = {nom: pd.read_csv(fichier) for nom, fichier in zip(NOMS_DES_SYSTEMES, FICHIERS_CSV)}

    # Initialisation
    resultats = {}

    # Trouver les lambda des systèmes dans les donneés filtrées
    for nom, systeme in systemes.items():
        resultat = trouver_lambdas(donnees_filtres, systeme=systeme, nom_du_systeme=nom, decalage=0.1)
        resultats.update({nom: resultat})

    plot(donnees, resultats, save_as='svg')


if __name__ == '__main__':
    main()
