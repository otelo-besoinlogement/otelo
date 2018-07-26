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
def pourcentage(valeur):
    return "{:.2%}".format(valeur)

@register.filter
def positif(valeur):
    return valeur if valeur >= 0 else 0 

@register.filter
def valabs(valeur):
    return valeur if valeur >= 0 else (-1) * valeur

@register.filter
def somme(objets, parametre):
    try:
        return sum([int(objet.__getattribute__(parametre)) for objet in objets])
    except Exception as e:
        return e

@register.filter
def somme_float(objets, parametre):
    try:
        return sum([float(objet.__getattribute__(parametre)) for objet in objets])
    except Exception as e:
        return e
    
@register.filter
def ratio(objets, parametres):
    try:
        parametre, parametre2 = parametres.split('/')
        nominateur = sum([int(objet.__getattribute__(parametre)) for objet in objets])
        denominateur = sum([int(objet.__getattribute__(parametre2)) for objet in objets])
        return nominateur/denominateur
    except Exception as e:
        return e  