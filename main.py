import pulp
import numpy as np
import datetime #mydate=datetime.datetime(2014,1,1)+datetime.timedelta(days=7) exemple date time

#Choix des différents scénarios
jour_initial_panneaux_datetime=datetime.date(2014,7,1)
mois_initial=int(str(jour_initial_panneaux_datetime)[5:7])
if (mois_initial>=4 and mois_initial<=9):
    choix_saison="ete"
else:
    choix_saison="hiver"


def optiglobal(jour,dt,prix_tonne,l1dem,l2IT,PHW,l3donne,tdepart,tarrivee):
    # Choix des tarifs
    conso_abo = [6, 9, 12, 15, 18, 24, 30, 36]
    prixcreux = 0.1230  # 22h30 à 6h30
    prixplein = 0.1580
    tarif_abo = (np.array([123.6, 151.32, 177.24, 201.36, 223.68, 274.68, 299.52, 337.56]) * jour / 365)
    cout_surplus = 6.34 * jour / 365
    nb_voiture = 4
    #Calcul tarif
    emission_saison = {'hiver': [40.0, 39.0, 37.0, 34.0, 33.0, 29.0, 26.0, 22.0, 23.0, 23.0, 23.0, 24.
                                 0, 24.0, 24.0, 24.0, 24.0, 24.0, 24.0, 26.0, 26.0, 26.0, 26.0, 26.0, 26.0, 26.0,
                                 26.0, 25.0, 26.0, 26.0, 26.0, 28.0, 29.0, 30.0, 33.0, 35.0, 36.0, 37.0, 39.0, 4
                                 0.0, 41.0, 41.0, 41.0, 41.0, 41.0, 40.0, 40.0, 40.0, 38.0, 37.0, 38.0, 36.0, 36.
                                 0, 36.0, 38.0, 36.0, 36.0, 36.0, 36.0, 36.0, 35.0, 37.0, 41.0, 43.0, 43.0, 44.0,
                                 44.0, 45.0, 45.0, 45.0, 44.0, 44.0, 44.0, 44.0, 43.0, 43.0, 43.0, 43.0, 44.0, 4
                                 3.0, 42.0, 42.0, 43.0, 43.0, 43.0, 42.0, 42.0, 43.0, 43.0, 42.0, 42.0, 41.0, 42.
                                 0, 38.0, 39.0, 38.0, 36.0, 35.0, 26.0, 26.0, 28.0, 27.0, 27.0, 27.0, 28.0, 27.0,
                                 27.0, 27.0, 27.0, 28.0, 29.0, 31.0, 36.0, 38.0, 39.0, 41.0, 41.0, 40.0, 39.0, 3
                                 9.0, 37.0, 37.0, 37.0, 39.0, 39.0, 39.0, 40.0, 42.0, 43.0, 44.0, 44.0, 44.0, 44.
                                 0, 44.0, 43.0, 44.0, 44.0, 43.0, 44.0, 44.0, 44.0, 42.0, 41.0, 41.0, 37.0, 37.0,
                                 34.0, 35.0, 35.0, 36.0, 35.0, 33.0, 34.0, 33.0, 33.0, 32.0, 32.0, 34.0, 34.0, 3
                                 4.0, 36.0, 37.0, 39.0, 38.0, 39.0, 38.0, 39.0, 38.0, 39.0, 39.0, 39.0, 39.0, 39.
                                 0, 39.0, 39.0, 39.0, 40.0, 41.0, 43.0, 42.0, 44.0, 43.0, 43.0, 42.0, 42.0, 42.0,
                                 43.0, 42.0, 41.0, 40.0, 42.0, 43.0, 43.0, 43.0, 43.0, 42.0, 41.0, 42.0, 42.0, 4
                                 2.0, 43.0, 43.0, 43.0, 42.0, 42.0, 44.0, 43.0, 43.0, 43.0, 44.0, 42.0, 42.0, 40.
                                 0, 40.0, 40.0, 40.0, 41.0, 42.0, 42.0, 42.0, 42.0, 41.0, 41.0, 42.0, 43.0, 44.0,
                                 44.0, 44.0, 45.0, 44.0, 43.0, 43.0, 43.0, 44.0, 44.0, 45.0, 45.0, 44.0, 44.0, 4
                                 6.0, 45.0, 45.0, 37.0, 35.0, 34.0, 34.0, 35.0, 33.0, 31.0, 31.0, 31.0, 31.0, 32.
                                 0, 36.0, 41.0, 43.0, 43.0, 42.0, 45.0, 49.0, 49.0, 50.0, 51.0, 52.0, 46.0, 46.0,
                                 45.0, 45.0, 46.0, 46.0, 47.0, 47.0, 49.0, 49.0, 48.0, 47.0, 47.0, 44.0, 42.0, 4
                                 1.0, 41.0, 41.0, 41.0, 43.0, 43.0, 43.0, 42.0, 44.0, 43.0, 44.0, 40.0, 41.0, 40.
                                 0, 40.0, 40.0, 40.0, 40.0, 40.0, 40.0, 40.0, 44.0, 46.0, 48.0, 47.0, 45.0, 43.0,
                                 43.0, 42.0, 42.0, 42.0, 42.0, 42.0, 41.0, 41.0, 42.0, 41.0, 43.0, 43.0, 43.0, 4
                                 4.0, 44.0, 44.0, 44.0, 44.0, 44.0, 43.0, 43.0, 43.0, 43.0, 43.0, 43.0, 43.0, 42.
                                 0, 40.0, 39.0, 38.0, 35.0], 'ete': [13.0, 13.0, 13.0, 13.0, 13.0, 14.0, 14.0, 14
                                                                     .0, 14.0, 15.0, 14.0, 15.0, 14.0, 14.0, 14.0, 14.0,
                                                                     14.0, 14.0, 14.0, 13.0, 14.0
        , 14.0, 14.0, 13.0, 13.0, 13.0, 13.0, 13.0, 13.0, 14.0, 14.0, 15.0, 16.0, 17.0,
                                                                     17.0, 16.0, 17.0, 19.0, 18.0, 18.0, 18.0, 19.0,
                                                                     19.0, 20.0, 20.0, 21.0, 20.0, 20
                                                                     .0, 21.0, 21.0, 21.0, 22.0, 22.0, 22.0, 22.0, 21.0,
                                                                     21.0, 22.0, 22.0, 25.0, 26.0
        , 28.0, 31.0, 32.0, 31.0, 30.0, 29.0, 28.0, 28.0, 28.0, 27.0, 26.0, 27.0, 26.0,
                                                                     27.0, 28.0, 27.0, 28.0, 29.0, 30.0, 29.0, 30.0,
                                                                     30.0, 30.0, 31.0, 30.0, 30.0, 30
                                                                     .0, 30.0, 31.0, 31.0, 31.0, 32.0, 32.0, 31.0, 31.0,
                                                                     31.0, 33.0, 30.0, 30.0, 31.0
        , 34.0, 36.0, 38.0, 38.0, 37.0, 38.0, 39.0, 39.0, 38.0, 37.0, 36.0, 36.0, 35.0,
                                                                     33.0, 33.0, 32.0, 32.0, 32.0, 32.0, 32.0, 31.0,
                                                                     31.0, 32.0, 32.0, 32.0, 32.0, 32
                                                                     .0, 32.0, 32.0, 32.0, 32.0, 32.0, 32.0, 32.0, 32.0,
                                                                     32.0, 32.0, 32.0, 33.0, 33.0
        , 33.0, 32.0, 32.0, 33.0, 30.0, 28.0, 29.0, 30.0, 29.0, 30.0, 29.0, 27.0, 27.0,
                                                                     27.0, 32.0, 33.0, 36.0, 35.0, 34.0, 34.0, 33.0,
                                                                     33.0, 32.0, 32.0, 32.0, 36.0, 39
                                                                     .0, 42.0, 41.0, 42.0, 34.0, 30.0, 30.0, 28.0, 29.0,
                                                                     28.0, 31.0, 31.0, 32.0, 31.0
        , 31.0, 31.0, 31.0, 31.0, 31.0, 32.0, 33.0, 34.0, 34.0, 33.0, 33.0, 33.0, 23.0,
                                                                     17.0, 14.0, 15.0, 13.0, 13.0, 14.0, 14.0, 13.0,
                                                                     13.0, 13.0, 12.0, 13.0, 12.0, 11
                                                                     .0, 11.0, 11.0, 11.0, 11.0, 11.0, 10.0, 10.0, 9.0,
                                                                     9.0, 9.0, 9.0, 8.0, 8.0, 9.0,
                                                                     8.0, 9.0, 9.0, 9.0, 9.0, 9.0, 10.0, 11.0, 13.0,
                                                                     13.0, 14.0, 14.0, 15.0, 15.0, 1
                                                                     5.0, 15.0, 15.0, 15.0, 13.0, 12.0, 12.0, 13.0,
                                                                     13.0, 13.0, 13.0, 13.0, 13.0, 14.
                                                                     0, 14.0, 13.0, 14.0, 13.0, 14.0, 13.0, 13.0, 13.0,
                                                                     12.0, 12.0, 11.0, 11.0, 11.0,
                                                                     11.0, 10.0, 11.0, 10.0, 10.0, 10.0, 11.0, 11.0,
                                                                     11.0, 11.0, 11.0, 11.0, 11.0, 1
                                                                     1.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0,
                                                                     10.0, 10.0, 10.0, 11.0, 10.0, 11.
                                                                     0, 11.0, 12.0, 12.0, 12.0, 13.0, 13.0, 13.0, 13.0,
                                                                     15.0, 15.0, 15.0, 15.0, 15.0,
                                                                     16.0, 17.0, 16.0, 12.0, 12.0, 11.0, 11.0, 11.0,
                                                                     11.0, 10.0, 10.0, 10.0, 10.0, 1
                                                                     1.0, 11.0, 11.0, 11.0, 13.0, 14.0, 15.0, 17.0,
                                                                     19.0, 24.0, 23.0, 25.0, 28.0, 30.
                                                                     0, 31.0, 31.0, 32.0, 32.0, 31.0, 31.0]}
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


def centralized_optimization(states):
    # Constantes
    dt = 0.5  # pas de temps
    jour = 1  # nombre de jour
    prix_tonne=56*10**(-6)
    # env_name in {'ferme', 'evs', 'industrie', 'datacenter'}
    # recupération des données
    #state['datetime'] heure de la simulation
    for env_name, state in states.items():
        if env_name == 'ferme':
            pv_production = state['pv_prevision']
        elif env_name == 'datacenter':
            hotwater_price = state['hotwater_price_prevision']
            datacenter_prevision = state['datacenter_prevision']
        elif env_name == 'industrie':
            industrie_consommation=state['industrie_prevision']
        elif env_name == 'evs':
            tdepart=state['tdepart_prevision']
            tarrivee=state['tarrivee_prevision']
    # optimization
    lbatplus4,lbatmoins4,lbatplus3,lbatmoins3,L2HP,lbatplus1,lbatmoins1=optiglobal(jour,dt,prix_tonne,industrie_consommation,datacenter_prevision,hotwater_price,pv_production,tdepart,tarrivee)
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