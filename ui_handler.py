from ui import App_interface, redStateImage, yellowStateImage, greenStateImage
from tkinter import messagebox

class interface_handler(App_interface):
    
    def __init__(self):
        super().__init__()
        #Get variable from App_interface class
        self.voltage = float(self.voltValue._text.split(' ')[0])
        self.current = float(self.currValue._text.split(' ')[0])
        self.consume = float(self.powValue._text.split(' ')[0])
        self.fee = float(self.feeValue._text.split(' ')[1])
        self.bill = 0
        (self._timerHours, 
        self._timerMinutes, 
        self._timerSeconds) = self.chargerTimerValue._text.split(' : ')
        self.chargerState = self.stateValue._text

    def check_state(self):
        if "等待連接" in self.chargerState:
            return "waiting"
        elif "請拔出充電槍" in self.chargerState:
            return "complete"
        elif "正在充電" in self.chargerState:
            return "charging"
        else:
            return "stop"
    
    def update_state(self, state, text=None):
        if state == "stop":
            self.chargerState = "暫不提供服務"
            self.stateImage.configure(image=redStateImage)
            self.stateValue.configure(text="暫不提供服務")
            if text != None:
                self.stateValue.configure(text=text)
        elif state == "waiting":
            self.chargerState = "等待連接"
            self.stateImage.configure(image=yellowStateImage)
            self.stateValue.configure(text="等待連接")
        elif state == "charging":
            self.chargerState = "正在充電"
            self.stateImage.configure(image=greenStateImage)
            self.stateValue.configure(text="正在充電")
        elif state == "complete":
            self.chargerState = "充電完成，請拔出充電槍"
            self.stateImage.configure(image=greenStateImage)
            self.stateValue.configure(text="充電完成，請拔出充電槍")
            
    def update_data(self, ev_voltage, ev_current):
        self.voltage = ev_voltage
        self.current = ev_current
        self.fee = 265
        self.consume = (self.voltage * self.current)/1000

    def update_timer(self):
        self._timerSeconds = int(self._timerSeconds) + 1
        if int(self._timerSeconds) == 60:
            self._timerSeconds = "0"
            self._timerMinutes = int(self._timerMinutes) + 1
        if int(self._timerMinutes) == 60:
            self._timerMinutes = "0"
            self._timerHours = int(self._timerHours) + 1
        
    def update_interface(self):
        self.voltValue.configure(text = "{} V".format(self.voltage))
        self.currValue.configure(text = "{} A".format(self.current))
        self.powValue.configure(text = "{} kW".format(self.consume))
        self.chargerTimerValue.configure(text = "{} : {} : {}".format
                                      (str(self._timerHours).zfill(2),
                                       str(self._timerMinutes).zfill(2),
                                       str(self._timerSeconds).zfill(2)))
        self.bill = round(float(self.bill) + ((float(self.fee) * float(self.consume)) / 3600),2)
        self.feeValue.configure(text = "$ {}".format(self.bill))
        
    def clean_screen(self):
        self.voltValue.configure(text = "{} V".format("0"))
        self.currValue.configure(text = "{} A".format("0"))
        self.powValue.configure(text = "{} kW".format("0.00"))
        self.chargerTimerValue.configure(text = "{} : {} : {}"
                                         .format("00","00","00"))
        self.feeValue.configure(text = "$ {}".format("0.00"))
        self.voltage = 0
        self.current = 0
        self.consume = 0
        self._timerHours = self._timerMinutes = self._timerSeconds = 0
    
    def complete_charging(self):
        self.voltage = 0
        self.current = 0
        self.voltValue.configure(text = "{} V".format("0"))
        self.currValue.configure(text = "{} A".format("0"))

    def refresh_screen(self):
            if self.check_state() == "charging":
                self.update_timer()
                self.update_interface()
                self.after(1000, self.refresh_screen)
            elif self.check_state() == "complete":
                self.complete_charging()
                self.after(10, self.refresh_screen)
            else:
                self.clean_screen()
                self.after(10, self.refresh_screen)
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.quit()
            self.destroy()


