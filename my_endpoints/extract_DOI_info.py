# BETA VERSION
import requests
import re
from crossref.restful import Works
from crossref.restful import Journals
from bs4 import BeautifulSoup
from idutils import is_doi
import pandas as pd
from tqdm import tqdm

class Extract_DOI_info:
    def __init__(self, doi, config):
        self.doi = doi
        self.config = config

    def elsevier(self):
        '''
        Search all information in Elsevier about a work through DOI

        Parameters:
            doi (string): Unique identifier of the scientific works.

        Returns:
            list[str]: String list of works information.
        '''
        try:
            apiKey_elsevier = self.config["api_keys"]["elsevier"]
            _title, _author, _affiliation, _abstract, _issn, _issued, _published = self.crossRef()
            
            if _title or _abstract or _author or _issn or _issued or _published is None:
                url = f"https://api.elsevier.com/content/article/doi/{self.doi}?apiKey={apiKey_elsevier}&httpAccept=application/json"
                respuesta = requests.get(url)
                if respuesta.status_code == 200:
                    # Lanza una excepción para códigos de estado HTTP malos (4xx o 5xx)
                    datos = respuesta.json()
                    _title = (datos['full-text-retrieval-response']['coredata']['dc:title']) if _title is None else _title
                    _abstract = (datos['full-text-retrieval-response']['coredata']['dc:description']) if _abstract is None else _abstract
                    _author = (datos['full-text-retrieval-response']['coredata']['dc:creator']) if _author is None else _author         
                    _issn = (datos['full-text-retrieval-response']['coredata']['prism:issn']) if _issn is None else _issn         
            return _title, _author, _affiliation, _abstract, _issn, _issued, _published
        except requests.exceptions.RequestException as e:
            print(f"Error al hacer la solicitud a la API de Elsevier: {e}")
            return None
        except KeyError:
            print("Error: La respuesta de la API no contiene los metadatos esperados.")
            return None
    
    def springer(self):
        '''
        Search all information in Springer about a work through DOI

        Parameters:
            doi (string): Unique identifier of the scientific works.

        Returns:
            list[str]: String list of works information.
        '''
        try:
            apiKey_springer = self.config["api_keys"]["springer"]
            _title, _author, _affiliation, _abstract, _issn, _issued, _published = self.crossRef()
            if _title or _abstract or _author or _issued or _published is None:
                url = f'https://api.springernature.com/metadata/json?api_key={apiKey_springer}&callback=&s=1&p=10&q=(doi:{self.doi})'
                response = requests.request("GET", url)            
                if response.status_code == 200:
                    data = response.json()
                    total_search = int(data['result'][0]['total'])
                    if (total_search>0):
                        for i in range(0,total_search):
                            _title = data['records'][i]['title'] if _title is None else _title
                            _abstract = data['records'][i]['abstract'] if _abstract is None else _abstract
                            _author = data['records'][i]['creators'] if _author is None else _author
                            _published = data['records'][i]['publicationDate'] if _published is None else _published
                            #_issn = data['records'][i]['ISSN'] if _issn is None else _issn
                    else:
                        _title = data['records'][0]['title'] if _title is None else _title
                        _abstract = data['records'][0]['abstract'] if _abstract is None else _abstract
                        _author = data['records'][0]['creators'] if _author is None else _author
                        _published = data['records'][0]['publicationDate'] if _published is None else _published

            return _title, _author, _affiliation, _abstract, _issn, _issued, _published
        except requests.exceptions.RequestException as e:
            print(f"Error al hacer la solicitud a la API de Springer: {e}")
            return None, None, None, None, None, None, None
        except KeyError:
            print("Error: La respuesta de la API no contiene los metadatos esperados.")
            return None, None, None, None, None, None, None 

    def crossRef(self):
        '''
        Search all information in CrossRef about a work through DOI

        Parameters:
            doi (string): Unique identifier of the scientific works.

        Returns:
            list[str]: String list of works information.
        '''
        works = Works()
        result = works.doi(self.doi)
        
        _title = _abstract = _author = _affiliation = _issn = _issued = _published = None
        if ('title' in  result.keys()):
            if len(result['title']) > 0:
                _title = result['title'][0] #print(result['title'][0])
            if 'abstract' in result.keys():
                _abstract = (str(result['abstract']).replace('<jats:p>', '').replace('</jats:p>', '').replace('</jats:title>','').replace('<jats:title>','').replace('<jats:italic>', '').replace('</jats:italic>', ''))
            if 'author' in result.keys():
                _author = result['author']
                nombres_apellidos = []
                authors_affiliation = []
                for autor in _author:
                    nombre = autor.get('given', '')
                    apellido = autor.get('family', '')
                    affiliation = autor.get('affiliation', '')
                    if nombre and apellido:  # Solo agregar si ambos existen                        
                        nombres_apellidos.append(f"{nombre} {apellido}")
                        authors_affiliation.append(affiliation)
                _author = "; ".join(nombres_apellidos)
                #Se comprueba si esta o no vacia la afiliación
                if (all(len(sublist) == 0 for sublist in authors_affiliation)) :
                    _affiliation = ""
                else:
                    #Extraer los valores de 'name' y unirlos dentro de cada sublista
                    sublists_as_strings = [
                        ". ".join(item['name'] for item in sublist)
                        for sublist in authors_affiliation
                    ]
                    #Unir todas las cadenas resultantes con "; "
                    _affiliation = "; ".join(sublists_as_strings)

            if 'ISSN' in result.keys():
                _issn = "; ".join(result['ISSN'])
                
            if 'issued' in result.keys(): 
                if (result['issued'] != ""):
                    str_fecha = [str(elemento) for elemento in result['issued']['date-parts'][0]]
                    _issued = "-".join(str_fecha)

            if 'published' in result.keys(): 
                if (result['published'] != ""):
                    str_fecha = [str(elemento) for elemento in result['published']['date-parts'][0]]
                    _published = "-".join(str_fecha)
        else:
            self.scrapMetadatos()
        return _title, _author, _affiliation, _abstract, _issn, _issued, _published 
    
    def scrapMetadatos(self):
        '''
        Resolve a DOI to its final URL using the DOI redirection service.

        Parameters:
            doi (string): Unique identifier of the scientific works.

        Returns:
            list[str]: String list of works information.
        '''

        url = f"https://doi.org/{self.doi}"
        response = requests.get(url, allow_redirects=True)
        
        if response.status_code == 200:
            _title = _author = _abstract = _issn  = _issued = _published = ''
            if ('ejgo' in response.url):
                url = response.url  # Devuelve la URL final después de las redirecciones
                # Realizar la solicitud HTTP
                response = requests.get(url)
                # Parsear el contenido HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                # Extraer el título
                title = soup.find('title').get_text(strip=True) if soup.find('title') else 'Título no encontrado'
                # Extraer autores (depende de la estructura HTML)
                authors = [meta['content'] for meta in soup.find_all('meta', attrs={'name': 'DC.Creator'})]
                # Extraer el resumen (depende de la estructura HTML)
                abstract = soup.find('meta', attrs={'name': 'DC.Description'})['content']
            
            if ('arxiv' in response.url):
                try:
                    # 1. Extraer el identificador de arXiv del DOI (usando regex)
                    match = re.search(r"10\.48550/arXiv\.(\d+\.\d+)", self.doi)
                    if not match:
                        return None  # DOI no válido

                    arxiv_id = match.group(1)

                    # 2. Construir la URL de arXiv
                    url = f"https://arxiv.org/abs/{arxiv_id}"

                    # 3. Realizar la solicitud GET
                    response = requests.get(url)
                    response.raise_for_status()  # Lanza una excepción para códigos de error HTTP

                    # 4. Parsear el HTML
                    soup = BeautifulSoup(response.content, "html.parser")

                    # 5. Extraer metadatos (usando selectores CSS más robustos)
                    metadatos = {}

                    def extraer_contenido(selector, atributo='content', multiple=False):
                        elementos = soup.select(selector)
                        if elementos:
                            if multiple:
                                return [e.get(atributo) for e in elementos if e.get(atributo)] # Manejo de atributos faltantes en elementos de la lista
                            else:
                                elemento = elementos[0]
                                return elemento.get(atributo) if elemento.get(atributo) else None # Manejo de atributo faltante
                        return None
                    
                    _title = extraer_contenido('meta[property="og:title"]')
                    _abstract = extraer_contenido('meta[property="og:description"]')
                    _published = extraer_contenido('meta[name="citation_date"]').replace("/", "-")
                    _affiliation = ''
                    _author = "; ".join([nombre.replace(",", "") for nombre in (extraer_contenido('meta[name="citation_author"]', multiple=True))])
            
                    metadatos["categories"] = extraer_contenido('meta', multiple=True)

                    # arXiv v3 style metadata (con manejo de NoneType)
                    if not _author:
                        autores_elements = soup.select('.authors > a')
                        _author = [a.text.strip() for a in autores_elements] if autores_elements else None

                    if not metadatos["categories"]:
                        categorias_elements = soup.select('.subjects')
                        metadatos["categories"] = [c.text.strip() for c in categorias_elements] if categorias_elements else None
                except requests.exceptions.RequestException as e:
                    print(f"Error en la solicitud: {e}")
                    return None
                except (AttributeError, TypeError) as e:  # Maneja errores si no se encuentran elementos
                    print(f"Error al parsear el HTML: {e}")
                    return None
                except Exception as e:
                    print(f"Error inesperado: {e}")
                    return None
            return _title, _author, _affiliation, _abstract, _issn, _issued, _published 


        else:
            print(f"Error: No se pudo resolver el DOI. Código de estado: {response.status_code}")
            return None
    
    def extractMetadata(self):
        '''
        Extract work's information since different sources

        Parameters:
            doi (string): Unique identifier of the scientific works.

        Returns:
            list[str]: String list of works information.
        '''
        try:
            works = Works()
            result = works.doi(self.doi)
            _title = _abstract = _affiliation = _author = _issn = _issued = _published = ''
            if result != None:
                if 'content-domain' in result.keys():
                    if len(result['content-domain']['domain'])>0:
                        if("elsevier" in result['content-domain']['domain'][0]):
                            _title, _author, _affiliation, _abstract, _issn, _issued, _published = self.elsevier()
                        elif ("springer" in result['content-domain']['domain'][0]):
                            _title, _author, _affiliation, _abstract, _issn, _issued, _published = self.springer() 
                        else:
                            _title, _author, _affiliation, _abstract, _issn, _issued, _published = self.crossRef()
                    elif 'publisher' in result.keys():
                        if len(result['publisher'])>0:
                            if 'IEEE' in result['publisher']:
                                #_title, _abstract, _author = ieee(doi) #activar cuando se active el api key
                                _title, _author, _affiliation, _abstract, _issn, _issued, _published = self.crossRef() 
                            else:
                                _title, _author, _affiliation, _abstract, _issn, _issued, _published = self.crossRef()  
                        else:
                            _title, _author, _affiliation, _abstract, _issn, _issued, _published = self.crossRef()     
                    else:
                        _title, _author, _affiliation, _abstract, _issn, _issued, _published = self.crossRef()
                        
                elif 'license' in result.keys():
                    if(len(result['license'][0]['URL'])>0):                            
                        if "creativecommons" in result['license'][0]['URL']:
                            _title, _author, _affiliation, _abstract, _issn, _issued, _published = self.crossRef()
            elif('arXiv' in self.doi):
                _title, _author, _affiliation, _abstract, _issn, _issued, _published = self.scrapMetadatos()
            else:
                return None, None, None, None, None, None, None #no existe el doi
            return _title, _author, _affiliation, _abstract, _issn, _issued, _published 
            
        except KeyError as e:
            print(f"Error: No se encuentra el Key: {e}")
            return None
    
    def validar_doi(self):
        '''
        Check DOI in format and if exist the publication

        Parameters:
            doi (string): Unique identifier of the scientific works.

        Returns:
            valid (bool): String list of works information.
            
        '''
        if ('DOI' in self.doi):self.doi = self.doi[self.doi.rindex(': ')+2:]

        if not (bool(is_doi(self.doi))):
            return False, self.doi

        if Works().doi(self.doi):
            return True, self.doi

        try:
            result = requests.get(f"https://doi.org/{self.doi}", allow_redirects=True, timeout=10)
            return result.status_code == 200, self.doi
        except requests.RequestException:
            return False, self.doi