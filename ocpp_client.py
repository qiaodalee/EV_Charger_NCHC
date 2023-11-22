from websocket import create_connection
import time, datetime
import json
import threading
import os

class ocpp_client:
    def __init__(self, host, port, id, idTag):
        self.ws = None
        self.host = host
        self.port = port
        self.id = id
        self.idTag = idTag
        self.status = "closed"
        self.transactionid = None
        self.error_code = "NoError"
    
    def start(self):
        try:
            self.ws = create_connection("ws://" + self.host + ":" + self.port)
        except Exception as e:
            print ( e.name)
            print ( "websocket is not connect")
        self.update_state(req="BootNotification", meter=0)

    def close(self):
        self.ws.close()
        self.ws = None

    def send_data(self, data):
        try:
            self.ws.send(json.dumps(data))
        except Exception as e:
            print(e.name)

    def message_handler(self, rec_data):
        if "BootNotification_conf" in rec_data["header"]["req"]:
            if ( rec_data["body"]["status"] == "accepted"):
                alive = threading.Thread(target=self.HeartBeat, args=(rec_data["body"]["interval"],))
                alive.start()
                self.status = "ready"
            else:
                time.sleep(rec_data["body"]["interval"])
                self.update_state(self, "BootNotification", 0)
            
        elif "HeartBeat_conf" in rec_data["header"]["req"]:
            pass
        elif "StatusNotification_conf" in rec_data["header"]["req"]:
            pass
        elif "StartTransaction_conf" in rec_data["header"]["req"]:
            if ( rec_data["body"]["idTagInfo"]["status"] == "accepted"):
                self.transactionid = rec_data["body"]["transactionId"]
            else:
                self.transactionid = None
        elif "StopTransaction_conf" in rec_data["header"]["req"]:
            if ( rec_data["body"]["idTagInfo"]["status"] == "accepted"):
                self.transactionid = None
        return


    def ocpp_listener(self):
        data = self.ws.recv()
        data = json.loads(data)
        print(data)
        message = threading.Thread(target=self.message_handler, args=(data,))
        message.start()
        return

    def HeartBeat(self, interval):
        while self.ws is not None:
            time.sleep(interval)
            if ( self.status == "ready"):
                self.update_state(req="HeartBeat", meter=0)

    def update_state(self, req, meter):
        print(req)
        if ( req == "BootNotification"):
            self.send_data({"header" : "BootNotification_req",
                            "body" : {
                                "chargePointModel" : "cp_001",
                                "chargePointVendor" : "ttu",
                                "chargePointid" : self.id,
                                "chargePointIDTag" : self.idTag
                            }})
        elif(req == "HeartBeat"):
            self.send_data({"header" : {"id" : self.id, "req" : "HeartBeat_req"}})
        elif(req == "StatusNotification"):
            self.send_data({"header" : {"id" : self.id, "req" : "StatusNotification_req"},
                            "body" : {
                                "status" : self.status,
                                "errorCode" : self.error_code,
                            }})
        elif(req == "StartTransaction"):
            timeStamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.send_data({"header" : {"id" : self.id, "req" : "StartTransaction_req"},
                            "body" : {
                                "connectorId" : 1,
                                "chargePointIDTag" : self.idTag,
                                "meterStart" : meter,
                                "timeStamp" : timeStamp,
                            }})
        elif(req == "StopTransaction"):
            timeStamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.send_data({"header" : {"id" : self.id, "req" : "StopTransaction_req"},
                            "body" : {
                                "chargePointIDTag" : self.idTag,
                                "meterStop" : meter,
                                "timeStamp" : timeStamp,
                                "transactionid" :  self.transactionid
                            }})
        try:
            ocpp_listner = threading.Thread(target=self.ocpp_listener)
            ocpp_listner.start()
            ocpp_listner.join(timeout=10)
            
            if ocpp_listner.is_alive():
                raise TimeoutError
        except TimeoutError:
            print("time out !")
            os._exit(0)
        except Exception as e:
            print(e.name)
            os._exit(0)
        
