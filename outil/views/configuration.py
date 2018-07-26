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

import os
import time
from django.db import transaction
from django.shortcuts import render
from django.shortcuts import redirect
from outil.models import ParametreZE
from outil.models import Commune
from outil.initialisation.charger_bdd import init_bdd
from outil.initialisation.charger_bdd import init_classe_communes
from outil.initialisation.charger_bdd import init_communes
from outil.initialisation.params import REPERTOIRE_SAUVEGARDE
from outil.calcul.calculs_ze import CalculZE

@transaction.atomic
def initialisation(request):
    """
    Vue permettant la réinitialisation de la base de données de paramètrage
    """
    init_bdd()
    message_succes = 'Paramètrages (volet B) réinitialisés'
    return render(request, 'succes.html', locals())

@transaction.atomic
def initialisation_classe(request):
    """
    Vue permettant la réinitialisation des classes de commune dans la base de données
    """
    init_classe_communes()
    message_succes = 'Classes communales (volet C) réinitialisées'
    return render(request, 'succes.html', locals())

def initialisation_commune(request):
    """
    Vue permettant la réinitialisation des communes/EPCI
    """
    init_communes()
    message_succes = 'Communes et EPCI associés réinitialisés'
    return render(request, 'succes.html', locals())

def sauvegarde(request):
    """
    Vue permettant la sauvegarde du paramétrage dans un fichier .cfg (voire .cfgclass)
    Le répertoire de sauvegarde est défini dans la variable REPERTOIRE_SAUVEGARDE
    """
    message_erreur = None
    if request.method == 'POST':
        try:
            fichier = 'save_config_{0}.cfg'.format(time.strftime('%Y_%m_%d_%H%M%S'))
            chemin_fichier = os.path.join(REPERTOIRE_SAUVEGARDE, fichier)
            description = request.POST['description']
            ParametreZE.objects.sauvegarder(chemin_fichier, description)
            message_succes = 'Configuration des paramètres sauvegardée dans {0} avec la description : {1}'.format(fichier, description)
            if Commune.objects.classes_modifiees:
                fichier_modif_classe = fichier.replace('.cfg', '.cfgclass')
                chemin_fichier_modif_classe = os.path.join(REPERTOIRE_SAUVEGARDE, fichier_modif_classe)
                Commune.objects.sauvegarder(chemin_fichier_modif_classe)
                message_succes += '</p><p>Modification des classes communales sauvegardée dans {0}'.format(fichier_modif_classe)
            return render(request, 'succes.html', locals())
        except Exception as e:
            print(e)
            message_erreur = 'Impossible de sauvegarder la configuration.'
    return render(request, 'sauvegarde_config.html', locals())

@transaction.atomic
def chargement_config(request):
    """
    Vue permettant le chargement ou la suppression du paramétrage depuis un fichier .cfg (voire .cfgclass)
    Le répertoire de sauvegarde est défini dans la variable REPERTOIRE_SAUVEGARDE
    """
    message_erreur = None
    if request.method == 'POST':
        if 'load' in request.POST:
            chemin_fichier = os.path.join(REPERTOIRE_SAUVEGARDE, request.POST['fichier'])
            try:
                ParametreZE.objects.charger(chemin_fichier)
                message_succes = 'Configuration des paramètres chargée'
                chemin_fichier_modif_classe = chemin_fichier.replace('.cfg', '.cfgclass')
                if os.path.exists(chemin_fichier_modif_classe):
                    Commune.objects.charger(chemin_fichier_modif_classe)
                    message_succes += '</p><p>Modification des classes communales chargée'
                else:
                    init_classe_communes()
                    message_succes += "</p><p>Fichier de modification des classes communales inexistant. Les classes par défaut ont été affectées." 
                return render(request, 'succes.html', locals())
            except Exception as e:
                print(e)
                message_erreur = 'Impossible de charger le fichier {0}'.format(chemin_fichier)
        elif 'delete' in request.POST:
            try:
                chemin_fichier = os.path.join(REPERTOIRE_SAUVEGARDE, request.POST['fichier'])
                if os.path.exists(chemin_fichier):
                    os.remove(chemin_fichier)
                chemin_fichier_modif_classe = chemin_fichier.replace('.cfg', '.cfgclass')
                if os.path.exists(chemin_fichier_modif_classe):
                    os.remove(chemin_fichier_modif_classe)
            except Exception as e:
                print(e)
                message_erreur = 'Impossible de supprimer la configuration'
    fichiers_config = [(fichier, 
                        ParametreZE.objects.description(os.path.join(REPERTOIRE_SAUVEGARDE, fichier))) for fichier in os.listdir(REPERTOIRE_SAUVEGARDE) if fichier.endswith('.cfg')]        
    return render(request, 'chargement_config.html', locals())

'''

REDIRECTIONS

'''


REDIRECTION_SUIVANTE = {'/tpl/b11': 'outil:brique_1_2',
                        '/tpl/b12': 'outil:brique_1_3',
                        '/tpl/b13': 'outil:brique_1_4',
                        '/tpl/b14': 'outil:brique_1_5',
                        '/tpl/b15': 'outil:brique_1_6',
                        '/tpl/b16': 'outil:brique_1_7',
                        '/tpl/b17': 'outil:voletB1_ventilation',
                        '/tpl/b1-ventilation': '/tpl/b_resorption',
                        '/tpl/b_resorption': 'outil:brique_2_1',
                        '/tpl/b21': 'outil:brique_2_2',
                        '/tpl/b22': '/tpl/c_classe_commune',
                        }

'''

Fonction de traitement du POST

'''

def traitement_post(post, form_analyse, besoin_validation = False):
    message_erreur = None
    if 'next' in post:
        return message_erreur, True
    form = form_analyse(post)
    if besoin_validation:
        success, message_erreur = form.is_valid()
    if not message_erreur:
        form.modifier_parametres()
        #if 'save_and_next' in post:
        #    return message_erreur, True 
    return message_erreur, False
    

'''

Classe pour l'analyse des formulaires

'''

