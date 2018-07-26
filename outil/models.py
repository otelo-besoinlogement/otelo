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
from django.db import transaction
from django.db import models
#from outil.initialisation.params import FICHIER_EPCI
from outil.initialisation.params import FICHIER_COMMUNE
from outil.initialisation.params import FICHIER_COMMUNE_EPCI
import csv

class ParametreZEManager(models.Manager):
    
    '''
    
    Classe permettant la gestion des paramètres des zones d'emploi
    
    '''
    
    @property
    def codes_zone(self):
        '''
        Renvoie la liste des codes des zones d'emploi présentes dans la base
        '''
        return [param_ze.code_ze for param_ze in self.all()]
    
    def multi(self, attributs, attr_compl=None):
        '''
        Renvoie True si toutes les valeurs des paramètres ZE sont identiques dans la base.
        Cette fonction permet de définir le type d'affichage (multi-ZE ou par ZE)
        
        - attributs : liste des paramètres à tester
        - attr_compl : si l'une des valeurs de ce paramètre est True, 
                        renvoie False (utile pour le cas des paramètres 'autre')   
        '''
        parametres_ze = self.all()
        criteres = tuple([getattr(parametres_ze[0], attribut) for attribut in attributs])
        for param_ze in parametres_ze:
            if attr_compl:
                check = getattr(param_ze, attr_compl)
                if check:
                    return False
            if criteres != tuple([getattr(param_ze, attribut) for attribut in attributs]):
                return False
        return True      
    
    def modifier_via_dict(self, attribut, dictionnaire, valeur_pour_code_non_present= None):        
        for code_zone, valeur in dictionnaire.items():
            param_ze = self.get(code_ze = code_zone)
            setattr(param_ze, attribut, valeur)
            param_ze.save()
        if valeur_pour_code_non_present is not None:
            for param_ze in self.all():
                if param_ze.code_ze not in dictionnaire.keys():
                    setattr(param_ze, attribut, valeur_pour_code_non_present)
                    param_ze.save()        
    
    def modifier_via_valeur(self, attribut, valeur):
        for param_ze in self.all():
            setattr(param_ze, attribut, valeur)
            param_ze.save()        
    
    def modifier_via_liste(self, attribut, liste_code):
        for param_ze in self.all():
            if param_ze.code_ze in liste_code:
                setattr(param_ze, attribut, True)
            else:
                setattr(param_ze, attribut, False)
            param_ze.save()
    
    def modifier_critere_b11_autre(self, criteres_au, donnees_autre):
        for param_ze in self.all():
            if param_ze.code_ze in criteres_au:
                param_ze.b11_autre = True
                param_ze.autre_source_b11 = int(donnees_autre[param_ze.code_ze])
            else:
                param_ze.b11_autre = False
                param_ze.autre_source_b11 = 0
            param_ze.save()
    
    def modifier_heberg_b12_autre(self, hebergs_aut, donnees_autre):
        for param_ze in self.all():    
            if param_ze.code_ze in hebergs_aut:
                param_ze.b12_heberg_autre = True
                param_ze.autre_source_b12 = int(donnees_autre[param_ze.code_ze])
            else:
                param_ze.b12_heberg_autre = False
                param_ze.autre_source_b12 = 0
            param_ze.save()
    
    def sauvegarder(self, fichier, description, sep='|'):
        with open(fichier, 'w', encoding='utf-8', newline='\n') as f:
            csvwriter = csv.writer(f, delimiter=sep)
            csvwriter.writerow([description])
            for param_ze in self.all():
                csvwriter.writerow(param_ze.ligne_export_csv())
    
    def description(self, fichier, sep='|'):
        with open(fichier, 'r', encoding='utf-8') as f:
            csvreader = csv.reader(f, delimiter=sep)
            return next(csvreader)[0]
    
    def charger(self, fichier, sep='|'):
        with open(fichier, 'r', encoding='utf-8') as f:
            csvreader = csv.reader(f, delimiter=sep)
            next(csvreader)
            for jeu_param in csvreader:
                parametres = self.all()[0].parametres
                code_zone = jeu_param[parametres.index('code_ze')]
                param_ze = self.get(code_ze = code_zone)
                for i, valeur in enumerate(jeu_param):
                    setattr(param_ze, parametres[i], valeur)
                param_ze.save()
                
        
