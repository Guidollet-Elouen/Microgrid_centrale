import pulp
import numpy as np


def usine(jour,dt,l1dem,lp):
    ##Constante de l'usine
    pc1 = 0.95  # coeff de performance de charge
    pd1 = 1 / 0.95  # coeff de performance de decharge
    capa1 = 30  # capacite de la batterie
    pmax1 = 10  # puissance maximale
    ##Declaration des dictionnaires
    batterie1={}#Etat de charge de la batterie en KWh
    lbatplus1={}#Puissance de charge de la batterie en KW
    lbatmoins1={}#Puissance de décharge de la batterie en KW
    charge1={} #Indicateur de charge (si 0 on décharge)
    l1={} #Demande total d'électricité
    ##Boucle sur les jours et les heures
    for t in range(int(jour*24/dt)):
        ##Declaration des variables pour un temps t
        batterie1[t]=pulp.LpVariable("batterie1_"+str(t), 0.0, capa1)#variable batterie au temps t avec son min et max
        lbatplus1[t]=pulp.LpVariable("lbatplus1_"+str(t), 0.0, pmax1)#variable lbatplus au temps t avec son min et max
        lbatmoins1[t]=pulp.LpVariable("lbatmoins1_"+str(t), 0.0, pmax1)#variable lbatmoinsau temps t avec son min et max
        charge1[t]=pulp.LpVariable("charge1_"+str(t), cat="Binary") #variable binaire de charge
        l1[t]=lbatplus1[t]-lbatmoins1[t]+l1dem[t] #Conso total d'élec
        ##Declaration des contraintes
        lp+=lbatmoins1[t]<=pmax1*(1-charge1[t]),"contrainte_decharge1_"+str(t) #Contrainte du BIGM
        lp += lbatplus1[t] <= pmax1 * charge1[t], "contrainte_charge1_" + str(t) #Contrainte du BIGM
        if t==0:
            lp+=batterie1[t]==0+(pc1*lbatplus1[t]-lbatmoins1[t]*pd1)*dt,"contrainte_batterie1_"+str(t) #Evolution de la batterie
        else:
            lp+=batterie1[t]==batterie1[t-1]+(pc1*lbatplus1[t]-lbatmoins1[t]*pd1)*dt,"contrainte_batterie1_"+str(t) #Evolution de la batterie
    #lp.setObjective(pulp.lpSum(l1[t]*landa for t in range(int(jour*dt*24))))
    return l1,lbatplus1,lbatmoins1

def datacenter(jour,dt,l2IT,PHW,lp):
    ##Constante du data center
    EER = 4  # efficacité énergetique du système
    COPCS = EER + 1
    Consomax = 10  # maximum de vente d'eau chaude
    e = 0.5  # efficacite thermale
    TCOM = 60  # temperature de consommation de l'eau
    TR = 35  # temperature de sortie de l'eau
    COPHP = TCOM * e / (TCOM - TR)
    ##Calcul des listes de consommation à partir de l2IT
    LNF2 = []
    HR2 = []
    for i in range(int(24*jour/dt)):
        LNF2.append((1 + 1 / (EER * dt)) * l2IT[i])
        HR2.append((COPCS / EER) * l2IT[i])
    ##Declaration de la variable alpha2
    alpha2={} #Coefficient indiquant la part de notre chaleur que l'on utilise pour chauffer de l'eau
    L2HP={}
    HDC={}
    ##Boucle sur les jours et les heures
    for t in range(int(jour*24/dt)):
        alpha2[t]=pulp.LpVariable("alpha2_"+str(t), 0.0, 1)
        L2HP[t]=alpha2[t]*HR2[t]/((COPHP-1)*dt)
        HDC[t]=COPHP*dt*L2HP[t]
        lp+=HDC[t]<=Consomax,"contrainte_vente_eau2_"+str(t) #Contrainte de vente d'eau chaude
    #lp.setObjective(pulp.lpSum((LNF2[t]+L2HP[t])*landa-HDC[t]*PHW[t] for t in range(int(jour*dt*24))))
    return LNF2,L2HP,HDC

