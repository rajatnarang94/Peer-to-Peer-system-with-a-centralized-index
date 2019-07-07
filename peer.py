class PeerNode:
    def __init__(self, host_name, port_no):
        self.host_name = host_name
        self.port_no = port_no
        self.next = None


class PeerList:
    def __init__(self):
        self.head = None

    def already_present(self, host_name, port_no):
        p = self.head
        while p != None:
            if p.host_name == host_name and p.port_no == port_no:
                return True
            p = p.next
        return False

    def add_peer(self, host_name, port_no):
        if self.already_present(host_name, port_no):
            print("Duplicate Peer Entry")
            return False
        new_peer = PeerNode(host_name,  port_no)
        new_peer.next = self.head
        self.head = new_peer
        return True

    def print_list(self):
        cur = self.head
        res = []
        while cur != None:
            res.append({'host_name': cur.host_name, 'port_no': str(cur.port_no)})
            cur = cur.next
        print(res)

    def delete_peer(self, host_name, port_no):
        if self.head == None:
            print("Peer list is empty.")
            return

        temp = self.head
        if temp.host_name == host_name and temp.port_no == port_no:
            self.head = temp.next
            return

        prev = None
        while temp != None and (temp.host_name != host_name or temp.port_no != port_no):
            prev = temp
            temp = temp.next

        if temp == None:
            return

        prev.next = temp.next

    def get_peer(self, host_name, port_no):
        temp = self.head
        while temp != None:
            if temp.host_name == host_name and temp.port_no == port_no:
                return temp
            temp = temp.next
        print("Peer not found")
        return None

    def get_port_no(self, host_name):
        temp = self.head
        while temp != None:
            if temp.host_name == host_name:
                return temp.port_no
            temp = temp.next
        print("Peer not found with hostname", host_name)
        return None

'''sol = PeerList()
sol.add_peer("12", 2)
sol.add_peer("23", 3)
sol.add_peer("34", 4)
sol.print_list()
cur = sol.get_peer("23", 3)
print()
print("[host_name= "+ cur.host_name + ", port_no = "+str(cur.port_no)+ "]", end = " ")
sol.delete_peer("12", 2)
print()
sol.print_list()
sol.delete_peer("34", 4)
print()
sol.print_list()
sol.delete_peer("23", 3)
print()
sol.print_list()'''