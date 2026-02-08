import os
import tlsh
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations

def calculer_tlsh_fichier(chemin):
    """Calcule le hash TLSH d'un fichier."""
    try:
        with open(chemin, 'rb') as f:
            data = f.read()
            if len(data) < 50:
                return None
            return tlsh.hash(data)
    except:
        return None

def lister_fichiers(dossier):
    """Liste les fichiers d'un dossier."""
    fichiers = []
    for root, _, noms in os.walk(dossier):
        for nom in noms:
            if os.path.isfile(os.path.join(root, nom)):
                fichiers.append(os.path.join(root, nom))
    return fichiers

def calculer_matrice_distance(dossier):
    """Calcule la matrice des distances TLSH."""
    print("🔍 Calcul des hashes TLSH...")
    fichiers = lister_fichiers(dossier)
    hashes_tlsh = {}
    
    for chemin in fichiers:
        h = calculer_tlsh_fichier(chemin)
        if h:
            hashes_tlsh[chemin] = h
            print(f"✓ {os.path.basename(chemin)}")
    
    if len(hashes_tlsh) < 2:
        print("❌ Pas assez de fichiers")
        return None, None
    
    # Matrice des distances
    noms = list(hashes_tlsh.keys())
    n = len(noms)
    matrice = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i+1, n):
            dist = tlsh.diff(hashes_tlsh[noms[i]], hashes_tlsh[noms[j]])
            matrice[i,j] = dist
            matrice[j,i] = dist
    
    return noms, matrice

def creer_heatmap(matrice, noms, nom_sortie="heatmap_tlsh.png"):
    """Crée une VRAIE heatmap colorée."""
    # Tri par similarité (fichiers proches ensemble)
    scores = np.sum(matrice, axis=1)
    ordre = np.argsort(scores)
    matrice_triee = matrice[ordre][:, ordre]
    noms_tries = [noms[i] for i in ordre]
    
    # Configuration graphique
    plt.figure(figsize=(12, 10))
    sns.set(font_scale=0.8)
    
    # COULEURS : VERT FONCE = SIMILAIRE, ROUGE = DIFFERENT
    mask = matrice_triee == 0  # Diagonale en blanc
    sns.heatmap(
        matrice_triee,
        annot=True,           # Afficher les chiffres
        fmt='.0f',            # Format entier
        cmap='RdYlGn_r',      # Rouge->Vert INVERSE (vert=similaire)
        center=50,            # Centre des couleurs à 50
        square=True,          # Carrés parfaits
        linewidths=0.5,       # Bordures
        cbar_kws={'label': 'Distance TLSH (0=identique)'},
        xticklabels=[os.path.basename(f)[:15] for f in noms_tries],
        yticklabels=[os.path.basename(f)[:15] for f in noms_tries],
        mask=mask
    )
    
    plt.title('🔥 HEATMAP SIMILARITÉ FICHIERS (Vert = très similaires)', 
              fontsize=16, pad=20)
    plt.xlabel('Fichiers (triés par similarité)', fontsize=12)
    plt.ylabel('Fichiers (triés par similarité)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    # SAUVEGARDE
    plt.savefig(nom_sortie, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"✅ HEATMAP SAUVEGARDÉE : {os.path.abspath(nom_sortie)}")
    
    return noms_tries, matrice_triee

if __name__ == "__main__":
    dossier = input("Dossier à analyser : ").strip()
    if not os.path.exists(dossier):
        print("❌ Dossier introuvable")
        exit()
    
    noms, matrice = calculer_matrice_distance(dossier)
    if matrice is None:
        exit()
    
    noms_tries, matrice_triee = creer_heatmap(matrice, noms)
    
    print("\n📊 STATS :")
    print(f"Distance min: {np.min(matrice_triee):.1f}")
    print(f"Distance max: {np.max(matrice_triee):.1f}")
    print("\n🎉 Ouvre heatmap_tlsh.png pour voir les carrés colorés !")
