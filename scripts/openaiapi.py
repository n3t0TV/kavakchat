from openai import OpenAI 
import os
import re
import json
import json_repair

with open("../config.json", 'r') as file:
    print('Loading api key')
    config_data = json.load(file)
    apikeystr=config_data["openaikey"]


'''
Realiza un chat prompt y regresa respuesta como texto
Input: prompt de systema y prompt de usuario
Output: resultado de prompt como texto
'''

def promptChatText(systemMessage,promptMessage):
  MODEL="gpt-4o"
  client = OpenAI(api_key=apikeystr)
  completion = client.chat.completions.create(
    model=MODEL,
    temperature=0.2,
    stop=None,
    messages=[
      {"role": "system", "content": systemMessage}, # <-- This is the system message that provides context to the model
      {"role": "user", "content": promptMessage}  # <-- This is the user message for which the model will generate a response
    ]
  )
  result=completion.choices[0].message.content
  return result

'''
Realiza un chat prompt y regresa respuesta como JSON
Input: prompt de systema y prompt de usuario
Output: resultado de prompt como JSON
'''

def promptChatJson(systemMessage,promptMessage):
  MODEL="gpt-4o"
  client = OpenAI(api_key=apikeystr)
  completion = client.chat.completions.create(
    model=MODEL,
    temperature=0.1,
    stop=None,
    response_format={"type": "json_object"},
    messages=[
      {"role": "system", "content": systemMessage}, # <-- This is the system message that provides context to the model
      {"role": "user", "content": promptMessage}  # <-- This is the user message for which the model will generate a response
    ]
  )
  result=str(completion.choices[0].message.content)
  return result
'''
Parsea texto con JSONS (de un nivel) buscando coincidencias de {} y parseando el contenido
Input: Sting en formato JSOn a parsear
Output: Listado de objetos JSON encontrados
'''

def extract_json_objects(itemStringFinal):
    # Regular expression pattern to find JSON objects
    # print("***Extracting json object***")
  
    pattern = r"\{.*?\}"
    matches = re.findall(pattern, itemStringFinal, re.DOTALL)

    # Attempt to parse each match as JSON and return it
    json_objects = []
    for match in matches:
        try:
            json_objects.append(json_repair.loads(match))
        except json.JSONDecodeError:
            print("Json decode error", match)
            error_description = str(e)
          
        except Exception as e:
            print("Error: parsing JSON object!!")
            error_description = str(e)
            print(error_description)
            print("-----")
            print(match)
            print("-----")
    print("***Finished extracting json object***")
    return json_objects



