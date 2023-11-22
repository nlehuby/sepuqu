#!/usr/bin/env python
# coding: utf-8

import json
import csv
import datetime


millesime = None
with open("metadata.txt") as metadata_file:
    line = metadata_file.readline()
    millesime = datetime.datetime.strptime(line[0:10], '%Y-%m-%d').strftime('%m/%Y')

with open('services-publics.json') as json_file:
    data = json.load(json_file)

def parse_opening_hours(txt):
    if txt is None:
        return None
    osm_days = {"Lundi": "Mo", "Mardi": "Tu", "Mercredi":"We", "Jeudi": "Th", "Vendredi":"Fr", "Samedi":"Sa", "Dimanche":"Su", "jours_feries": "PH"}

    opening_hours = ""
    for plage in txt:
        if not plage["nom_jour_fin"] or not plage["nom_jour_debut"]:
            return
        if not plage["valeur_heure_debut_1"] or not plage["valeur_heure_fin_1"]:
            return              
        opening_hours += osm_days[plage["nom_jour_debut"]]
        if plage["nom_jour_debut"] != plage["nom_jour_fin"]:
            opening_hours += "-{}".format(osm_days[plage["nom_jour_fin"]])
        opening_hours += " "

        opening_hours += "{}-{}".format(plage['valeur_heure_debut_1'][0:5], plage['valeur_heure_fin_1'][0:5])
        if plage['valeur_heure_debut_2']:
            opening_hours += ",{}-{}".format(plage['valeur_heure_debut_2'][0:5], plage['valeur_heure_fin_2'][0:5])        
        opening_hours += "; "
    return(opening_hours[:-2])


def _retreat_name(official_name):
    zz = official_name.split(" - ")
    if len(zz)==1:
        return
    city_name = zz[1]
    
    if city_name.startswith("A"):
        return official_name.replace(" - ", " d'")
    if city_name.startswith("E"):
        return official_name.replace(" - ", " d'")
    if city_name.startswith("I"):
        return official_name.replace(" - ", " d'")
    if city_name.startswith("O"):
        return official_name.replace(" - ", " d'")
    if city_name.startswith("U"):
        return official_name.replace(" - ", " d'")
    if city_name.startswith("É"):
        return official_name.replace(" - ", " d'")
    if city_name.startswith("È"):
        return official_name.replace(" - ", " d'")
    if city_name.startswith("Ê"):
        return official_name.replace(" - ", " d'")
    if city_name.startswith("Î"):
        return official_name.replace(" - ", " d'")
    if city_name.startswith("Le "):
        return official_name.replace(" - Le ", " du ")   
    if city_name.startswith("Les "):
        return official_name.replace(" - Les ", " des ")    
    if city_name.startswith("H"):
        return official_name.replace(" - ", " d'")          
    return official_name.replace(" - ", " de ")


export = []

wheelchair_mapping = {
    "ACC": "yes",
    "DEM": "limited",
    "NAC": "no",
    "": None
}

def retreat_sous_prefecture_name(official_name):
    name = _retreat_name(official_name)
    if name:
        return name.replace("préfecture","Préfecture")
    return

def retreat_townhall_name(official_name):
    return _retreat_name(official_name)

def retreat_prison_name(official_name):
    if not official_name.startswith("Etablissement"):
        return
    return "É" + official_name[1:]

def retreat_CPAM_name(official_name):
    return official_name.replace("Caisse primaire d'assurance maladie (CPAM)", "CPAM").split(" - ")[0]

def retreat_Caf_name(official_name):
    return official_name.replace("Caisse d'allocations familiales (Caf)", "Caf").split(" - ")[0]

def retreat_PMI_name(official_name):
    return official_name.replace("Centre de protection maternelle et infantile (PMI)", "PMI").split(" - ")[0]

def retreat_CIO_name(official_name):
    return official_name.replace("Centre d’information et d’orientation (CIO)", "CIO").replace("Centre d'information et d'orientation (CIO)","CIO").split(" - ")[0]

def retreat_Mission_Locale_name(official_name):
    return official_name.replace("Mission locale pour l'insertion professionnelle et sociale des jeunes (16-25 ans)", "Mission locale").split(" - ")[0]

