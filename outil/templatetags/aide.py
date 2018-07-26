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

from django import template

register = template.Library()

@register.filter
def aide(url):
    if url=='/tpl/b11':
        return '/static/Guide_methodologique.pdf#page=19'
    elif url=='/tpl/b12':
        return '/static/Guide_methodologique.pdf#page=26'
    elif url=='/tpl/b13':
        return '/static/Guide_methodologique.pdf#page=29'
    elif url=='/tpl/b14':
        return '/static/Guide_methodologique.pdf#page=35'
    elif url=='/tpl/b15':
        return '/static/Guide_methodologique.pdf#page=38'
    elif url=='/tpl/b16':
        return '/static/Guide_methodologique.pdf#page=41'
    elif url=='/tpl/b17':
        return '/static/Guide_methodologique.pdf#page=45'
    elif url=='/tpl/b1-ventilation':
        return '/static/Guide_methodologique.pdf#page=51'
    elif url=='/tpl/b21':
        return '/static/Guide_methodologique.pdf#page=55'
    elif url=='/tpl/b22':
        return '/static/Guide_methodologique.pdf#page=62'
    elif url=='/tpl/c_classe_commune':
        return '/static/Guide_methodologique.pdf#page=76'
    elif url == 'classes-commune':
        return '/static/Guide_methodologique.pdf#page=86'
    elif url == 'etab-finess':
        return '/static/Annexes_guide_methodologique.pdf#page=6'
    else:
        return '/static/Guide_methodologique.pdf'