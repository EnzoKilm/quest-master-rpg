# -*- coding: utf-8 -*-

##########################################
#            Quest Master RPG            #
#           Programme principal          #
# BEAUCHAMP Enzo et DAUNAY Florian (721) #
#      Projet final - ISN 2018-2019      #
#    Lycée Montesquieu, 72000 Le Mans    #
##########################################

import tkinter as tk
import tkinter.font as tkFont
import os
import sqlite3
import hashlib
import sys
import time
from PIL import Image, ImageTk
from random import randint

class db_coordos_perso:
    def __init__(self):
        # Connexion à la db
        self.conn = sqlite3.connect("db/database.db")
        self.c = self.conn.cursor()
        # Création de la table pour les users
        self.c.execute("""
        CREATE TABLE IF NOT EXISTS coordosPerso(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            pseudo TEXT,
            coordosCarteX INTEGER,
            coordosCarteY INTEGER,
            carte TEXT,
            posX INTEGER,
            posY INTEGER,
            direction INTEGER,
            numeroMaison INTEGER
                )""")
        # Sauvegarde
        self.conn.commit()

    def ajoutPerso(self, pseudo, coordosCarteX, coordosCarteY, carte, posX, posY, direction, numeroMaison):
        self.c.execute("""
        INSERT INTO coordosPerso(pseudo, coordosCarteX, coordosCarteY, carte, posX, posY, direction, numeroMaison) VALUES(?, ?, ?, ?, ?, ?, ?, ?)""", (pseudo, coordosCarteX, coordosCarteY, carte, posX, posY, direction, numeroMaison))
        self.conn.commit()

    def getCoordos(self, pseudo):
        self.c.execute("""SELECT * FROM coordosPerso WHERE pseudo=?""", (pseudo,))
        coordos = self.c.fetchone()
        return coordos

    def changeCoordos(self, pseudo, listeCoordos):
        nomColonnes = ["coordosCarteX", "coordosCarteY", "carte", "posX", "posY", "direction", "numeroMaison"]
        for i in range(0, len(nomColonnes)):
            self.c.execute("""UPDATE coordosPerso SET %s = ? WHERE pseudo = ?""" % (nomColonnes[i]), (listeCoordos[i], pseudo,))
        # Sauvegarde
        self.conn.commit()

class database:
    def __init__(self):
        # Connexion à la db
        self.conn = sqlite3.connect("db/database.db")
        self.c = self.conn.cursor()
        # Création de la table pour les users
        self.c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            pseudo TEXT,
            mdp TEXT,
            classe TEXT,
            sexe TEXT,
            lvl INTEGER,
            vie INTEGER,
            xp INTEGER,
            attaque INTEGER,
            defense INTEGER,
            argent INTEGER,
            armePrincipale TEXT,
            armeSecondaire TEXT,
            bouclier TEXT,
            casque TEXT,
            plastron TEXT,
            jambieres TEXT,
            bottes TEXT,
            utilisable1 TEXT,
            utilisable2 TEXT,
            utilisable3 TEXT,
            utilisable4 TEXT,
            attaqueSpeciale TEXT
                )""")
        # Sauvegarde
        self.conn.commit()

    def connexion_db(self, pseudo, mdp_hash):
        self.c.execute("""SELECT pseudo FROM users WHERE pseudo=?""", (pseudo,))
        resultat = self.c.fetchone()
        if resultat == None:
            return False
        else:
            self.c.execute("""SELECT mdp FROM users WHERE pseudo=?""", (pseudo,))
            resultat = self.c.fetchone()
            mdp = resultat[0]
            if mdp_hash == mdp:
                return True
            else:
                return False

    def inscription_db(self, pseudo, mdp_hash, classe, sexe, lvl, vie, xp, attaque, defense, argent, armePrincipale, armeSecondaire, bouclier, casque, plastron, jambieres, bottes, utilisable1, utilisable2, utilisable3, utilisable4, attaqueSpeciale):
        # On regarde si l'utilisateur existe déjà
        self.c.execute("""SELECT pseudo FROM users WHERE pseudo=?""", (pseudo,))
        resultat = self.c.fetchone()
        if resultat == None:
            default = "default"
            self.c.execute("""
            INSERT INTO users(pseudo, mdp, classe, sexe, lvl, vie, xp, attaque, defense, argent, armePrincipale, armeSecondaire, bouclier, casque, plastron, jambieres, bottes, utilisable1, utilisable2, utilisable3, utilisable4, attaqueSpeciale) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (pseudo, mdp_hash, classe, sexe, lvl, vie, xp, attaque, defense, argent, armePrincipale, armeSecondaire, bouclier, casque, plastron, jambieres, bottes, utilisable1, utilisable2, utilisable3, utilisable4, attaqueSpeciale))
            self.conn.commit()
            dbCoordos = db_coordos_perso()
            dbCoordos.ajoutPerso(pseudo, 6, 2, "maison", 384, 320, 1, 0)
            return True
        else:
            return False

    def getStats(self):
        self.c.execute("""SELECT * FROM users WHERE pseudo=?""", (pseudo,))
        stats = self.c.fetchone()
        return stats

    def getMoney(self, pseudo):
        self.c.execute("""SELECT argent FROM users WHERE pseudo=?""", (pseudo,))
        argent = self.c.fetchone()
        return argent[0]

    def getActualItem(self, pseudo, position):
        self.c.execute("""SELECT %s FROM users WHERE pseudo=?""" % (position), (pseudo,))
        nomItem = self.c.fetchone()
        return nomItem

    def changerArgent(self, pseudo, nouveauSolde):
        self.c.execute("""UPDATE users SET argent = ? WHERE pseudo = ?""", (nouveauSolde, pseudo,))
        self.conn.commit()

    def getUtilisables(self, pseudo):
        listeUtilisables = ["utilisable1", "utilisable2", "utilisable3", "utilisable4"]
        valueUtilisables = []
        for utilisable in listeUtilisables:
            self.c.execute("""SELECT %s FROM users WHERE pseudo=?""" % (utilisable), (pseudo,))
            value = self.c.fetchone()
            if value[0] == "vide":
                valueUtilisables.append(None)
            else:
                valueUtilisables.append(value[0])

        # On regarde où se trouve les places libres
        indexValues = []
        for value in valueUtilisables:
            if value == None:
                indexValues.append(valueUtilisables.index(value))
            else:
                pass

        return indexValues

    def changerItem(self, pseudo, nom, position, nouveauSolde):
        if position == "utilisables":
            indexValues = database.getUtilisables(self, pseudo)
            # Si il n'y a aucune place de libre dans l'INVENTAIRE
            if len(indexValues) == 0:
                return "ErreurPlace"
            # Sinon (si il y a de la place)
            else:
                # On récupère la position d'une place libre dans l'inventaire (+1 car la liste commence à 0)
                position = "utilisable" + str(indexValues[0]+1)
                itemActuel = database.getActualItem(self, pseudo, position)
        else:
            # On regarde si l'item que le joueur veut acheter n'est pas le même que celui qu'il possède déjà
            itemActuel = database.getActualItem(self, pseudo, position)

        if itemActuel[0] == nom:
            return "ErrorNom"
        else:
            try:
                database.changerArgent(self, pseudo, nouveauSolde)
                self.c.execute("""UPDATE users SET %s = ? WHERE pseudo = ?""" % (position), (nom, pseudo,))
                self.conn.commit()
                return "Valide", position
            except:
                return "Erreur"

    def removeUtilisable(self, pseudo, position):
        self.c.execute("""UPDATE users SET %s = "vide" WHERE pseudo = ?""" % (position), (pseudo,))
        self.conn.commit()

    def changerVie(self, pseudo, vie):
        self.c.execute("""UPDATE users SET vie = ? WHERE pseudo = ?""", (vie, pseudo,))
        self.conn.commit()

    def changerNiveau(self, pseudo, niveau):
        self.c.execute("""UPDATE users SET lvl = ? WHERE pseudo = ?""", (niveau, pseudo,))
        self.conn.commit()

    def changerXP(self, pseudo, experience):
        self.c.execute("""UPDATE users SET xp = ? WHERE pseudo = ?""", (experience, pseudo,))
        self.conn.commit()

    def newAttaqueDefense(self, pseudo, attaque, defense):
        self.c.execute("""UPDATE users SET attaque = ? WHERE pseudo = ?""", (attaque, pseudo,))
        self.c.execute("""UPDATE users SET defense = ? WHERE pseudo = ?""", (defense, pseudo,))
        self.conn.commit()

    def getAttaqueDefense(self, pseudo):
        self.c.execute("""SELECT attaque FROM users WHERE pseudo=?""", (pseudo,))
        attaque = self.c.fetchone()
        self.c.execute("""SELECT defense FROM users WHERE pseudo=?""", (pseudo,))
        defense = self.c.fetchone()
        return attaque[0], defense[0]

# Classe pour la gestion de la classe avec les stats des items du joueur
class db_playerStats:
    def __init__(self):
        # Connexion à la db
        self.conn = sqlite3.connect("db/database.db")
        self.c = self.conn.cursor()
        # Création de la table pour les users
        self.c.execute("""
        CREATE TABLE IF NOT EXISTS itemStats(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            nom TEXT,
            typeItem TEXT,
            statistique INTEGER,
            prix INTEGER
                )""")
        # Sauvegarde
        self.conn.commit()

    def getItem(self, itemName):
        self.c.execute("""SELECT nom FROM itemStats WHERE nom=?""", (itemName,))
        nomItem = self.c.fetchone()
        if nomItem == None:
            return True
        else:
            return False

    def ajoutItem(self, nom, typeItem, statistique):
        if db_playerStats.getItem(self, nom) == True:
            self.c.execute("""
            INSERT INTO itemStats(nom, typeItem, statistique) VALUES(?, ?, ?)""", (nom, typeItem, statistique))
            self.conn.commit()
        else:
            pass

    def itemStats(self, itemName):
        self.c.execute("""SELECT statistique FROM itemStats WHERE nom=?""", (itemName,))
        statsItem = self.c.fetchone()
        return statsItem[0]

    def changePrix(self, itemName, itemStat, itemType):
        if itemType == "utilisables":
            prixItem = itemStat
        else:
            prixItem = itemStat * 10
        self.c.execute("""UPDATE itemStats SET prix = ? WHERE nom = ?""", (prixItem, itemName,))
        self.conn.commit()

    def getPrix(self, itemName):
        self.c.execute("""SELECT prix FROM itemStats WHERE nom=?""", (itemName,))
        prixItem = self.c.fetchone()
        return prixItem[0]

#######################################
# Classe stats items dans la db
databaseStats = db_playerStats()

listeTypes = ["armePrincipale", "armeSecondaire", "bouclier", "casque", "plastron", "jambieres", "bottes", "utilisables"]
statistique = 0

for typeItem in listeTypes:
    listeItems = os.listdir("inventaire/" + typeItem)

    for nomItem in listeItems:
        # Ajout des items si ils ne sont pas dans la database
        newNomItem = nomItem[0:len(nomItem)-4]
        databaseStats.ajoutItem(newNomItem, typeItem, statistique)

        # Changement du prix des items en fonction de leurs stats
        statItem = databaseStats.itemStats(newNomItem)
        databaseStats.changePrix(newNomItem, statItem, typeItem)

#######################################

# Classe pour la gestion de la classe avec les stats des items du joueur
class db_monsterStats:
    def __init__(self):
        # Connexion à la db
        self.conn = sqlite3.connect("db/database.db")
        self.c = self.conn.cursor()
        # Création de la table pour les users
        self.c.execute("""
        CREATE TABLE IF NOT EXISTS monsterStats(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            nom TEXT,
            niveau INTEGER,
            vie INTEGER,
            attaque INTEGER,
            defense INTEGER,
            imgSrc TEXT
                )""")
        # Sauvegarde
        self.conn.commit()

    def getStat(self, statistique, nomMonstre):
        self.c.execute("""SELECT %s FROM monsterStats WHERE nom=?""" % (statistique), (nomMonstre,))
        valeurStat = self.c.fetchone()
        return valeurStat[0]

    def testNomMonstre(self, nomMonstre):
        self.c.execute("""SELECT nom FROM monsterStats WHERE nom=?""", (nomMonstre,))
        nomMonstre = self.c.fetchone()
        if nomMonstre == None:
            return True
        else:
            return False

    def addMonstre(self, nomMonstre):
        if db_monsterStats.testNomMonstre(self, nomMonstre) == True:
            self.c.execute("""
            INSERT INTO monsterStats(nom, niveau, vie, attaque, defense, imgSrc) VALUES(?, ?, ?, ?, ?, ?)""", (nomMonstre, 1, 50, 10, 10, "imagesCombat/monstre1.png"))
            self.conn.commit()
        else:
            pass

    def monstreAleatoire(self, niveauMonstre):
        self.c.execute("""SELECT nom FROM monsterStats WHERE niveau=?""", (niveauMonstre,))
        nomsMonstres = self.c.fetchall()
        monstreAlea = randint(0, len(nomsMonstres)-1)
        return nomsMonstres[monstreAlea][0]

    def getImgSrc(self, nomMonstre):
        self.c.execute("""SELECT imgSrc FROM monsterStats WHERE nom=?""", (nomMonstre,))
        imgSrc = self.c.fetchone()
        return imgSrc[0]

#######################################
# Crypter un mot de passe en SHA512
def cryptage_mdp(mdp):
    # Premier hashage
    mdp_hash = hashlib.sha512()
    mdp_hash.update(mdp.encode('utf8'))
    mdp_hash = mdp_hash.hexdigest()
    # Deuxième hashage
    mdp_double_hash = hashlib.sha512()
    mdp_double_hash.update(mdp_hash.encode('utf8'))
    mdp_double_hash = mdp_double_hash.hexdigest()

    return mdp_double_hash
#######################################

