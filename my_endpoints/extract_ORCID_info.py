# BETA VERSION
import json
import requests
import re
import time
from crossref.restful import Works
from crossref.restful import Journals
from bs4 import BeautifulSoup
from idutils import is_doi
import pandas as pd
from tqdm import tqdm
from my_endpoints.extract_DOI_info import Extract_DOI_info

class Extract_ORCID_info:
    def __init__(self, orcid, config):
        self.orcid = orcid
        self.config = config
    
    def extracInfoORCID(self, df_writeByORCID=''):
        '''
        Extract information from papers through ORCID

        Parameters:
            ORCID (string): Unique identifier of the scientifics.

        Returns:
            list[str]: String list of works information.
            
        '''
        # URL base de la API de ORCID
        BASE_URL = f'https://pub.orcid.org/v3.0/{self.orcid}'

        # Headers para la autenticación
        headers = {
            'Accept': 'application/json',
        }

        # OAuth 2.0 authentication (if required)
        # Note: Authentication is not always required to access public data.
        # If you need to access private data, you must implement the OAuth 2.0 flow.

        # Make the GET request
        response = requests.get(BASE_URL, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:        
            # Convert the response to JSON
            data = response.json()
            # Extract basic profile information
            orcid_profile = data.get('person', {})
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
            name = (f"{family_name.replace('N/A','').upper()} {given_name.upper()}")

            # Extraer afiliaciones
            employments = data.get('activities-summary', {}).get('employments', {}).get('employment-summary', [])
            if employments:
                for employment in employments:
                    org_name = employment.get('organization', {}).get('name', 'N/A')
                    start_date = employment.get('start-date', {}).get('year', {}).get('value', 'N/A')
                    end_date = employment.get('end-date', {}).get('year', {}).get('value', 'N/A')
                    #print(f"- {org_name} ({start_date} - {end_date})")
            
            # Extraer publicaciones
            works = data.get('activities-summary', {}).get('works', {}).get('group', [])
            publications_array =[]
            if works:
                #for work in works:
                for work in tqdm(works, total= len(works), desc=f"Works from {self.orcid}", unit=" files", ncols=100, colour='blue', position=1, leave=False):
                    publications = {}
                    work_summary = work.get('work-summary', [{}])[0]
                    title = work_summary.get('title', {}).get('title', {}).get('value', 'N/A')
                    publication_date = work_summary.get('publication-date', {})
                    
                    if publication_date:  # Check if publication_date is not empty
                        year = publication_date.get('year', {}).get('value', 'N/A') if publication_date.get('year') else 'N/A'
                        month = publication_date.get('month', {}).get('value', 'N/A') if publication_date.get('month') else 'N/A'
                        day = publication_date.get('day', {}).get('value', 'N/A') if publication_date.get('day') else 'N/A'
                        formatted_date = f"{year}-{month}-{day}"
                    else:
                        formatted_date = 'N/A'  # If there is no publication_date
                    
                    publication_type = work_summary.get('type', 'N/A')
                    
                    # Check if DOI exists
                    external_ids = work_summary.get('external-ids', {}).get('external-id', [])
                    doi = 'N/A'
                    for external_id in external_ids:
                        if external_id.get('external-id-type') == 'doi':
                            doi = external_id.get('external-id-value', 'N/A')
                            break
                    
                    if (bool(re.match(r"^\d{4}", formatted_date)) and (doi != 'N/A')):
                        _doi = (f"{doi if doi != 'N/A' else 'Not available'}")
                        info_doi = Extract_DOI_info(_doi, self.config)
                        _title, author, _affiliation, abstract, issn, _issued, _published = info_doi.extractMetadata()
                        publications['titulo'] = title
                        new_row = [self.orcid, name, _doi, title, abstract, author, publication_type,  _issued, _published]
                        df_writeByORCID = pd.concat([df_writeByORCID, pd.DataFrame([new_row], columns=df_writeByORCID.columns)], ignore_index=True)
            return df_writeByORCID 
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
