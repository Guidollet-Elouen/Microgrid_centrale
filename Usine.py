import pulp

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





