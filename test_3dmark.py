import os,time,psutil,pytest,allure
import xml.etree.ElementTree as ET
from common_func import *
from tools_manage import *


folder='performance'

def filewriting(content):

    try:
        os.mkdir(f'.\\{folder}')
    except:
        print('file exits, so skip create performance folder.')

    testresult = open(f'.\\{folder}\\3DMark_performance_result.csv', 'a')
    testresult.write(content)
    testresult.close()


def processtokill():
    for proc in psutil.process_iter():
        print(proc.name)
        if '3DMark' in str(proc.name):
            proc.kill()


def launch3dmark():
    performanceitem = ['firestrike_extreme', 'firestrike_ultra', 'timespy', 'timespy_extreme']

    if os.path.exists('C:\\3DMark'):

        for i in performanceitem:
            xml_file_path = f'{os.getcwd()}\\{folder}\\{i}_performance.xml'
            app = Application(backend="win32").start(
                cmd_line=f'C:\\3DMark\\3DMarkCmd.exe --definition={i}.3dmdef --export={xml_file_path}', wait_for_idle=False)
            appp = Application(backend="win32").connect(path=r'C:\3DMark\3DMarkCmd.exe')
            m=0
            while True:
                m += 1
                time.sleep(10)
                #超過1800秒(30分鐘)3dmarkcmd還在執行，那就判斷應該是程式當機沒有在執行了，就把程式關閉反回fail
                if not appp.is_process_running() and m < 180:
                     break
                elif m == 180:
                    # print('not')
                    processtokill()
                    raise Warning('It looks like the APP meets some problems, please check APP if it still alive.')

            time.sleep(10)

        xmlcheck(performanceitem)
    else:
        # print("Can't find the 3Dmark folder. Check if 3Dmark app is installed well.")
        raise Warning('Can not find the 3DMark folder. Check if 3DMark app is installed well.')


def xmlcheck(performanceitem):

    # xml=None
    # list = [
    #     'PerformanceGraphicsScore',
    #     'PerformanceCPUScore',
    #     'Performance3DMarkScore',
    #     'PerformanceGraphicsTest1',
    #     'PerformanceGraphicsTest2',
    #     'PerformanceCpuSection2']
    #
    for i in performanceitem:

        if os.path.exists('%s\\%s_performance.xml' %(folder,i)):
            tree = ET.parse('%s\\%s_performance.xml' %(folder,i))
            root = tree.getroot()

            for child in root[0][1][4:-1]:
                filewriting(child.tag + ',' + child.text+ '\n')
                print(child.tag + ',', child.text)
        filewriting('===========================================\n')

def test_3dmark(request):
    data = ActManage(item_total_path(), request.node.name)
    data.bios_set([[None, None, 'default']]).act()
    re = InstallManage().set_name('3dmark')
    if not re:
        pytest.skip('The 3DMark installation process is failed, so skip the test.')

    launch3dmark()

    if os.path.exists(f'.\\{folder}\\3DMark_performance_result.csv'):
        with allure.step('Performance Result'):
            allure.attach.file(f'.\\{folder}\\3DMark_performance_result.csv')

