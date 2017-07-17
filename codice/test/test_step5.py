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
        self.csocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.csocket.connect(((SERVER_HOST,SERVER_PORT)))

    def tearDown(self):
        self.payload = {"cmd":"exit","data":{"usr":"user3"}}
        self.csocket.send(message().encode(self.payload))
        self.csocket.close()

    def test_P1(self):
        self.payload = {"cmd":"login","data":{"usr":"user3","psw":"pass"}}
        self.csocket.send(message().encode(self.payload))
        data = self.csocket.recv(1024)
        data = message().decode(data)
        self.assertEqual("ok", data['response'])

        self.payload = {"cmd":"table","data":{"usr":"user3"}}
        self.csocket.send(message().encode(self.payload))
        data = self.csocket.recv(1024)
        data = message().decode(data)

        self.assertEqual("user2", data['data'][0][0])
        self.assertEqual(10, data['data'][0][1])
        self.assertEqual(4, data['data'][0][2])

        self.assertEqual("user1", data['data'][1][0])
        self.assertEqual(10, data['data'][1][1])
        self.assertEqual(3, data['data'][1][2])

if __name__=="__main__":
    part = sys.argv[1:]
    if len(part)==0:
        unittest.main()
    else:
        suite = unittest.TestSuite()
        for t in part:
            testName = 'test_{}'.format(t)
            print "Adding test: {}\n".format(testName)
            suite.addTest(TestStep1(testName))
        unittest.TextTestRunner(verbosity=2).run(suite)
