# Ai_API_unesco

[english](#english) | [spanish](#spanish)

## Spanish
Este repositorio contiene todo lo necesario para lanzar una API con [FastAPI](https://fastapi.tiangolo.com/) que utiliza dos proveedores distintos
de LLMs ([vLLM](https://docs.vllm.ai/en/latest/) y [openrouter](https://openrouter.ai/)) y clasifica artículos científicos en las categorías de investigación definidas por la UNESCO.
- [vLLM](https://docs.vllm.ai/en/latest/)
  es una biblioteca de código abierto lista para producción diseñada para optimizar el uso de LLMs.
  vLLM permite que los modelos de lenguaje se ejecuten de manera más rápida y eficiente, además de soportar arquitecturas distribuidas y LLMs de
  código abierto, e.g. [HuggingFace](https://huggingface.co/).
  Si está interesado en utilizar vLLM como proveedor, debe considerar sus recursos de hardware y seguir las [instrucciones](https://docs.vllm.ai/en/latest/getting_started/installation.html) de instalación.

- [OpenRouter ](https://openrouter.ai/)
  es una plataforma de código abierto diseñada para la creación y gestión de APIs para modelos de lenguaje, específicamente orientada a
  facilitar la integración y el uso de modelos de LLMs.
  Si está interesado en utilizar OpenRouter como proveedor, revise su [documentación](https://openrouter.ai/docs/quickstart).

### Requerimientos del sistema
- Ubuntu server 22.04

### Instalación
- Clonar este repositorio.
- Crear y utilizar un entorno virtual (Recomendado) con python 3.10. Puede utilizar [miniconda3](https://www.anaconda.com/docs/getting-started/miniconda/install#quickstart-install-instructions), [venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) u otros.
- Moverse hasta la raíz del repositorio clonado e instalar las librerías y paquetes necesarios con:
  
      pip install -r requirements.txt
  
- Renombrar el archivo "config_yaml.txt" por "config.yaml" dentro del directorio "my_config".
- Modificar el nuevo archivo "config.yaml" con la información sobre su proveedor de servicios de LLMs según las instrucciones del mismo archivo.
- Lanzar la API con el siguiente comando:

      fastapi run v2_3_main.py --host 0.0.0.0 --port 8001

  Siéntase libre de cambiar la información del **host** y el **port**.
  
### Configuración de vLLM
- Una vez que ha instalado exitosamente la librería siguiendo las [instrucciones](https://docs.vllm.ai/en/latest/getting_started/installation.html) oficiales según las características de su entorno; se debe levantar un servidor que gestione las peticiones al LLM. Por ejemplo, si desea utilizar el modelo libre [meta-llama/Llama-3.1-8B-Instruct](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct) en su entorno local, ejecute:

      CUDA_VISIBLE_DEVICES=0 vllm serve meta-llama/Llama-3.1-8B-Instruct --dtype auto --device cuda --trust-remote-code --load_format bitsandbytes --gpu-memory-utilization 0.7 --max-seq-len-to-capture 9216 --max-model-len 9216 --disable-log-stats --disable-log-requests --tensor-parallel-size 1 --quantization bitsandbytes --enforce-eager

  Esto levantará un servidor con la interfaz de [OpenAI](https://platform.openai.com/docs/overview) en el puerto **8000** por defecto.
  Puede revisar y modificar los parámetros del servidor vLLM con su [documentación](https://docs.vllm.ai/en/latest/serving/engine_args.html).
    - Nota: Si no está seguro de qué modelo utilizar, debe tomar en cuenta los recuros **hardware** de su organización, [aquí](https://docs.unsloth.ai/get-started/beginner-start-here/unsloth-requirements#approximate-vram-requirements-based-on-model-parameters) puede consultar una aproximación del uso de VRAM de acuerdo al tamaño de un LLM.

### Configuración de OpenRouter
- Para utilizar OpenRouter como proveedor, basta con [obtener](https://openrouter.ai/) las credenciales necesarias en su plataforma y definirlas correctamente en el archivo **config.yaml**. OpenRouter también utiliza la interfaz de [OpenAI](https://platform.openai.com/docs/overview) para realizar consultas al LLM.

### Endpoints
Al lanzar el servicio, estarán disponibles los siguientes **Endpoints**:

#### /classify/
- Descripción: Este endpoint se encarga de clasificar un artículo a partir de su título y resumen (abstract), utilizando un LLM y las categorías predefinidas de la UNESCO. El título y el resumen son enviados como parámetros y el modelo devuelve información sobre la clasificación del artículo.
- Método: **POST**
- Datos de entrada:
    - Tipo de dato: **JSON**
    - Estructura esperada:

          { "title": "Título del artículo",
            "abstract": "Resumen o abstract del artículo"
          }
      
    - Nota: El campo title (título) es obligatorio, mientras que el campo abstract (resumen) es opcional; si no se incluye, la clasificación se realizará solo con el título del artículo.
- Datos de salida:
    - Tipo de dato: **JSON**
    - Ejemplo de salida:

          {"detailed_code":"3-35A",
           "detailed_name":"Física",
           "specific_code":"3-5A",
           "specific_name":"Ciencias físicas",
           "wide_code":"05-A",
           "wide_name":"Ciencias naturales, matemáticas y estadísticas",
           "other_options":["3-35A-Física"]
          }
      
- Código de ejemplo con **requests** en Python:

      import requests

      url = "http://127.0.0.1:8001/classify/"
      data = {"title": "Search for Gamma-Ray Spectral Lines from Dark Matter Annihilation up to 100 TeV toward the Galactic Center with MAGIC.", 
              "abstract": "[No abstract available]"
             }

      response = requests.post(url, json=data)
      print(response.text)

#### /classify_by_doi/
- Descripción: Este endpoint se encarga de clasificar un artículo a partir de un **doi** utilizando un LLM y las categorías predefinidas de la UNESCO. El **doi** es enviado como parámetro y el modelo devuelve información sobre la clasificación del artículo.
- Método: **POST**
- Datos de entrada:
    - Tipo de dato: **JSON**
    - Estructura esperada:

          { "doi": "DOI del artículo, e.g: 10.48550/arXiv.2403.02159"}
      
    - Nota: El campo **doi** es obligatorio.
- Datos de salida:
    - Tipo de dato: **JSON**
    - Ejemplo de salida:

          {"detailed_code":"3-35A",
           "detailed_name":"Física",
           "specific_code":"3-5A",
           "specific_name":"Ciencias físicas",
           "wide_code":"05-A",
           "wide_name":"Ciencias naturales, matemáticas y estadísticas",
           "other_options":["3-35A-Física"]
          }
      
- Código de ejemplo con **requests** en Python:

      import requests

      url = "[http://127.0.0.1:8001/classify/](http://127.0.0.1:8001/classify_by_doi/)"
      doi_prueba = '10.48550/arXiv.2403.02159'
      data = {"doi": doi_prueba}

      response = requests.post(url, json=data)
      print(response.text)

#### /extract_metadata_paper_by_DOI/
- Descripción: Este endpoint se encarga de obtener toda información relevante de un artículo a partir del **DOI**, dando la opción de devolver con un **JSON** o en escribirlo en un archivo JSON. 
- Método: **POST**
- Datos de entrada:
    - Tipo de dato: **JSON**
    - Estructura esperada:

          {"doi" : DOI del artículo, e.g: '10.3390/app15041934' , "write2File" : False}
      
    - Nota: El campo **DOI** es obligatorio, y el campo **write2File** dejarlo en False por defecto.
- Datos de salida:
    - Tipo de dato: **JSON**
    - Ejemplo de salida:

           {
            "DOI":"10.3390/app15041934",
            "Title":"Evaluating the Impact of Membership Functions and Defuzzification Methods in a Fuzzy System: Case of Air Quality Levels",
            "Authors":"Juan Fernando Lima; Andrés Patiño-León; Marcos Orellana; Jorge Luis Zambrano-Martinez",
            "Affiliation":"Computer Science Research & Development Laboratory (LIDI), Universidad del Azuay, Cuenca 010204, Ecuador; Computer Science Research & Development Laboratory (LIDI), Universidad del Azuay, Cuenca 010204, Ecuador. Facultad de Informática, Universidad Nacional de la Plata, La Plata 1900, Argentina; Computer Science Research & Development Laboratory (LIDI), Universidad del Azuay, Cuenca 010204, Ecuador; Computer Science Research & Development Laboratory (LIDI), Universidad del Azuay, Cuenca 010204, Ecuador",
            "Abstract":"Since the 1960s, fuzzy logic has contributed to developing control systems based on modeling nonlinear problems using linguistic terms and inference rules. In the air quality domain, fuzzy logic has allowed us to tackle inferential environmental systems that are tolerant of human uncertainty and aimed at decision support. These systems are composed of three processes: a function to define a membership degree of the system’s value concerning a human linguistic term; an inference engine for decision making; and defuzzification methods focused on transforming the aggregated fuzzy set into a real-world value. Over the years, multiple mathematical formulas have been proposed to enrich membership functions or defuzzification methods; however, their use is                            sometimes limited to classical functions, limiting the importance of other proposals. This paper aims to evaluate the impact of the transformation functions in an air quality fuzzy system. The results of this work prove that the defuzzification method has a more significant effect than the others. It should be noted that by considering these results or their evaluation method, the quality of future fuzzy systems can be improved in both industrial and academic domains.",
            "issn":"2076-3417",
            "Issued":"2025-2-13",
            "Published":"2025-2-13"
          }
      
- Código de ejemplo con **requests** en Python:

      import requests

      url = url = "http://127.0.0.1:8001/extract_metadata_paper_by_DOI/"
      doi = '10.3390/app15041934'
      
      data ={
              "doi" : '10.3390/app15041934',
              "write2File" : False
            }

      response = requests.post(url, json=data)
      print(response.text)

#### /search_papers_by_orcid/
- Descripción: Este endpoint se encarga de obtener toda información relevante de un artículo a partir del **DOI**, dando la opción de devolver con un **JSON** o en escribirlo en un archivo JSON. 
- Método: **POST**
- Datos de entrada:
    - Tipo de dato: **JSON**
    - Estructura esperada:

          {"orcid" : ORCID del investigador, e.g: '0000-0002-5339-7860' , "write2File" : False}

   - Nota: El campo **DOI** es obligatorio, y el campo **write2File** dejarlo en False por defecto.
- Datos de salida:
    - Tipo de dato: **JSON**
    - Ejemplo de salida:


          [
            {
              "ORCID":"0000-0002-5339-7860",
              "Name":"ZAMBRANO-MARTINEZ JORGE LUIS",
              "DOI":"10.3390/app15041934",
              "Title":"Evaluating the Impact of Membership Functions and Defuzzification Methods in a Fuzzy System: Case of Air Quality Levels","Abstract":"Since the 1960s, fuzzy logic has contributed to developing control systems based on modeling nonlinear problems using linguistic terms and inference rules. In the air quality domain, fuzzy logic has allowed us to tackle inferential environmental systems that are tolerant of human uncertainty and aimed at decision support. These systems are composed of three processes: a function to define a membership degree of the system’s value concerning a human linguistic term; an inference engine for decision making; and defuzzification methods focused on transforming the aggregated fuzzy set into a real-world value. Over the years, multiple mathematical formulas have been proposed to enrich membership functions or defuzzification methods; however, their use is sometimes limited to classical functions, limiting the importance of other proposals. This paper aims to evaluate the impact of the transformation functions in an air quality fuzzy system. The results of this work prove that the defuzzification method has a more significant effect than the others. It should be noted that by considering these results or their evaluation method, the quality of future fuzzy systems can be improved in both industrial and academic domains.",
              "Authors":"Juan Fernando Lima; Andrés Patiño-León; Marcos Orellana; Jorge Luis Zambrano-Martinez",
              "Publication type":"journal-article",
              "Issued":"2025-2-13",
              "Published":"2025-2-13"
            },
            {  
              "ORCID":"0000-0002-5339-7860",
              "Name":"ZAMBRANO-MARTINEZ JORGE LUIS",
              "DOI":"10.5281/zenodo.14448094",
              "Title":"Data Visualization Model for Multi-party Analysis and Strategic Decision-Making in International Trade",
              "Abstract":"This paper presents a detailed analysis of Ecuador&rsquo;s non-oil exports over ten years. The study was performed using the SPEM methodology and data-cleaning processes. The results highlight a notable coherence in analyzing the most relevant export items and the main trading partners, providing essential information for strategic decision-making. Furthermore, recommendations related to the technical conditions necessary to achieve precise and accurate communication through data visualization were considered, and adequate answers to the questions generated in the business knowledge stage contributed to the users&rsquo; knowledge. Furthermore, the study suggests incorporating import data to enhance the analysis and provide a foundation for future research in this area.",
              "Authors":"Molina Alarcón, Inés Paola; Tonon Ordóñez, Luis Bernardo; Zambrano-Martinez, Jorge Luis; Orellana, Marcos",
              "Publication type":"journal-article",
              "Issued":null,
              "Published":"2025-01-07"
            },
            {
              "ORCID":"0000-0002-5339-7860",
              "Name":"ZAMBRANO-MARTINEZ JORGE LUIS",
              "DOI":"10.1007/978-3-031-75431-9_9",
              "Title":"Automatic Parking Space Segmentation Using K-Means Clustering and Image Processing Techniques",
              "Abstract":"Proper management of parking spaces is essential in urban environments. This study proposes an approach for parking space segmentation using the K-means algorithm and the OpenCV library. The main objective is to determine the trapezoid describing the parking area by analyzing data previously collected from multiple photographs. These images contain several vehicles parked in different dispositions and moments in time. For this, the coordinates of the four leading edges that compose each car were considered. The previously obtained data were used to estimate the trapezoid defining each photograph’s parking zone. This approach combines segmentation and image processing techniques to delimit parking spaces in urban environments.",
              "Authors":"Anthony Xavier Romero Gonzalez; Kevin Sebastian Campoverde Ambrosi; Patricio Eduardo Ramon Celi; Alexandra Bermeo; Marcos Orellana; Jorge Luis Zambrano-Martinez; Patricio Santiago García-Montero",
              "Publication type":"book-chapter",
              "Issued":"2024-10-10",
              "Published":"2024-10-10"
            }
          ]
- Código de ejemplo con **requests** en Python:
  
      url = "http://127.0.0.1:8001/search_papers_by_orcid/"
      
      data ={
          "inputFile" : '',
          "orcid" : "0000-0002-5339-7860",
          "write2File" : False
      }
      
      response = requests.post(url, json=data)
      print(response.text)

#### /seach_authors_by_affiliation/
- Descripción: Este endpoint se encarga de obtener todos los autores que están dentro de la afiliación colocada. En el caso que se desea realizar una búsqueda completa, donde se extrae la información del autor y los artículos realizados con la afiliación colocada, es necesario activar **searchFull**, y se puede discernir entre fechas (año-mes).
- Método: **POST**
- Datos de entrada:
    - Tipo de dato: **JSON**
    - Estructura esperada:

          {
            "affiliation" : Afiliación a buscar, e.g: 'Universidad del Azuay',
            "searchFull" : False,
            "from_date" : '2024-11',
            "to_date" : '2024-12',
            "write2File" : False
          }
  - Nota: El campo **affiliation** es obligatorio, y los campo **searchFull**, **write2File** dejarlo en False por defecto.
- Datos de salida:
    - Tipo de dato: **JSON**
    - Ejemplo de salida:

          [
            {
              "ORCID":"0000-0001-7191-2056",
              "Name":"MARTÍNEZ-URGILÉS, EMANUEL",
              "Affiliation":"Universidad del Azuay",
              "Status":"Active"
            },
            {
              "ORCID":"0000-0002-1276-9007",
              "Name":"RODAS, DIANA",
              "Affiliation":"Universidad del Azuay",
              "Status":"Active"
            },
            {
              "ORCID":"0000-0002-5992-9530",
              "Name":"MOSCOSO AMADOR, MARIA DE LOURDES",
              "Affiliation":"Universidad del Azuay",
              "Status":"Active"
            },
            {
              "ORCID":"0000-0001-5076-0372",
              "Name":"MEDINA ALTAMIRANO, SEBASTIÁN DIEGO ",
              "Affiliation":"Universidad del Azuay",
              "Status":"Innactive"
            },
            {
              "ORCID":"0000-0003-2108-412X",
              "Name":"TAPIA, EULALIA",
              "Affiliation":"Universidad del Azuay",
              "Status":"Innactive"
            }
          ]
      
- Código de ejemplo con **requests** en Python:

      url = "http://127.0.0.1:8001/seach_authors_by_affiliation/"

      data ={
          "affiliation" : "Universidad del Azuay",
          "searchFull" : False,
          "from_date" : '',
          "to_date" : '',
          "write2File" : False
      }

      response = requests.post(url, json=data)
      print(response.text)

#### Más endpoints en construcción...
### Aplicación UI en construcción...
  
## English
This repository contains everything needed to launch an API with [FastAPI](https://fastapi.tiangolo.com/) that uses two different LLM providers ([vLLM](https://docs.vllm.ai/en/latest/) and [openrouter](https://openrouter.ai/)) and classifies scientific articles into the research categories defined by UNESCO.
- [vLLM](https://docs.vllm.ai/en/latest/)
  is a production-ready open-source library designed to optimize the use of LLMs.
  vLLM allows language models to run faster and more efficiently, while also supporting distributed architectures and open-source LLMs, e.g., [HuggingFace](https://huggingface.co/).
  If you are interested in using vLLM as a provider, you should consider your hardware resources and follow the installation [instructions](https://docs.vllm.ai/en/latest/getting_started/installation.html).

- [OpenRouter ](https://openrouter.ai/)
  is an open-source platform designed for creating and managing APIs for language models, specifically aimed at facilitating the integration and use of LLMs.
  If you are interested in using OpenRouter as a provider, check out its [documentation](https://openrouter.ai/docs/quickstart).

### System requirements
- Ubuntu server 22.04

### Instalation
- Clone this repository.
- Create and use a virtual environment (Recommended) with Python 3.10. You can use [miniconda3](https://www.anaconda.com/docs/getting-started/miniconda/install#quickstart-install-instructions), [venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/), or others.
- Navigate to the root of the cloned repository and install the required libraries and packages with:
  
      pip install -r requirements.txt

- Rename the file "config_yaml.txt" to "config.yaml" inside the "my_config" directory.
- Edit the newly renamed "config.yaml" file with the information about your LLM service provider, following the instructions in the file.
- Launch the API with the following command:

      fastapi run v2_3_main.py --host 0.0.0.0 --port 8001

  Feel free to change the **host** y el **port** information.
  
### vLLM Configuration
- Once you have successfully installed the library following the official [instructions](https://docs.vllm.ai/en/latest/getting_started/installation.html) according to your environment's specifications, you need to start a server to handle requests to the LLM. For example, if you want to use the open model [meta-llama/Llama-3.1-8B-Instruct](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct) in your local environment, run:

      CUDA_VISIBLE_DEVICES=0 vllm serve meta-llama/Llama-3.1-8B-Instruct --dtype auto --device cuda --trust-remote-code --load_format bitsandbytes --gpu-memory-utilization 0.7 --max-seq-len-to-capture 9216 --max-model-len 9216 --disable-log-stats --disable-log-requests --tensor-parallel-size 1 --quantization bitsandbytes --enforce-eager

  This will start a server with the [OpenAI](https://platform.openai.com/docs/overview) interface on port **8000** by default.
  You can review and modify the vLLM server parameters in its [documentation](https://docs.vllm.ai/en/latest/serving/engine_args.html).
    - Note: If you are unsure which model to use, consider your organization's **hardware** resources. You can check an approximate VRAM usage based on the model size [here](https://docs.unsloth.ai/get-started/beginner-start-here/unsloth-requirements#approximate-vram-requirements-based-on-model-parameters).

### OpenRouter Configuration
- To use OpenRouter as a provider, simply [obtain](https://openrouter.ai/) the necessary credentials from its platform and set them correctly in the **config.yaml** file. OpenRouter also uses the [OpenAI](https://platform.openai.com/docs/overview) interface to query the LLM.

### Endpoints
Once the service is running, the following **Endpoints** will be available:

#### /classify/
- Description: This endpoint classifies an article based on its title and abstract, using an LLM and UNESCO’s predefined categories. The title and abstract are sent as parameters, and the model returns classification information.
- Method: **POST**
- Input Data:
    - Data type: **JSON**
    - Expected structure:

          { "title": "Paper title",
            "abstract": "Abstract or summary of the article."
          }
      
    - Note: The title field is required, while the abstract field is optional. If not provided, the classification will be performed using only the article's title.
- Output Data:
    - Data type: **JSON**
    - Example output:

          {"detailed_code":"3-35A",
           "detailed_name":"Física",
           "specific_code":"3-5A",
           "specific_name":"Ciencias físicas",
           "wide_code":"05-A",
           "wide_name":"Ciencias naturales, matemáticas y estadísticas",
           "other_options":["3-35A-Física"]
          }
      
- Example code using **requests** in Python:

      import requests

      url = "http://127.0.0.1:8001/classify/"
      data = {"title": "Search for Gamma-Ray Spectral Lines from Dark Matter Annihilation up to 100 TeV toward the Galactic Center with MAGIC.", 
              "abstract": "[No abstract available]"
             }

      response = requests.post(url, json=data)
      print(response.text)

#### /classify_by_doi/
- Description: This endpoint classifies an article based on a **DOI**, using an LLM and UNESCO’s predefined categories. The **DOI** is sent as a parameter, and the model returns classification information.
- Method: **POST**
- Input Data:
    - Data type: **JSON**
    - Expected structure:

          { "doi": "paper DOI, e.g: 10.48550/arXiv.2403.02159"}
      
    - Note: **doi** field is required.
- Output Data:
    - Data type: **JSON**
    - Example output:

          {"detailed_code":"3-35A",
           "detailed_name":"Física",
           "specific_code":"3-5A",
           "specific_name":"Ciencias físicas",
           "wide_code":"05-A",
           "wide_name":"Ciencias naturales, matemáticas y estadísticas",
           "other_options":["3-35A-Física"]
          }
      
- Example code using **requests** in Python:

      import requests

      url = "[http://127.0.0.1:8001/classify/](http://127.0.0.1:8001/classify_by_doi/)"
      test_doi = '10.48550/arXiv.2403.02159'
      data = {"doi": test_doi}

      response = requests.post(url, json=data)
      print(response.text)

#### /extract_metadata_paper_by_DOI/
- Description: This endpoint obtains all relevant information from an article through the **DOI**, giving the option to return it with a **JSON** or write it to a JSON file. 
- Method: **POST**
- Input:
    - Data type: **JSON**
    - Expected structure:

          {"doi" : DOI del artículo, e.g: '10.3390/app15041934' , "write2File" : False}
      
    - Note: The **DOI** is required, and the **write2File** field should be left False by default.
- Output data:
    - Data type: **JSON**
    - Example output:

           {
            "DOI":"10.3390/app15041934",
            "Title":"Evaluating the Impact of Membership Functions and Defuzzification Methods in a Fuzzy System: Case of Air Quality Levels",
            "Authors":"Juan Fernando Lima; Andrés Patiño-León; Marcos Orellana; Jorge Luis Zambrano-Martinez",
            "Affiliation":"Computer Science Research & Development Laboratory (LIDI), Universidad del Azuay, Cuenca 010204, Ecuador; Computer Science Research & Development Laboratory (LIDI), Universidad del Azuay, Cuenca 010204, Ecuador. Facultad de Informática, Universidad Nacional de la Plata, La Plata 1900, Argentina; Computer Science Research & Development Laboratory (LIDI), Universidad del Azuay, Cuenca 010204, Ecuador; Computer Science Research & Development Laboratory (LIDI), Universidad del Azuay, Cuenca 010204, Ecuador",
            "Abstract":"Since the 1960s, fuzzy logic has contributed to developing control systems based on modeling nonlinear problems using linguistic terms and inference rules. In the air quality domain, fuzzy logic has allowed us to tackle inferential environmental systems that are tolerant of human uncertainty and aimed at decision support. These systems are composed of three processes: a function to define a membership degree of the system’s value concerning a human linguistic term; an inference engine for decision making; and defuzzification methods focused on transforming the aggregated fuzzy set into a real-world value. Over the years, multiple mathematical formulas have been proposed to enrich membership functions or defuzzification methods; however, their use is                            sometimes limited to classical functions, limiting the importance of other proposals. This paper aims to evaluate the impact of the transformation functions in an air quality fuzzy system. The results of this work prove that the defuzzification method has a more significant effect than the others. It should be noted that by considering these results or their evaluation method, the quality of future fuzzy systems can be improved in both industrial and academic domains.",
            "issn":"2076-3417",
            "Issued":"2025-2-13",
            "Published":"2025-2-13"
          }
      
- Example code with **requests** in Python:

      import requests

      url = url = "http://127.0.0.1:8001/extract_metadata_paper_by_DOI/"
      doi = '10.3390/app15041934'
      
      data ={
              "doi" : '10.3390/app15041934',
              "write2File" : False
            }

      response = requests.post(url, json=data)
      print(response.text)


#### /search_papers_by_orcid/
- Description: This endpoint is responsible for obtaining all relevant information of an article from the **DOI**, giving the option to return it with a **JSON** or write it to a JSON file. 
- Method: **POST**
- Input:
    - Data type: **JSON**
    - Expected structure:

          {"orcid" : ORCID del investigador, e.g: '0000-0002-5339-7860' , "write2File" : False}

    - Note: The **DOI** is required, and the **write2File** field should be left False by default.
- Output data:
    - Data type: **JSON**
    - Example output:

          [
            {
              "ORCID":"0000-0002-5339-7860",
              "Name":"ZAMBRANO-MARTINEZ JORGE LUIS",
              "DOI":"10.3390/app15041934",
              "Title":"Evaluating the Impact of Membership Functions and Defuzzification Methods in a Fuzzy System: Case of Air Quality Levels","Abstract":"Since the 1960s, fuzzy logic has contributed to developing control systems based on modeling nonlinear problems using linguistic terms and inference rules. In the air quality domain, fuzzy logic has allowed us to tackle inferential environmental systems that are tolerant of human uncertainty and aimed at decision support. These systems are composed of three processes: a function to define a membership degree of the system’s value concerning a human linguistic term; an inference engine for decision making; and defuzzification methods focused on transforming the aggregated fuzzy set into a real-world value. Over the years, multiple mathematical formulas have been proposed to enrich membership functions or defuzzification methods; however, their use is sometimes limited to classical functions, limiting the importance of other proposals. This paper aims to evaluate the impact of the transformation functions in an air quality fuzzy system. The results of this work prove that the defuzzification method has a more significant effect than the others. It should be noted that by considering these results or their evaluation method, the quality of future fuzzy systems can be improved in both industrial and academic domains.",
              "Authors":"Juan Fernando Lima; Andrés Patiño-León; Marcos Orellana; Jorge Luis Zambrano-Martinez",
              "Publication type":"journal-article",
              "Issued":"2025-2-13",
              "Published":"2025-2-13"
            },
            {  
              "ORCID":"0000-0002-5339-7860","Name":"ZAMBRANO-MARTINEZ JORGE LUIS","DOI":"10.5281/zenodo.14448094",
              "Title":"Data Visualization Model for Multi-party Analysis and Strategic Decision-Making in International Trade",
              "Abstract":"This paper presents a detailed analysis of Ecuador&rsquo;s non-oil exports over ten years. The study was performed using the SPEM methodology and data-cleaning processes. The results highlight a notable coherence in analyzing the most relevant export items and the main trading partners, providing essential information for strategic decision-making. Furthermore, recommendations related to the technical conditions necessary to achieve precise and accurate communication through data visualization were considered, and adequate answers to the questions generated in the business knowledge stage contributed to the users&rsquo; knowledge. Furthermore, the study suggests incorporating import data to enhance the analysis and provide a foundation for future research in this area.",
              "Authors":"Molina Alarcón, Inés Paola; Tonon Ordóñez, Luis Bernardo; Zambrano-Martinez, Jorge Luis; Orellana, Marcos",
              "Publication type":"journal-article",
              "Issued":null,
              "Published":"2025-01-07"
            },
            {
              "ORCID":"0000-0002-5339-7860","Name":"ZAMBRANO-MARTINEZ JORGE LUIS","DOI":"10.1007/978-3-031-75431-9_9",
              "Title":"Automatic Parking Space Segmentation Using K-Means Clustering and Image Processing Techniques",
              "Abstract":"Proper management of parking spaces is essential in urban environments. This study proposes an approach for parking space segmentation using the K-means algorithm and the OpenCV library. The main objective is to determine the trapezoid describing the parking area by analyzing data previously collected from multiple photographs. These images contain several vehicles parked in different dispositions and moments in time. For this, the coordinates of the four leading edges that compose each car were considered. The previously obtained data were used to estimate the trapezoid defining each photograph’s parking zone. This approach combines segmentation and image processing techniques to delimit parking spaces in urban environments.",
              "Authors":"Anthony Xavier Romero Gonzalez; Kevin Sebastian Campoverde Ambrosi; Patricio Eduardo Ramon Celi; Alexandra Bermeo; Marcos Orellana; Jorge Luis Zambrano-Martinez; Patricio Santiago García-Montero",
              "Publication type":"book-chapter",
              "Issued":"2024-10-10",
              "Published":"2024-10-10"
            }
          ]
- Example code with **requests** in Python:
  
      url = "http://127.0.0.1:8001/search_papers_by_orcid/"
      
      data ={
          "inputFile" : '',
          "orcid" : "0000-0002-5339-7860",
          "write2File" : False
      }
      
      response = requests.post(url, json=data)
      print(response.text)
      
#### /seach_authors_by_affiliation/
- Description: This endpoint is responsible for retrieving all authors within the specified affiliation. If you want to perform a full search, which extracts author information and articles written with the specified affiliation, you must activate **searchFull**, and you can distinguish between dates (year-month).
- Method: **POST**
- Input:
    - Data type: **JSON**
    - Expected structure:

          {
            "affiliation" : Afiliación a buscar, e.g: 'Universidad del Azuay',
            "searchFull" : False,
            "from_date" : '2024-11',
            "to_date" : '2024-12',
            "write2File" : False
          }
  
    - Note: The **affiliation** is required, and the **searchFull**, **write2File** field should be left False by default.
- Output data:
    - Data type: **JSON**
    - Example output:

          [
            {
              "ORCID":"0000-0001-7191-2056",
              "Name":"MARTÍNEZ-URGILÉS, EMANUEL",
              "Affiliation":"Universidad del Azuay",
              "Status":"Active"
            },
            {
              "ORCID":"0000-0002-1276-9007",
              "Name":"RODAS, DIANA",
              "Affiliation":"Universidad del Azuay",
              "Status":"Active"
            },
            {
              "ORCID":"0000-0002-5992-9530",
              "Name":"MOSCOSO AMADOR, MARIA DE LOURDES",
              "Affiliation":"Universidad del Azuay",
              "Status":"Active"
            },
            {
              "ORCID":"0000-0001-5076-0372",
              "Name":"MEDINA ALTAMIRANO, SEBASTIÁN DIEGO ",
              "Affiliation":"Universidad del Azuay",
              "Status":"Innactive"
            },
            {
              "ORCID":"0000-0003-2108-412X",
              "Name":"TAPIA, EULALIA",
              "Affiliation":"Universidad del Azuay",
              "Status":"Innactive"
            }
          ]
      
- Example code with **requests** in Python:

      url = "http://127.0.0.1:8001/seach_authors_by_affiliation/"

      data ={
          "affiliation" : "Universidad del Azuay",
          "searchFull" : False,
          "from_date" : '',
          "to_date" : '',
          "write2File" : False
      }

      response = requests.post(url, json=data)
      print(response.text)

#### More endpoints coming soon...
#### UI App coming soon...
