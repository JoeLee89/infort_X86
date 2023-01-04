import pywinauto,pytest,subprocess, time, os, allure
import hwinfo_collect
from pywinauto import Application
from pywinauto import Desktop
from common_func import *
from tools_manage import InstallManage


@pytest.fixture(scope='session')
def hw64info_launch(burnin_launch):
    re = InstallManage().set_name('hwinfo64')
    if not re:
        pytest.skip('The installation process is failed, so skip the test.')

    if not os.path.exists('.\\temp\\hwinfo64log.txt'):
        subprocess.Popen('.\\tool\\hwinfo64\\HWiNFO64.exe')
        app=Desktop()['HWiNFO64']
        app.wait('visible')
        app.set_focus()
        app['Start'].click()
        try:
            time.sleep(5)
            appp=Desktop()['HWiNFO64 Update']
            appp.wait('visible',timeout=5)
            appp['Close'].click()
        except (pywinauto.timings.TimeoutError, pywinauto.findbestmatch.MatchError):
            pass
        main=Application().connect(path='.\\tool\\hwinfo64\\HWiNFO64.exe')
        temp=main.window(title_re='HWiNFO64.*@.*')
        temp.close()
        main.window(title_re='HWiNFO64.*').menu_select(u'Report -> Create')
        main.window(title='Create Logfile').wait('visible',timeout=5)
        main.window(title='Create Logfile')['RadioButton'].click()
        main.window(title='Create Logfile')['CheckBox'].click()
        main.window(title='Create Logfile')['Edit'].set_edit_text(os.getcwd()+'\\temp\\hwinfo64log.txt')
        main.window(title='Create Logfile')['Next'].click()
        main.window(title='Create Logfile')['Finish'].click()
        main.window(title_re='HWiNFO64.*').close()


@pytest.fixture(scope='session')
def burnin_launch():
    re=InstallManage().set_name('burnintest')
    if not re:
        pytest.skip('The installation process is failed, so skip the test.')

    if not os.path.exists('.\\temp\\hwinfo64log.txt'):
        burnin_config='''
        SETTEST 3D
        UNSETTEST 2D
        UNSETTEST BATTERY
        UNSETTEST CD
        UNSETTEST CPU
        UNSETTEST DISK
        UNSETTEST GPGPU
        UNSETTEST MICROPHONE
        UNSETTEST MEMORY
        UNSETTEST PARALLEL
        UNSETTEST PCIE
        UNSETTEST SERIAL
        UNSETTEST SOUND
        UNSETTEST USB
        UNSETTEST VIDEO
        SETDURATION 0.5
        SETDUTYCYCLE 3D 100
        RUN CONFIG
        EXIT
        '''
        with open('.\\temp\\test.bits','w') as file:
            file.write(burnin_config)
        subprocess.Popen(f'C:\\Program Files\\BurnInTest\\bit.exe -s {os.getcwd()}\\temp\\test.bits')
        time.sleep(10)


def test_video_gen3(hw64info_launch,request):
    # set up bios setting to default
    # save log file to temp, so it could remember what test item should continue after reboot.
    # data = ActManage(item_total_path(), request.node.name)
    # data.bios_set([[None, None, 'default']]).act()

    start='Video Adapter -------------------------------------------------------------'
    end='Monitor -------------------------------------------------------------------'
    result=None
    mang=hwinfo_collect.Manage()
    video=hwinfo_collect.Video()
    mang.set_func(video)
    mang.set_requirment(start,end)
    speed, all = mang.act()
    target='PCIe v3.0 x16 (8.0 GT/s) @ x16 (8.0 GT/s)'
    with allure.step('Graphic card related info'):
        # write graphic card related data in file
        if not os.path.exists('.\\temp\\video.txt'):
            with open('.\\temp\\video.txt','a') as file:
                for i in all:
                    file.write(i+'\n')
        allure.attach.file('.\\temp\\video.txt')
    for i in speed:
        if 'x16' in i:
            result=i
    assert target in result

def test_video_gen4(hw64info_launch,request):
    # set up bios setting to default
    # save log file to temp, so it could remember what test item should continue after reboot.
    data = ActManage(item_total_path(), request.node.name)
    data.bios_set([[None, None, 'default']]).act()

    start='Video Adapter -------------------------------------------------------------'
    end='Monitor -------------------------------------------------------------------'
    result=None
    mang=hwinfo_collect.Manage()
    video=hwinfo_collect.Video()
    mang.set_func(video)
    mang.set_requirment(start,end)
    speed, all = mang.act()
    target='PCIe v4.0 x16 (16.0 GT/s) @ x16 (16.0 GT/s)'
    with allure.step('Graphic card related info'):
        # write graphic card related data in file
        if not os.path.exists('.\\temp\\video.txt'):
            with open('.\\temp\\video.txt','a') as file:
                for i in all:
                    file.write(i+'\n')
        allure.attach.file('.\\temp\\video.txt')
    for i in speed:
        if 'x16' in i:
            result=i
    assert target in result


def test_storage(hw64info_launch,request):
    # set up bios setting to default
    # save log file to temp, so it could remember what test item should continue after reboot.
    data = ActManage(item_total_path(), request.node.name)
    data.bios_set([[None, None, 'default']]).act()

    start='Drives --------------------------------------------------------------------'
    end='Audio ---------------------------------------------------------------------'
    mang=hwinfo_collect.Manage()
    result=hwinfo_collect.Others()
    mang.set_func(result)
    mang.set_requirment(start,end)
    speed, all = mang.act()
    with allure.step('Storage related info'):
        # write graphic card related data in file
        if not os.path.exists('.\\temp\\storage.txt'):
            with open('.\\temp\\storage.txt','a') as file:
                for i in all:
                    file.write(i+'\n')
        allure.attach.file('.\\temp\\storage.txt')

def test_memory(hw64info_launch,request):
    # set up bios setting to default
    # save log file to temp, so it could remember what test item should continue after reboot.
    data = ActManage(item_total_path(), request.node.name)
    data.bios_set([[None, None, 'default']]).act()

    start='Memory --------------------------------------------------------------------'
    end='Bus -----------------------------------------------------------------------'
    mang=hwinfo_collect.Manage()
    result=hwinfo_collect.Others()
    mang.set_func(result)
    mang.set_requirment(start,end)
    speed, all = mang.act()
    with allure.step('Memory related info'):
        # write graphic card related data in file
        if not os.path.exists('.\\temp\\memory.txt'):
            with open('.\\temp\\memory.txt','a') as file:
                for i in all:
                    file.write(i+'\n')
        allure.attach.file('.\\temp\\memory.txt')

# pytest -vs test_info.py::test_nvme --alluredir=report
