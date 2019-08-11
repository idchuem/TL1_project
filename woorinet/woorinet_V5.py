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
# Import NE IP from Text file
################################################################################################
def NE_IP(Model):  # 장비 IP리스트 수집 함수
    IP = []
    f = open('c:/intel/' + Model + '.txt', encoding='utf-8')
    for line in f.read().split():
        IpTemp = line
        IP.append(IpTemp)
    f.close()
    return IP


################################################################################################
# Create TL1 device class
################################################################################################
class Woorinet:
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
        print('Successfully logged in')
        return telnet

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
    def LogParsing(NE_IP, line):
        line2 = line.split(";")
        node = line2[1]
        line3 = line2[0].split('   "')
        line4 = line3[0].split('/*')
        line4 = line4[1:]  # line4 = header(괜찮음)
        line5 = line3[1:]  # line5 = value
        temp1 = ""
        temp2 = ""

        # head 라인과 Value 라인 갯수가 일치하지 않는 경우
        if len(line5) == False:
            print('line empty')
        elif len(line4) > len(line5):
            line4 = line4[-len(line5):]
        elif len(line4) < len(line5):
            tmp = line4[0]
            for k in range(len(line5)):
                line4.append(tmp)

        for i in range(len(line4)):
            temp = line4[i].strip(' */\r\n')
            temp1 = temp1 + ',' + temp

        heading = temp1[1:]

        for i in range(len(line5)):
            line6 = line5[i].strip('\r\n')
            if line6[-1] == '"':
                line6 = line6.strip('"')
                temp2 = temp2 + ',' + line6
        value = temp2[1:]
        return heading, value
        ##### String: ?? #####

    ############################################################################################
    # Returns system name in sting
    ############################################################################################
    def get_sysname(NE_IP, telnet):
        telnet.write(';\n')
        telnet.read_until(';')
        telnet.write('RTRV-SYS:::;\n')
        Log = telnet.read_until(';')
        head, val = Woorinet.LogParsing(NE_IP, Log)
        head = head.split(',')
        val = val.split(',')

        heading = head[0] + ',' + head[1]
        value = val[0] + ',' + val[1]

        return heading, value
        ##### $AU3USAGE,$AU4USAGE #####

    ############################################################################################
    # Returns low-order capacity usage in percentage(string)
    ############################################################################################
    def get_lowcapa(NE_IP, telnet):
        telnet.write('RTRV-LO-CAPA:::;\n')
        Log = telnet.read_until(';')
        head, val = Woorinet.LogParsing(NE_IP, Log)

        head = head.split(',')
        val = val.split(',')

        Usage_AU3 = int(100 * (int(val[0]) / int(val[1])))
        Usage_AU4 = int(100 * (int(val[2]) / int(val[3])))

        heading = 'Usage_AU3,Usage_AU4'
        value = str(Usage_AU3) + "%," + str(Usage_AU4) + "%"

        return heading, value
        ##### String: AU3usage,AU4usage #####

    ############################################################################################
    # Returns software version of device
    ############################################################################################
    def get_swversion(NE_IP, telnet):
        telnet.write('RTRV-VER-SW:::;\n')
        Log = telnet.read_until(';')
        head, val = Woorinet.LogParsing(NE_IP, Log)

        head = head.split(',')
        head[0] = head[0].split(':')[0]
        val = val.split(',')
        val[0] = val[0].split(':')[0]

        heading = head[0] + ',' + head[1]
        value = val[0] + ',' + val[1]

        return heading, value
        ##### String: MCUSlot,SWVersion #####

    ############################################################################################
    # Returns clock configuration
    ############################################################################################
    def CLK(NE_IP, telnet):
        telnet.write('RTRV-CLK:::;\n')
        Log = telnet.read_until(';')

        head, val = Woorinet.LogParsing(NE_IP, Log)

        head = head.split(',')
        val = val.split(',')

        heading = head[0] + ',' + head[1] + ',' + head[2]
        value = val[0] + ',' + val[1] + ',' + val[2]

        return heading, value
        ##### String: ProvisionClock1,ProvisionClock2,CurrenClock #####

    ############################################################################################
    # Returns clock configuration on TSI slot
    ############################################################################################
    def ALM(NE_IP, telnet):
        telnet.write('RTRV-ALM:::;\n')
        Log = telnet.read_until(';')
        head, val = Woorinet.LogParsing(NE_IP, Log)
        value = ''
        head = head.split(',')
        heading = head[0].split(':')[0] + '.' + val[2] + '.' + val[3] + ',' + val[4]

        val = val.split(',')
        for i in range(int(len(val) / 5)):
            value = value + val[i * 5].split(':')[0] + ',' + val[i * 5 + 2] + ',' + val[i * 5 + 3] + ',' + val[
                i * 5 + 4]

        print(value)
        return heading, value
        ##### String: CardType,Reason,DATETIME #####

    ############################################################################################
    # Returns Port Configuration on Slot
    ############################################################################################
    def PORT(NE_IP, AID, telnet):
        telnet.write('RTRV-PORT::' + AID + ':;\n')
        Log = telnet.read_until(';')
        head, val = Woorinet.LogParsing(NE_IP, Log)
        heading = head
        value = val.split(',')[1]
        value = value.split(':')[1]
        return heading, value
        ##### String: Slot-Port,ACT #####

    ############################################################################################
    # Returns MSP protection failure
    ############################################################################################
    def get_mspFailure(NE_IP, telnet):
        telnet.write('RTRV-SW:::;\n')
        Log = telnet.read_until(';')
        head, val = Woorinet.LogParsing(NE_IP, Log)

        head = head.split(',')
        val = val.split(',')
        value = ""
        head1, alms = Woorinet.ALM(NE_IP, telnet)  # 모든 ALM 긁어오기

        for i in range(len(val)):
            if val[i] == 'P-FAIL':  # Protection Fail인데
                port = val[i - 2].split(':')[0]  # P-Fail 포트 선언
                head1, act = Woorinet.PORT(NE_IP, port, telnet)  # P-Fail포트가 ACT인지 확인
                if len(port) == 3:  # Port가 Card로 표현되는 Case의 예외처리(S3A => S3A-P1)
                    port = port + '-P1'
                if act == 'ACT' and (port not in alms):  # P-Fail포트가 act면서 알람도 없으면 절체불가상태로 판단.
                    value = value + port + '\n'

        heading = 'SW-FAIL'
        return heading, value

    ############################################################################################
    # Returns MSSPR protection failure
    ############################################################################################
    def get_mssprFailure(NE_IP, telnet):
        telnet.write('RTRV-SW-MSSPR:::;\n')
        Log = telnet.read_until(';')
        head, val = Woorinet.LogParsing(NE_IP, Log)
        head = head.split(',')
        val = val.split(',')
        value = ""
        print(val)
        swtype = ['SWITCHING', 'THROUGH', 'LEARNING']
        for i in range(len(val)):
            if val[i] in swtype:  # MSSPR IDLE상태가 아닌 경우
                port = val[i - 1].split(':')[0]
                state = val[i]
                value1 = port + ', ' + state + '\n'
                value = value + value1
        print(value)
        heading = 'MSSPR-FAIL'
        return heading, value