class ParametreZE(models.Model):
    
    '''
    Classe Model du paramètrage d'une zone d'emploi
    '''
    
    CHOIX_SOURCE = (('RP', 'Recensement INSEE'), ('SNE', "Système National d'Enregistrement"), ('Autre', 'Autre source de données'))
    
    SCENARIOS_OMPHALE = {'Central_B': 'scénario central – décélération',
                        'Central_C': 'scénario central – tendanciel',
                        'Central_H': 'scénario central – accélération', 
                        'Central_M': 'scénario central – maintien',
                        'PH_C': 'scénario population haute – tendanciel', 
                        'PB_C': 'scénario population basse – tendanciel',}
    
    nom_ze = models.CharField(max_length=255)
    code_ze = models.CharField(max_length=6, unique=True)
    source_b11 = models.CharField(max_length=4, choices=CHOIX_SOURCE, default='RP')
    b11_sa = models.BooleanField(default=True)
    b11_fortune = models.BooleanField(default=True)
    b11_hotel = models.BooleanField(default=True)
    b11_autre = models.BooleanField(default=False)
    b11_etablissement = models.CharField(max_length=20, default='123456789AB')
    b11_part_etablissement = models.IntegerField(default=100)
    autre_source_b11 = models.IntegerField(default=0)
    b12_cohab_interg_subie = models.BooleanField(default=True)
    b12_heberg_particulier = models.BooleanField(default=True)
    b12_heberg_gratuit = models.BooleanField(default=True)
    b12_heberg_temporaire = models.BooleanField(default=True)
    b12_heberg_autre = models.BooleanField(default=False)
    autre_source_b12 = models.IntegerField(default=0)
    b13_taux_effort = models.IntegerField(default=30)
    b13_acc = models.BooleanField(default=True)
    b13_plp = models.BooleanField(default=True)
    source_b14 = models.CharField(max_length=4, default='RP')
    b14_rp_abs_sani = models.BooleanField(default=True)
    b14_rp_abs_sani_chauf = models.BooleanField(default=False)
    b14_ff_abs_wc = models.BooleanField(default=False)
    b14_ff_abs_sdb = models.BooleanField(default=False)
    b14_ff_abs_chauf = models.BooleanField(default=False)
    b14_ff_quali_ssent = models.BooleanField(default=False)
    b14_ff_quali_ssent_mv = models.BooleanField(default=False)
    b14_ff_quali_tt = models.BooleanField(default=True)
    b14_proprietaire = models.BooleanField(default=False)
    b14_locataire_hors_hlm = models.BooleanField(default=True)
    b15_rp_surp_mod = models.BooleanField(default=False)
    b15_rp_surp_acc = models.BooleanField(default=True)
    b15_filo_surp_mod = models.BooleanField(default=False)
    b15_filo_surp_acc = models.BooleanField(default=False)
    b15_proprietaire = models.BooleanField(default=False)
    b15_locataire_hors_hlm = models.BooleanField(default=True)
    b17_tout_menage = models.BooleanField(default=True)
    b17_hors_prb_env = models.BooleanField(default=False)
    b17_hors_assist_mat = models.BooleanField(default=False)
    b17_hors_demande_rapprochement = models.BooleanField(default=False)
    b17_hors_trois_motifs = models.BooleanField(default=False)
    b12_ventilation = models.IntegerField(default=100)
    b13_ventilation = models.IntegerField(default=100)
    b14_ventilation = models.IntegerField(default=100)
    b15_ventilation = models.IntegerField(default=100)
    b14_taux_rehabilitation = models.IntegerField(default=100)
    b1_taux_mobilite = models.IntegerField(default=50)
    b2_tx_restructuration = models.FloatField(default=9999)
    b2_tx_disparition = models.FloatField(default=9999)
    b2_tx_vacance = models.FloatField(default=9999)
    b2_tx_residence_secondaire = models.FloatField(default=9999)
    b2_choix_omphale = models.BooleanField(default=True)
    b2_scenario_omphale = models.CharField(max_length=50, default='Central_C')
    autre_source_b21 = models.IntegerField(default=0)
    horizon_resorption = models.IntegerField(default=20)
    
    objects = ParametreZEManager()
    
    @property
    def parametres(self):
        return [elt for elt in sorted(self.__dict__.keys()) if elt != '_state']
    
    def ligne_export_csv(self):
        return [getattr(self, attr) for attr in self.parametres]
    
    @property
    def sources_b11(self):
        source = 'aucune source'
        if self.b11_fortune or self.b11_hotel or self.b11_sa:
            source = 'Recensement 2014' if self.source_b11 == 'RP' else 'SNE 2016'
            if self.b11_autre and self.autre_source_b11 > 0:
                source += ' + source externe'
        else:
            if self.b11_autre and self.autre_source_b11 > 0:
                source = 'source externe'
        return source
    
    @property
    def categories_b11(self):
        categories = []
        if self.b11_sa:
            categories.append('Sans Abris')
        if self.b11_fortune:
            categories.append('Habitats de Fortune')
        if self.b11_hotel:
            categories.append("Logés à l'hôtel")
        if self.b11_autre:
            categories.append('Autres données')
        return ' - '.join(categories)
    
    @property
    def etablissements_b11(self):
        CATEGORIES_HEBERGEMENT = {
            '1' : 'Aire station nomades',
            '2' : 'Autre ctre.accueil',
            '3' : 'C.A.D.A.',
            '4' : 'C.H.R.S.',
            '5' : 'C.P.H.',
            '6' : 'Foyer jeunes trav.',
            '7' : 'Foyer trav. migrants',
            '8' : 'Héberg.fam.malades',
            '9' : 'Log.foyer non spéc.',
            'A' : 'Maisons relais-pens.',
            'B' : 'Resid.soc. hors MRel',
        }
        etablissements = []
        for num, etablissement in CATEGORIES_HEBERGEMENT.items():
            if num in self.b11_etablissement:
                etablissements.append(etablissement)
        if len(etablissements) > 0:
            return ' - '.join(etablissements)
        return "Aucune catégorie d'établissement retenue"
    
    @property
    def categories_b12(self):
        categories = []
        if self.b12_heberg_particulier:
            categories.append('Logés chez un particulier')
        if self.b12_heberg_gratuit:
            categories.append('Logés à titre gratuit')
        if self.b12_heberg_temporaire:
            categories.append("Logés temporairement")
        if self.b12_heberg_autre:
            categories.append('Autres données')
        return ' - '.join(categories)
    
    @property
    def categories_b13(self):
        categories = []
        if self.b13_acc:
            categories.append('Accédants')
        if self.b13_plp:
            categories.append('Locataires du parc privé')
        #if self.b13_pls:
        #    categories.append("Locataires du parc social")
        if len(categories) > 0:
            return ', '.join(categories) + " dont le taux d'effort est supérieur à {0}%.".format(str(self.b13_taux_effort))
        return 'aucune catégorie selectionnée'
    
    @property
    def sources_b14(self):
        if self.source_b14 == 'FF':
            return 'Fichiers fonciers 2015'
        elif self.source_b14 == 'RP':
            return 'Recensement 2014'
        elif self.source_b14 == 'PPPI':
            return 'Filocom 2015'
    
    @property
    def champs_b14(self):
        description = ''
        categories = []        
        if self.b14_proprietaire:
            categories.append('Propriétaires occupants')
        if self.b14_locataire_hors_hlm:
            categories.append('Locataires hors parc social')
        if len(categories) > 0:
            description = ', '.join(categories)
        
        if self.source_b14 == 'PPPI':
            description += ' dont le logement est potentiellement indigne.'
        elif self.source_b14 == 'RP':
            if self.b14_rp_abs_sani:
                description += ' dont le logement ne possède pas de sanitaires.'
            if self.b14_rp_abs_sani_chauf:
                description += ' dont le logement ne possède ni sanitaires ni chauffage.'            
        if self.source_b14 == 'FF':
            description += ' dont le logement'
            if self.b14_ff_quali_ssent_mv:
                description += ', sans entretien et de mauvaise qualité,'
            elif self.b14_ff_quali_ssent:
                description += ', sans entretien,'
            description += ' ne possède pas '
            if self.b14_ff_abs_wc:
                description += "de wc, "
            if self.b14_ff_abs_sdb:
                description += "de salle de bain, "
            if self.b14_ff_abs_chauf:
                description += "de chauffage, "
            description = description[:-2] + '.'
        return description
    
    @property
    def sources_b15(self):
        if self.b15_rp_surp_mod or self.b15_rp_surp_acc:
            return 'Recensement 2014'
        if self.b15_filo_surp_mod or self.b15_filo_surp_acc:
            return 'Filocom 2015'
        return '---'
    
    @property
    def surocc_b15(self):
        if self.b15_rp_surp_mod:
            return ' en suroccupation modérée.'
        if self.b15_rp_surp_acc:
            return ' en suroccupation accentuée.'
        if self.b15_filo_surp_mod:
            return ' en suroccupation légère.'
        if self.b15_filo_surp_acc:
            return ' en suroccupation lourde.'
        return '---'
    
    @property
    def categories_b15_cat(self):
        categories = []
        if self.b15_proprietaire:
            categories.append('Propriétaires')
        if self.b15_locataire_hors_hlm:
            categories.append('Locataires du parc privé')
        #if self.b15_locataire_hlm:
        #    categories.append('Locataires du parc social')
        return ', '.join(categories)

    @property
    def categories_b17(self):
        if self.b17_tout_menage:
            description = 'Prise en compte de toutes les demandes quelque soit le motif.'
        if self.b17_hors_prb_env:
            description = "Prise en compte de toutes les demandes sauf celles pour problème d'environnement ou de voisinage."
        if self.b17_hors_assist_mat:
            description = 'Prise en compte de toutes les demandes sauf celles pour assistant(e) maternel(le) ou familial(e).'
        if self.b17_hors_demande_rapprochement:
            description = "Prise en compte de toutes les demandes sauf celles pour rapprochement des équipements et des services."
        if self.b17_hors_trois_motifs:
            description = "Prise en compte de toutes les demandes sauf celles pour problème d'environnement ou de voisinage, assistant(e) maternel(le) ou familial(e) ou rapprochement des équipements et des services."
        return description
    
    @property
    def scenario_evolution_retenu(self):
        if not self.b2_choix_omphale:
            return 'scénario hors Omphale'
        else:            
            return 'Omphale 2017 - scénario {0}'.format(self.SCENARIOS_OMPHALE[self.b2_scenario_omphale])
    
    @property
    def idf(self):
        if self.code_ze[:2] == '11' or self.code_ze == '0056':
            return True
        return False
    
    @property
    def ratio_4_3(self):
        if self.b13_taux_effort < 35:
            if self.idf:
                return 0.0257
            else:
                return 0.0521
        else:
            if self.idf:
                return 0.017
            else:
                return 0.0441
    
    @property
    def ratio_2_5(self):
        if self.idf:
            return 0.1729
        else:
            return 0.0025
    
    @property
    def ratio_3_5(self):
        if self.b13_taux_effort < 35:
            if self.idf:
                return 0.077
            else:
                return 0.0101
        else:
            if self.idf:
                return 0.0753
            else:
                return 0.0142
            
    @property
    def ratio_4_5(self):
        if self.idf:
            return 0.1001
        else:
            return 0.0116
    
