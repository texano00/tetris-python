import unittest
from config import *
import socket
import sys
import time

class message(object):
    def encode(self,data):
        return base64.b64encode(json.dumps(data))+"\n\r"

    def decode(self,data):
        return json.loads(base64.b64decode(data))

def addMove(user,move,data):
    data.pop("response",None)
    data["data"].pop('player',None)
    data["data"].pop('first',None)

    data["cmd"] = 'game'
    data['data']['status'] = 'status'
    data['data']['last_play'] = {}
    data['data']['last_play']['move'] = move
    data['data']['last_play']['usr'] = user

    data['data']['play'][user]['done'].append(move)

    return data

class TestStep4(unittest.TestCase): 

    def setUp(self):
        self.csocket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.csocket1.connect(((SERVER_HOST,SERVER_PORT)))

        self.csocket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.csocket2.connect(((SERVER_HOST,SERVER_PORT)))

    def tearDown(self):
        self.payload = {"cmd":"exit","data":{"usr":"user1"}}
        self.csocket1.send(message().encode(self.payload))
        self.csocket1.close()

        self.payload = {"cmd":"exit","data":{"usr":"user2"}}
        self.csocket2.send(message().encode(self.payload))
        self.csocket2.close()

    def test_P1(self):
        self.payload = {"cmd":"login","data":{"usr":"user1","psw":"pass"}}
        self.csocket1.send(message().encode(self.payload))
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual("ok", data['response'])

        self.payload = {"cmd":"login","data":{"usr":"user2","psw":"pass"}}
        self.csocket2.send(message().encode(self.payload))
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual("ok", data['response'])

        self.payload = {"cmd":"play","data":{"usr":"user1"}}
        self.csocket1.send(message().encode(self.payload))
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual("waiting", data['response'])

        self.payload = {"cmd":"play","data":{"usr":"user2"}}
        self.csocket2.send(message().encode(self.payload))
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual("waiting", data['response'])

        ##START USER2
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual("start", data['data']['status'])
        self.assertEqual(1, data['data']['first'])

        data = addMove('user2',1,data) #USER2 PLAY 1
        self.csocket2.send(message().encode(data))
        ##END USER2

        ##START USER1
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual("start", data['data']['status'])
        self.assertEqual(0, data['data']['first'])

        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual(1, data['data']['last_play']['move'])
        self.assertEqual("user2", data['data']['last_play']['usr'])
        self.assertEqual([1], data['data']['play']['user2']['done'])

        data = addMove('user1',5,data) #USER1 PLAY 5
        self.csocket1.send(message().encode(data))
        ##END USER1

        ##START USER2
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual(5, data['data']['last_play']['move'])
        self.assertEqual("user1", data['data']['last_play']['usr'])
        self.assertEqual([5], data['data']['play']['user1']['done'])

        data = addMove('user2',7,data) #USER2 PLAY 3
        self.csocket2.send(message().encode(data))
        ##END USER2

        ##START USER1
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual(7, data['data']['last_play']['move'])
        self.assertEqual("user2", data['data']['last_play']['usr'])
        self.assertEqual([1,7], data['data']['play']['user2']['done'])

        data = addMove('user1',4,data) #USER1 PLAY 4
        self.csocket1.send(message().encode(data))
        ##END USER1

        ##START USER2
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual(4, data['data']['last_play']['move'])
        self.assertEqual("user1", data['data']['last_play']['usr'])
        self.assertEqual([5,4], data['data']['play']['user1']['done'])

        data = addMove('user2',6,data) #USER2 PLAY 6
        self.csocket2.send(message().encode(data))
        ##END USER2

        ##START USER1
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual(6, data['data']['last_play']['move'])
        self.assertEqual("user2", data['data']['last_play']['usr'])
        self.assertEqual([1,7,6], data['data']['play']['user2']['done'])

        data = addMove('user1',2,data) #USER1 PLAY 2
        self.csocket1.send(message().encode(data))
        ##END USER1

        ##START USER2
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual(2, data['data']['last_play']['move'])
        self.assertEqual("user1", data['data']['last_play']['usr'])
        self.assertEqual([5,4,2], data['data']['play']['user1']['done'])

        data = addMove('user2',8,data) #USER2 PLAY 8
        self.csocket2.send(message().encode(data))
        ##END USER2

        ##START USER1
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual(8, data['data']['last_play']['move'])
        self.assertEqual("user2", data['data']['last_play']['usr'])
        self.assertEqual([1,7,6,8], data['data']['play']['user2']['done'])

        data = addMove('user1',9,data) #USER1 PLAY 9
        self.csocket1.send(message().encode(data))
        ##END USER1

        ##START USER2
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual(9, data['data']['last_play']['move'])
        self.assertEqual("user1", data['data']['last_play']['usr'])
        self.assertEqual([5,4,2,9], data['data']['play']['user1']['done'])

        data = addMove('user2',3,data) #USER2 PLAY 3
        self.csocket2.send(message().encode(data))
        ##END USER2

        ##USER1 KNOW THAT THERE'S NO WINNNER
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual("none", data['data']['winner'])

        ##USER2 KNOW THAT THERE'S NO WINNNER
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual("none", data['data']['winner'])

    def test_P2(self):
        self.payload = {"cmd":"login","data":{"usr":"user1","psw":"pass"}}
        self.csocket1.send(message().encode(self.payload))
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual("ok", data['response'])

        self.payload = {"cmd":"login","data":{"usr":"user2","psw":"pass"}}
        self.csocket2.send(message().encode(self.payload))
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual("ok", data['response'])

        self.payload = {"cmd":"play","data":{"usr":"user1"}}
        self.csocket1.send(message().encode(self.payload))
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual("waiting", data['response'])

        self.payload = {"cmd":"play","data":{"usr":"user2"}}
        self.csocket2.send(message().encode(self.payload))
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual("waiting", data['response'])

        ##START USER2
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual("start", data['data']['status'])
        self.assertEqual(1, data['data']['first'])

        data = addMove('user2',1,data) #USER2 PLAY 1
        self.csocket2.send(message().encode(data))
        ##END USER2

        ##START USER1
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual("start", data['data']['status'])
        self.assertEqual(0, data['data']['first'])

        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual(1, data['data']['last_play']['move'])
        self.assertEqual("user2", data['data']['last_play']['usr'])
        self.assertEqual([1], data['data']['play']['user2']['done'])

        data = addMove('user1',5,data) #USER1 PLAY 5
        self.csocket1.send(message().encode(data))
        ##END USER1

        ##START USER2
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual(5, data['data']['last_play']['move'])
        self.assertEqual("user1", data['data']['last_play']['usr'])
        self.assertEqual([5], data['data']['play']['user1']['done'])

        data = addMove('user2',2,data) #USER2 PLAY 2
        self.csocket2.send(message().encode(data))
        ##END USER2

        ##START USER1
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual(2, data['data']['last_play']['move'])
        self.assertEqual("user2", data['data']['last_play']['usr'])
        self.assertEqual([1,2], data['data']['play']['user2']['done'])

        data = addMove('user1',3,data) #USER1 PLAY 3
        self.csocket1.send(message().encode(data))
        ##END USER1

        ##START USER2
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual(3, data['data']['last_play']['move'])
        self.assertEqual("user1", data['data']['last_play']['usr'])
        self.assertEqual([5,3], data['data']['play']['user1']['done'])

        data = addMove('user2',7,data) #USER2 PLAY 7
        self.csocket2.send(message().encode(data))
        ##END USER2

        ##START USER1
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual(7, data['data']['last_play']['move'])
        self.assertEqual("user2", data['data']['last_play']['usr'])
        self.assertEqual([1,2,7], data['data']['play']['user2']['done'])

        data = addMove('user1',4,data) #USER1 PLAY 4
        self.csocket1.send(message().encode(data))
        ##END USER1

        ##START USER2
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual(4, data['data']['last_play']['move'])
        self.assertEqual("user1", data['data']['last_play']['usr'])
        self.assertEqual([5,3,4], data['data']['play']['user1']['done'])

        data = addMove('user2',6,data) #USER2 PLAY 6
        self.csocket2.send(message().encode(data))
        ##END USER2

        ##START USER1
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual(6, data['data']['last_play']['move'])
        self.assertEqual("user2", data['data']['last_play']['usr'])
        self.assertEqual([1,2,7,6], data['data']['play']['user2']['done'])

        data = addMove('user1',9,data) #USER1 PLAY 9
        self.csocket1.send(message().encode(data))
        ##END USER1

        ##START USER2
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual(9, data['data']['last_play']['move'])
        self.assertEqual("user1", data['data']['last_play']['usr'])
        self.assertEqual([5,3,4,9], data['data']['play']['user1']['done'])

        data = addMove('user2',8,data) #USER2 PLAY 8
        self.csocket2.send(message().encode(data))
        ##END USER2

        ##USER1 KNOW THAT THERE'S NO WINNNER
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual("none", data['data']['winner'])

        ##USER2 KNOW THAT THERE'S NO WINNNER
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual("none", data['data']['winner'])

    def test_P3(self):
        self.payload = {"cmd":"login","data":{"usr":"user1","psw":"pass"}}
        self.csocket1.send(message().encode(self.payload))
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual("ok", data['response'])

        self.payload = {"cmd":"login","data":{"usr":"user2","psw":"pass"}}
        self.csocket2.send(message().encode(self.payload))
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual("ok", data['response'])

        self.payload = {"cmd":"play","data":{"usr":"user1"}}
        self.csocket1.send(message().encode(self.payload))
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual("waiting", data['response'])

        self.payload = {"cmd":"play","data":{"usr":"user2"}}
        self.csocket2.send(message().encode(self.payload))
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual("waiting", data['response'])

        ##START USER2
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual("start", data['data']['status'])
        self.assertEqual(1, data['data']['first'])

        data = addMove('user2',3,data) #USER2 PLAY 3
        self.csocket2.send(message().encode(data))
        ##END USER2

        ##START USER1
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual("start", data['data']['status'])
        self.assertEqual(0, data['data']['first'])

        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual(3, data['data']['last_play']['move'])
        self.assertEqual("user2", data['data']['last_play']['usr'])
        self.assertEqual([3], data['data']['play']['user2']['done'])

        data = addMove('user1',5,data) #USER1 PLAY 5
        self.csocket1.send(message().encode(data))
        ##END USER1

        ##START USER2
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual(5, data['data']['last_play']['move'])
        self.assertEqual("user1", data['data']['last_play']['usr'])
        self.assertEqual([5], data['data']['play']['user1']['done'])

        data = addMove('user2',9,data) #USER2 PLAY 3
        self.csocket2.send(message().encode(data))
        ##END USER2

        ##START USER1
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual(9, data['data']['last_play']['move'])
        self.assertEqual("user2", data['data']['last_play']['usr'])
        self.assertEqual([3,9], data['data']['play']['user2']['done'])

        data = addMove('user1',6,data) #USER1 PLAY 6
        self.csocket1.send(message().encode(data))
        ##END USER1

        ##START USER2
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual(6, data['data']['last_play']['move'])
        self.assertEqual("user1", data['data']['last_play']['usr'])
        self.assertEqual([5,6], data['data']['play']['user1']['done'])

        data = addMove('user2',4,data) #USER2 PLAY 4
        self.csocket2.send(message().encode(data))
        ##END USER2

        ##START USER1
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual(4, data['data']['last_play']['move'])
        self.assertEqual("user2", data['data']['last_play']['usr'])
        self.assertEqual([3,9,4], data['data']['play']['user2']['done'])

        data = addMove('user1',7,data) #USER1 PLAY 7
        self.csocket1.send(message().encode(data))
        ##END USER1

        ##START USER2
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual(7, data['data']['last_play']['move'])
        self.assertEqual("user1", data['data']['last_play']['usr'])
        self.assertEqual([5,6,7], data['data']['play']['user1']['done'])

        data = addMove('user2',1,data) #USER2 PLAY 1
        self.csocket2.send(message().encode(data))
        ##END USER2

        ##START USER1
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual(1, data['data']['last_play']['move'])
        self.assertEqual("user2", data['data']['last_play']['usr'])
        self.assertEqual([3,9,4,1], data['data']['play']['user2']['done'])

        data = addMove('user1',2,data) #USER1 PLAY 2
        self.csocket1.send(message().encode(data))
        ##END USER1

        ##START USER2
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual(2, data['data']['last_play']['move'])
        self.assertEqual("user1", data['data']['last_play']['usr'])
        self.assertEqual([5,6,7,2], data['data']['play']['user1']['done'])

        data = addMove('user2',8,data) #USER2 PLAY 8
        self.csocket2.send(message().encode(data))
        ##END USER2

        ##USER1 KNOW THAT THERE'S NO WINNNER
        data = self.csocket1.recv(1024)
        data = message().decode(data)
        self.assertEqual("none", data['data']['winner'])

        ##USER2 KNOW THAT THERE'S NO WINNNER
        data = self.csocket2.recv(1024)
        data = message().decode(data)
        self.assertEqual("none", data['data']['winner'])

if __name__=="__main__":
    part = sys.argv[1:]
    if len(part)==0:
        unittest.main()
    else:
        suite = unittest.TestSuite()
        for t in part:
            testName = 'test_{}'.format(t)
            print "Adding test: {}\n".format(testName)
            suite.addTest(TestStep4(testName))
        unittest.TextTestRunner(verbosity=2).run(suite)
