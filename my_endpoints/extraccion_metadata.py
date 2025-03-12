# BETA VERSION
import json
import requests
import re
import time
from crossref.restful import Works
from crossref.restful import Journals
from bs4 import BeautifulSoup
from idutils import is_doi

def extraer_metadatos_orcid(orcid_id, access_token):
    """
    Extrae metadatos de un perfil de ORCID usando su ID y token de acceso.
    Args:
        orcid_id (str): El ID de ORCID del perfil.
        access_token (str): Tu token de acceso de ORCID.
    Retorna:
        dict: Un diccionario con los metadatos del perfil de ORCID, o None si ocurre un error.
    """
    url = f"https://api.orcid.org/v3.0/{orcid_id}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    try:
        respuesta = requests.get(url, headers=headers)
        respuesta.raise_for_status()  # Lanza una excepción para códigos de estado HTTP malos (4xx o 5xx)
        datos = respuesta.json()
        print(datos)
        #return datos
    except requests.exceptions.RequestException as e:
        print(f"Error al hacer la solicitud a la API de ORCID: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: La respuesta de la API no es un JSON válido.")
        return None
        

def outputFile_json(doi, title, abstract, author, is_write=False):
    data = {
      "doi" : doi,
      "title": title,
      "abstract": abstract,
      "author": author
    }
    if is_write == True:
        with open('data_paper.json', "w") as archivo_json:
            json.dump(data, archivo_json, indent=4)
    else:
        return json.dumps(data)
        

def elsevier(doi, config):
    try:
        apiKey = config["api_keys"]["elsevier"]
        url = f"https://api.elsevier.com/content/article/doi/{doi}?apiKey={apiKey}&httpAccept=application/json"
        respuesta = requests.get(url)
        respuesta.raise_for_status()  # Lanza una excepción para códigos de estado HTTP malos (4xx o 5xx)
        datos = respuesta.json()
        return (datos['full-text-retrieval-response']['coredata']['dc:title']),(datos['full-text-retrieval-response']['coredata']['dc:description']), (datos['full-text-retrieval-response']['coredata']['dc:creator'])
        
    except requests.exceptions.RequestException as e:
        print(f"Error al hacer la solicitud a la API de Elsevier: {e}")
        return None
    except KeyError:
        print("Error: La respuesta de la API no contiene los metadatos esperados.")
        return None
        

def crossRef(doi):
    works = Works()
    result = works.doi(doi)
    _title = _abstract = _author= None
    if ('license' in  result.keys()):
        if 'title' in result.keys(): _title = result['title'][0] #print(result['title'][0])
        if 'abstract' in result.keys():
            #print(str(result['abstract']).replace('<jats:p>', '').replace('</jats:p>', '').replace('</jats:title>','').replace('<jats:title>','').replace('<jats:italic>', '').replace('</jats:italic>', ''))
            _abstract = (str(result['abstract']).replace('<jats:p>', '').replace('</jats:p>', '').replace('</jats:title>','').replace('<jats:title>','').replace('<jats:italic>', '').replace('</jats:italic>', ''))
        if 'author' in result.keys():
            _author = result['author']
            #for author in result['author']:
            #    print(author)

    else:
        if 'title' in result.keys():
            if 'title' in result.keys(): _title = result['title'][0] #print(result['title'][0])
            if 'abstract' in result.keys():
                #print(str(result['abstract']).replace('<jats:p>', '').replace('</jats:p>', '').replace('</jats:title>','').replace('<jats:title>','').replace('<jats:italic>', '').replace('</jats:italic>', ''))
                _abstract = (str(result['abstract']).replace('<jats:p>', '').replace('</jats:p>', '').replace('</jats:title>','').replace('<jats:title>','').replace('<jats:italic>', '').replace('</jats:italic>', ''))
            if 'author' in result.keys():
                _author = result['author']
                #for author in result['author']:
                #    print(author)
        else:
            scrapMetadatos(doi)

    return _title,_abstract, _author 
    

def springer(doi, config):
    apikey = config["api_keys"]["springer"]
    url = f'https://api.springernature.com/metadata/json?api_key={apikey}&callback=&s=1&p=10&q=(doi:{doi})'
    response = requests.request("GET", url)
    data = response.json()
    _title = _abstract = _author= None
    total_search = int(data['result'][0]['total'])
    if (total_search>0):
        for i in range(0,total_search):
            _title = data['records'][i]['title']
            _abstract = data['records'][i]['abstract']
            _author = data['records'][i]['creators']
    else:
        _title = data['records'][0]['title']
        _abstract = data['records'][0]['abstract']
        _author = data['records'][0]['creators']
        
    return _title, _abstract, _author
    

