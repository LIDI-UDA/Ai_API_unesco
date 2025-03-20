# BETA VERSION
import json
import requests
import calendar
import re
from datetime import datetime
from crossref.restful import Works
from crossref.restful import Journals
from bs4 import BeautifulSoup
from idutils import is_doi
import pandas as pd
from tqdm import tqdm
from my_endpoints.extract_DOI_info import Extract_DOI_info

class Extract_affiliation_info:
    def __init__(self, config, affiliation, from_date, until_date):        
        self.config = config
        self.affiliation = affiliation
        self.from_date = from_date
        self.until_date = until_date
    
    def affiliation_search_crossRef(self):
        '''
        Search for all works information in CrossRef through affiliation between the dates entered in the parameters.

        Parameters:
            affiliation (String): The name of the affiliation
            from_date (String): Date the works search begins
            to_date (String): Date the works search ends

        Returns:
            list[str]: String list of works information.
        '''
        _from_date = self.from_date or (datetime.date.today()).strftime("%Y-%m")
        _until_date = self.until_date or (datetime.date.today()).strftime("%Y-%m")
        df_write = pd.DataFrame(columns=['DOI', 'Title', 'Authors', 'Abstract', 'ISSN', 'Issued', 'Published'])
        works = Works()
        result = works.query(affiliation=f'"{self.affiliation}"').select('title, author, abstract ,DOI, issued, deposited, published', 'ISSN').sort('published').order('asc').filter(has_affiliation='true').filter(from_online_pub_date = _from_date).filter(until_online_pub_date = _until_date)
        _count = works.query(affiliation=f'"{self.affiliation}"').select('title, author, abstract ,DOI, issued, deposited, published', 'ISSN').sort('published').order('asc').filter(has_affiliation='true').filter(from_online_pub_date = _from_date).filter(until_online_pub_date = _until_date).count()
    
        for item in tqdm(result, total= _count, desc="Papers in CrossRef", unit=" files", ncols=100, colour='blue', position=0, leave=False):
            _doi = _title = _abstract = _authors = _ISSN = _issued = _published = None
            if 'DOI' in item.keys() and 'title' in item.keys(): #solo ingresan los que tienen los parametros llenos de author, title y DOI
                #Verifica la afiliación y solo se hace la busqueda cuando al menos un autor tiene la afiliación
                is_affiliation = False
                if 'author' in item.keys():
                    for aff_j in item['author']:
                        for aff_i in aff_j['affiliation']:
                            if 'name' in aff_i.keys():
                                if self.affiliation in aff_i['name']:
                                    is_affiliation = True

                if is_affiliation: #Cuando se hace una busqueda solo por año
                    _doi = item['DOI']
                    _title = item['title'][0]
                    _authors = item['author']
                    nombres_apellidos = []
                    for autor in _authors:
                        nombre = autor.get('given', '')
                        apellido = autor.get('family', '')
                        if nombre and apellido:  # Solo agregar si ambos existen
                            nombres_apellidos.append(f"{nombre} {apellido}")
                    _authors = "; ".join(nombres_apellidos)
                    
                    if ('abstract' in item.keys()):_abstract = (str(item['abstract'])
                                                        .replace('<jats:p>','')
                                                        .replace('</jats:p>','')
                                                        .replace('<jats:title>','')
                                                        .replace('</jats:title>',' ')
                                                        .replace('<jats:p/>','')
                                                        .replace('<jats:sec>','')
                                                        .replace('</jats:sec>',' ')
                                                        .replace('<jats:italic>','')
                                                        .replace('</jats:italic>',' ')
                                                        .replace('<jats:bold>', '')
                                                        .replace('</jats:bold>',' ')
                                                        .replace('<p>','')
                                                        .replace('</p>','')
                                                        .replace('<jats:bold>','')
                                                        .replace('</jats:bold>','')
                                                        .replace('</jats:sec><jats:sec>\n', '')
                                                        .strip()
                                                        )
                    
                    if ('ISSN' in item.keys()):_ISSN = '; '.join(item['ISSN'])
                    #_issued = item['issued']['date-parts'][0][0]
                    if 'issued' in item.keys(): 
                        if (item['issued'] != ""):
                            str_fecha = [str(elemento) for elemento in item['issued']['date-parts'][0]]
                            _issued = "-".join(str_fecha)
                    if 'published' in item.keys(): 
                        str_fecha = [str(elemento) for elemento in item['published']['date-parts'][0]]
                        _published = "-".join(str_fecha)
                        
                    new_row = [_doi, _title, _authors, _abstract, _ISSN, _issued, _published]
                    df_write = pd.concat([df_write, pd.DataFrame([new_row], columns=df_write.columns)], ignore_index=True)     
        return df_write     
    
    def affiliation_search_Elsevier(self):
        '''
        Search for all works information in Elsevier through affiliation between the dates entered in the parameters.

        Parameters:
            affiliation (String): The name of the affiliation
            from_date (String): Date the works search begins
            to_date (String): Date the works search ends

        Returns:
            list[str]: String list of works information.
        '''

        apiKey_elsevier = self.config["api_keys"]["elsevier"]

        # Convert dates to datetime objects
        inicio = datetime.strptime(self.from_date, "%Y-%m")
        fin = datetime.strptime(self.until_date, "%Y-%m")
        
        # Lista para almacenar los meses y años formateados
        meses_formateados = []
        # Iterar sobre el rango de fechas
        while inicio <= fin:
            # Formatear el mes y año como "Month YYYY"
            meses_formateados.append(inicio.strftime("%B %Y"))
            # Avanzar al siguiente mes
            if inicio.month == 12:
                inicio = inicio.replace(year=inicio.year + 1, month=1)
            else:
                inicio = inicio.replace(month=inicio.month + 1)
        # Unir los meses formateados con " OR "
        _dateString = " OR ".join(f'"{mes}"' for mes in meses_formateados)
        
        # URL base de la API de Scopus
        url = 'https://api.elsevier.com/content/search/scopus'
        
        # Parámetros de la solicitud
        params = {
            #'query': f'AF-ID({"\"{affiliation}\" 60108706"}) AND PUBDATETXT("{_fromDate}" OR "{_toDate}")  AND (LIMIT-TO(DOCTYPE,"ar") OR LIMIT-TO(DOCTYPE,"cp") OR LIMIT-TO(DOCTYPE,"ch") OR LIMIT-TO(DOCTYPE,"re"))',
            'query': f'AF-ID({"\"{self.affiliation}\" 60108706"}) AND PUBDATETXT({_dateString})  AND (LIMIT-TO(DOCTYPE,"ar") OR LIMIT-TO(DOCTYPE,"cp") OR LIMIT-TO(DOCTYPE,"ch") OR LIMIT-TO(DOCTYPE,"re"))',
            'apiKey': apiKey_elsevier,
            'count' : 200,
            'httpAccept': 'application/json'
        }

        # Hacer la solicitud a la API
        response = requests.get(url, params=params)
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            df_writeByAff = pd.DataFrame(columns=['DOI','Title', 'Authors' ,'Abstract', 'ISSN',  'Issued', 'Published'])
            # Convertir la respuesta a JSON
            data = response.json()
            count_search = int(data.get('search-results', {}).get('opensearch:totalResults'))
            datos = data.get('search-results', {}).get('entry', [])
            
            for entry in tqdm(datos, total= count_search, desc="Papers in Elsevier ", unit=" files", ncols=100, colour='blue', position=0, leave=False):
                _title = _issn = _issued = ''
                doi = entry.get('prism:doi')
                if doi:
                    issn_list = [value for key, value in entry.items() 
                        if key in ('prism:issn', 'prism:eIssn') and value]
                    _issn = '; '.join(issn_list)
                    info_doi = Extract_DOI_info(doi, self.config)
                    _title,_author,affiliation, _abstract, issn, _issued, published = info_doi.extractMetadata()

                    new_row = [doi, _title, _author, _abstract, _issn, _issued, entry.get('prism:coverDate')]
                    df_writeByAff = pd.concat([df_writeByAff, pd.DataFrame([new_row], columns=df_writeByAff.columns)], ignore_index=True)
    
            return df_writeByAff
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    
    def affiliation_search_byOrcid(self, inputFile=''):
        '''
        Search for all works information in ORCID through affiliation between the dates entered in the parameters.

        Parameters:
            affiliation (String): The name of the affiliation
            from_date (String): Date the works search begins
            to_date (String): Date the works search ends

        Returns:
            list[str]: String list of works information.
        '''

        df_writeByAff = pd.DataFrame(columns=['DOI', 'Title', 'Authors', 'Abstract', 'ISSN', 'Issued', 'Published'])
        # Convertir las fechas a objetos datetime
        inicio = datetime.strptime(self.from_date, "%Y-%m")
        fin = datetime.strptime(self.until_date + "-01","%Y-%m-%d")
         # Obtener el último día del mes usando calendar.monthrange
        _, ultimo_dia = calendar.monthrange(fin.year, fin.month)
        fin = datetime(fin.year, fin.month, ultimo_dia)
        if inputFile != '':
            #Code to add when reading a file and proceed with the extraction of metadata
            print('')
        else:
            # Configuración de la API de ORCID
            ORCID_API_URL = "https://pub.orcid.org/v3.0/search/"

            # Parámetros de búsqueda
            query = f"affiliation-org-name:\"{self.affiliation}\""  # Reemplaza "Universidad" con el nombre de la universidad que buscas
            # Convertir las fechas a objetos datetime
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

                    for researcher in tqdm(researchers, total= len(researchers), desc=f"Researchers in {self.affiliation} ({self.from_date} to {self.until_date})", unit=" Work", ncols=100, colour='blue', position=0, leave=False):
                        orcid_id = researcher.get("orcid-identifier", {}).get("path") #Se obtiene el ORCID
                        _status = 'Innactive'
                        # URL base de la API de ORCID
                        BASE_URL = f'https://pub.orcid.org/v3.0/{orcid_id}'
                        # Realizar la solicitud GET
                        response = requests.get(BASE_URL, headers=headers)
                        data_orcid = response.json()
                        # Verificar si la solicitud fue exitosa
                        if response.status_code == 200: 
                            works = data_orcid.get('activities-summary', {}).get('works', {}).get('group', [])
                            if works:
                                for work in works:
                                    work_summary = work.get('work-summary', [{}])[0]
                                    publication_date = work_summary.get("publication-date", {})
                                    
                                    if publication_date != None:
                                        year = publication_date.get("year", {}).get("value") if publication_date.get('year') else 'N/A'
                                        month = publication_date.get("month", {}).get("value", 1) if publication_date.get('month') else None
                                        day = publication_date.get("day", {}).get("value", 1) if publication_date.get('day') else 1
                                    if year and month:
                                        # Si el día no está disponible, lo establecemos como 1
                                        try:
                                            fecha_publicacion = datetime(int(year), int(month), int(day))
                                        except ValueError:
                                            _, ultimo_dia = calendar.monthrange(int(year), int(month))
                                            fecha_publicacion = datetime(int(year), int(month), ultimo_dia)
                                        if fecha_publicacion >= inicio and fecha_publicacion <= fin:
                                            # Verificar si existe DOI
                                            external_ids = work_summary.get('external-ids', {}).get('external-id', [])
                                            doi = 'N/A'
                                            for external_id in external_ids:
                                                if external_id.get('external-id-type') == 'doi':
                                                    doi = external_id.get('external-id-value', 'N/A')
                                                    break
                                            if ((doi != 'N/A')):
                                                _doi = (f"{doi if doi != 'N/A' else 'No disponible'}")
                                                info_doi = Extract_DOI_info(_doi,self.config)                                        
                                                _title, author, org_name, abstract, issn, _issued, _published = info_doi.extractMetadata()
                                                if org_name != None:
                                                    if self.affiliation in org_name:
                                                        new_row = [_doi, _title, author, abstract, issn, _issued, _published]
                                                        df_writeByAff = pd.concat([df_writeByAff, pd.DataFrame([new_row], columns=df_writeByAff.columns)], ignore_index=True)
                                                        
                    # Verificar si hay más resultados
                    if len(researchers) < rows or start + rows >= max_results:
                        return df_writeByAff 
                        break  # No hay más resultados
                    
                    start += rows  # Avanzar al siguiente bloque de resultados 
                else:
                    print(f"Error en la solicitud: {response.status_code}")
                    print(response.text)
                    break # Detener si hay un error    
