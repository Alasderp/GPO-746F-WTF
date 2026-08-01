#!/usr/bin/env python3

import serial
import threading
import queue
import time

class SerialProducerConsumer:
    """Read and write threads with queue-based data flow."""

    def __init__(self, port, baudrate=9600):
        self.ser = serial.Serial(port, baudrate, timeout=0.1)
        self.read_queue = queue.Queue(maxsize=10000)
        self.write_queue = queue.Queue()
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._reader, daemon=True).start()
        threading.Thread(target=self._writer, daemon=True).start()
        
    
    def _reader(self):
        while self.running:
            if self.ser.in_waiting:
                data = self.ser.readlines(self.ser.in_waiting)
                try:
                    self.read_queue.put(data, block=False)
                except queue.Full:
                    # Drop oldest if queue is full
                    try:
                        self.read_queue.get_nowait()
                    except queue.Empty:
                        pass
                    self.read_queue.put(data, block=False)
            else:
                time.sleep(0.001)

    def _writer(self):
        while self.running:
            try:
                data = self.write_queue.get(timeout=0.1)
                self.ser.write(data)
                self.write_queue.task_done()
            except queue.Empty:
                continue

    def send(self, data):
        """Queue data for sending."""
        self.write_queue.put(data)

    def receive(self, timeout=1.0):
        """Get received data from the queue."""
        try:
            return self.read_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def stop(self):
        self.running = False
        self.ser.close()
        
        
        
try:   
    # Usage
    pc = SerialProducerConsumer('/dev/ttyS0', 115200)
    pc.start()

    #pc.send(b'AT+CREG?\r\n')
    
    mobileNumber = "+447928428483"
    atCommand = "ATD{0};\r\n".format(mobileNumber)
    pc.send(atCommand.encode())
    
    atCommandPlayDialTone = 'AT+STTONE=1,20,15000\r\n'
    atcommandPlayOffHook = 'AT+STTONE=1,7,5000\r\n'
    atCommandStopAudio = "AT+STTONE=0\r\n"
    
    #pc.send(atCommandPlayDialTone.encode())
    time.sleep(2)
    #pc.send(atCommandStopAudio.encode())
     
    # Process data as it arrives
    while True:
        time.sleep(0.1)
        data = pc.receive()
        if data:
            for lineBytes in data:
                lineString = lineBytes.decode("utf-8")
                print(lineString)
               
                if lineString.find("OK") != -1:
                    print("\nOutgoing call initiated\n")
                elif lineString.find("VOICE CALL: END") != -1:
                    print("\nCall was ended\n")
            
except KeyboardInterrupt:
    pc.send(atCommandStopAudio.encode())
    pc.stop()
except Exception as e:
    pc.send(atCommandStopAudio.encode())
    print(e)
    pc.stop()
finally:
    pc.send(atCommandStopAudio.encode())
    pc.stop()
