import openaiapi

class Prompts:
    
    '''
    Prompt para clasifica mensaje de un usuario
    Input: Mensaje del usuario
    Output: JSON con tipo de solicitud
    '''
    def classifyPrompt(text,chatStory):
        print('Classifying prompt')
        resultString=openaiapi.promptChatJson(
                               f'Necesitas clasificar un texto enviado por un usuario para determinar el tipo de solicitud. El resultado sera utilizado para decidir el flujo en un sistema\
                               Genera un objeto JSON con las siguientes llaves: \
                               1. "tiposolicitud: Indica el tipo de solicitud dentro de las siguientes opciones" ["plataforma","pagos","sedes","catalogo","calculo","otro"] \
                               i. plataforma: mensajes que tienen que ver con que es kavak, a que se dedica la empresa, como funcina la plataforma, que solucion de negocio resuelve, dudas de la tecnologia, beneficios de comprar o vender en la plataforma, presencia en la industria\
                               ii. sedes: mensajes que tienen que ver con las sucursales, diraccion, ciudades en donde se tiene presencia. ubicacion de centros de inspeccion \
                               iii. pagos: mensajes que tienen que ver con planes de compra, planes de venta, formas de pago, medios de pago, planes de pago, proceso de pago, documentacion necesaria, periodos de prueba, devoluciones, garantias, servicios de mantenimiento,solicitud de compra \
                               iv. catalogo: mensajes que tengan que ver con  busquedas en catalogo de autos, modelos disponibles, marcas, año de fabricacion, version de autos, precios, dimensiones de autos \
                               v. otros: otros mensajes no incluidos en los puntos anteriores',
                               f'Clasifica el texto del usuario \
                               {text}'
                              )
        print(resultString)                    
        resJson = openaiapi.extract_json_objects(resultString)
        return resJson
    
    '''
    Prompt para responder informaciones genericas sobre empresa y plataforma
    Input: Texto con datos de la empresa y la plataforma
    Output: Texto con mejor respuesta para el usuario
    '''
    def platformPrompt(text,dataPlataforma,chatStory):

        resultString=openaiapi.promptChatTextStory(f'Eres un asistente de soporte al cliente para Kavak, que ofrece una plataforma para servicios de compra y venta de autos usados. Tu tarea es proporcionar respuestas precisas y utiles.\
                                              Reglas\
                                                i. Si no tienes información suficiente para responder a una consulta, indícalo claramente y sugiere al usuario que se comunique con un representante de soporte para obtener más ayuda.\
                                                ii. Si no estás seguro de la respuesta, no inventes.\
                                                iii. Descarta sugerir comunicarse con representate de soporte de Kavak \
                                                iv. Utiliza esta informacion de referencia:\
                                                {dataPlataforma}',
                                                chatStory.story
                              )
        print(resultString) 
        return resultString
    
    '''
    Prompt para responder informaciones genericas sobre sedes
    Input: Texto con datos de sedes de la empresa
    Output: Texto con mejor respuesta para el usuario
    '''
    def sitesPrompt(text,dataSites,chatStory):
        resultString=openaiapi.promptChatTextStory(f'Eres un asistente de soporte al cliente para Kavak, que ofrece una plataforma para servicios de compra y venta de autos usados. Tu tarea es proporcionar respuestas precisas y utiles.\
                                              Reglas\
                                                i. Si no tienes información suficiente para responder a una consulta, indícalo claramente y sugiere al usuario que se comunique con un representante de soporte para obtener más ayuda.\
                                                ii. Si no estás seguro de la respuesta, no inventes.\
                                                iii. Descarta sugerir comunicarse con representate de soporte de Kavak \
                                                iv. Utiliza esta informacion de referencia:\
                                                {dataSites}',
                                                chatStory.story
                              )
        print(resultString) 
        return resultString
    
    '''
    Prompt para responder informaciones genericas sobre pagos
    Input: Texto con datos de pagos de la empresa
    Output: Texto con mejor respuesta para el usuario
    '''
    def paymentPrompt(text,dataPayments,chatStory):
        resultString=openaiapi.promptChatText(f'Eres un asistente de soporte al cliente para Kavak, que ofrece una plataforma para servicios de compra y venta de autos usados. Tu tarea es proporcionar respuestas precisas y utiles.\
                                              Reglas\
                                                i. Si no tienes información suficiente para responder a una consulta, indícalo claramente y sugiere al usuario que se comunique con un representante de soporte para obtener más ayuda.\
                                                ii. Si no estás seguro de la respuesta,no inventes.\
                                                iii. Descarta sugerir comunicarse con representate de soporte de Kavak',
                                                f'Redacta una respuesta con la informacion de pagos \
                                                {dataPayments}'
                              )
        print(resultString) 
        return resultString
    
    '''
    Prompt para identificar la mejor opcion dentro de un catalogo con parametros de busqueda del usuario
    Input: JSON con catalogo de autos
    Output: Json indicando mejor opcion segun parametros de busqueda o si no existe
    '''
    def extraerParametrosPrompt(text,catalogo,chatStory):

        print('Searching car')
        
        resultString=openaiapi.promptChatJsonStory(f'Necesitas extraer los datos de busqueda de cada auto incluidos en la solicitud de un usuario \
                                                 Genera un objeto JSON con los datos de la busqueda  \
                                                i. model: Nombre del modelo string, por ejemplo (Mazda, Vento, Corolla, Journey)\
                                                ii. make: Fabricante string, por ejemplo (Ford, Toyota, Honda)\
                                                iii. year: Año integer, Por ejemplo (2019, 2019)\
                                                iv. version: Version, por ejemplo (Luxury,  Sedan, Adventure)\
                                                v. maxprice: Precio maximo float, por ejemplo (200000,180000)\
                                                Utilza solo los campos especificados en el listado anterior',
                                                chatStory.story                                             
                                            )
        
        resJson = openaiapi.extract_json_objects(resultString)
        print('**PARAMETROS*')
        print(resJson)
        return resJson
      
    def catalogPrompt(text,catalogo,chatStory):
        resultString=openaiapi.promptChatTextStory(f'Eres un asistente de soporte al cliente para Kavak, que ofrece una plataforma para servicios de compra y venta de autos usados. Tu tarea es proporcionar respuestas precisas y utiles.\
                                              Reglas\
                                                i. Si no tienes información suficiente para responder a una consulta, preguta por mas detalle.\
                                                ii. Descarta sugerir comunicarse con representate de soporte de Kavak \
                                                iii. Para formatos de montos utiliza $, elimina comas "," ',
                                                chatStory.story
                              )
        print(resultString) 
        return resultString
    

    def planPrompt(resJson,planJson,story):

        '''f'Considera el siguiente historial de la conversacion:\
                                                {story} \,
                                                Redacta una respuesta describiendo la informacion de la mejor opcion encontrada \
                                                {resJson} \
                                                '''
                               
        resultString=openaiapi.promptChatText(f'Eres un asistente de soporte al cliente para Kavak, que ofrece una plataforma para servicios de compra y venta de autos usados. Tu tarea es proporcionar respuestas precisas y utiles.\
                                              Reglas\
                                                i. Si no tienes información suficiente para responder a una consulta, indícalo claramente y sugiere al usuario que se comunique con un representante de soporte para obtener más ayuda.\
                                                ii. Si no estás seguro de la respuesta, no inventes\
                                                iii. Descarta sugerir comunicarse con representate de soporte de Kavak \
                                                iv. Para formatos de montos utiliza $, elimina comas "," ',
                                                story
                                                
                                                
                              )
        print(resultString) 
        return resultString