def panneaux_solaires(jour,dt,l3donne,lp):
    ##Constante des panneaux solaires
    pc3 = 0.95  # coeff de performance de charge
    pd3 = 1 / 0.95  # coeff de performance de decharge
    capa3 = 30  # capacite de la batterie
    pmax3 = 10  # puissance maximale
    ##Declaration des vdictionnaires
    batterie3={} #Etat de charge de la batterie en KWh
    lbatplus3={} #Puissance de charge de la batterie en KW
    lbatmoins3={} #Puissance de decharge de la batterie en KM
    charge3={} #Indicateur de charge (si 0 on décharge)
    l3={} #demande total d'électricité (vente ici)
    ##Boucle sur les jours et les heures
    for t in range(int(jour*24/dt)):
        ##Declaration des variables pour un temps t
        batterie3[t]=pulp.LpVariable("batterie3_"+str(t), 0.0, capa3) #variable batterie au temps t avec son min et max
        lbatplus3[t]=pulp.LpVariable("lbatplus3_"+str(t), 0.0, pmax3 ) #variable lbatplus au temps t avec son min et max
        lbatmoins3[t]=pulp.LpVariable("lbatmoins3_"+str(t), 0.0, pmax3) #variable lbatmoins au temps t avec son min et max
        charge3[t]=pulp.LpVariable("charge3_"+str(t), cat="Binary") #variable binaire de charge
        l3[t]=lbatplus3[t]-lbatmoins3[t]-l3donne[t] #Conso total d'élec (négatif ici en géneral)
        ##Declaration des contraintes
        lp+=lbatmoins3[t]<=pmax3*(1-charge3[t]),"contrainte_decharge3_"+str(t) #Contrainte du BIGM
        lp += lbatplus3[t] <= pmax3 * charge3[t], "contrainte_charge3_" + str(t) #Contrainte du BIGM
        if t==0:
            lp+=batterie3[t]==0+(pc3*lbatplus3[t]-lbatmoins3[t]*pd3)*dt,"contrainte_batterie3_"+str(t) #Evolution de la batterie
        else:
            lp+=batterie3[t]==batterie3[t-1]+(pc3*lbatplus3[t]-lbatmoins3[t]*pd3)*dt,"contrainte_batterie3_"+str(t) #Evolution de la batterie
    #lp.setObjective(pulp.lpSum(l3[t]*landa for t in range(int(jour*dt*24))))
    return l3,lbatplus3,lbatmoins3

