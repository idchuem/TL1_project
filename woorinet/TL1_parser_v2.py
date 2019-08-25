#-*- coding:UTF-8 -*-

import pandas as pd
import telnetlib
import sys

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


################################################################################################
# returns IP list from Text file
################################################################################################
def get_neip(Model):
    IP = []
    f = open('c:/intel/' + Model + '.txt', encoding='utf-8')
    for line in f.read().split():
        IpTemp = line
        IP.append(IpTemp)
    f.close()
    return IP


class woorinet:
    ############################################################################################
    # connect and login to TL1 device
    ############################################################################################
    def login(NE_IP):
        telnet = Telnet(NE_IP, port=5543)
        print('\nLogging in ' + NE_IP)
        telnet.read_until(':')
        telnet.write('ADMIN\n')
        telnet.read_until(':')
        telnet.write('ADMIN\n')
        telnet.write(';\n')
        neid = telnet.read_until(';')
        neid=neid[8:15]
        print('Successfully logged in')
        return telnet, neid

    ############################################################################################
    # Logout and disconnect from TL1 device
    ############################################################################################
    def logout(NE_IP):
        print('Logging out')
        telnet.write('CANC-USER::ADMIN:CTAG;')
        telnet.close()
        print('Logged out from ' + NE_IP)

    ############################################################################################
    # Process TL1 response message
    ############################################################################################
    def get_logs(NE_IP, line1):
        tmp = ""
        line2 = line1.strip(";")
        line3 = line2.split('   "')
        line4 = line3[1:]  # line4 = value
        if len(line4) == False:
            line4 = '-'
            print('line empty')
        for i in range(len(line4)):
            line6 = line4[i].strip('\r\n')
            line6 = line6.split('"')[0]
            tmp = tmp + ',' + line6
        value = tmp[1:]
        return value

    ############################################################################################
    # Returns system name in sting
    ############################################################################################
    def get_sysname(NE_IP, telnet):
        telnet.write(';\n')
        telnet.read_until(';')
        telnet.write('RTRV-SYS:::;\n')
        Log = telnet.read_until(';')
        val = woorinet.get_logs(NE_IP, Log)
        val = val.split(',')
        # |  val[0] |   val[1]  | val[2] |  val[3]
        # |   TID   |  Location | Vendor | DateTime
        value = val[0] + ',' + val[1]
        return value
        ##### $AU3USAGE,$AU4USAGE #####

    def get_model(NE_IP,telnet):
        telnet.write(';\n')
        telnet.read_until(';')
        telnet.write('RTRV-DATE:::;\n')
        Log = telnet.read_until(';')
        val = woorinet.get_logs(NE_IP, Log)
        val = val.split(':')[0]
        value = val.split('-')[1]
        # |  Model |
        return value
    ############################################################################################
    # Returns low-order capacity usage in percentage(string)
    ############################################################################################
    def get_lowcapa(NE_IP, telnet):
        telnet.write('RTRV-LO-CAPA:::;\n')
        Log = telnet.read_until(';')
        val = woorinet.get_logs(NE_IP, Log)
        val = val.split(',')
        # |  val[0]   |   val[1]   |  val[2] |  val[3]
        # |  AU3_USE  |  AU3_Total | AU4_USE | AU4_Total
        Usage_AU3 = int(100 * (int(val[0]) / int(val[1])))
        Usage_AU4 = int(100 * (int(val[2]) / int(val[3])))
        value = str(Usage_AU3) + "%," + str(Usage_AU4) + "%"

        return value
        ##### String: AU3usage,AU4usage #####

    ############################################################################################
    # Returns software version of device
    ############################################################################################
    def get_swversion(NE_IP, telnet):
        telnet.write('RTRV-VER-SW:::;\n')
        Log = telnet.read_until(';')
        val = woorinet.get_logs(NE_IP, Log)
        val = val.split(',')
        # |     val[0]    |    val[1]     |  val[2] |  val[3]
        # |  ActMCU:TYPE  |  Software Ver |  Date   |  Time
        val[0] = val[0].split(':')[0]
        value = val[0] + ',' + val[1]
        return value
        ##### String: MCUSlot,SWVersion #####

    ############################################################################################
    # Returns clock configuration
    ############################################################################################
    def get_clkconfig(NE_IP, telnet):
        telnet.write('RTRV-CLK:::;\n')
        Log = telnet.read_until(';')
        val = woorinet.get_logs(NE_IP, Log)
        val = val.split(',')
        # |  val[0] |  val[1] |  val[2] | val[3] |  Val[4]
        # |  CLK1   |  CLK2   |  Date   |  Time  | Revertive
        value = val[0] + ',' + val[1] + ',' + val[2]

        return value
        ##### String: ProvisionClock1,ProvisionClock2,CurrenClock #####

    ############################################################################################
    # Returns derived clock
    ############################################################################################
    def get_clkderived(NE_IP, telnet):
        telnet.write('RTRV-CLK-DERIVED:::;\n')
        Log = telnet.read_until(';')
        val = woorinet.get_logs(NE_IP, Log)
        val = val.split(',')
        # |  val[0] |  val[1] |  val[2] | val[3] |
        # |  CURCLK |  CURSSM |  CLK1   |  CLK2  |
        value = val[0] + ',' + val[1] + ',' + val[2]+ ',' + val[3]

        return value
        ##### String: ProvisionClock1,ProvisionClock2,CurrenClock #####

    ############################################################################################
    # Returns clock ssm
    ############################################################################################
    def get_clkssm(NE_IP, telnet):
        telnet.write('RTRV-SSM:::;\n')
        Log = telnet.read_until(';')
        val=woorinet.get_clkconfig(NE_IP,telnet)
        clkcfg=val.split(',')
        if clkcfg[0] == clkcfg[1]:
            act='CLK1'
        elif clkcfg[0] == clkcfg[2]:
            act='CLK2'
        val = woorinet.get_logs(NE_IP, Log)
        val = val.split(',')
        for i in range(len(val)):
            val1 = val[i].split(':')
            if val1[0]==clkcfg[0]: #EXT 이름이 SSM 결과에 있는 경우
                value=val1[0]+','+val1[1]+','+ val[i+1]
            elif val1[0] ==act: #CLK ACT side와 일치하는 경우
                value=val1[0]+','+val1[1]+','+ val[i+1]
        # |  CLKSRC, QUALITY, RXSSMPROV
        return value
        ##### String: ProvisionClock1,ProvisionClock2,CurrenClock #####

    ############################################################################################
    # Returns port state on Slot
    ############################################################################################
    def get_portstate(NE_IP, AID, telnet):
        telnet.write('RTRV-PORT::' + AID + ':;\n')
        Log = telnet.read_until(';')
        val = woorinet.get_logs(NE_IP, Log)
        # |   [0]    |    [1]               | [3] #
        # | Capacity | Slot-Port: ACT/DEACT | BER #
        value = val.split(',')[1]
        value = value.split(':')[1]
        return value

    ############################################################################################
    # Returns slot states
    ############################################################################################
    def get_slotstate(NE_IP, telnet):
        telnet.write('RTRV-SLOT:::;\n')
        Log = telnet.read_until(';')
        val = woorinet.get_logs(NE_IP, Log)
        # |   [0]     |  [1]   | #
        # | SLOT:UNIT | status | #
        print(val)
        val1=val.split(':')
        val2=val.split(',')
        return val

    ############################################################################################
    # Returns MSP protection failure
    ############################################################################################
    def get_mspfailure(NE_IP, telnet):
        telnet.write('RTRV-SW:::;\n')
        Log = telnet.read_until(';')
        val = woorinet.get_logs(NE_IP, Log)
        # |  val[0]  |   val[1]   | val[2] |  val[3]  |  Val[4] | ~~~~
        # | AID:Type | Work./Prot.| Status |  Lockout |  UNI/BI | ~~~~
        val = val.split(',')
        value = ""
        alms = woorinet.get_alms(NE_IP, telnet)  # 모든 ALM 긁어오기
        # |    val[0]    |  val[1]  |  val[2] |  val[3]  |  Val[4] | val[5]| ~~~~
        # | AID:Severity |  SA/NSA  |  TYPE   |  Reason  |  Date   | Time  | ~~~~
        for i in range(len(val)):
            if val[i] == 'P-FAIL':  # Protection Fail인데
                port = val[i - 2].split(':')[0]  # P-Fail 포트 선언
                act = woorinet.get_portstate(NE_IP, port, telnet)  # P-Fail포트가 ACT인지 확인
                if val[i+1][0]=='S': # 광카드 아닌경우(Card Protection인 경우)
                    pass
                elif len(port) == 3:  # 광카드이면서 Card Protection인 경우
                    port1 = port + '-P1' # Card 경보, Port경보 모두 비교 하기 위한
                else : #광카드 이면서 Port Protection인 경우
                    port1 = port[:3]
                if act == 'ACT':
                    if (port not in alms) or (port1 not in alms):  # P-Fail포트가 act면서 알람도 없으면 절체불가상태로 판단.
                        value = value + port + '\n'
        value=value.strip('\n')
        return value

    ############################################################################################
    # Returns MSSPR protection failure
    ############################################################################################
    def get_mssprfailure(NE_IP, telnet):
        telnet.write('RTRV-SW-MSSPR:::;\n')
        Log = telnet.read_until(';')
        val = woorinet.get_logs(NE_IP, Log)
        # |  val[0]  |     val[1]   |     val[2]    |   val[3]  |  Val[4] | Val[5]  | ~~~~
        # | AID:UNIT | MSSPR Status | Switch Status |  Lockout  |  UNI/BI | BR & SW | ~~~~
        val = val.split(',')
        failure =['SWITCHING', 'THROUGH', 'LEARNING']
        value = ""
        for i in range(len(val)):
            if val[i] in failure:  # MSSPR Status가 IDLE상태가 아닌 경우
                port = val[i - 1].split(':')[0]
                state = val[i]
                value = value + port + ', ' + state + '\n'
        value = value.strip('\n')
        return value

    ############################################################################################
    # Returns Section PM on slot/port
    ############################################################################################
    '''
    def get_tca(NE_IP, telnet):
        slot=[]
        val = woorinet.get_slotstate(NE_IP,telnet)
        val1 = val.split(',')
        value=""
        #print(val1)
        for i in range(len(val1)):
            val2=val1[i].split(':')
            if len(val2)==2 and val1[i+1]=='NORM' and val2[1][0]=='S':
                slot.append(val2[0])
        for i in range(len(slot)):
            telnet.write('RTRV-PM-RS::'+slot[i]+':;\n')
            Log = telnet.read_until(';')
            val = woorinet.get_logs(NE_IP, Log)
            print(val)
            val=val.split('-')
            for i in range(len(val)):
                val1=val[i].split(',')
                print(val1)
            # |   val[0 ]  |  val[1] |  val[2] |  val[3] |  Val[4] | val[5]~~~~
            # | PID:SIGNAL | Cur 15M | Pre 15M |  Cur 1D |  Pre 1D | ~~~~
            if int(val[3]) >= 5 or int(val[3]) >= 5 or int(val[3]) >= 5: #CUR 1Day PM이 5초 이상
                value=value + ','+val[0]+','+ val[1]+','+val[3] +'\n'
        print(value)
        return value
        '''

    ############################################################################################
    # Return alarms
    ############################################################################################
    def get_alms(NE_IP, telnet):
        telnet.write('RTRV-ALM:::;\n')
        Log = telnet.read_until(';')
        val = woorinet.get_logs(NE_IP, Log)
        value = ''
        val = val.split(',')
        # |    val[0]    |  val[1]  |  val[2] |  val[3]  |  Val[4] | val[5]| ~~~~
        # | AID:Severity |  SA/NSA  |  TYPE   |  Reason  |  Date   | Time  | ~~~~

        for i in range(int(len(val) / 5)):
            value = value + val[i * 5].split(':')[0] + ',' + val[i * 5 + 2] + ',' + val[i * 5 + 3] + ',' + val[i * 5 + 4] +','
        return value
        ##### String: CardType,Reason,DATETIME #####

    ############################################################################################
    # analyze alarms and return risky
    ############################################################################################
    def analyze_alarm(NE_IP, telnet):
        val = get_alms(NE_IP, telnet)
        # |    val[0]    |  val[1]  |  val[2] |  val[3]  |  Val[4] | val[5]| ~~~~
        # | AID:Severity |  SA/NSA  |  TYPE   |  Reason  |  Date   | Time  | ~~~~
        val = val.split(',')
        value = ""
        criticals = []
        for i in range(len(val)):
            if val[i] in criticals:  # 사전에 정의한 알람 내용이 발생하면,
                port = val[i - 3].split(':')[0]
                reason = val[i]
                date = val[i + 1] + val[i + 2]
                value = value + port + ', ' + state + ', ' + date + '\n'

        return value

