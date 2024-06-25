# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 16:37:25 2023

@author: 88696

"""
#C:\Users\88696\BX api  
import sys
sys.path.append(r'C:\Users\88696\BX api')
import asyncio
import gzip
import time
import json
import hmac
import urllib3
import requests
import threading
from hashlib import sha256
import websockets
import nest_asyncio
import signal

nest_asyncio.apply()



# 先測試網路行不行
def wait_for_internet_connection():
    while True:
        try:
            urllib3.urlopen('https://www.google.com.tw/',timeout=1)
            return
        except urllib3.URLError:
            time.sleep(3)

print("網路連線成功 !!!")




# 連上設定檔

try:
    #print("嘗試開啟設定檔")
    setting = open("C:/Users/88696/BX api/setting.txt").read().split("\n")
    #setting = open(input("user : ")+"/setting.txt").read().split("\n")
    #print("Successfully opened the settings file.")
except Exception as e:
    print(f"Failed to open the settings file. Error: {e}")


APIURL = "https://open-api.bingx.com"
APIKEY = setting[0].split()[-1]
#print(APIKEY)
SECRETKEY = setting[1].split()[-1]
#print(SECRETKEY)

coin = setting[2].split()[-1].upper()
bx_symbol = coin+"-USDT"
bn_symbol = coin+"USDT"
rate = float(setting[3].split()[-1])
#print("bx_symbol = " + bx_symbol)
#print("bn_symbol = " + bn_symbol)
                


#設定函數



    
  
def get_sign(api_secret, payload):
    signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
    #print("sign=" + signature)
    return signature
    
def praseParam(paramsMap):
    sortedKeys = sorted(paramsMap)
    paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
    return paramsStr
    
def send_request(methed, path, urlpa, payload):
    url = "%s%s?%s&signature=%s" % (APIURL, path, urlpa, get_sign(SECRETKEY, urlpa))
        #print(url)

    headers = {
            'X-BX-APIKEY': APIKEY,
        }

    response = requests.request(methed, url, headers=headers, data=payload)
    return response.text


def get_balance():
    payload = {}
    path = '/openApi/swap/v2/user/balance'
    methed = "GET"
    paramsMap = {
            "timestamp": int(time.time() * 1000),
        }
    paramsStr = praseParam(paramsMap)
    response_text = send_request(methed, path, paramsStr, payload)
    return json.loads(response_text)  # Convert the response string to a Python dictionary

def get_price(symbol):
    payload = {}
    path = '/openApi/swap/v2/quote/price'
    method = "GET"
    paramsMap = {
            "symbol": symbol
        }
    paramsStr = praseParam(paramsMap)
    response = send_request(method, path, paramsStr, payload)
    
    try:
        data = json.loads(response)
        return data
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:", str(e))
    except Exception as e:
        print("An error occurred:", str(e))


def get_price1(symbol):
    payload = {}
    path = '/openApi/swap/v2/quote/price'
    methed = "GET"
    paramsMap = {
            "symbol": symbol
        }
    paramsStr = praseParam(paramsMap)
    response = send_request(methed, path, paramsStr, payload)
        #print(get_price(bx_symbol)['data'])
    return json.loads(response)


def test_order(symbol, side, volume, tradeType):
    payload = {}
    path = '/openApi/swap/v2/trade/order/test'
    methed = "POST"
    paramsMap = {
    "symbol": symbol,
    "type": tradeType,
    "side": side,
    #"positionSide": "",
    #"price": 0,
    "quantity": volume,
   # "stopPrice": 0,
   "timestamp": int(time.time() * 1000),
   "recvWindow": 100,
        #"timeInForce": ""
        }
    paramsStr = praseParam(paramsMap)
        #print(send_request(methed, path, paramsStr, payload) )
    return json.loads(send_request(methed, path, paramsStr, payload))

def post_morder(symbol, price, side, volume, tradeType , positionSide):
    payload = {}
    path = '/openApi/swap/v2/trade/order'
    methed = "POST"
    paramsMap = {
      "symbol": symbol,
      "type": tradeType,
      "side": side,
      "positionSide": positionSide,
      "price": price,
      "quantity": volume,
       # "stopPrice": 0,
      "timestamp": int(time.time() * 1000),
      "recvWindow": 100
        #"timeInForce": ""
        }
    paramsStr = praseParam(paramsMap)
    data = send_request(methed, path, paramsStr, payload)
    #print(send_request(methed, path, paramsStr, payload) )
    return json.loads(data)

def post_order(symbol, side, volume, tradeType , positionSide):
    payload = {}
    path = '/openApi/swap/v2/trade/order'
    methed = "POST"
#    takeProfit = {
##        "type": "TAKE_PROFIT",
#        "stopPrice": takeProfit,
#        "price": '0',
#        "workingType": "MARK_PRICE"
#    }
    paramsMap = {
      "symbol": symbol,
      "type": tradeType,
      "side": side,
      "positionSide": positionSide,
      #"price": price,
      "quantity": volume,
  #    "takeProfit": json.dumps(takeProfit),
      "timestamp": int(time.time() * 1000),
     # "recvWindow": 300
        #"timeInForce": ""
        }
    paramsStr = praseParam(paramsMap)
    data = send_request(methed, path, paramsStr, payload)
    #print(send_request(methed, path, paramsStr, payload) )
    return json.loads(data)
#要不要json.load
        #return json.loads(send_request(methed, path, paramsStr, payload))
    
def set_leverage(symbol , leverage , side):
    print(f"Setting leverage: Symbol = {symbol}, Leverage = {leverage}, Side = {side}" )
    payload = {}
    path = '/openApi/swap/v2/trade/leverage'
    methed = "POST"
    paramsMap = {
    "symbol": symbol,
    "side": side,
    "leverage": leverage,
    "timestamp": int(time.time() * 1000) 
    }
    paramsStr = praseParam(paramsMap)
    return send_request(methed, path, paramsStr, payload)
  
def get_leverage(symbol):
    payload = {}
    path = '/openApi/swap/v2/trade/leverage'
    methed = "GET"
    paramsMap = {
            "symbol": symbol,
            "timestamp": int(time.time()*1000)
        }
    paramsStr = praseParam(paramsMap)
    response = send_request(methed, path, paramsStr, payload)
    return json.loads(response)
    
def close_all(symbol):
    payload = {}
    path = '/openApi/swap/v2/user/balance'
    methed = "POST"
    paramsMap = {
        "timestamp": int(time.time()*1000),
        "symbol" : symbol
        }
    paramsStr = praseParam(paramsMap)
    return send_request(methed, path, paramsStr, payload)    
    
def position(symbol):
    payload = {}
    path = '/openApi/swap/v2/user/positions'
    methed = "GET"
    paramsMap = {
        "symbol": symbol,
        "timestamp": int(time.time()*1000)
        }
    paramsStr = praseParam(paramsMap)
    response = send_request(methed, path, paramsStr, payload)
    return json.loads(response)
def depth(symbol):
    payload = {}
    path = '/openApi/swap/v2/quote/depth'
    methed = "GET"
    paramsMap = {
        "symbol": symbol,
        "limit": 5
        }
    paramsStr = praseParam(paramsMap)
    response = send_request(methed, path, paramsStr, payload)
        #print(response)
    return json.loads(response)

def order(symbol,oid ):
    payload = {}
    path = '/openApi/swap/v2/trade/order'
    methed = "GET"
    paramsMap = {
    "symbol": symbol,
    "orderId": oid,
    "timestamp": int(time.time()*1000),
    "recvWindow": 0
    }
    paramsStr = praseParam(paramsMap)
    response = send_request(methed, path, paramsStr, payload)
    #print(response)
    return json.loads(response)  



def futinf():
    payload = {}
    path = '/openApi/swap/v2/quote/contracts'
    method = "GET"
    paramsMap = {
        
        }
    paramsStr = praseParam(paramsMap)
    response = send_request(method, path, paramsStr, payload)
    #print(response)
    return json.loads(response)
#ws
def get_trade_min_limit_by_symbol(symbol):
    data = futinf()  # 
    if "data" in data:
        for contract in data["data"]:
            if contract.get("symbol") == symbol:
                return float(contract.get("tradeMinLimit", 0))  # 
    return 0  # 

bn_price = 0
bx_price = 0  
best_bid_price = 0
best_ask_price = 0
confirm = 0
confirm2 = 0
data1 = ""
data2 = ""
fs = ""

#bn
if setting[4].split()[-1] == "f":
    fs = "f"


async def on_message(message):
 #   current_time = time.time() * 1000
    global bn_price
    data = json.loads(message)
    if data['e'] == 'trade':
    #    server_timestamp_ms = int(data['T'])
        bn_price = float(data['p'])
      #  delay = current_time - server_timestamp_ms  # （毫秒）
       # print(f"BN  Price: {bn_price}, Server Timestamp: {server_timestamp_ms}, Delay: {delay:.2f} ms")

async def bn_websocket():
    uri = "wss://stream.binance.com/ws/" + bn_symbol.lower() + "@trade"
    async with websockets.connect(uri) as ws:
        try:
            while True:
                message = await ws.recv()
                await on_message(message)
        except websockets.exceptions.ConnectionClosed as e:
            pass
     #       print(f'Bn Error : {e}')
#BTC-USDT@trade




async def handle_bx_message2(message):
 #   current_time = time.time() * 1000
    global bx_price
    decompressed_data = gzip.decompress(message).decode()
    try:
        data = json.loads(decompressed_data)
        if data['data'] is not None:
       #     server_timestamp_ms = int(data['data'][0]['T'])
            #print(data)
            bx_price = float(data['data'][0]['p'])
            
      #      delay = current_time - server_timestamp_ms  # 
       #     print(f"BX   Price: {bx_price}, Server Timestamp: {server_timestamp_ms}, Delay: {delay:.2f} ms")
      #  else:
       #     print("Received data does not contain expected 'data' field.")
    except Exception as e:
        pass
        #print(f"Error processing message: {e}")
    
    if decompressed_data == "Ping":
        return "Pong"
    

async def handle_bx_message(message):
    global bx_price
    decompressed_data = gzip.decompress(message).decode()
    try:
        data = json.loads(decompressed_data)

        bx_price = float(data['data'][0]['p'])
        #print(bx_price)

    except Exception as e:
        pass
        #print(f"Error processing message: {e}")
    
    if decompressed_data == "Ping":
        return "Pong"


async def bx_websocket():
    uri = "wss://open-api-swap.bingx.com/swap-market"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({"id": "id1", "reqType": "sub", "dataType": bx_symbol + "@trade"}))
        async for message in websocket:
            pong_payload = await handle_bx_message2(message)
            if pong_payload:
                await websocket.send(pong_payload)

        
def print_info():
        #os.system("cls")
        balance = float(get_balance()["data"]["balance"]["balance"])
        print("--------------------------------------")
        print("coin       :", coin)
        print("rate       :", rate)
        print("price mode :", setting[4].split()[-1])
        print("balance    :", balance)
        print("--------------------------------------")
#socket = "wss://"+fs+"stream.binance.com/ws/"+bn_symbol.lower()+"@aggTrade"

#print(socket)



def run_trade():
    
    print("執行交易程式...")
    while bx_price == 0 or bn_price == 0 :
        pass    

    #, "best_ask_price : " + str(best_ask_price),', ' ,"best_bid_price : " + str(best_bid_price) 
    print("BN : " +  str(bn_price) + " | BX :  " + str(bx_price) )
    balance = float(get_balance()["data"]["balance"]["balance"])
    print_info()
    set_leverage(bx_symbol , 4 , "LONG")
    set_leverage(bx_symbol , 4 , "SHORT")
    leverage = int(get_leverage(symbol=bx_symbol)["data"]["longLeverage"] ) 
    print("槓桿設為： " + str(leverage) + " 倍")
    mode = "none"    
    amt = float( 2 * leverage ) / bx_price
    
    
    rrate = (1 + rate/100 )
    
    #bx_price = float(get_price(bx_symbol)['data']['price'])
    #amt = (get_position(bx_symbol)['data'])
    #abc = get_price(bx_symbol)['data']
    
    
   # float( 1 * leverage ) / bx_price
    #balance
    print("設定下單量 ：" + str(amt) + " " + coin)
    
    print("開始交易 !!!")
    print("======================================")


    
    
    alive = True          #下單不成功 alive false
    
    while alive : 
               
        try:
            if  mode == "none":
                #if bx_price > bn_price*rrate :
                if bn_price > bx_price * rrate :
                    #print("BN : " +  str(bn_price) + " | BX :  " + str(bx_price) )
                    #time.sleep(0.1)
                    #amt = float( 3.8 * leverage * x ) / bx_price               #下單前再設定一次成交量   
                #    if bn_price > bx_price * rrate :
                        
                        buy = post_order(symbol=bx_symbol, volume=amt, side="BUY", tradeType="MARKET", positionSide = "LONG")
                        #print(bn_price > bx_price * rrate)
                        if buy["code"] == 0 :   
                            oid_long = buy['data']['order']['orderId']                       
                            mode = "long"                      
                            longE = float(order(bx_symbol, oid_long)['data']['order']['avgPrice'])                  
                            longqty = order(bx_symbol, oid_long)['data']['order']["executedQty"]                  
                            print("做 多   :", longE)
                            #print("rate = " + str((bx_price - bn_price) * 100 / bx_price) )
                            #print("BN : " +  str(bn_price) + " | BX :  " + str(bx_price) )
                           # print(bn_price > bx_price * rrate)
                        else:
                            
                            alive = False
                            print("下多單出錯，迴圈停止")
                            print(buy)


                elif bx_price > bn_price*rrate  :
                #elif bn_price > bx_price * rrate  :
                    #print("BN : " +  str(bn_price) + " | BX :  " + str(bx_price) )
                    #time.sleep(0.1)
                   # if bx_price > bn_price*rrate  :
             #       amt = float( 3.8 * leverage * x ) / bx_price
                        sell = post_order(symbol=bx_symbol, volume=amt, side="SELL", tradeType="MARKET", positionSide = "SHORT")
                        
                        if sell["code"] == 0:
                                                   
                            oid_short = sell['data']['order']['orderId']                        
                            mode = "short"                        
                            shortE = float(order(bx_symbol, oid_short)['data']['order']['avgPrice'] )                       
                            shortqty = order(bx_symbol, oid_short)['data']['order']["executedQty"]                        
                            print("做 空   :", shortE)
                           # print("rate = " + str((bx_price - bn_price)* 100 / bx_price ))
                           # print("BN : " +  str(bn_price) + " | BX :  " + str(bx_price) )
        
                        else:
                            
                            alive = False
                            print("下空單出錯，迴圈停止")
                            print(sell)
                #elif    True :
                        #print("BN : " +  str(bn_price) + " | BX :  " + str(bx_price) )
            elif mode == "long" and (bn_price <= bx_price or bx_price >= longE):
            #elif mode == "long" and (bx_price < bn_price or bx_price <= longE):
                                             
             #   if bn_price <= bx_price or bx_price >= longE :           # 多倉平倉條件
    
                    #amt = float(get_position(bx_symbol)['data'][0]['availableAmt'])
                amt = float(longqty)                   
                tradeinfo = post_order( symbol=bx_symbol, volume = amt, side="SELL", tradeType="MARKET", positionSide = "LONG" )
                    
                    
                if tradeinfo["code"] == 0:
                                         
                    oid_longout = tradeinfo['data']['order']['orderId']                                                                       
                    mode = "none"                            
                    longoutp = order(bx_symbol, oid_longout)['data']['order']['avgPrice']                        
                        #longoutqty = order(bx_symbol, oid_longout)['data']['order']["executedQty"]                        
                    print("平 多   :", longoutp )                       
                        #balance = float(get_balance()["data"]["balance"]["balance"])                        
                    print("--------------------------------------")   
                        #print("Balance    : ", balance)



            elif  mode == "short" and (bx_price < bn_price or bx_price <= shortE) :
            #elif  mode == "short" and (bn_price <= bx_price or bx_price >= shortE) :
             #   if bx_price < bn_price or bx_price <= shortE :          # 空倉平倉條件
                    
                    #amt = float(get_position(bx_symbol)['data'][0]['availableAmt'])
                amt = float(shortqty)
                tradeinfo = post_order(symbol=bx_symbol, volume=amt, side="BUY", tradeType="MARKET", positionSide = "SHORT" )
                    
                
                if tradeinfo["code"] == 0:
                        
                    oid_shortout = tradeinfo['data']['order']['orderId']
                    mode = "none"
                    shortoutp = order(bx_symbol, oid_shortout)['data']['order']['avgPrice']                        
                        #shortoutqty = order(bx_symbol, oid_shortout)['data']['order']["executedQty"]                        
                    print("平 空   :", shortoutp )                       
                        #balance = float(get_balance()["data"]["balance"]["balance"])                       
                    print("--------------------------------------")   
                        #print("Balance    : ", balance)

                time.sleep(0)
                
                
                
        
        except KeyboardInterrupt:
       
            close_info = close_all(bx_symbol)       
            print("全部平倉" )            
            print(close_info)            
            #print("停止。")
            
            sys.exit()


def signal_handler(signal, frame):
    close_info = close_all(bx_symbol)       
    print("迴圈外終止 全部平倉" )            
    print(close_info)            

    sys.exit()



#run_trade() # 主執行序
async def main():
    """
    主函数
    """
    trade_thread = threading.Thread(target=run_trade)
    trade_thread.start()
    #run_trade()

    await asyncio.gather(
        bx_websocket(),
        bn_websocket()
    )

    print("數據線程啟動")
    
    


if __name__ == "__main__":
    
    signal.signal(signal.SIGINT, signal_handler)
    
    asyncio.run(main())






