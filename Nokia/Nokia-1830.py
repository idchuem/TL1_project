import pandas as pd
import telnetlib
import sys
import time

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
                list[index] = bytes(item, encoding='utf-8')
            match_index,match_object, match_text = super(Telnet, self).expect(list,timeout)
            return match_index, match_object, str(match_text,encoding='utf-8')


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
#	now_date= str(now.tm_year)+str(mon)+str(day)+str(hour)+str(min)
	now_date= str(mon)+str(day)
	return(now_date)

def NE_IP(Model) : #장비 IP리스트 수집 함수
    IP=[]
    f=open('c:/intel/'+Model, encoding='utf-8')
    for line in f.read().split():
        IpTemp=line
        IP.append(IpTemp)
    f.close()
    return IP

def LogParsing(NE_IP) : #장비 접속 수 TL1수행 함수
    print(NE_IP+' - Started')
    telnet=Telnet(NE_IP)
    telnet.read_until('login:')
    telnet.write('cli')
    telnet.read_until('username:')
    telnet.write('admin')  # TL1 경보조회 명령
    telnet.read_until('password:')
    telnet.write('admin')
    telnet.read_until('?')
    telnet.write('Y')
    telnet.read_until('#')
    telnet.write('show card inventory *')
    Inventory=telnet.read_until('#')

    for line in Inventory.readlines():
        try:
            data1 = line.split(":")  # Inventory 라인 쪼개기
            data2 = data1[2].split(",")  # TYPE 데이터 쪼개기
            data3 = data2[6].split("=")  # TCUR 데이터 쪼개기
            data4 = data1[0].split('"')
            if data3[0] == "TCUR":  # 온도 데이터(TCUR) 있는지 확인
                # temp1.append(TID)
                temp2.append(IP[i])
                temp3.append(data4[1])
                temp4.append(data2[6])
                temp5.append(data2[7])
                if (int(data3[1]) >= 50):
                    # temp6.append(TID)
                    temp7.append(IP[i])
                    temp8.append(data4[1])
                    temp9.append(data2[6])
                    temp10.append(data2[7])
        except IndexError:
            data1[0] = 1

    # result["00_TID"] = temp1
    result["01_NE IP"] = temp2
    result["02_Location"] = temp3
    result["03_Current Temp"] = temp4
    result["01_Average Temp"] = temp5

    f.close()
    df = pd.DataFrame(result)
    df.to_csv("c:/intel/" + IP[i] + "_temperature.csv", index="false", encoding='ms949')
    print(IP[i] + ' - Completed')

    #    result["00_TID"] = temp6


result["01_NE IP"] = temp7
result["02_Location"] = temp8
result["03_Current Temp"] = temp9
result["01_Average Temp"] = temp10

df = pd.DataFrame(result)
df.to_csv("c:/intel/temperature_All.csv", index="false", encoding='ms949')
print('finished')

telnet.close()

    return Logs1 # Log반환



if __name__ == '__main__':
    now_date = now_time()  # 시간호출
    LogFileAll = open('Inventories for temperature checking' + now_date+'.log','w', encoding='ms949')
    IP=NE_IP("6500.txt")


    temp6 = []
    temp7 = []
    temp8 = []
    temp9 = []
    temp10 = []


    for i in range(len(IP)) : #장비 수 만큼 온도수집 수행
        LogParsed = LogParsing(IP[i])

        data1 = []
        data2 = []
        data3 = []
        data4 = []
        result = {}
        temp1 = []
        temp2 = []
        temp3 = []
        temp4 = []
        temp5 = []
        Tid = ""
        TID = ""
        #print(TidParsed)
        #Tid = TidParsed.split('\\"')  # Inventory 라인 쪼개기
        #TID=Tid[2]

        #if TID != True:
        #    TID=Tid[3]

        f = open(IP[i]+'_log_all_'+ now_date +'.log', 'w', encoding='ms949')  # 파싱된 로그를 임시 저장할 파일
        f.write(LogParsed)  # 임시 파일에 로그 저장
        f.close()

        f = open(IP[i]+'_log_all_'+ now_date +'.log', 'r', encoding='ms949')  # 파싱된 로그를 임시 저장할 파일


        for line in f.readlines():
            try:
                data1 = line.split(":") # Inventory 라인 쪼개기
                data2 = data1[2].split(",") # TYPE 데이터 쪼개기
                data3 = data2[6].split("=") # TCUR 데이터 쪼개기
                data4 = data1[0].split('"')
                if data3[0] == "TCUR" : #온도 데이터(TCUR) 있는지 확인
                    #temp1.append(TID)
                    temp2.append(IP[i])
                    temp3.append(data4[1])
                    temp4.append(data2[6])
                    temp5.append(data2[7])
                    if (int(data3[1]) >= 50):
                        #temp6.append(TID)
                        temp7.append(IP[i])
                        temp8.append(data4[1])
                        temp9.append(data2[6])
                        temp10.append(data2[7])
            except IndexError :
                data1[0]=1


#    result["00_TID"] = temp6
    result["01_NE IP"] = temp7
    result["02_Location"] = temp8
    result["03_Current Temp"] = temp9
    result["01_Average Temp"] = temp10

    df = pd.DataFrame(result)
    df.to_csv("c:/intel/temperature_All.csv",index="false", encoding='ms949')
    print('finished')
