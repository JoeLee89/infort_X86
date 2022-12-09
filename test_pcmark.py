from tools_manage import InstallManage as im
from pywinauto.application import Application
import pywinauto
import os,time,psutil
import xml.etree.ElementTree as ET
performanceitem=['pcmark_score','lightweight_score','productivity_score','entertainment_score','creativity_score','computation_score','system_storage_score','raw_system_storage_score']

def filewriting(content):
    testresult = open('PCMark10_performance_result.csv', 'a')
    testresult.write(content)
    testresult.close()

def processtokill():
    for proc in psutil.process_iter():
        print(proc.name)
        if 'PCMark' in str(proc.name):
            proc.kill()

def launchapp():

    if os.path.exists("C:\\Program Files\\UL\\PCMark 10"):
        app = Application(backend="win32").start(
            cmd_line=r'C:\Program Files\UL\PCMark 10\pcmark10cmd.exe --systeminfo=on --all=on --secondarystorage=off --export %s\\pcmark10.xml' % os.getcwd(),
            wait_for_idle=False)
        appp = Application(backend="win32").connect(path=r'C:\Program Files\UL\PCMark 10\pcmark10cmd.exe')
        i = 0
        while True:
            time.sleep(5)
            i+=1

            if not appp.is_process_running() and i< 540:
                break

            elif appp.is_process_running() and i==540:
                processtokill()
                raise Warning('It looks like the APP meets some problems, please check APP if it still alive.')

        time.sleep(10)
        if os.path.exists('%s\\pcmark10.xml' % os.getcwd()):
            xmlcheck()
        else:
            raise Warning('It looks like the APP meets some problems, please check APP if it still alive.')

    else:
        print("Can't find the PCMARK10 folder. Check if 3Dmark app is installed well.")


def xmlcheck():
    for i in performanceitem:
         #print('%s\\%s_performance.xml' % (os.getcwd(), i))
        if os.path.exists('%s\\pcmark10.xml' % os.getcwd()):
            tree = ET.parse('%s\\pcmark10.xml' % os.getcwd())
            root = tree.getroot()
            for child in root.iter(i):
                filewriting(child.tag + ',' + child.text + '\n')
                print(child.tag + ',', child.text)


def test_pcmark():
    re = im.set_name('3dmark')
    if re:
        launchapp()

    else:
        raise Warning('Tool installation is failed.')