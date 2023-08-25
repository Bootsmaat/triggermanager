from fizprotocol import *
import receiver
import socket, sys, threading, struct
from time import sleep

# interval between status polls in s
POLL_TIMEOUT = 4


# class representing connection to pisync
# hold object receiver which asyncronally gets the response 
class conman():
    def __init__(
        self,
        conn_error_cb = None, 
        generic_cb = None,
        status_update_cb = None
    ) -> None:

        self.callbacks = {}
        self.cb_i = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receiver = receiver.Receiver(self.on_fire_trigger)
        
        self.error_cb = conn_error_cb

        self.lock = threading.Lock()
        self.stop_signal = threading.Event()
        self.send_signal = threading.Event()

        # store callbacks to bind later
        self.bind_error_callback(conn_error_cb)
        self.bind_generic_callback(generic_cb)
        self.receiver.status_update_cb = status_update_cb

    def __del__(self):
        print("cleaning up conman")
        self.cleanup()

    def cleanup(self):
        # TODO maybe have receiver listen to the same stop signal
        self.receiver.stop()
        self.stop_signal.set()

        try:
            self.receiver.join(2) #added a 2 second timeout so it doesn't halt quiting the application TODO: FIX THIS
            self.status_poller.join(2)
        except RuntimeError:
            print("trying to close thread but not open yet")
        except Exception as e: print(e)

        self.sock.close()

    def bind_trigger_callback (self, func):
        self.receiver.trigger_cb = func

    def bind_error_callback (self, func):
        self.receiver.error_cb = func

    def bind_generic_callback (self, func):
        self.receiver.generic_event_cb = func

    def send_opc(self, opc):
        print('sending opc: %s' % str(opc))
        data = construct_packet(opc)

        try:
            self.lock.acquire()
            self.sock.send(data)
            self.lock.release()

        except BrokenPipeError as e:
            print("conman: BrokenPipeError")
            self.receiver.stop()
            self.lock.release()
            self.stop_signal.set()
            self.error_cb(e)
            raise e

        except ConnectionAbortedError as e:
            print("conman: ConnectionAbortedError")
            self.receiver.stop()
            self.lock.release()
            self.stop_signal.set()
            self.error_cb(e)
            # raise e

    def connect(self, addr):
        try:
            self.sock.close()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((addr, CONF_PORT))
            self.receiver.setSocket(self.sock)
            self.send_signal.set()

            def poll_status(conn, stop_signal, send_signal):
                while(True):
                    if (send_signal.is_set()):
                        conn.send_opc(OP_STATUS)

                    sleep(POLL_TIMEOUT)

                    if (stop_signal.is_set()):
                        return

            self.stop_signal.clear()
            self.status_poller = threading.Thread(
                name='status_poller', 
                target=lambda : poll_status(self, self.stop_signal, self.send_signal))
            self.status_poller.start()

        except OSError as e:
            print('OSError raised')
            raise e
        else:
            self.send_opc(OP_FD)
            self.receiver.start()

    # sends all triggers
    def send_trigger(self, triggers):
        self.send_opc(OP_TCLEAR)

        for t in triggers:
            data = construct_packet(OP_TSET, tr_id=t.id, tr_afr=t.activation_frame)
            try:
                self.lock.acquire()
                self.sock.send(data)
                self.lock.release()
            except ConnectionAbortedError as e:
                print("conman: ConnectionAbortedError")
                self.receiver.stop()
                return e
            sleep(.1)

    def send_fiz_config(self, fiz_string):
        data = construct_packet(OP_SET, cat_set=fiz_string)
        try:
            self.lock.acquire()
            self.sock.send(data)
            self.lock.release()
        except ConnectionAbortedError as e:
            print("conman: ConnectionAbortedError")
            self.receiver.stop()
            return e

    def bind_id(self, id, callback):
        self.callbacks[id] = callback

    def on_fire_trigger(self, tr_id):
        if tr_id in self.callbacks:
            print ('on_fire_trigger: trigger %i fired' % tr_id)
            self.callbacks[tr_id] (tr_id)
        else:
            print ('on_fire_trigger: key %i not bound to a callback' % tr_id)