class firstPage:
    def __init__(self):
        global frame_first
        # Initialisation
        frame_first = tk.Tk()
        frame_first.configure(background="#999999")
        # Dimensions de l'écran
        screen_width = frame_first.winfo_screenwidth()
        screen_height = frame_first.winfo_screenheight()
        # Dimensions de la frame
        x = 770
        y = 736
        x_offset = int((screen_width-x)/2)
        y_offset = int((screen_height-y)/3)
        # Taille (largeur x hauteur + x_offset + y_offset)
        frame_first.geometry("%sx%s+%s+%s" % (x, y, x_offset, y_offset))
        # Titre
        frame_first.title("Quest Master RPG | Connexion/Inscription")

        # Background
        backgroundImg = ImageTk.PhotoImage(Image.open('QuestMaster.png'))
        backgroundLabel = tk.Label(frame_first, image=backgroundImg)
        backgroundLabel.pack()
        backgroundLabel.place(x=0, y=0, relwidth=1, relheight=1)

        """Contenu de la frame"""
        # Frame TITRE
        frame_titre = tk.Frame(backgroundLabel, borderwidth=2, relief=tk.GROOVE)
        frame_titre.pack(side=tk.TOP)
        # Texte TITRE
        tk.Label(frame_titre, text="Quest Master RPG - Connexion / Inscription").pack(side=tk.TOP, padx=8, pady=8)

        # Frame BOUTONS
        frame_boutons = tk.Frame(backgroundLabel, borderwidth=2, relief=tk.GROOVE)
        frame_boutons.pack(side=tk.TOP, pady=y/3)
        # Bouton CONNEXION/INSCRIPTION
        tk.Button(frame_boutons, text="Connexion/Inscription", command=lambda:firstPage.connexion_inscription(), cursor="hand2", height=int(y/200), width=48).pack(side=tk.TOP)
        # Bouton QUITTER
        tk.Button(frame_boutons, text="Quitter", command=lambda:frame_first.destroy(), cursor="hand2", height=int(y/200), width=48).pack(side=tk.TOP)

        # Frame VERSION DU JEU
        frame_version = tk.Frame(backgroundLabel, borderwidth=2, relief=tk.GROOVE)
        frame_version.pack(side=tk.BOTTOM)
        # Texte VERSION DU JEU
        tk.Label(frame_version, text="Version 1.0.0").pack(side=tk.TOP, padx=8, pady=8)

        # Boucle
        frame_first.mainloop()

    def connexion_inscription():
        global frame, entree_pseudo_connexion, entree_mdp_connexion, entree_pseudo_inscription, entree_mdp_inscription, texte_console, choix_classe, choix_sexe
        # On détruit la première page
        frame_first.destroy()
        # On crée la fenêtre d'inscription
        frame = tk.Tk()
        frame.configure(background="#999999")
        # Dimensions de l'écran
        screen_width = frame.winfo_screenwidth()
        screen_height = frame.winfo_screenheight()
        # Dimensions de la frame
        x = 770
        y = 736
        x_offset = int((screen_width-x)/2)
        y_offset = int((screen_height-y)/3)
        # Taille (largeur x hauteur + x_offset + y_offset)
        frame.geometry("%sx%s+%s+%s" % (x, y, x_offset, y_offset))
        # Titre
        frame.title("Quest Master RPG | Connexion/Inscription")

        """Contenu de la frame"""
        # Frame TITRE
        frame_titre = tk.Frame(frame, borderwidth=2, relief=tk.GROOVE)
        frame_titre.pack(side=tk.TOP)
        # Texte TITRE
        tk.Label(frame_titre, text="Quest Master RPG | Connexion/Inscription").pack(side=tk.TOP, padx=8, pady=8)

        # Frame CONNEXION/INSCRIPTION
        frame_connexion_inscription = tk.Frame(frame, borderwidth=2, background="#999999")
        frame_connexion_inscription.pack(side=tk.TOP, pady=y/4)
        # ---------------------------------------
        # Frame CONNEXION
        frame_connexion = tk.Frame(frame_connexion_inscription, borderwidth=2, relief=tk.GROOVE)
        frame_connexion.pack(side=tk.LEFT)
        # ---------------------------------------
        # Texte CONNEXION
        tk.Label(frame_connexion, text="Connexion\n").pack()
        # ---------------------------------------
        # INPUTS
        tk.Label(frame_connexion, text="Pseudo : ").pack()
        entree_pseudo_connexion = tk.Entry(frame_connexion)
        entree_pseudo_connexion.pack()
        entree_pseudo_connexion.focus_force()
        # ---------------------------------------
        tk.Label(frame_connexion, text="Mot de passe : ").pack()
        entree_mdp_connexion = tk.Entry(frame_connexion, show='*')
        entree_mdp_connexion.pack()
        # ---------------------------------------
        # Texte ESPACE
        tk.Label(frame_connexion, text=" ").pack()
        # ---------------------------------------
        # Bouton CONNEXION
        tk.Button(frame_connexion, text="Connexion", command=lambda:firstPage.connexion(), cursor="hand2", height=int(y/300), width=32).pack(side=tk.TOP)

        # ---------------------------------------
        # Frame ESPACE
        frame_espace = tk.Frame(frame_connexion_inscription, borderwidth=2, relief=tk.GROOVE)
        frame_espace.pack(side=tk.LEFT, padx=64)

        # ---------------------------------------
        # Frame INSCRIPTION
        frame_inscription = tk.Frame(frame_connexion_inscription, borderwidth=2, relief=tk.GROOVE)
        frame_inscription.pack(side=tk.RIGHT)
        # ---------------------------------------
        # Texte INSCRIPTION
        tk.Label(frame_inscription, text="Inscription\n").pack()
        # ---------------------------------------
        # Frame ENTRÉES
        frame_entrees = tk.Frame(frame_inscription, borderwidth=2, relief=tk.GROOVE)
        frame_entrees.pack()
        # ---------------------------------------
        # INPUTS
        tk.Label(frame_entrees, text="Pseudo : ").pack()
        entree_pseudo_inscription = tk.Entry(frame_entrees)
        entree_pseudo_inscription.pack()
        # ---------------------------------------
        tk.Label(frame_entrees, text="Mot de passe : ").pack()
        entree_mdp_inscription = tk.Entry(frame_entrees, show='*')
        entree_mdp_inscription.pack()
        # ---------------------------------------
        # Frame CHOIX CLASSE
        frame_choix_classe = tk.Frame(frame_inscription, borderwidth=2, relief=tk.GROOVE)
        frame_choix_classe.pack()
        # Texte CHOIX CLASSE
        tk.Label(frame_choix_classe, text="Classe du personnage").pack()
        # ---------------------------------------
        # BOUTONS CHOIX CLASSE
        liste_classes_personnage = ["Guerrier", "Archer", "Mage"]
        choix_classe = tk.StringVar()
        choix_classe.set(liste_classes_personnage[0])
        for i in range(0, len(liste_classes_personnage)):
            b = tk.Radiobutton(frame_choix_classe, variable=choix_classe, text=liste_classes_personnage[i], value=liste_classes_personnage[i])
            b.pack(side='left', expand=1)
        # ---------------------------------------
        # Frame CHOIX SEXE
        frame_choix_sexe = tk.Frame(frame_inscription, borderwidth=2, relief=tk.GROOVE)
        frame_choix_sexe.pack()
        # Texte CHOIX SEXE
        tk.Label(frame_choix_sexe, text="Sexe du personnage").pack()
        # ---------------------------------------
        # BOUTONS CHOIX SEXE
        valeur_liste_sexe_personnage = ["f", "h"]
        liste_sexe_personnage = ["Féminin", "Masculin"]
        choix_sexe = tk.StringVar()
        choix_sexe.set(valeur_liste_sexe_personnage[1])
        for i in range(0, len(liste_sexe_personnage)):
            b = tk.Radiobutton(frame_choix_sexe, variable=choix_sexe, text=liste_sexe_personnage[i], value=valeur_liste_sexe_personnage[i])
            b.pack(side='left', expand=1)
        # ---------------------------------------
        # Texte ESPACE
        tk.Label(frame_inscription, text=" ").pack()
        # ---------------------------------------
        # Bouton CONNEXION
        tk.Button(frame_inscription, text="Inscription", command=lambda:firstPage.inscription(), cursor="hand2", height=int(y/300), width=32).pack(side=tk.RIGHT)
        # Frame CONSOLE
        frame_console = tk.Frame(frame, borderwidth=2, relief=tk.GROOVE)
        frame_console.pack(side=tk.BOTTOM)
        # Texte CONSOLE
        texte_console = tk.Label(frame_console, text="", relief="ridge")
        texte_console.pack(side=tk.BOTTOM, padx=0, pady=0)

    def connexion():
        global texte_console, pseudo, numeroMaison
        # On récupère les entrées
        pseudo = entree_pseudo_connexion.get().strip()
        mdp = entree_mdp_connexion.get().strip()

        if pseudo == "" or mdp == "":
            texte_console.configure(text="Veuillez remplir tous les champs disponibles.")
        else:
            # On crypte le mot de passe
            mdp_hash = cryptage_mdp(mdp)
            # On essaye de connecter le joueur à la db
            db = database()
            login = db.connexion_db(pseudo, mdp_hash)

            if login == False:
                texte_console.configure(text="Nom d'utilisateur/mot de passe incorrect.")
            else:
                frame.destroy()

                # On récupère la dernière position enregistrée du joueur
                dbCoordos = db_coordos_perso()
                coordosPerso = dbCoordos.getCoordos(pseudo)

                # On lance la page de jeu
                numeroMaison = coordosPerso[8]
                fenetre1jour=fenetreApp([int(coordosPerso[2]), int(coordosPerso[3])], coordosPerso[4], coordosPerso[5], coordosPerso[6], coordosPerso[7])

    def inscription():
        global texte_console, pseudo, classe, sexe, numeroMaison
        # On récupère les entrées
        pseudo = entree_pseudo_inscription.get().strip()
        mdp = entree_mdp_inscription.get().strip()
        classe = choix_classe.get().strip().lower()
        sexe = choix_sexe.get().strip()

        if pseudo == "" or mdp == "":
            texte_console.configure(text="Veuillez remplir tous les champs disponibles.")
        else:
            # On crypte le mot de passe
            mdp_hash = cryptage_mdp(mdp)
            # On essaye de connecter le joueur à la db
            db = database()
            login = db.inscription_db(pseudo, mdp_hash, classe, sexe, 1, 100, 0, 1, 1, 0, "epee_bois", "poing", "bouclier_bois", "vide", "vide", "vide", "vide", "vide", "vide", "vide", "vide", "default")

            if login == False:
                texte_console.configure(text="Le pseudo '" + pseudo + "' est déjà prit.")
            else:
                frame.destroy()
                # On lance la page de jeu
                numeroMaison = 0
                fenetre1jour=fenetreApp([6, 2], "maison", 384, 320, 1)

