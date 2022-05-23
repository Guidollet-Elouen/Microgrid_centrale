import pulp

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


#test fonction
def optivoiture(jour,dt,tdepart,tarrivee,k):
    lp = pulp.LpProblem("Probleme_voiture"+".lp", pulp.LpMinimize)#Declaration du problème
    lp.setSolver()
    l4,lbatplus4,lbatmoins4,batterie,charge=charge_voiture(jour,dt,lp,tdepart,tarrivee,k)#Prise en compte des charges de voiture
    lp.setObjective(pulp.lpSum([pulp.lpSum(lbatplus4[t][v]-lbatmoins4[t][v] for v in range(k)) for t in range(int(jour*24/dt))]))
    lp.solve()
    return lbatplus4,lbatmoins4,batterie,charge
