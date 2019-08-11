# -*- coding: utf-8 -*-
#!/opt/liko/bin/python

import os
import sys
#import ConfigParser
import telnetlib
#import AF6500_LIST
import time

class Telnet(telnetlib.Telnet, object):
    if sys.version > '3':
        def read_until(self, expected, timeout = None):
            expected = bytes(expected, encoding = 'utf-8')
            received = super(Telnet, self).read_until(expected, timeout)
            return str(received, encoding = 'ms949', errors = 'ignore')

        def write(self, buffer):
            buffer = bytes(buffer, encoding = 'utf-8')
            super(Telnet, self).write(buffer)

        def expect(self, list, timeout = None):
            for index, item in enumerate(list):
                list[index] = bytes(item, encoding = 'utf-8', errors = 'ignore')
            match_index, match_object, match_text = super(Telnet, self).expect(list, timeout)
            return match_index, match_object, str(match_text, encoding = 'utf-8')


def getneip():
    ip = []
    f = open('NE_IP', encoding = 'utf-8')
    for line in f.read().split():
        ip.append(line)
    f.close()
    return(ip)

#[모듈] SONET->SDH 계위변경
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

#[모듈] 텔넷 후 Log Parsing
def LogParsing(hostnames,NE_IP) :

  #####텔넷 접속#####
  telnet =Telnet(NE_IP)
  telnet.read_until('<') #"<" 이 나올때까지 문자열 읽어들임, 저장은 안함
  telnet.write('ACT-USER:'+hostnames+':ADMIN:CTAG::ADMIN:;') # TL1 로그인 명령
  telnet.read_until('<')

  #####경보조회 명령실행#####
  telnet.write('RTRV-ALM-ALL:'+hostnames+':ALL:CTAG:::,;') #TL1 경보조회 명령
  Logs=telnet.read_until('<') #< 이 나올때까지 RTRV로그를 읽어서 Log에 저장
  print hostnames + '(' + NE_IP + ')' + ' Parsing Completed!'

  #####텔넷 종료####
  telnet.write('CANC-USER:'+hostnames+':ADMIN:CTAG;') #TL1 로그오프 명령
  telnet.close()

  return Logs # Log반환


