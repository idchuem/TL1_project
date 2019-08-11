
Jun, [06.02.19 09:00]
# -*- coding: cp949 -*-
#!/opt/liko/bin/python


import sys
import copy
import ConfigParser
from telnetlib import Telnet
import AF6500_LIST
import os
import time

cp = ConfigParser.ConfigParser() #ConfigParser함수 호출
cp.read(["AF6500_IP.conf"]) #ConfigParser로 읽어들일 IP,TID,계정 정보
AF6500LIST=AF6500_LIST #AF6500 외부 함수모듈에서 ConfigParser를 수행하는 함수 호출

#[모듈] 실행시간을 추출,화일명 생성에도 참조됨
#실제로 이 파일내에서는 now_time()함수는 하는일이 없음(날짜는 수동으로 입력)
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


#[모듈] SONET->SDH 계위변경
def SONET_TO_STM(SONET) :
  SONET_Split=SONET.split('-') # SONET 경보(SHELF-SLOT-PORT-AUG-TUG)를 - 단위로 쪼개 리스트로 저장
  SDH_Temp = "" # SDH변환을 위한 임시 변수 선언
  n = 0
  if (len(SONET_Split)>4) : # TUG(SONET_Split[4])가 존재하는 경보
    SONET_Split[1]='#'+SONET_Split[1]
    SONET_Split[2]='SL'+SONET_Split[2]
    SONET_Split[3]='P'+SONET_Split[3]
    SONET_Split[4]='AUG'+str((int(SONET_Split[4])+2)/3) #(SONET계위-> SDH변환)
    SONET_Split[0]=SONET_Split[0].replace('VT2AU4','VC12')
    SONET_Split[0]=SONET_Split[0].replace('STS3C', 'VC4')
    SONET_Split[0]=SONET_Split[0].replace('STS1AU4', 'VC3')
    while(len(SONET_Split)-n) : # 쪼개진 경보 길이만큼 반복
      SDH_Temp=SDH_Temp+str(SONET_Split[n])+'-' #변환된 SDH 경보를 다시 재 조립
      n=n+1

  else : # TUG가 없는경우(SONET_Split[4] 가 없는 경보)
    SONET_Split[0] = SONET_Split[0].replace('OC256', 'STM64')
    SONET_Split[0] = SONET_Split[0].replace('OC48', 'STM16')
    SONET_Split[0] = SONET_Split[0].replace('OC12', 'STM4')
    SONET_Split[0] = SONET_Split[0].replace('OC3', 'STM1')
    while(len(SONET_Split)-n) :# 쪼개진 경보 길이만큼 반복
      SDH_Temp=SDH_Temp+str(SONET_Split[n])+'-' #변환된 SDH 경보를 다시 재 조립
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

#메인모듈로서 이 화일을 실행하면 최초 이부분부터 실행됨
if name == 'main':

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