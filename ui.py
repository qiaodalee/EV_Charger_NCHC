import customtkinter as ctk
from PIL import Image

ctk.set_appearance_mode("light")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
app_size = "576x340"
app_width = int(app_size[:3])
app_height = int(app_size[4:])
va_frame_font_size = 28
info_frame_font_size = 20
stateImage_size = 25
vendorProvideImage_size = 170
font_family = "Arial"
text_color = "black"

#red = not in service or error occur / yellow = started and waiting / green = charging or charge completed
redStateImage = ctk.CTkImage(light_image=Image.open("./image/red_state.png"),
                              size=(stateImage_size,stateImage_size))
yellowStateImage = ctk.CTkImage(light_image=Image.open("./image/yellow_state.png"),
                              size=(stateImage_size,stateImage_size))
greenStateImage = ctk.CTkImage(light_image=Image.open("./image/green_state.png"),
                              size=(stateImage_size,stateImage_size))
vendorProvideImage = ctk.CTkImage(light_image=Image.open("./image/nchc.png"),
                              size=(vendorProvideImage_size,vendorProvideImage_size))

class App_interface(ctk.CTk):
      def __init__(self):
        super().__init__()
        # configure window
        self.title("EV Charger | EVSE")
        self.geometry(app_size)
        top_font = ctk.CTkFont(size=va_frame_font_size, weight="bold", family=font_family)
        info_font = ctk.CTkFont(size=info_frame_font_size, family=font_family)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        #self.iconbitmap("./image/icon.ico")
        #configure grid layout (2x3)
        self.grid_columnconfigure((0,1), weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=8)
        self.grid_rowconfigure(2, weight=1)
        # Voltage display frame and element inside
        self.voltage_frame = ctk.CTkFrame(self, width=app_width/2, corner_radius=0, fg_color="#5eaceb")
        self.voltage_frame.grid(column=0, row=0, sticky="nwes")
        self.voltage_frame.columnconfigure(0, weight=1)
        self.voltage_frame.rowconfigure((0,1), weight=1)
        # element inside the frame
        self.voltStr = ctk.CTkLabel(self.voltage_frame,text="電壓",font=top_font,text_color=text_color)
        self.voltStr.grid(column=0, row=0, pady=(50,0))
        #element inside the frame VARIABLE
        self.voltValue = ctk.CTkLabel(self.voltage_frame,text="0 V",font=top_font,text_color=text_color)
        self.voltValue.grid(column=0, row=1, pady=(0,50))
        #Current display frame and element inside
        self.current_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#5eeb8b")
        self.current_frame.grid(column=1, row=0, sticky="nwes")
        self.current_frame.columnconfigure(0, weight=1)
        self.current_frame.rowconfigure((0,1), weight=1)
        # element inside the frame CONSTANT
        self.currStr = ctk.CTkLabel(self.current_frame,text="電流",font=top_font,text_color=text_color)
        self.currStr.grid(column=0, row=0, pady=(50,0))
        #element inside the frame VARIABLE
        self.currValue = ctk.CTkLabel(self.current_frame,text="0 A",font=top_font,text_color=text_color)
        self.currValue.grid(column=0, row=1, pady=(0,50))
        self.vendorImage = ctk.CTkLabel(self, image=vendorProvideImage, text="")
        self.vendorImage.place(relx=0.35,y=0)
        #Charge info display frame and element inside
        self.info_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="white")
        self.info_frame.grid(column=0, row=1, columnspan=2, sticky="nswe")
        self.info_frame.columnconfigure((0,1), weight=1)
        self.info_frame.rowconfigure((0,1,2), weight=1)
        #element inside the frame CONSTANT
        self.powStr = ctk.CTkLabel(self.info_frame,text="用電量: ",font=info_font,text_color=text_color)
        self.powStr.grid(column=0, row=0,sticky="e", pady=(5,5))
        self.feeStr = ctk.CTkLabel(self.info_frame,text="金額: ",font=info_font,text_color=text_color)
        self.feeStr.grid(column=0, row=1, sticky="e", pady=(5,5))
        self.chargerTimerStr = ctk.CTkLabel(self.info_frame,text="已充電時間: ",font=info_font,text_color=text_color)
        self.chargerTimerStr.grid(column=0, row=2, sticky="e", pady=(5,5))
        #element inside the frame VARIABLE
        self.powValue = ctk.CTkLabel(self.info_frame,text="0.00 kW",font=info_font,text_color=text_color)
        self.powValue.grid(column=1, row=0, sticky="w", pady=(5,5))
        self.feeValue = ctk.CTkLabel(self.info_frame,text="$ 0.00",font=info_font,text_color=text_color)
        self.feeValue.grid(column=1, row=1, sticky="w", pady=(5,5))
        self.chargerTimerValue = ctk.CTkLabel(self.info_frame,text="00 : 00 : 00",font=info_font,text_color=text_color)
        self.chargerTimerValue.grid(column=1, row=2, sticky="w", pady=(5,5))
        #EVSE state frame
        self.state_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#efefef")
        self.state_frame.grid(column=0, row=2, columnspan=2, sticky="nswe")
        self.state_frame.columnconfigure(0, weight=1)
        self.state_frame.columnconfigure(1, weight=1)
        self.state_frame.rowconfigure(0, weight=1)
        #element inside the frame VARIABLE
        self.stateImage = ctk.CTkLabel(self.state_frame, image=redStateImage, text="")
        self.stateImage.grid(column=0,row=0,sticky="e", pady=5, padx=5)
        self.stateValue = ctk.CTkLabel(self.state_frame,text="暫不提供服務",font=info_font,text_color=text_color)
        self.stateValue.grid(column=1, row=0, sticky="w", pady=(0,5), padx=5)