'''        
class EpciManager(models.Manager):
    
    def integrer_epci(self):
        Epci.objects.all().delete()
        #with open(FICHIER_EPCI, 'r', encoding = 'utf-8') as f:
        with open(FICHIER_COMMUNE, 'r', encoding = 'utf-8') as f:
            lignes = csv.reader(f, delimiter = ';')
            next(lignes) # enlever l'entête
            for ligne in lignes:
                #if len(Epci.objects.filter(code = str(ligne[2]))) == 0:
                    #e = Epci(code=ligne[2], nom=ligne[3])
                if len(Epci.objects.filter(code = str(ligne[4]))) == 0:
                    e = Epci(code=ligne[4], nom=ligne[5])
                    print(e)
                    e.save()
    

class Epci(models.Model):
    code = models.CharField(max_length=15, unique = True)
    nom = models.CharField(max_length=255)
    
    objects = EpciManager()
    
    def __str__(self):
        return self.nom
'''    
    
    

class CommuneManager(models.Manager):
    
    @property
    def classes_modifiees(self):
        for commune in self.all():
            if commune.classe != 9999:
                return True
        return False 
    
    def reinitiliser_classe(self):
        for commune in self.all():
            commune.classe = 9999
            commune.save()

    def modifier_classes(self, classes_commune):
        for code, classe in classes_commune.items():
            commune = self.get(code = code)
            commune.classe = classe
            commune.save()
    
    def modifier_epcis(self, epcis_commune):
        for code, code_epci in epcis_commune.items():
            commune = self.get(code = code)
            commune.code_epci = code_epci
            commune.nom_epci = self.nom_epci(code_epci)
            commune.save()
    
    def nom_epci(self, code_epci):
        communes = self.filter(code_epci = code_epci)
        return communes[0].nom_epci
     
    def sauvegarder(self, fichier, sep='|'):
        with open(fichier, 'w', encoding='utf-8', newline='\n') as f:
            csvwriter = csv.writer(f, delimiter=sep)
            for commune in self.all():
                if commune.classe != 9999:
                    csvwriter.writerow([commune.code, commune.classe])
    
    def charger(self, fichier, sep='|'):
        with open(fichier, 'r', encoding='utf-8') as f:
            csvreader = csv.reader(f, delimiter=sep)
            for jeu_param in csvreader:
                commune = self.get(code = jeu_param[0])
                commune.classe = jeu_param[1]
                commune.save()
    
    @transaction.atomic
    def integrer_communes(self):
        Commune.objects.all().delete()
        # récupération des epcis 2017 pour communes 2015
        '''
        code_epcis = {}
        nom_epcis = {}
        nom_communes = {}
        with open(FICHIER_COMMUNE_EPCI, 'r', encoding = 'utf-8') as f:
            lignes = csv.reader(f, delimiter = '|')
            next(lignes)
            for ligne in lignes:
                code_epcis[ligne[0]] = ligne[2]
                nom_epcis[ligne[0]] = ligne[3]
                nom_communes[ligne[0]] = ligne[1]
        '''
        # integration des communes 2015   
        with open(FICHIER_COMMUNE, 'r', encoding = 'utf-8') as f:
            lignes = csv.reader(f, delimiter = ';')
            next(lignes) # enlever l'entête
            for ligne in lignes:
                c = Commune(code = ligne[0].zfill(5),
                            nom = ligne[1],#nom_communes[ligne[0].zfill(5)],
                            code_ze = ligne[2].zfill(4),
                            code_epci = ligne[4],#code_epcis[ligne[0].zfill(5)] if ligne[0].zfill(5) in code_epcis.keys() else '',
                            nom_epci = ligne[5],#nom_epcis[ligne[0].zfill(5)] if ligne[0].zfill(5) in code_epcis.keys() else '',
                            classe_init = int(ligne[12]) if ligne[12] != ' ' else 7,
                            nb_logements = int(ligne[7]) if ligne[7] != ' ' else 0,
                            nb_logements_ze = int(ligne[9]),
                            vacance1 = float(ligne[15]) if ligne[15] != ' ' else 0,
                            vacance2 = float(ligne[16]) if ligne[16] != ' ' else 0,
                            vacance3 = float(ligne[17]) if ligne[17] != ' ' else 0,
                            vacance4 = float(ligne[18]) if ligne[18] != ' ' else 0,
                            vacance5 = float(ligne[19]) if ligne[19] != ' ' else 0,
                            vacance6 = float(ligne[20]) if ligne[20] != ' ' else 0,
                            vacance7 = float(ligne[21]) if ligne[21] != ' ' else 0,
                            rs1 = float(ligne[22]) if ligne[22] != ' ' else 0,
                            rs2 = float(ligne[23]) if ligne[23] != ' ' else 0,
                            rs3 = float(ligne[24]) if ligne[24] != ' ' else 0,
                            rs4 = float(ligne[25]) if ligne[25] != ' ' else 0,
                            rs5 = float(ligne[26]) if ligne[26] != ' ' else 0,
                            rs6 = float(ligne[27]) if ligne[27] != ' ' else 0,
                            rs7 = float(ligne[28]) if ligne[28] != ' ' else 0,
                            disparition1 = float(ligne[29]) if ligne[29] != ' ' else 0,
                            disparition2 = float(ligne[30]) if ligne[30] != ' ' else 0,
                            disparition3 = float(ligne[31]) if ligne[31] != ' ' else 0,
                            disparition4 = float(ligne[32]) if ligne[32] != ' ' else 0,
                            disparition5 = float(ligne[33]) if ligne[33] != ' ' else 0,
                            disparition6 = float(ligne[34]) if ligne[34] != ' ' else 0,
                            disparition7 = float(ligne[35]) if ligne[35] != ' ' else 0,
                            tdm1 = float(ligne[36]) if ligne[36] != ' ' else 0,
                            tdm2 = float(ligne[37]) if ligne[37] != ' ' else 0,
                            tdm3 = float(ligne[38]) if ligne[38] != ' ' else 0,
                            tdm4 = float(ligne[39]) if ligne[39] != ' ' else 0,
                            tdm5 = float(ligne[40]) if ligne[40] != ' ' else 0,
                            tdm6 = float(ligne[41]) if ligne[41] != ' ' else 0,
                            tdm7 = float(ligne[42]) if ligne[42] != ' ' else 0)
                print(c)
                c.save()
        