class fenetreCombat:
    def __init__(self, coordosGrille, map_type, coordos_perso, directionPerso, boss):
        global classe, sexe, niveauJoueur, nombreTourEnnemi, joueurGele, jaugeDegatsAttaqueSpe, canvas, x, y, fenetre, persoCombat, sort, ennemiCombat, variable_fini, matrice1, matrice2, matrice3, matrice4, statAttackArmePrincipale, statAttackArmeSecondaire, statAttackSpecial, statDefJoueur, vieJoueur, statDefEnnemi, statAttackEnnemi, vieEnnemi, nombreTour, statAttackSpecial, txtTour, fontPV, txtVieJoueur, txtVieEnnemi, joueur_stats, listeImagesTkinterUtilisables, listeImagesUtilisables, ennemiCombat, niveau_monstres, attaqueDefense
        variable_fini = True

        matrice1=fenetreCombat.matriceCoords(20,477,173,528)
        matrice2=fenetreCombat.matriceCoords(20,544,173,595)
        matrice3=fenetreCombat.matriceCoords(20,610,173,661)
        matrice4=fenetreCombat.matriceCoords(20,677,173,728)

        # On déturit l'ancienne fenêtre
        fenetre.destroy()

        fenetre=tk.Tk()
        # Définition de la taille de la fenêtre
        x = 770
        y = 736
        # Ajustement à la taille de l'écran
        w = (fenetre.winfo_screenwidth()-x)/2
        h = (fenetre.winfo_screenheight()-y)/3
        # Taille + position de la fenêtre
        fenetre.geometry(str(x) + "x" + str(y) + "+" + str(int(w)) + "+" + str(int(h)))
        # dirt_intersection
        fenetre.title("Quest Master RPG | Combat")
        # Bloquage du redimensionnement
        fenetre.maxsize(x,y)
        fenetre.minsize(x,y)
        canvas = tk.Canvas(fenetre, width=x, height=y, background="#ffffff")

        ###############################################
        # On récupère les stats de l'utilisateur
        ##########
        db = database()
        joueur_stats = db.getStats()
        classe = joueur_stats[3]
        sexe = joueur_stats[4]
        niveauJoueur = joueur_stats[5]

        # Attaque / defense
        attaqueDefense = db.getAttaqueDefense(pseudo)

        ### VIE ###
        vieJoueur = joueur_stats[6]

        ### Attaque Principale/Secondaire + Defense ###
        statDefJoueur = attaqueDefense[1]
        for i in range(0, len(nomItemsInventaire)):
            nomItemPerso = joueur_stats[i+11]
            typeItem = nomItemsInventaire[i]

            statsItem = databaseStats.itemStats(nomItemPerso)

            if typeItem == "armePrincipale":
                statAttackArmePrincipale = statsItem + attaqueDefense[0]
            elif typeItem == "armeSecondaire":
                statAttackArmeSecondaire = statsItem
            elif typeItem in ["bouclier", "casque", "plastron", "jambieres", "bottes"]:
                statDefJoueur += statsItem
            else:
                pass

        ###############################################
        # Stats de l'ennemi
        ##########
        databaseMonstres = db_monsterStats()

        nomsMonstres = ["monstre1", "monstre2", "chevalier", "squelette", "boss", "arbre", "cerbère", "poisson lanterne"]
        for nomMonstre in nomsMonstres:
            databaseMonstres.addMonstre(nomMonstre)

        # On récupère le niveau des monstres de la zone
        moduleDossierImages = __import__("maps." + dossierImages + ".parametres", globals(), locals(), ['niveau_monstres', 'fond_ecran_combat'], 0)

        niveau_monstres = moduleDossierImages.niveau_monstres

        if boss == True:
            nomMonstre = databaseMonstres.monstreAleatoire("X")
            fond_ecran_combat = moduleDossierImages.fond_ecran_combat
            monstreImgSrc = databaseMonstres.getImgSrc(nomMonstre)
        else:
            nomMonstre = databaseMonstres.monstreAleatoire(niveau_monstres)
            fond_ecran_combat = moduleDossierImages.fond_ecran_combat
            monstreImgSrc = databaseMonstres.getImgSrc(nomMonstre)

        listeStats = ["vie", "attaque", "defense"]
        statsMonstre = []
        for stat in listeStats:
            statsMonstre.append(databaseMonstres.getStat(stat, nomMonstre))

        vieEnnemi = statsMonstre[0]
        statAttackEnnemi = statsMonstre[1]
        statDefEnnemi = statsMonstre[2]

        nombreTour = 0
        nombreTourEnnemi = 1
        joueurGele = False
        jaugeDegatsAttaqueSpe = 0
        ############################

        imageFond = Image.open(fond_ecran_combat)
        backgroundFenetre = ImageTk.PhotoImage(imageFond)
        fond = canvas.create_image(0,0, anchor=tk.NW, image=backgroundFenetre)
        ligne = canvas.create_line(0,(y*(7/11)),x,(y*(7/11)))

        #creations rectangles du menu
        rectAttack=canvas.create_rectangle(20,477,172,527, fill="#ff0000")
        txt = canvas.create_text(96, 502, text="Attaque", font="Arial 16 italic", fill="black")

        rectSwitch=canvas.create_rectangle(20,544,172,594, fill="#ffff00")
        txt = canvas.create_text(96, 569, text="Attaque spéciale", font="Arial 14 italic", fill="black")

        rectSort=canvas.create_rectangle(20,610,172,661, fill="#ff00ff")
        txt = canvas.create_text(96, (1271/2), text="Sortilège", font="Arial 16 italic", fill="black")

        rectFuir=canvas.create_rectangle(20,677,172,728, fill="#0000ff")
        txt = canvas.create_text(96, (1405/2), text="Fuir", font="Arial 16 italic", fill="black")

        # Rectangle du milieu
        rectAction=canvas.create_rectangle(201,477,569,728, fill="#ffffff")
        txtTour = canvas.create_text(385, 702, text="Tour du joueur", font="Arial 16 italic", fill="blue")
        # Rectangles des PV
        fontPV = tkFont.Font(family='Helvetica', size=32, weight='bold')
        rectPVjoueur = canvas.create_rectangle(201, 477, 353, 537, fill="#ffffff")
        txtVieJoueur = canvas.create_text(277, 507, text=vieJoueur, fill="blue", font=fontPV)
        rectPVennemi = canvas.create_rectangle(417, 477, 569, 537, fill="#ffffff")
        txtVieEnnemi = canvas.create_text(493, 507, text=vieEnnemi, fill="red", font=fontPV)

        # Rectangle à droite
        rectInfos = canvas.create_rectangle(586, 477, 762, 728, fill="#7884AB", outline="#17111A") #176px de large et 251 de haut
        # Images et numéros des utilisables
        listeImagesUtilisables = []
        listeImagesUtilisables.append(tk.PhotoImage(file="inventaire/utilisables/vide.png"))
        listeImagesTkinterUtilisables = []
        for i in range(0, 4):
            listeImagesUtilisables.append(tk.PhotoImage(file="inventaire/utilisables/" + joueur_stats[i+18] + ".png"))
            imageUtilisable = canvas.create_image(595+i*41, 487, anchor=tk.NW, image=listeImagesUtilisables[i+1])
            listeImagesTkinterUtilisables.append(imageUtilisable)
            canvas.create_text(611+i*41, 529, text=str(i+1), fill="black")

        # Images des persos
        imagePersoCombat= tk.PhotoImage(file="imagesCombat/"+classe+"_"+sexe+"_droite.png")
        persoCombat=canvas.create_image(62, 200, anchor=tk.NW, image=imagePersoCombat)
        imageEnnemiCombat= tk.PhotoImage(file=monstreImgSrc)
        ennemiCombat=canvas.create_image(420, 14, anchor=tk.NW, image=imageEnnemiCombat)
        canvas.pack()

        fenetre.bind("<Any-KeyPress>", fenetreCombat.utiliserSoin)
        fenetre.bind("<Button-1>", lambda event: fenetreCombat.clicAttaque(event, coordosGrille, map_type, coordos_perso, directionPerso))
        fenetre.mainloop()

    def matriceCoords(x1,y1,x2,y2):
        matrice=[]
        listeX=[]
        listeY=[]
        while True:
            listeX.append(x1)
            x1+=1
            if x1==x2:
                break

        while True:
            listeY.append(y1)
            y1+=1
            if y1==y2:
                break

        longueurX=len(listeX)
        longueurY=len(listeY)

        for i in range (0,longueurX):
            for j in range (0,longueurY):
                listeCoords=[]
                listeCoords.append(listeX[i])
                listeCoords.append(listeY[j])
                matrice.append(listeCoords)

        return matrice

    def clicAttaque(event, coordosGrille, map_type, coordos_perso, directionPerso):
        global niveauJoueur, txtEcran, joueur_stats, nombreTourEnnemi, joueurGele, jaugeDegatsAttaqueSpe, txtVieJoueur, txtVieEnnemi, variable_fini, txtTour, txtEcran, statAttackArmePrincipale, statAttackArmeSecondaire, vieJoueur, statDefJoueur, statAttackSpecial, statDefEnnemi, vieEnnemi, nombreTour, matrice1, matrice2, matrice3, matrice4, mvtSort, ennemiCombat, canvas, x, y, mvt, persoCombat, imagePersoCombat, sort, imageSort
        if variable_fini == True:
            variable_fini = False

            if joueurGele == True:
                coordsClique = [21,478]
            else:
                try:
                    canvas.delete(txtEcran)
                except:
                    pass
                coordsClique=[]
                coordsClique.append(event.x)
                coordsClique.append(event.y)

            listeMatrices = [matrice1, matrice2, matrice3, matrice4]
            inMatriceCounter = 0
            for matrice in listeMatrices:
                if coordsClique in matrice:
                    inMatriceCounter += 1
                else:
                    pass

            if inMatriceCounter > 0:

                if joueurGele == False:
                    # ATTAQUE PRINCIPALE
                    a=len(matrice1)+1
                    for i in range (0,a):
                        if coordsClique==matrice1[i-1]:
                            nombreTour+=1
                            mvtSort=10
                            try:
                                canvas.delete(txtEcran)
                            except:
                                pass

                            ###################################

                            mvt=300
                            canvas.delete(persoCombat)
                            imagePersoCombat2= tk.PhotoImage(file="imagesCombat/"+classe+"_"+sexe+"_bras_levé.png")
                            persoCombat2=canvas.create_image((62+mvt), 200, anchor=tk.NW, image=imagePersoCombat2)
                            fenetre.update()
                            time.sleep(0.6)
                            canvas.delete(persoCombat2)
                            imagePersoCombat= tk.PhotoImage(file="imagesCombat/"+classe+"_"+sexe+"_droite.png")
                            persoCombat = canvas.create_image(62, 200 , anchor=tk.NW, image=imagePersoCombat)

                            ####################################
                            # Statistiques du combat
                            # L'attaque correspond aux points d'attaque du joueur
                            ##########
                            degats = statAttackArmePrincipale - statDefEnnemi
                            if degats < 0:
                                degats = 0
                            else:
                                pass

                            vieEnnemi -= degats
                            ####################################

                            txtEcran = canvas.create_text(385, 602, text="Coup : "+str(degats), font="Arial 16 italic", fill="black")

                    # ATTAQUE SECONDAIRE
                    b=len(matrice2)+1
                    for i in range (0,b):
                        if coordsClique==matrice2[i-1]:
                            nombreTour+=1
                            mvtSort=10
                            try:
                                canvas.delete(txtEcran)
                            except:
                                pass

                            ###################################

                            #animation bras du personnage
                            canvas.delete(persoCombat)
                            imagePersoCombat2= tk.PhotoImage(file="imagesCombat/"+classe+"_"+sexe+"_bras_levé.png")
                            persoCombat2=canvas.create_image(62, 200, anchor=tk.NW, image=imagePersoCombat2)
                            fenetre.update()
                            time.sleep(0.2)   #temps entre bras levé et boule de feu
                            canvas.delete(persoCombat2)
                            imagePersoCombat= tk.PhotoImage(file="imagesCombat/"+classe+"_"+sexe+"_droite.png")
                            persoCombat = canvas.create_image(62,200 , anchor=tk.NW, image=imagePersoCombat)

                            #animation de la foudre
                            imageSort= tk.PhotoImage(file="imagesCombat/eclair.png")
                            mvt=0
                            sort1=canvas.create_image(158,221, anchor=tk.NW, image=imageSort)
                            fenetre.update()
                            time.sleep(0.03)
                            sort2=canvas.create_image(158+128,221, anchor=tk.NW, image=imageSort)
                            fenetre.update()
                            time.sleep(0.03)
                            sort3=canvas.create_image(158+256,221, anchor=tk.NW, image=imageSort)
                            fenetre.update()
                            time.sleep(0.03)
                            canvas.pack()
                            mvtSort+=1
                            #delete les images de foudre
                            fenetre.update()
                            time.sleep(0.05)
                            canvas.delete(sort1)
                            fenetre.update()
                            time.sleep(0.05)
                            canvas.delete(sort2)
                            fenetre.update()
                            time.sleep(0.05)
                            canvas.delete(sort3)
                            fenetre.update()

                            ####################################
                            # Statistiques du combat
                            # L'attaque correspond aux points d'attaque du joueur + une chance d'effectuer un coup critique
                            ##########
                            chanceCritique = randint(0, 1)
                            if chanceCritique == 0:
                                degatsCritique = randint(30, 100)
                            else:
                                degatsCritique = 0

                            degats = statAttackArmePrincipale + degatsCritique - statDefEnnemi
                            if degats < 0:
                                degats = 0
                            else:
                                pass

                            vieEnnemi -= degats
                            ####################################

                            txtEcran = canvas.create_text(385, 602, text="Foudre : "+str(degats), font="Arial 16 italic", fill="black")

                    # SORT
                    c=len(matrice3)+1
                    for i in range (0,c):
                        if coordsClique==matrice3[i-1]:
                            nombreTour+=1
                            mvtSort=10

                            try:
                                canvas.delete(txtEcran)
                            except:
                                pass

                            ######################
                            ####   Animation  ####
                            #animation du bras du personnage
                            canvas.delete(persoCombat)
                            imagePersoCombat2= tk.PhotoImage(file="imagesCombat/"+classe+"_"+sexe+"_bras_levé.png")
                            persoCombat2=canvas.create_image(62, 200, anchor=tk.NW, image=imagePersoCombat2)
                            fenetre.update()
                            time.sleep(0.2)   #temps entre bras levé et boule de feu
                            canvas.delete(persoCombat2)
                            imagePersoCombat= tk.PhotoImage(file="imagesCombat/"+classe+"_"+sexe+"_droite.png")
                            persoCombat = canvas.create_image(62,200 , anchor=tk.NW, image=imagePersoCombat)
                            ###
                            #animation boule de  feu
                            imageSort= tk.PhotoImage(file="imagesCombat/bouleDeFeu.png")
                            mvt=0
                            for i in range (0,290):
                                fenetre.update()
                                time.sleep(.0002)
                                try:
                                    canvas.delete(sort)
                                except:
                                    pass

                                sort=canvas.create_image((158+mvt+mvtSort),221 , anchor=tk.NW, image=imageSort)
                                canvas.pack()
                                mvtSort+=1
                            canvas.delete(sort)
                            imageSortImpact= tk.PhotoImage(file="imagesCombat/bouleDeFeuImpact.png")
                            sortImpact=canvas.create_image((158+mvt+mvtSort),221 , anchor=tk.NW, image=imageSortImpact)
                            fenetre.update()
                            time.sleep(0.2)
                            canvas.delete(sortImpact)
                            fenetre.update()

                            ####################################
                            # Statistiques du combat
                            # L'attaque correspond aux points d'attaque du joueur
                            ##########
                            degats = statAttackArmePrincipale + 20 - statDefEnnemi
                            if degats < 0:
                                degats = 0
                            else:
                                pass

                            vieEnnemi -= degats
                            ####################################

                            txtEcran = canvas.create_text(385, 602, text="Boule de feu : "+str(degats), font="Arial 16 italic", fill="black")

                    # FUITE
                    d=len(matrice4)+1
                    for i in range (0,d):
                        if coordsClique==matrice4[i-1]:
                            chanceFuir=randint(0,1)
                            if chanceFuir==0:
                                try:
                                    canvas.delete(txtEcran)
                                except:
                                    pass
                                txtEcran = canvas.create_text(385, 602, text="Fuite réussie", font="Arial 16 italic", fill="black")

                                # On met à jour la vie du joueur dans la base de données
                                db = database()
                                db.changerVie(joueur_stats[1], vieJoueur)

                                fenetre.destroy()
                                fenetre1jour=fenetreApp([coordosGrille[0], coordosGrille[1]], map_type, coordos_perso[0], coordos_perso[1], directionPerso)

                            elif chanceFuir==1:
                                try:
                                    canvas.delete(txtEcran)
                                except:
                                    pass
                                txtEcran = canvas.create_text(385, 602, text="Fuite ratée", font="Arial 16 italic", fill="black")

                                nombreTour+=1

                            else:
                                pass
                        else:
                            pass

                else:
                    joueurGele = False

                # On regarde si l'ennemi est mort
                if vieEnnemi <= 0:
                    vieEnnemi = 0
                    try:
                        canvas.delete(txtEcran)
                    except:
                        pass
                    try:
                        canvas.delete(txtVieEnnemi)
                        txtVieEnnemi = canvas.create_text(493, 507, text=vieEnnemi, fill="red", font=fontPV)
                    except:
                        pass

                    time.sleep(0.1)
                    canvas.delete(ennemiCombat)
                    fenetre.update()

                    piecesGagnees = randint(10,30)*niveau_monstres

                    # On met à jour la vie du joueur dans la base de données
                    db = database()
                    db.changerVie(joueur_stats[1], vieJoueur)
                    # Et son argent
                    argentJoueur = db.getMoney(joueur_stats[1])
                    nouveauSolde = argentJoueur + piecesGagnees
                    db.changerArgent(joueur_stats[1], nouveauSolde)

                    xpGagnee = randint(10,20)*niveau_monstres*1.5

                    # On vérifie si le joueur a gagné un niveau
                    db = database()
                    joueur_stats = db.getStats()
                    niveauJoueur = joueur_stats[5]
                    xpJoueur = joueur_stats[7] + int(xpGagnee)
                    doPlayerLvlUp = fenetreApp.verifLvlUp(xpJoueur, niveauJoueur, experiencePourLvlUp)
                    if doPlayerLvlUp == False:
                        txtEcran = canvas.create_text(385, 580, text="Ennemi mort", font="Arial 16 italic", fill="green")
                        txtEcran2 = canvas.create_text(385, 602, text="Vous avez gagné "+str(piecesGagnees)+" pièces", font="Arial 16 italic", fill="gold")
                        txtEcran3 = canvas.create_text(385, 640, text="Il vous reste "+str(experiencePourLvlUp[niveauJoueur]-xpJoueur)+" xp pour passer au niveau suivant", font="Arial 16 italic", fill="purple", width="300")
                        fenetre.update()
                    else:
                        xpJoueur = doPlayerLvlUp[1]
                        niveauJoueur = doPlayerLvlUp[2]
                        txtEcran = canvas.create_text(385, 590, text="Ennemi mort", font="Arial 16 italic", fill="green")
                        txtEcran2 = canvas.create_text(385, 612, text="Vous avez gagné "+str(piecesGagnees)+" pièces", font="Arial 16 italic", fill="gold")
                        txtEcran3 = canvas.create_text(385, 638, text="Vous êtes passé au niveau "+str(niveauJoueur)+" !", font="Arial 16 italic", fill="purple")
                        fenetre.update()
                        vieJoueur = niveauJoueur*100
                        attaqueJoueur =  attaqueDefense[0] + niveauJoueur
                        defenseJoueur = attaqueDefense[1] + niveauJoueur
                        db.newAttaqueDefense(pseudo, attaqueJoueur, defenseJoueur)

                    # On sauvegarde le niveau et l'expérience du joueur
                    db = database()
                    db.changerNiveau(pseudo, niveauJoueur)
                    db.changerXP(pseudo, xpJoueur)
                    db.changerVie(pseudo, vieJoueur)

                    time.sleep(8)

                    fenetre.destroy()
                    fenetre1jour=fenetreApp([coordosGrille[0], coordosGrille[1]], map_type, coordos_perso[0], coordos_perso[1], directionPerso)

                else:
                    # TOUR DE L'ENNEMI
                    try:
                        canvas.delete(txtTour)
                    except:
                        pass
                    try:
                        canvas.delete(txtVieEnnemi)
                        txtVieEnnemi = canvas.create_text(493, 507, text=vieEnnemi, fill="red", font=fontPV)
                    except:
                        pass

                    txtTour = canvas.create_text(385, 702, text="Tour de l'ennemi", font="Arial 16 italic", fill="red")
                    fenetre.update()
                    canvas.pack()
                    time.sleep(2)

                    ###################################
                    # Suppression du texte concernant l'attaque précédente
                    try:
                        canvas.delete(txtEcran)
                    except:
                        pass
                    ###################################

                    #######################################################################
                    typeSortEnnemi = randint(0, 2)

                    # Attaque spéciale (laser)
                    if nombreTourEnnemi%5 == 0 and nombreTourEnnemi > 1:
                        mvt=0
                        mvtSort=128

                        imageSort= tk.PhotoImage(file="imagesCombat/laser.png")
                        sort1=canvas.create_image(420,(444-190), anchor=tk.NW, image=imageSort)
                        fenetre.update()
                        time.sleep(0.01)
                        sort2=canvas.create_image(420-128,(444-190), anchor=tk.NW, image=imageSort)
                        fenetre.update()
                        time.sleep(0.01)
                        sort3=canvas.create_image(420-256,(444-190), anchor=tk.NW, image=imageSort)
                        fenetre.update()
                        time.sleep(0.01)
                        canvas.pack()

                        fenetre.update()
                        time.sleep(0.2)
                        canvas.delete(sort1)
                        fenetre.update()

                        canvas.delete(sort2)
                        fenetre.update()

                        canvas.delete(sort3)
                        fenetre.update()

                        ####################################
                        # Statistiques du combat
                        # L'attaque correspond à la moitié des dégats infligés par l'ennemi depuis le début du combat
                        ##########
                        degats = jaugeDegatsAttaqueSpe - statDefJoueur
                        if degats < 0:
                            degats = nombreTourEnnemi
                        else:
                            pass
                        ####################################
                        txtAttaqueEnnemi = "Laser"

                    # Attaque secondaire (glaçon)
                    elif typeSortEnnemi == 0:
                        mvtSort = 0

                        imageSort= tk.PhotoImage(file="imagesCombat/glacon.png")
                        mvt=0
                        for i in range (0,290):
                            fenetre.update()
                            time.sleep(.0002)
                            try:
                                canvas.delete(sort)
                            except:
                                pass

                            sort=canvas.create_image((420-mvtSort),221 , anchor=tk.NW, image=imageSort)
                            canvas.pack()
                            mvtSort+=1

                        canvas.delete(sort)
                        imageSortImpact= tk.PhotoImage(file="imagesCombat/glacon.png")
                        sortImpact=canvas.create_image((420-mvtSort),221 , anchor=tk.NW, image=imageSortImpact)
                        fenetre.update()
                        time.sleep(0.2)
                        canvas.delete(sortImpact)
                        fenetre.update()

                        ####################################
                        # Statistiques du combat
                        # L'attaque correspond aux points d'attaque de l'ennemi
                        ##########
                        degats = statAttackEnnemi - statDefJoueur
                        if degats < 0:
                            degats = 1
                        else:
                            pass
                        # Chance de geler le joueur
                        chanceGel = randint(0, 3)
                        if chanceGel == 0:
                            joueurGele = True
                        else:
                            pass
                        jaugeDegatsAttaqueSpe += degats
                        ####################################
                        txtAttaqueEnnemi = "Glaçon"

                    # Attaque principale (boule de feu)
                    else:
                        mvtSort=10

                        imageSort= tk.PhotoImage(file="imagesCombat/bouleDeFeuEnnemi.png")
                        mvt=0
                        for i in range (0,290):
                            fenetre.update()
                            time.sleep(.0002)
                            try:
                                canvas.delete(sort)
                            except:
                                pass

                            sort=canvas.create_image((420-mvtSort),221 , anchor=tk.NW, image=imageSort)
                            canvas.pack()
                            mvtSort+=1
                        canvas.delete(sort)
                        imageSortImpact= tk.PhotoImage(file="imagesCombat/bouleDeFeuImpactEnnemi.png")
                        sortImpact=canvas.create_image((420-mvtSort),221 , anchor=tk.NW, image=imageSortImpact)
                        fenetre.update()
                        time.sleep(0.2)
                        canvas.delete(sortImpact)
                        fenetre.update()

                        ####################################
                        # Statistiques du combat
                        # L'attaque correspond aux points d'attaque de l'ennemi
                        ##########
                        degats = statAttackEnnemi - statDefJoueur
                        if degats < 0:
                            degats = 1
                        else:
                            pass
                        jaugeDegatsAttaqueSpe += degats
                        ####################################
                        txtAttaqueEnnemi = "Boule de feu"

                    #######################################################################

                    try:
                        canvas.delete(txtEcran)
                    except:
                        pass

                    # 25% de chances d'esquiver l'attaque de l'ennemi
                    chanceEsquive = randint(0, 3)
                    if chanceEsquive == 0 and txtAttaqueEnnemi != "Laser":
                        txtEcran = canvas.create_text(385, 602, text=txtAttaqueEnnemi+" : esquive", font="Arial 16 italic", fill="green")
                        joueurGele = False
                    elif joueurGele == True:
                        vieJoueur -= degats
                        txtEcran = canvas.create_text(385, 602, text=txtAttaqueEnnemi+" : vous a gelé pour 1 tour", font="Arial 16 italic", fill="blue")
                        fenetre.update()
                    else:
                        vieJoueur -= degats
                        txtEcran = canvas.create_text(385, 602, text=txtAttaqueEnnemi+" : "+str(degats), font="Arial 16 italic", fill="red")

                    try:
                        canvas.delete(txtTour)
                    except:
                        pass

                    try:
                        canvas.delete(txtVieJoueur)
                        txtVieJoueur = canvas.create_text(277, 507, text=vieJoueur, fill="blue", font=fontPV)
                    except:
                        pass

                    txtTour = canvas.create_text(385, 702, text="Tour du joueur", font="Arial 16 italic", fill="blue")
                    nombreTour += 1
                    nombreTourEnnemi += 1

                    variable_fini = True

                    if joueurGele == True:
                        fenetreCombat.clicAttaque("<Button-1>", coordosGrille, map_type, coordos_perso, directionPerso)
                    else:
                        pass

                    # On regarde si le joueur est mort
                    if vieJoueur <= 0:
                        try:
                            canvas.delete(txtTour)
                        except:
                            pass
                        try:
                            canvas.delete(txtEcran)
                        except:
                            pass

                        vieJoueur = 0
                        try:
                            canvas.delete(txtVieJoueur)
                            txtVieJoueur = canvas.create_text(277, 507, text=vieJoueur, fill="blue", font=fontPV)
                        except:
                            pass
                        txtEcran = canvas.create_text(385, 602, text="Joueur mort", font="Arial 16 italic", fill="black")
                        fenetre.update()
                        time.sleep(3)

                        # On met à jour la vie du joueur dans la base de données
                        vieJoueur = niveauJoueur*100
                        db = database()
                        db.changerVie(joueur_stats[1], vieJoueur)

                        fenetre.destroy()
                        # On fait respawn le joueur dans sa maison
                        fenetre1jour=fenetreApp([6, 2], "maison", 384, 288, 1)
                    else:
                        pass

            else:
                variable_fini = True

        else:
            pass

    def utiliserSoin(event):
        global vieJoueur, canvas, txtEcran, txtVieJoueur
        # On récupère la touche pressée
        touche = event.keysym

        # On récupère les stats du joueur
        db = database()
        joueur_stats = db.getStats()

        # Utilisation des items
        if touche == "1" or touche == "ampersand":
            databaseStats = db_playerStats()
            statsItem = databaseStats.itemStats(joueur_stats[18])
            if statsItem == 0: # si il n'y a pas d'utilisable
                try:
                    canvas.delete(txtEcran)
                except:
                    pass
                txtEcran = canvas.create_text(385, 602, text="Vous n'avez aucun objet dans cet emplacement", font="Arial 16 italic", fill="red", width=250, justify="center")
            else:
                vieJoueur += statsItem
                if vieJoueur > niveauJoueur*100:
                    vieJoueur = niveauJoueur*100
                else:
                    pass
                try:
                    canvas.delete(txtEcran)
                except:
                    pass
                txtEcran = canvas.create_text(385, 602, text="Vous avez gagné "+str(statsItem)+" points de vie", font="Arial 16 italic", fill="green")

                # On ajoute la vie au joueur
                try:
                    canvas.delete(txtVieJoueur)
                except:
                    pass
                txtVieJoueur = canvas.create_text(277, 507, text=vieJoueur, fill="blue", font=fontPV)

                # On retire l'item de l'inventaire
                db = database()
                db.removeUtilisable(joueur_stats[1], "utilisable1")
                # On met à jour la vie du joueur dans la base de données
                db.changerVie(joueur_stats[1], vieJoueur)

                # On change l'image
                canvas.delete(listeImagesTkinterUtilisables[0])
                canvas.create_image(595+0*41, 487, anchor=tk.NW, image=listeImagesUtilisables[0])

        elif touche == "2" or touche == "eacute":
            databaseStats = db_playerStats()
            statsItem = databaseStats.itemStats(joueur_stats[19])
            if statsItem == 0: # si il n'y a pas d'utilisable
                try:
                    canvas.delete(txtEcran)
                except:
                    pass
                txtEcran = canvas.create_text(385, 602, text="Vous n'avez aucun objet dans cet emplacement", font="Arial 16 italic", fill="red", width=250, justify="center")
            else:
                vieJoueur += statsItem
                if vieJoueur > niveauJoueur*100:
                    vieJoueur = niveauJoueur*100
                else:
                    pass
                try:
                    canvas.delete(txtEcran)
                except:
                    pass
                txtEcran = canvas.create_text(385, 602, text="Vous avez gagné "+str(statsItem)+" points de vie", font="Arial 16 italic", fill="green")

                # On ajoute la vie au joueur
                try:
                    canvas.delete(txtVieJoueur)
                except:
                    pass
                txtVieJoueur = canvas.create_text(277, 507, text=vieJoueur, fill="blue", font=fontPV)

                # On retire l'item de l'inventaire
                db = database()
                db.removeUtilisable(joueur_stats[1], "utilisable2")
                # On met à jour la vie du joueur dans la base de données
                db.changerVie(joueur_stats[1], vieJoueur)

                # On change l'image
                canvas.delete(listeImagesTkinterUtilisables[1])
                canvas.create_image(595+1*41, 487, anchor=tk.NW, image=listeImagesUtilisables[0])

        elif touche == "3" or touche == "quotedbl":
            databaseStats = db_playerStats()
            statsItem = databaseStats.itemStats(joueur_stats[20])
            if statsItem == 0: # si il n'y a pas d'utilisable
                try:
                    canvas.delete(txtEcran)
                except:
                    pass
                txtEcran = canvas.create_text(385, 602, text="Vous n'avez aucun objet dans cet emplacement", font="Arial 16 italic", fill="red", width=250, justify="center")
            else:
                vieJoueur += statsItem
                if vieJoueur > niveauJoueur*100:
                    vieJoueur = niveauJoueur*100
                else:
                    pass
                try:
                    canvas.delete(txtEcran)
                except:
                    pass
                txtEcran = canvas.create_text(385, 602, text="Vous avez gagné "+str(statsItem)+" points de vie", font="Arial 16 italic", fill="green")

                # On ajoute la vie au joueur
                try:
                    canvas.delete(txtVieJoueur)
                except:
                    pass
                txtVieJoueur = canvas.create_text(277, 507, text=vieJoueur, fill="blue", font=fontPV)

                # On retire l'item de l'inventaire
                db = database()
                db.removeUtilisable(joueur_stats[1], "utilisable3")
                # On met à jour la vie du joueur dans la base de données
                db.changerVie(joueur_stats[1], vieJoueur)

                # On change l'image
                canvas.delete(listeImagesTkinterUtilisables[2])
                canvas.create_image(595+2*41, 487, anchor=tk.NW, image=listeImagesUtilisables[0])

        elif touche == "4" or touche == "quoteright":
            databaseStats = db_playerStats()
            statsItem = databaseStats.itemStats(joueur_stats[21])
            if statsItem == 0: # si il n'y a pas d'utilisable
                try:
                    canvas.delete(txtEcran)
                except:
                    pass
                txtEcran = canvas.create_text(385, 602, text="Vous n'avez aucun objet dans cet emplacement", font="Arial 16 italic", fill="red", width=250, justify="center")
            else:
                vieJoueur += statsItem
                if vieJoueur > niveauJoueur*100:
                    vieJoueur = niveauJoueur*100
                else:
                    pass
                try:
                    canvas.delete(txtEcran)
                except:
                    pass
                txtEcran = canvas.create_text(385, 602, text="Vous avez gagné "+str(statsItem)+" points de vie", font="Arial 16 italic", fill="green")

                # On ajoute la vie au joueur
                try:
                    canvas.delete(txtVieJoueur)
                except:
                    pass
                txtVieJoueur = canvas.create_text(277, 507, text=vieJoueur, fill="blue", font=fontPV)

                # On retire l'item de l'inventaire
                db = database()
                db.removeUtilisable(joueur_stats[1], "utilisable4")
                # On met à jour la vie du joueur dans la base de données
                db.changerVie(joueur_stats[1], vieJoueur)

                # On change l'image
                canvas.delete(listeImagesTkinterUtilisables[3])
                canvas.create_image(595+3*41, 487, anchor=tk.NW, image=listeImagesUtilisables[0])

