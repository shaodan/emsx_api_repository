import blpapi
import sys
import datetime


SESSION_STARTED         = blpapi.Name("SessionStarted")
SESSION_STARTUP_FAILURE = blpapi.Name("SessionStartupFailure")
SERVICE_OPENED          = blpapi.Name("ServiceOpened")
SERVICE_OPEN_FAILURE    = blpapi.Name("ServiceOpenFailure")
ERROR_INFO              = blpapi.Name("ErrorInfo")
CREATE_ORDER            = blpapi.Name("CreateOrder")

d_service="//blp/emapisvc_beta"
# d_service="//blp/emapisvc"
d_host="localhost"
d_port=8194
bEnd=False


class SessionEventHandler():

    def processEvent(self, event, session):
        print("event type:", event.eventType())
        try:
            if event.eventType() == blpapi.Event.SESSION_STATUS:
                self.processSessionStatusEvent(event,session)
            
            elif event.eventType() == blpapi.Event.SERVICE_STATUS:
                self.processServiceStatusEvent(event,session)

            elif event.eventType() == blpapi.Event.RESPONSE:
                self.processResponseEvent(event)
            
            else:
                self.processMiscEvents(event)
                
        except:
            print ("Exception:  %s" % sys.exc_info()[0])
            
        return False


    def processSessionStatusEvent(self,event,session):  
        print ("Processing SESSION_STATUS event")

        for msg in event:
            print("msg: type ", msg.messageType())
            if msg.messageType() == SESSION_STARTED:
                print ("Session started...")
                session.openServiceAsync(d_service)
                print("openServiceAsync finished")
                
            elif msg.messageType() == SESSION_STARTUP_FAILURE:
                print >> sys.stderr, ("Error: Session startup failed")
                
            else:
                print (msg)
                

    def processServiceStatusEvent(self,event,session):
        print ("Processing SERVICE_STATUS event")
        
        for msg in event:
            print("msg: type ", msg.messageType())
            if msg.messageType() == SERVICE_OPENED:
                print ("Service opened...")

                service = session.getService(d_service)
    
                request = service.createRequest("CreateOrderAndRouteEx")

                # The fields below are mandatory
                request.set("EMSX_TICKER", "510900 CH Equity")
                request.set("EMSX_AMOUNT", 100)
                request.set("EMSX_ORDER_TYPE", "LMT")
                request.set("EMSX_LIMIT_PRICE", 1.17)
                request.set("EMSX_TIF", "DAY")
                request.set("EMSX_HAND_INSTRUCTION", "DOT")  # MAN-手工下单，DOT-DMA下单
                request.set("EMSX_SIDE", "SELL")
                request.set("EMSX_BROKER", "CSEC")
#                 request.set("EMSX_ACCOUNT", "testAccount") # 多账户下单

            
                # The fields below are optional
                #request.set("EMSX_ACCOUNT","TestAccount")
                #request.set("EMSX_BASKET_NAME", "HedgingBasket")
                #request.set("EMSX_BROKER", "BMTB")
                #request.set("EMSX_CFD_FLAG", "1")
                #request.set("EMSX_CLEARING_ACCOUNT", "ClrAccName")
                #request.set("EMSX_CLEARING_FIRM", "FirmName")
                #request.set("EMSX_CUSTOM_NOTE1", "Note1")
                #request.set("EMSX_CUSTOM_NOTE2", "Note2")
                #request.set("EMSX_CUSTOM_NOTE3", "Note3")
                #request.set("EMSX_CUSTOM_NOTE4", "Note4")
                #request.set("EMSX_CUSTOM_NOTE5", "Note5")
                #request.set("EMSX_EXCHANGE_DESTINATION", "ExchDest")
                #request.set("EMSX_EXEC_INSTRUCTION", "Drop down values from EMSX Ticket")
                #request.set("EMSX_GET_WARNINGS", "0")
                #request.set("EMSX_GTD_DATE", "20170105")
                #request.set("EMSX_INVESTOR_ID", "InvID")
                #request.set("EMSX_LIMIT_PRICE", 123.45)
                #request.set("EMSX_LOCATE_BROKER", "BMTB")
                #request.set("EMSX_LOCATE_ID", "SomeID")
                #request.set("EMSX_LOCATE_REQ", "Y")
                #request.set("EMSX_NOTES", "Some notes")
                #request.set("EMSX_ODD_LOT", "0")
                #request.set("EMSX_ORDER_ORIGIN", "")
                #request.set("EMSX_ORDER_REF_ID", "UniqueID")
                #request.set("EMSX_P_A", "P")
                #request.set("EMSX_RELEASE_TIME", 34341)
                #request.set("EMSX_REQUEST_SEQ", 1001)
                #request.set("EMSX_SETTLE_CURRENCY", "USD")
                #request.set("EMSX_SETTLE_DATE", 20170106)
                #request.set("EMSX_SETTLE_TYPE", "T+2")
                #request.set("EMSX_STOP_PRICE", 123.5)
                            
                print ("Request: %s" % request.toString())
                    
                self.requestID = blpapi.CorrelationId()
                
                session.sendRequest(request, correlationId=self.requestID)
                print(datetime.datetime.now())
                            
            elif msg.messageType() == SERVICE_OPEN_FAILURE:
                print >> sys.stderr, ("Error: Service failed to open")        
                
    def processResponseEvent(self, event):
        print ("Processing RESPONSE event")
        
        for msg in event:
            
            print ("MESSAGE: %s" % msg.toString())
            print ("CORRELATION ID: %d" % msg.correlationIds()[0].value())
            
            if msg.correlationIds()[0].value() == self.requestID.value():
                print(datetime.datetime.now())
                if msg.messageType() == ERROR_INFO:
                    errorCode = msg.getElementAsInteger("ERROR_CODE")
                    errorMessage = msg.getElementAsString("ERROR_MESSAGE")
                    print ("ERROR CODE: %d\tERROR MESSAGE: %s" % (errorCode,errorMessage))
                elif msg.messageType() == CREATE_ORDER:
                    emsx_sequence = msg.getElementAsInteger("EMSX_SEQUENCE")
                    message = msg.getElementAsString("MESSAGE")
                    print ("EMSX_SEQUENCE: %d\tMESSAGE: %s" % (emsx_sequence,message))
                else:
                    print ("MESSAGE TYPE: %s" % msg.messageType())
                global bEnd
                bEnd = True
                
    def processMiscEvents(self, event):
        print ("Processing " + event.eventType() + " event")
        for msg in event:
            print ("MESSAGE: %s" % (msg.tostring()))

sessionOptions = blpapi.SessionOptions()
sessionOptions.setServerHost(d_host)
sessionOptions.setServerPort(d_port)

print ("Connecting to %s:%d" % (d_host,d_port))

eventHandler = SessionEventHandler()

session = blpapi.Session(sessionOptions, eventHandler.processEvent)

if session.startAsync(): 
    while bEnd==False:
        pass
    session.stop()
else:
    print ("Failed to start session.")