class FormAnalyse:
    
    def __init__(self, post):
        self.post = post
    
    def choix_mono_multi(self, type):
        if 'choix-{0}-mono-multi'.format(type) in self.post:
            return self.post['choix-{0}-mono-multi'.format(type)]
        return None

    def valeur_radio_multi(self, type):
        if 'multi-{0}-ze'.format(type) in self.post:
            return self.post['multi-{0}-ze'.format(type)]
        return None
    
    def boolean_radio_multi(self, type, valeur):
        if 'multi-{0}-ze'.format(type) in self.post:
            return True if self.post['multi-{0}-ze'.format(type)] == valeur else False
        return None
    
    def dictionnaire_radio_mono(self, prefixe):
        '''
        Dictionnaire : 
            - clef : code ZE
            - valeur : valeur retournee par le formulaire pour la valeur prefixe + code ZE
        '''
        prefixe = 'mono-{0}-ze'.format(prefixe)
        parametres = {k[len(prefixe):]: v for k, v in self.post.items() if k.startswith(prefixe)}
        if len(parametres) == 0:
            return {}
        return parametres
    
    def dictionnaire_boolean_radio_mono(self, prefixe, bool):
        prefixe = 'mono-{0}-ze'.format(prefixe)
        parametres = {k[len(prefixe):]: bool[v] for k, v in self.post.items() if k.startswith(prefixe)}
        if len(parametres) == 0:
            return {}
        return parametres
    
    def boolean_checkbox_multi(self, prefixe, suffixe):
        prefixe = 'multi-{0}-ze-'.format(prefixe)
        if prefixe + suffixe in self.post:
            return True
        return False
    
    def liste_checkbox_mono(self, prefixe, suffixe):
        '''
        Liste des codes ZE pour lesquels le critere est coché
        '''
        prefixe = 'mono-{0}-ze-'.format(prefixe)
        parametres = [k[len(prefixe + suffixe):] for k, v in self.post.items() if k.startswith(prefixe + suffixe)]
        if len(parametres) == 0:
            return []
        return parametres 
    


'''

ACCUEIL

'''

def accueil(request):
    (message_erreur, redirection) = traitement_post(request.POST, FormAnalyseB11, besoin_validation=True) if request.method == 'POST' else (None, False)    
    if redirection:
        return redirect(REDIRECTION_SUIVANTE[request.path])
        
    parametres = ParametreZE.objects.all()
    return render(request, 'accueil.html', locals())

'''

BRIQUE B11

'''

@transaction.atomic
def b11(request):
    (message_erreur, redirection) = traitement_post(request.POST, FormAnalyseB11, besoin_validation=True) if request.method == 'POST' else (None, False)    
    if redirection:
        return redirect(REDIRECTION_SUIVANTE[request.path])
        
    parametres = ParametreZE.objects.all()
    multi_source = ParametreZE.objects.multi(['source_b11'])
    valeurs_source = [('RP', 'Recensement', 'source_b11','RP'), 
                      ('SNE', 'SNE', 'source_b11', 'SNE')]
    multi_critere = ParametreZE.objects.multi(['b11_sa', 'b11_fortune', 'b11_hotel'], attr_compl = 'b11_autre')
    valeurs_critere = [('sa', 'Sans Abris', 'b11_sa', True),
                       ('fo', 'Habitations de fortune', 'b11_fortune', True),
                       ('ho', "Logés à l'hôtel", 'b11_hotel', True),
                       ('au', '(+) Autre :', 'b11_autre', True)]
    multi_etablissement = ParametreZE.objects.multi(['b11_etablissement'])
    valeurs_etablissement = [('1', 'Aire nomades'), ('2', "Autre centre d'accueil"), ('3', 'C.A.D.A'),
                             ('4', 'C.H.R.S'), ('5', 'C.P.H'), ('6', "Foyer jeunes travailleurs"), ('7', 'Foyer travailleurs migrants'),
                             ('8', 'Hébergement fam. malades'), ('9', 'Logements foyer non spécialisé'), ('A', 'Maisons relais-pension'),
                             ('B', 'Résidence sociale hors maisons relais')]
    parametre_etablissement = 'b11_etablissement'
    multi_taux_etablissement = ParametreZE.objects.multi(['b11_part_etablissement'])
    parametre_taux_etablissement = 'b11_part_etablissement'
    return render(request, 'b11.html', locals())


class FormAnalyseB11(FormAnalyse):
    
    @property
    def etablissement_multi(self):        
        if 'etablissement-multi' in self.post:
            return ''.join(self.post.getlist('etablissement-multi'))
        return None
    
    @property
    def etablissement_mono(self):
        parametres = {k[18:]: ''.join(self.post.getlist(k)) for k in self.post if k.startswith('etablissement-mono')}
        if len(parametres) == 0:
            return {}
        return parametres
    
    @property
    def taux_etablissement_multi(self):        
        if 'number-taux_etablissement-multi' in self.post:
            return int(self.post['number-taux_etablissement-multi'])
        return None
    
    @property
    def taux_etablissement_mono(self):
        parametres = {k[30:]: int(self.post[k]) for k in self.post if k.startswith('number-taux_etablissement-mono')}
        if len(parametres) == 0:
            return {}
        return parametres
    
    def is_valid(self):
        '''
        S'assure de la validité des valeurs saisies qui doivent être entières
        '''
        for code, donnee in self.donnees_autre_mono.items():
            try:
                d = int(donnee)
            except ValueError:
                return False, 'Donnée saisie incorrecte pour zone ' + code
        return True, None        
    
    def modifier_parametres(self):
        if self.choix_mono_multi('source') == 'mono':
            ParametreZE.objects.modifier_via_dict('source_b11', self.dictionnaire_radio_mono('source'))
        elif self.choix_mono_multi('source') == 'multi':
            message_erreur = ParametreZE.objects.modifier_via_valeur('source_b11', self.valeur_radio_multi('source'))
        if self.choix_mono_multi('critere') == 'mono':
            ParametreZE.objects.modifier_via_liste('b11_sa', self.liste_checkbox_mono('critere', 'sa')) 
            ParametreZE.objects.modifier_via_liste('b11_fortune',self.liste_checkbox_mono('critere', 'fo')) 
            ParametreZE.objects.modifier_via_liste('b11_hotel',self.liste_checkbox_mono('critere', 'ho'))
            message_erreur = ParametreZE.objects.modifier_critere_b11_autre(self.liste_checkbox_mono('critere', 'au'), self.donnees_autre_mono)
        elif self.choix_mono_multi('critere') == 'multi':
            ParametreZE.objects.modifier_via_valeur('b11_sa', self.boolean_checkbox_multi('critere', 'sa'))
            ParametreZE.objects.modifier_via_valeur('b11_fortune', self.boolean_checkbox_multi('critere','fo')) 
            ParametreZE.objects.modifier_via_valeur('b11_hotel', self.boolean_checkbox_multi('critere','ho'))
            ParametreZE.objects.modifier_via_valeur('b11_autre', False)
            ParametreZE.objects.modifier_via_valeur('autre_source_b11', 0)
        if self.choix_mono_multi('etablissement') == 'mono':
            ParametreZE.objects.modifier_via_dict('b11_etablissement', self.etablissement_mono, valeur_pour_code_non_present='X')
        elif self.choix_mono_multi('etablissement') == 'multi':
            ParametreZE.objects.modifier_via_valeur('b11_etablissement', self.etablissement_multi or 'X')
        if self.choix_mono_multi('taux_etablissement') == 'mono':
            ParametreZE.objects.modifier_via_dict('b11_part_etablissement', self.taux_etablissement_mono, valeur_pour_code_non_present=100)
        elif self.choix_mono_multi('taux_etablissement') == 'multi':
            ParametreZE.objects.modifier_via_valeur('b11_part_etablissement', self.taux_etablissement_multi if self.taux_etablissement_multi is not None else 100)
    
    @property
    def donnees_autre_mono(self):
        codes = self.liste_checkbox_mono('critere', 'au')
        datas = {}
        for code in codes:
            datas[code] = self.post['data' + code]
        return datas  
 
