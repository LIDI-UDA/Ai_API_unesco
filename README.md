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
