# BETA VERSION
import json
import requests
import re
import os
from crossref.restful import Works
from crossref.restful import Journals
from bs4 import BeautifulSoup
from idutils import is_doi
import pandas as pd
from tqdm import tqdm

from my_endpoints.extract_ORCID_info import Extract_ORCID_info
from my_endpoints.extract_DOI_info import Extract_DOI_info
from my_endpoints.extract_affiliation_info import Extract_affiliation_info


def affiliation_search(affiliation):
    works = Works()
    result = works.query(affiliation=f'"{affiliation}"').sample(10).select('title,author, abstract ,DOI, issued, deposited, published', 'ISSN')
    for item in result:
        is_affiliation = False
        is_affiliation = any(affiliation in aff_i['name'] 
                     for aff_j in item['author'] 
                     for aff_i in aff_j['affiliation'])

        if is_affiliation:
            print(item.keys()) 
            print(item['title'][0])
            print(item['author'])
            #print(item['author'][0]['affiliation'][0]['name'])
            if ('abstract' in item.keys()):print(str(item['abstract'])
                                                 .replace('<jats:p>','')
                                                 .replace('</jats:p>','')
                                                 .replace('<jats:title>','')
                                                 .replace('</jats:title>',' ')
                                                 .replace('<jats:p/>','')
                                                 .replace('<jats:sec>','')
                                                 .replace('</jats:sec>',' ')
                                                 .replace('<jats:italic>','')
                                                 .replace('</jats:italic>',' ')
                                                 .replace('<p>','')
                                                 .replace('</p>','')
                                                 .replace('<jats:bold>','')
                                                 .replace('</jats:bold>','')
                                                 .strip())
                
                                                 
            print(item['DOI'])
            if ('ISSN' in item.keys()):print(item['ISSN'])
            print(item['issued']['date-parts'][0][0])
            print(item['published']['date-parts'][0])
            #print(item['published-online']['date-parts'][0])
            print('---------------')
            

def affiliation_search(affiliation, yyyy, mm=None):
    works = Works()
    #result = works.query(affiliation=f'"{affiliation}"').sample(100).select('title,author, abstract ,DOI, issued, deposited, published', 'ISSN')
    result = works.query(affiliation=f'"{affiliation}"').select('title,author, abstract ,DOI, issued, deposited, published', 'ISSN')
    for item in result:
        if 'author' in item.keys() and 'DOI' in item.keys() and 'title' in item.keys(): #solo ingresan los que tienen los parametros llenos de author, title y DOI
            #Verifica la afiliación y solo se hace la busqueda cuando al menos un autor tiene la afiliación
            is_affiliation = False
            #is_affiliation = any(affiliation in aff_i['name'] 
            #             for aff_j in item['author'] 
            #             for aff_i in aff_j['affiliation'])
            
            for aff_j in item['author']:
                for aff_i in aff_j['affiliation']:
                    if 'name' in aff_i.keys():
                        if affiliation in aff_i['name']:
                            is_affiliation = True

            if is_affiliation and (yyyy in item['published']['date-parts'][0]) and mm==None: #Cuando se hace una busqueda solo por año
                print(item.keys()) 
                print(item['title'][0])
                print(item['author'])
                #print(item['author'][0]['affiliation'][0]['name'])
                if ('abstract' in item.keys()):print(str(item['abstract'])
                                                    .replace('<jats:p>','')
                                                    .replace('</jats:p>','')
                                                    .replace('<jats:title>','')
                                                    .replace('</jats:title>',' ')
                                                    .replace('<jats:p/>','')
                                                    .replace('<jats:sec>','')
                                                    .replace('</jats:sec>',' ')
                                                    .replace('<jats:italic>','')
                                                    .replace('</jats:italic>',' ')
                                                    .replace('<p>','')
                                                    .replace('</p>','')
                                                    .replace('<jats:bold>','')
                                                    .replace('</jats:bold>','')
                                                    .strip())
                print(item['DOI'])
                if ('ISSN' in item.keys()):print(item['ISSN'])
                print(item['issued']['date-parts'][0][0])
                print(item['published']['date-parts'][0])
                #print(item['published-online']['date-parts'][0])
                print('---------------')
                
            elif(is_affiliation and len(item['published']['date-parts'][0])>1):# cuando se realiza una busqueda por año y mes
                if (is_affiliation and 
                    (yyyy in item['published']['date-parts'][0]) and 
                    (mm == item['published']['date-parts'][0][1])):
                    print(item.keys()) 
                    print(item['title'][0])
                    print(item['author'])
                    #print(item['author'][0]['affiliation'][0]['name'])
                    if ('abstract' in item.keys()):print(str(item['abstract'])
                                                        .replace('<jats:p>','')
                                                        .replace('</jats:p>','')
                                                        .replace('<jats:title>','')
                                                        .replace('</jats:title>',' ')
                                                        .replace('<jats:p/>','')
                                                        .replace('<jats:sec>','')
                                                        .replace('</jats:sec>',' ')
                                                        .replace('<jats:italic>','')
                                                        .replace('</jats:italic>',' ')
                                                        .replace('<p>','')
                                                        .replace('</p>','')
                                                        .replace('<jats:bold>','')
                                                        .replace('</jats:bold>','')
                                                        .strip())
                        
                                                        
                    print(item['DOI'])
                    if ('ISSN' in item.keys()):print(item['ISSN'])
                    print(item['issued']['date-parts'][0][0])
                    print(item['published']['date-parts'][0])
                    #print(item['published-online']['date-parts'][0])
                    print('---------------')


