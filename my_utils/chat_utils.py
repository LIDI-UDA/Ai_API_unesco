from typing import List, Dict 

def get_sys_prompt() -> str:
    """
    Define y devuelve el prompt del sistema para el llm.
    
    Retorna:
        - str: El prompt del sistema.
    """
    return "You are an expert assistant in classifying scientific articles."

def get_main_prompt(title: str, abstract: str, key: str, is_final: bool = False) -> List[Dict[str, str]]:
    """
    Genera el prompt para clasificar un artículo en una categoría de investigación.
    
    Args:
        - title: El título del artículo.
        - abstract: El resumen del artículo.
        - key: Las categorías de investigación disponibles.
        - is_final: Indica si es la clasificación final o no.
    
    Retorna:
        - List[Dict[str, str]]: Lista de diccionarios con los roles del sistema y el usuario.
    """
    prompt = f"The title of the article is as follows:\n{title}\n"
    prompt += f"The abstract of the article is as follows:\n{abstract}\n"
    prompt += "Analyze the following research categories, which are in Spanish, and answer "
    prompt += "Which of the following research categories represents the article?\n"
    prompt += f"{key}\n Respond only with the exact category code. "
    prompt += "Example response format: '1-11A'."
    if not is_final:
        prompt += "If no category is suitable, respond with the code: '0-0'."

    return [
        {"role": "system", "content": get_sys_prompt()},
        {"role": "user", "content": prompt}
    ]
    

def get_corrective_prompt(actual_opt: str, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Genera un prompt de correción si la respuesta proporcionada no es válida.
    
    Args:
        - actual_opt: La respuesta incorrecta proporcionada por el modelo.
        - messages: Lista del último mensaje previo.
    
    Retorna:
        - List[Dict[str, str]]: La lista de mensajes con la instrucción de correción.
    """
    corrective_prompt = "Your answer: '" + actual_opt + "' is not among the available options "
    corrective_prompt += "or does not meet the response format. Please review the information and respond "
    corrective_prompt += "only with the exact category code. Example response format: '1-11A'."
    
    corr_messages = messages.copy()
    corr_messages.append({
        "role": "assistant", "content": actual_opt,
        "role": "user", "content": corrective_prompt
    })
    
    return corr_messages


def get_llm_answer(client, model: str, messages: List[Dict[str, str]]) -> str:
    """
    Obtiene la respuesta del llm con la interfaz de openAI.
    
    Args:
        - client: Cliente llm (vllm u openrouter) con interfaz de openAI.
        - model: El nombre del modelo a utilizar.
        - messages: Los mensajes que se envían al llm (lista de diccionarios).
    
    Retorna:
        - str: La respuesta del modelo en formato de texto.
    """
    answer = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.8,
        extra_body={
            'repetition_penalty': 1,
            'top_p': 1,
            #'frequency_penalty': 0,
            #'presence_penalty': 0,
            #'top_k': 0,
            #'do_sample': True,
            #'seed':42,
            'max_tokens': 64,
        })
    
    return answer.choices[0].message.content.strip()


def cut_messages(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Corta y obtiene los dos últimos mensajes de la lista de mensajes.
    
    Args:
        - messages: Lista de mensajes a modificar (lista de diccionarios).
    
    Retorna:
        List[Dict[str, str]]: Lista de mensajes cortados (sin los dos últimos).
    """
    return messages[:-2]

def generate_options_string(ready_zip: List[tuple], is_multi: bool = False) -> str:
    """
    Genera una cadena de texto que lista las opciones disponibles para clasificar un artículo.
    
    Args:
        - ready_zip: Lista de tuplas con código, nombre y descripción de las opciones.
        - is_multi: Si las opciones incluyen descripción.
    
    Retorna:
        - str: La cadena con las opciones generadas.
    """
    options = ""
    if is_multi:
        for cod, el, desc in ready_zip:
            options += "###########\n"
            options += f"- Code: {str(cod)}\n"
            options += f"- Name: {str(el)}\n"
            options += f"- Description: {str(desc)}\n\n"
    else:
        for cod, el in ready_zip:
            options += "###########\n"
            options += f"- Code: {str(cod)} "
            options += f"- Name: {str(el)}\n"

    return options.strip()
    

def get_client_model_name(client) -> str:
    """
    Obtiene el nombre del modelo disponible en el cliente.
    
    Args:
        - client: Cliente llm (vllm u openrouter) con interfaz de openAI.
    
    Retorna:
        - str: El nombre del modelo.
    """
    models = client.models.list()
    return models.data[0].id