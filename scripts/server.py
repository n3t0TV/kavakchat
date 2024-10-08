
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import BaseServer
from  dataapi import DataAPI
import urllib.parse
from prompts import Prompts
import json_repair
import json
from twilio.rest import Client


class ChatStory:
    def __init__(self) -> None:
        self.story=[]
    def addStoryMessage(self,role,msg):
        self.story.append({"role": role, "content": msg})
        if(len(self.story)>5):#MAx 5 messages history to avoid huge prompts
            self.story=self.story[1:]
'''
Class to encapuslate all chat process flow
'''
class ChatService:
    def __init__(self):
        print('Chat service')

  
    '''
    Process a short catalog and searches for user parameters using the reference data
    Input: User text and a JSON containing catalog data parsed from csv
    Output: Message to respond the user
    '''
    def processCatalog(self,text,resJson,catalogo,chatStory):
        
        #To scale this prompt up to large datasets, extract search parameters from user text, then
        #filter catalog search in database using these parameters and finally use prompt to create message response using text provided by user
        if(resJson):
         
            
            bestmatches=[]
            for params in resJson:
                print('***JSON PARAMS***')
                print (params)
                bestmatches.extend(DataAPI.find_best_matches(params,catalogo))
            
            print(bestmatches)
            chatStory.addStoryMessage("assistant",f'Describe los autos del siguiente catalogo considerando la solciitud del usuario {catalogo}')
            resultString=Prompts.catalogPrompt(text,bestmatches,chatStory)
     
        else:
            resultString='No pude encontrar ninguna opcion que coincida con lo que buscas'

        return resultString
    
    
    '''
    Calculate the payment plans for the best option found in catalog
    Input: JSON with search parameters, cataloj JSON with all car data
    Output: Message describing user the car found and the payment plans 
    '''
    def processCalculo(self,resJson,catalogo,chatStory):
        
        print('JSON PARAMS')
        print(json.dumps(resJson))
      
        resultString='Por favor especifica los detalles del auto'
        if(resJson):
            resSearch = DataAPI.find_best_matches(resJson[0],catalogo,1)
            if(resSearch):
                print('**Resultado busqueda: ***')
                print(resSearch)
                print('Calculo a precio con tasa de interes 10 porciento a 3 años')
                planPagos=DataAPI.calcular_plan_pagos(float(resSearch[0]['price']),0.1,3,6,0.2)
                print('Plan de pagos')
                print(planPagos)
                chatStory.addStoryMessage("assistant",f'Describe los planes de pagos del siguiente JSON: {planPagos}, especifica al inicio el detalle del auto')
                resultString=Prompts.planPrompt(resJson,planPagos,chatStory.story)
                
        return resultString

    '''
    Process a message from a user and returns a string response using the clasification data and processing the corresponding flow
    Input: User input message and JSON indicaring classification response
    Output: Response to user
    '''
    def processMessage(self,reqType,text,chatStory):


        resString=''
        if(reqType['tiposolicitud']=='plataforma'):
            resString=Prompts.platformPrompt(text,self.webpage['plataforma'],chatStory)
        elif (reqType['tiposolicitud']=='sedes'):
            resString=Prompts.sitesPrompt(text,self.webpage['sedes'],chatStory)
        elif (reqType['tiposolicitud']=='pagos'):
            resJson=Prompts.extraerParametrosPrompt(text,self.catalogo,chatStory)
            if(resJson):

                resString=self.processCalculo(resJson,self.catalogo,chatStory)
            else:
                resString=Prompts.paymentPrompt(text,self.webpage['pagos'],chatStory)
            
        elif  (reqType['tiposolicitud']=='catalogo'):
            resJson=Prompts.extraerParametrosPrompt(text,self.catalogo,chatStory)
            resString=self.processCatalog(text,resJson,self.catalogo,chatStory)
        elif  (reqType['tiposolicitud']=='calculo'):
            resString=self.processCalculo(text,self.catalogo,chatStory)
        else: #otro
            resString=Prompts.platformPrompt(text,self.webpage['plataforma'],chatStory)

        return resString

    '''
    Receives a request from a user, classifies the message and proceeds to analyze the input
    Input: User text
    Output: Message response to user
    '''
    def processRequest(self,text,chatStory):
        print('Processing prompt')
        print('Story')
        print(chatStory.story)
        resJson=Prompts.classifyPrompt(text,chatStory.story)
        
        resultString=''
        if(resJson):           
            print(resJson[0])
            resultString=self.processMessage(resJson[0],text,chatStory)
        return resultString

    def initializeData(self):
        self.webpage=DataAPI.load_json_from_file('../data/webpage.json')
        self.catalogo=DataAPI.load_json_from_file('../data/catalogo.json')


