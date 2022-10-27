import socket,subprocess,datetime,time,pickle,re,pytest,os,requests,sys
import bios_update
from common_func import *

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

def device_manage_action(name,require):
    from pywinauto import Application, Desktop
    name = name
    require= require
    Application().start(r'mmc devmgmt.msc')
    app = Application(backend='uia').connect(path='mmc.exe')
    main = app.window(title='Device Manager')
    lan = main.child_window(title='Network adapters', control_type='TreeItem')
    lan.expand()
    lan_target = lan.child_window(title=name, control_type='TreeItem', found_index=0)
    lan_target.click_input(button='left', double=True)
    win = app[f'{name} Properties']
    win['Advanced'].select()
    win['Vertical'].wheel_mouse_input(wheel_dist=-20)
    win['Wake on Magic Packet'].select()
    while True:
        status = win['ComboBox'].selected_text()
        if require == 'Enabled':
            if status == require:
                break
            else:
                win['ComboBox'].type_keys('{DOWN}')
                if win['ComboBox'].selected_text() != require:
                    win['ComboBox'].type_keys('{UP}')
        if require == 'Disabled':
            if status == require:
                break
            else:
                win['ComboBox'].type_keys('{UP}')
                if win['ComboBox'].selected_text() != require:
                    win['ComboBox'].type_keys('{DOWN}')

    win['OK'].click()
    main.close()

# def test_wol(request, get_mac,mac_initial,item):
def test_wol_bios_enable(request, get_mac,item):
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


    client=mac_initial
    mac_list=get_mac
    data=['wol']

    data=data+mac_list

    #send data to console in package list
    data=pickle.dumps(data)
    # data=data.encode('utf-8')
    client.sendall(data)

    while True:
        recv=client.recv(1024)
        if recv=='ok':
            print(f'from server receive:{recv}')
            break
    now = datetime.datetime.now()
    cmd('.\\tool\\sleeper\\sleeper.exe -S0010 -R 60 -N 1 -F -E')

    after=datetime.datetime.now()
    re=(after-now).seconds
    assert re < 300


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
    assert content == 10485760

def test_s3(request, item):
    data = ActManage()
    data.set_name_item(request.node.name, item)
    data.bios_set([])
    data_re = data.act()
    if not data_re[0]:
        pytest.skip(data_re[1])
    command='wmic nic where netEnabled=true get name, speed'
    re=subprocess.Popen(command,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    item=['intel','realtek']

    first=[]
    second=[]
    while True:
        output=re.stdout.readline().decode().strip().lower()
        if output == "":
            break
        for i in item:
            if i in output:
                first.append(output)

    cmd('.\\tool\\sleeper\\sleeper.exe -S0010 -R 30 -N 1 -E')
    #wait for lan device recovery to be detected.
    time.sleep(20)

    re = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        output=re.stdout.readline().decode().strip().lower()
        if output == "":
            break
        for m in first:
            if m in output:
                second.append(output)

    assert first == second

def test_s4(request, item):
    data = ActManage()
    data.set_name_item(request.node.name, item)
    data.bios_set([])
    data_re = data.act()
    if not data_re[0]:
        pytest.skip(data_re[1])
    command='wmic nic where netEnabled=true get name, speed'
    re=subprocess.Popen(command,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    item=['intel','realtek']

    first=[]
    second=[]
    while True:
        output=re.stdout.readline().decode().strip().lower()
        if output == "":
            break
        for i in item:
            if i in output:
                first.append(output)

    cmd('.\\tool\\sleeper\\sleeper.exe -S0001 -R 60 -N 1 -E')

    #wait for lan device recovery to be detected.
    time.sleep(20)

    re = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        output=re.stdout.readline().decode().strip().lower()
        if output == "":
            break
        for m in first:
            if m in output:
                second.append(output)

    assert first == second


def test_lan1_disable(request, item):
    item = ['intel', 'realtek']
    command = 'wmic nic where netEnabled=true get name'
    before = []
    after = []

    # write data info to file
    if not os.path.exists('.\\temp\\before.txt'):
        re = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        while True:
            output = re.stdout.readline().decode().strip().lower()
            if output == "":
                break
            for i in item:
                if i in output:
                    with open('.\\temp\\before.txt', 'a') as a:
                        a.write(output + '\n')

    # start changing bios setting
    data = ActManage()
    data.set_name_item(request.node.name, item)
    if 'intel' in before:
        data.bios_set(['PCH LAN i219-V Controller', 'Disabled', 'item'])
    else:
        data.bios_set(['LAN1 Enable', 'Disabled', 'item'])
    data_re = data.act()
    if not data_re[0]:
        pytest.skip(data_re[1])

    # read all lan info, before bios item is changed.
    with open('.\\temp\\before.txt', 'r') as a:
        before = a.read().strip()
        before = before.split('\n')
        print(before)

    # read all lan info, after bios item is changed.
    re = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        output = re.stdout.readline().decode().strip().lower()
        if output == "":
            break
        for i in item:
            if i in output:
                after.append(output)
    os.unlink('.\\temp\\before.txt')
    assert before[0] != after[0]

def test_lan2_disable(request, item):
    item = ['intel', 'realtek']
    command = 'wmic nic where netEnabled=true get name'
    before=[]
    after=[]

    #write data info to file
    if not os.path.exists('.\\temp\\before.txt'):
        re=subprocess.Popen(command,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        while True:
            output=re.stdout.readline().decode().strip().lower()
            if output == "":
                break
            for i in item:
                if i in output:
                    with open('.\\temp\\before.txt', 'a') as a:
                        a.write(output+'\n')

    #start changing bios setting
    data = ActManage()
    data.set_name_item(request.node.name, item)
    if 'intel' in before:
        data.bios_set(['PCH LAN i211 Controller','Disabled','item'])
    else:
        data.bios_set(['LAN2 Enable', 'Disabled', 'item'])
    data_re = data.act()
    if not data_re[0]:
        pytest.skip(data_re[1])

    #read all lan info, before bios item is changed.
    with open('.\\temp\\before.txt','r') as a:
        before=a.read().strip()
        before=before.split('\n')
        print(before)

    #read all lan info, after bios item is changed.
    re = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        output = re.stdout.readline().decode().strip().lower()
        if output == "":
            break
        for i in item:
            if i in output:
                after.append(output)
    os.unlink('.\\temp\\before.txt')
    assert before[1] != after[0]












