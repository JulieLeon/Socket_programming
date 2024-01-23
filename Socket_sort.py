import socket
import argparse

#Constantes
PORT = 32000

# create an INET, STREAMing socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# now connect to the web server on port - the normal http port
s.connect(("localhost", PORT))
# bind the socket to a public host, and a well-known port
s.bind((socket.gethostname(), PORT))
# become a server socket
s.listen()


"""while True:
    # accept connections from outside
    (clientsocket, address) = s.accept()
    # now do something with the clientsocket
    # in this case, we'll pretend this is a threaded server
    ct = client_thread(clientsocket)
    ct.run()"""

