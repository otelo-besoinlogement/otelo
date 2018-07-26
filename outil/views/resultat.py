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

import csv
from django.http import HttpResponse
from django.shortcuts import render
from outil.models import ParametreZE
from outil.models import Commune
from outil.calcul.calculs_ze import CalculZE
from outil.calcul.calculs_epci import CalculEPCI

def synthese_zone_emploi(request):
    parametres = ParametreZE.objects.all()
    if 'codes_zone_synthese' in request.session:
        codes_zone = request.session['codes_zone_synthese']
    else:
        codes_zone = ParametreZE.objects.codes_zone
    affichage_resultat = False
    if request.method == 'POST':
        codes_zone = [code for code in request.POST.getlist('zone_emploi') if code != '0000']
        if len(codes_zone) > 0:
            #try:
            resultats = CalculZE().resultats(codes_zone)
            request.session['codes_zone_synthese'] = codes_zone
            affichage_resultat = True
            #except Exception as e:
            #    print(e)    
    return render(request, 'resultat_synthese_ze.html', locals())

def resultat_par_ze(request):
    parametres = ParametreZE.objects.all()
    affichage_resultat = False
    if request.method == 'POST':
        code_zone = request.POST['zone_emploi']
        if code_zone != '0000':            
            try:
                resultat = CalculZE().resultat(code_zone)
                affichage_resultat = True
                dp_positive = True if resultat.demande_potentielle >= 0 else False
                decomposition_dp_positive = True if (resultat.menages_suppl >= 0 and resultat.besoin_en_renouvellement>=0 and resultat.evolution_logements_vacants >= 0 and resultat.evolution_residences_secondaires >= 0) else False   
            except Exception as e:
                print(e)
    return render(request, 'resultat_par_ze.html', locals())

def export_ze(request):
    parametres = ParametreZE.objects.all()
    if 'codes_zone_synthese' in request.session:
        codes_zone = request.session['codes_zone_synthese']
    else:
        codes_zone = ParametreZE.objects.codes_zone
    if request.method == 'POST':
        codes_zone = [code for code in request.POST.getlist('zone_emploi') if code != '0000']
        if len(codes_zone) > 0:
            try:
                resultats = CalculZE().resultats(codes_zone)
                request.session['codes_zone_synthese'] = codes_zone
                nom_fichier = 'export_ze.csv'
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachement; filename="{0}"'.format(nom_fichier)
                writer = csv.writer(response, delimiter=';')
                writer.writerow(['Code Zone Emploi', 
                                 'Nom Zone Emploi',
                                 'B. Besoins totaux en production de logements (1 an)',
                                 'Réhabilitation (1 an)',                                 
                                 'B1. LS (1 an)',
                                 'B1. LL (1 an)',
                                 'Total B1 (1 an)',
                                 'Part du B1 dans le total B',
                                 'B2. LS (1 an)',
                                 'B2. LL (1 an)',
                                 'Total B2 (1 an)',
                                 'Part du B2 dans le total B',
                                 'Besoins en LS (1 an)',
                                 'Part des besoins en LS',
                                 'Besoins en LL(1 an)',
                                 'Parc Filocom 2015',
                                 'B1. Besoins en stock après réallocation (1 an) rapporté au parc total',
                                 'B2. Besoins en flux (1 an) rapporté au parc total',
                                 'B. Besoins totaux en production de logements (1 an) rapporté au parc total',
                                 'Parc social RPLS 2015',
                                 'Besoins en LS rapportés au parc social (1 an)',
                                 'Parc non social',
                                 'Besoins en LL rapportés au parc non social (1 an)',
                                 'Total 1.1',
                                 'Total 1.2',
                                 'Total 1.3',
                                 'Total 1.4',
                                 'Total 1.5',
                                 'Total 1.7',
                                 'Besoin issu du renouvellement du parc 2015-2021',
                                 "Besoin issu de l'évolution RP 2015-2021",
                                 "Besoin issu de l'évolution RS 2015-2021",
                                 "Besoin issu de l'évolution LV 2015-2021",                       
                                 ])
                for resultat in resultats:
                    writer.writerow([resultat.code_zone, 
                                     resultat.nom_zone, 
                                     resultat.total_besoin_1an,
                                     resultat.total_besoin_rehabilitation_1an,                                     
                                     resultat.total_besoin_stock_ls_1an,
                                     resultat.total_besoin_stock_ll_1an,
                                     resultat.total_besoin_en_stock_apres_reallocation_1an,
                                     str(resultat.part_besoin_stock_apres_reallocation).replace('.', ','),
                                     resultat.demande_potentielle_ls_1an,
                                     resultat.demande_potentielle_ll_1an,
                                     resultat.demande_potentielle_1an,
                                     str(resultat.part_demande_potentielle).replace('.', ','),
                                     resultat.total_besoin_ls_1an,
                                     str(resultat.part_besoin_ls).replace('.', ','),
                                     resultat.total_besoin_ll_1an,
                                     resultat.parc_total_filo,
                                     str(resultat.part_besoin_stock_apres_reallocation_sur_parc_total_1an).replace('.', ','),                           
                                     str(resultat.part_demande_potentielle_sur_parc_total_1an).replace('.', ','),
                                     str(round(resultat.besoin_rapporte_au_parc_total_1an*100, 2)).replace('.', ','),
                                     resultat.parc_social_rpls,
                                     str(resultat.part_besoin_ls_sur_parc_social).replace('.', ','),
                                     resultat.parc_non_social,
                                     str(resultat.part_besoin_ll_sur_parc_non_social).replace('.', ','),
                                     resultat.total_b11,
                                     resultat.total_b12,
                                     resultat.total_b13_corrige,
                                     resultat.total_b14,
                                     resultat.total_b15_corrige,
                                     resultat.total_b17,
                                     -resultat.renouvellement,
                                     resultat.menages_residence_principale_supplementaire,
                                     resultat.evolution_residences_secondaires,
                                     resultat.evolution_logements_vacants,
                                     ])
                return response
            except Exception as e:
                print(e)    
    return render(request, 'resultat_export_ze.html', locals())

                          
