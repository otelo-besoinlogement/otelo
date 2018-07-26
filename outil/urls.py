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

from django.conf.urls import url

from .views import configuration
from .views import resultat

urlpatterns = [
    url(r'^accueil$', configuration.accueil, name='accueil'),
    url(r'^init$', configuration.initialisation, name='initialisation'),
    url(r'^init_classe$', configuration.initialisation_classe, name='initialisation_classe'),
    url(r'^init_commune$', configuration.initialisation_commune, name='initialisation_commune'),
    url(r'^save$', configuration.sauvegarde, name='sauvegarde'),
    url(r'^load$', configuration.chargement_config, name='chargement'),
    url(r'^b11$', configuration.b11, name='brique_1_1'),
    url(r'^b12$', configuration.b12, name='brique_1_2'),
    url(r'^b13$', configuration.b13, name='brique_1_3'),
    url(r'^b14$', configuration.b14, name='brique_1_4'),
    url(r'^b15$', configuration.b15, name='brique_1_5'),
    url(r'^b16$', configuration.b16, name='brique_1_6'),
    url(r'^b17$', configuration.b17, name='brique_1_7'),
    url(r'^b1-ventilation$', configuration.b1_ventilation, name='voletB1_ventilation'),
    url(r'^b21$', configuration.b21, name='brique_2_1'),
    url(r'^b22$', configuration.b22, name='brique_2_2'),
    url(r'^b_resorption$', configuration.b_resorption, name='voletB_resorption'),
    url(r'^c_classe_commune$', configuration.c_classe_commune, name='classe_commune'),
    url(r'^synthese_ze$', resultat.synthese_zone_emploi, name='synthese_ze'),    
    url(r'^resultat_par_ze$', resultat.resultat_par_ze, name='resultat_par_ze'),
    url(r'^export_ze$', resultat.export_ze, name='export_ze'), 
    url(r'^synthese_epci$', resultat.synthese_epci, name='synthese_epci'),
    url(r'^resultat_par_epci$', resultat.resultat_par_epci, name='resultat_par_epci'),
    url(r'^export_epci$', resultat.export_epci, name='export_epci'),      
]