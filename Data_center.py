import pulp

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