class ciena:

  def __init__(self, IP):
    self.dt = datetime.datetime.now()
    self.dtStr = self.dt.strftime('%Y-%m-%d %Hh%Mm%Ss')
    self.NE_IP = IP
    self.tl1 = self.LogIn()
    self.NE_ID = self.GetNeid()

  def LogIn(self):
    tl1 = Telnet(self.NE_IP)
    tl1.read_until('<')
    tl1.write('ACT-USER::ADMIN:CTAG::ADMIN:;')
    tl1.read_until('<')
    return tl1

  def LogOut(self):
    self.tl1.write('CANC-USER:' + self.NE_ID + ':ADMIN:CTAG;')
    self.tl1.close()

  def GetNeid(self):
    self.tl1.write(';')
    tmp = self.tl1.read_until('<')
    hostname = tmp[8:20]
    return hostname

  def GetAlm(self):  # [모듈] 텔넷 후 Log Parsing
    print(self.NE_ID + ' (' + self.NE_IP + ')  에서 현재 알람을 추출중입니다...')
    location, severity, cause, description, datetimes = [], [], [], [], []
    self.tl1.write('RTRV-ALM-ALL:' + self.NE_ID + ':ALL:CTAG:::,;')
    Logs = self.tl1.read_until('<')
    lines = Logs.split('   "')[1:]
    for line in lines:
      alm = line.split(',')
      dateTmp = alm[4].split('-')
      timeTmp = alm[5].split('-')
      dt = datetime.datetime(int(alm[9].split('=')[1]), int(dateTmp[0]), int(dateTmp[1]), int(timeTmp[0]),
                             int(timeTmp[1]), int(timeTmp[2]))  # year, month, day, hour, min, sec
      datetimes.append(dt)
      location.append(alm[0])
      severity.append(alm[1].split(':')[1])
      cause.append(alm[2])
      description.append(alm[7].split(':')[1][1: -1])
    almParsed = {'location': location, 'severity': severity, 'cause': cause, 'description': description,
                 'datetimes': datetimes}
    print('완료!\n')
    return almParsed

  def GetCrs(self):  # [모듈] 텔넷 후 Log Parsing
    print(self.NE_ID + ' (' + self.NE_IP + ') 에서 맵 정보를 추줄중입니다...')
    crs1, crs2 = [], []
    self.tl1.write('RTRV-CRS-VT2:' + self.NE_ID + ':ALL:CTAG:::,;')
    Logs = self.tl1.read_until('<')
    lines = Logs.split('   "')
    for line in lines:
      if line[0] == 'V':
        crsTmp = line.split(',')
        crs1.append(crsTmp[0])
        crs2.append(crsTmp[1].split(':')[0])
    crs = {'from': crs1, 'to': crs2}
    print('완료!\n')
    return crs

  def DelCrs(self, deadCkt):
    delDenied = []
    f = open('Delete result ' + self.NE_IP, 'wt')
    f1 = open('Delete denied ' + self.NE_IP, 'wt')
    for crs1, crs2 in zip(deadCkt['From'], deadCkt['To']):
      delCommand = "DLT-CRS-VT2::" + crs1 + "," + crs2 + ":CTAG:::,;"
      # self.tl1.write('delCommand')
      # result = self.tl1.expect(['COMPLD','DENY']
      # result = result[2][result[1].span()[0]:result[1].span()[1]]
      f.write('Command :' + delCommand + '\n')
      '''
      f.write('result  :'+result + '\n\n')
      if result == 'DENY':

          f1.write('Command :' + delCommand + '\n')
          f.write('result  :' + result + '\n\n')
          delDenied.append(delCommand)
      '''
    f1.close()
    f.close()
    if len(delDenied) != 0:
      print('삭제에 실패한 회선이 있습니다. 확인이 필요합니다.\n')
      for line in delDenied:
        print('Command: ' + line)
    return delDenied

  def ResCrs(self, resCkt):
    f = open('Restore result ' + self.NE_IP, 'wt')
    f1 = open('Restore denied ' + self.NE_IP, 'wt')
    for crs1, crs2 in zip(resCkt['From'], resCkt['To']):
      crsCommand = "ENT-CRS-VT2::" + crs1 + "," + crs2 + ":CTAG::2WAY:,,CKTID = 'Restored',,;"
      print(crsCommand)
      # self.tl1.write(crsCommand)
      # result = self.tl1.until('<')
      # result = self.tl1.expect(['COMPLD','DENY']
      # result = result[2][result[1].span()[0]:result[1].span()[1]]
      f.write('Command :' + crsCommand + '\n')
      """
      f.write('result  :'+result + '\n\n')
      if result == 'DENY':

          f1.write('Command :' + delCommand + '\n')
          f.write('result  :' + result + '\n\n')
          delDenied.append(delCommand)
      """
    f.close()
    f1.close()

  def CrsInAlm(self, crs, alm):
    print(self.NE_ID + ' (' + self.NE_IP + ')  에서 미사용 회선을 추출 중 입니다...')
    deadFrom, deadTo = [], []
    cktDead = open('Dead Circuits' + IP, 'wt')
    for crs_from, crs_to in zip(crs['from'], crs['to']):
      if (crs_from in alm['location']) and (crs_to in alm['location']):  # IF CROSS-CONNECT 'FROM,TO' ARE BOTH ALARMED
        k = alm['location'].index(crs_from)
        j = alm['location'].index(crs_to)
        dt1 = alm['datetimes'][k]
        dt2 = alm['datetimes'][j]
        td1 = self.dt - dt1
        td2 = self.dt - dt2
        if td1.days > 30 or td2.days > 30:  # IF ALARMED ELASPED MORE THAN 30 DAYS
          if (alm['cause'][k] == 'UNEQ') or (alm['cause'][j] == 'UNEQ'):
            date_from = dt1.strftime('%Y-%m-%d')
            date_to = dt2.strftime('%Y-%m-%d')
            cktDead.write('CrsFrom: ' + crs_from + '\n')
            cktDead.write('Almfrom: ' + alm['location'][k] + ' (' + alm['cause'][k] + ", " + date_from + ')' + '\n')
            cktDead.write('CrsTo  : ' + crs_to + '\n')
            cktDead.write('AlmTo  : ' + alm['location'][j] + ' (' + alm['cause'][j] + ", " + date_to + ')' + '\n\n')
            deadFrom.append(crs_from)
            deadTo.append(crs_to)
    cktDead.close()
    deadCkt = {'From': deadFrom, 'To': deadTo}
    print('완료!!!\n미사용 내역은 "dead circuits ' + IP + '.log"  파일에서 확인 가능합니다.\n')
    return deadCkt