'''

BRIQUE B12

'''

@transaction.atomic 
def b12(request):
    (message_erreur, redirection) = traitement_post(request.POST, FormAnalyseB12, besoin_validation=True) if request.method == 'POST' else (None, False)    
    if redirection:
        return redirect(REDIRECTION_SUIVANTE[request.path])
        
    parametres = ParametreZE.objects.all()
    multi_cohab = ParametreZE.objects.multi(["b12_cohab_interg_subie"])
    valeurs_cohab = [('Oui', 'Prise en compte','b12_cohab_interg_subie', True), 
                     ('Non', 'Non prise en compte','b12_cohab_interg_subie', False)]
    multi_heberg = ParametreZE.objects.multi(['b12_heberg_particulier', 'b12_heberg_gratuit', 'b12_heberg_temporaire'], attr_compl='b12_heberg_autre')
    valeurs_heberg = [('par','Logés chez un particulier','b12_heberg_particulier', True),
                      ('gra','Logés à titre gratuit','b12_heberg_gratuit', True),
                      ('tmp','Logés temporairement','b12_heberg_temporaire', True),
                      ('aut', '(+) Autre:', 'b12_heberg_autre', True)
                      ]
    return render(request, 'b12.html', locals())


class FormAnalyseB12(FormAnalyse):
    
    def is_valid(self):
        '''
        S'assure de la validité des valeurs saisies qui doivent être entières
        '''
        for code, donnee in self.donnees_autre_mono.items():
            try:
                d = int(donnee)
            except ValueError:
                return False, 'Donnée saisie incorrecte pour zone ' + code
        return True, None        
    
    def modifier_parametres(self):
        if self.choix_mono_multi('cohab')== 'mono':
            bool = {'Oui': True, 'Non':False}
            ParametreZE.objects.modifier_via_dict('b12_cohab_interg_subie', self.dictionnaire_boolean_radio_mono('cohab', bool))
        elif self.choix_mono_multi('cohab') == 'multi':
            ParametreZE.objects.modifier_via_valeur('b12_cohab_interg_subie', self.boolean_radio_multi('cohab', 'Oui'))
        if self.choix_mono_multi('heberg')== 'mono':
            ParametreZE.objects.modifier_via_liste('b12_heberg_particulier', self.liste_checkbox_mono('heberg', 'par')) 
            ParametreZE.objects.modifier_via_liste('b12_heberg_gratuit', self.liste_checkbox_mono('heberg','gra'))
            ParametreZE.objects.modifier_via_liste('b12_heberg_temporaire',self.liste_checkbox_mono('heberg','tmp'))                                                         
            ParametreZE.objects.modifier_heberg_b12_autre(self.liste_checkbox_mono('heberg','aut'), self.donnees_autre_mono)
        elif self.choix_mono_multi('heberg') == 'multi':
            ParametreZE.objects.modifier_via_valeur('b12_heberg_particulier', self.boolean_checkbox_multi('heberg', 'par')) 
            ParametreZE.objects.modifier_via_valeur('b12_heberg_gratuit', self.boolean_checkbox_multi('heberg', 'gra')) 
            ParametreZE.objects.modifier_via_valeur('b12_heberg_temporaire', self.boolean_checkbox_multi('heberg', 'tmp'))
            ParametreZE.objects.modifier_via_valeur('b12_heberg_autre', False)
            ParametreZE.objects.modifier_via_valeur('autre_source_b12', 0) 
    
  
    @property
    def donnees_autre_mono(self):
        codes = self.liste_checkbox_mono('heberg', 'aut')
        datas = {}
        for code in codes:
            datas[code] = self.post['data' + code]
        return datas                
    
'''

BRIQUE B13

'''
 
@transaction.atomic 
def b13(request):
    (message_erreur, redirection) = traitement_post(request.POST, FormAnalyseB13) if request.method == 'POST' else (None, False)    
    if redirection:
        return redirect(REDIRECTION_SUIVANTE[request.path])
    parametres = ParametreZE.objects.all()
    multi_taux = ParametreZE.objects.multi(['b13_taux_effort'])
    valeurs_taux = [(25, '25 %'), (30, '30 %'),(33, '33 %'), (35, '35 %'), (40, '40 %'),]
    parametre_taux = 'b13_taux_effort'
    multi_categorie = ParametreZE.objects.multi(['b13_acc', 'b13_plp'])
    valeurs_categorie = [('acc', 'Accédants', 'b13_acc', True),
                         ('plp', 'Locataires du parc privé', 'b13_plp', True),
                         ] 
    return render(request, 'b13.html', locals())