############################################################################################
# Main Function
############################################################################################
if __name__ == '__main__':

    TID = []
    NEIP=[]
    NEID = []
    MODEL =[]
    Location = []
    AU3Usage = []
    AU4Usage = []
    SLOT = []
    VER = []
    CURCLK = []
    PRVCLK1 = []
    PRVCLK2 = []
    SWFAIL = []
    MSSPRFAIL = []
    CLKSSM = []
    CLKSSMPRV = []
    CLKCUR = []
    CURSSM = []
    CLKPRV1 = []
    CLKPRV2 = []

    IP = get_neip("device_list2")

    for i in range(len(IP)):  # IP수 만큼 함수 실행

        telnet,neid = woorinet.login(IP[i])  # TL1접속
        #perp=woorinet.get_performance(IP[i],telnet)
        # 시스템 정보 조회
        sysname = woorinet.get_sysname(IP[i], telnet)
        sysname = sysname.split(',')
        TID.append(sysname[0])
        Location.append(sysname[1])
        NEIP.append(IP[i])
        NEID.append(neid)
        #모델명 조회
        model=woorinet.get_model(IP[i],telnet)
        MODEL.append(model)
        """
        # Low Order 용량 조회
        val = woorinet.get_lowcapa(IP[i], telnet)
        val = val.split(',')
        AU3Usage.append(val[0])
        AU4Usage.append(val[1])
        # MCU 버전 조회
        val = woorinet.get_swversion(IP[i], telnet)
        val = val.split(',')
        SLOT.append(val[0])
        VER.append(val[1])
        # Clock원 조회
        val = woorinet.get_clkconfig(IP[i], telnet)
        val = val.split(',')
        CURCLK.append(val[0])
        PRVCLK1.append(val[1])
        PRVCLK2.append(val[2])
        # Clock원 품질조회
        val=woorinet.get_clkssm(IP[i], telnet)
        val = val.split(',')
        CURSSM.append(val[1])
        CLKSSMPRV.append(val[2])

        #유도클럭원 조회
        val =woorinet.get_clkderived(IP[i], telnet)
        val = val.split(',')
        CLKCUR.append(val[0])
        CLKSSM.append(val[1])

        # MSP-SW FAIL 조회
        val = woorinet.get_mspfailure(IP[i], telnet)
        SWFAIL.append(val)
        # MSSPR FAIL 조회
        val = woorinet.get_mssprfailure(IP[i], telnet)
        MSSPRFAIL.append(val)
        """
    result = {'노드명': TID, '모델명':MODEL, 'NE_IP': NEIP, 'NE_ID': NEID, '설치위치': Location, 'AU4사용율': AU3Usage, 'AU3사용율': AU4Usage, 'Working MCU': SLOT,
              'MCU버전': VER,
              '클럭원 1': PRVCLK1, '클럭원 2': PRVCLK2, '현재 클럭원': CURCLK ,'클럭원 품질':CLKSSM,'클럭원 설정품질':CLKSSMPRV, '유도 클럭원': CLKCUR ,'유도 클럭품질' : CLKSSM, 'MSP 절체불가': SWFAIL,
              'MSSPR 절체불가': MSSPRFAIL}

    df = pd.DataFrame(result)
    print(df)
    df.to_csv("woorinet_all.csv", index="False", encoding='ms949')
    print(' Completed')