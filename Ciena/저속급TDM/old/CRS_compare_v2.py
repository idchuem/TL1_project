# -*- coding: cp949 -*-
#!/opt/liko/bin/python

import sys
import telnetlib
import time
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

def now_time() :
    now= time.localtime()
    if int(now.tm_mon) <10 :
      mon=str('0')+str(now.tm_mon)
    else :
      mon=now.tm_mon
    if int(now.tm_mday) <10 :
      day=str('0')+str(now.tm_mday)
    else :
      day=now.tm_mday
    if int(now.tm_hour) <10 :
      hour=str('0')+str(now.tm_hour)
    else :
      hour=now.tm_hour
    if now.tm_min <10 :
      min=str('0')+str(now.tm_min)
    else :
      min=now.tm_min
#  now_date= str(now.tm_year)+str(mon)+str(day)+str(hour)+str(min)
    now_date= str(mon)+str(day)
    return(now_date)

def getNeip ():
    IP=[]
    f=open('NE_IP', encoding='utf-8')
    for line in f.read().split():
        IP.append(line)
    f.close()
    return(IP)

def getNeid ():
    telnet = Telnet(NE_IP)
    telnet.read_until('<')
    telnet.write('ACT-USER:' + hostnames + ':ADMIN:CTAG::ADMIN:;')
    telnet.read_until('<')
    telnet.write('RTRV-CRS-VT2:' + hostnames + ':ALL:CTAG:::,;')
    Logs = telnet.read_until('<')
    print(hostnames + '(' + NE_IP + ')' + ' getNeid Completed!')
    telnet.write('CANC-USER:' + hostnames + ':ADMIN:CTAG;')
    telnet.close()

def SONET_TO_STM(SONET) :
     #VT2-SHELF-SLOT-PORT-AUG-TUG-AU-TU
    SONET_Split=SONET.split('-') # SONET 경보(SHELF-SLOT-PORT-AUG-TUG)를 - 단위로 쪼개 리스트로 저장
    SDH_Temp = "" # SDH변환을 위한 임시 변수 선언
    n = 0
    if (len(SONET_Split)>4) :
        SONET_Split[1]='#'+SONET_Split[1]
        SONET_Split[2]='SL'+SONET_Split[2]
        SONET_Split[3]='P'+SONET_Split[3]
        SONET_Split[4]='AUG'+str((int(SONET_Split[4])+2)/3) #(SONET계위-> SDH변환)
        SONET_Split[0]=SONET_Split[0].replace('VT2AU4','VC12')
        SONET_Split[0]=SONET_Split[0].replace('STS3C', 'VC4')
        SONET_Split[0]=SONET_Split[0].replace('STS1AU4', 'VC3')
        while(len(SONET_Split)-n) : # 쪼개진 경보 길이만큼 반복
            SDH_Temp=SDH_Temp+SONET_Split[n]+'-' #변환된 SDH 경보를 다시 재 조립
            n=n+1

    else : # TUG가 없는경우(SONET_Split[4] 가 없는 경보)
        SONET_Split[0] = SONET_Split[0].replace('OC256', 'STM64')
        SONET_Split[0] = SONET_Split[0].replace('OC48', 'STM16')
        SONET_Split[0] = SONET_Split[0].replace('OC12', 'STM4')
        SONET_Split[0] = SONET_Split[0].replace('OC3', 'STM1')
    while(len(SONET_Split)-n) :# 쪼개진 경보 길이만큼 반복
        SDH_Temp=SDH_Temp+SONET_Split[n]+'-' #변환된 SDH 경보를 다시 재 조립
        n=n+1
    SDH=SDH_Temp[0:len(SDH_Temp)-1] #최종 변환된 SDH경보에서 '-' text제거하기 위한 목적
    return(SDH)

def getCrs(hostnames,NE_IP) : #[모듈] 텔넷 후 Log Parsing

    telnet =Telnet(NE_IP)
    telnet.read_until('<')
    telnet.write('ACT-USER:'+hostnames+':ADMIN:CTAG::ADMIN:;')
    telnet.read_until('<')
    telnet.write('RTRV-CRS-VT2:'+hostnames+':ALL:CTAG:::,;')
    Logs=telnet.read_until('<')
    print(hostnames + '(' + NE_IP + ')' + ' getCrs Completed!')
    telnet.write('CANC-USER:'+hostnames+':ADMIN:CTAG;')
    telnet.close()

    return Logs

def getAlms(hostnames,NE_IP) : #[모듈] 텔넷 후 Log Parsing

    telnet =Telnet(NE_IP)
    telnet.read_until('<')
    telnet.write('ACT-USER:'+hostnames+':ADMIN:CTAG::ADMIN:;')
    telnet.read_until('<')
    telnet.write('RTRV-ALM-ALL:'+hostnames+':ALL:CTAG:::,;')
    Logs=telnet.read_until('<')
    print(hostnames + '(' + NE_IP + ')' + ' getAlms Completed!')
    telnet.write('CANC-USER:'+hostnames+':ADMIN:CTAG;')
    telnet.close()

    return Logs

#메인모듈로서 이 화일을 실행하면 최초 이부분부터 실행됨

NE_IP=getNeip()

for IP in NE_IP:
    AlmLocation = []
    cause = []
    years = []
    months=[]
    days=[]
    crs1 = []
    crs2 = []
    bothUneq = 0
    bothUneq1 =0
    fromUneq = 0
    toUneq = 0
    bothNotUneq = 0

    alms = getAlms('',IP)
    alm = alms.split('   "')
    alm=alm[1:]

    for i in range(len(alm)): # 장비 알람 저장
        if alm[i][0]=='V':
            alm1 = alm[i].split(',')
            year=int(alm1[9].split('=')[1])
            month = int(alm1[4].split('-')[0])
            day = int(alm1[4].split('-')[1])

            AlmLocation.append(alm1[0])
            cause.append(alm1[2])
            years.append(year)
            months.append(month)
            days.append(day)


    crs=getCrs('', IP)
    crs=crs.split('   "')
    for i in range(len(crs)):
        if crs[i][0]=='V':
            crstmp = crs[i].split(',')
            crs1.append(crstmp[0])
            crs2.append(crstmp[1].split(':')[0])

    for i in range(len(crs1)):
        if (crs1[i] in AlmLocation) and (crs2[i] in AlmLocation):
            k=AlmLocation.index(crs1[i])
            j=AlmLocation.index(crs2[i])

            dt11=datetime.datetime.now()
            dt12=datetime.datetime(years[k],months[k],days[k])
            dt21=datetime.datetime.now()
            dt22=datetime.datetime(years[j],months[j],days[j])

            td1=dt11-dt12
            td2 = dt21 - dt22

            date11=dt12.strftime('%Y-%m-%d')
            date22=dt22.strftime('%Y-%m-%d')

            if td1.days > 30 or td2.days > 30:
                if cause[k]=='UNEQ' :
                    print(crs1[i]+' ~ '+crs2[i])
                    'DLT-CRS-VT2::'+crs1[i]+','+crs2[i]+':CTAG:::,;'

                    print(AlmLocation[k]+'~'+cause[k]+" "+date11)
                elif cause[j]=='UNEQ':
                    print(crs1[i]+'~'+crs2[i])
                    print(AlmLocation[j]+' : '+cause[j]+" : "+date22)


    print(fromUneq)
