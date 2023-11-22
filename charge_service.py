class charge_service:

    def __init__(self, ServiceID, ServiceName, ServiceCategory, FreeService, SupportedEnergyTransferMode):
        self.ServiceID = ServiceID
        self.ServiceName = ServiceName
        self.ServiceCategory = ServiceCategory
        self.FreeService = FreeService
        self.SupportedEnergyTransferMode = SupportedEnergyTransferMode
        self.meter = 0
        self.SAScheduleTuple = [
                                        {
                                            "SAScheduleTupleID": 1,
                                            "PMaxSchedule": {
                                                "PMaxScheduleEntry": [
                                                    {
                                                        "PMax": {
                                                            "Value": 11000,
                                                            "Multiplier": 0,
                                                            "Unit": "W"
                                                        },
                                                        "RelativeTimeInterval": {
                                                            "start": 0
                                                        }
                                                    },
                                                    {
                                                        "PMax": {
                                                            "Value": 7000,
                                                            "Multiplier": 0,
                                                            "Unit": "W"
                                                        },
                                                        "RelativeTimeInterval": {
                                                            "start": 43200,
                                                            "duration": 43200
                                                        }
                                                    }
                                                ]
                                            },
                                            "SalesTariff": {
                                                "Id": "id1",
                                                "SalesTariffID": 10,
                                                "NumEPriceLevels": 2,
                                                "SalesTariffEntry": [
                                                    {
                                                        "EPriceLevel": 1,
                                                        "RelativeTimeInterval": {
                                                            "start": 0
                                                        }
                                                    },
                                                    {
                                                        "EPriceLevel": 2,
                                                        "RelativeTimeInterval": {
                                                            "start": 43200,
                                                            "duration": 43200
                                                        }
                                                    }
                                                ]
                                            }
                                        }
                                    ]
        self.AC_EVSEStatus = {
                                "NotificationMaxDelay": 0,
                                "EVSENotification": "None",
                                "RCD": False
                            }
