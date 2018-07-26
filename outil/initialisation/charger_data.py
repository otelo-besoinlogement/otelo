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

import xlrd


class ZEDatas():
    
    '''
    Gestionnaire des données issues des packs B1 et B2 pour les zones d'emploi 
    '''
    
    def __init__(self):
        '''
        Constructeur
        
        zones -- dictionnaire
            clef : code de la zone d'emploi
            valeur : ZEData de la zone d'emploi 
        '''
        self.zones = dict()
    
    def importer_pack_donnees(self, fichier_pack, fichier_projection):
        '''
        Intègre les données des packs B1 et B2 dans l'attribut zones
        '''
        fpack = FichierPack(fichier_pack)
        fproj = FichierProjection(fichier_projection)
        for code in fpack.codes_zones:
            self.zones[code] = ZEData()
            self.zones[code].integrer_donnees_pack(fpack, code)
            self.zones[code].integrer_donnees_proj(fproj, code)

class ZEData():
    
    def __init__(self):
        '''
        Constructeur - Initialise les attributs qui accueilleront les valeurs pour chaque brique
        '''
        self.b1_synthese = {}
        # Brique 1-1
        self._b11_sa_rp = None
        self.b11_sa_sne = None
        self.b11_fortune_rp = None
        self.b11_fortune_sne_camping = None
        self.b11_fortune_sne_squat = None
        self.b11_hebergement = {}
        # Brique 1-2
        self.b12_heberges_filo = None
        self.b12_heberges_sne_particulier = None
        self.b12_heberges_sne_gratuit = None
        self.b12_heberges_sne_temporaire = None
        self.b12_hotel_rp = None
        self.b12_hotel_sne = None
        # Brique 1-3
        self.b13_inadequation_financiere = {}
        # Brique 1-4
        self.b14_mauvaise_qualite_rp = {}
        self.b14_mauvaise_qualite_ff = {}
        self.b14_mauvaise_qualite_filo = {}
        # Brique 1-5
        self.b15_suroccup_rp = {}
        self.b15_suroccup_filo = {}
        # Brique B2
        self.projection_filo = {}
        self.menages_omphale = {}
    
    def integrer_donnees_pack(self, fichier_pack, code_zone):
        '''
        Integre les données du pack B1 pour la ZE dans les attributs correspondants
        '''
        f = fichier_pack        
        self.b1_synthese = f.dict_ze_from_sheet('Synthèse des besoins', code_zone)
        
        self._b11_sa_rp = f.valeur('nb_personnes', code_zone, '1_1_SansAbris')
        self.b11_sa_sne = f.valeur('nb_menages', code_zone, '1_1_Sans_abris_SNE')
        self.b11_fortune_rp = f.valeur('nb_menages', code_zone,'1_1_HdFortune')
        self.b11_fortune_sne_camping = f.valeur('nb_menages_camping', code_zone, '1_1_HdFortune_SNE')
        self.b11_fortune_sne_squat = f.valeur('nb_menages_squat', code_zone, '1_1_HdFortune_SNE')
        self.b11_hebergement = f.b11_heberg(code_zone)
        
        self.b12_heberges_filo = f.valeur('nb_foyers_fiscaux_rev', code_zone, '1_2_Hébergés')
        self.b12_heberges_sne_gratuit = f.valeur('nb_menages_gratuit', code_zone, '1_2_Hébergés_SNE') 
        self.b12_heberges_sne_temporaire = f.valeur('nb_menages_temp', code_zone, '1_2_Hébergés_SNE') 
        self.b12_heberges_sne_particulier = f.valeur('nb_menages_particulier', code_zone, '1_2_Hébergés_SNE')
        self.b12_hotel_rp = f.valeur('nb_menages', code_zone, '1_2_Hotel')
        self.b12_hotel_sne = float(f.valeur('nb_menages', code_zone, '1_2_Hotel_SNE') or 0)
        
        self.b13_inadequation_financiere = f.dict_ze_from_sheet('1_3_Inadequation_financiere', code_zone)
        
        self.b14_mauvaise_qualite_rp = f.dict_ze_from_sheet('1_4_Mauvaise_qualité', code_zone)
        self.b14_mauvaise_qualite_ff = f.dict_ze_from_sheet('1_4_Mauvaise_qualité_FF', code_zone)
        self.b14_mauvaise_qualite_filo = f.dict_ze_from_sheet('1_4_Mauvaise_qualité_Filo', code_zone)
        
        self.b15_suroccup_rp = f.dict_ze_from_sheet('1_5_Suroccupation', code_zone)
        self.b15_suroccup_filo = f.dict_ze_from_sheet('1_5_Suroccupation_Filo', code_zone)
        
        self.b17_parc_social = f.dict_ze_from_sheet('1_7_Parc_social', code_zone)
        
        self.menages_omphale = f.dict_ze_from_sheet('2_1_Omphale_men', code_zone, etiquette_en_minuscule=True)
    
    def integrer_donnees_proj(self, fichier_projection, code_zone):
        '''
        Integre les données du pack B2 pour la ZE dans les attributs correspondants
        '''
        f = fichier_projection
        self.projection_filo = f.dict_ze_from_sheet('passage OTELO', code_zone)
    
    @property
    def b11_sa_rp(self):
        '''
        Corrige la donnée secrétisée issue de la brique B1.1 (Recensement)
        '''
        try:
            data = round(float(self._b11_sa_rp))
            return data
        except Exception as e:
            return 0

