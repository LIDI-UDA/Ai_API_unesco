from my_utils import chat_utils
from typing import Dict, List, Union

def ensure_valid_response(
    actual_opt: str, 
    messages: str, 
    valid_options: List[str], 
    client, 
    config: Dict[str, Union[Dict[str, str], str]]
) -> str:
    """
    Función que verifica si la respuesta proporcionada por el llm es válida.
    Si no lo es, intenta corregirla hasta un máximo de 2 intentos.
    
    Args:
    - actual_opt: La respuesta actual del LLM.
    - messages: El mensaje enviado al modelo de lenguaje.
    - valid_options: Opciones válidas para comparar la respuesta del modelo.
    - client: Cliente llm (vllm u openrouter) con interfaz de openAI.
    - config: Configuración (yaml) con varios parámetros.
    
    Retorna:
    - str: La respuesta válida del modelo o '0-0' si no se logra obtener una respuesta válida después de los intentos.
    """
    MAX_LLM_TRIES = 2
    TRIES_COUNTER = 0

    while actual_opt not in valid_options and TRIES_COUNTER < MAX_LLM_TRIES:
        corrective_prompt = chat_utils.get_corrective_prompt(actual_opt, messages)
        actual_opt = chat_utils.get_llm_answer(client, config["dynamic_config"]["dynamic_model_name"], corrective_prompt)
        TRIES_COUNTER += 1

    if actual_opt not in valid_options:
        return '0-0'
    
    return actual_opt

def classify_paper(
    title: str, 
    abstract: str, 
    unesco_options: Dict[str, List[str]], 
    unesco_search: Dict[str, Dict[str, str]], 
    client, 
    config: Dict[str, Union[Dict[str, str], str]]
) -> Dict[str, Union[str, List[str]]]:
    """
    Clasifica un artículo basado en su título y resumen usando las opciones predefinidas de la UNESCO.
    
    Args:
    - title: El título del artículo a clasificar.
    - abstract: El resumen del artículo a clasificar.
    - unesco_options: Diccionario de opciones de clasificación de la UNESCO.
    - unesco_search: Diccionario de búsqueda con detalles adicionales sobre las categorías.
    - client: Cliente llm (vllm u openrouter) con interfaz de openAI.
    - config: Configuración (yaml) con varios parámetros.
    
    Retorna:
    - dict: Diccionario con los códigos y nombres de las categorías de clasificación obtenidas, 
            o un mensaje indicando que no fue clasificado.
    """
    wrong_answer_flag = False 
    final_code_options = []    # Lista para almacenar los códigos de categoría final
    final_name_options = []    # Lista para almacenar los nombres de categoría final
    
    # Iterar sobre las opciones de UNESCO para consultas al llm
    for key, value in unesco_options.items():
        messages = chat_utils.get_main_prompt(title, abstract, key, is_final=False)
        actual_opt = chat_utils.get_llm_answer(client, config["dynamic_config"]["dynamic_model_name"], messages)
        valid_options = value + ['0-0']
        
        # Si la opción no es válida, intentar corregirla
        if actual_opt not in valid_options:
            actual_opt = ensure_valid_response(actual_opt, messages, valid_options, client, config)

        if actual_opt in value:
            final_code_options.append(actual_opt)
            final_name_options.append(unesco_search[actual_opt]["NOM_CAMPO_DETALLADO"])

    # Si no se clasificó en ninguna categoría, devolver "No clasificado"
    if not final_code_options:
        return {"category_code": "0-0", "category_name": "No clasificado"}

    final_options_string = chat_utils.generate_options_string(zip(final_code_options, final_name_options), is_multi=False)
    messages = chat_utils.get_main_prompt(title, abstract, final_options_string, is_final=True)
    actual_opt = chat_utils.get_llm_answer(client, config["dynamic_config"]["dynamic_model_name"], messages)
    
    if actual_opt not in final_code_options:
        actual_opt = ensure_valid_response(actual_opt, messages, final_code_options, client, config)
    
    return {
        "detailed_code": actual_opt,
        "detailed_name": unesco_search[actual_opt]["NOM_CAMPO_DETALLADO"],
        "specific_code": unesco_search[actual_opt]["COD_CAMPO_ESPECÍFICO"],
        "specific_name": unesco_search[actual_opt]["NOM_CAMPO_ESPECÍFICO"],
        "wide_code": unesco_search[actual_opt]["COD_CAMPO_AMPLIO"],
        "wide_name": unesco_search[actual_opt]["NOM_CAMPO_AMPLIO"],
        "other_options": [el + "-" + final_name_options[i] for i, el in enumerate(final_code_options)]
    }
