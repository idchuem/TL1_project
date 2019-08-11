# -*- coding: cp949 -*-
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
    crs1, crs2 = [], []
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

        location.append(alm[0])
        severity.append(alm[1].split(':')[1])
        cause.append(alm[2])
        description.append(alm[7].split(':')[1][1: -1])
        datetimes.append(dt)

    almParsed={'location': location, 'severity': severity, 'cause': cause, 'description': description, 'datetimes': datetimes}
    return almParsed

if __name__ == "__main__":
    NE_IP=getNeip()

    for IP in NE_IP:
        alms = getAlms('',IP) #alms={'location': location, 'severity': severity, 'cause': cause, 'description': description, 'datetimes': datetimes}
        crsConn=getCrs('', IP) #crs={'from':crs1,'to':crs2}

        for crs1,crs2 in zip(crsConn['from'],crsConn['to']):
            if (crs1 in alms['location']) and (crs2 in alms['location']): #IF CROSS-CONNECT 'FROM,TO' ARE BOTH ALARMED
                k=alms['location'].index(crs1)
                j=alms['location'].index(crs2)
                dt=datetime.datetime.now()
                dt1=alms['datetimes'][k]
                dt2=alms['datetimes'][j]
                td1=dt-dt1
                td2=dt-dt2
                date1=dt1.strftime('%Y-%m-%d')
                date2=dt2.strftime('%Y-%m-%d')
                if td1.days > 30 or td2.days > 30: #IF ALARMED ELASPED MORE THAN 30 DAYS
                    if alms['cause'][k]=='UNEQ' :
                        alarm = alms['location'][k]+', '+alms['cause'][k]+", "+date1+ ' & '+alms['location'][j]+', '+alms['cause'][j]+", "+date2
                        delCommand = "DLT-CRS-VT2::"+crs1+","+crs2+":CTAG:::,;"
                        print('Alarmed: '+alarm)
                        print('Command: '+delCommand)

                        crsCommand = "ENT-CRS-VT2::"+crs1+","+crs2+":CTAG::2WAY:,,CKTID='Restore',,;"
                        #telnet.write(command)
                        #cmdResult=telnet.read_until('<')
                        #print('Restore: '+crsCommand)
                        #print('CmdResult: '+cmdResult)

                    elif alms['cause'][j]=='UNEQ':
                        alarm = alms['location'][j]+', '+alms['cause'][j]+", "+date2+ ' & '+alms['location'][k]+', '+alms['cause'][k]+", "+date1
                        delCommand="DLT-CRS-VT2::"+crs1+","+crs2+":CTAG:::,;"
                        print('Alarmed: '+alarm)
                        print('Command: '+delCommand)

                        crsCommand = "ENT-CRS-VT2::"+crs1+","+crs2+":CTAG::2WAY:,,CKTID='Restore',,;"
                        #telnet.write(command)
                        #cmdResult=telnet.read_until('<')
                        print('Restore: '+crsCommand)
                        print('CmdResult: '+cmdResult)
