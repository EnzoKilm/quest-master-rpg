##########################################
#            Quest Master RPG            #
#          Programme secondaire          #
# BEAUCHAMP Enzo et DAUNAY Florian (721) #
#      Projet final - ISN 2018-2019      #
#    Lycée Montesquieu, 72000 Le Mans    #
##########################################

import tkinter as tk
import os
import tkinter.font as tkFont

fenetre = tk.Tk()

#############################
"""NOM GRILLE"""
nomGrille = "maison1_map3-3.txt"
"""DOSSIER IMAGES"""
dossierImages = "maison1_map3-3"
#############################

grille = open("cartes/" + nomGrille, "r")
lignes = grille.readlines()

x = (len(lignes[0])-1)*32
y = (len(lignes))*32

w = (fenetre.winfo_screenwidth()-x)/2
h = (fenetre.winfo_screenheight()-y)/3

fenetre.geometry(str(x) + "x" + str(y) + "+" + str(int(w)) + "+" + str(int(h)))
fenetre.title("Création de carte")

fenetre.maxsize(x,y)
fenetre.minsize(x,y)

canvas = tk.Canvas(fenetre, width=x, height=y, background="#B7B7B7")

moduleDossierImages = __import__("maps." + dossierImages + ".parametres", globals(), locals(), ['liste_caracteres_bloques', 'liste_caracteres_fleche', 'liste_caracteres_maison', 'coordonnees_interieur_maison', 'coordonnees_porte_maison', 'maison_shop'], 0)
liste_caracteres_bloques = moduleDossierImages.liste_caracteres_bloques
images_bloquees = []
liste_caracteres_fleche = moduleDossierImages.liste_caracteres_fleche
fleche = []
liste_caracteres_maison = moduleDossierImages.liste_caracteres_maison
maison = []
coordonnees_interieur_maison = moduleDossierImages.coordonnees_interieur_maison
coordonnees_porte_maison = moduleDossierImages.coordonnees_porte_maison
shop = moduleDossierImages.maison_shop

liste_images = []
stringCaracteres = "_$,;%!#&'~^@+à=-`çéabcdefghijklmnopqrstuvwxyz0123456789"
for caractere in stringCaracteres:
    path = "maps/" + dossierImages + "/" + caractere + ".png"
    if os.path.exists(path) == True:
        image = tk.PhotoImage(file=path)
        liste_images.append(image)
    else:
        # FILL IMAGE ICI
        path = "maps/" + dossierImages + "/a.png"
        image = tk.PhotoImage(file=path)
        liste_images.append(image)

def position_image(caractere, x, y):
    global canvas
    try:
        canvas.create_image(x*32, y*32, anchor=tk.NW, image=liste_images[stringCaracteres.find(caractere)])
        canvas.pack()
        if caractere in liste_caracteres_bloques:
            image_b = [x*32, y*32]
            images_bloquees.append(image_b)
        elif caractere in liste_caracteres_fleche:
            image_b = [x*32, y*32]
            fleche.append(image_b)
        elif caractere in liste_caracteres_maison:
            image_b = [x*32, y*32]
            maison.append(image_b)
        else:
            pass
    except:
        pass

for i in range (0, len(lignes)):
    j = 0
    for caractere in lignes[i]:
        # On positionne l'image
        position_image(caractere, j, i)
        j += 1

############################################
######### PROCESSUS POUR LES SHOP ##########
############################################
if shop == True:
    liste_items = []
    alphabetItems = "abcdefgh"
    for caractere in alphabetItems:
        path = "shop_" + dossierImages + "/" + caractere + ".png"
        if os.path.exists(path) == True:
            image = tk.PhotoImage(file=path)
            liste_items.append(image)
        else:
            path = dossierImages + "/a.png"
            image = tk.PhotoImage(file=path)
            liste_items.append(image)

    coordosImages = [[448, 64], [576, 64], \
                    [448, 192], [576, 192], \
                    [448, 320], [576, 320], \
                    [448, 448], [576, 448]]

    x = 0
    for coordos in coordosImages:
        canvas.create_image(coordos[0], coordos[1], anchor=tk.NW, image=liste_items[x])
        canvas.pack()
        x += 1

    moduleDossierShop = __import__("shop_" + dossierImages + ".parametres", globals(), locals(), ['prixItems'], 0)
    prixItems = moduleDossierShop.prixItems
    nomsItems = moduleDossierShop.nomsItems

    coordosPrix = [[528, 88], [656, 88], \
                    [528, 217], [656, 217], \
                    [528, 346], [656, 346], \
                    [528, 475], [656, 475]]

    priceFont = tkFont.Font(family='Helvetica', size=16, weight='bold')

    x = 0
    for coordos in coordosPrix:
        canvas.create_text(coordos[0], coordos[1], text=prixItems[x], font=priceFont)
        canvas.pack()
        x += 1

    coordosBoutons = [[496, 145], [624, 145], \
                    [496, 273], [624, 273], \
                    [496, 401], [624, 401], \
                    [496, 529], [624, 529]]

    texteShop = tk.Label(fenetre, text="", relief="sunken", fg="black", anchor=tk.CENTER, height=4, width=41)
    texteShop = canvas.create_window(208, 512, window=texteShop)

    def acheterItem(nom, prix):
        print(nom, prix)

    x = 0
    for coordos in coordosBoutons:
        # ici le "lambda x=x:" permet de n'exécuter la commande que lorsque le bouton sera cliqué et on lui assigne la valeur actuelle de x (x différent pour chaque bouton)
        bouton = tk.Button(fenetre, text="      Acheter      ", command=lambda x=x: acheterItem(nomsItems[x], prixItems[x]), cursor="hand2", height=1, borderwidth=4)
        bouton = canvas.create_window(coordos[0], coordos[1], window=bouton)
        x += 1

else:
    pass
############################################

fenetre.mainloop()
