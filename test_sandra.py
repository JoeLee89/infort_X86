import os
from pywinauto.application import Application
import pywinauto
import time
from tools_manage import *
import pytest, allure
from common_func import *
from tools_manage import *
import datetime

#pywinauto.timings.Timings.slow()

needitem=['<<< Processor Arithmetic >>>',
          '<<< Processor Multi-Media >>>',
          '<<< Processor Cryptography >>>',
          '<<< Processor Financial Analysis >>>',
          '<<< Processor Scientific Analysis >>>',
          '<<< Processor Multi-Core Efficiency >>>',
          '<<< Processor Power Management Efficiency >>>',
          '<<< Video Shader Compute >>>',
          '<<< Media (Audio/Video) Transcode >>>',
          '<<< Video Memory Bandwidth >>>',
          '<<< Memory Bandwidth >>>',
          '<<< Cache & Memory Latency >>>',
          '<<< Cache Bandwidth >>>',
          '<<< Memory Transaction Throughput >>>']
folder='performance'

def writing():
    global sandrafile,content,repeat
    blank = 0
    performancefile = open(f'.\\{folder}\\sandra_performance_result.csv', 'a')

    try:
        os.mkdir(f'.\\{folder}')
    except:
        print('file exits, so skip to create performance folder.')

    while True:
        content=content.replace(':',',')
        performancefile.write(content)
        content = sandrafile.readline()
        if len(content) == 0:
            blank+=1
        if "< Benchmark Status >" in content or blank >4:
            performancefile.close()
            return

def mainloopforsandra():
    global content
    global sandrafile

    if os.path.exists('.\\performance\\sandra_benchmark_report.txt'):
        sandrafile = open('.\\performance\\sandra_benchmark_report.txt', encoding="utf-16")
        content = sandrafile.readline()
        while content:
            content = content.strip('\n')

            if content in needitem:
                writing()
            content = sandrafile.readline()
        sandrafile.close()
    else:
        print("Can't find the file sandra_benchmark_report.txt")


def processtokill():
    for proc in psutil.process_iter():
        # print(proc.name)
        if 'Sandra' in str(proc.name):
            proc.kill()

def sandralaunch(path):
    # in case if performance has been launched before, to rename the test report first.
    file=os.path.exists('%s\\performance\\sandra_benchmark_report.txt' % (os.getcwd()))
    if file:
        now=datetime.datetime.now()
        os.rename('.\\performance\\sandra_benchmark_report.txt',f'.\\performance\\sandra_benchmark_report_{now.time().strftime("%H%M%S")}.txt')

    app=Application(backend="win32").start(cmd_line=f'{path}\\sandra.exe')
    dlg_spec=app['LocalComputer - SiSoftware Sandra']
    dlg_spec.wait('exists',timeout=50)
    app['Tip of the Day'].wait('exists',timeout=30)
    app.window(best_match='Tip of the Day').close()
    #dlg_spec['&Tools'].click()
    app['LocalComputer - SiSoftware Sandra'].move_window(x=100, y=0, width=800, height=500)
    app['LocalComputer - SiSoftware Sandra'].type_keys('+t+t{ENTER}')
    app['LocalComputer - SiSoftware Sandra'].type_keys('+C+C{ENTER}')
    # pywinauto.keyboard.send_keys('{DOWN 4}{ENTER}')
    app["Create Report"].wait('visible',10)
    app["Create Report"].type_keys('^n')
    app["Create Report : Step 1 of 9"].wait('visible')
    app["Create Report : Step 1 of 9"].type_keys('{UP 4}{TAB} %s\\tool\\sandra\\test.sis' % (os.getcwd()))
    app["Create Report : Step 1 of 9"].type_keys('^n')

    app["Create Report : Step 2 of 9"].wait('exists',10)
    app["Create Report : Step 2 of 9"].type_keys('^n')

    app["Create Report : Step 3 of 9"].wait('exists',10)
    app["Create Report : Step 3 of 9"].type_keys('^n')

    app["Create Report : Step 4 of 9"].wait('exists',10)
    app["Create Report : Step 4 of 9"].type_keys('^n')

    app["Create Report : Step 5 of 9"].wait('exists',10)
    app["Create Report : Step 5 of 9"].type_keys('^n')

    app["Create Report : Step 6 of 9"].wait('exists',10)
    app["Create Report : Step 6 of 9"].type_keys('^n')

    app["Create Report : Step 7 of 9"].wait('exists',10)
    app["Create Report : Step 7 of 9"].type_keys('^n')

    app["Create Report : Step 8 of 9"].wait('exists',10)
    app["Create Report : Step 8 of 9"].type_keys('^n')

    app["Create Report : Step 9 of 9"].wait('exists',10)
    app["Create Report : Step 9 of 9"].type_keys('%s\\performance\\sandra_benchmark_report.txt' % (os.getcwd()))
    app["Create Report : Step 9 of 9"].type_keys('{ENTER}')

    # waittoclose=app["Create Report - SiSoftware Sandra"].wait('exists')
    #app["Create Report - SiSoftware Sandra"].wait_cpu_usage_lower(threshold=5)  # wait until CPU usage is lower than 5%
    #print(waittoclose)
    app_check=app["Create Report - .*"].wait('exists',10,5)
    timedelta=datetime.timedelta(hours=4)
    finish_time=datetime.datetime.now()+timedelta
    if app_check:
        while True:
            now = datetime.datetime.now()
            time.sleep(1)
            if now > finish_time:
                break

    # count=0
    # while True:
    #     try:
    #         time.sleep(1)
    #         app["Create Report - .*"].wait('visible',10,5)
    #         print('still alive')
    #         if count > 2000:
    #             app["Create Report - SiSoftware Sandra"].close()
    #             break
    #         else:
    #             count+=1
    #     except Exception as a:
    #         print('exit')
    #         print(a)
    #         break
    try:
        app.kill()
        processtokill()
    except Exception as a:
        print('Got exception while trying to close the sandra tool : ', a)
    #waittoclose=app["Create Report - SiSoftware Sandra"].wait_not('visible')


def test_sandra(request):
    data = ActManage(item_total_path(), request.node.name)
    data.bios_set([[None, None, 'default']]).act()

    re=InstallManage().set_name('sandra')
    if not re:
        pytest.skip('The Sandra installation process is failed, so skip the test.')

    target_folder=os.listdir('C:\\Program Files\\SiSoftware')[0]
    target_folder='C:\\Program Files\\SiSoftware\\' + target_folder
    if os.path.exists(target_folder):
        print('Start launching the sandra tool, and testing performance.')
        sandralaunch(target_folder)
        mainloopforsandra()
        print('Sandra performance is finished.')
    else:
        pytest.skip('Can not fine the related Sandra folder name, please check.')

    if os.path.exists(f'.\\{folder}\\sandra_performance_result.csv'):
        with allure.step('Performance Result'):
            allure.attach.file(f'.\\{folder}\\sandra_performance_result.csv')

