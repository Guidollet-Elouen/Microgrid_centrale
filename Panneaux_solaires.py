import pulp

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


