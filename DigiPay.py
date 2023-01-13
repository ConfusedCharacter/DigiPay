#-*- coding: utf-8 -*-

#================================#
# DigiPay API                    #
#                                #
# By: Confused Character         #
#================================#



import requests
import uuid



class api:
    def __init__(self,phone):
        self.phone = phone
        self.user_id = None
        self.accessToken = None #open("data.txt").read()
        self.refreshToken = None
        self.session = requests.session()

    def send_code(self):
        self.session.get("https://app.mydigipay.com/auth/login")
        self.session.headers.update({
            'Agent': 'WEB',
            'Digipay-Version': '2022-10-04',
            'Client-Version': '1.0.0',
            'Authorization': 'Basic d2ViYXBwLWNsaWVudC1pZDp3ZWJhcHAtY2xpZW50LXNlY3JldC1kZWJlZTc5ZC1iMDRkLTQ3ZWYtOGVkNS1jMzJlMjRlYzgzNmU=',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36',
            'Origin': 'https://app.mydigipay.com',
            'Referer': 'https://app.mydigipay.com/auth/login',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'close'
        })
        data_json = {
            "cellNumber":self.phone,
            "device":{
                "deviceId":str(uuid.uuid4()),
                "deviceModel":"WEB_BROWSER",
                "deviceAPI":"WEB_BROWSER",
                "osName":"WEB"
                }
        }
        req = self.session.post("https://app.mydigipay.com/digipay/api/users/send-sms",json=data_json)
        if req.json()['result']['title'] == "SUCCESS":
            self.user_id = req.json()["userId"]
            return {"status":True}
        else:
            return {"status":False,"message":req.json()['result']['message']}

    def login(self,code:str):
        req = self.session.post("https://app.mydigipay.com/digipay/api/users/activate",json={
            "smsToken":code,
            "userId":self.user_id
        })
        if req.json()['result']['title'] == "SUCCESS":
            self.accessToken = req.json()["accessToken"]
            self.refreshToken = req.json()["refreshToken"]
            self.session.headers.update({'authorization': 'Bearer '+self.accessToken})
            return {"status":True}
        else:
            return {"status":False,"message":req.json()['result']['message']}

    def balance(self):
        #self.session.headers.update({'authorization': 'Bearer '+self.accessToken})
        req = self.session.get("https://app.mydigipay.com/digipay/api/wallets/balance")
        if req.json()['result']['title'] == "SUCCESS":
            return {"status":True,"amount":req.json()['amount']}
        else:
            return {"status":False,"message":req.json()['result']['message']}

    def _get_refid(self,data):
        return data.split('var redirectUrl = "')[1].split('"')[0].split("RefId=")[1].split("\\u0026")[0]
    
    def buyCharge(self,phone,operator,amount):
        if operator == "irancell":
            operatorId = '2'
        elif operator == "hamrahaval":
            operatorId = '1'
        elif operator == "rightel":
            operatorId = '3'
        
        json_d = {"chargeType":"2","targetedCellNumber":phone,"chargePackage":{"amount":amount},"operatorId":operatorId,"redirectUrl":"https://app.mydigipay.com/payment/result/top-up","cellNumberType":"2"}
        req = self.session.post("https://app.mydigipay.com/digipay/api/top-ups",json=json_d)
        if req.json()['result']['title'] == "SUCCESS":
            url = req.json()['payUrl']
            data_url = self.session.get(url)
            bankRefId = self._get_refid(data_url.text)
            return bankRefId
        else:
            return {"status":False,"message":req.json()['result']['message']}


    def get_list_charge(self,operator):
        if operator == "irancell":
            operatorId = '2'
        elif operator == "hamrahaval":
            operatorId = '1'
        elif operator == "rightel":
            operatorId = '3'

        req = self.session.get(f"https://app.mydigipay.com/digipay/api/top-ups/info/{operatorId}?type=1")
        return req.json()['topUpInfos'][0]['chargePackages']

    def cashIn(self,amount:int):
        data = {"amount":str(amount*10),"redirectUrl":"https://app.mydigipay.com/payment/result/cash-in"}
        req = self.session.post("https://app.mydigipay.com/digipay/api/wallets/cash-in",json=data)
        url = req.json()['payUrl']
        data_url = self.session.get(url).text
        bankRefId = self._get_refid(data_url)
        return bankRefId
    
    def transfer(self,phone,amount):
        req_check = self.session.get("https://app.mydigipay.com/digipay/api/users/"+phone)
        if req_check.json()['result']['title'] == "SUCCESS":
            data = {"amount":amount*10,"destCellNumber":phone}
            req = self.session.post("https://app.mydigipay.com/digipay/api/wallets",json=data)
            if req.json()['result']['title'] == "SUCCESS":
                return {"status":True,"message":req.json()['result']['message']}
            else:
                return {"status":False,"message":req.json()['result']['message']}
        else:
            return {"status":False,"message":req_check.json()['result']['message']}


client = api("09123456789")
if client.send_code():
    if client.login(input("Enter Code: ")):
        print(client.balance())
        print(client.cashIn(10000))
        print(client.transfer("09123456789",10000))
        print(client.buyCharge("09123456789","hamrahaval",50000))
        print(client.get_list_charge())