if __name__ == '__main__':

    head1 = ""
    TID = []
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

    IP = NE_IP("woorinet_neip.txt")

    for i in range(len(IP)):  # IP수 만큼 함수 실행
        telnet = Woorinet.login(IP[i])  # TL1접속

        Heading, Value = Woorinet.get_sysname(IP[i], telnet)

        head1 = Heading.split(',')
        val1 = Value.split(',')
        TID.append(val1[0])
        Location.append(val1[1])
'''
        # Low Order 용량 조회
        Heading, Value = Woorinet.get_lowcapa(IP[i], telnet)
        head2 = Heading.split(',')
        val2 = Value.split(',')
        AU3Usage.append(val2[0])
        AU4Usage.append(val2[1])
'''
        # MCU 버전 조회
        Heading, Value = Woorinet.get_swversion(IP[i], telnet)
        head3 = Heading.split(',')
        val3 = Value.split(',')
        SLOT.append(val3[0])
        VER.append(val3[1])
'''
        # Clock원 조회
        Heading, Value = Woorinet.CLK(IP[i], telnet)
        head4 = Heading.split(',')
        val4 = Value.split(',')
        CURCLK.append(val4[0])
        PRVCLK1.append(val4[1])
        PRVCLK2.append(val4[2])
        # MSP-SW FAIL 조회
        Heading, Value = Woorinet.get_mspFailure(IP[i], telnet)
        head5 = Heading
        SWFAIL.append(Value)
        # MSSPR FAIL 조회
        Heading, Value = Woorinet.get_mssprFailure(NE_IP, telnet)
        head6 = Heading
        MSSPRFAIL.append(Value)

    result = {head1[0]: TID, head1[1]: Location, head2[0]: AU3Usage, head2[1]: AU4Usage, head3[0]: SLOT, head3[1]: VER,
              head4[0]: CURCLK, head4[1]: PRVCLK1, head4[2]: PRVCLK2, head5: SWFAIL, head6: MSSPRFAIL}
'''
    result={head1[0]: TID, head1[1]:Location, head3[1]:VER}

    # print(result)
    df = pd.DataFrame(result)
    print(df)
    df.to_csv("c:/intel/woorinet_version.csv", index="False", encoding='ms949')
    print(' Completed')