def charge_voiture(jour,dt,lp,tdepart,tarrivee,k):
    ##Constante
    pc4=0.95 #coeff de performance de charge
    pd4=1/0.95 #coeff de performance de decharge
    capamax4=40 #capacite maximale de la batterie d'une voiture
    capamin4=10 #capacite minimale de la batterie au depart de la voiture
    pmaxtot4=40 #puissance maximale de charge ou decharge
    pmaxrapide4=22 #puissance maximale de charge d'un chargeur rapide
    pmaxlent4=3#puissance maximale de charge d'un chargeur lent  ##Probleme si pmaxlent<8
    coutvoyage=4 #depense energetique du deplacement quotidien
    batterie_initiale=0 #choix de la charge initiale de la batterie
    ##Declaration des dictionnaires
    batterie4={} #Etat de charge de la batterie des voitures en KWh
    lbatplus4={}#Puissance de charge de la batterie des voitures en KW
    lbatmoins4={} #Puissance de décharge de la batterie des voitures en KW
    charge4={} #Indicateur de charge des voitures (si 0 on décharge)
    crapide4={}#Indicateur de si on utilise un chargeur rapide
    clent4={}#Indicateur de si on utilise un chargeur lent
    l4={}; #Demande total d'électricité
    ##Debut des boucles sur les jours, les heures et les voitures
    for j in range(jour):
        for t in range(int(24/dt)):
            treel=t+j*int(24/dt)# definit un temps reel pour avoir des dictionnaires à 2 dimension et non à 3
            ##Declaration des "sous-dictionnaires"
            batterie4[treel]={}
            lbatplus4[treel]={}
            lbatmoins4[treel]={}
            charge4[treel]={}
            crapide4[treel]={}
            clent4[treel]={}
            for v in range(k):
                ##Declaration de toutes les variables pour 1 voiture et 1 temps
                batterie4[treel][v]=pulp.LpVariable("batterie4__%i_%i_%i"%(j,t,v), 0.0, capamax4) #variable batterie des voitures au temps t avec son min et max
                lbatplus4[treel][v]=pulp.LpVariable("lbatplus4__%i_%i_%i"%(j,t,v), 0.0, pmaxrapide4)#variable lbatplus des voitures au temps t avec son min et max
                lbatmoins4[treel][v]=pulp.LpVariable("lbatmoins4__%i_%i_%i"%(j,t,v), 0.0, pmaxrapide4)#variable lbatmoins des voitures au temps t avec son min et max
                charge4[treel][v]=pulp.LpVariable("charge4__%i_%i_%i"%(j,t,v), cat="Binary") #variable binaire de charge des voitures
                crapide4[treel][v] = pulp.LpVariable("crapide4__%i_%i_%i"%(j,t,v), cat="Binary")#Variable binaire d'utilisation d'un chargeur rapide
                clent4[treel][v] = pulp.LpVariable("clent4__%i_%i_%i"%(j,t,v), cat="Binary")#Variable binaire d'utilisation d'un chargeur lent
                ##Contrainte d'une voiture v au temps treel
                lp+=lbatmoins4[treel][v]<=pmaxrapide4*(1-charge4[treel][v]),"contrainte_decharge4__%i_%i_%i"%(j,t,v) #Contrainte du BIGM
                lp += lbatplus4[treel][v] <= pmaxrapide4 * charge4[treel][v], "contrainte_charge4__%i_%i_%i"%(j,t,v) #Contrainte du BIGM
                lp += lbatplus4[treel][v] <= pmaxrapide4 * crapide4[treel][v]+pmaxlent4*clent4[treel][v], "contrainte_charge_rapide/lent4__%i_%i_%i"%(j,t,v) #Contrainte du chargeur rapide/lent
                lp += lbatmoins4[treel][v] <= pmaxrapide4 * crapide4[treel][v]+pmaxlent4*clent4[treel][v], "contrainte_decharge_rapide/lent4__%i_%i_%i"%(j,t,v) #Contrainte du chargeur rapide/lent
                ##Continuite de la batterie
                if treel==0:
                     lp+=batterie4[treel][v]==batterie_initiale+(pc4*lbatplus4[treel][v]-lbatmoins4[treel][v]*pd4)*dt,"contrainte_batterie4_avant_depart__%i_%i_%i"%(j,t,v) #Evolution de la batterie
                if treel>0 and t+1!=tarrivee[v][j]:
                    lp+=batterie4[treel][v]==batterie4[treel-1][v]+(pc4*lbatplus4[treel][v]-lbatmoins4[treel][v]*pd4)*dt,"contrainte_batterie4_avant_depart__%i_%i_%i"%(j,t,v) #Evolution de la batterie
                if t==tdepart[v][j]:
                    lp+=batterie4[treel][v]>=capamin4,"contrainte_batterie4_depart_%i_%i"%(j,v) #Etat des batteries au depart
                if t+1==tarrivee[v][j]:
                    lp+=batterie4[treel][v]==batterie4[tdepart[v][j]+j*int(24/dt)][v]-coutvoyage,"contrainte_batterie4_arrivee_%i_%i"%(j,v) #Etat des batteries à l'arrivée
                ##Continuite de la position sur les chargeurs(rapide ou non)
                if (treel>0 and t<=tdepart[v][j]):
                    lp+=crapide4[treel][v]==crapide4[treel-1][v],"continuite_crapide_avant_depart_%i_%i_%i"%(j,t,v)
                    lp+=clent4[treel][v]==clent4[treel-1][v],"continuite_clent_avant_depart_%i_%i_%i"%(j,t,v)
                if (t<tarrivee[v][j] and t>tdepart[v][j]):
                    lp+=crapide4[treel][v]==0,"continuite_crapide_deplacement_%i_%i_%i"%(j,t,v)
                    lp+=clent4[treel][v]==0,"continuite_clent_deplacement_%i_%i_%i"%(j,t,v)
                if t>tarrivee[v][j]:
                    lp+=crapide4[treel][v]==crapide4[treel-1][v],"continuite_crapide_avant_depart_%i_%i_%i"%(j,t,v)
                    lp+=clent4[treel][v]==clent4[treel-1][v],"continuite_clent_apres_arrivee_%i_%i_%i"%(j,t,v)
                lp+=clent4[treel][v]+crapide4[treel][v]<=1,"choix_borne_rapide_lent_%i_%i_%i"%(j,t,v)
            ##PContraintes communes aux 4 voitures
            l4[treel]=pulp.lpSum(lbatplus4[treel][v]-lbatmoins4[treel][v] for v in range(k)) #Conso total d'élec
            lp+= l4[treel]<=40,"Contrainte_charge_maximale_total_4_%i_%i"%(j,t)
            lp += l4[treel] >= -40, "Contrainte_decharge_maximale_total_4_%i_%i"%(j,t)
            lp+= pulp.lpSum(crapide4[treel][v] for v in range(k))<=2,"Contrainte_utilisation_chargeur_rapide_4_%i_%i"%(j,t)
            lp+= pulp.lpSum(clent4[treel][v] for v in range(k))<=2,"Contrainte_utilisation_chargeur_lent_4_%i_%i"%(j,t)
    #lp.setObjective(pulp.lpSum([pulp.lpSum(lbatplus4[t][v]-lbatmoins4[t][v] for v in range(k)) for t in range(int(jour*24/dt))]))
    return l4,lbatplus4,lbatmoins4,batterie4,charge4

