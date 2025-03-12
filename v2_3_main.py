import json
import yaml
from openai import OpenAI
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from my_endpoints import clasificacion_articulos
from my_endpoints import extraccion_metadata

# Carga de datos y configuraciones
with open("my_config/config.yaml", "r") as file:
    config = yaml.safe_load(file)
    
with open(config["data_paths"]["unesco_options"], "r", encoding="utf-8") as f:
    unesco_options = json.load(f)

with open(config["data_paths"]["unesco_search"], "r", encoding="utf-8") as f:
    unesco_search = json.load(f)

if config["provider"] == "openrouter":
    client = OpenAI(
      base_url=config["openrouter_config"]["openrouter_base_url"],
      api_key=config["api_keys"]["openrouter"]
    )
    config["dynamic_config"]["dynamic_model_name"] = config["openrouter_config"]["openrouter_model_name"] 
else:
    client = OpenAI(
      base_url=config["vllm_config"]["vllm_base_url"],
      api_key=config["api_keys"]["vllm"]
    )
    config["dynamic_config"]["dynamic_model_name"] = config["vllm_config"]["vllm_model_name"] 

# Inicializar API
app = FastAPI()

# Deshabilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Validación de datos para solicitudes del endpoint "classify"
class ArticleInput(BaseModel):
    title: str
    abstract: str = "[No abstract available]"

# Validación de datos para solicitudes del endpoint "classify_by_doi"
class DoiInput(BaseModel):
    doi: str

# Endpoint para clasificar un artículo
@app.post("/classify/")
async def classify_article(article: ArticleInput):
    result = clasificacion_articulos.classify_paper(article.title, 
                                                    article.abstract,
                                                    unesco_options,
                                                    unesco_search,
                                                    client,
                                                    config)
    return result

# Endpoint para extraer metadata a partir un artículo y clasificarlo
# utilizando su título y abstract (si existe)
@app.post("/classify_by_doi/")
async def get_metadata(doi: DoiInput):
    metadata = json.loads(extraccion_metadata.extractMetadataPaper(doi.doi,
                                                                   config))
    #print(metadata)
    classification = clasificacion_articulos.classify_paper(metadata['title'], 
                                                            metadata['abstract'],
                                                            unesco_options,
                                                            unesco_search,
                                                            client,
                                                            config)
    return classification
