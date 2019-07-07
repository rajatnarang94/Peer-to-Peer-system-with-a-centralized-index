import socket
from peer import PeerList
from rfc import RFCList
import _thread
import traceback

def add_rfc(_request, client_hostname, client_port_no):
    rfc_no = _request[0].strip().split()[2].strip()
    rfc_title = _request[3].strip().split(':')[1].strip()
    rfc_list.add_rfc(rfc_no, rfc_title, client_hostname)
    response = ['P2P-CI/1.0 200 OK',  rfc_no + ' ' + rfc_title + ' ' + client_hostname + ' ' + client_port_no]
    return "\n".join(response)

def lookup_rfc(_request):
    rfc_no = _request[0].strip().split()[2].strip()
    peers_with_rfc = rfc_list.lookup(rfc_no)

    if len(peers_with_rfc) == 0:
        return "P2P-CI/1.0 404 Not Found"
    response = ['P2P-CI/1.0 200 OK']
    for peer in peers_with_rfc:
        peer_port_no = peer_list.get_port_no(peer['peer_hostname'])
        response.append(rfc_no + ' ' + peer['rfc_title'] + ' ' + peer['peer_hostname'] + ' ' + str(peer_port_no))
    return "\n".join(response)

def list_all_rfc():
    all_rfcs = rfc_list.list_all()

    if len(all_rfcs) == 0:
        return "P2P-CI/1.0 404 Not Found"

    response = ['P2P-CI/1.0 200 OK']
    for rfc in all_rfcs:
        peer_port_no = peer_list.get_port_no(rfc['peer_hostname'])
        if peer_port_no:
            response.append(rfc['rfc_number'] + ' ' + rfc['rfc_title'] + ' ' + rfc['peer_hostname'] + ' ' + str(peer_port_no))
    return "\n".join(response)

def spawned_thread(c):
    c.send("P2P-CI/1.0 200 OK".encode())
    while True:
        _request = c.recv(4096).decode()
        try:
            _request = _request.split('\n')
            method = _request[0].strip().split()[0].strip()

            if method == 'LIST':
                version = _request[0].strip().split()[2].strip()
            else:
                version = _request[0].strip().split()[3].strip()
        except:
            c.send("P2P-CI/1.0 400 Bad Request".encode())
            traceback.print_exc()
            continue

        if version != 'P2P-CI/1.0':
            c.send("505 P2P-CI Version Not Supported".encode())
            continue

        try:
            host_name = _request[1].strip().split(':')[1].strip()
            port_no = _request[2].strip().split(':')[1].strip()
        except:
            c.send("P2P-CI/1.0 400 Bad Request".encode())
            continue

        if method == 'ADD':
            try:
                response = add_rfc(_request, host_name, port_no)
                c.send(response.encode())
            except:
                c.send("P2P-CI/1.0 400 Bad Request".encode())
        elif method == 'LOOKUP':
            try:
                response = lookup_rfc(_request)
                c.send(response.encode())
            except:
                c.send("P2P-CI/1.0 400 Bad Request".encode())
        elif method == 'LIST':
            try:
                response = list_all_rfc()
                c.send(response.encode())
            except:
                c.send("P2P-CI/1.0 400 Bad Request".encode())
        elif method == 'EXIT':
            peer_list.delete_peer(host_name, port_no)
            while rfc_list.delete_rfc(host_name):
                continue
            c.send("P2P-CI/1.0 200 OK".encode())
            c.close()
            print('**********Client thread terminated**********')
            break


if __name__ == '__main__':
    s = socket.socket()
    port = 7734
    s.bind(('', port))
    s.listen(5)
    print("Server started, listening for connections!")
    peer_list = PeerList()
    rfc_list = RFCList()
    while True:
        c, addr = s.accept()
        print('Got connection from', addr)
        _request = c.recv(4096).decode().split('\n')

        client_host_name, client_port_no = _request[0].split(':')[1].strip(), _request[1].split(':')[1].strip()

        peer_list.add_peer(client_host_name, client_port_no)
        _thread.start_new_thread(spawned_thread, (c, ))
