# Ai_API_unesco

## Spanish
Este repositorio contiene todo lo necesario para lanzar una API con [FastAPI](https://fastapi.tiangolo.com/) que utiliza dos proveedores distintos
de LLMs ([vllm](https://docs.vllm.ai/en/latest/) y [openrouter](https://openrouter.ai/)) y clasifica artículos científicos en las categorías de investigación definidas por la UNESCO.

### Instalación y Configuración
- Clonar este repositorio.
- Crear y utilizar un entorno virtual (Recomendado) con python 3.10. Puede utilizar [miniconda3](https://www.anaconda.com/docs/getting-started/miniconda/install#quickstart-install-instructions), [venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) u otros.
- Moverse hasta la raíz del repositorio clonado e instalar las librerías y paquetes necesarios con
  
      pip install -r requirements.txt
  
- Renombrar el archivo "config_yaml.txt" por "config.yaml" dentro del directorio "my_config".
- Modificar el nuevo archivo "config.yaml" con la información sobre su proveedor de servicios de LLMs según las instrucciones del mismo archivo.
- Lanzar la API con el siguiente comando:

      uvicorn v2_3_main:app --reload --host 0.0.0.0 --port 8001

  Siéntase libre de cambiar la información del **host** y el **port**.
  
### Instalación y Configuración

## English
This repository contains everything needed to launch an API with  [FastAPI](https://fastapi.tiangolo.com/) that uses two different LLM providers ([vllm](https://docs.vllm.ai/en/latest/) and [openrouter](https://openrouter.ai/)) and classifies scientific articles into the research categories defined by UNESCO.

Steps to launch the API:
