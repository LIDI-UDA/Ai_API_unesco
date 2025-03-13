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

### Instalación
- Clonar este repositorio.
- Crear y utilizar un entorno virtual (Recomendado) con python 3.10. Puede utilizar [miniconda3](https://www.anaconda.com/docs/getting-started/miniconda/install#quickstart-install-instructions), [venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) u otros.
- Moverse hasta la raíz del repositorio clonado e instalar las librerías y paquetes necesarios con
  
      pip install -r requirements.txt
  
- Renombrar el archivo "config_yaml.txt" por "config.yaml" dentro del directorio "my_config".
- Modificar el nuevo archivo "config.yaml" con la información sobre su proveedor de servicios de LLMs según las instrucciones del mismo archivo.
- Lanzar la API con el siguiente comando:

      uvicorn v2_3_main:app --reload --host 0.0.0.0 --port 8001

  Siéntase libre de cambiar la información del **host** y el **port**.
  
### Configuración de vLLM
- Una vez que ha instalado exitosamente la librería siguiendo las [instrucciones](https://docs.vllm.ai/en/latest/getting_started/installation.html) oficiales según las características de su entorno; se debe levantar un servidor que gestione las peticiones al LLM. Por ejemplo, si desea utilizar el modelo libre [meta-llama/Llama-3.1-8B-Instruct](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct) en su entorno local, ejecute:

      CUDA_VISIBLE_DEVICES=0 vllm serve meta-llama/Llama-3.1-8B-Instruct --dtype auto --device cuda --trust-remote-code --load_format bitsandbytes --gpu-memory-utilization 0.7 --max-seq-len-to-capture 9216 --max-model-len 9216 --disable-log-stats --disable-log-requests --tensor-parallel-size 1 --quantization bitsandbytes --enforce-eager

  Esto levantará un servidor con la interfaz de [OpenAI](https://platform.openai.com/docs/overview) en el puerto **8000** por defecto.
  Puede revisar y modificar los parámetros del servidor vLLM con su [documentación](https://docs.vllm.ai/en/latest/serving/engine_args.html).
    - Nota: Si no está seguro de qué modelo utilizar, debe tomar en cuenta los recuros **hardware** de su organización, [aquí](https://docs.unsloth.ai/get-started/beginner-start-here/unsloth-requirements#approximate-vram-requirements-based-on-model-parameters) puede consultar una aproximación del uso de VRAM de acuerdo al tamaño de un LLM.

### Configuración de OpenRouter
- Para utilizar OpenRouter como proveedor, basta con [obtener](https://openrouter.ai/) las credenciales necesarias en su plataforma y definirlas correctamente en el archivo **config.yaml**. Openouter también utiliza la interfaz de [OpenAI](https://platform.openai.com/docs/overview) para realizar consultas al LLM.

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
      
- Código de ejemplo con **requests** en python:

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
      
- Código de ejemplo con **requests** en python:

      import requests

      url = "[http://127.0.0.1:8001/classify/](http://127.0.0.1:8001/classify_by_doi/)"
      doi_prueba = '10.48550/arXiv.2403.02159'
      data = {"doi": doi_prueba}

      response = requests.post(url, json=data)
      print(response.text)
  
## English
This repository contains everything needed to launch an API with  [FastAPI](https://fastapi.tiangolo.com/) that uses two different LLM providers ([vllm](https://docs.vllm.ai/en/latest/) and [openrouter](https://openrouter.ai/)) and classifies scientific articles into the research categories defined by UNESCO.

Steps to launch the API:

# Título principal

Aquí hay algo de contenido en la sección de ejemplo.

---

[Ir a la sección de ejemplo](#classify)