class Commune(models.Model):
    
    code = models.TextField(max_length=5, unique=True)
    nom = models.TextField(max_length=60)
    code_ze = models.TextField(max_length=5)
    code_epci = models.TextField(max_length=10)
    nom_epci = models.TextField(max_length=150)
    classe_init = models.IntegerField()
    classe = models.IntegerField(default=9999)
    nb_logements = models.IntegerField(default=0)
    nb_logements_ze = models.IntegerField(default=0)
    vacance1 = models.FloatField(default=0)
    vacance2 = models.FloatField(default=0)
    vacance3 = models.FloatField(default=0)
    vacance4 = models.FloatField(default=0)
    vacance5 = models.FloatField(default=0)
    vacance6 = models.FloatField(default=0)
    vacance7 = models.FloatField(default=0)
    rs1 =  models.FloatField(default=0)
    rs2 =  models.FloatField(default=0)
    rs3 =  models.FloatField(default=0)
    rs4 =  models.FloatField(default=0)
    rs5 =  models.FloatField(default=0)
    rs6 =  models.FloatField(default=0)
    rs7 = models.FloatField(default=0)
    disparition1 = models.FloatField(default=0)
    disparition2 = models.FloatField(default=0)
    disparition3 = models.FloatField(default=0)
    disparition4 = models.FloatField(default=0)
    disparition5 = models.FloatField(default=0)
    disparition6 = models.FloatField(default=0)
    disparition7 = models.FloatField(default=0)
    tdm1 = models.FloatField(default=0)
    tdm2 = models.FloatField(default=0)
    tdm3 = models.FloatField(default=0)
    tdm4 = models.FloatField(default=0)
    tdm5 = models.FloatField(default=0)
    tdm6 = models.FloatField(default=0)
    tdm7 = models.FloatField(default=0)

    objects = CommuneManager()
    
    def __str__(self):
        return self.nom
    
    @property
    def departement(self):
        return self.code[:2] if not self.code.startswith('97') else self.code[:3] 
    
    def classification(self):
        return self.classe if self.classe != 9999 else self.classe_init
    
    @property
    def classe_calcul(self):
        classe_calcul = {4 : 1, # classe du Guide : classe de calcul
                         6 : 2,
                         7 : 3,
                         3 : 4,
                         5 : 5,
                         1 : 6,
                         2 : 7}
        return classe_calcul[self.classe] if self.classe != 9999 else classe_calcul[self.classe_init]
    
    @property
    def coeff_vacance(self):
        return getattr(self, 'vacance' + str(self.classe_calcul))
    
    @property
    def coeff_rs(self):
        return getattr(self, 'rs' + str(self.classe_calcul))
    
    @property
    def coeff_disparition(self):
        return getattr(self, 'disparition' + str(self.classe_calcul))
    
    @property
    def coeff_tdm(self):
        return getattr(self, 'tdm' + str(self.classe_calcul))
    
    def besoin_en_logement_naif(self, besoin_logement_ze):
        if besoin_logement_ze == 0:
            return 0 # a vérifier!
        resultat = self.nb_logements * besoin_logement_ze / self.nb_logements_ze
        return round(resultat)
    
    def besoin_en_logement_brut(self, besoin_logement_ze):
        if besoin_logement_ze == 0:
            return 0 # a vérifier!
        resultat = self.nb_logements * ((1 + 0.01 * self.coeff_vacance + 0.01 * self.coeff_rs + 0.01 * self.coeff_disparition - 0.01 * self.coeff_tdm) * (1 + (besoin_logement_ze/self.nb_logements_ze)) - 1)
        return round(resultat)

    def besoin_en_logement_borne(self, besoin_logement_ze):
        resultat = self.besoin_en_logement_brut(besoin_logement_ze)
        return resultat if resultat >= 0 else 0
    
    