import socket
import json

MAX_SEQ = 3
flag2 = 0
def inc(k):
    if k < MAX_SEQ:
        k = k + 1
    else:
        k = 0
    return k

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 1234))
s.listen(5)
clientsocket, address = s.accept()
print(f"Connection from {address} has been established.")

if __name__ == "__main__":
    frame_expected = 0
    while True:
        msg = clientsocket.recv(56)
        if len(msg) <= 0:
            continue
        frame_recieved = json.loads(msg.decode("utf-8"))
        print(f"\nFrame {frame_recieved['seqNum']} recieved ")
        print(frame_recieved)
        # if  frame_recieved["seqNum"] == 2 and flag2 == 0 :
        #     flag2 = 1
        #     continue
        # elif frame_recieved["seqNum"] == 2 and flag2 == 1 :
        #     flag2 = 0
        if(frame_recieved["seqNum"] == frame_expected):    
            frame_recieved["ack"] = frame_recieved["seqNum"]
            frame_recieved["seqNum"] = 4
            clientsocket.send(bytes(json.dumps(frame_recieved),"utf-8"))
            print(f"\nsent ack for {frame_recieved['ack']}")
            frame_expected = inc(frame_expected)