def extractMetadataPaper(config, doi, write2File=False):
    '''
    Return all meta data of work by DOI 

    Parameters:
        DOI (String): Digital Object Identifie
        write2File (bool): All results write in a json File or in json (memory)
    
    Returns:
        list: json 
    
    Examples:
    >>> searchPapersByORCID('Path', "010.3390/app15041934", write2File=False)
    '''
     
    info = Extract_DOI_info(doi,config)
    is_correct, doi = info.validar_doi() #valida si existe el artículo con su DOI
    if is_correct:
        df_writeByDOI = pd.DataFrame(columns=['DOI', 
                                              'Title', 
                                              'Authors', 
                                              'Affiliation', 
                                              'Abstract', 
                                              'issn',  
                                              'Issued', 
                                              'Published'])
        
        title, author, affiliation, abstract, issn, issued, published = info.extractMetadata()
        new_row = [doi, title, author, affiliation, abstract, issn, issued, published]
        df_writeByDOI = pd.concat([df_writeByDOI, pd.DataFrame([new_row], columns=df_writeByDOI.columns)], ignore_index=True)

        if write2File == True:
            df_writeByDOI.to_json("data_paper.json", orient="records", lines=True)
        else:
            json_data = df_writeByDOI.to_dict(orient='records')
            return (json_data[0])
    else:
        print(f'DOI: {doi} is incorrect.')
        return None
    

