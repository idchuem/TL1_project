# -*- coding: utf-8 -*-
# !/opt/liko/bin/python

import sys
import os
import telnetlib
import datetime

def getneip():
    ip = []
    f = open('NE_IP', encoding = 'utf-8')
    for line in f.read().split():
        ip.append(line)
    f.close()
    return(ip)


def send_mail(self):

    print('Sending mail...')
    server=smtplib.SMTP('mail.skbroadband.com',25)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('snocjs','gaongkwkebqbdthl')
    sent_from= 'NOC점검봇'
    addrs =['pacemaker00@sk.com']
    subject = "[Daily report] Test"
    text ='Please check the attachment.'

    body = MIMEText(text)
    msg=MIMEMultipart()
    msg['From']= sent_from
    msg['Subject'] = subject
    msg.attach(body)

    with open(self.saveFile, "rb") as file:
        part = MIMEApplication(file.read(), Name=basename(self.saveFile))
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(self.saveFile)
        msg.attach(part)

    for to in addrs:
        msg['To'] = to
        server.sendmail(sent_from,to,msg.as_string())

    print('mail has sent')
    server.quit()

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

    def GetAlm(self) : #[모듈] 텔넷 후 Log Parsing
        print(self.NE_ID + ' (' + self.NE_IP + ')  에서 현재 알람을 추출중입니다...')
        location, severity, cause, description, datetimes = [], [], [], [], []
        self.tl1.write('RTRV-ALM-ALL:' + self.NE_ID  + ':ALL:CTAG:::,;')
        Logs = self.tl1.read_until('<')
        lines = Logs.split('   "')[1:]
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
        almParsed = {'location': location, 'severity': severity, 'cause': cause, 'description': description, 'datetimes': datetimes}
        print('완료!\n')
        return almParsed

    def GetCrs(self) : #[모듈] 텔넷 후 Log Parsing
        print(self.NE_ID+' ('+self.NE_IP + ') 에서 맵 정보를 추줄중입니다...')
        crs1, crs2 = [], []
        self.tl1.write('RTRV-CRS-VT2:' + self.NE_ID + ':ALL:CTAG:::,;')
        Logs = self.tl1.read_until('<')
        lines = Logs.split('   "')
        for line in lines:
            if line[0] == 'V':
                crsTmp = line.split(',')
                crs1.append(crsTmp[0])
                crs2.append(crsTmp[1].split(':')[0])
        crs = {'from':crs1, 'to':crs2}
        print('완료!\n')
        return crs

    def DelCrs(self, deadCkt):
        delDenied = []
        f = open('Delete result ' + self.NE_IP, 'wt')
        f1 = open('Delete denied ' + self.NE_IP, 'wt')
        for crs1, crs2 in zip(deadCkt['From'], deadCkt['To']):
            delCommand = "DLT-CRS-VT2::" + crs1 + "," + crs2 + ":CTAG:::,;"
            #self.tl1.write('delCommand')
            #result = self.tl1.expect(['COMPLD','DENY']
            #result = result[2][result[1].span()[0]:result[1].span()[1]]
            f.write('Command :'+delCommand+'\n')
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
                print('Command: '+line)
        return delDenied

    def ResCrs(self, resCkt):
        f = open('Restore result ' + self.NE_IP, 'wt')
        f1 = open('Restore denied ' + self.NE_IP, 'wt')
        for crs1, crs2 in zip(resCkt['From'], resCkt['To']):
            crsCommand = "ENT-CRS-VT2::" + crs1 + "," + crs2 + ":CTAG::2WAY:,,CKTID = 'Restored',,;"
            print(crsCommand)
            #self.tl1.write(crsCommand)
            #result = self.tl1.until('<')
            #result = self.tl1.expect(['COMPLD','DENY']
            #result = result[2][result[1].span()[0]:result[1].span()[1]]
            f.write('Command :'+crsCommand+'\n')
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
            if (crs_from in alm['location']) and (crs_to in alm['location']): #IF CROSS-CONNECT 'FROM,TO' ARE BOTH ALARMED
                k = alm['location'].index(crs_from)
                j = alm['location'].index(crs_to)
                dt1 = alm['datetimes'][k]
                dt2 = alm['datetimes'][j]
                td1 = self.dt-dt1
                td2 = self.dt-dt2
                if td1.days > 30 or td2.days > 30: #IF ALARMED ELASPED MORE THAN 30 DAYS
                    if (alm['cause'][k] == 'UNEQ') or (alm['cause'][j] == 'UNEQ') :
                        date_from = dt1.strftime('%Y-%m-%d')
                        date_to = dt2.strftime('%Y-%m-%d')
                        cktDead.write('CrsFrom: '+crs_from+'\n')
                        cktDead.write('Almfrom: ' +alm['location'][k]+ ' ('+alm['cause'][k]+", "+date_from+ ')'+'\n')
                        cktDead.write('CrsTo  : '+crs_to+'\n')
                        cktDead.write('AlmTo  : ' +alm['location'][j]+ ' ('+alm['cause'][j]+", "+date_to+ ')'+'\n\n')
                        deadFrom.append(crs_from)
                        deadTo.append(crs_to)
        cktDead.close()
        deadCkt = {'From':deadFrom,'To':deadTo}
        print('완료!!!\n미사용 내역은 "dead circuits '+IP+'.log"  파일에서 확인 가능합니다.\n')
        return deadCkt

if __name__ == "__main__":

    host = []
    NE_IP = getneip()
    f = open('readme','rt', encoding = 'utf-8')
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
            #print(deadCkt)
            #print(len(deadCkt['From']))
            #print(len(deadCkt['To']))
            node.LogOut()
            print(' == ============================================')
            print('회선 삭제를 시작하려면 commit을 입력 하십시오.')
            commit = 0
            while(commit != 'commit'):
                commit = input()
            if commit == 'commit':
                node.DelCrs(deadCkt)
    elif cmd == 'restore':
        loc = False
        while loc == False :
            node = ciena('12.4.44.127')
            print('일괄복구 할 맵 정보(Delete result)가 있는 파일명을 입력 해 주세요')
            print('EX) "Delete result 12.4.44.127"')
            cmd = input()
            loc = os.path.exists(cmd)
            if loc == True:
                crsFrom, crsTo = [], []
                f = open(cmd, 'rt')
                lines = f.readlines()
                print(lines)
                for line in lines :
                    print(line)
                    From = line.split(':')[3].split('.')[0]
                    To = line.split(':')[3].split('.')[0]
                    crsFrom.append(From)
                    crsTo.append(To)
                resCkt = {'From':crsFrom, 'To':crsTo}
                node.ResCrs(resCkt)
    else:
        print('명령을 잘못 입력했습니다. 프로그램을 종료합니다.')
        input()