def scrapMetadatos(doi):
    """
    Resuelve un DOI a su URL final utilizando el servicio de redirección de DOI.
    """
    url = f"https://doi.org/{doi}"
    response = requests.get(url, allow_redirects=True)
    
    if response.status_code == 200:

        if ('ejgo' in response.url):
            url = response.url  # Devuelve la URL final después de las redirecciones
            # Realizar la solicitud HTTP
            response = requests.get(url)
            # Parsear el contenido HTML
            soup = BeautifulSoup(response.content, 'html.parser')
        
            # Extraer el título
            title = soup.find('title').get_text(strip=True) if soup.find('title') else 'Título no encontrado'
            print(title)
            # Extraer autores (depende de la estructura HTML)
            authors = [meta['content'] for meta in soup.find_all('meta', attrs={'name': 'DC.Creator'})]
            print(authors)
            # Extraer el resumen (depende de la estructura HTML)
            abstract = soup.find('meta', attrs={'name': 'DC.Description'})['content']
            print(abstract)
            # Extraer la fecha de publicación (depende de la estructura HTML)
            #date = soup.find('span', class_='date').get_text(strip=True) if soup.find('span', class_='date') else 'Fecha no encontrada'
        
        if ('arxiv' in response.url):
            try:
                # 1. Extraer el identificador de arXiv del DOI (usando regex)
                match = re.search(r"10\.48550/arXiv\.(\d+\.\d+)", doi)
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

                metadatos["title"] = extraer_contenido('meta[property="og:title"]')
                metadatos["abstract"] = extraer_contenido('meta[property="og:description"]')
                metadatos["date"] = extraer_contenido('meta[property="article:published_time"]')

                metadatos["authors"] = extraer_contenido('meta[name="citation_author"]', multiple=True)
                metadatos["categories"] = extraer_contenido('meta[name="citation_subject"]', multiple=True)

                # arXiv v3 style metadata (con manejo de NoneType)
                if not metadatos["authors"]:
                    autores_elements = soup.select('.authors > a')
                    metadatos["authors"] = [a.text.strip() for a in autores_elements] if autores_elements else None

                if not metadatos["categories"]:
                    categorias_elements = soup.select('.subjects')
                    metadatos["categories"] = [c.text.strip() for c in categorias_elements] if categorias_elements else None
                
                return metadatos['title'], metadatos['abstract'], metadatos['authors']

            except requests.exceptions.RequestException as e:
                print(f"Error en la solicitud: {e}")
                return None
            except (AttributeError, TypeError) as e:  # Maneja errores si no se encuentran elementos
                print(f"Error al parsear el HTML: {e}")
                return None
            except Exception as e:
                print(f"Error inesperado: {e}")
                return None
    else:
        print(f"Error: No se pudo resolver el DOI. Código de estado: {response.status_code}")
        return None
        

def valida_formato_doi(doi):
  return (bool(is_doi(doi)))
    

def validar_doi(doi):
    if ('DOI' in doi):doi = doi[doi.rindex(': ')+2:]

    if not valida_formato_doi(doi):
        return False, doi

    if Works().doi(doi):
        return True, doi

    try:
        result = requests.get(f"https://doi.org/{doi}", allow_redirects=True, timeout=10)
        return result.status_code == 200, doi
    except requests.RequestException:
        return False, doi
        

def journals(issn):
    journals = Journals()
    if (journals.journal_exists(issn)):
        results = journals.journal(issn)
        return results
    else:
        return 'Journal no exist'
        

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
                    

def extractMetadata(doi, config):
    try:
        works = Works()
        result = works.doi(doi)
        _title = _abstract = _author = ''
        if result != None:
            if 'content-domain' in result.keys():
                if len(result['content-domain']['domain'])>0:
                    if("elsevier" in result['content-domain']['domain'][0]):
                        _title, _abstract, _author = elsevier(doi, config)
                    elif ("springer" in result['content-domain']['domain'][0]):
                        _title, _abstract, _author = springer(doi, config) 
                    else: 
                        _title, _abstract, _author = crossRef(doi)
                else:
                    _title, _abstract, _author =crossRef(doi)
            elif 'license' in result.keys():
                if(len(result['license'][0]['URL'])>0):                            
                    if "creativecommons" in result['license'][0]['URL']:
                        _title, _abstract, _author = crossRef(doi)
                        #print('creativecommons')
                
        elif('arXiv' in doi):
            _title, _abstract, _author = scrapMetadatos(doi)
            #print('arXiv')
        else:
            return None #no existe el doi
        return _title, _abstract, _author
        
    except KeyError as e:
        print(f"Error: No se encuentra el Key: {e}")
        return None
        

def readFiles(excel_path):
    df = pd.read_excel(excel_path, sheet_name='Vice. Invest.')
    df_write = pd.DataFrame(columns=['index', 'doi', 'title','abstract', 'authors'])
    return df,df_write
    

def extractMetadataPaper(doi, config):
    is_correct, doi = validar_doi(doi) #valida si existe el artículo con su DOI
    if is_correct:
        title, abstract, author = extractMetadata(doi, config)
        data = outputFile_json(doi, title, abstract, author)
        #print(data)
        return data
    else:
        print(f'DOI {doi} is incorrect.')
        return None
        

def extractMetadataPapers(inputFile):
    df, dfwrite = readFiles(inputFile)
    unique_dois = df['Id Documento'].astype(str).unique().tolist()
    for doi in unique_dois:  
        is_correct, doi = validar_doi(doi) #valida si existe el artículo con su DOI
        if is_correct:
            title, abstract, author = extractMetadata(doi)
            data = outputFile_json(doi, title, abstract, author)
            #print(data)
        else:
            print(f'--> DOI {doi} is incorrect.')