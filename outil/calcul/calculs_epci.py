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

from outil.models import Commune
from .calculs_ze import CalculZE

class CalculEPCI:
    
    def __init__(self, codes_zone):
        self.codes_zone = codes_zone
    
    @property
    def epcis(self):
        '''
        retourne la liste de dictionnaires des EPCI concernés par les ZE 
        sous la forme {'code_epci': 'XXXXXX', 'nom_epci':'YYYYY'}
        '''
        return Commune.objects.filter(code_ze__in=self.codes_zone).values('code_epci', 'nom_epci').distinct().order_by('nom_epci')
    
    def communes(self, code_epci):
        return Commune.objects.filter(code_epci=code_epci).filter(code_ze__in=self.codes_zone).order_by('code')
    
    def resultat(self, code_epci):
        resultats_ze = CalculZE().resultats(self.codes_zone)
        resultat = ResultatEPCI(code_epci)
        resultat.besoin_en_logement_naif_final = resultat.besoin_en_logement_naif(resultats_ze)
        resultat.besoin_en_logement_final = resultat.besoin_en_logement_cale(resultats_ze)
        resultat.besoin_en_logement_final_1an = round(resultat.besoin_en_logement_final/6)
        return resultat
        
    def resultats(self, codes_epci):
        resultats_ze = CalculZE().resultats(self.codes_zone)
        resultats = []
        for code_epci in codes_epci:
            resultat = ResultatEPCI(code_epci)
            resultat.besoin_en_logement_naif_final = resultat.besoin_en_logement_naif(resultats_ze)
            resultat.besoin_en_logement_final = resultat.besoin_en_logement_cale(resultats_ze)
            resultat.besoin_en_logement_final_1an = round(resultat.besoin_en_logement_final/6)
            resultats.append(resultat)
        return resultats
    
class ResultatEPCI:
    
    def __init__(self, code_epci):
        self.code_epci = code_epci
        self.communes = Commune.objects.filter(code_epci=code_epci)
        self.stockage_bel_ze_borne = {}
    
    @property
    def nom_epci(self):
        return (self.communes)[0].nom_epci
    
    @property
    def departements(self):
        return ', '.join(sorted(set([commune.departement for commune in self.communes])))
    
    def besoin_en_logement_naif(self, resultats_ze):
        bel_epci_final = 0
        #print('EPCI', self.code_epci)
        for commune in self.communes:
            code_ze = commune.code_ze
            #print(commune.nom, code_ze)
            bel_ze = self.besoin_logement_ze(code_ze, resultats_ze)
            bel_comm_naif = commune.besoin_en_logement_naif(bel_ze)
            bel_epci_final += bel_comm_naif
        return round(bel_epci_final)
    
    def besoin_en_logement_cale(self, resultats_ze):
        bel_epci_final = 0
        #print('EPCI', self.code_epci)
        for commune in self.communes:
            code_ze = commune.code_ze
            #print(commune.nom, code_ze)
            bel_ze = self.besoin_logement_ze(code_ze, resultats_ze)
            #print('BEL ZE : ', bel_ze)
            bel_comm_borne = commune.besoin_en_logement_borne(bel_ze)
            #print('BEL COMM BORNE : ', bel_comm_borne)
            bel_ze_borne = self.besoin_en_logement_ze_borne(code_ze, resultats_ze)
            #print('BEL ZE BORNE : ', bel_ze_borne)
            if bel_ze_borne > 0:
                bel_epci_final += bel_comm_borne * bel_ze / bel_ze_borne
        #print('BEL EPCI', bel_epci_final)
        return round(bel_epci_final)
    
    def besoin_logement_ze(self, code_ze, resultats_ze):        
        for resultat_ze in resultats_ze:
            if resultat_ze.code_zone == code_ze:
                return resultat_ze.total_besoin_6ans
        return 0
    
    def besoin_en_logement_ze_borne(self, code_ze, resultats_ze):
        if code_ze in self.stockage_bel_ze_borne: # verification si calcul déjà effectué pour ZE
            return self.stockage_bel_ze_borne[code_ze]
        communes_ze = Commune.objects.filter(code_ze=code_ze)
        bel_ze_borne = 0
        for commune in communes_ze:
            bel_ze = self.besoin_logement_ze(code_ze, resultats_ze)
            bel_ze_borne += commune.besoin_en_logement_borne(bel_ze)
        self.stockage_bel_ze_borne[code_ze] = bel_ze_borne # stockage pour éviter nouveau calcul
        return bel_ze_borne
                    
