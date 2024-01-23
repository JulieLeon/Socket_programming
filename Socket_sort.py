import socket
import argparse

#Constantes
PORT = 32000
MESSAGE1 = b'Hello'

#Arguments
parser = argparse.ArgumentParser(description='A parallelized sort usinig sockets', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-s','--server',action='store_true', help='Run as server')
args = parser.parse_args()

if args.server :
    # create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host, and a well-known port
    s.bind((socket.gethostname(), PORT)) 
    # become a server socket
    s.listen()
    (clientsocket, address) = s.accept()
    text = clientsocket.recv(len(MESSAGE1))

else :
    # create an INET, STREAMing socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # now connect to the web server on port - the normal http port
    serversocket.connect(("localhost", PORT))
    serversocket.send(MESSAGE1)








"""while True:
    # accept connections from outside
    (clientsocket, address) = s.accept()
    # now do something with the clientsocket
    # in this case, we'll pretend this is a threaded server
    ct = client_thread(clientsocket)
    ct.run()"""

