import pulp
import matplotlib.pyplot as plt
import pandas
import numpy as np
import datetime #mydate=datetime.datetime(2014,1,1)+datetime.timedelta(days=7) exemple date time
import time

##Parametres
#Constantes
dt=0.5 #pas de temps
jour=7#nombre de jour
taille_panneaux=100 #taille du panneaux en m2
nb_voiture=4

#Choix des différents scénarios
site_usine=3#Entre 1 et 3
scenario_usine=22#Entre 1 et 30
scenario_datacenter=2#Entre 1 et 10
region_panneaux="grand_nord"
jour_initial_panneaux_datetime=datetime.date(2014,7,1)
mois_initial=int(str(jour_initial_panneaux_datetime)[5:7])
if (mois_initial>=4 and mois_initial<=9):
    choix_saison="ete"
else:
    choix_saison="hiver"

#Choix des tarifs
prix_tonne=56*10**(-6)
conso_abo=[6,9,12,15,18,24,30,36]
prixcreux=0.1230 #22h30 à 6h30
prixplein=0.1580
tarif_abo=(np.array([123.6,151.32,177.24,201.36,223.68,274.68,299.52,337.56])*jour/365)
cout_surplus=6.34*jour/365

##Import des données
d_datacenter=pandas.read_csv("/Users/elouenguidollet/Desktop/pythonProject/optim_et_energie/data_center/data_center_weekly_scenarios.csv",sep=";",decimal=".")
d_usine=pandas.read_csv("/Users/elouenguidollet/Desktop/pythonProject/optim_et_energie/industrial_consumer/indus_weekly_cons_scenarios.csv",sep=";",decimal=".")
d_panneaux=pandas.read_csv("/Users/elouenguidollet/Desktop/pythonProject/optim_et_energie/solar_farm/pv_prod_scenarios.csv",sep=";",decimal=".")
d_station=pandas.read_csv("/Users/elouenguidollet/Desktop/pythonProject/optim_et_energie/charging_station/ev_scenarios.csv",sep=";",decimal=".")
d_emission_hiver=pandas.read_csv("/Users/elouenguidollet/Desktop/pythonProject/eCO2mix_RTE_Annuel-Definitif_2020_winter.csv",sep=";")
d_emission_ete=pandas.read_csv("/Users/elouenguidollet/Desktop/pythonProject/eCO2mix_RTE_Annuel-Definitif_2020_summer.csv",sep=";")
#Emission
emission_saison={}
emission_saison["hiver"]=list(d_emission_hiver["co2_rate"])
emission_saison["ete"]=list(d_emission_ete["co2_rate"])

#Data center
choix_sce_data=d_datacenter[d_datacenter["scenario"]==scenario_datacenter]
l2IT=list(choix_sce_data["cons (kW)"])#Conso data center
PHW = [0.5] * int(24 * jour/dt)  # prix de l'eau chaude en euro/KWH
#Usine
choix_sce_usine=d_usine[(d_usine["scenario"]==scenario_usine) & (d_usine["site_id"]==site_usine)]
l1dem=list(choix_sce_usine["cons (kW)"]) #Demande de la consommation de l'usine
#Panneaux solaires et voitures
jour_actuel_datetime=jour_initial_panneaux_datetime
l3donne_tempo=[]
tdepart=[[],[],[],[]]
tarrivee=[[],[],[],[]]
for njour in range(jour):
    jour_reel=str(jour_actuel_datetime)[8:10]
    mois=str(jour_actuel_datetime)[5:7]
    annee=str(jour_actuel_datetime)[0:4]
    jour_actuel=str(jour_reel)+"/"+str(mois)+"/"+str(annee)
    choix_sce_panneaux=d_panneaux[(d_panneaux["region"]==region_panneaux) & (d_panneaux["day"]==jour_actuel)]
    l3donne_tempo+=list(choix_sce_panneaux["pv_prod (W/m2)"]) #Production du panneau en W/m2
    for k in range(nb_voiture):
        choix_sce_station=d_station[(d_station["day"]==jour_actuel) & (d_station["ev_id"]==(k+1))]
        tdepart[k]+=list(choix_sce_station["time_slot_dep"])
        tarrivee[k]+=list(choix_sce_station["time_slot_arr"])
    jour_actuel_datetime+=datetime.timedelta(days=1)