class FichierXLS:
    
    '''
    Classe facilitant la lecture et l'extraction des données d'un pack xls    
    '''
    
    def __init__(self, fichier_xls):
        '''
        Constructeur 
        
        classeur : Workbook du fichier_xls
        '''
        self.classeur = xlrd.open_workbook(fichier_xls)
        
    def dict_ze_from_sheet(self, nom_feuille, code_zone, etiquette_en_minuscule=False):
        '''
        Retourne les données correspondantes à une zone d'emploi pour la feuille designée
        sous la forme d'un dictionnaire
        
        Dictionnaire retourné :
        clef : etiquette d'entete (en minuscule si etiquette_en_minuscule est True)
        valeur: valeur pour la zone d'emploi
        '''
        menages = {}        
        entete = self.entete(nom_feuille)
        for colonne in entete[2:]:
            valeur = self.valeur(colonne, code_zone, nom_feuille)
            if not valeur:
                valeur = 0
            menages[colonne.lower() if etiquette_en_minuscule else colonne] = valeur
        return menages
    
    def entete(self, nom_feuille):
        '''
        Retourne l'entête de la feuille sous forme de liste de valeur
        '''
        feuille = self.classeur.sheet_by_name(nom_feuille)
        return [cell.value for cell in feuille.row(0)]
    
    def valeur(self, nom_colonne, code_zone, nom_feuille):
        '''
        Retourne la valeur associée à la zone d'emploi pour la colonne demandée
        '''
        feuille = self.classeur.sheet_by_name(nom_feuille)
        index_colonne = [cell.value for cell in feuille.row(0)].index(nom_colonne)
        index_ligne = [cell.value for cell in feuille.col(0)].index(code_zone)
        return feuille.cell(index_ligne, index_colonne).value
       


class FichierPack(FichierXLS):
    
    '''
    Classe facilitant la lecture et l'extraction des données d'un pack B1
    
    Hérite de la classe FichierXLS
    '''
    
    @property
    def codes_zones(self):
        '''
        Retourne la liste des codes des zones d'emploi présentes dans le pack B1
        ''' 
        feuille = self.classeur.sheet_by_name('1_1_SansAbris')
        return [cell.value for cell in feuille.col(0)][1:] 
    
    def b11_heberg(self, code_zone):
        '''
        Retourne un dictionnaire des différentes catégories d'hébergements de la brique B1.1
        avec leurs capacités
        
        Dictionnaire retourné :
        clef : categorie d'hébergement
        valeur : dictionnaire avec en clef le type de client et en valeur la capacité
        '''
        hebergements = {}
        nom_feuille = '1_1_Hébergement_social'
        entete = self.entete(nom_feuille)
        for colonne in entete[2:]:
            categorie = colonne.split('_')[0]
            client = colonne.split('_')[1]
            valeur = self.valeur(colonne, code_zone, nom_feuille)
            if valeur == '':
                valeur = 0
            if categorie not in hebergements.keys():
                hebergements[categorie] = {}
            hebergements[categorie][client] = valeur
        return hebergements


class FichierProjection(FichierXLS):
    
    '''
    Classe facilitant la lecture et l'extraction des données d'un pack B2
    
    Hérite de la classe FichierXLS    
    '''
    
    pass
  

