from pywinauto.application import Application
import pywinauto
import os,time,psutil,pytest,allure
import xml.etree.ElementTree as ET
from tools_manage import *
from common_func import *
performanceitem=['pcmark_score','lightweight_score','productivity_score','entertainment_score','creativity_score','computation_score','system_storage_score','raw_system_storage_score']
folder='performance'

def filewriting(content):

    try:
        os.mkdir(f'.\\{folder}')
    except:
        print('file exits, so skip create performance folder.')
    testresult = open(f'.\\{folder}\\PCMark10_performance_result.csv', 'a')
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


def test_pcmark(request):
    data = ActManage(item_total_path(), request.node.name)
    data.bios_set([[None, None, 'default']]).act()

    re = InstallManage().set_name('crystaldiskmark')
    if not re:
        pytest.skip('The installation process is failed, so skip the test.')

    launchapp()
    if os.path.exists(f'.\\{folder}\\PCMark10_performance_result.cs'):
        with allure.step('Performance Result'):
            allure.attach.file(f'.\\{folder}\\PCMark10_performance_result.csv')