class FormAnalyseB13(FormAnalyse):

    @property
    def taux_multi(self):
        if 'taux-multi' in self.post:
            return int(self.post['taux-multi'])
        return None
    
    @property
    def taux_mono(self):
        parametres = {k[9:]: int(v) for k, v in self.post.items() if k.startswith('taux-mono')}
        if len(parametres) == 0:
            return {}
        return parametres
        
    def modifier_parametres(self):
        if self.choix_mono_multi('taux') == 'multi':
            ParametreZE.objects.modifier_via_valeur('b13_taux_effort', self.taux_multi)
        elif self.choix_mono_multi('taux') == 'mono':
            ParametreZE.objects.modifier_via_dict('b13_taux_effort', self.taux_mono)
        if self.choix_mono_multi('categorie') == 'multi':
            ParametreZE.objects.modifier_via_valeur('b13_acc', self.boolean_checkbox_multi('categorie', 'acc'))
            ParametreZE.objects.modifier_via_valeur('b13_plp', self.boolean_checkbox_multi('categorie', 'plp'))
        elif self.choix_mono_multi('categorie') == 'mono':
            ParametreZE.objects.modifier_via_liste('b13_acc', self.liste_checkbox_mono('categorie', 'acc'))
            ParametreZE.objects.modifier_via_liste('b13_plp', self.liste_checkbox_mono('categorie', 'plp'))
            
            
'''

BRIQUE B14

'''

@transaction.atomic 
def b14(request):
    (message_erreur, redirection) = traitement_post(request.POST, FormAnalyseB14, besoin_validation=True) if request.method == 'POST' else (None, False)    
    if redirection:
        return redirect(REDIRECTION_SUIVANTE[request.path])
    parametres = ParametreZE.objects.all()
    multi = ParametreZE.objects.multi(['source_b14', 
                                       'b14_rp_abs_sani', 
                                       'b14_rp_abs_sani_chauf',
                                       'b14_ff_abs_wc',
                                       'b14_ff_abs_sdb',
                                       'b14_ff_abs_chauf', 
                                       'b14_proprietaire',
                                       'b14_locataire_hors_hlm',
                                       ])
    return render(request, 'b14.html', locals())

class FormAnalyseB14(FormAnalyse):
    
    @property
    def qualite_multi(self):
        if 'selecteur-multi' in self.post:
            return  self.post.getlist('selecteur-multi')
        return None
    
    @property
    def source_multi(self):
        if 'RP' in self.qualite_multi:
            return 'RP'
        elif 'FF' in self.qualite_multi:
            return 'FF'
        elif 'PPPI' in self.qualite_multi:
            return 'PPPI'
        else:
            return None
    
    def categorie_multi(self, categorie):
        return categorie in self.qualite_multi
    
    def categorie_multi_from(self, categories):
        for categorie in categories:
            if categorie in self.qualite_multi:
                return True
        return False
    
    @property
    def qualite_mono(self):
        parametres = {k[14:]: self.post.getlist(k) for k in self.post if k.startswith('selecteur-mono')}
        if len(parametres) == 0:
            return {}
        return parametres
    
    @property
    def source_mono(self):
        r = {}
        for k,v in self.qualite_mono.items():
            if 'RP' in v:
                r[k] = 'RP'
            elif 'FF' in v:
                r[k] = 'FF'
            elif 'PPPI' in v:
                r[k] = 'PPPI'
        return r
    
    def categorie_mono(self, categorie):
        r = []
        for k,v in self.qualite_mono.items():
            if categorie in v:
                r.append(k)
        return r
    
    def categorie_mono_from(self, categories):
        r = []
        for k,v in self.qualite_mono.items():
            for categorie in categories:
                if categorie in v:
                    r.append(k)
                    continue
        return r
    
    def is_valid(self):
        if self.choix_mono_multi('qualite') == 'multi':
            return self._verifier_liste(self.qualite_multi)
        elif self.choix_mono_multi('qualite') == 'mono':
            message_erreur = ''
            for k, v in self.qualite_mono.items():
                success, msg_err = self._verifier_liste(v)
                if msg_err:
                    message_erreur += msg_err + ' pour la zone {0}.\n'.format(k)
            if message_erreur:
                return False, message_erreur
            return True, None
    
    def _verifier_liste(self, liste):
        if len(set(liste) & set(['prop', 'locnonhlm'])) == 0:
            return False, 'Aucune catégorie spécifiée'
        if 'RP' in liste:                
            if len(set(liste) & set(['sani', 'sani_chauf'])) == 0:
                return False, 'Aucun niveau de confort spécifié'
        elif 'FF' in liste:
            if len(set(liste) & set(['wc', 'chauf', 'sdb', 'wc_chauf', 'wc_sdb', 'sdb_chauf', 'wc_sdb_chauf'])) == 0:
                return False, 'Aucun niveau de confort spécifié'
            if len(set(liste) & set(['ss_ent_mv_quali', 'ss_ent', 'tout'])) == 0:
                return False, 'Aucun niveau de qualité du bâti spécifié'
        elif 'PPPI' in liste:
            pass
        else:
            return False, 'Source non spécifiée'
        return True, None        
    
    def modifier_parametres(self):
        if self.choix_mono_multi('qualite') == 'multi':
            ParametreZE.objects.modifier_via_valeur('source_b14', self.source_multi)
            ParametreZE.objects.modifier_via_valeur('b14_proprietaire', self.categorie_multi('prop'))
            ParametreZE.objects.modifier_via_valeur('b14_locataire_hors_hlm', self.categorie_multi('locnonhlm'))
            ParametreZE.objects.modifier_via_valeur('b14_rp_abs_sani', self.categorie_multi('sani'))
            ParametreZE.objects.modifier_via_valeur('b14_rp_abs_sani_chauf', self.categorie_multi('sani_chauf'))
            ParametreZE.objects.modifier_via_valeur('b14_ff_quali_ssent', self.categorie_multi('ss_ent'))
            ParametreZE.objects.modifier_via_valeur('b14_ff_quali_ssent_mv', self.categorie_multi('ss_ent_mv_quali'))
            ParametreZE.objects.modifier_via_valeur('b14_ff_quali_tt', self.categorie_multi('tout'))
            ParametreZE.objects.modifier_via_valeur('b14_ff_abs_wc', self.categorie_multi_from(['wc', 'wc_chauf', 'wc_sdb', 'wc_sdb_chauf']))
            ParametreZE.objects.modifier_via_valeur('b14_ff_abs_chauf', self.categorie_multi_from(['chauf', 'wc_chauf', 'sdb_chauf', 'wc_sdb_chauf']))
            ParametreZE.objects.modifier_via_valeur('b14_ff_abs_sdb', self.categorie_multi_from(['sdb', 'wc_sdb', 'sdb_chauf', 'wc_sdb_chauf']))
        elif self.choix_mono_multi('qualite') == 'mono':
            ParametreZE.objects.modifier_via_dict('source_b14', self.source_mono)
            ParametreZE.objects.modifier_via_liste('b14_proprietaire', self.categorie_mono('prop'))
            ParametreZE.objects.modifier_via_liste('b14_locataire_hors_hlm', self.categorie_mono('locnonhlm'))
            ParametreZE.objects.modifier_via_liste('b14_rp_abs_sani', self.categorie_mono('sani'))
            ParametreZE.objects.modifier_via_liste('b14_rp_abs_sani_chauf', self.categorie_mono('sani_chauf'))
            ParametreZE.objects.modifier_via_liste('b14_ff_quali_ssent', self.categorie_mono('ss_ent'))
            ParametreZE.objects.modifier_via_liste('b14_ff_quali_ssent_mv', self.categorie_mono('ss_ent_mv_quali'))
            ParametreZE.objects.modifier_via_liste('b14_ff_quali_tt', self.categorie_mono('tout'))
            ParametreZE.objects.modifier_via_liste('b14_ff_abs_wc', self.categorie_mono_from(['wc', 'wc_chauf', 'wc_sdb', 'wc_sdb_chauf']))
            ParametreZE.objects.modifier_via_liste('b14_ff_abs_chauf', self.categorie_mono_from(['chauf', 'wc_chauf', 'sdb_chauf', 'wc_sdb_chauf']))
            ParametreZE.objects.modifier_via_liste('b14_ff_abs_sdb', self.categorie_mono_from(['sdb', 'wc_sdb', 'sdb_chauf', 'wc_sdb_chauf']))

