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

from .outils_xls import lignes_xls

class ZonesEmploi():
    
    '''
    
    Gestionnaire des zones d'emploi 
    
    Les données sont chargées à partir du fichier 2015 de l'INSEE via la méthode .charger()
    
    '''
    
    def __init__(self):
        self.zones_emploi = list()
    
    def codes_zone(self, nvelle_region=None):
        if nvelle_region is None:
            return [zone_emploi.code for zone_emploi in self.zones_emploi]
        return [zone_emploi.code for zone_emploi in self.zones_emploi if nvelle_region in zone_emploi.codes_nv_region]
    
    def get(self, code_zone):
        for zone_emploi in self.zones_emploi:
            if code_zone == zone_emploi.code:
                return zone_emploi
    
    def nom(self, code_zone):
        return self.get(code_zone).nom
            
    def code_zone_emploi(self, commune):
        if isinstance(commune, Commune):
            for zone_emploi in self.zones_emploi:
                if commune in zone_emploi:
                    return zone_emploi.code
        elif isinstance(commune, str):
            for zone_emploi in self.zones_emploi:
                if commune in zone_emploi:
                    return zone_emploi.code
    
    def codes_insee(self, zone):
        if isinstance(zone, ZoneEmploi):
            return zone.codes_insee
        elif isinstance(zone, str):
            zone_emploi = self.get(zone)
            if zone_emploi:
                return zone_emploi.codes_insee
    
    def codes_departement(self, zone):
        if isinstance(zone, ZoneEmploi):
            return zone.codes_departement
        elif isinstance(zone, str):
            zone_emploi = self.get(zone)
            if zone_emploi:
                return zone_emploi.codes_departement
    
    def codes_anc_region(self, zone):
        if isinstance(zone, ZoneEmploi):
            return zone.codes_anc_region
        elif isinstance(zone, str):
            zone_emploi = self.get(zone)
            if zone_emploi:
                return zone_emploi.codes_anc_region
    
    def codes_nv_region(self, zone):
        if isinstance(zone, ZoneEmploi):
            return zone.codes_nv_region
        elif isinstance(zone, str):
            zone_emploi = self.get(zone)
            if zone_emploi:
                return zone_emploi.codes_nv_region
            
    def charger(self, fichier_xls, nom_feuille='Composition_communale'):
        for ligne_xls in lignes_xls(fichier_xls, nom_feuille, start=6):
            self._integrer_commune(ligne_xls)
    
    def _integrer_commune(self, ligne_xls):
        code_insee = ligne_xls[0]
        nom_commune = ligne_xls[1] 
        code_zone_emploi = ligne_xls[2]
        nom_zone_emploi = ligne_xls[3]
        code_departement = ligne_xls[4] 
        code_ancienne_region = ligne_xls[5]
        code_nouvelle_region = ligne_xls[6]
        nvelle_commune = Commune(code_insee, nom_commune, code_departement, code_ancienne_region, code_nouvelle_region)
        nvelle_zone = ZoneEmploi(code_zone_emploi, nom_zone_emploi)       
        if nvelle_zone in self.zones_emploi:
            for zone in self.zones_emploi:
                if zone == nvelle_zone:
                    zone.ajout(nvelle_commune)
                    break            
        else:
            nvelle_zone.ajout(nvelle_commune)
            self.zones_emploi.append(nvelle_zone)                

class ZoneEmploi():
    
    def __init__(self, code, nom):
        self.code = code
        self.nom = nom
        self.communes = list()
    
    @property
    def codes_insee(self):
        return [commune.code_insee for commune in self.communes]
    
    @property
    def codes_departement(self):
        return list(set([commune.code_dep for commune in self.communes]))
    
    @property
    def codes_anc_region(self):
        return list(set([commune.code_anc_region for commune in self.communes]))
    
    @property
    def codes_nv_region(self):
        return list(set([commune.code_nv_region for commune in self.communes]))
    
    def ajout(self, commune):
        if commune not in self.communes:
            self.communes.append(commune)
        
    def __eq__(self, ze):
        return self.code == ze.code
    
    def __contains__(self, commune):
        return commune in self.communes
    
    def __repr__(self):
        return self.nom + ' (' + self.code + ')'

class Commune():
    
    def __init__(self, code_insee, nom, code_departement, code_ancienne_region, code_nouvelle_region):
        self.code_insee = code_insee
        self.nom = nom
        self.code_dep = code_departement
        self.code_anc_region = code_ancienne_region
        self.code_nv_region = code_nouvelle_region  

    def __eq__(self, commune):
        return self.code_insee == commune.code_insee
    
    def __repr__(self):
        return self.nom + ' (' + self.code_insee + ')'
    