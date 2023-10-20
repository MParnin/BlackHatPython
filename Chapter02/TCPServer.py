import socket
import threading


IP = "0.0.0.0"
PORT = 9998

def main(): 
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # IP address and port for server to listen to 
    server.bind((IP, PORT))

    # Server begins listening
    # Maximum backlog of 5 connections 
    server.listen(5)
    print(f'[*] Listening on {IP}:{PORT}')
    
    # Main loop awaiting a connection
    while True:

        # Receives client socket in client variable
        # Receives connection details in address variable
        client, address = server.accept()
        print(f'[*] Accepted connection from {address[0]}:{address[1]}')

        # Create thread object that points to handle_client function
        client_handler = threading.Thread(target=handle_client, args=(client,))

        # Start thread to handle client connection
        # Main loop is ready to handle another connection
        client_handler.start()

# Receives the client connection and returns simple message to client
def handle_client(client_socket):
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')
        sock.send(b'ACK')

if __name__ == '__main__':
    main()