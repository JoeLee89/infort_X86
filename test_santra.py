import os
from pywinauto.application import Application
import pywinauto
import time
import pytest


#pywinauto.timings.Timings.slow()

repeat=False
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


def writing():
    performancefile=open('sandra_performance_result.csv','a')
    while True:
        global content
        global repeat
        if repeat==False:
            repeat=True
            print(repeat)
            performancefile.write('''\n
===================================
=====SANTRA PERFORMANCE RESULT=====
===================================\n''')

        content=content.replace(':',',')
        performancefile.write(content)
        print(content)
        content = sandrafile.readline()
        if "< Benchmark Status >" in content:
            performancefile.close()
            return

def mainloopforsandra():
    global content
    global sandrafile

    if os.path.exists('sandra_benchmark_report.txt'):
        #print('good')
        sandrafile = open('sandra_benchmark_report.txt', encoding="utf-16")
        content = sandrafile.readline()
        while content:
            content = content.strip('\n')
            # print(content)
            # input()

            if content in needitem:
                writing()
            content = sandrafile.readline()
        sandrafile.close()
    else:
        print("Can't find the file sandra_benchmark_report.txt")




def sandralaunch():
    app=Application(backend="win32").start(cmd_line='C:\Program Files\SiSoftware\SiSoftware Sandra Tech Support (Engineer) Titanium.RTMb\sandra.exe')
    dlg_spec=app['LocalComputer - SiSoftware Sandra']
    dlg_spec.wait('exists',timeout=50)
    app['Tip of the Day'].wait('exists',timeout=30)
    app.window(best_match='Tip of the Day').close()
    #dlg_spec['&Tools'].click()
    app['LocalComputer - SiSoftware Sandra'].move_window(x=0,y=0)
    pywinauto.mouse.click('left',coords=(190, 50))
    pywinauto.keyboard.send_keys('{DOWN 4}{ENTER}')
    app["Create Report"].wait('visible')
    app["Create Report"].type_keys('^n')
    app["Create Report : Step 1 of 9"].wait('visible')
    app["Create Report : Step 1 of 9"].type_keys('{UP 4}{TAB} %s \\test.sis' % (os.getcwd()))
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
    app["Create Report : Step 9 of 9"].type_keys('%s \\sandra_benchmark_report.txt' % (os.getcwd()))
    app["Create Report : Step 9 of 9"].type_keys('{ENTER}')


    waittoclose=app["Create Report - SiSoftware Sandra"].wait('exists')
    #app["Create Report - SiSoftware Sandra"].wait_cpu_usage_lower(threshold=5)  # wait until CPU usage is lower than 5%
    #print(waittoclose)


    while 'Create Report' in str(waittoclose):
        waittoclose=app["Create Report - SiSoftware Sandra"].wait('exists')
        #print(waittoclose)
        time.sleep(1)
    app.window(best_match='LocalComputer - SiSoftware Sandra').close()
    #waittoclose=app["Create Report - SiSoftware Sandra"].wait_not('visible')




def test_sandra():
    if os.path.exists("C:\Program Files\SiSoftware\SiSoftware Sandra Tech Support (Engineer) Titanium.RTMb"):
        sandralaunch()
        mainloopforsandra()
        print('Santra performance is finished.')
    else:
        raise Warning('Can not fine the related Sandra folder name, please check.')

