import pandas as pd
import telnetlib
import sys

class Telnet(telnetlib.Telnet,object):
    if sys.version > '3':
        def read_until(self,expected,timeout=None):
            expected = bytes(expected,encoding='utf-8')
            received = super(Telnet,self).read_until(expected,timeout)
            return str(received, encoding='utf-8', errors='ignore')
        def write(self, buffer):
            buffer = bytes(buffer, encoding ='utf-8')
            super(Telnet,self).write(buffer)
        def expect(self,list,timeout=None):
            for index,item in enumerate(list):
                list[index] = bytes(item, encoding='utf-8', errors='ignore')
            match_index,match_object, match_text = super(Telnet, self).expect(list,timeout)
            return match_index, match_object, str(match_text,encoding='utf-8')


def NE_IP(Model) : #장비 IP리스트 수집 함수
    IP=[]

    f=open('c:/intel/'+Model+'.txt', encoding='utf-8')
    for line in f.read().split():
        IpTemp=line
        IP.append(IpTemp)
    f.close()
    return IP

def LogParsing(NE_IP) : #장비 접속 수 TL1수행 함수

    temp1=""
    temp2=[]
    temp3=[]
    temp4=[]
    temp5=[]
    Logs=""
    print(NE_IP+' - Started')
    telnet=Telnet(NE_IP)
    telnet.read_until('login:', timeout=5)
    telnet.write('su\n')
    telnet.read_until('Password:', timeout=5)
    telnet.write('wwp\n')
    temp1=telnet.read_until('>', timeout=5)
    node=temp1.split('shell.')[1]
    node=node.lstrip()[:-1]
    print(node)
    telnet.write('chassis show temperature\n')
    Logs=telnet.read_until('>', timeout=5)
    telnet.write('exit\n')
    f = open('log', 'w')
    f.write(Logs)
    f.close()
    f = open('log', 'r')

    for line in f.readlines():
        try:
            if line[0] == "|":
                temp1 = line.rsplit()
                if temp1[8] == 'C':
                    Node = node
                    IP=NE_IP
                    Location = 'system'
                    CardType = 'system'
                    Temperature = temp1[1]
                    TempLow = temp1[4]
                    TempHigh = temp1[7]
                    temp2.append(Node)
                    temp3.append(CardType)
                    temp4.append(Location)
                    temp5.append(Temperature)
                    temp10.append(IP)
                    if Temperature >= '0':
                        temp6.append(Node)
                        temp7.append(CardType)
                        temp8.append(Location)
                        temp9.append(Temperature)
                        temp11.append(IP)
        except:
            pass
    f.close()

    result = {}
    result["00_IP"] = temp2
    result["00_Node"] = temp3
    result["01_CardType"] = temp4
    result["02_Location"] = temp5
    result["03_Temperature"] = temp6
    return temp2,temp3,temp4,temp5,temp6,temp7,temp8,temp9,temp10,temp11

if __name__ == '__main__':

    IP=NE_IP("5160-2")
    temp6 =[]
    temp7 =[]
    temp8 =[]
    temp9 =[]
    temp10 =[]
    temp11=[]
    for i in range(len(IP)) :

        Node,CardType,Location,Temperature,temp6,temp7,temp8,temp9,temp10,temp11 =LogParsing(IP[i])
        result={}
        result["00_IP"] = temp10
        result["00_Node"] = Node
        result["01_CardType"] = CardType
        result["02_Location"] = Location
        result["03_Temperature"] = Temperature


        #df = pd.DataFrame(result)
        #df.to_csv("c:/intel/"+IP[i]+"_temperature.csv", index="false", encoding='ms949')

    result = {}
    result["00_IP"] = temp11
    result["00_Node"] = temp6
    result["01_CardType"] = temp7
    result["02_Location"] = temp8
    result["03_Temperature"] = temp9

    df = pd.DataFrame(result)
    df.to_csv("c:/intel/5160_ALL_temperature.csv", index="false", encoding='ms949')
    print(' Completed')