def retreat_Pole_Emploi_name(official_name):
    return "Pôle Emploi", official_name.replace("Pôle emploi - ", "")

def retreat_France_Services_name(official_name):
    return "France Services", official_name.replace("France Services - ", "")

def retreat_Urssaf_name(official_name):
    if not official_name.startswith("Urssaf"):
        return
    return official_name.split(" - ")[0]

for feature in data["service"]:
    elem = {}
    if not feature.get("pivot"):
        continue
    elem["categorie"] = feature["pivot"][0]["type_service_local"]
    elem["official_name"] = feature["nom"]
    elem['branch'] = None
    if elem["categorie"] in ["mairie", "mairie_com"]:
        elem["name"] = retreat_townhall_name(feature["nom"])
    elif elem["categorie"] in ["esm"]:
        elem["name"] = retreat_prison_name(feature["nom"])            
    elif elem["categorie"] in ["sous_pref"]:
        elem["name"] = retreat_sous_prefecture_name(feature["nom"])      
    elif elem["categorie"] in ["cpam"]:
        elem["name"] = retreat_CPAM_name(feature["nom"]) 
    elif elem["categorie"] in ["caf"]:
        elem["name"] = retreat_Caf_name(feature["nom"])
    elif elem["categorie"] in ["cio"]:
        elem["name"] = retreat_CIO_name(feature["nom"])
    elif elem["categorie"] in ["pmi"]:
        elem["name"] = retreat_PMI_name(feature["nom"])
    elif elem["categorie"] in ["mission_locale"]:
        elem["name"] = retreat_Mission_Locale_name(feature["nom"])                        
    elif elem["categorie"] in ["pole_emploi"]:
        elem["name"], elem["branch"] = retreat_Pole_Emploi_name(feature["nom"]) 
    elif elem["categorie"] in ["msap"]:
        elem["name"], elem["branch"] = retreat_France_Services_name(feature["nom"])           
    elif elem["categorie"] in ["ti", "tribunal_commerce", "tgi", 
                               "te", "cour_appel", "maison_centrale", "maison_arret", 
                               "centre_penitentiaire", "centre_detention", "csl"]:
        elem["name"] = feature["nom"]
    elif elem["categorie"] in ["urssaf"]:
        elem["name"] = retreat_Urssaf_name(feature["nom"])          
    else :
        elem["name"] = None
    elem["contact:phone"] = None
    if feature.get("telephone"):
    	phone_number = feature["telephone"][0]["valeur"]
    	if len(phone_number) > 9 and phone_number.startswith("0") and '(' not in phone_number :
        	elem["contact:phone"] = "+33 " + phone_number[1:]
    elem["contact:website"] = None
    if feature.get("site_internet"):
        elem["contact:website"] = feature.get("site_internet")[0]["valeur"]
    elem["contact:email"] = None
    if feature.get("adresse_courriel"):
        elem["contact:email"] = feature.get("adresse_courriel")[0]     
    elem["ref:FR:SIRET"] = feature["siret"]
 
    if not feature.get("adresse"):
        continue
    feature_address = feature["adresse"][0]
    elem["longitude"] = feature_address["longitude"]
    elem["latitude"] = feature_address["latitude"]
    elem["address_txt"] = "{} {} {} {} {}".format(
        feature_address["complement1"],
        feature_address["complement2"],
        feature_address["numero_voie"],
        feature_address["code_postal"],
        feature_address["nom_commune"],
    )
    elem["wheelchair"] = wheelchair_mapping[feature_address["accessibilite"]]
    elem["wheelchair:description"] = feature_address["note_accessibilite"]
    
    elem["opening_hours"] = parse_opening_hours(feature["plage_ouverture"])
    
    elem["insee"] = feature["code_insee_commune"]
    elem["id"] = feature["id"]
    elem["millesime"] = millesime

    export.append(elem)

with open('output/services_publics.csv', 'w') as out_file:
    csv_writer = csv.DictWriter(out_file, delimiter=',', fieldnames=export[0].keys())
    csv_writer.writeheader()
    for row in export:
        csv_writer.writerow(row)

