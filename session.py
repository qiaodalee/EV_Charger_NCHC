import json
import random

class session_handler():

    def __init__(self):
        self.session_id = "00"

    def check_session_id(self, received_data):
        received_data_id = json.loads(received_data)["V2G_Message"]["Header"]["SessionID"]

        if received_data_id == self.session_id:
            return True
        else:
            return True
        
    def session_start(self):
        self.session_id = str(int((random.random()) * 10000000000000000))
    
    def session_stop(self):
        self.session_id = "00"

    def check_supportedAppProtocolReq(self, received_data):
        return json.loads(received_data)["supportedAppProtocolReq"]["AppProtocol"][0]["ProtocolNamespace"] == "urn:iso:15118:2:2013:MsgDef"

    def check_SessionSetupReq(self, received_data):
        received_data = json.loads(received_data)["V2G_Message"]
        if self.check_session_id(received_data) is False:
            return False
        return True
    
    def check_PaymentServiceSelectionReq(self, received_data):
        if json.loads(received_data)["V2G_Message"]["Body"]["PaymentServiceSelectionReq"]["SelectedPaymentOption"] == None:
            return False
        if json.loads(received_data)["V2G_Message"]["Body"]["PaymentServiceSelectionReq"]["SelectedServiceList"]["SelectedService"][0]["ServiceID"] == None:
            return False
        return True
    
    def set_volt_and_curr(self, received_data):
        ev_volt = 10 ** json.loads(received_data)["V2G_Message"]["Body"]["chargeParameterDiscoveryReq"]["AC_EVChargeParameter"]["EVMaxVoltage"]["Multiplier"]
        ev_volt = ev_volt * json.loads(received_data)["V2G_Message"]["Body"]["chargeParameterDiscoveryReq"]["AC_EVChargeParameter"]["EVMaxVoltage"]["Value"]
        ev_curr = 10 ** json.loads(received_data)["V2G_Message"]["Body"]["chargeParameterDiscoveryReq"]["AC_EVChargeParameter"]["EVMaxCurrent"]["Multiplier"]
        ev_curr = ev_curr * json.loads(received_data)["V2G_Message"]["Body"]["chargeParameterDiscoveryReq"]["AC_EVChargeParameter"]["EVMaxCurrent"]["Value"]
        return min(ev_volt, 480), min(ev_curr, 63)


        
