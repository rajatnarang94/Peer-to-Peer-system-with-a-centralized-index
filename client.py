import socket
from random import randint
import _thread
import os
from datetime import datetime
from pytz.reference import LocalTimezone
from platform import platform


class Client:
    def __init__(self):
        self.server_IP = socket.gethostbyname('localhost')
        self.server_port = 7734

        self.client_socket = socket.socket()
        self.client_host_name = socket.gethostname() + "@" + str(randint(1, 1000))

        self.upload_server_port = 1024 + randint(1, 48000)
        self.upload_server_socket = socket.socket()
        self.upload_server_socket.bind(('', self.upload_server_port))
        self.is_connected = False

    def p2p_get(self, _request):
        response = self.send_request(_request)
        print('\033[91m' + response + '\033[0m')
        content = response.split('\n')
        if response is None or len(content) < 2:
            return

        rfc = [x.strip() for x in content[1].split()]
        rfc_no, rfc_title, peer_hostname, peer_port_no = rfc[0], rfc[1], rfc[2], int(rfc[3])

        receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        peer_hostname = peer_hostname.split('@')[0].strip()
        receive_socket.connect((peer_hostname, peer_port_no))

        receive_socket.send(rfc_title.encode())

        meta_data = receive_socket.recv(4096).decode()
        if meta_data == 'P2P-CI/1.0 404 Not Found' or meta_data == 'P2P-CI/1.0 400 Bad Request':
            print(meta_data)
            return

        # Need to check this, since recv is a blocking call, this while loop won't exit, unless something like a empty
        # string or EOF(maybe) is received
        # Ans: once the other side closes the connection, the received data field would get 0 bytes and then this loop exits
        # if you don't call c.close() then this loop doesn't terminate
        f = open(rfc_title + ".txt", 'w')
        received_data = receive_socket.recv(4096).decode()
        while received_data:
            f.write(received_data)
            received_data = receive_socket.recv(4096).decode()

        f.close()
        print('RFC downloaded')
        add_request = ['ADD RFC ' + rfc_no + ' P2P-CI/1.0', 'Host: ' + self.client_host_name,
                       'Port: ' + str(self.upload_server_port), 'Title: ' + rfc_title]
        add_request = "\n".join(add_request)
        response = self.send_request(add_request)

        print('\033[91m' + response+ '\033[0m')
        receive_socket.close()

    def connect_to_server(self):
        self.client_socket.connect((self.server_IP, self.server_port))
        _request = "Host: " + self.client_host_name + "\nPort: " + str(self.upload_server_port)
        self.client_socket.send(_request.encode())
        response = self.client_socket.recv(4096).decode()
        return response

    def send_request(self, _request):
        self.client_socket.send(_request.encode())
        response = self.client_socket.recv(4096).decode()
        return response

    def upload_server_process(self):
        self.upload_server_socket.listen(5)
        while True:
            c, addr = self.upload_server_socket.accept()
            rfc_title = c.recv(4096).decode().strip()
            if rfc_title:
                try:
                    statinfo = os.stat(rfc_title + '.txt')
                    lastModified = datetime.fromtimestamp(statinfo.st_mtime).strftime('%a, %d %b %Y %H:%M:%S %Z')
                    reply = ["P2P-CI/1.0 200 OK"]
                    reply.append(
                        "Date:" + datetime.now().strftime('%a,%d %b %Y %H:%M:%S') + " " + LocalTimezone().tzname(
                            datetime.now()))
                    reply.append("OS:" + platform())
                    reply.append("Last-Modified:" + lastModified + " " + LocalTimezone().tzname(datetime.now()))
                    reply.append("Content-Length:" + str(statinfo.st_size))
                    reply.append("Content-Type:text/text")
                    c.send("\n".join(reply).encode())

                    with open(rfc_title + ".txt") as file:
                        for line in file:
                            c.send(line.encode())
                    c.close()
                except:
                    return "P2P-CI/1.0 400 Bad Request"


if __name__ == '__main__':
    client = Client()
    while True:
        response = ''
        if not client.is_connected:
            option = input('Connect to Server, (y/n)? ')
            if option == 'y' and not client.is_connected:
                _thread.start_new_thread(client.upload_server_process, ())
                response = client.connect_to_server()
                client.is_connected = True
        else:
            option = input(
                "Hello!!\n" + "List of methods available:\n" + "1. ADD: add an RFC to the peer to peer network\n"
                + "2. LOOKUP: find peers that have a specified RFC\n" + "3. LIST: list all RFCs available\n"
                + "4. GET: download an RFC\n" + "5. EXIT: terminate connection\n" + "Select option - 1, 2, 3, 4 or 5\n")

            option = int(option)
            _request = []
            if option == 1:
                rfc_no, rfc_title = input("Enter RFC number: "), input("Enter RFC title: ")
                _request = ['ADD RFC ' + rfc_no + ' P2P-CI/1.0', 'Host: ' + client.client_host_name,
                            'Port: ' + str(client.upload_server_port), 'Title: ' + rfc_title]
            elif option == 2:
                rfc_no, rfc_title = input("Enter RFC number: "), input("Enter RFC title: ")
                _request = ['LOOKUP RFC ' + rfc_no + ' P2P-CI/1.0', 'Host: ' + client.client_host_name,
                            'Port: ' + str(client.upload_server_port), 'Title: ' + rfc_title]
            elif option == 3:
                _request = ['LIST ALL P2P-CI/1.0', 'Host: ' + client.client_host_name,
                            'Port: ' + str(client.upload_server_port)]
            elif option == 4:
                rfc_no = input("Enter RFC number: ")
                _request = ['LOOKUP RFC ' + rfc_no + ' P2P-CI/1.0', 'Host: ' + client.client_host_name,
                            'OS: ' + platform()]
                _thread.start_new_thread(client.p2p_get, ("\n".join(_request), ))
            elif option == 5:
                _request = ['EXIT RFC 123 P2P-CI/1.0', 'Host: ' + client.client_host_name, 'Port: ' + str(client.upload_server_port)]

            if option != 4 and len(_request) > 0:
                response = client.send_request("\n".join(_request))
            if option == 5:
                print('\033[91m' + response + '\033[0m')
                client.client_socket.close()
                break

        print('\033[91m'+response+'\033[0m')
