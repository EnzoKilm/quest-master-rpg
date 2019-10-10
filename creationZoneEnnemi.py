##########################################
#            Quest Master RPG            #
#          Programme secondaire          #
# BEAUCHAMP Enzo et DAUNAY Florian (721) #
#      Projet final - ISN 2018-2019      #
#    Lycée Montesquieu, 72000 Le Mans    #
##########################################

while True:
    nomMap = input("Nom de la map : ")
    fichierMap = open("cartes/" + nomMap + ".txt","r")
    lignesMap = fichierMap.readlines()

    listeCaracteresChemin = []
    while True:
        caractereChemin = input("Caractère du chemin : ")
        if caractereChemin == "":
            break
        else:
            listeCaracteresChemin.append(caractereChemin)

    for ligne in lignesMap:
        position = lignesMap.index(ligne)
        if ligne[len(ligne)-1:] == "\n":
            ligne = ligne[:-1]
        else:
            pass
        for caractereMap in ligne:
            for caracChemin in listeCaracteresChemin:
                if caractereMap == caracChemin:
                    ligne = ligne.replace(caractereMap, "!", 1)
                else:
                    pass
        lignesMap[position] = ligne


    listeCaractereBloque = []
    while True:
        caractereBloque = input("Caractère bloqué : ")
        if caractereBloque == "":
            break
        else:
            listeCaractereBloque.append(caractereBloque)

    for ligne in lignesMap:
        position = lignesMap.index(ligne)
        if ligne[len(ligne)-1:] == "\n":
            ligne = ligne[:-1]
        else:
            pass
        for caractereMap in ligne:
            for caracBloque in listeCaractereBloque:
                if caractereMap == caracBloque:
                    ligne = ligne.replace(caractereMap, "?", 1)
                else:
                    pass
        lignesMap[position] = ligne


    listeCaracterePasBloque = []
    while True:
        caracterePasBloque = input("Caractère pas bloqué : ")
        if caracterePasBloque == "":
            break
        else:
            listeCaracterePasBloque.append(caracterePasBloque)

    for ligne in lignesMap:
        position = lignesMap.index(ligne)
        if ligne[len(ligne)-1:] == "\n":
            ligne = ligne[:-1]
        else:
            pass
        for caractereMap in ligne:
            for caracPasBloque in listeCaracterePasBloque:
                if caractereMap == caracPasBloque:
                    ligne = ligne.replace(caractereMap, ".", 1)
                else:
                    pass
        lignesMap[position] = ligne

    coordosCaracteres = [[-1, -1], [0, -1], [1, -1], \
                        [-1, 0], [0, 0], [1, 0], \
                        [-1, 1], [0, 1], [1, 1]]

    newMap = []
    for ligne in lignesMap:
        newMap.append(list(ligne))

    def changerAutour(caractereAchanger, caractereAmettre):
        numeroLigne = -1
        for ligne in newMap:
            numeroLigne += 1
            numeroCaractere = -1
            for caractere in ligne:
                numeroCaractere += 1
                if caractere == caractereAchanger:
                    for coordos in coordosCaracteres:
                        try:
                            caractereAutour = newMap[numeroLigne+coordos[0]][numeroCaractere+coordos[1]]
                        except:
                            caractereAutour = "?"

                        if caractereAutour == ".":
                            newMap[numeroLigne+coordos[0]][numeroCaractere+coordos[1]] = caractereAmettre
                        else:
                            pass

        if caractereAmettre == "9":
            numeroLigne = -1
            for ligne in newMap:
                numeroLigne += 1
                numeroCaractere = -1
                for caractere in ligne:
                    numeroCaractere += 1
                    if caractere == ".":
                        newMap[numeroLigne][numeroCaractere] = caractereAmettre
                    elif caractere == "?":
                        newMap[numeroLigne][numeroCaractere] = "0"
                    elif caractere == "!":
                        newMap[numeroLigne][numeroCaractere] = "0"
                    else:
                        pass
        else:
            pass


    listeCaracteresAchanger = ["!", "0", "1", "2", "3", "4", "5", "6", "7", "8"]
    for caractere in listeCaracteresAchanger:
        if caractere == "!":
            changerAutour(caractere, "0")
        else:
            changerAutour(caractere, str(int(caractere)+1))

    mapFinale = []
    for ligne in newMap:
        newLigne = ""
        for caractere in ligne:
            newLigne += caractere
        mapFinale.append(newLigne)
        print(newLigne)

    sauvegardeFichier = open("cartes/zoneEnnemi_"+nomMap+".txt","w")
    for ligne in mapFinale:
        sauvegardeFichier.write(ligne+"\n")
    sauvegardeFichier.close()
