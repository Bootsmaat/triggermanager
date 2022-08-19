from fizprotocol import *
import receiver
import socket, sys, threading, struct
from time import sleep


# class representing connection to pisync
# hold object receiver which asyncronally gets the response 
class conman():
    def __init__(
        self,
        conn_error_cb = None, 
        generic_cb = lambda a: print(f'{a} received')
    ) -> None:

        self.callbacks = {}
        self.cb_i = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rec = receiver.Receiver(self.on_fire_trigger)

        # store callbacks to bind later
        self.bind_error_callback(conn_error_cb)
        self.bind_generic_callback(generic_cb)

    def cleanup(self):
        self.rec.stop()
        self.sock.close()

    def bind_trigger_callback (self, func):
        self.rec.trigger_cb = func

    def bind_error_callback (self, func):
        self.rec.error_cb = func

    def bind_generic_callback (self, func):
        self.rec.generic_event_cb = func

    def send_opc(self, opc):
        print('sending opc: %s' % str(opc))
        data = construct_packet(opc)

        try:
            self.sock.send(data)

        except BrokenPipeError as e:
            print("conman: BrokenPipeError")
            self.rec.stop()
            raise e

        except ConnectionAbortedError as e:
            print("conman: ConnectionAbortedError")
            self.rec.stop()
            raise e

    def connect(self, addr):
        try:
            self.sock.close()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((addr, CONF_PORT))
            self.rec.setSocket(self.sock)
        except OSError as e:
            print('OSError raised')
            raise e
        else:
            self.send_opc(OP_FD)
            self.rec.start()

    # sends all triggers
    def send_trigger(self, triggers):
        self.send_opc(OP_TCLEAR)

        for t in triggers:
            data = construct_packet(OP_TSET, tr_id=t.id, tr_afr=t.activation_frame)
            try:
                self.sock.send(data)
            except ConnectionAbortedError as e:
                print("conman: ConnectionAbortedError")
                self.rec.stop()
                return e
            sleep(.1)

    def send_fiz_config(self, fiz_string):
        data = construct_packet(OP_SET, cat_set=fiz_string)
        try:
            self.sock.send(data)
        except ConnectionAbortedError as e:
            print("conman: ConnectionAbortedError")
            self.rec.stop()
            return e

    def bind_id(self, id, callback):
        self.callbacks[id] = callback

    def on_fire_trigger(self, tr_id):
        if tr_id in self.callbacks:
            print ('on_fire_trigger: trigger %i fired' % tr_id)
            self.callbacks[tr_id] (tr_id)
        else:
            print ('on_fire_trigger: key %i not bound to a callback' % tr_id)