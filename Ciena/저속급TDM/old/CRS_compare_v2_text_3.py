# -*- coding: utf-8 -*-
#!/opt/liko/bin/python

import sys
import telnetlib
import time
import pandas as pd
import datetime

class Telnet(telnetlib.Telnet, object):
    if sys.version > '3':
        def read_until(self, expected, timeout=None):
            expected = bytes(expected, encoding='utf-8')
            received = super(Telnet, self).read_until(expected, timeout)
            return str(received, encoding='ms949', errors='ignore')

        def write(self, buffer):
            buffer = bytes(buffer, encoding='utf-8')
            super(Telnet, self).write(buffer)

        def expect(self, list, timeout=None):
            for index, item in enumerate(list):
                list[index] = bytes(item, encoding='utf-8', errors='ignore')
            match_index, match_object, match_text = super(Telnet, self).expect(list, timeout)
            return match_index, match_object, str(match_text, encoding='utf-8')

def getNeip ():
    IP=[]
    neid=[]
    f=open('NE_IP', encoding='utf-8')
    for line in f.read().split():
        IP.append(line)
    f.close()
    return(IP)

class ciena:

    def __init__(self,NE_IP):
        self.dt = datetime.datetime.now()
        self.dtStr=self.dt.strftime('%Y-%m-%d %Hh%Mm%Ss')
        self.NE_IP =NE_IP


    def getNeid(self,NE_IP):
        telnet = Telnet(NE_IP)
        telnet.write(;)
        hostname = telnet.read_until('<')

    def DateDelta(self,):
        dt = datetime.datetime.now()
        td1=dt-dt
        date=dt1.strftime('%Y-%m-%d')
        return date

    def GetCrs(self) : #[모듈] 텔넷 후 Log Parsing
        crs1,crs2 = [],[]
        f=open('crs')
        Logs=f.read()
        f.close()
        lines = Logs.split('   "')
        for line in lines:
            if line[0]=='V':
                crsTmp=line.split(',')
                crs1.append(crsTmp[0])
                crs2.append(crsTmp[1].split(':')[0])
        crs={'from':crs1,'to':crs2}
        print(self.NE_IP + ' 에서 맵 정보를 추줄하였습니다...')
        return crs

    def CrsDel(self,crsFrom,crsTo):
        for crs1,crs2 in zip(crsFrom,crsTo):
            delCommand = "DLT-CRS-VT2::" + crs1 + "," + crs2 + ":CTAG:::,;"
            #telnet.write(delCommand)
            #result=telnet.until('<')
            #result[-5:]
            f=open('Delete result '+self.NE_IP,'wt')
            f.write('Command :'+delCommand+'\n')
            f.write('result  :'+result + '\n\n')
            f.close()

    def crsRes(self,crsFrom,crsTo):
        for crs1,crs2 in zip(crsFrom,crsTo):
            crsCommand = "ENT-CRS-VT2::" + crs1 + "," + crs2 + ":CTAG::2WAY:,,CKTID='Restore',,;"
            #telnet.write(crsCommand)
            #result=telnet.until('<')
            #result[-5:]
            f = open('Restore result '+self.NE_IP, 'wt')
            f.write('Command :'+crsCommand+'\n')
            f.write('result  :'+result + '\n\n')
            f.close()

    def GetAlm(self) : #[모듈] 텔넷 후 Log Parsing
        location,severity,cause,description,datetimes=[],[],[],[],[]
        f=open('alm')
        Logs=f.read()
        f.close()
        lines= Logs.split('   "')[1:]
        for line in lines:
            alm = line.split(',')

            dateTmp = alm[4].split('-')
            timeTmp = alm[5].split('-')
            dt = datetime.datetime(int(alm[9].split('=')[1]), int(dateTmp[0]), int(dateTmp[1]), int(timeTmp[0]), int(timeTmp[1]), int(timeTmp[2])) #year, month, day, hour, min, sec

            datetimes.append(dt)
            location.append(alm[0])
            severity.append(alm[1].split(':')[1])
            cause.append(alm[2])
            description.append(alm[7].split(':')[1][1: -1])
        almParsed={'location': location, 'severity': severity, 'cause': cause, 'description': description, 'datetimes': datetimes}
        print(self.NE_IP+' 에서 현재 알람을 추출하였습니다...')
        return almParsed

    def CrsInAlm(self,crs,alm):
        deadFrom,deadTo=[],[]
        cktDead = open('Dead Circuits' + IP, 'wt')
        for crs_from,crs_to in zip(crs['from'],crs['to']):
            if (crs_from in alm['location']) and (crs_to in alm['location']): #IF CROSS-CONNECT 'FROM,TO' ARE BOTH ALARMED
                k=alm['location'].index(crs_from)
                j=alm['location'].index(crs_to)
                dt1=alm['datetimes'][k]
                dt2=alm['datetimes'][j]
                td1=self.dt-dt1
                td2=self.dt-dt2
                if td1.days > 30 or td2.days > 30: #IF ALARMED ELASPED MORE THAN 30 DAYS
                    if (alm['cause'][k]=='UNEQ') or (alm['cause'][j]=='UNEQ') :
                        date_from = dt1.strftime('%Y-%m-%d')
                        date_to = dt2.strftime('%Y-%m-%d')
                        cktDead.write('CrsFrom: '+crs_from+'\n')
                        cktDead.write('Almfrom: ' +alm['location'][k]+ ' ('+alm['cause'][k]+", "+date_from+ ')'+'\n')
                        cktDead.write('CrsTo  : '+crs_to+'\n')
                        cktDead.write('AlmTo  : ' +alm['location'][j]+ ' ('+alm['cause'][j]+", "+date_to+ ')'+'\n\n')
                        deadFrom.append(crs_from)
                        deadTo.append(crs_to)
        cktDead.close()
        deadCkt={'From':deadFrom,'To':deadTo}
        return deadCkt

if __name__ == "__main__":
    host = []
    NE_IP=getNeip()
    f=open('readme','rt', encoding='utf-8')
    readme=f.read()
    f.close()
    print(readme)
    start = input()
    if start != 'start':
        sys.exit()

    for IP in NE_IP:
        node=ciena(IP)
        host.append(node)
        alm=node.GetAlm()
        crs=node.GetCrs()
        deadCkt=node.CrsInAlm(crs,alm)
        print(IP+' 에서 미사용 회선을 추출하였습니다. "dead circuits '+IP+'.log" 파일을 확인하십시오')
        print('파일을 확인하셨으면 회선 삭제를 진행하시겠습니까?')
        commit = 0
        while(commit!='commit'):
            print('삭제를 시작하려면 commit을 입력 하십시오.')
            commit = input()

