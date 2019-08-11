import pandas as pd
import telnetlib
import sys

class Telnet(telnetlib.Telnet, object):
    if sys.version > '3':
        def read_until(self, expected, timeout=3):
            expected = bytes(expected, encoding='utf-8')
            received = super(Telnet, self).read_until(expected, timeout)
            return str(received, encoding='utf-8', errors='ignore')
        def write(self,buffer):
            buffer = bytes(buffer, encoding='utf-8')
            super(Telnet, self).write(buffer)
        def expect(self,list,timeout=3):
            for index, item in enumerate(list):
                list[index] = bytes(item, encoding='utf-8', errors='ignore')
            match_index, match_object, match_text = super(Telnet, self).expect(list, timeout)
            return match_index, match_object, str(match_text, encoding='utf-8')

def get_neip(file): #장비 IP리스트 수집 함수
    f = open(file, 'rt')
    ip = f.read().splitlines()
    return ip

class Ciena:
    class Ptn:
        def __init__(self, ip):
            self.ne_ip = ip
            self.id = 'su'
            self.password = 'wwp'
            self.tl1 = self.ne_login()
            self.ne_id = self.get_sys()
            print('Logged in - {}'.format(self.ne_ip))

        def ne_login(self):
            telnet = Telnet(self.ne_ip)
            telnet.read_until('login:')
            telnet.write('su\n')
            telnet.read_until('Password:')
            telnet.write('wwp\n')
            telnet.read_until('>')
            return telnet

        def get_sys(self):
            self.tl1.write('system show\n')
            tid = self.tl1.read_until('>')
            return tid

        def get_temp(self):
            self.tl1.write('chassis show temperature\n')
            log = self.tl1.read_until('>')
            temp_ary = self.parse(log)
            result = {'temperature': temp_ary[1]}
            return result

        @staticmethod
        def parse(log):
            table = []
            log1 = log.split('+')[-1]
            lines = log1.split('\r\n')
            for line in lines:
                columns = []
                cols = line.strip('|').split('|')
                for col in cols:
                    columns.append(col.strip())
                table.append(columns)
            return table

if __name__  == '__main__':
    neip = get_neip('5160')

    ne_ip, ne_tid, ne_temp = [], [], []
    for ip in neip:

        ne = Ciena.Ptn(ip)
        tid = ne.get_sys()
        temp = ne.get_temp()

        ne_ip.append(ip)
        ne_tid.append(tid)
        ne_temp.append(temp)

    result = {'IP':ne_ip, 'TID': ne_tid, 'Temp': ne_temp }
    df = pd.DataFrame(result)
    df.to_csv("c:/intel/5160_healthcheck.csv", index = "false", encoding = 'utf-8')
    print(' Completed')


