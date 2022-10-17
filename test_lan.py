import socket,subprocess,datetime,time,pickle,re,pytest,os,requests,sys
import bios_update
from common_func import cmd,process_finish,reboot, PreSetting

@pytest.fixture
def get_mac():
    proc = subprocess.Popen(['ipconfig', '-all'], stdout=subprocess.PIPE)
    title = 0
    search_title = re.compile(r'Ethernet adapter Ethernet.*:')
    search_address = re.compile(r'Physical Address.*: (.*)')
    mac_list=[]
    for line in iter(proc.stdout.readline,''):
        # print(line.strip())
        line=line.decode('utf-8')
        # print(line)
        search_title_Re = search_title.search(line)
        search_addresse_Re = search_address.search(line)

        if not title and search_title_Re:
            title = 1
        if title and search_addresse_Re:
            # print(search_addresse_Re.group(1).replace('-', ''))
            mac_list.append(search_addresse_Re.group(1).replace('-', '').strip())
            title = 0

        if not line:
            break
    return mac_list if mac_list else []


@pytest.fixture
def mac_initial():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('192.168.0.10', 6666))
    yield client
    client.close()


# def test_wol(request, get_mac,mac_initial,item):
def test_wol(request, get_mac,item):
    # client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client.connect(('192.168.0.10',6666))
    if item in ['all',request.node.name]:
        pass
    else:
        pytest.skip('The function is not selected.')

    #update bios setting
    #no need to load default, because other itmes will overwrite the bios setting to set other items as default setting
    act=bios_update.Action()
    act.set_item('i219 Wake on LAN', 'Disabled', 'item')
    act.action()

    #reboot DUT with setup pytest command in startup folder
    _reboot=reboot(request.node.name,item)
    _process=process_finish(request.node.name)

    if not _reboot and not _process:
        pytest.skip('The function is finished, so skip')

    #
    # client=mac_initial
    # mac_list=get_mac
    # data=['wol']

    # data=data+mac_list
    #
    # #send data to console in package list
    # data=pickle.dumps(data)
    # # data=data.encode('utf-8')
    # client.sendall(data)
    #
    # while True:
    #     recv=client.recv(1024)
    #     if recv=='ok':
    #         print(f'from server receive:{recv}')
    #         break
    # now = datetime.datetime.now()
    # cmd('.\\tool\\sleeper\\sleeper.exe -S0010 -R 60 -N 1 -F -E')
    #
    # after=datetime.datetime.now()
    # re=(after-now).seconds
    # assert re < 300


def test_wolxx(request, get_mac, item):
# def test_wolxx(request, get_mac, mac_initial, item):
    # client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client.connect(('192.168.0.10',6666))
    if item in ['all', request.node.name]:
        pass
    else:
        pytest.skip('The function is not selected.')
    # update bios setting
    act = bios_update.Action()
    act.set_item('i219 Wake on LAN', 'Disabled', 'item')
    act.action()

    # reboot DUT with setup pytest command in startup folder
    _reboot = reboot(request.node.name, item)
    _process = process_finish(request.node.name)

    if not _reboot and not _process:
        pytest.skip('The function is finished, so skip')
#
# def test_test(item):
#     if item in ['all','test_test']:
#         print('got name=', item)
#     else:
#         pytest.skip('The function is not selected.')
#     #found what kind of the name is the function used?
#     # print('aaa=',request.node.name)
#     # bios_update(request.node.name)
#
#     # print('finish')
# def test_test11(item):
#     if item in ['all','test_test11']:
#         print('got name=', item)
#     else:
#         pytest.skip('The function is not selected.')

def test_surf_web(request, item):
    # def test_wolxx(request, get_mac, mac_initial, item):

    if item in ['all', request.node.name]:
        pass
    else:
        pytest.skip('The function is not selected.')

    # make bios load default
    act=bios_update.Action()
    act.set_item(None, None,'default')
    act.action()

    # reboot DUT with setup pytest command in startup folder
    _reboot = reboot(request.node.name, item)
    _process = process_finish(request.node.name)

    if not _reboot and not _process:
        pytest.skip('The function is finished, so skip')


    re=requests.get("https://www.google.com.tw/")
    assert re.status_code == 200

def test_download_file(request, item):
    presetting = PreSetting()
    presetting.bios_set([None, None, 'default'])
    presetting.func_set(request.node.name, item)
    re=presetting.act()
    if not re[0]:
        pytest.skip(re[1])

    link='http://http.speed.hinet.net/test_010m.zip'
    url=requests.get(link)
    content=len(url.content)
    print(content)
    print(re)


    assert content > 0






