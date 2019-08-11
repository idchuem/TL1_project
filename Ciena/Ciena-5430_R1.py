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
    telnet.read_until('Login:', timeout=2)
    telnet.write('superuser\n')
    telnet.read_until('Password:', timeout=2)
    telnet.write('superuser1!\n')
    temp1=telnet.read_until('help):', timeout=2)
    node=temp1.split(',')[1]
    node = node.split(')')[0]
    print(node)
    telnet.write('!shell\n')
    telnet.read_until('>', timeout=2)
    telnet.write("""dbgshell -c 'zi " /tempctrl/viewAmbientTemp"'\n""")
    Logs=telnet.read_until('CTMP>')
    telnet.write('logout\n')
    telnet.read_until('help):', timeout=2)
    telnet.write("10\n")

    f = open('log', 'w')
    f.write(Logs)
    f.close()
    f = open('log', 'r')

    for line in f.readlines():

        try:
            if line[-2] == 'C':
                line = line.split()
                Node = node
                #line[0] =  카드타입
                #line[1] = Slot번호
                #line[2] = 온도
                CardType = line[0]
                if line[1] == 'ambient':
                    Location = 'System'
                elif line[0] == 'CTM':
                    if line[1] == '0':
                        Location = 'A-CTM'
                    else :
                        Location = 'C-CTM'
                elif line[0] == 'LM':
                    line[1]=(1 + int(line[1]))
                    if line[1] >= 16:
                        Location = 'C-'+str(line[1]-15)
                    else :
                        Location = 'A-' + str(line[1])
                elif line[0] == 'SM':
                    Location = 'B-'+str(int(line[1])+1)

                Temperature = line[2]
                temp2.append(Node)
                temp3.append(CardType)
                temp4.append(Location)
                temp5.append(Temperature)
                if Temperature[:-1] >= '0' :
                    temp6.append(Node)
                    temp7.append(CardType)
                    temp8.append(Location)
                    temp9.append(Temperature)
        except:
            pass
    f.close()
    return temp2,temp3,temp4,temp5,temp6,temp7,temp8,temp9

if __name__ == '__main__':

    IP=NE_IP("5430")
    temp6 =[]
    temp7 =[]
    temp8 =[]
    temp9 =[]
    for i in range(len(IP)) :

        Node,CardType,Location,Temperature,temp6,temp7,temp8,temp9 =LogParsing(IP[i])
        result={}
        result["00_Node"] = Node
        result["01_CardType"] = CardType
        result["02_Location"] = Location
        result["03_Temperature"] = Temperature

        df = pd.DataFrame(result)
        df.to_csv("c:/intel/"+IP[i]+"_temperature.csv", index="false", encoding='ms949')

    result = {}
    result["00_Node"] = temp6
    result["01_CardType"] = temp7
    result["02_Location"] = temp8
    result["03_Temperature"] = temp9

    df = pd.DataFrame(result)
    df.to_csv("c:/intel/5430_ALL_temperature.csv", index="false", encoding='ms949')
    print(' Completed')