def synthese_epci(request):
    calcul_epci = CalculEPCI(ParametreZE.objects.codes_zone)
    epcis = calcul_epci.epcis
    if 'codes_epci_synthese' in request.session:
        codes_epci = request.session['codes_epci_synthese']
    else:
        codes_epci = [epci['code_epci'] for epci in epcis]
    affichage_resultat = False
    if request.method == 'POST':
        codes_epci = [code for code in request.POST.getlist('epci') if code != '0000']
        if len(codes_epci) > 0:
            try:
                resultats = calcul_epci.resultats(codes_epci)
                request.session['codes_epci_synthese'] = codes_epci
                affichage_resultat = True
            except Exception as e:
                print(e)    
    return render(request, 'resultat_synthese_epci.html', locals())

def resultat_par_epci(request):
    calcul_epci = CalculEPCI(ParametreZE.objects.codes_zone)
    epcis = calcul_epci.epcis 
    affichage_resultat = False
    if request.method == 'POST':
        code_epci = request.POST['epci']
        if code_epci != '0000':
            communes = calcul_epci.communes(code_epci)
            resultat = calcul_epci.resultat(code_epci)
            affichage_resultat = True
    return render(request, 'resultat_par_epci.html', locals())

def export_epci(request):
    calcul_epci = CalculEPCI(ParametreZE.objects.codes_zone)
    epcis = calcul_epci.epcis
    if 'codes_epci_synthese' in request.session:
        codes_epci = request.session['codes_epci_synthese']
    else:
        codes_epci = [epci['code_epci'] for epci in epcis]
    affichage_resultat = False
    if request.method == 'POST':
        codes_epci = [code for code in request.POST.getlist('epci') if code != '0000']
        if len(codes_epci) > 0:
            try:
                resultats = calcul_epci.resultats(codes_epci)
                request.session['codes_epci_synthese'] = codes_epci
                nom_fichier = 'export_epci.csv'
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachement; filename="{0}"'.format(nom_fichier)
                writer = csv.writer(response, delimiter=';')
                writer.writerow(['Code EPCI 2017', 
                                'Nom EPCI 2017', 
                                'Départements',                               
                                'Besoin en logement naïf (6 ans)',
                                'Besoin en logement après corrections (1 an)',
                                'Besoin en logement après corrections (6 ans)',
                                ])
                for resultat in resultats:
                    writer.writerow([resultat.code_epci, 
                                     resultat.nom_epci,
                                     resultat.departements,
                                     resultat.besoin_en_logement_naif_final,
                                     resultat.besoin_en_logement_final_1an,
                                     resultat.besoin_en_logement_final,
                                     ])
                return response 
            except Exception as e:
                print(e)    
    return render(request, 'resultat_export_epci.html', locals())
