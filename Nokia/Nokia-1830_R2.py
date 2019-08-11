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

    print(NE_IP+' - Started')
    telnet=Telnet(NE_IP)
    ver=telnet.read_until('login:', timeout=120)
    telnet.write('cli\n')
    log1=telnet.expect(["Password:","Username:"], timeout=120)
    if log1[2].lstrip() == 'Password:':
        telnet.write('cli\n')
        telnet.read_until('Username:', timeout=120)
    telnet.write('admin\n')  # TL1 경보조회 명령
    telnet.read_until('Password:', timeout=120)
    telnet.write('admin\n')
    telnet.read_until('(Y/N)?', timeout=120)
    print('logged in')
    telnet.write('Y\n')
    telnet.read_until('AL', timeout=120)
    node=telnet.read_until('#', timeout=120)
    node=node[:-1]
    print(node)
    telnet.write('show card inventory *\n')
    Logs=""
    for i in range(20):
        log1=telnet.expect(["#",">"], timeout=120)
        print(log1[2][-1])
        if log1[2][-1] == '#':
            Logs=Logs+log1[2]
            break
        telnet.write('y')
        Logs=Logs+log1[2]
    f = open('log', 'w')
    f.write(Logs)
    f.close()
    f = open('log', 'r')

    temp1 =[]
    temp2 =[]
    temp3 =[]


    for line in f.readlines():
        try:
            if line[1] == ' ':
                CardType = line[9:19].strip()
                Location=line[0:8].strip()
                telnet.write('show card'+' '+Location+'\n')
                temp=telnet.read_until('#', timeout=120)
                index=temp.find('Temperature         :')
                if index != -1:
                    Temperature=temp[index+23:index+25]
                    Temperature=int(Temperature)
                    print(Temperature)
                    temp1.append(CardType)
                    temp2.append('"'+Location)
                    temp3.append(Temperature)
                    if Temperature >= 0 :
                        temp7.append(node)
                        temp4.append(CardType)
                        temp5.append('"' + Location)
                        temp6.append(Temperature)
                    print (CardType + Location + Temperature)
        except :
            pass
    f.close()
    telnet.write('logout')
    return temp1,temp2,temp3,temp4,temp5,temp6,temp7, node

if __name__ == '__main__':

    IP=NE_IP("1830-2")
    temp4 =[]
    temp5 =[]
    temp6 =[]
    temp7 =[]
    for i in range(len(IP)) :

        CardType,Location,Temperature,temp4,temp5,temp6,temp7,node =LogParsing(IP[i])
        result={}
        result["00_Node"] = node
        result["01_CardType"] = CardType
        result["02_Location"] = Location
        result["03_Temperature"] = Temperature
        df = pd.DataFrame(result)
        df.to_csv("c:/intel/"+node+"_temperature.csv", index="false", encoding='ms949')

    result = {}
    result["00_Node"] = temp7
    result["01_CardType"] = temp4
    result["02_Location"] = temp5
    result["03_Temperature"] = temp6
    print(result)
    df = pd.DataFrame(result)
    df.to_csv("c:/intel/1830_ALL_temperature.csv", index="false", encoding='ms949')
    print(' Completed')


