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

from outil.initialisation.params import PACK
from outil.initialisation.params import FICHIER_PROJECTION_B2
from outil.initialisation.charger_data import ZEDatas
from outil.models import ParametreZE

class CalculZE:
    
    '''
    
    Gestionnaire des résultats pour l'ensemble des ZE
    
    '''
    
    def __init__(self):
        '''
        Constructeur
        
        Charge les données ZE des pack dans l'attribut datas (dans un objet ZEDatas)
        '''
        self.datas = ZEDatas()
        self.datas.importer_pack_donnees(PACK, FICHIER_PROJECTION_B2)
    
    def resultats(self, codes_zone):
        '''
        Renvoie la liste des resultats pour tous les codes ZE demandés avec les résultats inter-ZE
        '''
        resultats = []
        for code in ParametreZE.objects.codes_zone:
            parametres_zone = ParametreZE.objects.get(code_ze=code)
            resultats.append(ResultatZE(self.datas.zones[code], parametres_zone))
        # Ajout pour chaque resultat des résultats inter-ZE correspondant
        resultat_inter_ze = ResultatInterZE(resultats)
        for resultat in resultats:
            resultat.part_parc_total = resultat_inter_ze.part_parc_total(resultat.code_zone)
            resultat.part_besoin_stock_apres_reallocation_sur_ensemble_ze = resultat_inter_ze.part_besoin_stock_apres_reallocation(resultat.code_zone)
            resultat.part_besoin_stock_apres_reallocation_selection = resultat_inter_ze.part_besoin_stock_apres_reallocation_selection(resultat.code_zone, codes_zone)
            resultat.part_besoin_flux_sur_ensemble_ze = resultat_inter_ze.part_besoin_en_flux(resultat.code_zone)
            resultat.part_besoin_flux_selection = resultat_inter_ze.part_besoin_en_flux_selection(resultat.code_zone, codes_zone)
        return [resultat for resultat in resultats if resultat.parametres.code_ze in codes_zone]
        
    def resultat(self, code_zone):
        '''
        Renvoie les resultats de la ZE sans résultats inter-ZE
        '''
        parametres_zone = ParametreZE.objects.get(code_ze=code_zone)
        resultat = ResultatZE(self.datas.zones[code_zone], parametres_zone)
        return resultat    


class ResultatInterZE:
    
    def __init__(self, resultats_ze):
        self.resultats_ze = resultats_ze
        
    def resultat(self, code_zone):
        for r in self.resultats_ze:
            if r.code_zone == code_zone:
                return r
        return None

    @property
    def parc_total_filo(self):
        return sum([r.parc_total_filo for r in self.resultats_ze])
   
    @property
    def total_besoin_en_stock_apres_reallocation_6ans(self):
        return sum([r.total_besoin_en_stock_apres_reallocation_6ans for r in self.resultats_ze])
    
    def total_besoin_en_stock_apres_reallocation_6ans_selection(self, codes_zone):
        return sum([r.total_besoin_en_stock_apres_reallocation_6ans for r in self.resultats_ze if r.code_zone in codes_zone])
    
    @property
    def total_besoin_en_flux_6ans(self):
        return sum([r.demande_potentielle for r in self.resultats_ze])
    
    def total_besoin_en_flux_6ans_selection(self, codes_zone):
        return sum([r.demande_potentielle for r in self.resultats_ze if r.code_zone in codes_zone])
    
    def part_parc_total(self, code_zone):
        parc_total_ze = self.resultat(code_zone).parc_total_filo
        return parc_total_ze / self.parc_total_filo
    
    def part_besoin_stock_apres_reallocation(self, code_zone):
        besoin_stock_ze = self.resultat(code_zone).total_besoin_en_stock_apres_reallocation_6ans
        if self.total_besoin_en_stock_apres_reallocation_6ans == 0:
            return 0
        return besoin_stock_ze / self.total_besoin_en_stock_apres_reallocation_6ans
    
    def part_besoin_stock_apres_reallocation_selection(self, code_zone, codes_zone):
        besoin_stock_ze = self.resultat(code_zone).total_besoin_en_stock_apres_reallocation_6ans
        if self.total_besoin_en_stock_apres_reallocation_6ans_selection(codes_zone) == 0:
            return 0
        return besoin_stock_ze / self.total_besoin_en_stock_apres_reallocation_6ans_selection(codes_zone)
    
    def part_besoin_en_flux(self, code_zone):
        besoin_stock_ze = self.resultat(code_zone).demande_potentielle
        if self.total_besoin_en_flux_6ans == 0:
            return 0
        return besoin_stock_ze / self.total_besoin_en_flux_6ans
    
    def part_besoin_en_flux_selection(self, code_zone, codes_zone):
        besoin_stock_ze = self.resultat(code_zone).demande_potentielle
        if self.total_besoin_en_flux_6ans_selection(codes_zone) == 0:
            return 0
        return besoin_stock_ze / self.total_besoin_en_flux_6ans_selection(codes_zone)


