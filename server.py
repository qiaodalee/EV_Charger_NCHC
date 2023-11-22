"""
1. init Stage (waiting for connection)
2. Supported App Protocol Stage + Session creation
3. Service Discovery Stage
4. Payment Service Selection Stage
5. Authorization Stage
6. Charge Parameter Stage
7. Power Delivery stage
8. Charging state (while loop)
9. Power Delivery stage (stop charging)
10. Connection termination
"""

import socket
import threading
import json
import calendar
import time
import os

class EVSE_Server():

    def __init__(self, host, port, udp_port, ui_handler, process_handler, charge_service, ocpp_client):
        self.host = host
        self.IPv4 = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.udp_port = udp_port
        self.server_socket = None
        self.is_running = False
        self.ui_handler = ui_handler # interface_handler instance
        self.process_handler = process_handler
        self.charge_service = charge_service
        self.selected_SASchedule = None
        self.ev_voltage = 480
        self.ev_current = 63
        self.ocpp_client = ocpp_client

    def closing(self):
        while True:
            time.sleep(4)
            try:
                bool(self.ui_handler.winfo_exists() == 1)
            except:
                self.ocpp_client.update_state(req = "StatusNotification", meter = 0)
                os._exit(0)

    def restart_all(self):
        udp_server_thread = threading.Thread(target=self.start_udp)
        stop_tcp_server_thread = threading.Thread(target=self.stop)
        stop_tcp_server_thread.start()
        stop_tcp_server_thread.join()
        udp_server_thread.start()
    
    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.host, self.port))
        except:
        	pass 
        self.server_socket.listen(1)
        self.is_running = True
        print("TCP server 已啟動等待通訊中...")
        client_thread = threading.Thread(target=self.listen_for_connections)
        client_thread.start()

    
    def stop(self):
        self.server_socket.close()
        self.is_running = False
        print("TCP server 已關閉通訊...")
        self.ui_handler.update_state(state="stop")
        
    
    def listen_for_connections(self):
        while self.is_running:
            print("TCP server 等待連線中...")
            try:
                client_socket, address = self.server_socket.accept()
                print("接受來自", address, "的連線\n")
                client_thread = threading.Thread(target=self.client_handler, args=(client_socket,))
                client_thread.start()
            except:
                pass
      
    def client_handler(self, client_socket):
        while self.is_running:
            data = client_socket.recv(1024)
            if not data:
                break
            received_data = data.decode()
            print("接收到Req: ", received_data)
            if "Terminate" in received_data:
                response = self.process_data(received_data)
                print("傳送Res: ", response)
                client_socket.sendall(response.encode())
                break
            response = self.process_data(received_data)
            try:
                print("傳送Res: ", response)
                client_socket.sendall(response.encode())
            except:
                self.restart_all() 
                exit()
        client_socket.close()
        self.restart_all()

    def start_udp(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.udp_port))
        print("UDP server 已啟動等待通訊中...")
        client_thread = threading.Thread(target=self.listen_for_udp_connections)
        client_thread.start()
        closing_thread = threading.Thread(target=self.closing)
        closing_thread.start()

    def stop_udp(self):
        self.server_socket.close()
        print("UDP server 已關閉通訊...")
        tcp_server_thread = threading.Thread(target=self.start)
        tcp_server_thread.start()

    def listen_for_udp_connections(self):
        self.ui_handler.update_state(state="waiting")
        print("UDP server 等待連線中...")
        try:
            in_data, address = self.server_socket.recvfrom(1024)
            print("接受來自", address, "的SDP封包: ", in_data.decode())
            response = self.process_data(in_data.decode())
            print("傳送資料: ", response)
            try:
                self.server_socket.sendto(response.encode(), address)
            except:
                self.restart_all() 
                exit()
            self.stop_udp()
        except: 
            pass

    def process_data(self, received_data):
        out_data = None

        if "SDP_REQUEST" in received_data:
            out_data = {"IP address" : self.IPv4, 
                        "Port" : self.port,
                        "Security" : "NO_TLS",
                        "Transport" : "TCP"}
            
        elif "supportedAppProtocolReq" in received_data:

            if self.process_handler.check_supportedAppProtocolReq(received_data) is not True:
                return out_data
            
            out_data = {
                            "supportedAppProtocolRes": {
                                "ResponseCode": "OK_SuccessfulNegotiation",
                                "SchemaID": json.loads(received_data)["supportedAppProtocolReq"]["AppProtocol"][0]["SchemaID"]
                            }
                        }
            
        elif "SessionSetupReq" in received_data:
            if self.process_handler.check_session_id (received_data) is False:
                return out_data
            self.process_handler.session_start()
            out_data = {
                            "V2G_Message": {
                                "Header": {
                                    "SessionID": self.process_handler.session_id
                                },
                                "Body": {
                                    "SessionSetupRes": {
                                        "ResponseCode": "OK_NewSessionEstablished",
                                        "EVSEID": "UK123E1234",
                                        "EVSETimeStamp": calendar.timegm(time.gmtime())
                                    }
                                }
                            }
                        }
        elif "ServiceDiscoveryReq" in received_data:
            if self.process_handler.check_session_id (received_data) is False:
                return out_data
            out_data = {
                            "V2G_Message": {
                                "Header": {
                                "SessionID": self.process_handler.session_id
                                },
                                "Body": {
                                    "ServiceDiscoveryRes": {
                                        "ResponseCode": "OK",
                                        "PaymentOptionList": {
                                        "PaymentOption": ["ExternalPayment"]
                                        },
                                        "ChargeService": {
                                            "ServiceID": self.charge_service.ServiceID,
                                            "ServiceName": self.charge_service.ServiceName,
                                            "ServiceCategory": self.charge_service.ServiceCategory,
                                            "FreeService": self.charge_service.FreeService,
                                            "SupportedEnergyTransferMode": {
                                                "EnergyTransferMode": self.charge_service.SupportedEnergyTransferMode
                                            }
                                        }
                                    }
                                }
                            }
                        }
        elif "PaymentServiceSelectionReq" in received_data:
            if self.process_handler.check_session_id (received_data) is False:
                return out_data
            if self.process_handler.check_PaymentServiceSelectionReq(received_data) is False:
                return out_data
            out_data = {
                            "V2G_Message": {
                                "Header": {
                                    "SessionID": self.process_handler.session_id
                                },
                                "Body": {
                                    "PaymentServiceSelectionRes": {
                                        "ResponseCode": "OK"
                                    }
                                }
                            }
                        }
        elif "AuthorizationReq" in received_data:
            if self.process_handler.check_session_id (received_data) is False:
                return out_data
            out_data = {
                            "V2G_Message": {
                                "Header": {
                                "SessionID": self.process_handler.session_id
                                },
                                "Body": {
                                    "AuthorizationRes": {
                                        "ResponseCode": "OK",
                                        "EVSEProcessing": "Finished"
                                    }
                                }
                            }
                        }
        elif "chargeParameterDiscoveryReq" in received_data:
            if self.process_handler.check_session_id (received_data) is False:
                return out_data
            self.ev_voltage, self.ev_current = self.process_handler.set_volt_and_curr(received_data)
            out_data = {
                            "V2G_Message": {
                                "Header": {
                                "SessionID": self.process_handler.session_id
                                },
                                "Body": {
                                "ChargeParameterDiscoveryRes": {
                                    "ResponseCode": "OK",
                                    "EVSEProcessing": "Finished",
                                    "SAScheduleList": {
                                    "SAScheduleTuple": self.charge_service.SAScheduleTuple,
                                    "AC_EVSEChargeParameter": {
                                    "AC_EVSEStatus": self.charge_service.AC_EVSEStatus,
                                    "EVSENominalVoltage": {
                                        "Value": self.ev_voltage,
                                        "Multiplier": 0,
                                        "Unit": "V"
                                    },
                                    "EVSEMaxCurrent": {
                                        "Value": self.ev_current,
                                        "Multiplier": 0,
                                        "Unit": "A"
                                    }
                                    }
                                    }
                                    }
                                }
                            }
                        }   
        elif "PowerDeliveryReq" in received_data:
            if self.process_handler.check_session_id (received_data) is False:
                return out_data
            if json.loads(received_data)["V2G_Message"]["Body"]["PowerDeliveryReq"]["ChargeProgress"] == "Start":
                self.ocpp_client.update_state(req="StartTransaction", meter=self.charge_service.meter)
                self.selected_SASchedule = json.loads(received_data)["V2G_Message"]["Body"]["PowerDeliveryReq"]["SAScheduleTupleID"]
                self.ui_handler.update_data(self.ev_voltage, self.ev_current)
                self.ui_handler.update_state(state="charging")
                self.ocpp_client.status = "charging"

            elif json.loads(received_data)["V2G_Message"]["Body"]["PowerDeliveryReq"]["ChargeProgress"] == "Stop":
                self.ocpp_client.update_state(req="StopTransaction", meter=self.charge_service.meter)
                self.selected_SASchedule = None
                self.ui_handler.update_state(state="complete")
                self.ocpp_client.status = "complete"


            else:
                return out_data
            out_data = {
                            "V2G_Message": {
                                "Header": {
                                "SessionID": self.process_handler.session_id,
                                },
                                "Body": {
                                    "PowerDeliveryRes": {
                                        "ResponseCode": "OK",
                                        "AC_EVSEStatus": self.charge_service.AC_EVSEStatus
                                    }
                                }
                            }
                        }
        elif "ChargingStatusReq" in received_data:
            if self.process_handler.check_session_id (received_data) is False:
                return out_data
            self.charge_service.meter = self.charge_service.meter+5
            out_data = {
                            "V2G_Message": {
                                "Header": {
                                "SessionID": self.process_handler.session_id,
                                },
                                "Body": {
                                    "ChargingStatusRes": {
                                        "ResponseCode": "OK",
                                        "EVSEID": "UK123E1234",
                                        "SAScheduleTupleID": self.selected_SASchedule,
                                        "ReceiptRequired": False,
                                        "AC_EVSEStatus": self.charge_service.AC_EVSEStatus
                                    }
                                }
                            }
                        }
        elif "SessionStopReq" in received_data:
            if self.process_handler.check_session_id (received_data) is False:
                return out_data
            out_data = {
                            "V2G_Message": {
                                "Header": {
                                "SessionID": self.process_handler.session_id,
                                },
                                "Body": {
                                    "SessionStopRes": {
                                        "ResponseCode": "OK"
                                    }
                                }
                            }
                        }
            self.process_handler.session_stop()
        if out_data is not None:
            return json.dumps(out_data)
        else:
            return out_data
