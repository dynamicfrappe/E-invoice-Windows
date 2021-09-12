from django.shortcuts import render

# Create your views here.
from http.client import HTTPSConnection
from base64 import b64encode
import ssl
import json
from payer.models import PayerAccount
url = 'id.preprod.eta.gov.eg'
method= '/connect/token'



def get_token():
    account  = PayerAccount.objects.all().first()
    key =account.user_key 
    secret = account.token_key
    grant_type = 'client_credentials'
    srta = str(key) + ":" + str(secret)
    str_byte = bytes(srta, 'utf-8')
    userAndPass = b64encode(str_byte).decode("ascii")
    body = 'grant_type=%s'%grant_type
    headers = { 'Authorization' : 'Basic %s'%userAndPass ,
				 'Content-Type': 'application/x-www-form-urlencoded'}

    c = HTTPSConnection(url, context=ssl._create_unverified_context())
    c.request('POST', method , headers=headers  ,body=body)
    try :

        res = c.getresponse()
        data = res.read()
        json_data = json.loads(data )
        json_data.get("access_token")
        return( json_data.get("access_token"))
    except Exception as e:
        return {'erro' , e}
       

def home(request):
    page = 'last_documents.html'
    account  = PayerAccount.objects.all().first()
    token = get_token()
    headers = {
				"Authorization"   : 'Bearer %s'%token,
				"Accept"          : "application/json" ,
				"Accept-Language" : "ar" ,
				'Content-Type'    :'application/json' 
				 }
    valid = {"submissionId":"MQN2JBG4VEYTH9GGRG13C1FF10"}
    number = 1 
    if request.GET.get('page') :
        number = int(request.GET.get('page'))


    c = HTTPSConnection('api.preprod.invoicing.eta.gov.eg' ,context=ssl._create_unverified_context())
    c.request('GET', f'/api/v1.0/documents/recent?pageNo={number}&pageSize=20' ,headers=headers  )
    res = c.getresponse()
    data = res.read()
    ara = json.loads(data)
    print(ara)
    result = ara.get('result')
    metadata = ara.get('metadata')
    available_pages = metadata.get('totalPages')
    pages = [ i for i in range(1 , int(available_pages) )]
    available_pages = metadata.get('totalCount')
    content = {
        "token": result,
        "pages" :pages , 
        "page_number" : number,
    }
    return render(request ,page , content)