'''

BRIQUE B15

'''

@transaction.atomic
def b15(request):
    (message_erreur, redirection) = traitement_post(request.POST, FormAnalyseB15) if request.method == 'POST' else (None, False)    
    if redirection:
        return redirect(REDIRECTION_SUIVANTE[request.path])
    parametres = ParametreZE.objects.all()
    multi_source = ParametreZE.objects.multi(['b15_rp_surp_mod', 'b15_rp_surp_acc', 'b15_filo_surp_mod', 'b15_filo_surp_acc'])
    valeurs_source = [('rp_mod', 'Recensement - suroccupation modérée', 'b15_rp_surp_mod', True),
                      ('rp_acc', 'Recensement - suroccupation accentuée', 'b15_rp_surp_acc', True),
                      ('filo_mod', 'Filocom - suroccupation légère', 'b15_filo_surp_mod', True),
                      ('filo_acc', 'Filocom - suroccupation lourde', 'b15_filo_surp_acc', True),]
    multi_categorie = ParametreZE.objects.multi(['b15_proprietaire', 'b15_locataire_hors_hlm'])
    valeurs_categorie = [('pro', 'Propriétaire', 'b15_proprietaire', True),
                         ('plp', 'Locataires du parc privé', 'b15_locataire_hors_hlm', True),
                         ] 
    return render(request, 'b15.html', locals())
     
       
class FormAnalyseB15(FormAnalyse):
    
    def modifier_parametres(self):
        if self.choix_mono_multi('source') == 'multi':
            ParametreZE.objects.modifier_via_valeur('b15_rp_surp_mod', self.boolean_radio_multi('source', 'rp_mod'))
            ParametreZE.objects.modifier_via_valeur('b15_rp_surp_acc', self.boolean_radio_multi('source', 'rp_acc'))
            ParametreZE.objects.modifier_via_valeur('b15_filo_surp_mod', self.boolean_radio_multi('source', 'filo_mod'))
            ParametreZE.objects.modifier_via_valeur('b15_filo_surp_acc', self.boolean_radio_multi('source', 'filo_acc'))
        elif self.choix_mono_multi('source') == 'mono':
            bool = {'rp_mod':True, 'rp_acc':False, 'filo_mod':False, 'filo_acc':False}
            ParametreZE.objects.modifier_via_dict('b15_rp_surp_mod', self.dictionnaire_boolean_radio_mono('source', bool))
            bool = {'rp_mod':False, 'rp_acc':True, 'filo_mod':False, 'filo_acc':False}
            ParametreZE.objects.modifier_via_dict('b15_rp_surp_acc', self.dictionnaire_boolean_radio_mono('source', bool))
            bool = {'rp_mod':False, 'rp_acc':False, 'filo_mod':True, 'filo_acc':False}
            ParametreZE.objects.modifier_via_dict('b15_filo_surp_mod', self.dictionnaire_boolean_radio_mono('source', bool))
            bool = {'rp_mod':False, 'rp_acc':False, 'filo_mod':False, 'filo_acc':True}
            ParametreZE.objects.modifier_via_dict('b15_filo_surp_acc', self.dictionnaire_boolean_radio_mono('source', bool))
        if self.choix_mono_multi('categorie') == 'multi':
            ParametreZE.objects.modifier_via_valeur('b15_proprietaire', self.boolean_checkbox_multi('categorie', 'pro'))
            ParametreZE.objects.modifier_via_valeur('b15_locataire_hors_hlm', self.boolean_checkbox_multi('categorie', 'plp'))
        if self.choix_mono_multi('categorie') == 'mono':
            ParametreZE.objects.modifier_via_liste('b15_proprietaire', self.liste_checkbox_mono('categorie', 'pro'))
            ParametreZE.objects.modifier_via_liste('b15_locataire_hors_hlm', self.liste_checkbox_mono('categorie', 'plp'))

'''

BRIQUE B16

'''

def b16(request):
    (message_erreur, redirection) = traitement_post(request.POST, FormAnalyseB16) if request.method == 'POST' else (None, False)    
    if redirection:
        return redirect(REDIRECTION_SUIVANTE[request.path])
    parametres = ParametreZE.objects.all()
    return render(request, 'b16.html', locals())
     

class FormAnalyseB16(FormAnalyse):
    pass


'''

BRIQUE B17

'''

@transaction.atomic 
def b17(request):
    (message_erreur, redirection) = traitement_post(request.POST, FormAnalyseB17) if request.method == 'POST' else (None, False)    
    if redirection:
        return redirect(REDIRECTION_SUIVANTE[request.path])
    parametres = ParametreZE.objects.all()
    multi_motif = ParametreZE.objects.multi(['b17_tout_menage', 'b17_hors_prb_env','b17_hors_assist_mat', 'b17_hors_demande_rapprochement', 'b17_hors_trois_motifs'])
    valeurs_motif = [('Aucun', 'Aucun motif à exclure', 'b17_tout_menage', True),
                     ('Environnement',"Problème d'environnement ou de voisinage", 'b17_hors_prb_env', True),
                     ('Assistant',"Assistant(e) maternel(le) ou familial(e)", 'b17_hors_assist_mat', True),
                     ('Rapprochement',"Rapprochement des équipements et des services", 'b17_hors_demande_rapprochement', True),
                     ('Trois',"les 3 motifs", 'b17_hors_trois_motifs', True),
                     ]
    return render(request, 'b17.html', locals())