def searchAuthorsByAffiliation(_affiliation, config, searchFull=False, write2File=False):
    '''
    Return all authors searched by a affiliation in resume o full information (include their works)

    Parameters:
        _affiliation (String): The name of the affiliation
        searchFull (bool):  Full search that include alls works or simple search
        write2File (bool): All results write in a File or in json
    
    Returns:
        list: json 
    
    Examples:
    >>> searchAuthorsByAffiliation("Universidad del Azuay", searchFull=False, write2File=False)
    '''
    # Configuración de la API de ORCID
    ORCID_API_URL = "https://pub.orcid.org/v3.0/search/"

    # Parámetros de búsqueda
    query = f"affiliation-org-name:\"{_affiliation}\""  # Reemplaza "Universidad" con el nombre de la universidad que buscas
    start = 0
    rows = 1000  # Número de resultados por página
    all_researchers = []

    # Encabezados de la solicitud
    headers = {
        "Accept": "application/json",
        #"Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    # Realizar la solicitud a la API de ORCID
    response = requests.get(ORCID_API_URL, headers=headers, params={
        "q": query,
        #"start": start,
        #"rows": rows
        "start": start
    })

    if response.status_code == 200:
        data_prime = response.json()
        max_results = data_prime.get("num-found", [])
        print(max_results)
        print(searchFull)
        if searchFull:
            df_writeByORCID = pd.DataFrame(columns=['ORCID', 'Name' ,'DOI', 'Title', 'Abstract','Author',  'Issued', 'Published'])
        else:
            df_writeByORCID = pd.DataFrame(columns=['ORCID', 'Name' ,'Affiliation', 'Status'])        

    while start < max_results:
        response = requests.get(ORCID_API_URL, headers=headers, params={
        "q": query,
        "start": start,
        "rows": rows
        })

        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            # Procesar la respuesta JSON
            data = response.json()
            researchers = data.get("result", [])
            count = data.get("num-found", [])
            # Mostrar los resultados
            for researcher in tqdm(researchers, total= len(researchers), desc=f"Researchers in {_affiliation}", unit=" Person", ncols=100, colour='blue', position=0, leave=False):
                orcid_id = researcher.get("orcid-identifier", {}).get("path") #Se obtiene el ORCID
                _status = 'Innactive'
                # URL base de la API de ORCID
                BASE_URL = f'https://pub.orcid.org/v3.0/{orcid_id}'
                # Realizar la solicitud GET
                response = requests.get(BASE_URL, headers=headers)
                
                # Verificar si la solicitud fue exitosa
                if response.status_code == 200: 
                    data_orcid = response.json()
                    orcid_profile = data_orcid.get('person', {})
                    name = orcid_profile.get('name', {})
                    if name:
                        if name.get('given-names', {}) is not None and name.get('given-names', {}).get('value') is not None:
                            given_name = name.get('given-names', {}).get('value')
                        else:
                            given_name = 'N/A'

                        if name.get('family-name', {}) is not None and name.get('family-name', {}).get('value') is not None:
                            family_name = name.get('family-name', {}).get('value')
                        else:
                            family_name = 'N/A'

                    name = (f"{family_name.replace('N/A','').upper()}, {given_name.upper()}")
                    affiliation = researcher.get("orcid-profile", {}).get("orcid-activities", {}).get("affiliations", {}).get("affiliation", [])

                    if len(affiliation) > 0 :
                        for aff in affiliation:
                            org_name = aff.get("organization", {}).get("name")
                            print(f"  - {org_name}")
                    else:
                        works = data_orcid.get('activities-summary', {}).get('works', {}).get('group', [])
                        if works:
                            for work in works:
                                work_summary = work.get('work-summary', [{}])[0]
                                # Verificar si existe DOI
                                if work_summary.get('external-ids', {}) != None:
                                    external_ids = work_summary.get('external-ids', {}).get('external-id', []) if work_summary.get('external-ids') else 'N/A'
                                    doi = 'N/A'
                                    for external_id in external_ids:
                                        if external_id.get('external-id-type') == 'doi':
                                            doi = external_id.get('external-id-value', 'N/A')
                                            break
                                    if ((doi != 'N/A')):
                                        _doi = (f"{doi if doi != 'N/A' else 'No disponible'}")
                                        info = Extract_DOI_info(doi,config)
                                        _title, author, org_name, abstract, issn, _issued, _published = info.extractMetadata()
                                        org_name = _affiliation
                                        _status = 'Active'
                                        if searchFull:
                                            new_row = [orcid_id, name, _doi, _title, abstract, author,  _issued, _published]
                                            df_writeByORCID = pd.concat([df_writeByORCID, pd.DataFrame([new_row], columns=df_writeByORCID.columns)], ignore_index=True)
                                        else:
                                            break;
                                else:
                                    break;
                        else:
                            org_name = _affiliation
                        
                    if searchFull ==False:    
                        new_row = [orcid_id, name, org_name, _status]
                        df_writeByORCID = pd.concat([df_writeByORCID, pd.DataFrame([new_row], columns=df_writeByORCID.columns)], ignore_index=True)
            # Verificar si hay más resultados
            if len(researchers) < rows or start + rows >= max_results:
                if write2File:
                    if searchFull:
                        df_writeByORCID.to_excel(f'{os.getcwd()}/Researchers In {_affiliation} - Full.xlsx')
                    else:
                        df_writeByORCID.to_excel(f'{os.getcwd()}/Researchers In {_affiliation}.xlsx')
                else:
                    json_data = df_writeByORCID.to_dict(orient='records')
                    return (json_data)  
                break  # No hay más resultados
            
            start += rows  # Avanzar al siguiente bloque de resultados 
              
        else:
            print(f"Error en la solicitud: {response.status_code}")
            print(response.text)
            break # Detener si hay un error

def searchPapersByORCID(config, inputFile=None, orcid=None, write2File=False):
    '''
    Return all works searched by a ORCID 

    Parameters:
        inputFile (String): The path of the read file in Excel format
        orcid (String):  Researcher ID
        write2File (bool): All results write in a File or in json
    
    Returns:
        list: json 
    
    Examples:
    >>> searchPapersByORCID('Path', "0000-8123-2323-xxxx", write2File=False)
    '''
    df_writeByORCID = pd.DataFrame(columns=['ORCID', 'Name' ,'DOI', 'Title', 'Abstract', 'Authors','Publication type',  'Issued', 'Published'])
    if (inputFile != '') and (orcid == ''):
        df = pd.read_excel(inputFile, sheet_name='DocentesUDA')
        # Filtra las filas donde 'Orcid' no es nulo ni está en blanco
        df = df[df['Orcid'].astype(str).str.strip() != '-']
        unique_orcid = df['Orcid'].astype(str).unique().tolist()
        df_writeByORCID = pd.DataFrame(columns=['ORCID', 'Name' ,'DOI', 'Title', 'Abstract', 'Authors','Publication type',  'Issued', 'Published'])        
        for orcid in tqdm(unique_orcid, total= len(unique_orcid), desc="Researchers ", unit=" Researcher", ncols=100, colour='blue', position=0, leave=False):
            df_writeByORCID = Extract_ORCID_info.extracInfoORCID(orcid, df_writeByORCID)
    
    elif (orcid != '') and (inputFile == ''):
        info = Extract_ORCID_info(orcid, config)
        df_writeByORCID = info.extracInfoORCID(df_writeByORCID)
    else:
        return None
    
    if write2File:
        df_writeByORCID.to_excel(f'{os.getcwd()}/papersByOrcid.xlsx')
    else:
        json_data = df_writeByORCID.to_dict(orient='records')
        return (json_data)


def searchPapersByAffiliation(config, affiliation, from_date, to_date, write2File=False):
    '''
    Return all works searched by an Affiliation

    Parameters:
        affiliation (String): The name of the affiliation
        from_date (String): Date the works search begins
        to+date (String): Date the works search ends
        write2File (bool): All results write in a File or in json
    
    Returns:
        list: json 
    
    Examples:
    >>> searchPapersByAffiliation('Affiliation', '2024-11', '2024-12', write2File=False)
    '''
    info = Extract_affiliation_info(config, affiliation, from_date, to_date)
    df_write = pd.DataFrame(columns=['DOI', 'Title','Authors', 'Abstract', 'ISSN', 'Issued', 'Published'])
    df_write_crossRef = info.affiliation_search_crossRef()
    df_write_elsevier = info.affiliation_search_Elsevier()
    df_write_ByOrcid = info.affiliation_search_byOrcid()
    df_write = pd.concat([df_write_crossRef, df_write_elsevier, df_write_ByOrcid])
    df_write = df_write.drop_duplicates(subset='DOI', keep='first').reset_index(drop=True)
    if write2File:
        df_write.to_excel(f'{os.getcwd()}/papers in {affiliation} between {from_date}_{to_date}.xlsx')
    else:
        json_data = df_write.to_dict(orient='records')
        return (json_data)
