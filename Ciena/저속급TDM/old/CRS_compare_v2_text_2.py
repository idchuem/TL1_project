# -*- coding: utf-8 -*-
#!/opt/liko/bin/python

import sys
import telnetlib
import time
import pandas as pd
import datetime

def getNeip ():
    IP=[]
    f=open('NE_IP', encoding='utf-8')
    for line in f.read().split():
        IP.append(line)
    f.close()
    return(IP)

def getCrs(hostnames,NE_IP) : #[모듈] 텔넷 후 Log Parsing
    crs_from, crs_to = [], []
    f=open('crs')
    Logs=f.read()
    f.close()
    lines = Logs.split('   "')
    for line in lines:
        if line[0]=='V':
            crsTmp=line.split(',')
            crs_from.append(crsTmp[0])
            crs_to.append(crsTmp[1].split(':')[0])
    crs={'from':crs_from,'to':crs_to}
    print(NE_IP + ' 에서 맵 정보를 추줄하였습니다...')
    return crs

def getAlms(hostnames,NE_IP) : #[모듈] 텔넷 후 Log Parsing
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
    print(NE_IP+' 에서 현재 알람을 추출하였습니다...')
    return almParsed

if __name__ == "__main__":
    NE_IP=getNeip()
    f=open('readme','rt', encoding='utf-8')
    readme=f.read()
    f.close()
    print(readme)
    start = input()
    if start != 'start':
        sys.exit()

    for IP in NE_IP:
        alms = getAlms('',IP) #alms={'location': location, 'severity': severity, 'cause': cause, 'description': description, 'datetimes': datetimes}
        crsConn=getCrs('', IP) #crs={'from':crs_from,'to':crs_to}
        cktDead = open('Dead Circuits' + IP, 'wt')
        cktDel = open('Deleted circuits '+IP, 'wt')
        cktRestore = open('Restoring circuits '+IP, 'wt')

        for crs_from,crs_to in zip(crsConn['from'],crsConn['to']):

            if (crs_from in alms['location']) and (crs_to in alms['location']): #IF CROSS-CONNECT 'FROM,TO' ARE BOTH ALARMED
                k=alms['location'].index(crs_from)
                j=alms['location'].index(crs_to)
                dt=datetime.datetime.now()
                dt1=alms['datetimes'][k]
                dt2=alms['datetimes'][j]
                td1=dt-dt1
                td2=dt-dt2
                date1=dt1.strftime('%Y-%m-%d')
                date2=dt2.strftime('%Y-%m-%d')

                if td1.days > 30 or td2.days > 30: #IF ALARMED ELASPED MORE THAN 30 DAYS
                    if alms['cause'][k]=='UNEQ' or alms['cause'][j]=='UNEQ':

                        cktDead.write('CrsFrom: '+crs_from+'\n')
                        cktDead.write('Almfrom: ' +alms['location'][k]+ ' ('+alms['cause'][k]+", "+date1+ ')'+'\n')
                        cktDead.write('CrsTo  : '+crs_to+'\n')
                        cktDead.write('AlmTo  : ' +alms['location'][j]+ ' ('+alms['cause'][j]+", "+date2+ ')'+'\n\n')
                        delCommand = "DLT-CRS-VT2::"+crs_from+","+crs_to+":CTAG:::,;"
                        crsCommand = "ENT-CRS-VT2::"+crs_from+","+crs_to+":CTAG::2WAY:,,CKTID='Restore',,;"
                        cktDel.write(delCommand+'\n')
                        cktRestore.write(crsCommand+'\n')

                        #telnet.write(command)
                        #cmdResult=telnet.read_until('<')
                        #print('Restore: '+crsCommand)
                        #print('CmdResult: '+cmdResult)

        print(IP+' 에서 미사용 회선을 추출하였습니다. "dead circuits '+IP+'.log" 파일을 확인하십시오')
        print('파일을 확인하셨으면 회선 삭제를 진행하시겠습니까?')
        commit = 0
        while(commit!='commit'):
            print('삭제를 시작하려면 commit을 입력 하십시오.')
            commit = input()

        cktDead.close()
        cktDel.close()
        cktRestore.close()