class ResultatZE:
    
    def __init__(self, data, parametres):
        self.data = data
        self.parametres = parametres
    
    @property
    def code_zone(self):
        return self.parametres.code_ze
    
    @property
    def nom_zone(self):
        return self.parametres.nom_ze
    
    @property
    def parc_total_filo(self):
        return round(self.data.b1_synthese['parc_filo15'])
    
    @property
    def parc_social_rpls(self):
        return round(self.data.b1_synthese['parc_social_2015'])
    
    @property
    def parc_non_social(self):
        return self.parc_total_filo - self.parc_social_rpls
    
    @property
    def parc_2021(self):
        return self.parc_total_filo + self.demande_potentielle
    
    @property
    def nb_rs_2021(self):
        d = self.data
        parc_residence_secondaire = d.projection_filo['Parc TOTAL Modeocc 2015 [RS]']
        return round(parc_residence_secondaire + self.evolution_residences_secondaires)
    
    @property
    def nb_lv_2021(self):
        d = self.data
        parc_logement_vacant = d.projection_filo['Parc TOTAL Modeocc 2015 [VA]']
        return round(parc_logement_vacant + self.evolution_logements_vacants)        
    
    @property
    def total_besoin_6ans(self):
        resultat = self.total_besoin_en_stock_apres_reallocation_6ans + self.demande_potentielle
        return resultat
    
    @property
    def total_besoin_1an(self):
        return round(self.total_besoin_6ans/6)
    
    @property
    def total_besoin_ls_6ans(self):
        return self.total_besoin_stock_ls_6ans + self.demande_potentielle_ls
    
    @property
    def total_besoin_ls_1an(self):
        return self.total_besoin_stock_ls_1an + self.demande_potentielle_ls_1an
        
    @property
    def part_besoin_ls(self):
        if self.total_besoin_1an == 0:
            return 0
        return round(self.total_besoin_ls_1an * 100/ self.total_besoin_1an, 2)
    
    @property
    def part_besoin_ls_sur_parc_social(self):
        return round(self.total_besoin_ls_1an * 100/self.parc_social_rpls, 2)
    
    @property
    def part_besoin_ls_sur_parc_social_6ans(self):
        return round(self.total_besoin_ls_6ans * 100/self.parc_social_rpls, 2)
    
    @property
    def total_besoin_ll_6ans(self):
        return self.total_besoin_stock_ll_6ans + self.demande_potentielle_ll
            
    @property
    def total_besoin_ll_1an(self):
        return self.total_besoin_stock_ll_1an + self.demande_potentielle_ll_1an
    
    @property
    def part_besoin_ll(self):
        if self.total_besoin_1an == 0:
            return 0
        return round(self.total_besoin_ll_1an * 100/self.total_besoin_1an, 2)
        
    @property
    def part_besoin_ll_sur_parc_non_social(self):
        return round(self.total_besoin_ll_1an * 100/self.parc_non_social, 2)
    
    @property
    def part_besoin_ll_sur_parc_non_social_6ans(self):
        return round(self.total_besoin_ll_6ans * 100/self.parc_non_social, 2)
               
    @property
    def besoin_rapporte_au_parc_total_6ans(self):
        return self.total_besoin_6ans / self.parc_total_filo
    
    @property
    def besoin_rapporte_au_parc_total_1an(self):
        return self.total_besoin_1an / self.parc_total_filo
    
    """
    
    VOLET B1
    
    """

    @property
    def total_besoin_en_stock(self):
        resultat = self.total_b11 + self.total_b12 + self.total_b13_corrige + self.total_b14 + self.total_b15_corrige + self.total_b17
        return resultat
    
    @property
    def total_besoin_en_stock_apres_reallocation(self):
        p = self.parametres
        resultat = self.total_besoin_en_stock - p.b1_taux_mobilite/100 * self.total_besoin_inadequation
        return resultat
    
    @property
    def total_besoin_en_stock_6ans(self):
        p = self.parametres
        resultat = self.total_besoin_en_stock * 6 / p.horizon_resorption
        return round(resultat)
    
    @property
    def total_besoin_en_stock_1an(self):
        p = self.parametres
        resultat = self.total_besoin_en_stock / p.horizon_resorption
        return round(resultat)
    
    @property
    def total_besoin_en_stock_apres_reallocation_6ans(self):
        p = self.parametres
        resultat = self.total_besoin_en_stock_apres_reallocation * 6 / p.horizon_resorption
        return round(resultat)
    
    @property
    def part_besoin_stock_apres_reallocation(self):
        if self.total_besoin_6ans == 0:
            return 0
        return round(self.total_besoin_en_stock_apres_reallocation_6ans * 100/self.total_besoin_6ans, 2)
    
    @property
    def part_besoin_stock_apres_reallocation_sur_parc_total_1an(self):
        return round(self.total_besoin_en_stock_apres_reallocation_1an * 100/self.parc_total_filo, 2)
    
    @property
    def part_besoin_stock_apres_reallocation_sur_parc_total_6ans(self):
        return round(self.total_besoin_en_stock_apres_reallocation_6ans * 100/self.parc_total_filo, 2)
    
    @property
    def part_besoin_stock_ls_sur_besoin_en_stock_apres_reallocation(self):
        if self.total_besoin_en_stock_apres_reallocation == 0:
            return 0
        return round(self.total_besoin_stock_ls * 100 /self.total_besoin_en_stock_apres_reallocation, 2)
        
    @property
    def total_besoin_en_stock_apres_reallocation_1an(self):
        p = self.parametres
        resultat = self.total_besoin_en_stock_apres_reallocation / p.horizon_resorption
        return round(resultat)
    
    @property
    def total_reallocation_6ans(self):
        return round(self.total_besoin_en_stock_6ans - self.total_besoin_en_stock_apres_reallocation_6ans)
    
    '''     
    @property
    def total_besoin_en_stock_hors_ll(self):
        return self.total_besoin_en_stock - self.total_besoin_stock_ll
    
    @property
    def total_besoin_en_stock_hors_ll_6ans(self):
        p = self.parametres
        resultat = self.total_besoin_en_stock_hors_ll * 6 / p.horizon_resorption
        return round(resultat)
    '''
    
    @property
    def total_besoin_stock_ls(self):
        p = self.parametres
        resultat = self.total_b11 + self.total_b12 * (p.b12_ventilation/100) + self.total_b13_corrige * (p.b13_ventilation/100) + self.total_b14 * (p.b14_ventilation/100) + self.total_b15_corrige * (p.b15_ventilation/100) + self.total_b17
        return round(resultat)
    
    @property
    def total_besoin_stock_ls_6ans(self):
        p = self.parametres
        resultat = self.total_besoin_stock_ls * 6 / p.horizon_resorption
        return round(resultat)
    
    @property
    def total_besoin_stock_ls_1an(self):
        p = self.parametres
        resultat = self.total_besoin_stock_ls / p.horizon_resorption
        return round(resultat)
    
    @property
    def total_besoin_stock_ll(self):
        p = self.parametres
        resultat = (100-p.b12_ventilation)/100 * self.total_b12 + (100-p.b13_ventilation)/100 *  self.total_b13_corrige + (100-p.b14_ventilation)/100 * self.total_b14 + (100-p.b15_ventilation)/100 * self.total_b15_corrige - p.b1_taux_mobilite/100 * self.total_besoin_inadequation
        return round(resultat)
    
    @property
    def total_besoin_stock_ll_6ans(self):
        p = self.parametres
        resultat = self.total_besoin_stock_ll * 6 / p.horizon_resorption
        return round(resultat)
    
    @property
    def total_besoin_stock_ll_1an(self):
        p = self.parametres
        resultat = self.total_besoin_stock_ll / p.horizon_resorption
        return round(resultat)
    
    @property
    def total_besoin_inadequation(self):
        return self.total_b13_corrige + self.total_b15_corrige
    
    @property
    def total_b11(self):
        CATEGORIES = {
            '1' : 'Aire Station Nomades',
            '2' : 'Autre Ctre.Accueil',
            '3' : 'C.A.D.A.',
            '4' : 'C.H.R.S.',
            '5' : 'C.P.H.',
            '6' : 'Foyer Jeunes Trav.',
            '7' : 'Foyer Trav. Migrants',
            '8' : 'Héberg.Fam.Malades',
            '9' : 'Log.Foyer non Spéc.',
            'A' : 'Maisons Relais-Pens.',
            'B' : 'Autre Résidence Soc', #'B' : 'Resid.Soc. hors MRel',
        }
        p = self.parametres
        d = self.data        
        resultat = 0
        if p.source_b11 == 'RP':
            if p.b11_sa:
                resultat += d.b11_sa_rp
            if p.b11_fortune:
                resultat += d.b11_fortune_rp
            if p.b11_hotel:
                resultat += d.b12_hotel_rp
        elif p.source_b11 == 'SNE':
            if p.b11_sa:
                resultat += d.b11_sa_sne
            if p.b11_fortune:
                resultat += d.b11_fortune_sne_camping + d.b11_fortune_sne_squat
            if p.b11_hotel:
                resultat += d.b12_hotel_sne
        if p.b11_autre:
            resultat += p.autre_source_b11
        for num_categorie in CATEGORIES:
            if num_categorie in p.b11_etablissement:
                for k in d.b11_hebergement[CATEGORIES[num_categorie]]:
                    resultat += p.b11_part_etablissement/100 * d.b11_hebergement[CATEGORIES[num_categorie]][k]
        return round(resultat)
    
    @property
    def total_b11_1an(self):
        p = self.parametres
        resultat = self.total_b11 / p.horizon_resorption
        return round(resultat)
        
    @property
    def total_b11_6ans(self):
        p = self.parametres
        resultat = self.total_b11 * 6 / p.horizon_resorption
        return round(resultat)
    
    @property
    def total_b12(self):
        p = self.parametres
        d = self.data        
        resultat = 0
        if p.b12_cohab_interg_subie:
            resultat += d.b12_heberges_filo
        if p.b12_heberg_particulier:
            resultat += d.b12_heberges_sne_particulier
        if p.b12_heberg_gratuit:
            resultat += d.b12_heberges_sne_gratuit
        if p.b12_heberg_temporaire:
            resultat += d.b12_heberges_sne_temporaire
        if p.b12_heberg_autre:
            resultat += p.autre_source_b12
        return round(resultat)
    
    @property
    def total_b12_1an(self):
        p = self.parametres
        resultat = self.total_b12 / p.horizon_resorption
        return round(resultat)
        
    @property
    def total_b12_6ans(self):
        p = self.parametres
        resultat = self.total_b12 * 6 / p.horizon_resorption
        return round(resultat)
    
    @property
    def total_b12_ls(self):
        p = self.parametres
        resultat = self.total_b12 * (p.b12_ventilation/100)
        return round(resultat)
    
    @property
    def total_b12_ll(self):
        resultat = self.total_b12 - self.total_b12_ls
        return round(resultat)

    @property
    def total_b13_corrige(self):
        p = self.parametres
        correction_stock_13 = -1 * p.ratio_4_3 * self.total_b14
        resultat = round(self.total_b13 + correction_stock_13)
        return resultat if resultat > 0 else 0
    
    @property
    def total_b13_corrige_1an(self):
        p = self.parametres
        resultat = self.total_b13_corrige / p.horizon_resorption
        return round(resultat)
        
    @property
    def total_b13_corrige_6ans(self):
        p = self.parametres
        resultat = self.total_b13_corrige * 6 / p.horizon_resorption
        return round(resultat)
    
    @property
    def total_b13_corrige_apres_reallocation_6ans(self):
        p = self.parametres
        resultat = (self.total_b13_corrige * (1 - p.b1_taux_mobilite/100)) * 6 / p.horizon_resorption
        return round(resultat)
    
    @property
    def total_b13(self):
        p = self.parametres
        d = self.data        
        resultat = 0
        taux = str(p.b13_taux_effort)
        if p.b13_acc:
            resultat += d.b13_inadequation_financiere['nb_all_plus{0}_Acc'.format(taux)]
        if p.b13_plp:
            resultat += d.b13_inadequation_financiere['nb_all_plus{0}_PLP'.format(taux)]
        #if p.b13_pls:
        #    resultat += d.b13_inadequation_financiere['nb_all_plus{0}_PLS'.format(taux)]
        return round(resultat)
    
    @property
    def total_b13_ls(self):
        p = self.parametres
        resultat = self.total_b13_corrige * (p.b13_ventilation/100)
        return round(resultat)
    
    @property
    def total_b13_ll(self):
        p = self.parametres
        resultat = self.total_b13_corrige * ((100 - p.b13_ventilation)/100)
        return round(resultat)
        
    @property
    def total_b14(self):
        p = self.parametres
        d = self.data        
        resultat = 0
        if p.b14_proprietaire:
            if p.source_b14 == "RP":
                if p.b14_rp_abs_sani:
                    resultat += d.b14_mauvaise_qualite_rp['sani_ppT']
                elif p.b14_rp_abs_sani_chauf:
                    resultat += d.b14_mauvaise_qualite_rp['sani_chfl_ppT']                
            elif p.source_b14 == "FF":
                variable = 'pp_ss_'
                if p.b14_ff_quali_ssent:
                    variable += 'ent_'
                elif p.b14_ff_quali_ssent_mv:
                    variable += 'quali_ent_'
                if p.b14_ff_abs_wc and p.b14_ff_abs_chauf and p.b14_ff_abs_sdb:
                    variable += '3elts_'
                else:
                    if p.b14_ff_abs_wc:
                        variable += 'wc_'
                    if p.b14_ff_abs_sdb:
                        variable += 'sdb_'
                    if p.b14_ff_abs_chauf:
                        variable += 'chauff_'
                variable += 'ppt'
                resultat += d.b14_mauvaise_qualite_ff[variable]
            elif p.source_b14 == "PPPI":
                resultat += d.b14_mauvaise_qualite_filo['pppi_po']
            # on exclut, pour les logements occupés par le proprio la part de réhabilitation 
            resultat = resultat * (100 - p.b14_taux_rehabilitation)/100 
        if p.b14_locataire_hors_hlm:
            if p.source_b14 == "RP":
                if p.b14_rp_abs_sani:
                    resultat += d.b14_mauvaise_qualite_rp['sani_loc_nonHLM']
                elif p.b14_rp_abs_sani_chauf:
                    resultat += d.b14_mauvaise_qualite_rp['sani_chfl_loc_nonHLM']                
            elif p.source_b14 == "FF":
                variable = 'pp_ss_'
                if p.b14_ff_quali_ssent:
                    variable += 'ent_'
                elif p.b14_ff_quali_ssent_mv:
                    variable += 'quali_ent_'
                if p.b14_ff_abs_wc and p.b14_ff_abs_chauf and p.b14_ff_abs_sdb:
                    variable += '3elts_'
                else:
                    if p.b14_ff_abs_wc:
                        variable += 'wc_'
                    if p.b14_ff_abs_sdb:
                        variable += 'sdb_'
                    if p.b14_ff_abs_chauf:
                        variable += 'chauff_'
                variable += 'loc'
                resultat += d.b14_mauvaise_qualite_ff[variable]
            elif p.source_b14 == "PPPI":
                resultat += d.b14_mauvaise_qualite_filo['pppi_lp']
        """
        if p.b14_locataire_hlm:
            if p.source_b14 == "RP":
                if p.b14_rp_abs_sani:
                    resultat += d.b14_mauvaise_qualite_rp['sani_loc_HLM']
                elif p.b14_rp_abs_sani_chauf:
                    resultat += d.b14_mauvaise_qualite_rp['sani_chfl_loc_HLM']
            elif p.source_b14 == "FF":
                variable = 'pHLM_ss_'
                if p.b14_ff_quali_ssent:
                    variable += 'ent_'
                elif p.b14_ff_quali_ssent_mv:
                    variable += 'quali_ent_'
                if p.b14_ff_abs_wc and p.b14_ff_abs_chauf and p.b14_ff_abs_sdb:
                    variable += '3elts_'
                else:
                    if p.b14_ff_abs_wc:
                        variable += 'wc_'
                    if p.b14_ff_abs_sdb:
                        variable += 'sdb_'
                    if p.b14_ff_abs_chauf:
                        variable += 'chauff_'
                variable += 'ppt'
                resultat += d.b14_mauvaise_qualite_ff[variable]
            elif p.source_b14 == "PPPI":
                resultat += d.b14_mauvaise_qualite_filo['pppi_lh']
        """
        return round(resultat)
    
    @property
    def total_b14_1an(self):
        p = self.parametres
        resultat = self.total_b14 / p.horizon_resorption
        return round(resultat)
        
    @property
    def total_b14_6ans(self):
        p = self.parametres
        resultat = self.total_b14 * 6 / p.horizon_resorption
        return round(resultat)
    
    @property
    def total_b14_ls(self):
        p = self.parametres
        resultat = self.total_b14 * (p.b14_ventilation/100)
        return round(resultat)
    
    @property
    def total_b14_ll(self):
        resultat = self.total_b14 - self.total_b14_ls
        return round(resultat)
    
    @property
    def total_besoin_rehabilitation(self): 
        p = self.parametres
        d = self.data        
        resultat = 0
        if p.source_b14 == "RP":
            if p.b14_rp_abs_sani:
                resultat += d.b14_mauvaise_qualite_rp['sani_ppT']
            elif p.b14_rp_abs_sani_chauf:
                resultat += d.b14_mauvaise_qualite_rp['sani_chfl_ppT']                
        elif p.source_b14 == "FF":
            variable = 'pp_ss_'
            if p.b14_ff_quali_ssent:
                variable += 'ent_'
            elif p.b14_ff_quali_ssent_mv:
                variable += 'quali_ent_'
            if p.b14_ff_abs_wc and p.b14_ff_abs_chauf and p.b14_ff_abs_sdb:
                variable += '3elts_'
            else:
                if p.b14_ff_abs_wc:
                    variable += 'wc_'
                if p.b14_ff_abs_sdb:
                    variable += 'sdb_'
                if p.b14_ff_abs_chauf:
                    variable += 'chauff_'
            variable += 'ppt'
            resultat += d.b14_mauvaise_qualite_ff[variable]
        elif p.source_b14 == "PPPI":
            resultat += d.b14_mauvaise_qualite_filo['pppi_po']
        resultat = resultat * (p.b14_taux_rehabilitation/100)
        return round(resultat)
    
    @property
    def total_besoin_rehabilitation_6ans(self):
        p = self.parametres
        resultat = self.total_besoin_rehabilitation * 6 / p.horizon_resorption
        return round(resultat)
    
    @property
    def total_besoin_rehabilitation_1an(self):
        p = self.parametres
        resultat = self.total_besoin_rehabilitation / p.horizon_resorption
        return round(resultat)
    
    @property
    def part_besoin_rehabilitation_sur_besoin_complementaire(self):
        if self.besoins_complementaires_6ans == 0:
            return 0
        return round(self.total_besoin_rehabilitation_6ans * 100 / self.besoins_complementaires_6ans, 2)
    
    @property
    def total_b15_corrige(self):
        p = self.parametres
        correction_stock_15 = -1 * p.ratio_2_5 * self.total_b12 - p.ratio_3_5 * self.total_b13 - p.ratio_4_5 * self.total_b14
        resultat = round(self.total_b15 + correction_stock_15)
        return resultat if resultat > 0 else 0
    
    @property
    def total_b15_corrige_1an(self):
        p = self.parametres
        resultat = self.total_b15_corrige / p.horizon_resorption
        return round(resultat)
        
    @property
    def total_b15_corrige_6ans(self):
        p = self.parametres
        resultat = self.total_b15_corrige * 6 / p.horizon_resorption
        return round(resultat)
    
    @property
    def total_b15_corrige_apres_reallocation_6ans(self):
        p = self.parametres
        resultat = (self.total_b15_corrige * (1 - p.b1_taux_mobilite/100)) * 6 / p.horizon_resorption
        return round(resultat)
    
    @property
    def total_b15(self):
        p = self.parametres
        d = self.data        
        resultat = 0
        if p.b15_proprietaire:
            if p.b15_rp_surp_mod:
                resultat += d.b15_suroccup_rp['nb_men_mod_ppT']
            elif p.b15_rp_surp_acc:
                resultat += d.b15_suroccup_rp['nb_men_acc_ppT']
            elif p.b15_filo_surp_mod:
                resultat += d.b15_suroccup_filo['surocc_leg_po']
            elif p.b15_filo_surp_acc:
                resultat += d.b15_suroccup_filo['surocc_lourde_po']
        if p.b15_locataire_hors_hlm:
            if p.b15_rp_surp_mod:
                resultat += d.b15_suroccup_rp['nb_men_mod_loc_nonHLM']
            elif p.b15_rp_surp_acc:
                resultat += d.b15_suroccup_rp['nb_men_acc_loc_nonHLM']
            elif p.b15_filo_surp_mod:
                resultat += d.b15_suroccup_filo['surocc_leg_lp']
            elif p.b15_filo_surp_acc:
                resultat += d.b15_suroccup_filo['surocc_lourde_lp']
        """
        if p.b15_locataire_hlm:
            if p.b15_rp_surp_mod:
                resultat += d.b15_suroccup_rp['nb_men_mod_loc_HLM']
            elif p.b15_rp_surp_acc:
                resultat += d.b15_suroccup_rp['nb_men_acc_loc_HLM']
            elif p.b15_filo_surp_mod:
                resultat += d.b15_suroccup_filo['surocc_leg_lh']
            elif p.b15_filo_surp_acc:
                resultat += d.b15_suroccup_filo['surocc_lourde_lh']
        """
        return round(resultat)
    
    @property
    def total_b15_ls(self):
        p = self.parametres
        resultat = self.total_b15_corrige * (p.b15_ventilation/100)
        return round(resultat)
    
    @property
    def total_b15_ll(self):
        resultat = self.total_b15_corrige - self.total_b15_ls
        return round(resultat)
    
    @property
    def total_b16(self):
        p = self.parametres
        correction_stock_13 = -1 * p.ratio_4_3 * self.total_b14
        correction_stock_15 = -1 * p.ratio_2_5 * self.total_b12 - p.ratio_3_5 * self.total_b13 - p.ratio_4_5 * self.total_b14
        return round(correction_stock_13 + correction_stock_15)
    
    @property
    def total_b17(self):
        p = self.parametres
        d = self.data        
        resultat = 0
        if p.b17_tout_menage:
            resultat = d.b17_parc_social['crea']
        elif p.b17_hors_prb_env:
            resultat = d.b17_parc_social['crea_voisin']
        elif p.b17_hors_assist_mat:
            resultat = d.b17_parc_social['crea_mater']
        elif p.b17_hors_demande_rapprochement:
            resultat = d.b17_parc_social['crea_services']
        elif p.b17_hors_trois_motifs:
            resultat = d.b17_parc_social['crea_motifs']
        return round(resultat)
    
    @property
    def total_b17_1an(self):
        p = self.parametres
        resultat = self.total_b17 / p.horizon_resorption
        return round(resultat)
        
    @property
    def total_b17_6ans(self):
        p = self.parametres
        resultat = self.total_b17 * 6 / p.horizon_resorption
        return round(resultat)
    
    @property
    def part_b11(self):
        if self.total_besoin_en_stock_6ans == 0:
            return 0
        return round(self.total_b11_6ans * 100 / self.total_besoin_en_stock_6ans, 2)
    
    @property
    def part_b12(self):
        if self.total_besoin_en_stock_6ans == 0:
            return 0
        return round(self.total_b12_6ans * 100 / self.total_besoin_en_stock_6ans, 2) 
    
    @property
    def part_b13_corrige(self):
        if self.total_besoin_en_stock_6ans == 0:
            return 0
        return round(self.total_b13_corrige_6ans * 100 / self.total_besoin_en_stock_6ans, 2) 
    
    @property
    def part_b14(self):
        if self.total_besoin_en_stock_6ans == 0:
            return 0
        return round(self.total_b14 * 100 / self.total_besoin_en_stock_6ans, 2) 
    
    @property
    def part_b15_corrige(self):
        if self.total_besoin_en_stock_6ans == 0:
            return 0
        return round(self.total_b15_corrige * 100 / self.total_besoin_en_stock_6ans, 2)
    
    @property
    def part_b17(self):
        if self.total_besoin_en_stock_6ans == 0:
            return 0
        return round(self.total_b17 * 100 / self.total_besoin_en_stock_6ans, 2) 
    
    '''
    
    VOLET B2
    
    '''
   
    @property
    def evolution_menage(self):
        d = self.data
        parc_residence_princ_2014 = d.b1_synthese['nb_men14']
        parc_residence_princ_2008 = d.b1_synthese['nb_men08']
        return round(parc_residence_princ_2014 - parc_residence_princ_2008)
    
    def evolution_omphale(self, scenario):
        d = self.data
        variable = 'menages_{0}_' + scenario.lower()
        menages_2015 = d.menages_omphale[variable.format('2015')]
        menages_2021 = d.menages_omphale[variable.format('2021')]
        return round(menages_2021 - menages_2015)
   
    @property
    def menages_suppl(self):
        p = self.parametres
        d = self.data
        if p.b2_choix_omphale:
            variable = 'menages_{0}_' + p.b2_scenario_omphale.lower()
            menages_2015 = d.menages_omphale[variable.format('2015')]
            menages_2021 = d.menages_omphale[variable.format('2021')]
            return round(menages_2021 - menages_2015)
        else:
            return round(p.autre_source_b21)
    
    @property
    def menages_suppl_1an(self):
        return round(self.menages_suppl/6)
    
    @property
    def part_menages_suppl_sur_besoin_flux(self):
        if self.demande_potentielle == 0:
            return 0
        return round(self.menages_suppl * 100/self.demande_potentielle, 2)
    
    @property
    def demande_potentielle(self):
        p = self.parametres
        d = self.data        
        parc_total = self.parc_total_filo
        calcul = ((parc_total * self.taux_residence_principale_actuel + self.menages_suppl)/self.taux_residence_principale) - (parc_total + self.renouvellement) 
        return round(calcul)
    
    @property
    def part_demande_potentielle(self):
        if self.total_besoin_6ans == 0:
            return 0
        return round(self.demande_potentielle * 100 / self.total_besoin_6ans, 2)
    
    @property
    def part_demande_potentielle_sur_parc_total_1an(self):
        return round(self.demande_potentielle_1an * 100/ self.parc_total_filo, 2)
    
    @property
    def part_demande_potentielle_sur_parc_total_6ans(self):
        return round(self.demande_potentielle * 100/ self.parc_total_filo, 2)
        
    @property
    def demande_potentielle_ls(self):
        return round(self.part_ls_cible * self.demande_potentielle)
    
    @property
    def demande_potentielle_ll(self):
        return round(self.part_ll_cible * self.demande_potentielle)
    
    @property
    def demande_potentielle_1an(self):
        return round(self.demande_potentielle/6)
    
    @property
    def demande_potentielle_ls_1an(self):
        return round(self.demande_potentielle_ls/6)
    
    @property
    def demande_potentielle_ll_1an(self):
        return round(self.demande_potentielle_ll/6)
    
    @property
    def part_demande_potentielle_ls_sur_demande_potentielle(self):
        if self.demande_potentielle == 0:
            return 0
        return round(self.demande_potentielle_ls*100/self.demande_potentielle, 2)
    
    @property
    def part_ls_cible(self):
        return (self.parc_social_rpls + self.total_besoin_stock_ls)/(self.parc_total_filo + self.total_besoin_stock_ls + self.total_besoin_stock_ll)
    
    @property
    def part_ll_cible(self):
        return 1 - self.part_ls_cible
    
    @property
    def menages_residence_principale_supplementaire(self):
        return round(self.menages_suppl)
       
    @property
    def menages_logement_vacant_supplementaire(self):
        resultat = self.taux_vacance * (self.menages_residence_principale_supplementaire)/(1-self.taux_vacance-self.taux_residence_secondaire)
        return round(resultat)
    
    @property
    def menages_logement_vacant_supplementaire_1an(self):
        return round(self.menages_logement_vacant_supplementaire/6)
    
    @property
    def evolution_logements_vacants(self):
        evolution = self.taux_vacance * (self.parc_total_filo + self.renouvellement + self.demande_potentielle) - self.taux_vacance_actuel * self.parc_total_filo
        return round(evolution)
    
    @property
    def evolution_logements_vacants_1an(self):
        return round(self.evolution_logements_vacants/6)
    
    @property
    def part_logement_vacant_sur_besoin_flux(self):
        if self.demande_potentielle == 0:
            return 0
        return round(self.menages_logement_vacant_supplementaire * 100 / self.demande_potentielle, 2)
    
    @property
    def part_logement_vacant_sur_besoin_complementaire(self):
        if self.besoins_complementaires_6ans == 0:
            return 0
        return round(self.besoin_logements_vacants * 100 / self.besoins_complementaires_6ans, 2)
    
    @property
    def menages_residence_secondaire_supplementaire(self):
        d = self.data
        resultat = self.taux_residence_secondaire * (self.menages_residence_principale_supplementaire)/(1-self.taux_vacance-self.taux_residence_secondaire)
        return round(resultat)
    
    @property
    def menages_residence_secondaire_supplementaire_1an(self):
        return round(self.menages_residence_secondaire_supplementaire/6)
    
    @property
    def evolution_residences_secondaires(self):
        evolution = self.taux_residence_secondaire * (self.parc_total_filo + self.renouvellement + self.demande_potentielle) - self.taux_residence_secondaire_actuel * self.parc_total_filo
        return round(evolution)
    
    @property
    def evolution_residences_secondaires_1an(self):
        return round(self.evolution_residences_secondaires/6)
    
    @property
    def part_residence_secondaire_sur_besoin_flux(self):
        if self.demande_potentielle == 0:
            return 0
        return round(self.menages_residence_secondaire_supplementaire * 100 / self.demande_potentielle, 2)
    
    @property
    def part_residence_secondaire_sur_besoin_complementaire(self):
        if self.besoins_complementaires_6ans == 0:
            return 0
        return round(self.besoin_residences_secondaires * 100 / self.besoins_complementaires_6ans, 2)
    
    @property
    def taux_restructuration(self):
        p = self.parametres
        if p.b2_tx_restructuration == 9999:
            return self.taux_restructuration_actuel
        else:
            return p.b2_tx_restructuration / 100.0
    
    @property
    def taux_restructuration_actuel(self):
        d = self.data
        parc_restructure = d.projection_filo['Parc TOTAL Restructurés [09-15]']
        parc_total =  d.projection_filo['Parc TOTAL Modeoc 2009 Total']
        if parc_restructure == '[01:10]' or parc_restructure == 's':
            parc_restructure = 5 
        return parc_restructure/parc_total
    
    @property
    def taux_restructuration_actuel_ls(self):
        d = self.data
        parc_restructure = d.projection_filo['HLM-SEM Restructurés [09-15]']
        parc_total = d.projection_filo['HLM-SEM Modeoc 2009 Total']
        if parc_restructure == '[01:10]' or parc_restructure == 's':
            parc_restructure = 5        
        return parc_restructure/parc_total
    
    @property
    def taux_restructuration_actuel_lp(self):
        d = self.data
        parc_restructure = d.projection_filo['Parc privé Restructurés [09-15]']
        parc_total = d.projection_filo['Parc privé Modeoc 2009 Total']
        if parc_restructure == '[01:10]' or parc_restructure == 's':
            parc_restructure = 5        
        return parc_restructure/parc_total
    
    @property
    def nb_log_restructuration_ls(self):
        d = self.data
        parc_restructure = d.projection_filo['HLM-SEM Restructurés [09-15]']
        if parc_restructure == '[01:10]' or parc_restructure == 's':
            parc_restructure = 5        
        return round(parc_restructure)
    
    @property
    def nb_log_restructuration_lp(self):
        d = self.data
        parc_restructure = d.projection_filo['Parc privé Restructurés [09-15]']
        if parc_restructure == '[01:10]' or parc_restructure == 's':
            parc_restructure = 5        
        return round(parc_restructure)
    
    @property
    def taux_disparition(self):
        p = self.parametres
        d = self.data
        if p.b2_tx_disparition == 9999:
            return self.taux_disparition_actuel
        else:
            return p.b2_tx_disparition / 100.0
    
    @property
    def taux_disparition_actuel(self):
        d = self.data
        parc_disparu = d.projection_filo['Parc TOTAL Disparition [09-15]']
        parc_total =  d.projection_filo['Parc TOTAL Modeoc 2009 Total']
        if parc_disparu == '[01:10]' or parc_disparu == 's':
            parc_disparu = 5
        return parc_disparu/parc_total
    
    @property
    def taux_disparition_actuel_ls(self):
        d = self.data
        parc_disparu = d.projection_filo['HLM-SEM Disparition [09-15]']
        parc_total = d.projection_filo['HLM-SEM Modeoc 2009 Total']
        if parc_disparu == '[01:10]' or parc_disparu == 's':
            parc_disparu = 5        
        return parc_disparu/parc_total
    
    @property
    def taux_disparition_actuel_lp(self):
        d = self.data
        parc_disparu = d.projection_filo['Parc privé Disparition [09-15]']
        parc_total = d.projection_filo['Parc privé Modeoc 2009 Total']
        if parc_disparu == '[01:10]' or parc_disparu == 's':
            parc_disparu = 5        
        return parc_disparu/parc_total
    
    @property
    def nb_log_disparition_ls(self):
        d = self.data
        parc_disparu = d.projection_filo['HLM-SEM Disparition [09-15]']
        if parc_disparu == '[01:10]' or parc_disparu == 's':
            parc_disparu = 5        
        return round(parc_disparu)
    
    @property
    def nb_log_disparition_lp(self):
        d = self.data
        parc_disparu = d.projection_filo['Parc privé Disparition [09-15]']
        if parc_disparu == '[01:10]' or parc_disparu == 's':
            parc_disparu = 5        
        return round(parc_disparu)
    
    @property
    def renouvellement(self):
        d = self.data
        parc_total = self.parc_total_filo
        return round((self.taux_restructuration - self.taux_disparition) * parc_total)
    
    @property
    def besoin_en_renouvellement(self):        
        return -self.renouvellement
    
    @property
    def besoin_en_renouvellement_1an(self):        
        return round(self.besoin_en_renouvellement/6)
    
    @property
    def part_renouvellement_sur_besoin_flux(self):
        if self.demande_potentielle == 0:
            return 0
        return round(self.besoin_en_renouvellement * 100/self.demande_potentielle, 2)
    
    @property
    def taux_vacance(self):
        p = self.parametres        
        if p.b2_tx_vacance == 9999:
            return self.taux_vacance_actuel
        else:
            return p.b2_tx_vacance / 100
    
    @property
    def taux_vacance_actuel(self):
        d = self.data
        parc_vacant = d.projection_filo['Parc TOTAL Modeocc 2015 [VA]']
        parc_total = d.projection_filo['Parc TOTAL Modeoc 2015 Total']
        if parc_vacant == '[01:10]' or parc_vacant == 's':
            parc_vacant = 5
        return parc_vacant/parc_total
    
    @property
    def taux_vacance_actuel_ls(self):
        d = self.data
        parc_vacant = d.projection_filo['HLM-SEM Modeocc 2015 [VA]']
        parc_total = d.projection_filo['HLM-SEM Modeoc 2015 Total']
        if parc_vacant == '[01:10]' or parc_vacant == 's':
            parc_vacant = 5        
        return parc_vacant/parc_total
    
    @property
    def taux_vacance_actuel_lp(self):
        d = self.data
        parc_vacant = d.projection_filo['Parc privé Modeocc 2015 [VA]']
        parc_total = d.projection_filo['Parc privé Modeoc 2015 Total']
        if parc_vacant == '[01:10]' or parc_vacant == 's':
            parc_vacant = 5        
        return parc_vacant/parc_total
    
    @property
    def nb_log_vacance_ls(self):
        d = self.data
        parc_vacant = d.projection_filo['HLM-SEM Modeocc 2015 [VA]']
        if parc_vacant == '[01:10]' or parc_vacant == 's':
            parc_vacant = 5        
        return round(parc_vacant)
    
    @property
    def nb_log_vacance_lp(self):
        d = self.data
        parc_vacant = d.projection_filo['Parc privé Modeocc 2015 [VA]']
        if parc_vacant == '[01:10]' or parc_vacant == 's':
            parc_vacant = 5        
        return round(parc_vacant)
    
    @property
    def taux_residence_secondaire(self):
        p = self.parametres
        if p.b2_tx_residence_secondaire == 9999:
            return self.taux_residence_secondaire_actuel
        else:
            return p.b2_tx_residence_secondaire / 100
    
    @property
    def taux_residence_secondaire_actuel(self):
        d = self.data
        parc_residence_secondaire = d.projection_filo['Parc TOTAL Modeocc 2015 [RS]']
        parc_total = d.projection_filo['Parc TOTAL Modeoc 2015 Total']
        return parc_residence_secondaire/parc_total
    
    @property
    def taux_residence_secondaire_actuel_ls(self):
        d = self.data
        parc_residence_secondaire = d.projection_filo['HLM-SEM Modeocc 2015 [RS]']
        parc_total = d.projection_filo['HLM-SEM Modeoc 2015 Total']
        if parc_residence_secondaire == '[01:10]' or parc_residence_secondaire == 's':
            parc_residence_secondaire = 5        
        return parc_residence_secondaire/parc_total
    
    @property
    def taux_residence_secondaire_actuel_lp(self):
        d = self.data
        parc_residence_secondaire = d.projection_filo['Parc privé Modeocc 2015 [RS]']
        parc_total = d.projection_filo['Parc privé Modeoc 2015 Total']
        if parc_residence_secondaire == '[01:10]' or parc_residence_secondaire == 's':
            parc_residence_secondaire = 5        
        return parc_residence_secondaire/parc_total
    
    @property
    def nb_log_residence_secondaire_ls(self):
        d = self.data
        parc_residence_secondaire = d.projection_filo['HLM-SEM Modeocc 2015 [RS]']
        if parc_residence_secondaire == '[01:10]' or parc_residence_secondaire == 's':
            parc_residence_secondaire = 5        
        return round(parc_residence_secondaire)
    
    @property
    def nb_log_residence_secondaire_lp(self):
        d = self.data
        parc_residence_secondaire = d.projection_filo['Parc privé Modeocc 2015 [RS]']
        if parc_residence_secondaire == '[01:10]' or parc_residence_secondaire == 's':
            parc_residence_secondaire = 5        
        return round(parc_residence_secondaire)
    
    @property
    def taux_residence_principale(self):
        return 1 - self.taux_residence_secondaire - self.taux_vacance
    
    @property
    def taux_residence_principale_actuel(self):
        return 1 - self.taux_residence_secondaire_actuel - self.taux_vacance_actuel
    
    @property
    def besoins_complementaires_6ans(self):
        return self.total_besoin_rehabilitation_6ans + self.besoin_logements_vacants + self.besoin_residences_secondaires
    
    @property
    def besoins_complementaires_1an(self):
        return self.total_besoin_rehabilitation_1an + self.besoin_logements_vacants_1an + self.besoin_residences_secondaires_1an    
    