#메인모듈로서 이 화일을 실행하면 최초 이부분부터 실행됨
if name == 'main':
  host = []
  NE_IP = getneip()
  f = open('readme', 'rt', encoding='utf-8')
  readme = f.read()
  f.close()
  print(readme)
  cmd = input()
  if cmd == 'start':
    for IP in NE_IP:
      node = ciena(IP)
      host.append(node)
      alm = node.GetAlm()
      crs = node.GetCrs()
      deadCkt = node.CrsInAlm(crs, alm)

  now_date=now_time() #시간호출
  connect_id='AF6500-ID' # ConfigParser에서 AF6500-ID Section을 호출하기 위한 변수
  NE_IP = AF6500LIST.af6500_list() #AF6500 외부 함수모듈(ConfigParser)에서 NE_IP추출
  LogFileAll = open('전체장비 경보내역' + now_date + '.log', 'w')
  temp = 'AF6500-TID' # ConfigParser를 통해 TID를 읽어오기 위한 Section 변수 선언
  hostnames=[]

  for i in range(len(NE_IP)) : #NE의 갯수만큼 로그 파싱 반복구문

    hostnames.append(cp.get(temp, NE_IP[i])) #hostname(TID) 을 반복문에서 리스트 형태로 추가, temp(AF6500-TID) Section과 NE_IP(IP주소) 인덱스를 통해 TID 값 찾아냄
    LogParsed = LogParsing(hostnames[i], NE_IP[i]) # 로그 파싱 함수 호출
    WriteTemp=open(hostnames[i]+'_log_all_'+now_date+'.log','w') #파싱된 로그를 임시 저장할 파일
    WriteTemp.write(NE_IP[i]+'₩x0d') # 임시 파일 상단에 IP주소 추가
    WriteTemp.write(LogParsed) # 임시 파일에 로그 저장
    WriteTemp.close()

    ReadTemp=open(hostnames[i]+'_log_all_'+now_date+'.log','r') # 파일을 다시 읽어들임
    line=ReadTemp.readline() # 읽어들인 파일을 변수에 저장
    LineTemp=''

    while(line) : # 로그 1차 가공 반복문으로 로그 Record만큼 반복
      if line.find('SDH')>=0 :
        temp1=line.split('₩x0d') #문자열을 개행문자 단위(Record)로 쪼갬
        temp1[0]=temp1[0].strip() #앞뒤 빈칸 삭제
        LineTemp=LineTemp+temp1[0]+'₩n' #경보로그만 임시 변수에 행 단위로 저장
            line =ReadTemp.readline() #Readline을 통해 경보로그를 line에 다시 저장