chatservice=ChatService()
chatservice.initializeData()

chatStory={}
account_sid=''
auth_token=''
with open("../config.json", 'r') as file:
    print('Loading twilio api key')
    config_data = json.load(file)
    account_sid=config_data["account_sid"]
    auth_token=config_data["account_token"]


def sendTwilioResponse(numto,message):

    if(len(message)>1600):#max msg len
        message=message[:1600]

    client = Client(account_sid, auth_token)
    
    messageResponse = client.messages.create(
    from_='whatsapp:+14155238886',
    to= numto,#'whatsapp:+5215558059015'
    body=message
    )
    print(messageResponse.sid)
    return messageResponse

'''
Endpoints
Desc: Class with http get/post request handlers
'''
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    '''
    Process http POST requests
    input: JSON object containing text key and a string for the char input value
    output: String with kavak chat response
    '''
    def do_POST(self):
         # Get the content length (size of the incoming data)
        content_length = int(self.headers['Content-Length'])

        # Read the data sent in the POST request
        post_data = self.rfile.read(content_length)
        print('POST')
        parsed_path = urllib.parse.urlparse(self.path)
        response=''
        #To use subdomains
        if '/status' in parsed_path:
            print('Status callback')
            
        else:
           
            print(parsed_path)
            print(post_data)
            # Parse the data (assuming it's URL encoded or JSON)
            body_value=''
            try:
                # If JSON
                decoded_string = post_data.decode('utf-8')
                params = dict(param.split('=') for param in decoded_string.split('&'))

                #post_data = json_repair.loads(decoded_string)
            
            except json.JSONDecodeError:
                # If URL encoded
                print('ENCODE error')
                post_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
                params = dict(param.split('=') for param in decoded_string.split('&'))
            print(params)
            if('Body' in params):
                body_value = params.get('Body')
                print('DATA JSON')
                print(body_value)
                # Log the received data
                response=''
                userFrom=urllib.parse.unquote(params.get('From'))
                if( not userFrom in chatStory):
                    chatStory[userFrom]=ChatStory()
                    

                chatStory[userFrom].addStoryMessage("user",body_value)  
                response=chatservice.processRequest(body_value,chatStory[userFrom])
                chatStory[userFrom].addStoryMessage("assistant",response)
                print('STORY')
                print(chatStory[userFrom].story)

                twilioresponse=sendTwilioResponse(userFrom,response)
                # Respond to the client
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
            else:
                print('Empty body!')
            byte_data = response.encode('utf-8')
            self.wfile.write(byte_data)
        
    '''
    Process http GET requests
    input: JSON object containing text key and a string for the char input value
    output: String with kavak chat response
    '''
    def do_GET(self):
        print('GET!')
        print(self.path)
        parsed_path = urllib.parse.urlparse(self.path)

        #To use subdomains
        #if '/chat' in parsed_path:
           
        query = urllib.parse.parse_qs(parsed_path.query)
        text = query.get('text')[0]
        print('Text: ',text)
        if(text):
            response=chatservice.processRequest(text,'')
        else:
            response=''
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        byte_data = response.encode('utf-8')
        self.wfile.write(byte_data)
    
'''
Desc: Function that runs an http server indefinitely
'''
def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
    