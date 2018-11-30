#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# PSU.py - Jarkko Pesonen <jarpeson@utu.fi>
#   0.1     2018.10.15  Initial version.
#   0.2     2018.11.11  Reviced interface.
#
#
# This class interface uses typing (Python 3.5+) for public methods.
# https://docs.python.org/3/library/typing.html
#
import serial
import time

from Config_02W import Config

#debug level for PSU Class
debug_level = None     #debug_level None: do not print anything
                    #debug level 0: print init sequence
                    #debug_level 1: print init sequence and serial data
                    #debug level 2: print init sequence, serial data and misc.data

class PSU:

    #
    # Object properties
    #
    # instance of serial.Serial
    port    = None

    ###########################################################################
    #
    # Public interface
    #
    # Available via nested class as functions:
    #       PSU().measure.voltage()     float
    #       PSU().measure.current()     float
    # PSU properties:
    #       PSU().power                 bool
    #       PSU().voltage               float
    #       PSU().current_limit         float
    #       PSU().status                str             ["OVER CURRENT" | "OK"]
    #       PSU().port                  serial.Serial
    # PSU functions:
    #       PSU().values_tuple()        tuple
    #       PSU.find()                  str             ["/dev/.." | None]
    #
    # notes
    # PSU requires about 10 seconds for initial startup before using remote interface without handshake  

    class Measure:
        """PSU.Measure - nested class providing beautified naming for measurement functions."""
        def __init__(self, psu):
            self.psu = psu

        def voltage(self) -> float:
            """Read measured voltage from the device."""
            #measure PSU output voltage from P25V channel
            #return value in float -format
            if debug_level == 2: 
                print('voltage measurement ...')
            
            #read output voltage of P25V channel
            output_message = 'Measure:Voltage:DC? P25V'   
            if debug_level == 2: 
                print('output message:',output_message)
            self.psu._PSU__send_message(output_message)
                      
            #read input message
            #raise exception if message is not received  (timeout)
            try:
                input_message_byte=self.psu._PSU__read_message()             
            except ValueError:
                #timeout
                if debug_level is not None: print('ValueError exception')
                raise
            else:
                #message received
                input_message=input_message_byte.decode('utf-8')    #convert to string 
                if debug_level == 2: print('input message:',input_message)          
                measured_voltage = float(input_message)            
                if debug_level == 2: print('measured voltage: {0:2.3f} V'.format(measured_voltage))
                #return value
                return measured_voltage                          


        def current(self) -> float:
            """Read measured current from the device."""
            #measure PSU output current from P25V channel
            #return value in float -format
            if debug_level == 2: 
                print('current measurement ...')

            #read output current of P25V channel
            output_message = 'Measure:Current:DC? P25V'   
            if debug_level == 2: 
                print('output message:',output_message)
            self.psu._PSU__send_message(output_message)
            
            #read input message
            #raise exception if message is not received  (timeout)
            try:
                input_message_byte=self.psu._PSU__read_message()             
            except ValueError:
                #timeout
                if debug_level is not None: print('ValueError exception')
                raise
            else:
                #message received
                input_message=input_message_byte.decode('utf-8')    #convert to string 
                if debug_level == 2: print('input message:',input_message)          
                measured_current = float(input_message)            
                if debug_level == 2: print('measured current: {0:2.3f} A'.format(measured_current))
                return measured_current                 


    @property
    def power(self) -> bool:
        """Read PSU power state ("ON" or "OFF")."""
        #time.sleep(0.3)
        self.__send_message('Output:state?')
        #read input message
        #raise exception if message is not received  (timeout)
        try:
            input_message_byte=self.__read_message()  
        except ValueError:
            #timeout
            if debug_level == 2: print('ValueError exception on reading PSU status')
            raise ValueError('ValueError exception on reading PSU status')
        else:
            #message received
            input_message=input_message_byte.decode('utf-8')    #convert to string 
            PSU_on_off_status = int(input_message)              #convert to int
            if PSU_on_off_status == 1: 
                PSU_power_ON = True
            elif PSU_on_off_status == 0:
                PSU_power_ON = False
            else:
                raise ValueError('value error')
            return PSU_power_ON
		
    @power.setter
    def power(self, value: bool) -> bool:
        """Toggle power output ON or OFF. Setting is read back from the device
        and returned by this function (confirmation)."""  
        if value == True:
            if debug_level==2: print('Power ON')
            self.__send_message('Output:State ON')
        if value == False: 
            self.__send_message('Output:State OFF')
            if debug_level==2: print('Power OFF')
        # self.__send_message("Toggle power output SCPI command...")
        # self.__read_message()
        return self.power

    #for testing only, old version
    @property
    def voltage_set_value_test(self) -> float:
        """Read PSU voltage setting. NOT the same as measured voltage!"""
        time.sleep(0.3)
        #send message
        output_message = 'Source:Voltage:Immediate?'
        print('output message:',output_message)
        self.__send_message(output_message)

        #read input message
        #raise exception if message is not received  (timeout)
        try:
            input_message_byte=self.__read_message()             
        except ValueError:
            #timeout
            print('ValueError exception')
            raise
        else:
             #message received
            input_message=input_message_byte.decode('utf-8')    #convert to string 
            voltage_set_value_from_PSU = float(input_message)
            #debug only
            print('input message:',input_message)
            print('PSC Voltage set value verified:', voltage_set_value_from_PSU)
            #return value
            return voltage_set_value_from_PSU
        #return float(self.__read_message())

    @property
    def voltage(self) -> float:
        """Read PSU voltage setting. NOT the same as measured voltage!"""
        #read voltage set value from PSU
        #return value in float -format
        
        #send message
        output_message = 'Source:Voltage:Immediate?'
        if debug_level == 2: 
            print('output message:',output_message)
        self.__send_message(output_message)
        
        #read input message
        #raise exception if message is not received  (timeout)
        try:
            input_message_byte=self.__read_message()             
        except ValueError:
            #timeout
            if debug_level is not None: print('ValueError exception')
            raise
        else:
             #message received
            input_message=input_message_byte.decode('utf-8')    #convert to string 
            voltage_set_value_from_PSU = float(input_message)
            #debug only
            if debug_level == 2: print('input message:',input_message)
            if debug_level == 2: print('PSU Voltage set value verified (float):', voltage_set_value_from_PSU)
            #return value
            return voltage_set_value_from_PSU
        #return float(self.__read_message())


    @voltage.setter
    #def voltage(self, value: float) -> float:
    def voltage(self, voltage_set_value: float = None) -> float:
        """Set PSU voltage. After setting the value, the setting read back
        and returned. NOTE: This is NOT the measured actual output voltage!"""
        if voltage_set_value:
            output_message = 'Source:Voltage:Immediate {0:1.3f}'.format(voltage_set_value)      #output setting at 1 mV accuracy
            if debug_level == 2: print('output message:',output_message)
            self.__send_message(output_message)
            return self.voltage
         

    @property
    def current_limit(self) -> float:
        """Read PSU current limit setting."""
        output_message = 'Source:Current:Immediate?'
        if debug_level == 2: 
            print('output message:',output_message)
        self.__send_message(output_message)

        #read input message
        #raise exception if message is not received  (timeout)
        try:
            input_message_byte=self.__read_message()             
        except ValueError:
            #timeout
            if debug_level is not None: print('ValueError exception')
            raise
        else:
             #message received
            input_message=input_message_byte.decode('utf-8')    #convert to string 
            current_limit_from_PSU = float(input_message)
            #debug only
            if debug_level == 2: print('input message:',input_message)
            if debug_level == 2: print('PSU current limit verified {0:1.3f}:'.format(current_limit_from_PSU))
            #return value
            return current_limit_from_PSU
      
    @current_limit.setter
    def current_limit(self, current_set_value:float = None) -> float:
        """Set PSU current limit value."""
        if current_set_value:
            output_message = 'Source:Current:Immediate {0:1.3f}'.format(current_set_value)      #current limit setting at 1 mA accuracy
            if debug_level == 2: print('output message:',output_message)
            self.__send_message(output_message)
        return self.current_limit


    @property
    def status(self) -> str:
        """Read PSU Status (has/is current limit reached)."""
        self.__send_message("Query current limit status...")
        return ("OVER CURRENT", "OK")[(self.__read_message() == "<OK string response>")]

    @property
    def values(self) -> dict:
        """Returns a tuple for SQL INSERT."""
        return dict({
            "power"               :"ON" if self.power else "OFF",
            "voltage_setting"     :self.voltage,
            "current_limit"       :self.current_limit,
            "measured_current"    :self.measure.current(),
            "measured_voltage"    :self.measure.voltage(),
            "state"               :self.state
        })

