import socket,subprocess,datetime,time,pickle,re,pytest,os
import bios_update

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


def cmd(command):
    subp=subprocess.Popen(command,shell=True)
    subp.wait(300)
    if subp.poll() != 0:
        print('Failed to launch the tool with the command.')


@pytest.fixture
def mac_initial():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('192.168.0.10', 6666))
    yield client
    client.close()


def reboot(name,item):
    location = os.path.expanduser('~')
    script_location=f'{location}\\Desktop\\other_test\\auto\\'
    auto_location=f'{location}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\'

    if not os.path.exists(f'{script_location}{name}_rebooted.txt'):
        data=f'{script_location}venv\\Scripts\\pytest -v -s {script_location}lan.py --item={item}'
        print('name=',name)
        with open(f'{auto_location}run.bat','w') as f:
            f.write(data)
        with open(f'{script_location}{name}_rebooted.txt','w') as a:
            a.write('')
        cmd('shutdown /r')
        print('exist')
        time.sleep(60)

    else:
        return False
        # os.unlink(f'{script_location}{name}_rebooted.txt')
        # os.unlink(f'{auto_location}run.bat')

def process_finish(name):
    location = os.path.expanduser('~')
    script_location = f'{location}\\Desktop\\other_test\\auto\\'
    auto_location = f'{location}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\'
    if not os.path.exists(f'{script_location}{name}_finish.txt'):
        with open(f'{script_location}{name}_finish.txt','w') as a:
            a.write('')
        return True
    else:
        try:
            os.unlink(f'{auto_location}run.bat')
        except:
            pass
        return False


# def test_wol(request, get_mac,mac_initial,item):
def test_wol(request, get_mac,item):
    # client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client.connect(('192.168.0.10',6666))
    if item in ['all',request.node.name]:
        pass
    else:
        pytest.skip('The function is not selected.')
    #update bios setting
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