class FormAnalyseB17(FormAnalyse):
    
    def modifier_parametres(self):
        if self.choix_mono_multi('motif') == 'multi':
            ParametreZE.objects.modifier_via_valeur('b17_tout_menage', self.boolean_radio_multi('motif', 'Aucun'))
            ParametreZE.objects.modifier_via_valeur('b17_hors_prb_env', self.boolean_radio_multi('motif', 'Environnement'))
            ParametreZE.objects.modifier_via_valeur('b17_hors_assist_mat', self.boolean_radio_multi('motif', 'Assistant'))
            ParametreZE.objects.modifier_via_valeur('b17_hors_demande_rapprochement', self.boolean_radio_multi('motif', 'Rapprochement'))
            ParametreZE.objects.modifier_via_valeur('b17_hors_trois_motifs', self.boolean_radio_multi('motif', 'Trois')) 
        elif self.choix_mono_multi('motif') == 'mono':
            bool = {'Aucun':True, 'Environnement':False, 'Assistant':False, 'Rapprochement':False, 'Trois':False}
            ParametreZE.objects.modifier_via_dict('b17_tout_menage', self.dictionnaire_boolean_radio_mono('motif', bool))
            bool = {'Aucun':False, 'Environnement':True, 'Assistant':False, 'Rapprochement':False, 'Trois':False}
            ParametreZE.objects.modifier_via_dict('b17_hors_prb_env', self.dictionnaire_boolean_radio_mono('motif', bool))
            bool = {'Aucun':False, 'Environnement':False, 'Assistant':True, 'Rapprochement':False, 'Trois':False}
            ParametreZE.objects.modifier_via_dict('b17_hors_assist_mat', self.dictionnaire_boolean_radio_mono('motif', bool))
            bool = {'Aucun':False, 'Environnement':False, 'Assistant':False, 'Rapprochement':True, 'Trois':False}
            ParametreZE.objects.modifier_via_dict('b17_hors_demande_rapprochement', self.dictionnaire_boolean_radio_mono('motif', bool))
            bool = {'Aucun':False, 'Environnement':False, 'Assistant':False, 'Rapprochement':False, 'Trois':True}
            ParametreZE.objects.modifier_via_dict('b17_hors_trois_motifs', self.dictionnaire_boolean_radio_mono('motif', bool))

'''

VENTILATION B1

'''

@transaction.atomic
def b1_ventilation(request):

    (message_erreur, redirection) = traitement_post(request.POST, FormAnalyseB1Ventilation) if request.method == 'POST' else (None, False)    
    if redirection:
        return redirect(REDIRECTION_SUIVANTE[request.path])
    '''
    parametres = ParametreZE.objects.all()
    message_erreur = None
    if request.method == 'POST':
        if 'next' in request.POST:
            return redirect(REDIRECTION_SUIVANTE[request.path])
        params = {'ventilation_b12': 'b12_ventilation',
                  'ventilation_b13': 'b13_ventilation',
                  'ventilation_b14': 'b14_ventilation',
                  'ventilation_b15': 'b15_ventilation',
                  'taux_mobilite': 'b1_taux_mobilite',
                  #'taux_rehabilitation':'b14_taux_rehabilitation'
                  }
        for id, param in params.items():
            if id in request.POST:
                valeur = int(request.POST[id])
                if 0 <= valeur <= 100:
                    ParametreZE.objects.modifier_via_valeur(param, valeur)
        if 'save_and_next' in request.POST:
            return redirect(REDIRECTION_SUIVANTE[request.path])
    '''
    parametres = ParametreZE.objects.all()
    multi_b12_ventilation = ParametreZE.objects.multi(['b12_ventilation'])
    parametre_b12_ventilation = 'b12_ventilation'
    multi_b13_ventilation = ParametreZE.objects.multi(['b13_ventilation'])
    parametre_b13_ventilation = 'b13_ventilation'
    multi_b14_ventilation = ParametreZE.objects.multi(['b14_ventilation'])
    parametre_b14_ventilation = 'b14_ventilation'
    multi_b15_ventilation = ParametreZE.objects.multi(['b15_ventilation'])
    parametre_b15_ventilation = 'b15_ventilation'
    multi_b1_taux_mobilite = ParametreZE.objects.multi(['b1_taux_mobilite'])
    parametre_b1_taux_mobilite = 'b1_taux_mobilite'
    return render(request, 'b1_ventilation.html', locals())

