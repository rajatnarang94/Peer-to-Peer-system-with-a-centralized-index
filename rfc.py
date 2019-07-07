class RFCNode:
    def __init__(self, rfc_number, rfc_title, peer_hostname):
        self.rfc_number = rfc_number
        self.rfc_title = rfc_title
        self.peer_hostname = peer_hostname
        self.next = None

class RFCList:
    def __init__(self):
        self.head = None

    def already_present(self, rfc_number, rfc_title, peer_hostname):
        p = self.head
        while p!=None:
            if p.rfc_number == rfc_number and p.rfc_title == rfc_title and p.peer_hostname == peer_hostname:
                return True
            p = p.next
        return False

    def add_rfc(self, rfc_number, rfc_title, peer_hostname):
        if self.already_present(rfc_number, rfc_title, peer_hostname):
            print("Duplicate RFC Entry")
            return False
        new_peer = RFCNode(rfc_number,  rfc_title, peer_hostname)
        new_peer.next = self.head
        self.head = new_peer
        return True

    def list_all(self):
        cur = self.head
        res = []
        while cur != None:
            res.append({"rfc_number": str(cur.rfc_number), "rfc_title":cur.rfc_title, "peer_hostname": cur.peer_hostname})
            cur = cur.next
        return res

    def delete_rfc(self, peer_hostname):
        if self.head == None:
            print("RFC list is empty.")
            return

        temp = self.head
        if temp.peer_hostname == peer_hostname:
            self.head = temp.next
            return True

        prev = None
        while temp != None and temp.peer_hostname != peer_hostname:
            prev = temp
            temp = temp.next

        if temp == None:
            return False

        prev.next = temp.next
        return True

    def lookup(self, rfc_number):
        if self.head == None:
            print("RFC list is empty.")
            return []

        res = []
        p = self.head
        while p != None:
            if p.rfc_number == rfc_number:
                res.append({'rfc_number': p.rfc_number, 'rfc_title': p.rfc_title, 'peer_hostname': p.peer_hostname})
            p = p.next
        return res
    
'''sol = RFCList()
sol.add_rfc(1, '12', 'ab')
sol.add_rfc(2, '23', 'bc')
sol.add_rfc(3, '34', 'cd')
sol.list_all()
cur = sol.lookup(3, '34')
print()
print(cur)
print(sol.delete_rfc('cd'))
print()
sol.list_all()
print(sol.delete_rfc('bc'))
print()
sol.list_all()
print(sol.delete_rfc('ab'))
print()
sol.list_all()'''