Jun, [06.02.19 09:00]
NE_Log=open(hostnames[i]+'_경보내역_'+now_date+'.log','w') #가공된 로그를 다시 파일로 저장
    NE_Log.write(LineTemp)
    NE_Log.close()

    result_line=hostnames[i]+'₩n'+LineTemp+'₩n' #가공된 로그에 TID를 붙여 변수저장

    LogFileAll.write(result_line) #전체 로그가 저장될 파일에 해당 노드의 로그 추가
    ReadTemp.close()
    os.system('del '+hostnames[i]+'_log_all_'+now_date+'.log₩n') #임시 로그 저장 피일 삭제

  tempresult1 = ''

  LogFileAll.close()

  for i in range(len(NE_IP)/2) :
    print 'Comparing '+hostnames[(i*2)+1]+' and '+ hostnames[(i*1)*2]
    ALL_COMPARE=open('전체장비 경보일치 비교내역'+now_date+'.log','a')

    NE1_Log=open(hostnames[(i*2)+1]+'_경보내역_'+now_date+'.log','r')
    NE2_Log=open(hostnames[(i*1)*2]+'_경보내역_'+now_date+'.log','r')


    NE1 = NE1_Log.readlines()
    NE2 = NE2_Log.readlines()

    tempsting1=""
    tempsting2=""

    NE1_CID=[]
    NE1_Desc=[]
    NE2_CID=[]
    NE2_Desc=[]

    NE1_result=''
    NE2_result=''

    for k in range(len(NE1)):
      tempstring1=NE1[k].split(":")
      tempstring2=tempstring1[0].split(",")
      tempstring3=tempstring2[0].split('"')
      tempstring11=tempstring1[1].split(",")
      NE1_CID.append(tempstring3[-1])
      NE1_Desc.append(tempstring11[1])

    for k in (range(len(NE2))) :
      tempstring4=NE2[k].split(":")
      tempstring5=tempstring4[0].split(",")
      tempstring6=tempstring5[0].split('"')
      tempstring44 = tempstring4[1].split(",")
      NE2_CID.append(tempstring6[-1])
      NE2_Desc.append(tempstring44[1])

  #  1번장비에 경보 2번장비와 매치하지 않는지
    n=0

    while(len(NE1)>n) :
      try :
        NE2_CID_Index = NE2_CID.index(NE1_CID[n])
        if NE1_Desc[n]!=NE2_Desc[NE2_CID_Index] :
          #print '1a('+str(n)+') : '+doj1a[n]+' - 2a('+str(index2a)+') : '+doj2a[index2a]+' 일치, 1z('+str(n)+') : '+doj1z[n]+' - 2z('+str(index2a)+') : '+doj2z[index2a]+' 일치'
          NE1_CID_SDH = SONET_TO_STM(NE1_CID[n])
          tempresult1 = tempresult1 + '1번장비 : ' + NE1_CID_SDH +' : ' + NE1_Desc[n] + ' 와 2번장비' + NE2_CID[NE2_CID_Index] + NE2_Desc[NE2_CID_Index] + ' : 경보명이 서로 다름' + '₩n'
        #1의 경보와 #2의
      except ValueError: #NE1의 CID가 NE2에 없는 경우
        NE1_CID_SDH=SONET_TO_STM(NE1_CID[n])
        tempresult1=tempresult1+'#1에만 경보 존재: '+ NE1_CID_SDH +' : '+ NE1_Desc[n] + '₩n'
      n=n+1

    # 2번장비에 경보가 1번장비와 매치하지 않는지
    n=0
    while(len(NE2)>n) :
      try:
        NE1_CID_Index=NE1_CID.index(NE2_CID[n])
        if NE2_Desc[n]!=NE1_Desc[NE1_CID_Index] :
          NE2_CID_SDH = SONET_TO_STM(NE2_CID[n])
          tempresult1 = tempresult1 + '2번장비 경보' +NE2_CID_SDH+ ' : '+ NE2_Desc[n] + '와 1번장비 경보' +NE1_CID_SDH[NE1_CID_Index] +':'+NE1_Desc[NE1_CID_Index] +  '의 경보명이 서로 다름' +'₩n'
      except ValueError:
        NE2_CID_SDH = SONET_TO_STM(NE2_CID[n])
        tempresult1 = tempresult1 + '#2에만 경보 존재: ' +NE2_CID_SDH+' : '+NE2_Desc[n]+'₩n'
      n=n+1

    NE_result_summary=''
    if len(NE1)==len(NE2) :
      NE_result_summary = hostnames[(i*1)*2]+' 경보개수 : ' + str(len(NE1))+'₩n'
      NE_result_summary = NE_result_summary + hostnames[(i*2)+1]+' 경보개수 : ' + str(len(NE2)) +'₩n'
      NE_result_summary = NE_result_summary + '==> 경보 개수 일치'

    else :
      NE_result_summary = hostnames[(i * 1) * 2] + ' 경보개수 : ' + str(len(NE1)) + '₩n'
      NE_result_summary = NE_result_summary + hostnames[(i * 2) + 1] + ' 경보개수 : ' + str(len(NE2)) + '₩n'
      NE_result_summary = NE_result_summary + '==> 경보 개수 불일치'

    ALL_COMPARE.write('■■■■'+hostnames[(i*1)*2]+' & '+hostnames[(i*2)+1]+'■■■■'+'₩n')
    ALL_COMPARE.write(NE_result_summary+'₩n')
    ALL_COMPARE.write(tempresult1+'₩n')
    ALL_COMPARE.close()

    NE1_Log.close()
    NE2_Log.close()
  print('.')
  print('.')
  print('.')
  raw_input("종료하려면 엔터키를 누르십쇼....")