import socket
import threading
import json
import random
import os
import string
import select

# control flags
timeout = 0
networkEnable=0
missedFrame = 100
networkEnable = None
MAX_SEQ = 3

#initialize socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1234))

# mapping the frame with its timer
frame_timer = []

# protocol helper functions
# /*Macro inc is expanded in - line: increment k circularly.*/
#define 
def inc(k):
    if k < MAX_SEQ:
        k = k + 1
    else:
        k = 0
    return k

def wait_for_event():

    global timeout
    ready_sockets, _, _ = select.select ([s], [], [], 0)

    if ready_sockets:
        return 1
    elif timeout:
        timeout=0
        return 2
    elif networkEnable:
        return 3
    else:
        return 0

        
def enable_network_layer():
    global networkEnable 
    networkEnable = 1

def disable_network_layer():
    global networkEnable
    networkEnable = 0


def from_network_layer():
    packet = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return packet


def to_physical_layer(r):
    s.send(bytes(json.dumps(r),"utf-8"))

def from_physical_layer():
    msg = s.recv(56)
    r = json.loads(msg.decode("utf-8"))
    return r
def start_timer(seq_frame):
    timer = threading.Timer(5.0, timer_callBack, [seq_frame]) 
    frame_timer[seq_frame]["timer"] = timer
    timer.start()

def stop_timer(seq_frame):
    frame_timer[seq_frame]["timer"].cancel()

def delay():
    for j in range(1000000):
        x = None

def timer_callBack(frameNum): 
    print(f"\n Frame {frameNum} timeout") 
    missedFrame = frameNum
    global timeout
    timeout=1

def to_network_layer(packet):
    packetq = ""

def between(a, b, c):
    # /*Return true if a <= b < c circularly; false otherwise.*/
    if (((a <= b) and (b < c)) or ((c < a) and (a <= b)) or ((b <=c) and (c < a))):
        return True 
    else:
        return False

    
def send_data( frame_nr,frame_expected,buffer):

    s = {"seqNum":frame_nr, "ack": (frame_expected + MAX_SEQ) % (MAX_SEQ + 1), "info": buffer[frame_nr],"kind":"data"}
    to_physical_layer(s)
    start_timer(frame_nr)
    print(f"{s}")
    delay()


if __name__ == "__main__":

    buffer=["","","",""] #/* buffers for the outbound stream */

    enable_network_layer() #/* allow network layer ready events */
    ack_expected = 0 #/* next ack expected inbound */
    next_frame_to_send = 0 #/* next frame going out */
    frame_expected = 0 #/* number of frame expected inbound */
    nbuffered = 0     # /* initially no packets are buffered */

    #initialize frame timers
    for i in range(MAX_SEQ+1):
        frame_timer.append({"seqNum": i, "timer":None})
    while True:
        event = wait_for_event()
        # network layer ready
        if event == 3:
            buffer[next_frame_to_send] = from_network_layer() # /* fetch new packet */
            nbuffered = nbuffered + 1 #/* expand the sender’s window */
            print(f"\nFrame {next_frame_to_send} sent")
            send_data(next_frame_to_send, frame_expected, buffer) #/* transmit the frame */
            next_frame_to_send = inc(next_frame_to_send)  # /* advance sender’s upper window edge */

        #frame arrival
        elif event == 1:
            r=from_physical_layer()   # /* get incoming frame from physical layer */
            if r["seqNum"] == frame_expected:   #/*Frames are accepted only in order. */
                to_network_layer(r["info"]) #/* pass packet to network layer */
                frame_expected=inc(frame_expected) #/* advance lower edge of receiver’s window */
                    
            while between(ack_expected, r["ack"], next_frame_to_send):
                # /*Handle piggybacked ack. */
                nbuffered = nbuffered - 1 # /* one frame fewer buffered*/
                stop_timer(ack_expected)  #/* frame arrived intact; stop timer */
                print(f"\nframe {r['ack']} acked")
                ack_expected = inc(ack_expected)  #/* contract sender’s window */

        #timeout
        elif event == 2:
            next_frame_to_send = ack_expected  #/* start retransmitting here */
            # stopping all timers for re-transmisiion
            temp = next_frame_to_send
            for j in range(nbuffered):
                stop_timer(temp)
                temp = inc(temp)
            #re-transmission
            for i in range(nbuffered):
                print(f"\nframe {next_frame_to_send} retransmitted")
                send_data(next_frame_to_send, frame_expected, buffer)#/* resend frame */
                next_frame_to_send = inc(next_frame_to_send) #/* prepare to send the next one */

        if (nbuffered <= MAX_SEQ):
            enable_network_layer()
        else:
            disable_network_layer()


      