'''

Copyright ou © ou Copr. Cerema, (novembre 2017) 

www.cerema.fr

Ce logiciel est un programme informatique facilitant la mise en oeuvre
de la méthodologie d’estimation territorialisée des besoins en logements 
conçue par la direction de l’Habitat de l’Urbanisme et des Paysages du 
ministère du Logement et de l’Habitat durable, en partenariat avec le 7
Service de l’Observation et des Statistiques du CGDD et le Cerema.

Ce logiciel est régi par la licence CeCILL soumise au droit français et
respectant les principes de diffusion des logiciels libres. Vous pouvez
utiliser, modifier et/ou redistribuer ce programme sous les conditions
de la licence CeCILL telle que diffusée par le CEA, le CNRS et l'INRIA 
sur le site "http://www.cecill.info".

En contrepartie de l'accessibilité au code source et des droits de copie,
de modification et de redistribution accordés par cette licence, il n'est
offert aux utilisateurs qu'une garantie limitée.  Pour les mêmes raisons,
seule une responsabilité restreinte pèse sur l'auteur du programme,  le
titulaire des droits patrimoniaux et les concédants successifs.

A cet égard  l'attention de l'utilisateur est attirée sur les risques
associés au chargement,  à l'utilisation,  à la modification et/ou au
développement et à la reproduction du logiciel par l'utilisateur étant 
donné sa spécificité de logiciel libre, qui peut le rendre complexe à 
manipuler et qui le réserve donc à des développeurs et des professionnels
avertis possédant  des  connaissances  informatiques approfondies.  Les
utilisateurs sont donc invités à charger  et  tester  l'adéquation  du
logiciel à leurs besoins dans des conditions permettant d'assurer la
sécurité de leurs systèmes et ou de leurs données et, plus généralement, 
à l'utiliser et l'exploiter dans les mêmes conditions de sécurité. 

Le fait que vous puissiez accéder à cet en-tête signifie que vous avez 
pris connaissance de la licence CeCILL, et que vous en avez accepté les
termes.

'''

from outil.models import ParametreZE
#from outil.models import Epci
from outil.models import Commune
from .params import PACK
from .params import FICHIER_ZE
from .charger_ze import ZonesEmploi 
from .charger_data import FichierPack
from outil.calcul.calculs_ze import CalculZE


def init_bdd():
    '''
    Reinitialise la table de paramètrage de la base de données
    '''
    ParametreZE.objects.all().delete()
    
    ze = ZonesEmploi()
    ze.charger(FICHIER_ZE)
    # Récupération des codes zone issus du Pack B1
    codes_zone = FichierPack(PACK).codes_zones
    for code in codes_zone:
        param_ze = ParametreZE(code_ze=code, nom_ze=ze.nom(code))
        param_ze.save()
    
    # Correction des paramètres Omphale pour les ZE n'ayant pas de scénarios Omphale 
    calcul = CalculZE()
    parametres = ParametreZE.objects.all()
    scenarii = [(nom_court, nom_long) for nom_court, nom_long in ParametreZE.SCENARIOS_OMPHALE.items()]
    for parametre in parametres:
        resultat = calcul.resultat(parametre.code_ze)
        evolution_menage = resultat.evolution_menage
        valeurs_scenario = [(valeurs[0], valeurs[1], resultat.evolution_omphale(valeurs[0])) for valeurs in scenarii]
        # modification des paramètrage des ZE n'ayant pas de scénario Omphale
        if parametre.b2_choix_omphale and valeurs_scenario[0][2] == 0:
            param = ParametreZE.objects.get(code_ze = parametre.code_ze)
            param.b2_choix_omphale = False            
            param.autre_source_b21 = evolution_menage
            param.save()
    
    #Commune.objects.all().delete()
    if len(Commune.objects.all()) == 0:
        Commune.objects.integrer_communes()

def init_classe_communes():
    '''
    Reinitialise les classes des communes
    '''
    Commune.objects.reinitiliser_classe()

def init_communes():
    '''
    Remets à jour les communes avec les EPCI associés à l'aide du fichier de désagrégation des communes
    '''
    Commune.objects.integrer_communes()    