def optiglobal(jour,dt,prix_tonne,l1dem,l2IT,PHW,l3donne,tdepart,tarrivee,jour_initial):
    # Choix des tarifs
    conso_abo = [6, 9, 12, 15, 18, 24, 30, 36]
    prixcreux = 0.1230  # 22h30 à 6h30
    prixplein = 0.1580
    tarif_abo = (np.array([123.6, 151.32, 177.24, 201.36, 223.68, 274.68, 299.52, 337.56]) * jour / 365)
    cout_surplus = 6.34 * jour / 365
    nb_voiture = 4
    #Calcul tarif
    emission_saison = {'hiver': [40.0, 39.0, 37.0, 34.0, 33.0, 29.0, 26.0, 22.0, 23.0, 23.0, 23.0, 24.0, 24.0, 24.0, 24.0, 24.0, 24.0, 24.0, 26.0, 26.0, 26.0, 26.0, 26.0, 26.0, 26.0,26.0, 25.0, 26.0, 26.0, 26.0, 28.0, 29.0, 30.0, 33.0, 35.0, 36.0, 37.0, 39.0, 40.0, 41.0, 41.0, 41.0, 41.0, 41.0, 40.0, 40.0, 40.0, 38.0, 37.0, 38.0, 36.0, 36.0, 36.0, 38.0, 36.0, 36.0, 36.0, 36.0, 36.0, 35.0, 37.0, 41.0, 43.0, 43.0, 44.0,44.0, 45.0, 45.0, 45.0, 44.0, 44.0, 44.0, 44.0, 43.0, 43.0, 43.0, 43.0, 44.0, 43.0, 42.0, 42.0, 43.0, 43.0, 43.0, 42.0, 42.0, 43.0, 43.0, 42.0, 42.0, 41.0, 42.0, 38.0, 39.0, 38.0, 36.0, 35.0, 26.0, 26.0, 28.0, 27.0, 27.0, 27.0, 28.0, 27.0,27.0, 27.0, 27.0, 28.0, 29.0, 31.0, 36.0, 38.0, 39.0, 41.0, 41.0, 40.0, 39.0, 39.0, 37.0, 37.0, 37.0, 39.0, 39.0, 39.0, 40.0, 42.0, 43.0, 44.0, 44.0, 44.0, 44.0, 44.0, 43.0, 44.0, 44.0, 43.0, 44.0, 44.0, 44.0, 42.0, 41.0, 41.0, 37.0, 37.0,34.0, 35.0, 35.0, 36.0, 35.0, 33.0, 34.0, 33.0, 33.0, 32.0, 32.0, 34.0, 34.0, 34.0, 36.0, 37.0, 39.0, 38.0, 39.0, 38.0, 39.0, 38.0, 39.0, 39.0, 39.0, 39.0, 39.0, 39.0, 39.0, 39.0, 40.0, 41.0, 43.0, 42.0, 44.0, 43.0, 43.0, 42.0, 42.0, 42.0,43.0, 42.0, 41.0, 40.0, 42.0, 43.0, 43.0, 43.0, 43.0, 42.0, 41.0, 42.0, 42.0, 42.0, 43.0, 43.0, 43.0, 42.0, 42.0, 44.0, 43.0, 43.0, 43.0, 44.0, 42.0, 42.0, 40.0, 40.0, 40.0, 40.0, 41.0, 42.0, 42.0, 42.0, 42.0, 41.0, 41.0, 42.0, 43.0, 44.0,44.0, 44.0, 45.0, 44.0, 43.0, 43.0, 43.0, 44.0, 44.0, 45.0, 45.0, 44.0, 44.0, 46.0, 45.0, 45.0, 37.0, 35.0, 34.0, 34.0, 35.0, 33.0, 31.0, 31.0, 31.0, 31.0, 32.0, 36.0, 41.0, 43.0, 43.0, 42.0, 45.0, 49.0, 49.0, 50.0, 51.0, 52.0, 46.0, 46.0,45.0, 45.0, 46.0, 46.0, 47.0, 47.0, 49.0, 49.0, 48.0, 47.0, 47.0, 44.0, 42.0, 41.0, 41.0, 41.0, 41.0, 43.0, 43.0, 43.0, 42.0, 44.0, 43.0, 44.0, 40.0, 41.0, 40.0, 40.0, 40.0, 40.0, 40.0, 40.0, 40.0, 40.0, 44.0, 46.0, 48.0, 47.0, 45.0, 43.0,43.0, 42.0, 42.0, 42.0, 42.0, 42.0, 41.0, 41.0, 42.0, 41.0, 43.0, 43.0, 43.0, 44.0, 44.0, 44.0, 44.0, 44.0, 44.0, 43.0, 43.0, 43.0, 43.0, 43.0, 43.0, 43.0, 42.0, 40.0, 39.0, 38.0, 35.0], 'ete': [13.0, 13.0, 13.0, 13.0, 13.0, 14.0, 14.0, 14.0, 14.0, 15.0, 14.0, 15.0, 14.0, 14.0, 14.0, 14.0,14.0, 14.0, 14.0, 13.0, 14.0, 14.0, 14.0, 13.0, 13.0, 13.0, 13.0, 13.0, 13.0, 14.0, 14.0, 15.0, 16.0, 17.0,17.0, 16.0, 17.0, 19.0, 18.0, 18.0, 18.0, 19.0,19.0, 20.0, 20.0, 21.0, 20.0, 20.0, 21.0, 21.0, 21.0, 22.0, 22.0, 22.0, 22.0, 21.0,21.0, 22.0, 22.0, 25.0, 26.0, 28.0, 31.0, 32.0, 31.0, 30.0, 29.0, 28.0, 28.0, 28.0, 27.0, 26.0, 27.0, 26.0,27.0, 28.0, 27.0, 28.0, 29.0, 30.0, 29.0, 30.0,30.0, 30.0, 31.0, 30.0, 30.0, 30.0, 30.0, 31.0, 31.0, 31.0, 32.0, 32.0, 31.0, 31.0,31.0, 33.0, 30.0, 30.0, 31.0, 34.0, 36.0, 38.0, 38.0, 37.0, 38.0, 39.0, 39.0, 38.0, 37.0, 36.0, 36.0, 35.0,33.0, 33.0, 32.0, 32.0, 32.0, 32.0, 32.0, 31.0,31.0, 32.0, 32.0, 32.0, 32.0, 32.0, 32.0, 32.0, 32.0, 32.0, 32.0, 32.0, 32.0, 32.0,32.0, 32.0, 32.0, 33.0, 33.0, 33.0, 32.0, 32.0, 33.0, 30.0, 28.0, 29.0, 30.0, 29.0, 30.0, 29.0, 27.0, 27.0,27.0, 32.0, 33.0, 36.0, 35.0, 34.0, 34.0, 33.0,33.0, 32.0, 32.0, 32.0, 36.0, 39.0, 42.0, 41.0, 42.0, 34.0, 30.0, 30.0, 28.0, 29.0,28.0, 31.0, 31.0, 32.0, 31.0, 31.0, 31.0, 31.0, 31.0, 31.0, 32.0, 33.0, 34.0, 34.0, 33.0, 33.0, 33.0, 23.0,17.0, 14.0, 15.0, 13.0, 13.0, 14.0, 14.0, 13.0,13.0, 13.0, 12.0, 13.0, 12.0, 11.0, 11.0, 11.0, 11.0, 11.0, 11.0, 10.0, 10.0, 9.0,9.0, 9.0, 9.0, 8.0, 8.0, 9.0,8.0, 9.0, 9.0, 9.0, 9.0, 9.0, 10.0, 11.0, 13.0,13.0, 14.0, 14.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 13.0, 12.0, 12.0, 13.0,13.0, 13.0, 13.0, 13.0, 13.0, 14.0, 14.0, 13.0, 14.0, 13.0, 14.0, 13.0, 13.0, 13.0,12.0, 12.0, 11.0, 11.0, 11.0,11.0, 10.0, 11.0, 10.0, 10.0, 10.0, 11.0, 11.0,11.0, 11.0, 11.0, 11.0, 11.0, 11.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0,10.0, 10.0, 10.0, 11.0, 10.0, 11.0, 11.0, 12.0, 12.0, 12.0, 13.0, 13.0, 13.0, 13.0,15.0, 15.0, 15.0, 15.0, 15.0,16.0, 17.0, 16.0, 12.0, 12.0, 11.0, 11.0, 11.0,11.0, 10.0, 10.0, 10.0, 10.0, 11.0, 11.0, 11.0, 11.0, 13.0, 14.0, 15.0, 17.0,19.0, 24.0, 23.0, 25.0, 28.0, 30.0, 31.0, 31.0, 32.0, 32.0, 31.0, 31.0]}
    # Choix des différents scénarios
    mois_initial = int(str(jour_initial)[5:7])
    if (mois_initial >= 4 and mois_initial <= 9):
        choix_saison = "ete"
    else:
        choix_saison = "hiver"
    tarif_reel=[]
    for treel in range(int(jour*24/dt)):
        t=treel%int(24/dt)
        if t<=12 or t>=45:#Heures creuses de 22h30 à 6h30 (on finit à 6h ou on commence à 23h)
            tarif_reel.append(prixcreux+prix_tonne*emission_saison[choix_saison][treel])
        else:
            tarif_reel.append(prixplein+prix_tonne*emission_saison[choix_saison][treel])
    lp = pulp.LpProblem("Probleme_global"+".lp", pulp.LpMinimize)#Declaration du problème
    l1,lbatplus1,lbatmoins1=usine(jour,dt,l1dem,lp)#Prise en compte de l'usine
    LNF2,L2HP,HDC=datacenter(jour,dt,l2IT,PHW,lp)#Prise en compte du data center
    l3,lbatplus3,lbatmoins3=panneaux_solaires(jour,dt,l3donne,lp)#Prise en compte des panneaux solaires
    l4,lbatplus4,lbatmoins4,batterie4,charge4=charge_voiture(jour,dt,lp,tdepart,tarrivee,nb_voiture)#Prise en compte des charges de voiture
    ltot={}
    fuite={}
    lopti={}#tel que ltot=lopti+fuite et on cherche a opti lopti
    cout_abo={}
    #Declaration variable binaire abonnement
    for i in range(8):
        cout_abo[i] = pulp.LpVariable("cout_abo_" +str(i),0, 1, pulp.LpBinary)
    lp+=pulp.lpSum(cout_abo[i] for i in range(8))==1,"Contrainte_palier_puissance_abo"
    pmax=pulp.LpVariable("pmax")
    surplus=pulp.LpVariable("surplus puissance",0)
    for t in range(int(jour*24/dt)):
        ltot[t]=l1[t]+l3[t]+pulp.lpSum(lbatplus4[t][v]-lbatmoins4[t][v] for v in range(nb_voiture))+(LNF2[t]+L2HP[t])#dernier terme consommation du data center
        lp+=pmax>=ltot[t],"Contrainte pmax"+str(t)
        fuite[t]=pulp.LpVariable("fuite_"+str(t), 0.0)
        lopti[t]=pulp.LpVariable("lopti_"+str(t), 0.0)
        lp+=ltot[t]==lopti[t]-fuite[t],"Contrainte_injection_elec"+str(t)
    lp+=pmax<=(pulp.lpSum(cout_abo[i]*conso_abo[i] for i in range(8))+surplus),"Contrainte pmax final"
    lp+=surplus<=1000*cout_abo[7],"Contrainte du surplus"
    lp.setObjective(pulp.lpSum([lopti[t] * tarif_reel[t]*dt -HDC[t]*PHW[t] for t in range(int(jour * 24/dt))])+pulp.lpSum(cout_abo[i]*tarif_abo[i] for i in range(8))+cout_surplus*surplus)
    lp.writeLP('model.lp')
    lp.solve(pulp.PULP_CBC_CMD(msg=True))
    return lbatplus4,lbatmoins4,lbatplus3,lbatmoins3,L2HP,lbatplus1,lbatmoins1