normalisation_panneaux=taille_panneaux/1000 #remettre en kW
lrepeat=np.repeat(np.array(l3donne_tempo)*(normalisation_panneaux),2)
l3donne=lrepeat.tolist() #production du panneau en kW
normalisation_panneaux=taille_panneaux/1000 #remettre en kW


def optiglobal(prix_tonne):
    #Calcul tarif
    tarif_reel=[]
    for treel in range(int(jour*24/dt)):
        t=treel%int(24/dt)
        if t<=12 or t>=45:#Heures creuses de 22h30 à 6h30 (on finit à 6h ou on commence à 23h)
            tarif_reel.append(prixcreux+prix_tonne*emission_saison[choix_saison][treel])
        else:
            tarif_reel.append(prixplein+prix_tonne*emission_saison[choix_saison][treel])
    lp = pulp.LpProblem("Probleme_global"+".lp", pulp.LpMinimize)#Declaration du problème
    #lp.setSolver("CBC")
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
    return lopti,lp,pmax,fuite,cout_abo,lbatplus4,lbatmoins4

##Definition de fonction pour le calcul des metriques
def calcul_cout_abo(pmax):
    bsurplus=1
    for i in range(len(conso_abo)):
        if pmax<=conso_abo[i]:
            cout_abo=tarif_abo[i]
            bsurplus=0
    if bsurplus==0:
        cout_abo
    else:
        return tarif_abo[-1]+cout_surplus*(pmax-conso_abo[-1])

def partie_entiere(a,puissance):
    b=10**puissance
    return int(a*b)/b
##Calcul des metriques
def main(prixtonne):
    T=[]
    lopti,lp,pmax,fuite,cout_abo,lbatplus4,lbatmoins4=optiglobal(prixtonne)
    achattot=0
    fuitetot=0
    couttot=0
    A=[]
    F=[]
    demande_tot=0
    production_tot=0
    conso_indus=0
    conso_data=0
    conso_tot=0
    conso_voiture=0
    for i in range(8):
        print(cout_abo[i].value())
    for t in range(int(24*jour/dt)):
        conso_voiture+=pulp.lpSum(lbatplus4[t][v]-lbatmoins4[t][v] for v in range(nb_voiture)).value()*dt
        production_tot+=l3donne[t]*dt
        demande_tot+=(l1dem[t]+l2IT[t])*dt
        T.append(t)
        F.append(fuite[t].value())
        couttot+=lopti[t].value()*tarif_reel[t]*dt
        achattot+=lopti[t].value()*dt
        fuitetot+=fuite[t].value()*dt
        A.append(lopti[t].value())
    cout_abo_tot=calcul_cout_abo(pmax.value())
    plt.plot(T,A)
    plt.show()
    autonomie=production_tot/(production_tot+achattot)
    time.sleep(1)
    print("fuite= ",partie_entiere(fuitetot,3),"KWh")
    print("pmax= ",partie_entiere(pmax.value(),3),"kW")
    print("coût= ",partie_entiere(couttot+cout_abo_tot,3)," €")
    print("achat= ",partie_entiere(achattot/1000,3),"MWh")
    print("autonomie= ",partie_entiere(autonomie*100,3),"%")
    print("conso industriel et data center=",partie_entiere(demande_tot/1000,3),"MWh")
    print("production solaire =",partie_entiere(production_tot,3),"KWh")
    print("conso voiture = ",partie_entiere(conso_voiture,3),"KWh")


def comparaison(prixtonne):#Attention longueur de A et T en fonction de len(prixtonne)
    A=[[],[]]
    T=[[],[]]
    for i in range(len(prixtonne)):
        lopti,lp,pmax,fuite,cout_abo,lbatplus4,lbatmoins4=optiglobal(prixtonne[i])
        for t in range(int(24*jour/dt)):
            T[i].append(t)
            A[i].append(lopti[t].value())
        plt.plot(T[i],A[i])
    plt.show()
##Problemes
#Interet de la vente de chaleur dans le cas global (benefice inter micro grid et consommation quand meme)
P=[56*10**(-6),560*10**(-6)]