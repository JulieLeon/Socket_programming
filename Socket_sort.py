import socket
import argparse

#Constantes
PORT = 32000
MESSAGE1 = b'Hello'
MESSAGE2 = b'Hi'

#Arguments
parser = argparse.ArgumentParser(description='A parallelized sort usinig sockets', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-s','--server',action='store_true', help='Run as server')
parser.add_argument('--host', default='localhost')
args = parser.parse_args()

# create an INET, STREAMing socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if args.server :
    # bind the socket to a public host, and a well-known port
    s.bind(('', PORT)) 
    # become a server socket
    s.listen()
    (clientsocket, address) = s.accept()
    text = clientsocket.recv(len(MESSAGE1))
    print(str(text))
    clientsocket.send(MESSAGE2)

else :
    # now connect to the web server on port - the normal http port
    s.connect((args.host, PORT))
    s.send(MESSAGE1)
    text2 = s.recv(len(MESSAGE2))
    print(str(text2))








"""while True:
    # accept connections from outside
    (clientsocket, address) = s.accept()
    # now do something with the clientsocket
    # in this case, we'll pretend this is a threaded server
    ct = client_thread(clientsocket)
    ct.run()"""

