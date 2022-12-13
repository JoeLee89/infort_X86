import os,time,psutil,pytest,allure
import xml.etree.ElementTree as ET
from common_func import *
from tools_manage import *

performanceitem=['firestrike_extreme','firestrike_ultra','timespy','timespy_extreme']
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
    if os.path.exists('C:\\3DMark'):
        for i in performanceitem:
            app = Application(backend="win32").start(
                cmd_line='C:\\3DMark\\3DMarkCmd.exe --definition=%s.3dmdef --export=%s\\%s_performance.xml' % (i, os.getcwd(),i), wait_for_idle=False)
            appp = Application(backend="win32").connect(path=r'C:\3DMark\3DMarkCmd.exe')
            m=0
            while True:
                m += 1
                time.sleep(10)
                #超過1800秒(30分鐘)3dmarkcmd還在執行，那就判斷應該是程式當機沒有在執行了，就把程式關閉反回fail
                if not appp.is_process_running() and m < 180:
                     break
                elif appp.is_process_running()and m == 180:
                    # print('not')
                    processtokill()
                    raise Warning('It looks like the APP meets some problems, please check APP if it still alive.')

            time.sleep(10)
            if os.path.exists('%s\\%s_performance.xml' % (os.getcwd(),i)):
                xmlcheck()
            else:
                # print("It looks like the APP meets some problems, please check APP if it still alive.")
                raise Warning('It looks like the APP meets some problems, please check APP if it still alive.')

    else:
        # print("Can't find the 3Dmark folder. Check if 3Dmark app is installed well.")
        raise Warning('Can not find the 3DMark folder. Check if 3DMark app is installed well.')


def xmlcheck():
    xml=None
    list = [
        'PerformanceGraphicsScore',
        'PerformanceCPUScore',
        'Performance3DMarkScore',
        'PerformanceGraphicsTest1',
        'PerformanceGraphicsTest2',
        'PerformanceCpuSection2']

    for i in performanceitem:

        if i=='firestrike_extreme':
            xml='FireStrikeExtreme'
        elif i=='firestrike_ultra':
            xml = 'FireStrikeUltra'
        elif i=='timespy':
            xml = 'TimeSpy'
        elif i=='timespy_extreme':
            xml = 'TimeSpyExtreme'
        #print('%s\\%s_performance.xml' % (os.getcwd(), i))
        gol=[xml+i for i in list]


        if os.path.exists('%s\\%s_performance.xml' %(os.getcwd(),i)):
            tree = ET.parse('%s\\%s_performance.xml' %(os.getcwd(),i))
            root = tree.getroot()
            for ls in gol:
                for child in root.iter(ls):
                    filewriting(child.tag + ',' + child.text+ '\n')
                    print(child.tag + ',', child.text)

def test_3dmark(request):
    data = ActManage(item_total_path(), request.node.name)
    data.bios_set([[None, None, 'default']]).act()
    re = InstallManage().set_name('3dmark')
    if not re:
        pytest.skip('The installation process is failed, so skip the test.')

    launch3dmark()

    if os.path.exists(f'.\\{folder}\\3DMark_performance_result.csv'):
        with allure.step('Performance Result'):
            allure.attach.file(f'.\\{folder}\\3DMark_performance_result.csv')