class Parametres():
    '''
    Classe qui reproduit les mêmes attributs que la classe ParametreZE du Model de l'application outil
    '''
    
    def __init__(self, code, nom):
        self.code_ze = code
        self.nom_ze = nom
        self.b11_sa = True
        self.b11_fortune = True
        self.b11_hotel = True
        self.b11_autre = False
        self.source_b11 = 'RP'
        self.autre_source_b11 = 0
        self.b12_cohab_interg_subie = True
        self.b12_heberg_particulier = True
        self.b12_heberg_gratuit = True
        self.b12_heberg_temporaire = True
        self.b12_heberg_autre = False
        self.autre_source_b12 = 0
        self.b13_taux_effort = 30
        self.b14_rp_abs_sani = True
        self.b14_rp_abs_sani_chauf = False
        self.b14_rp_abs_sani_ou_chauf = False
        self.b14_proprietaire = False
        self.b14_locataire_hors_hlm = True
        self.b14_locataire_hlm = False
        self.b15_rp_surp_mod = False
        self.b15_rp_surp_acc = True
        self.b15_filo_surp_mod = False
        self.b15_filo_surp_acc = False
        self.b15_proprietaire = False
        self.b15_locataire_hors_hlm = True
        self.b15_locataire_hlm = False
        self.b17_tout_menage = True
        self.b17_hors_prb_env = False
        self.b17_hors_assist_mat = False
        self.b17_hors_demande_rapprochement = False
        self.b17_hors_trois_motifs = False
        self.b2_tx_restructuration = 9999
        self.b2_tx_disparition = 9999
        self.b2_tx_vacance = 9999
        self.b2_tx_residence_secondaire = 9999
        self.b2_scenario_omphale = 'CENTRAL'
        self.horizon_resorption = 20