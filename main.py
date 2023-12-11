import threading
from threading import Event
from server import EVSE_Server
from ocpp_client import ocpp_client
from ui_handler import interface_handler
from session import session_handler
from charge_service import charge_service
import time

if __name__ == "__main__":
    ui = interface_handler()
    process = session_handler()
    charger = []
    charger = charge_service(1, "AC_DC_Charging", "EVCharging", False, ["DC_extended", "AC_three_phase_core"])
    event = Event()

    ocpp_ip = "10.103.103.59"
    ocpp = ocpp_client(ocpp_ip, "443", "0001", "C2309015")
    ocpp_thread = threading.Thread(target=ocpp.start, args=())
    ocpp_thread.start()

    app_ip = "10.103.103.57"
    app = EVSE_Server(app_ip, 15118, 15120, ui_handler=ui, process_handler = process, charge_service = charger, ocpp_client = ocpp)
    server_thread = threading.Thread(target=app.start_udp, args=())
    server_thread.daemon = True
    server_thread.start()
    '''
    ocpp = OCPP_Client("localhost", 15120, ui_handler=ui, server_socket=app)
    ocpp_thread = threading.Thread(target=ocpp.connect, args=())
    ocpp_thread.daemon = True
    ocpp_thread.start()
    '''
    ui.after(0, ui.refresh_screen())
    ui.mainloop()
