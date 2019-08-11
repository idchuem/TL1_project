import pandas as pd
import telnetlib
import sys

class Telnet(telnetlib.Telnet,object):
    if sys.version > '3':
        def read_until(self,expected,timeout=3):
            expected = bytes(expected,encoding='utf-8')
            received = super(Telnet,self).read_until(expected,timeout)
            return str(received, encoding='utf-8', errors='ignore')
        def write(self, buffer):
            buffer = bytes(buffer, encoding ='utf-8')
            super(Telnet,self).write(buffer)
        def expect(self,list,timeout=3):
            for index,item in enumerate(list):
                list[index] = bytes(item, encoding='utf-8', errors='ignore')
            match_index,match_object, match_text = super(Telnet, self).expect(list,timeout)
            return match_index, match_object, str(match_text,encoding='utf-8')


def get_neip(file) : #장비 IP리스트 수집 함수
    f=open(file,'rt')
    ip=f.read().splitlines()
    return ip

class Ciena:
    class Ptn:
        def __init__(self, ip, id, pw):
            self.ne_ip=ip
            self.tl1=self.ne_login()
            self.ne_id=self.get_sys()
            print('Logged in - {}'.format(self.ne_ip))

        def ne_login(self):
            telnet=Telnet(self.ne_ip)
            telnet.read_until('login:')
            telnet.write('su\n')
            telnet.read_until('Password:')
            telnet.write('wwp\n')
            telnet.read_until('>')

        def get_sys(self):
            self.tl1=telnet.write('system show\n')
            tid=self.tl1.read_until('>')

        def parse(self,log):
            table=[]
            log1=log.split('+')[-1]
            lines = log1.split('\r\n')
            for line in lines:
                columns = []
                cols = line.strip('|').split('|')
                for col in cols:
                    columns.append(col.strip())
                table.append(columns)
            return table

        def get_temp(self):
            self.tl1.write('chassis show temperature\n')
            log=telnet.read_until('>')

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
        result={"00_IP": temp2, "00_Node": temp3, "01_CardType": temp4, "02_Location": temp5, "03_Temperature": temp6
        return result

if __name__ == '__main__':

    ne_ip=get_neip('5160')
    ne=['']*len(ne_ip)
    for ip,ne in zip(ne_ip,ne):

        ne=Ciena.Ptn(ip)

        temp1=""
        temp2=[]
        temp3=[]
        temp4=[]
        temp5=[]
        Logs=""

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


