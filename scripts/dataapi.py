import json_repair
import json
import difflib

'''
Clase que contiene lectura de datos desde archivos JSON, filtros y busquedas sobre estos datos
'''
class DataAPI:


    '''
    Lee un JSON de un archivo
    Input: Path del archivo
    Output: Objeto JSON 
    '''
    def load_json_from_file(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                print(content)
        except UnicodeDecodeError as e:
            print(f"Error decoding file: {e}")
            # Handle the error, e.g., by reading with a different encoding or skipping problematic parts
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read()
                print("File read with fallback encoding (latin-1):")
                #print(content)

        try:
            contentJson=json_repair.loads(content)
        except json.JSONDecodeError as e:
            print('Data JSON parse error')
            contentJson={}

        return contentJson

    

    '''
    Realiza la busqueda del top n match dados los parametros de busqueda
    Input: JSON con datos de busqueda
    Output: listado JSON de los topn mejores matches encontrado en los datos
    '''
    def find_best_matches(search_params, catalog, top_n=5):
        matches = []
        
  
        for item in catalog:
            if('model' in search_params and search_params['model']):
                score_model = difflib.SequenceMatcher(None, search_params['model'].lower(), item['model'].lower()).ratio()
            else:
                score_model=0
            if('make' in search_params and search_params['make']):
                score_make = difflib.SequenceMatcher(None, search_params['make'].lower(), item['make'].lower()).ratio()
            else:
                score_make=0
            if('year' in search_params and search_params['year']):
                score_year = 1 if search_params['year'] == item['year'] else 0
            else:
                score_year=0
            if('version' in search_params and search_params['version']):
                score_version = difflib.SequenceMatcher(None, search_params['version'].lower(), item['version'].lower()).ratio()
            else:
                score_version=0

             # Handle range search for price
            max_price = search_params.get('maxprice', None)
            if max_price:
                try:
                    score_price = 1 if item['price'] <= max_price else 0
                except ValueError:
                    score_price=0
                
            else:
                score_price = 0
            

            total_score = (score_model + score_make + score_year + score_version+ score_price ) / 4
            
            matches.append((item, total_score))
        
        # Sort matches by total_score in descending order and take the top N
        best_matches = sorted(matches, key=lambda x: x[1], reverse=True)[:top_n]
        
        # Return only the car details, excluding the scores
        return [match[0] for match in best_matches]

    '''
    Calculo de planes de financiamiento de un auto
    Input: precio de auto y tasas de enganche, interes y plazos de 3 a 6 años
    Output: JSON con datos de planes de pago
    '''
    def calcular_plan_pagos(precio_auto, tasa_interes=0.10, min_anios=3, max_anios=6, enganche_porcentaje=0.20):
            planes_pagos = {}
            enganche_monto = precio_auto * enganche_porcentaje
            monto_financiado = precio_auto - enganche_monto
            for anios in range(min_anios, max_anios + 1):
                n_pagos = anios * 12
                tasa_mensual = tasa_interes / 12
                cuota_mensual = (monto_financiado * tasa_mensual) / (1 - (1 + tasa_mensual) ** -n_pagos)
                
                planes_pagos[anios] = {
                    "price": precio_auto,
                    "down_payment": enganche_monto,
                    "financed_amount": monto_financiado,
                    "interest_rate": tasa_interes,
                    "years": anios,
                    "monthly_amount": round(cuota_mensual, 2),
                    "total_amount": round(cuota_mensual * n_pagos, 2),
                    "total_interest": round(cuota_mensual * n_pagos - monto_financiado, 2)
                }
        
            return planes_pagos