#    def values_tuple(self) -> tuple:
#        """Returns a tuple for SQL INSERT."""
#        return (
#            "ON" if self.power else "OFF",
#            self.voltage,
#            self.current_limit,
#            self.measure.current(),
#            self.measure.voltage(),
#            self.status
#        )


    ###########################################################################
    #
    # Static method for finding the correct port
    #
    # NOTE: Completely untested.
    #
    @staticmethod
    def find() -> str:
        """Finds Agilent PSU from available serial devices.
        Return device file name or None if not found."""
        def transact(port, command: str) -> str:
            """Argument 'command' of type str. Returns type str"""
            port.write(command.encode('utf-8'))
            line = port.readline()
            # If the last character is not '\n', we had a timeout
            if line[-1:] != b'\n':
                raise ValueError(
                    "Serial read timeout! ({}s)".format(port.timeout)
                )
            return line.decode('utf-8')
        def found_at(port: str) -> bool:
            """Guaranteed to return True or False, depending on if the PSU is
            detected at the provided port."""
            def valid_firmware_string(firmware: str) -> bool:
                """Validate 'yyyy.x' version string.
                Returns True is meets criteria, False if not."""
                try:
                    if len(firmware) < len("yyyy.x"):
                        raise ValueError()
                    if firmware[4:5] != '.':
                        raise ValueError()
                    int(firmware[0:4])
                    int(firmware[5:6])
                except:
                    return False
                return True
            result = None
            try:
                port = serial.Serial(
                    port          = port,
                    baudrate      = Config.PSU.Serial.baudrate,
                    parity        = Config.PSU.Serial.parity,
                    stopbits      = Config.PSU.Serial.stopbits,
                    bytesize      = Config.PSU.Serial.bytesize,
                    timeout       = 0.1,
                    write_timeout = None
                )
                # Assuming 'yyyy.xx' return format
                response = transact(port, 'System:Version?')
                result = valid_firmware_string(response)
            except:
                result = False
            finally:
                try:
                    port.close()
                except:
                    pass
            return result or False
        #
        # PSU.find() block begins
        #
        import serial.tools.list_ports
        port = None
        for p in serial.tools.list_ports.comports(include_links=False):
            if found_at(p):
                port = p
                break
        return port



    ###########################################################################
    #
    # PSU "Private" methods
    #
    #   These may be freely changed. Client code will NOT access any of these
    #   methods.
    #
    #   NOTE: __init__() signature must remain as specified.
    #
    def __init__(self, port = None):
        """Initialize object and test that we are connected to PSU by issuing a version query.
        If port argument is omitted, Config.PSU.Serial.port is used."""
        self.measure = self.Measure(self) # <- must be here
        # def __init__(self,serial_port1,read_timeout):
        """Copied from 'PSU_class_010.py', 09.11.2018."""
        #initialize and open serial port
        #raise SerialException if device cannot be configured
        #raise ValueException if parameters are out of range

        #serial interface
        port          = port
        #port          = "COM14"
        baudrate      = Config.PSU.baudrate
        bytesize      = Config.PSU.bytesize
        parity        = Config.PSU.parity
        stopbits      = Config.PSU.stopbits
        timeout       = Config.PSU.timeout
        write_timeout = None
        xonxoff       = False
        rtscts        = False
        dsrdtr        = True
        #note: port -parameter is needed to scan serial ports
        #note: port and timeout is not read from config.py -file
        #note: change to self ? reading directly from here       
        if debug_level is not None: print('init port {0:s}..... '.format(port),end='')

        #print('init port',port,'..... ',end='')     #Python 3.0 or newer version required
        
        #open serial port
        try:
            self.serial_port = serial.Serial(port,baudrate,bytesize,parity,
                                        stopbits,timeout,xonxoff,rtscts,
                                        write_timeout,dsrdtr)
        except:
            if debug_level is not None: print('failed')
            raise
        else:
            if debug_level is not None: print('OK')
          
            #set remote mode
            if debug_level is not None: print('Remote mode')
            self.__set_remote_mode()

            #set power ON
            if debug_level is not None:
                if debug_level == 0: 
                    print('PSU POWER ON .....',end='')
                else: print('PSU POWER ON .....')
            
            try:
                self.power = True       #Turn PSU ON
            except:
                if debug_level is not None:
                    if debug_level == 0: print('failed')
                    else: print('PSU Power ON failed')
                raise ValueError('PSU Power ON failed')
            else:
                #check ON/OFF status from PSU
                if debug_level == 2: print('check ON/OFF status from PSU')
                try:
                    PSU_status = self.power 
                except:
                    if debug_level is not None:
                        print('failed')
                        print('ON/OFF status not verified')
                    raise ValueError('ON/OFF status not verified')
                else:
                    if PSU_status == False:      #should be True during Init
                        if debug_level is not None: print('failed')
                        raise ValueError('ON/OFF status not verified')
                    else:    
                        if debug_level is not None: print('ok')     
                                                
                        #select +25 V channel
                        if debug_level is not None:    
                            if debug_level == 0: 
                                print('select +25 V channel .....',end='')
                            else: print('select +25 V channel .....')
                        self.__select_channel('P25V')
                        #read and verify selected channel
                        selected_channel_from_PSU=self.__read_selected_channel()
                        if debug_level == 2: print('channel',selected_channel_from_PSU)
                        if selected_channel_from_PSU[0:4] == 'P25V':
                            if debug_level==0: 
                                print('ok')
                            if debug_level == 1 or debug_level == 2: print('+25V channel verified')

               
                            #set default voltage
                            if debug_level is not None:  
                                if debug_level == 0:
                                    print('set output voltage to {0:1.3f} V ......'.format(Config.PSU.default_voltage),end='') 
                                else: 
                                    print('set output voltage to {0:1.3f} V ......'.format(Config.PSU.default_voltage)) 
                            self.voltage=Config.PSU.default_voltage
                            #verify default voltage
                            voltage_set_value_from_PSU = self.voltage
                            if voltage_set_value_from_PSU == Config.PSU.default_voltage:
                                if debug_level is not None: print('ok')
                                if debug_level == 2:
                                    print("PSU voltage set value verified : {0:1.3f} V".format(voltage_set_value_from_PSU))
                                
                                #set current_limit 
                                if debug_level is not None:
                                    if debug_level == 0:
                                        print('set current limit to {0:1.3f} A ......'.format(Config.PSU.default_current_limit),end='') 
                                    else:
                                        print('set current limit to {0:1.3f} A ......'.format(Config.PSU.default_current_limit)) 
                                self.current_limit=Config.PSU.default_current_limit
                                #verify current limit
                                current_limit_from_PSU = self.current_limit
                                if current_limit_from_PSU == Config.PSU.default_current_limit:
                                    if debug_level is not None: print('ok')
                                    if debug_level == 2:
                                        print("PSU current limit verified : {0:1.3f} A".format(current_limit_from_PSU))
                                    if debug_level is not None: print('PSU ready')  #init sequence complete
                                    
                                    if debug_level==2:
                                        #measurement test
                                        measured_voltage=self.measure.voltage()
                                        print("measured voltage: {0:2.3f} V".format(measured_voltage))
                                        measured_current=self.measure.current()
                                        measured_current_mA=1000*measured_current
                                        print("measured current: {0:3.3f} mA".format(measured_current))  

                                else:
                                    if debug_level is not None: print('failed')
                                    if debug_level ==1 or debug_level == 2:
                                        print("PSU current limit: {0:1.3f} A".format(current_limit_from_PSU))  
                                    raise ValueError('Current limit setting not verified')
                            else:
                                if debug_level is not None: print('failed')
                                if debug_level == 1 or debug_level == 2:
                                    print("PSU voltage set value: {0:1.3f} V".format(voltage_set_value_from_PSU))  
                                raise ValueError('Output voltage setting not verified')
                        else:
                            if debug_level==0: print('failed')
                            if debug_level == 1 or debug_level == 2: print('selected channel not verified')
                            raise ValueError('selected channel not verified')
  
             
    def __send_message(self,message_data_str_out):
        """Copied from 'PSU_class_010.py', 09.11.2018."""
    
        #add LF and CR characters to the end of message 
        LF_char = 0x0A      #integer, Line feed
        CR_char = 0x0D      #integer, Carriage return
        LF_str = "{0:1c}".format(LF_char)
        CR_str = "{0:1c}".format(CR_char)            
        output_message = message_data_str_out+CR_str+LF_str
        output_message_byte=output_message.encode('utf-8')

        #write data to serial port
        bytes_written=self.serial_port.write(output_message_byte)

        #todo: test if no exceptions
        if debug_level == 1 or debug_level==2: print('send:',message_data_str_out)
        if debug_level == 2: print('bytes written:',bytes_written)
        return


    def __read_message(self):
        """read message from PSU
        Copied from 'PSU_class_010.py', 09.11.2018."""
        #read message from PSU
        #return bytestring
        #raises ValueError if message is not received

        if debug_level == 2: print('read timeout:',self.serial_port.timeout)
        #received_message_bytes=self.serial_port.read(4) #read 4 bytes from serial
        received_message_bytes=self.serial_port.read_until(b'\r\n',20) #read max. 20 bytes from serial
        if received_message_bytes[-1:] != b'\n': 
            if debug_level == 2: print ('timeout {0:1.2f} s'.format(self.serial_port.timeout))
            raise ValueError("Serial read timeout! ({0:1.2f} s)".format(self.serial_port.timeout))
            
        else:
            if debug_level == 1 or debug_level == 2: print('received:',received_message_bytes)
        return received_message_bytes       #return bytestring

    def read_selected_channel(self):
        #read selected channel from PSU
        selected_channel_from_PSU=self.__read_selected_channel()
        return selected_channel_from_PSU      

    def __read_selected_channel(self):
        #read selected channel from PSU
        #return selected channel in str format
        if debug_level == 2: 
            print('read selected channel')
        output_message = 'Instrument:Select?'
        self.__send_message(output_message)
        #read input message
        #raise exception if message is not received  (timeout)
        try:
            input_message_byte=self.__read_message()              
        except ValueError:
            #timeout
            if debug_level == 1 or debug_level ==2: print('ValueError exception')
            raise       
        else:
             #message received
            input_message=input_message_byte.decode('utf-8')    #convert to string 
            return input_message            

    #test only
    def select_channel_long_msg(self,channel):
        """test purpose only"""
        self.__select_channel_long_msg(channel)

    #test only
    def select_channel(self,channel):
        """test purpose only"""
        self.__select_channel(channel)



    #long message 
    def __select_channel_long_msg(self, channel='P6V'):
        """Copied from 'PSU_class_010.py', 09.11.2018."""
        #assert(channel in ['P6V', 'P25V','N25V'])
        output_message = 'Instrument:Select {0:s}'.format(channel)
        if debug_level == 2: print('output message:',output_message)
        self.__send_message(output_message)
        return

    #short message
    def __select_channel(self, channel='P6V'):
        """Copied from 'PSU_class_010.py', 09.11.2018."""
        #assert(channel in ['P6V', 'P25V','N25V'])
        output_message = 'INST:SEL {0:s}'.format(channel)
        if debug_level == 2: print('output message:',output_message)
        self.__send_message(output_message)
        return    

    
    def check_SCPI_version(self):
        """test purpose only"""
        self.__check_SCPI_version()

    #old version
    def __check_SCPI_version(self,version='-'):
        """Copied from 'PSU_class_010.py', 09.11.2018."""
        #check if version is equal to SCPI version of the PSU
        #compare bytestrings
                        
        #Version format is YYYY.V
        correct_version="1995.0"
        print('Checking SCPI version ..... ',end='')
        #correct_version_byte=correct_version.encode('utf-8')
      
        #LF_str = "{0:1c}".format(LF_char)
        #if input_message_byte[0]==correct_version_byte[0]:
        if version[0] == correct_version[0]:
            print('ok')
            return True    
        else:
            print('failed') 
            return False
              
            #raise NameError('Version not found')
            #raise ValueError

    def set_remote_mode(self):
        self.__send_message("System:Remote")

    def __set_remote_mode(self):
        #time.sleep(0.3)
        self.__send_message("System:Remote")

    def get_version(self):
        """test purpose only"""
        input_message=self.__get_version()
        return input_message

    def __get_version(self):
        """Read SCPI -version from PSU
        Copied from 'PSU_class_010.py', 09.11.2018."""
        #read SCPI -version from PSU
        #returns SCPI -version of the PSU in string -format
        #raises ValueError if version is not found

        self.__send_message("System:Version?")
        print()
        #read input message
        #raise exception if message is not received  (timeout)
        try:
            input_message_byte=self.__read_message()  
             
        except ValueError:
            #timeout
            if debug_level is not None: print('ValueError exception')
            raise
        
        else:
             #message received
            input_message=input_message_byte.decode('utf-8')    #convert to string 
            
            #test only
            version_number=float(input_message)
            version_number=version_number+0.002
            if debug_level is not None: print('SCPI version in str:',input_message)
            if debug_level is not None: print('SCPI version in float:', version_number)
            
            return input_message            



    #
    # Support for 'with' -statement. These should be left unmodified.
    #
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.port.close()




if __name__ == "__main__":
    """Basic test"""
    import os


    print("Finding PSU...", end="", flush=True)
    try:
        port = PSU.find()
        if not port:
            print("not found!")
            os._exit(-1)
    except:
        print("\nAbnormal termination!")
        raise


    with PSU(port) as psu:
        print(psu.values_tuple)


        psu.power = False
        psu.voltage = 3.3
        psu.current_limit = 0.3
        if psu.measure.voltage() > 0.02:
            raise ValueError("Unexpected voltage at terminal!")


        psu.power = True
        if abs(psu.measure.voltage() - psu.voltage) > 0.05:
            raise ValueError("Unexpected voltage difference between set and measured values!")


        print(psu.values_tuple)
        psu.power = False

        """
        except Exception as ex:
            print('other exception')
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print ("exeption1:",message)
            raise"""

# EOF
