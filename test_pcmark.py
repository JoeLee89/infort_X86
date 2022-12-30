from pywinauto.application import Application
import pywinauto
import os,time,psutil,pytest,allure
import xml.etree.ElementTree as ET
from tools_manage import *
from common_func import *
performanceitem=['pcmark_score',
                 'lightweight_score',
                 'productivity_score',
                 'entertainment_score',
                 'creativity_score',
                 'computation_score',
                 'system_storage_score',
                 'raw_system_storage_score']


def filewriting(content):
    folder = 'performance'
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
    xml_file_path = f'{os.getcwd()}\\performance\\pcmark10.xml'
    if os.path.exists("C:\\PCMark 10"):
        app = Application(backend="win32").start(
            cmd_line=f'C:\\PCMark 10\\pcmark10cmd.exe --definition=pcm10_benchmark.pcmdef --export-xml={xml_file_path}',
            wait_for_idle=False)
        appp = Application(backend="win32").connect(path=r'C:\PCMark 10\pcmark10cmd.exe')
        i = 0
        while True:
            time.sleep(5)
            i+=1

            if not appp.is_process_running() and i< 540:
                break

            elif i == 540:
                processtokill()
                raise Warning('It looks like the APP meets some problems, please check APP if it still alive.')

        time.sleep(10)
        xmlcheck()
    else:
        print("Can't find the PCMARK10 folder. Check if app is installed well.")


def xmlcheck():
    # for i in performanceitem:
    #      #print('%s\\%s_performance.xml' % (os.getcwd(), i))
    if os.path.exists(f'.\\performance\\pcmark10.xml'):
        tree = ET.parse(f'.\\performance\\pcmark10.xml')
        root = tree.getroot()
        for child in root[0][0][5:-1]:
            filewriting(child.tag + ',' + child.text + '\n')
            print(child.tag + ',', child.text)
        for child in root[0][1][5:-1]:
            filewriting(child.tag + ',' + child.text + '\n')
            print(child.tag + ',', child.text)

         # filewriting('===========================================\n')


def test_pcmark(request):
    # data = ActManage(item_total_path(), request.node.name)
    # data.bios_set([[None, None, 'default']]).act()

    # re = InstallManage().set_name('pcmark')
    # if not re:
    #     pytest.skip('The installation process is failed, so skip the test.')

    launchapp()
    if os.path.exists(f'.\\performance\\PCMark10_performance_result.cs'):
        with allure.step('Performance Result'):
            allure.attach.file(f'.\\performance\\PCMark10_performance_result.csv')