def conversion(branchement):
    tdepart=[-1]*4 #On prend tdepart=-1 initialement pour eviter le cas ou t[i] est vide qui bloquerait le code
    tarrivee=[49]*4
    for i in range(4):
        for t in range(47):
            if branchement[i]==0 and branchement[i+1]==1:
                tarrivee[i]=t
            if branchement[i] == 1 and branchement[i + 1] == 0:
                tdepart[i]=t
    return tdepart,tarrivee

def centralized_optimization(states):
    # Constantes
    dt = 0.5  # pas de temps
    jour = 1  # nombre de jour
    prix_tonne=56*10**(-6)
    # env_name in {'ferme', 'evs', 'industrie', 'datacenter'}
    # recupération des données
    for env_name, state in states.items():
        if env_name == 'ferme':
            pv_production = state['pv_prevision']
            jour_initial=state['datetime']
        elif env_name == 'datacenter':
            hotwater_price = state['hotwater_price_prevision']
            datacenter_prevision = state['consumption_prevision']
        elif env_name == 'industrie':
            industrie_consommation=state['consumption_prevision']
        elif env_name == 'evs':
            branchement=state['is_plugged_prevision']
            tdepart,tarrivee=conversion(branchement,jour,dt)
    # optimization
    lbatplus4,lbatmoins4,lbatplus3,lbatmoins3,L2HP,lbatplus1,lbatmoins1=optiglobal(jour,dt,prix_tonne,industrie_consommation,datacenter_prevision,hotwater_price,pv_production,tdepart,tarrivee,jour_initial)
    # get resultats
    res = {}
    lbat4=[]
    lbat3=[]
    l2HP=[]
    lbat1=[]
    for i in range(int(jour*24/dt)):
        lbat4.append(lbatplus4[i].value()-lbatmoins4[i].value())
        lbat3.append(lbatplus3[i].value() - lbatmoins3[i].value())
        lbat1.append(lbatplus1[i].value() - lbatmoins1[i].value())
        l2HP.append(L2HP[i].value())
    res['industrie']=lbat1
    res['datacenter']=l2HP
    res['ferme']=lbat3
    res['evs']=lbat4

    return res