# Classe pour le jeu
class fenetreApp:
    def __init__(self, coordosGrilleInitiale, type, pos_x, pos_y, image_initiale):
        global nomGrille, coordos_perso, directionPerso, directionPerso, grotte, flecheHaut, flecheBas, flecheGauche, flecheDroite, numeroMaison, joueur_attaque, joueur_defense, listeCompteurs, fenetre, canvas, img_perso, images_bloquees, perso_haut, perso_bas, perso_gauche, perso_droite, x, y, fleche, coordosGrille, dossierImages, maison, map_type, coordonnees_porte_maison, coordonnees_interieur_maison, nomZoneEnnemi, nomItemsInventaire, listeItemsTkinterInventaire, coordosItemsInventaire, positionItem, font_argent, argentJoueur
        fenetre = tk.Tk()
        ##################################################
        # Données propres au joueur
        ##########
        # Stats
        db = database()
        joueur_stats = db.getStats()
        ########
        # Expérience pour lvl up
        def xpNiveau(niveauMax):
            global experiencePourLvlUp
            experiencePourLvlUp = [10, 100]
            for i in range(0, niveauMax-2):
                ecartXP = experiencePourLvlUp[-1] + i*100
                experiencePourLvlUp.append(ecartXP)
            return experiencePourLvlUp
        experiencePourLvlUp = xpNiveau(100)
        ########

        # Images personnage
        # joueur_stats[3] = classe et joueur_stats[4] = sexe
        perso_haut = tk.PhotoImage(file="personnage/" + joueur_stats[3] + "_" + joueur_stats[4] + "_haut.png")
        perso_bas = tk.PhotoImage(file="personnage/" + joueur_stats[3] + "_" + joueur_stats[4] + "_bas.png")
        perso_gauche = tk.PhotoImage(file="personnage/" + joueur_stats[3] + "_" + joueur_stats[4] + "_gauche.png")
        perso_droite = tk.PhotoImage(file="personnage/" + joueur_stats[3] + "_" + joueur_stats[4] + "_droite.png")
        perso_images = [perso_haut, perso_bas, perso_gauche, perso_droite]

        ##################################################
        # Lecture des coordonnés + assignition de la carte
        ##########
        coordosGrille = coordosGrilleInitiale

        liste_map = [["map0-0.txt", "map0-1.txt", "map0-2.txt", "map0-3.txt", "map0-4.txt"], \
                    ["map1-0.txt", "map1-1.txt", "map1-2.txt", "map1-3.txt", "map1-4.txt"], \
                    ["map2-0.txt", "map2-1.txt", "map2-2.txt", "map2-3.txt", "map2-4.txt"], \
                    ["map3-0.txt", "map3-1.txt", "map3-2.txt", "map3-3.txt", "map3-4.txt"], \
                    ["map4-0.txt", "map4-1.txt", "map4-2.txt", "map4-3.txt", "map4-4.txt"], \
                    ["map5-0.txt", "map5-1.txt", "map5-2.txt", "map5-3.txt", "map5-4.txt"], \
                    ["map6-0.txt", "map6-1.txt", "map6-2.txt", "map6-3.txt", "map6-4.txt"]]

        liste_maisons = [[["donjon_map0-0.txt"], [""], [""], [""], [""]], \
                    [["grotte_map1-0.txt"], ["grotte_map1-1.txt"], [""], [""], ["donjon_map1-4.txt"]], \
                    [[""], ["grotte_map2-1.txt"], [""], [""], [""]], \
                    [["grotte_map3-0.txt"], ["grotte_map3-1.txt", "maison1_map3-1.txt"], [""], ["maison1_map3-3.txt", "maison2_map3-3.txt"], [""]], \
                    [["grotte_map4-0.txt"], [""], [""], [""], [""]], \
                    [["grotte_map5-0.txt"], [""], [""], [""], [""]], \
                    [["donjon_map6-0.txt"], [""], ["maison1_map6-2.txt"], [""], [""]]]

        images_map = [["map0-0", "map0-1", "map0-2", "map0-3", "map0-4"], \
                    ["map1-0", "map1-1", "map1-2", "map1-3", "map1-4"], \
                    ["map2-0", "map2-1", "map2-2", "map2-3", "map2-4"], \
                    ["map3-0", "map3-1", "map3-2", "map3-3", "map3-4"], \
                    ["map4-0", "map4-1", "map4-2", "map4-3", "map4-4"], \
                    ["map5-0", "map5-1", "map5-2", "map5-3", "map5-4"], \
                    ["map6-0", "map6-1", "map6-2", "map6-3", "map6-4"]]

        images_maisons = [[["donjon_map0-0"], [""], [""], [""], [""]], \
                    [["grotte_map1-0"], ["grotte_map1-1"], [""], [""], ["donjon_map1-4"]], \
                    [[""], ["grotte_map2-1"], [""], [""], [""]], \
                    [["grotte_map3-0"], ["grotte_map3-1", "maison1_map3-1"], [""], ["maison1_map3-3", "maison2_map3-3"], [""]], \
                    [["grotte_map4-0"], [""], [""], [""], [""]], \
                    [["grotte_map5-0"], [""], [""], [""], [""]], \
                    [["donjon_map6-0"], [""], ["maison1_map6-2"], [""], [""]]]

        zoneEnnemi_map = [["zoneEnnemi_map0-0.txt", "zoneEnnemi_map0-1.txt", "zoneEnnemi_map0-2.txt", "zoneEnnemi_map0-3.txt", "zoneEnnemi_map0-4.txt"], \
                    ["zoneEnnemi_map1-0.txt", "zoneEnnemi_map1-1.txt", "zoneEnnemi_map1-2.txt", "zoneEnnemi_map1-3.txt", "zoneEnnemi_map1-4.txt"], \
                    ["zoneEnnemi_map2-0.txt", "zoneEnnemi_map2-1.txt", "zoneEnnemi_map2-2.txt", "zoneEnnemi_map2-3.txt", "zoneEnnemi_map2-4.txt"], \
                    ["zoneEnnemi_map3-0.txt", "zoneEnnemi_map3-1.txt", "zoneEnnemi_map3-2.txt", "zoneEnnemi_map3-3.txt", "zoneEnnemi_map3-4.txt"], \
                    ["zoneEnnemi_map4-0.txt", "zoneEnnemi_map4-1.txt", "zoneEnnemi_map4-2.txt", "zoneEnnemi_map4-3.txt", "zoneEnnemi_map4-4.txt"], \
                    ["zoneEnnemi_map5-0.txt", "zoneEnnemi_map5-1.txt", "zoneEnnemi_map5-2.txt", "zoneEnnemi_map5-3.txt", "zoneEnnemi_map5-4.txt"], \
                    ["zoneEnnemi_map6-0.txt", "zoneEnnemi_map6-1.txt", "zoneEnnemi_map6-2.txt", "zoneEnnemi_map6-3.txt", "zoneEnnemi_map6-4.txt"]]

        zoneEnnemi_maison = [[["zoneEnnemi_donjon_map0-0.txt"], [""], [""], [""], [""]], \
                    [["zoneEnnemi_grotte_map1-0.txt"], ["zoneEnnemi_grotte_map1-1.txt"], [""], [""], ["zoneEnnemi_donjon_map1-4.txt"]], \
                    [[""], ["zoneEnnemi_grotte_map2-1.txt"], [""], [""], [""]], \
                    [["zoneEnnemi_grotte_map3-0.txt"], ["zoneEnnemi_grotte_map3-1.txt", "zoneEnnemiVIDE.txt"], [""], ["zoneEnnemiVIDE.txt", "zoneEnnemiVIDE.txt"], [""]], \
                    [["zoneEnnemi_grotte_map4-0.txt"], [""], [""], [""], [""]], \
                    [["zoneEnnemi_grotte_map5-0.txt"], [""], [""], [""], [""]], \
                    [["zoneEnnemi_donjon_map6-0.txt"], [""], ["zoneEnnemiVIDE.txt"], [""], [""]]]

        if type == "maison":
            map_type = "maison"
            nomGrille = liste_maisons[coordosGrille[0]][coordosGrille[1]][numeroMaison]
            dossierImages = images_maisons[coordosGrille[0]][coordosGrille[1]][numeroMaison]
            nomZoneEnnemi = zoneEnnemi_maison[coordosGrille[0]][coordosGrille[1]][numeroMaison]
        else:
            map_type = "map"
            nomGrille = liste_map[coordosGrille[0]][coordosGrille[1]]
            dossierImages = images_map[coordosGrille[0]][coordosGrille[1]]
            nomZoneEnnemi = zoneEnnemi_map[coordosGrille[0]][coordosGrille[1]]

        ##################################################
        # Propriétés de la fenêtre
        ##########
        # Ouverture du fichier contenant la grille
        grille = open("cartes/" + nomGrille, "r")
        lignes = grille.readlines()
        # Définition de la taille de la fenêtre (+2 pour compenser la bordure du canvas)
        x = 768+2
        y = 736
        # Ajustement à la taille de l'écran
        w = (fenetre.winfo_screenwidth()-x)/2
        h = (fenetre.winfo_screenheight()-y)/3
        # Taille + position de la fenêtre
        fenetre.geometry(str(x) + "x" + str(y) + "+" + str(int(w)) + "+" + str(int(h)))
        # dirt_intersection
        fenetre.title("Quest Master RPG | Jeu")
        # Bloquage du redimensionnement
        fenetre.maxsize(x,y)
        fenetre.minsize(x,y)

        ##################################################
        # Génération de la carte
        ##########
        # On crée un canvas en fond
        canvas = tk.Canvas(fenetre, width=x, height=y, background="#999999", borderwidth=0)
        # On force le focus sur le canvas
        canvas.focus_force()

        #########################
        # INVENTAIRE
        #####
        # Images autour de l'icone du personnage dimensions 48*48px
        # L'inventaire commence en [0, 608] jusqu'en [736, 734]

        # On récupère la classe et le sexe du personnage
        imagePerso = joueur_stats[3] + "_" + joueur_stats[4]

        ## Listes inventaire ##
        nomPersoInventaire = ["coinHautGauche", "coinHautDroite", "coinBasDroite", "coinBasGauche", imagePerso, \
                              "piecesGauche", "piecesDroite"]
        coordosPersoInventaire = [[16, 624], [64, 624], [64, 672], [16, 672], [17, 625], \
                                  [176, 656], [272, 656]]
        nomItemsInventaire = ["armePrincipale", "armeSecondaire", "bouclier", \
                              "casque", "plastron", "jambieres", "bottes", \
                              "utilisables", "utilisables", "utilisables", "utilisables"]
        coordosItemsInventaire = [[128, 624], [128, 656], [128, 688], \
                                  [176, 688], [208, 688], [240, 688], [272, 688], \
                                  [176, 624], [208, 624], [240, 624], [272, 624]]
        #######################

        # Statistiques du joueur
        joueur_lvl = joueur_stats[5]
        joueur_vie = joueur_stats[6]
        joueur_xp = joueur_stats[7]
        joueur_attaque = joueur_stats[8]
        joueur_defense = joueur_stats[9]
        joueur_argent = joueur_stats[10]

        #######################################################
        # AJOUT DES STATS DES ITEMS AUX STATS DU JOUEUR
        #############
        def addItemStatsToStats():
            global joueur_attaque, joueur_defense, listeAttaque, listeDefense
            # On récupère l'attaque et la défense de base du joueur
            db = database()
            joueur_stats = db.getStats()
            joueur_attaque = joueur_stats[8]
            joueur_defense = joueur_stats[9]
            # Pour chaque type d'item dans l'inventaire
            for i in range(0, len(nomItemsInventaire)):
                nomItemPerso = joueur_stats[i+11]
                typeItem = nomItemsInventaire[i]

                # On récupère les stats de l'item
                databaseStats = db_playerStats()
                statsItem = databaseStats.itemStats(nomItemPerso)

                listeAttaque = ["armePrincipale", "armeSecondaire"]
                listeDefense = ["bouclier", "casque", "plastron", "jambieres", "bottes"]
                # Si c'est un item offensif
                if typeItem in listeAttaque:
                    joueur_attaque += statsItem
                # Si c'est un item défensif
                elif typeItem in listeDefense:
                    joueur_defense += statsItem
                # Sinon (si c'est un utilisable)
                else:
                    pass
        addItemStatsToStats()
        #######################################################

        # ARGENT DU JOUEUR
        canvas.create_rectangle(204, 660, 276, 684, fill="#7884AB", outline="#17111A")
        font_argent = tkFont.Font(family='System', size=-24, weight='bold')
        argentJoueur = canvas.create_text(240, 672, anchor=tk.CENTER, text=str(joueur_argent), font=font_argent, fill="#17111A")

        # Rectangle avec les stats
        canvas.create_rectangle(320, 624, 496, 720, fill="#7884AB", outline="#17111A")
        # VIE / XP / ATTAQUE / DEFENSE
        # 1 ligne de stats = 24px
        font_stats = tkFont.Font(family='System', size=-18, weight='bold')
        compteurNiveau = canvas.create_text(324, 624, anchor=tk.NW, text="Niveau : "+str(joueur_lvl), font=font_stats, fill="#FFFFFF")
        compteurVie = canvas.create_text(324, 643, anchor=tk.NW, text="Vie : "+str(joueur_vie), font=font_stats, fill="#FFFFFF")
        compteurXP = canvas.create_text(324, 662, anchor=tk.NW, text="XP : "+str(joueur_xp)+"/"+str(experiencePourLvlUp[joueur_lvl]), font=font_stats, fill="#FFFFFF")
        compteurAttaque = canvas.create_text(324, 681, anchor=tk.NW, text="Attaque : "+str(joueur_attaque), font=font_stats, fill="#FFFFFF")
        compteurDefense = canvas.create_text(324, 700, anchor=tk.NW, text="Défense : "+str(joueur_defense), font=font_stats, fill="#FFFFFF")
        listeCompteurs = [compteurNiveau, compteurVie, compteurXP, compteurAttaque, compteurDefense]
        # Rectangle à droite (infos)
        font_infos = tkFont.Font(family='System', size=-18, weight='bold')
        canvas.create_rectangle(512, 624, 752, 720, fill="#FFFFFF", outline="#17111A")
        texteMap = canvas.create_text(515, 624, anchor=tk.NW, text="Appuyez sur la touche 'm' pour ouvrir la map", font=font_infos, fill="#000000", width="230")
        texteCopyrights = canvas.create_text(515, 681, anchor=tk.NW, text="Jeu crée par BEAUCHAMP Enzo et DAUNAY Florian", font=font_infos, fill="#000000", width="230")

        # ITEMS
        def placementItemInventaire(listeNom, listeCoordos, listeImages, positionDansListes, x):
            nomItemPerso = joueur_stats[x]
            path = "inventaire/" + listeNom[positionDansListes] + "/" + nomItemPerso + ".png"

            if os.path.exists(path) == True:
                listeImages.append(tk.PhotoImage(file=path))
                imageItem = canvas.create_image(listeCoordos[positionDansListes][0], listeCoordos[positionDansListes][1], anchor=tk.NW, image=listeImages[positionDansListes])
                listeItemsTkinterInventaire.append(imageItem)
            else:
                listeImages.append(tk.PhotoImage(file="inventaire/vide.png"))
                imageItem = canvas.create_image(listeCoordos[positionDansListes][0], listeCoordos[positionDansListes][1], anchor=tk.NW, image=listeImages[positionDansListes])
                listeItemsTkinterInventaire.append(imageItem)

        listeItemsInventaire = []
        listeItemsTkinterInventaire = []
        x = 10
        for i in range(0, len(nomItemsInventaire)):
            x += 1
            placementItemInventaire(nomItemsInventaire, coordosItemsInventaire, listeItemsInventaire, i, x)

        # IMAGE PERSO + PIECES
        def placementPersoInventaire(listeNom, listeCoordos, listeImages, positionDansListes):
            path = "inventaire/" + listeNom[positionDansListes] + ".png"

            if os.path.exists(path) == True:
                listeImages.append(tk.PhotoImage(file=path))
                canvas.create_image(listeCoordos[positionDansListes][0], listeCoordos[positionDansListes][1], anchor=tk.NW, image=listeImages[positionDansListes])
            else:
                listeImages.append(tk.PhotoImage(file="inventaire/vide.png"))
                canvas.create_image(listeCoordos[positionDansListes][0], listeCoordos[positionDansListes][1], anchor=tk.NW, image=listeImages[positionDansListes])

        listePersoInventaire = []
        for i in range(0, len(nomPersoInventaire)):
            placementPersoInventaire(nomPersoInventaire, coordosPersoInventaire, listePersoInventaire, i)

        ###########################

        # On récupère les paramètres du dossier des images
        moduleDossierImages = __import__("maps." + dossierImages + ".parametres", globals(), locals(), ['liste_caracteres_bloques', 'liste_caracteres_fleche', 'liste_caracteres_maison', 'coordonnees_interieur_maison', 'coordonnees_porte_maison', 'maison_shop', 'maison_grotte'], 0)
        liste_caracteres_bloques = moduleDossierImages.liste_caracteres_bloques
        images_bloquees = []
        liste_caracteres_fleche = moduleDossierImages.liste_caracteres_fleche
        fleche = []
        liste_caracteres_maison = moduleDossierImages.liste_caracteres_maison
        maison = []
        coordonnees_interieur_maison = moduleDossierImages.coordonnees_interieur_maison
        coordonnees_porte_maison = moduleDossierImages.coordonnees_porte_maison
        shop = moduleDossierImages.maison_shop
        grotte = moduleDossierImages.maison_grotte

        ############################################
        ##### PROCESSUS POUR TOUTES LES CARTES #####
        ############################################
        # On crée notre liste d'images
        liste_images = []
        stringCaracteres = "_$,;%!#&à'~^@+=-`çéabcdefghijklmnopqrstuvwxyz0123456789"
        # (pour chaque image qui existe)
        for caractere in stringCaracteres:
            path = "maps/" + dossierImages + "/" + caractere + ".png"
            if os.path.exists(path) == True:
                # On récupère l'image
                image = tk.PhotoImage(file=path)
                # Et on l'ajoute à la liste
                liste_images.append(image)
            else:
                path = "maps/" + dossierImages + "/a.png"
                image = tk.PhotoImage(file=path)
                liste_images.append(image)

        flecheHaut, flecheBas, flecheGauche, flecheDroite = [], [], [], []
        # Pour la position de l'image
        def position_image(caractere, x, y):
            try:
                # On crée une image (ici x c'est la largeur et y la hauteur)
                canvas.create_image(x*32, y*32, anchor=tk.NW, image=liste_images[stringCaracteres.find(caractere)])
                canvas.pack()
                if caractere in liste_caracteres_bloques:
                    image_b = [x*32, y*32]
                    images_bloquees.append(image_b)
                elif caractere in liste_caracteres_maison:
                    image_b = [x*32, y*32]
                    maison.append(image_b)
                elif caractere in liste_caracteres_fleche:
                    image_b = [x*32, y*32]
                    if caractere == "w":
                        flecheHaut.append(image_b)
                    elif caractere == "x":
                        flecheBas.append(image_b)
                    elif caractere == "y":
                        flecheDroite.append(image_b)
                    elif caractere == "z":
                        flecheGauche.append(image_b)

                    fleche.append(image_b)
                else:
                    pass
            except:
                pass

        # Pour chaque ligne de la grille
        for i in range (0, len(lignes)):
            # Pour chaque caractère de la ligne
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
                path = "maps/shop_" + dossierImages + "/" + caractere + ".png"
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

            # On récupère les listes relatives au shop contenant les infos sur les items
            moduleDossierShop = __import__("maps.shop_" + dossierImages + ".parametres", globals(), locals(), ['prixItems'], 0)
            nomsItems = moduleDossierShop.nomsItems
            positionInventaire = moduleDossierShop.positionInventaire
            # On récupère le prix des items dans la database
            prixItems = []
            for itemName in nomsItems:
                databaseStats = db_playerStats()
                prixItems.append(databaseStats.getPrix(itemName))

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


            texteShopLabel = tk.Label(fenetre, text="", relief="sunken", fg="black", anchor=tk.CENTER, height=4, width=41)
            texteShop = canvas.create_window(208, 512, window=texteShopLabel)

            def acheterItem(nom, prix, position, listeImages):
                global canvas, argentJoueur
                argent = db.getMoney(pseudo)
                if prix > argent:
                    texteShopLabel.configure(text="Vous n'avez pas assez d'argent.")
                else:
                    nouveauSolde = argent - prix
                    updateItem = db.changerItem(pseudo, nom, position, nouveauSolde)
                    if updateItem[0] == "Valide":
                        texteShopLabel.configure(text="Achat effectué avec succès.")

                        listeNomItemsInventaire = ["armePrincipale", "armeSecondaire", "bouclier", \
                                              "casque", "plastron", "jambieres", "bottes", \
                                              "utilisable1", "utilisable2", "utilisable3", "utilisable4"]

                        ########################################
                        # On met à jour l'item dans la barre d'inventaire
                        positionItem = listeNomItemsInventaire.index(updateItem[1])
                        imageTkinterItem.append(tk.PhotoImage(file="inventaire/" + nomItemsInventaire[positionItem] + "/" + nom + ".png"))
                        canvas.create_image(coordosItemsInventaire[positionItem][0], coordosItemsInventaire[positionItem][1], anchor=tk.NW, image=imageTkinterItem[-1])
                        ########################################
                        # On met à jour l'argent du joueur
                        try:
                            canvas.delete(argentJoueur)
                        except:
                            pass
                        argentJoueur = canvas.create_text(240, 672, anchor=tk.CENTER, text=str(nouveauSolde), font=font_argent, fill="#17111A")
                        ########################################
                        # On met à jour les statitiques du joueur dans la barre d'inventaire
                        addItemStatsToStats()

                        # Si on a acheté un item d'attaque
                        if updateItem[1] in listeAttaque:
                            # ON MET A JOUR LE COMPTEUR D'ATTAQUE
                            try:
                                canvas.delete(listeCompteurs[3])
                            except:
                                pass
                            compteurAttaque = canvas.create_text(324, 681, anchor=tk.NW, text="Attaque : "+str(joueur_attaque), font=font_stats, fill="#FFFFFF")
                            listeCompteurs[3] = compteurAttaque

                        # Sinon si on a acheté un item défensif
                        elif updateItem[1] in listeDefense:
                            # ON MET A JOUR LE COMPTEUR DE DÉFENSE
                            try:
                                canvas.delete(listeCompteurs[4])
                            except:
                                pass
                            compteurDefense = canvas.create_text(324, 700, anchor=tk.NW, text="Défense : "+str(joueur_defense), font=font_stats, fill="#FFFFFF")
                            listeCompteurs[4] = compteurDefense

                        # Sinon (si c'est un item utilisable)
                        else:
                            pass
                        ########################################

                    elif updateItem == "ErreurPlace":
                        texteShopLabel.configure(text="Vous n'avez plus de place dans votre inventaire.")
                    elif updateItem == "ErrorNom":
                        texteShopLabel.configure(text="Vous possédez déjà cet objet.")
                    # "Erreur"
                    else:
                        texteShopLabel.configure(text="Une erreur est survenue, veuillez réessayer.")

            x = 0
            imageTkinterItem = []
            for coordos in coordosBoutons:
                # ici le "lambda x=x:" permet de n'exécuter la commande que lorsque le bouton sera cliqué et on lui assigne la valeur actuelle de x (x différent pour chaque bouton)
                bouton = tk.Button(fenetre, text="      Acheter      ", command=lambda x=x: acheterItem(nomsItems[x], prixItems[x], positionInventaire[x], imageTkinterItem), cursor="hand2", height=1, borderwidth=4)
                bouton = canvas.create_window(coordos[0], coordos[1], window=bouton)
                x += 1

        else:
            pass
        ############################################
        # Position initiale du personnage selon les coordonnées du personnage (là où il était avant de quitter le jeu)
        img_perso = canvas.create_image(pos_x, pos_y, anchor=tk.NW, image=perso_images[image_initiale])
        canvas.pack()
        # Récupération des coordonnées et de la direction du perso
        coordos_perso = [pos_x, pos_y]
        directionPerso = image_initiale


        # Détection des touches pour les déplacements du personnage
        fenetre.bind("<Up>", fenetreApp.mouvement_perso)
        fenetre.bind("<z>", fenetreApp.mouvement_perso)
        fenetre.bind("<Down>", fenetreApp.mouvement_perso)
        fenetre.bind("<s>", fenetreApp.mouvement_perso)
        fenetre.bind("<Left>", fenetreApp.mouvement_perso)
        fenetre.bind("<q>", fenetreApp.mouvement_perso)
        fenetre.bind("<Right>", fenetreApp.mouvement_perso)
        fenetre.bind("<d>", fenetreApp.mouvement_perso)
        fenetre.bind("<m>", fenetreApp.map)

        fenetre.mainloop()
        ##################################################

    ####################
    # Vérification si le joueur a lvl up
    def verifLvlUp(xpJoueur, niveauActuel, listeExperienceNecessaire):
        for i in range(1,(len(listeExperienceNecessaire)+1)):
            if xpJoueur >= listeExperienceNecessaire[-i] and len(listeExperienceNecessaire)-i+1 > niveauActuel:
                totalXpNecessaire = 0
                for j in range(niveauActuel, len(listeExperienceNecessaire)-i+1):
                    totalXpNecessaire += listeExperienceNecessaire[j]
                if xpJoueur >= totalXpNecessaire:
                    newXp = xpJoueur - totalXpNecessaire
                    newNiveau = len(listeExperienceNecessaire)-i+1
                    return True, newXp, newNiveau
                else:
                    pass
            else:
                pass
        return False
    ####################

    ############################################
    ### Détection de la zone d'aggro des mobs ##
    ############################################
    def LireFichierZone(nomZoneEnnemi):
        zoneEnnemi=open("cartes/" + nomZoneEnnemi,"r")
        lignes=zoneEnnemi.readlines()

        matriceZone=[]

        for i in range (0,len(lignes)):
            j=0
            liste=[]
            for caractere in lignes[i]:
                liste.append(caractere)
                j+=1
            liste.reverse()
            del liste[0]
            liste.reverse()
            matriceZone.append(liste)

        return matriceZone

    def lectureFichierZonneEnnemi(nomZoneEnnemi):
        zoneEnnemi = open("cartes/" + nomZoneEnnemi,"r")
        lignes = zoneEnnemi.readlines()

        matriceZone = []

        for i in range (0, len(lignes)):
            j = 0
            listeLigne = []
            for caractere in lignes[i]:
                listeLigne.append(caractere)
                j += 1
            del listeLigne[-1]
            matriceZone.append(listeLigne)

        return matriceZone

    #transformation des caracteres recherchés en coordonnées
    def CoordsZoneEnnemi():
        matriceCoordsZoneEnnemi = []
        matriceZoneEnnemi = fenetreApp.lectureFichierZonneEnnemi(nomZoneEnnemi)
        # Liste contenant les probabilités de tomber sur un monstre
        ################## = # 1,  2,  3,  4,  5,  6,  7,  8,  9, X #
        listeCoordosEnnemi = [[], [], [], [], [], [], [], [], [], []]

        for i in range (0, len(matriceZoneEnnemi)):
            ligneZoneEnnemi = matriceZoneEnnemi[i]

            for j in range (0, len(ligneZoneEnnemi)):

                for k in range(1, 11):
                    if ligneZoneEnnemi[j] == str(k):
                        coordosCaseEnnemi = []
                        coordosCaseEnnemi.append(j*32)
                        coordosCaseEnnemi.append(i*32)
                        listeCoordosEnnemi[k-1].append(coordosCaseEnnemi)
                    elif ligneZoneEnnemi[j] == "X":
                        coordosCaseEnnemi = []
                        coordosCaseEnnemi.append(j*32)
                        coordosCaseEnnemi.append(i*32)
                        listeCoordosEnnemi[9].append(coordosCaseEnnemi)
                    else:
                        pass

        return listeCoordosEnnemi

    def ignore(self):
        return "break"

    def mouvement_perso(event):
        global img_perso, touche, fenetre, numeroMaison, coordos_perso
        # On récupère la position du personnage
        position_perso = canvas.coords(img_perso)
        # On récupère la touche pressée
        touche = event.keysym
        fenetre.bind("<"+touche+">", fenetreApp.ignore)
        listeCoordosEnnemi = fenetreApp.CoordsZoneEnnemi()

        if touche == "Up" or touche.upper() == "Z":
            # Direction du personnage
            directionPerso = 0
            # On récupère la position du personnage
            coordos_perso = [int(position_perso[0]), int(position_perso[1]-32)]
            # Si on va sur la porte d'une maison
            if int(position_perso[1]) > 0 and coordos_perso in maison:
                canvas.delete(img_perso)
                img_perso = canvas.create_image(coordos_perso[0], coordos_perso[1], anchor=tk.NW, image=perso_bas)
                canvas.pack()
                fenetre.destroy()
                if map_type == "map":
                    # On regarde si il y a différentes maisons
                    for coordosPorte in coordonnees_porte_maison:
                        if coordosPorte == coordos_perso:
                            numeroMaison = coordonnees_porte_maison.index(coordosPorte)
                        else:
                            pass
                    # On crée une nouvelle fenêtre
                    fenetre1jour=fenetreApp([coordosGrille[0], coordosGrille[1]], "maison", coordonnees_interieur_maison[numeroMaison][0], coordonnees_interieur_maison[numeroMaison][1], directionPerso)
                else:
                    # On crée une nouvelle fenêtre
                    fenetre1jour=fenetreApp([coordosGrille[0], coordosGrille[1]], "map", coordonnees_porte_maison[0], coordonnees_porte_maison[1], directionPerso)
            # Sinon si on va sur une flèche
            elif int(position_perso[1]) > 0 and coordos_perso in fleche:
                numeroMaison = 0
                canvas.delete(img_perso)
                img_perso = canvas.create_image(coordos_perso[0], coordos_perso[1], anchor=tk.NW, image=perso_haut)
                canvas.pack()
                fenetre.destroy()
                if coordos_perso in flecheHaut:
                    if grotte == True:
                        fenetre1jour=fenetreApp([coordosGrille[0]-1,coordosGrille[1]], "maison", coordos_perso[0], coordos_perso[1]+352, 0)
                    else:
                        fenetre1jour=fenetreApp([coordosGrille[0]-1,coordosGrille[1]], "map", coordos_perso[0], coordos_perso[1]+544, 0)
                elif coordos_perso in flecheBas:
                    if grotte == True:
                        fenetre1jour=fenetreApp([coordosGrille[0]+1,coordosGrille[1]], "maison", coordos_perso[0], coordos_perso[1]-352, 1)
                    else:
                        fenetre1jour=fenetreApp([coordosGrille[0]+1,coordosGrille[1]], "map", coordos_perso[0], coordos_perso[1]-544, 1)
                elif coordos_perso in flecheGauche:
                    if grotte == True:
                        fenetre1jour=fenetreApp([coordosGrille[0],coordosGrille[1]-1], "maison", coordos_perso[0]+288, coordos_perso[1], 2)
                    else:
                        fenetre1jour=fenetreApp([coordosGrille[0],coordosGrille[1]-1], "map", coordos_perso[0]+704, coordos_perso[1], 2)
                elif coordos_perso in flecheDroite:
                    if grotte == True:
                        fenetre1jour=fenetreApp([coordosGrille[0],coordosGrille[1]+1], "maison", coordos_perso[0]-288, coordos_perso[1], 3)
                    else:
                        fenetre1jour=fenetreApp([coordosGrille[0],coordosGrille[1]+1], "map", coordos_perso[0]-704, coordos_perso[1], 3)
            # Sinon si on est pas sur une image bloquée
            elif int(position_perso[1]) > 0 and coordos_perso not in images_bloquees:
                canvas.delete(img_perso)
                img_perso = canvas.create_image(coordos_perso[0], coordos_perso[1], anchor=tk.NW, image=perso_haut)
                canvas.pack()
                ###############
                # COMBAT
                #####
                for niveauZoneEnnemi in listeCoordosEnnemi:
                    for coordosZoneEnnemi in niveauZoneEnnemi:
                        if coordos_perso == coordosZoneEnnemi:
                            chanceCombat = listeCoordosEnnemi.index(niveauZoneEnnemi)+1
                        else:
                            pass

                # On regarde si des coordonnées ont bien été trouvées
                try:
                    chanceCombat
                # Sinon ça veut dire que le joueur est sur une case sans possibilité de combat
                except NameError:
                    chanceCombat = 0

                if chanceCombat == 10:
                    fenetreDeCombat = fenetreCombat(coordosGrille, map_type, coordos_perso, directionPerso, True)
                else:
                    nbAleatoireCombat = randint(0,9)
                    if nbAleatoireCombat < chanceCombat:
                        fenetreDeCombat = fenetreCombat(coordosGrille, map_type, coordos_perso, directionPerso, False)
                    else:
                        pass
                ###############
                # On enregistre la position du personnage
                listeCoordos = coordosGrille[0], coordosGrille[1], map_type, coordos_perso[0], coordos_perso[1], directionPerso, numeroMaison
                dbCoordos = db_coordos_perso()
                dbCoordos.changeCoordos(pseudo, listeCoordos)
            # Sinon on ne fait rien
            else:
                pass

        elif touche == "Down" or touche.upper() == "S":
            directionPerso = 1
            coordos_perso = [int(position_perso[0]), int(position_perso[1]+32)]
            # Si on va sur la porte d'une maison
            if int(position_perso[1]+32) < y-128 and coordos_perso in maison:
                canvas.delete(img_perso)
                img_perso = canvas.create_image(coordos_perso[0], coordos_perso[1], anchor=tk.NW, image=perso_bas)
                canvas.pack()
                fenetre.destroy()
                if map_type == "map":
                    # On regarde si il y a différentes maisons
                    for coordosPorte in coordonnees_porte_maison:
                        if coordosPorte == coordos_perso:
                            numeroMaison = coordonnees_porte_maison.index(coordosPorte)
                        else:
                            pass
                    # On crée une nouvelle fenêtre
                    fenetre1jour=fenetreApp([coordosGrille[0], coordosGrille[1]], "maison", coordonnees_interieur_maison[0][0], coordonnees_interieur_maison[0][1], directionPerso)
                else:
                    # On crée une nouvelle fenêtre
                    fenetre1jour=fenetreApp([coordosGrille[0], coordosGrille[1]], "map", coordonnees_porte_maison[0], coordonnees_porte_maison[1], directionPerso)
            # Sinon si on va sur une flèche
            elif int(position_perso[1]+32) < y-128 and coordos_perso in fleche:
                numeroMaison = 0
                canvas.delete(img_perso)
                img_perso = canvas.create_image(coordos_perso[0], coordos_perso[1], anchor=tk.NW, image=perso_bas)
                canvas.pack()
                fenetre.destroy()
                if coordos_perso in flecheHaut:
                    if grotte == True:
                        fenetre1jour=fenetreApp([coordosGrille[0]-1,coordosGrille[1]], "maison", coordos_perso[0], coordos_perso[1]+352, 0)
                    else:
                        fenetre1jour=fenetreApp([coordosGrille[0]-1,coordosGrille[1]], "map", coordos_perso[0], coordos_perso[1]+544, 0)
                elif coordos_perso in flecheBas:
                    if grotte == True:
                        fenetre1jour=fenetreApp([coordosGrille[0]+1,coordosGrille[1]], "maison", coordos_perso[0], coordos_perso[1]-352, 1)
                    else:
                        fenetre1jour=fenetreApp([coordosGrille[0]+1,coordosGrille[1]], "map", coordos_perso[0], coordos_perso[1]-544, 1)
                elif coordos_perso in flecheGauche:
                    if grotte == True:
                        fenetre1jour=fenetreApp([coordosGrille[0],coordosGrille[1]-1], "maison", coordos_perso[0]+288, coordos_perso[1], 2)
                    else:
                        fenetre1jour=fenetreApp([coordosGrille[0],coordosGrille[1]-1], "map", coordos_perso[0]+704, coordos_perso[1], 2)
                elif coordos_perso in flecheDroite:
                    if grotte == True:
                        fenetre1jour=fenetreApp([coordosGrille[0],coordosGrille[1]+1], "maison", coordos_perso[0]-288, coordos_perso[1], 3)
                    else:
                        fenetre1jour=fenetreApp([coordosGrille[0],coordosGrille[1]+1], "map", coordos_perso[0]-704, coordos_perso[1], 3)
            elif int(position_perso[1]+32) < y-128 and coordos_perso not in images_bloquees:
                canvas.delete(img_perso)
                img_perso = canvas.create_image(coordos_perso[0], coordos_perso[1], anchor=tk.NW, image=perso_bas)
                canvas.pack()
                ###############
                # COMBAT
                #####
                for niveauZoneEnnemi in listeCoordosEnnemi:
                    for coordosZoneEnnemi in niveauZoneEnnemi:
                        if coordos_perso == coordosZoneEnnemi:
                            chanceCombat = listeCoordosEnnemi.index(niveauZoneEnnemi)+1
                        else:
                            pass

                # On regarde si des coordonnées ont bien été trouvées
                try:
                    chanceCombat
                # Sinon ça veut dire que le joueur est sur une case sans possibilité de combat
                except NameError:
                    chanceCombat = 0

                if chanceCombat == 10:
                    fenetreDeCombat = fenetreCombat(coordosGrille, map_type, coordos_perso, directionPerso, True)
                else:
                    nbAleatoireCombat = randint(0,9)
                    if nbAleatoireCombat < chanceCombat:
                        fenetreDeCombat = fenetreCombat(coordosGrille, map_type, coordos_perso, directionPerso, False)
                    else:
                        pass
                ###############
                # On enregistre la position du personnage
                listeCoordos = coordosGrille[0], coordosGrille[1], map_type, coordos_perso[0], coordos_perso[1], directionPerso, numeroMaison
                dbCoordos = db_coordos_perso()
                dbCoordos.changeCoordos(pseudo, listeCoordos)
            else:
                pass

        elif touche == "Left" or touche.upper() == "Q":
            directionPerso = 2
            coordos_perso = [int(position_perso[0]-32), int(position_perso[1])]
            # Si on va sur la porte d'une maison
            if int(position_perso[0]) > 0 and coordos_perso in maison:
                canvas.delete(img_perso)
                img_perso = canvas.create_image(coordos_perso[0], coordos_perso[1], anchor=tk.NW, image=perso_bas)
                canvas.pack()
                fenetre.destroy()
                if map_type == "map":
                    # On regarde si il y a différentes maisons
                    for coordosPorte in coordonnees_porte_maison:
                        if coordosPorte == coordos_perso:
                            numeroMaison = coordonnees_porte_maison.index(coordosPorte)
                        else:
                            pass
                    # On crée une nouvelle fenêtre
                    fenetre1jour=fenetreApp([coordosGrille[0], coordosGrille[1]], "maison", coordonnees_interieur_maison[0][0], coordonnees_interieur_maison[0][1], directionPerso)
                else:
                    # On crée une nouvelle fenêtre
                    fenetre1jour=fenetreApp([coordosGrille[0], coordosGrille[1]], "map", coordonnees_porte_maison[0], coordonnees_porte_maison[1], directionPerso)
            # Sinon si on va sur une flèche
            elif int(position_perso[0]) > 0 and coordos_perso in fleche:
                numeroMaison = 0
                canvas.delete(img_perso)
                img_perso = canvas.create_image(coordos_perso[0], coordos_perso[1], anchor=tk.NW, image=perso_gauche)
                canvas.pack()
                fenetre.destroy()
                if coordos_perso in flecheHaut:
                    if grotte == True:
                        fenetre1jour=fenetreApp([coordosGrille[0]-1,coordosGrille[1]], "maison", coordos_perso[0], coordos_perso[1]+352, 0)
                    else:
                        fenetre1jour=fenetreApp([coordosGrille[0]-1,coordosGrille[1]], "map", coordos_perso[0], coordos_perso[1]+544, 0)
                elif coordos_perso in flecheBas:
                    if grotte == True:
                        fenetre1jour=fenetreApp([coordosGrille[0]+1,coordosGrille[1]], "maison", coordos_perso[0], coordos_perso[1]-352, 1)
                    else:
                        fenetre1jour=fenetreApp([coordosGrille[0]+1,coordosGrille[1]], "map", coordos_perso[0], coordos_perso[1]-544, 1)
                elif coordos_perso in flecheGauche:
                    if grotte == True:
                        fenetre1jour=fenetreApp([coordosGrille[0],coordosGrille[1]-1], "maison", coordos_perso[0]+288, coordos_perso[1], 2)
                    else:
                        fenetre1jour=fenetreApp([coordosGrille[0],coordosGrille[1]-1], "map", coordos_perso[0]+704, coordos_perso[1], 2)
                elif coordos_perso in flecheDroite:
                    if grotte == True:
                        fenetre1jour=fenetreApp([coordosGrille[0],coordosGrille[1]+1], "maison", coordos_perso[0]-288, coordos_perso[1], 3)
                    else:
                        fenetre1jour=fenetreApp([coordosGrille[0],coordosGrille[1]+1], "map", coordos_perso[0]-704, coordos_perso[1], 3)
            elif int(position_perso[0]) > 0 and coordos_perso not in images_bloquees:
                canvas.delete(img_perso)
                img_perso = canvas.create_image(coordos_perso[0], coordos_perso[1], anchor=tk.NW, image=perso_gauche)
                canvas.pack()
                ###############
                # COMBAT
                #####
                for niveauZoneEnnemi in listeCoordosEnnemi:
                    for coordosZoneEnnemi in niveauZoneEnnemi:
                        if coordos_perso == coordosZoneEnnemi:
                            chanceCombat = listeCoordosEnnemi.index(niveauZoneEnnemi)+1
                        else:
                            pass

                # On regarde si des coordonnées ont bien été trouvées
                try:
                    chanceCombat
                # Sinon ça veut dire que le joueur est sur une case sans possibilité de combat
                except NameError:
                    chanceCombat = 0

                if chanceCombat == 10:
                    fenetreDeCombat = fenetreCombat(coordosGrille, map_type, coordos_perso, directionPerso, True)
                else:
                    nbAleatoireCombat = randint(0,9)
                    if nbAleatoireCombat < chanceCombat:
                        fenetreDeCombat = fenetreCombat(coordosGrille, map_type, coordos_perso, directionPerso, False)
                    else:
                        pass
                ###############
                # On enregistre la position du personnage
                listeCoordos = coordosGrille[0], coordosGrille[1], map_type, coordos_perso[0], coordos_perso[1], directionPerso, numeroMaison
                dbCoordos = db_coordos_perso()
                dbCoordos.changeCoordos(pseudo, listeCoordos)
            else:
                pass

        elif touche == "Right" or touche.upper() == "D":
            directionPerso = 3
            coordos_perso = [int(position_perso[0]+32), int(position_perso[1])]
            # Si on va sur la porte d'une maison
            if int(position_perso[0]) < y and coordos_perso in maison:
                canvas.delete(img_perso)
                img_perso = canvas.create_image(coordos_perso[0], coordos_perso[1], anchor=tk.NW, image=perso_bas)
                canvas.pack()
                fenetre.destroy()
                if map_type == "map":
                    # On regarde si il y a différentes maisons
                    for coordosPorte in coordonnees_porte_maison:
                        if coordosPorte == coordos_perso:
                            numeroMaison = coordonnees_porte_maison.index(coordosPorte)
                        else:
                            pass
                    # On crée une nouvelle fenêtre
                    fenetre1jour=fenetreApp([coordosGrille[0], coordosGrille[1]], "maison", coordonnees_interieur_maison[0][0], coordonnees_interieur_maison[0][1], directionPerso)
                else:
                    # On crée une nouvelle fenêtre
                    fenetre1jour=fenetreApp([coordosGrille[0], coordosGrille[1]], "map", coordonnees_porte_maison[0], coordonnees_porte_maison[1], directionPerso)
            # Sinon si on va sur une flèche
            elif int(position_perso[0]) < y and coordos_perso in fleche:
                numeroMaison = 0
                canvas.delete(img_perso)
                img_perso = canvas.create_image(coordos_perso[0], coordos_perso[1], anchor=tk.NW, image=perso_droite)
                canvas.pack()
                fenetre.destroy()
                if coordos_perso in flecheHaut:
                    if grotte == True:
                        fenetre1jour=fenetreApp([coordosGrille[0]-1,coordosGrille[1]], "maison", coordos_perso[0], coordos_perso[1]+352, 0)
                    else:
                        fenetre1jour=fenetreApp([coordosGrille[0]-1,coordosGrille[1]], "map", coordos_perso[0], coordos_perso[1]+544, 0)
                elif coordos_perso in flecheBas:
                    if grotte == True:
                        fenetre1jour=fenetreApp([coordosGrille[0]+1,coordosGrille[1]], "maison", coordos_perso[0], coordos_perso[1]-352, 1)
                    else:
                        fenetre1jour=fenetreApp([coordosGrille[0]+1,coordosGrille[1]], "map", coordos_perso[0], coordos_perso[1]-544, 1)
                elif coordos_perso in flecheGauche:
                    if grotte == True:
                        fenetre1jour=fenetreApp([coordosGrille[0],coordosGrille[1]-1], "maison", coordos_perso[0]+288, coordos_perso[1], 2)
                    else:
                        fenetre1jour=fenetreApp([coordosGrille[0],coordosGrille[1]-1], "map", coordos_perso[0]+704, coordos_perso[1], 2)
                elif coordos_perso in flecheDroite:
                    if grotte == True:
                        fenetre1jour=fenetreApp([coordosGrille[0],coordosGrille[1]+1], "maison", coordos_perso[0]-288, coordos_perso[1], 3)
                    else:
                        fenetre1jour=fenetreApp([coordosGrille[0],coordosGrille[1]+1], "map", coordos_perso[0]-704, coordos_perso[1], 3)
            elif int(position_perso[0]) < y and coordos_perso not in images_bloquees:
                canvas.delete(img_perso)
                img_perso = canvas.create_image(coordos_perso[0], coordos_perso[1], anchor=tk.NW, image=perso_droite)
                canvas.pack()
                ###############
                # COMBAT
                #####
                for niveauZoneEnnemi in listeCoordosEnnemi:
                    for coordosZoneEnnemi in niveauZoneEnnemi:
                        if coordos_perso == coordosZoneEnnemi:
                            chanceCombat = listeCoordosEnnemi.index(niveauZoneEnnemi)+1
                        else:
                            pass

                # On regarde si des coordonnées ont bien été trouvées
                try:
                    chanceCombat
                # Sinon ça veut dire que le joueur est sur une case sans possibilité de combat
                except NameError:
                    chanceCombat = 0

                if chanceCombat == 10:
                    fenetreDeCombat = fenetreCombat(coordosGrille, map_type, coordos_perso, directionPerso, True)
                else:
                    nbAleatoireCombat = randint(0,9)
                    if nbAleatoireCombat < chanceCombat:
                        fenetreDeCombat = fenetreCombat(coordosGrille, map_type, coordos_perso, directionPerso, False)
                    else:
                        pass
                ###############
                # On enregistre la position du personnage
                listeCoordos = coordosGrille[0], coordosGrille[1], map_type, coordos_perso[0], coordos_perso[1], directionPerso, numeroMaison
                dbCoordos = db_coordos_perso()
                dbCoordos.changeCoordos(pseudo, listeCoordos)
            else:
                pass

        try:
            fenetre.after(50, fenetreApp.bindit)
        except:
            pass

    def bindit():
        try:
            fenetre.bind("<Up>", fenetreApp.mouvement_perso)
            fenetre.bind("<z>", fenetreApp.mouvement_perso)
            fenetre.bind("<Down>", fenetreApp.mouvement_perso)
            fenetre.bind("<s>", fenetreApp.mouvement_perso)
            fenetre.bind("<Left>", fenetreApp.mouvement_perso)
            fenetre.bind("<q>", fenetreApp.mouvement_perso)
            fenetre.bind("<Right>", fenetreApp.mouvement_perso)
            fenetre.bind("<d>", fenetreApp.mouvement_perso)
        except:
            pass

    def map(event):
        # On ferme le jeu
        fenetre.destroy()

        #####################
        # On crée la fenêtre de la map
        fenetreMap = tk.Tk()
        # Dimensions de l'écran
        screen_width = fenetreMap.winfo_screenwidth()
        screen_height = fenetreMap.winfo_screenheight()
        # Dimensions de la frame
        x = 963
        y = 762
        x_offset = int((screen_width-x)/2)
        y_offset = int((screen_height-y)/3)-20
        # Taille (largeur x hauteur + x_offset + y_offset)
        fenetreMap.geometry("%sx%s+%s+%s" % (x, y, x_offset, y_offset))
        # Titre
        fenetreMap.title("Quest Master RPG | Carte")

        # On crée un canvas en fond
        canvas = tk.Canvas(fenetreMap, width=x, height=y, background="#999999", borderwidth=0)
        # On force le focus sur le canvas
        canvas.focus_force()

        # Points de position de chacune des 9 images composant la carte
        listeCoordosImagesMap = [[0,0], [0,254], [0,508], \
                                [321,0], [321,254], [321,508], \
                                [642,0], [642,254], [642,508]]

        coordosPositionGrilleMap = [[-1, -1], [0, -1], [1, -1], \
                                [-1, 0], [0, 0], [1, 0], \
                                [-1, 1], [0, 1], [1, 1]]

        imagesMap = []
        for posCoordosGrilleMap in coordosPositionGrilleMap:
            positionDansListe = coordosPositionGrilleMap.index(posCoordosGrilleMap)
            try:
                imagesMap.append(tk.PhotoImage(file="carteJeu/mapsInGame/map"+str(coordosGrille[0]+posCoordosGrilleMap[0])+"-"+str(coordosGrille[1]+posCoordosGrilleMap[1])+".png"))
                canvas.create_image(listeCoordosImagesMap[positionDansListe][0], listeCoordosImagesMap[positionDansListe][1], anchor=tk.NW, image=imagesMap[positionDansListe])
                canvas.pack()
            except:
                imagesMap.append(tk.PhotoImage(file="carteJeu/mapsInGame/exterieurMap.png"))
                canvas.create_image(listeCoordosImagesMap[positionDansListe][0], listeCoordosImagesMap[positionDansListe][1], anchor=tk.NW, image=imagesMap[positionDansListe])
                canvas.pack()

        # Image indiquant la position du personnage
        imageVousEtesIci = tk.PhotoImage(file="carteJeu/vousEtesIci.png")
        canvas.create_image(x/2, y/2, anchor=tk.CENTER, image=imageVousEtesIci)
        canvas.pack()

        def closeMap(event):
            fenetreMap.destroy()

        fenetreMap.bind('<m>', closeMap)
        fenetreMap.bind('<Escape>', closeMap)

        # Boucle
        fenetreMap.mainloop()
        ####################

        # Quand l'utilisateur ferme la map on relance le jeu
        fenetre1jour = fenetreApp([coordosGrille[0], coordosGrille[1]], map_type, coordos_perso[0], coordos_perso[1], directionPerso)

##############-------------------##############
# Affichage de la première fenêtre
fenetre = firstPage()