class FormAnalyseB1Ventilation(FormAnalyse):
    
    @property
    def part_b12_multi(self):        
        if 'number-part_b12-multi' in self.post:
            return int(self.post['number-part_b12-multi'])
        return None
    
    @property
    def part_b12_mono(self):
        parametres = {k[20:]: int(self.post[k]) for k in self.post if k.startswith('number-part_b12-mono')}
        if len(parametres) == 0:
            return {}
        return parametres
    
    @property
    def part_b13_multi(self):        
        if 'number-part_b13-multi' in self.post:
            return int(self.post['number-part_b13-multi'])
        return None
    
    @property
    def part_b13_mono(self):
        parametres = {k[20:]: int(self.post[k]) for k in self.post if k.startswith('number-part_b13-mono')}
        if len(parametres) == 0:
            return {}
        return parametres
    
    @property
    def part_b14_multi(self):        
        if 'number-part_b14-multi' in self.post:
            return int(self.post['number-part_b14-multi'])
        return None
    
    @property
    def part_b14_mono(self):
        parametres = {k[20:]: int(self.post[k]) for k in self.post if k.startswith('number-part_b14-mono')}
        if len(parametres) == 0:
            return {}
        return parametres
    
    @property
    def part_b15_multi(self):        
        if 'number-part_b15-multi' in self.post:
            return int(self.post['number-part_b15-multi'])
        return None
    
    @property
    def part_b15_mono(self):
        parametres = {k[20:]: int(self.post[k]) for k in self.post if k.startswith('number-part_b15-mono')}
        if len(parametres) == 0:
            return {}
        return parametres
    
    @property
    def realloca_multi(self):        
        if 'number-realloca-multi' in self.post:
            return int(self.post['number-realloca-multi'])
        return None
    
    @property
    def realloca_mono(self):
        parametres = {k[20:]: int(self.post[k]) for k in self.post if k.startswith('number-realloca-mono')}
        if len(parametres) == 0:
            return {}
        return parametres
    
    def modifier_parametres(self):
        if self.choix_mono_multi('part_b12') == 'mono':
            ParametreZE.objects.modifier_via_dict('b12_ventilation', self.part_b12_mono, valeur_pour_code_non_present=100)
        elif self.choix_mono_multi('part_b12') == 'multi':
            ParametreZE.objects.modifier_via_valeur('b12_ventilation', self.part_b12_multi if self.part_b12_multi is not None else 100)
        if self.choix_mono_multi('part_b13') == 'mono':
            ParametreZE.objects.modifier_via_dict('b13_ventilation', self.part_b13_mono, valeur_pour_code_non_present=100)
        elif self.choix_mono_multi('part_b13') == 'multi':
            ParametreZE.objects.modifier_via_valeur('b13_ventilation', self.part_b13_multi if self.part_b13_multi is not None else 100)
        if self.choix_mono_multi('part_b14') == 'mono':
            ParametreZE.objects.modifier_via_dict('b14_ventilation', self.part_b14_mono, valeur_pour_code_non_present=100)
        elif self.choix_mono_multi('part_b14') == 'multi':
            ParametreZE.objects.modifier_via_valeur('b14_ventilation', self.part_b14_multi if self.part_b14_multi is not None else 100)
        if self.choix_mono_multi('part_b15') == 'mono':
            ParametreZE.objects.modifier_via_dict('b15_ventilation', self.part_b15_mono, valeur_pour_code_non_present=100)
        elif self.choix_mono_multi('part_b15') == 'multi':
            ParametreZE.objects.modifier_via_valeur('b15_ventilation', self.part_b15_multi if self.part_b15_multi is not None else 100)
        if self.choix_mono_multi('realloca') == 'mono':
            ParametreZE.objects.modifier_via_dict('b1_taux_mobilite', self.realloca_mono, valeur_pour_code_non_present=50)
        elif self.choix_mono_multi('realloca') == 'multi':
            ParametreZE.objects.modifier_via_valeur('b1_taux_mobilite', self.realloca_multi if self.realloca_multi is not None else 50)             

'''

BRIQUE 2.1 

'''

@transaction.atomic
def b21(request):
    (message_erreur, redirection) = traitement_post(request.POST, FormAnalyseB21, besoin_validation=True) if request.method == 'POST' else (None, False)    
    if redirection:
        return redirect(REDIRECTION_SUIVANTE[request.path])
    parametres = ParametreZE.objects.all()
    valeurs_scenario = [(nom_court, nom_long) for nom_court, nom_long in ParametreZE.SCENARIOS_OMPHALE.items()]
    parametre_scenario = 'b2_scenario_omphale'
    calcul = CalculZE()
    for parametre in parametres:
        resultat = calcul.resultat(parametre.code_ze)
        parametre.evol2008_2014 = resultat.evolution_menage
        parametre.valeurs_scenario = [(valeurs[0], valeurs[1], resultat.evolution_omphale(valeurs[0])) for valeurs in valeurs_scenario]
        # modification des paramètrage des ZE n'ayant pas de scénario Omphale
        if parametre.b2_choix_omphale and (parametre.valeurs_scenario)[0][2] == 0:
            param = ParametreZE.objects.get(code_ze = parametre.code_ze)
            param.b2_choix_omphale = False
            parametre.b2_choix_omphale = False
            param.autre_source_b21 = parametre.evol2008_2014
            parametre.autre_source_b21 = parametre.evol2008_2014
            param.save()
    multi_scenario = ParametreZE.objects.multi(['b2_scenario_omphale', 'b2_choix_omphale', 'autre_source_b21'])
    return render(request, 'b21.html', locals())

class FormAnalyseB21(FormAnalyse):
    
    def is_valid(self):
        '''
        S'assure de la validité des valeurs saisies qui doivent être entières
        '''
        for code, donnee in self.valeurs_autre_scenario.items():
            try:
                d = int(donnee)
            except ValueError:
                return False, 'Donnée saisie incorrecte pour zone ' + code
        return True, None
    
    @property
    def scenario_multi(self):
        if 'scenario-multi' in self.post:
            return str(self.post['scenario-multi'])
        return None
    
    @property
    def scenario_mono(self):
        parametres = {k[13:]: str(v) for k, v in self.post.items() if k.startswith('scenario-mono')}
        if len(parametres) == 0:
            return {}
        return parametres
    
    @property
    def choix_scenario(self):
        parametres = [k[22:] for k,v in self.post.items() if k.startswith('choix-scenario-omphale') and v == 'oui']
        if len(parametres) == 0:
            return []
        return parametres
    
    @property
    def valeurs_autre_scenario(self):
        parametres = {}
        codes_autre_valeur = [k[22:] for k,v in self.post.items() if k.startswith('choix-scenario-omphale') and v == 'non']
        for code in codes_autre_valeur:
            if 'number-scenario-mono' + code in self.post:
                parametres[code] = self.post['number-scenario-mono' + code]
        return parametres
        
    
    def modifier_parametres(self):
        if self.choix_mono_multi('scenario') == 'multi':
            ParametreZE.objects.modifier_via_valeur('b2_scenario_omphale', self.scenario_multi)
            ParametreZE.objects.modifier_via_valeur('b2_choix_omphale', True)
            ParametreZE.objects.modifier_via_valeur('autre_valeur_b21', 0)
        elif self.choix_mono_multi('scenario') == 'mono':
            ParametreZE.objects.modifier_via_liste('b2_choix_omphale', self.choix_scenario)
            ParametreZE.objects.modifier_via_dict('b2_scenario_omphale', self.scenario_mono)
            ParametreZE.objects.modifier_via_dict('autre_source_b21', {k:int(v) for k,v in self.valeurs_autre_scenario.items()}, valeur_pour_code_non_present=int(0))

'''

BRIQUE 2.2

'''

