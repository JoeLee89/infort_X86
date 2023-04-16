import subprocess
import os,time,psutil,pytest,allure
from tools_manage import *
from common_func import *


def launchapp():


    server_ip='192.168.0.129'

    folder = 'performance'
    try:
        os.mkdir(f'.\\{folder}')
    except:
        print('file exits, so skip create performance folder.')

    for item in ['upload','download']:
        if item == 'upload':
            re = subprocess.Popen(
                f'.\\tool\\iperf\\iperf3.exe -c {server_ip} --logfile .\\performance\\iperf_{item}.txt',
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        else:
            re = subprocess.Popen(
                f'.\\tool\\iperf\\iperf3.exe -R -c {server_ip} --logfile .\\performance\\iperf_{item}.txt',
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        # re=subprocess.Popen(f'.\\tool\\iperf\\iperf3.exe -c {server_ip} ', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        re.wait()
        if re.returncode != 0:
            print('re=',re.stdout.read())
            raise RuntimeError('The test iperf process is been closed unexpectedly')





def test_pcmark(request):
    data = ActManage(item_total_path(), request.node.name)
    data.bios_set([[None, None, 'default']]).act()

    re = InstallManage().set_name('iperf')
    if not re:
        pytest.skip('The Iperf installation process is failed, so skip the test.')

    launchapp()
    if os.path.exists(f'.\\performance\\PCMark10_performance_result.csv'):
        with allure.step('Performance Result'):
            allure.attach.file(f'.\\performance\\iperf_download.csv')
            allure.attach.file(f'.\\performance\\iperf_upload.csv')

launchapp()