@transaction.atomic
def b22(request):
    (message_erreur, redirection) = traitement_post(request.POST, FormAnalyseB22) if request.method == 'POST' else (None, False)    
    if redirection:
        return redirect(REDIRECTION_SUIVANTE[request.path])
    multi_restructuration = ParametreZE.objects.multi(['b2_tx_restructuration'])
    parametre_restructuration = 'b2_tx_restructuration'
    parametre_restructuration_info = 'restructuration_info'
    multi_disparition = ParametreZE.objects.multi(['b2_tx_disparition'])
    parametre_disparition = 'b2_tx_disparition'
    parametre_disparition_info = 'disparition_info'
    multi_vacance = ParametreZE.objects.multi(['b2_tx_vacance'])
    parametre_vacance = 'b2_tx_vacance'
    parametre_vacance_info = 'vacance_info'
    multi_residence_secondaire = ParametreZE.objects.multi(['b2_tx_residence_secondaire'])
    parametre_residence_secondaire = 'b2_tx_residence_secondaire'
    parametre_residence_secondaire_info = 'residence_secondaire_info'
    parametres = ParametreZE.objects.all()
    calcul = CalculZE()
    for parametre in parametres:
        resultat = calcul.resultat(parametre.code_ze)
        parametre.restructuration = round(resultat.taux_restructuration_actuel * 100, 2)
        parametre.disparition = round(resultat.taux_disparition_actuel * 100, 2)
        parametre.vacance = round(resultat.taux_vacance_actuel * 100, 2)
        parametre.residence_secondaire = round(resultat.taux_residence_secondaire_actuel * 100, 2)
        parametre.restructuration_info = [round(resultat.taux_restructuration_actuel_ls * 100, 2),
                                          round(resultat.taux_restructuration_actuel_lp * 100, 2),
                                          resultat.nb_log_restructuration_ls,
                                          resultat.nb_log_restructuration_lp]
        parametre.disparition_info = [round(resultat.taux_disparition_actuel_ls * 100, 2),
                                      round(resultat.taux_disparition_actuel_lp * 100, 2),
                                      resultat.nb_log_disparition_ls,
                                      resultat.nb_log_disparition_lp]                                      
        parametre.vacance_info = [round(resultat.taux_vacance_actuel_ls * 100, 2),
                                  round(resultat.taux_vacance_actuel_lp * 100, 2),
                                  resultat.nb_log_vacance_ls,
                                  resultat.nb_log_vacance_lp]
        parametre.residence_secondaire_info = [round(resultat.taux_residence_secondaire_actuel_ls * 100, 2),
                                               round(resultat.taux_residence_secondaire_actuel_lp * 100, 2),
                                               resultat.nb_log_residence_secondaire_ls,
                                               resultat.nb_log_residence_secondaire_lp]
    return render(request, 'b22.html', locals())

class FormAnalyseB22(FormAnalyse):
    
    def valeur_multi(self, type):
        if 'check-{0}-multi'.format(type) in self.post:
            return 9999
        else:
            return float(self.post['number-{0}-multi'.format(type)])
    
    def dictionnaire_mono(self, type):
        print(self.post)
        r = {}
        codes_ze = [k[12 + len(type):] for k, v in self.post.items() if k.startswith('number-{0}-mono'.format(type)) or k.startswith('hidden-{0}-mono'.format(type))] 
        for code in codes_ze:
            r[code] = 9999 if 'check-{0}-mono{1}'.format(type, code) in self.post.keys() else self.post['number-{0}-mono{1}'.format(type, code)]
        return r
    
    def modifier_parametres(self):
        if self.choix_mono_multi('restructuration') == 'multi':            
            ParametreZE.objects.modifier_via_valeur('b2_tx_restructuration', self.valeur_multi('restructuration'))
        elif self.choix_mono_multi('restructuration') == 'mono':
            ParametreZE.objects.modifier_via_dict('b2_tx_restructuration', self.dictionnaire_mono('restructuration'))
        if self.choix_mono_multi('disparition') == 'multi':            
            ParametreZE.objects.modifier_via_valeur('b2_tx_disparition', self.valeur_multi('disparition'))
        elif self.choix_mono_multi('disparition') == 'mono':
            ParametreZE.objects.modifier_via_dict('b2_tx_disparition', self.dictionnaire_mono('disparition'))
        if self.choix_mono_multi('vacance') == 'multi':            
            ParametreZE.objects.modifier_via_valeur('b2_tx_vacance', self.valeur_multi('vacance'))
        elif self.choix_mono_multi('vacance') == 'mono':
            ParametreZE.objects.modifier_via_dict('b2_tx_vacance', self.dictionnaire_mono('vacance'))
        if self.choix_mono_multi('residence_secondaire') == 'multi':            
            ParametreZE.objects.modifier_via_valeur('b2_tx_residence_secondaire', self.valeur_multi('residence_secondaire'))
        elif self.choix_mono_multi('residence_secondaire') == 'mono':
            ParametreZE.objects.modifier_via_dict('b2_tx_residence_secondaire', self.dictionnaire_mono('residence_secondaire'))

'''

RESORPTION BESOIN

'''

@transaction.atomic
def b_resorption(request):
    message_erreur = None
    if request.method == 'POST':
        if 'next' in request.POST:
            return redirect(REDIRECTION_SUIVANTE[request.path])
        if 'horizon' in request.POST:
            valeur = int(request.POST['horizon'])
            if 0 <= valeur <= 40:
                ParametreZE.objects.modifier_via_valeur('horizon_resorption', valeur)
        if 'save_and_next' in request.POST:
            return redirect(REDIRECTION_SUIVANTE[request.path])
    parametres = ParametreZE.objects.all()
    return render(request, 'b_resorption.html', locals()) 


'''

VOLET C

'''

@transaction.atomic
def c_classe_commune(request):
    parametres = ParametreZE.objects.all()
    codes_zone = ParametreZE.objects.codes_zone
    affichage_communes = False
    if request.method == 'POST':
        code_zone = request.POST['zone_emploi'] if 'zone_emploi' in request.POST else request.session['tmp_code_ze']
        if 'save_all' in request.POST:
            classes_commune = {k[6:]: int(v) for k, v in request.POST.items() if k.startswith('classe')}
            epcis_commune = {k[4:]: v for k, v in request.POST.items() if k.startswith('epci')}
            Commune.objects.modifier_classes(classes_commune)
            Commune.objects.modifier_epcis(epcis_commune)
        if code_zone != '0000':
            request.session['tmp_code_ze'] = code_zone
            communes_ze = Commune.objects.filter(code_ze = code_zone).order_by('code_epci', 'nom')
            epcis = Commune.objects.filter(code_ze__in=codes_zone).values('code_epci', 'nom_epci').distinct().order_by('code_epci')
            affichage_communes = True            
    return render(request, 'c_commune.html', locals())           
                        