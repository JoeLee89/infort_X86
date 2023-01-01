import socket,subprocess,datetime,time,pickle,re,pytest,os,requests,sys,re
import allure
import bios_update
from common_func import *
intel_lan_controller_type=[
    'PCH LAN i219-V Controller',
    'PCH LAN i211 Controller']

realtek_lan_controller_type=[
    'LAN1 Enable',
    'LAN2 Enable']
intel_wakeonlan_type=[
    'i219 Wake on LAN',
    'i211-AT Wake on LAN']

realtek_wakeonelan_type=[
    'LAN1 Enable',
    'LAN2 Enable']

def get_lan_name():
    proc = subprocess.Popen(['ipconfig', '-all'], stdout=subprocess.PIPE)
    title = 0
    search_title = re.compile(r'Ethernet adapter Ethernet.*:')
    search_lan_name = re.compile(r'Description.*: (.*)')
    lan_list=[]
    for line in iter(proc.stdout.readline,''):
        # print(line.strip())
        line=line.decode('utf-8')
        # print(line)
        search_title_Re = search_title.search(line)
        search_lan_nam_Re = search_lan_name.search(line)

        if not title and search_title_Re:
            title = 1
        if title and search_lan_nam_Re:
            # print(search_addresse_Re.group(1).replace('-', ''))
            lan_list.append(search_lan_nam_Re.group(1).strip())
            title = 0

        if not line:
            break
    return lan_list if lan_list else []

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

@pytest.fixture()
def lan_device_number_get():
    sub = subprocess.Popen('netsh interface show interface', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    i = 0
    re = []
    while True:
        data = sub.stdout.readline().decode().strip().split(maxsplit=3)
        for content in data:
            if content.startswith('Ethernet'):
                re.append(content)
        if len(data) == 0:
            i += 1
        if i == 2:
            break
    return re

# get each ethernet lan device name for future usage
def lan_device_number_get_other():
    sub = subprocess.Popen('netsh interface show interface', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    i = 0
    re = []
    while True:
        data = sub.stdout.readline().decode().strip().split(maxsplit=3)
        for content in data:
            if content.startswith('Ethernet'):
                re.append(content)
        if len(data) == 0:
            i += 1
        if i == 2:
            break
    return re


# to set pointed dut ip as static ip, and to make a connecting with server
def lan_link_initial(lan_number):
    dut_ip='192.168.10.18'
    server_ip = '192.168.10.19'
    num=lan_device_number_get_other()
    command=f'netsh interface ip set address "{num[lan_number]}" static {dut_ip}'
    # cmd(f'netsh interface ip set address "{lan_device_number_get[lan_number]}" static {dut_ip}')
    subprocess.Popen(command, shell=True)
    time.sleep(40)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, 8000))
    return client


# control wol disable/enable action
def device_wol_manage_action(name,require):
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


# @pytest.mark.skip('aaa')
# def test_lan2_wol_bios_enable_os_enable_s3(request, get_mac,lan_device_number_get):
#     # def test_lan2_wol_bios_enable_os_enable(request, get_mac,item,lan_device_number_get):
#     #confirm which lan device should be tested, starting from 0
#     lan_number=1
#     os_wol_status = 'Enabled'
#     bios_status='Enabled'
#
#     command = 'wmic nic where netEnabled=true get name'
#
#     # get all lan devices info
#     sub = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     result=sub.stdout.read()
#     result=[i for i in result.decode().lower().split() if 'intel' in i][0]
#
#     # start changing bios setting
#     data = ActManage(item_total_path(), request.note.name)
#
#     #disable lan2 chip
#     if 'intel' in result:
#         data.bios_set([[intel_wakeonlan_type[lan_number], bios_status, 'item']]).act()
#     else:
#         data.bios_set([[realtek_wakeonelan_type[lan_number], bios_status, 'item']]).act()
#
#     #confirm the data_re returned list
#     # if not data_re[0]:
#     #     pytest.skip(data_re[1])
#
#     lan_link = lan_link_initial(lan_number)
#     #get client side object and read to send MAC address to server
#     mac_adr=get_mac[lan_number]
#
#     #send MAC data to server
#     try:
#         lan_link.sendall(mac_adr.encode('utf-8'))
#     except Exception as a:
#         print('Error occured, while lan link.')
#         lan_link.close()
#         pytest.skip('server connection has error.')
#
#     # enable lan device in OS device management
#     lan = get_lan_name()
#     device_wol_manage_action(lan[lan_number], os_wol_status)
#
#     while True:
#         recv=lan_link.recv(1024).decode()
#         if recv=='ok':
#             print(f'from server receive:{recv}')
#             break
#
#     now = datetime.datetime.now()
#     cmd('.\\tool\\sleeper\\sleeper.exe -S0010 -R 300 -N 1 -F -E')
#
#     time.sleep(5)
#     after=datetime.datetime.now()
#     _re=(after-now).seconds
#
#     #reset IP to dynamic status
#     cmd(f'netsh interface ip set address "{lan_device_number_get[lan_number]}" dhcp')
#     lan_link.close()
#     assert _re < 300

# @pytest.mark.skip('aaa')
# def test_lan2_wol_bios_enable_os_enable_s4(request, get_mac,lan_device_number_get):
#     # def test_lan2_wol_bios_enable_os_enable(request, get_mac,item,lan_device_number_get):
#     #confirm which lan device should be tested, starting from 0
#     lan_number=1
#     os_wol_status = 'Enabled'
#     bios_status='Enabled'
#
#     command = 'wmic nic where netEnabled=true get name'
#
#     # get all lan devices info
#     sub = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     result=sub.stdout.read()
#     result=[i for i in result.decode().lower().split() if 'intel' in i][0]
#
#     # start changing bios setting
#     data = ActManage(item_total_path(), request.node.name)
#
#     #disable lan2 chip
#     if 'intel' in result:
#         data.bios_set([[intel_wakeonlan_type[lan_number], bios_status, 'item']]).act()
#     else:
#         data.bios_set([[realtek_wakeonelan_type[lan_number], bios_status, 'item']]).act()
#
#     #confirm the data_re returned list
#     # if not data_re[0]:
#     #     pytest.skip(data_re[1])
#
#     lan_link = lan_link_initial(lan_number)
#     #get client side object and read to send MAC address to server
#     mac_adr=get_mac[lan_number]
#
#     #send MAC data to server
#     try:
#         lan_link.sendall(mac_adr.encode('utf-8'))
#     except Exception as a:
#         print('Error occured, while lan link.')
#         lan_link.close()
#         pytest.skip('server connection has error.')
#
#     # enable lan device in OS device management
#     lan = get_lan_name()
#     device_wol_manage_action(lan[lan_number], os_wol_status)
#
#     while True:
#         recv=lan_link.recv(1024).decode()
#         if recv=='ok':
#             print(f'from server receive:{recv}')
#             break
#
#     now = datetime.datetime.now()
#     cmd('.\\tool\\sleeper\\sleeper.exe -S0001 -R 300 -N 1 -F -E')
#
#     time.sleep(5)
#     after=datetime.datetime.now()
#     _re=(after-now).seconds
#
#     #reset IP to dynamic status
#     cmd(f'netsh interface ip set address "{lan_device_number_get[lan_number]}" dhcp')
#     lan_link.close()
#     assert _re < 300

# @pytest.mark.skip('testing')
def test_lan2_wol_bios_enable_os_enable_s5(request, get_mac,lan_device_number_get):
    # def test_lan2_wol_bios_enable_os_enable(request, get_mac,item,lan_device_number_get):
    #confirm which lan device should be tested, starting from 0
    lan_number=1
    os_wol_status = 'Enabled'
    bios_status='Enabled'

    command = 'wmic nic where netEnabled=true get name'

    # get all lan devices info
    sub = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result=sub.stdout.read()
    result=[i for i in result.decode().lower().split() if 'intel' in i][0]

    # start changing bios setting
    data = ActManage(item_total_path(), request.node.name)

    #disable lan2 chip
    if 'intel' in result:
        data.bios_set([[intel_wakeonlan_type[lan_number], bios_status, 'item'],
                       ['RTC Wake system from S5', 'Enabled','item'],
                       ['Wake up minute', '5','value']]).act()
    else:
        data.bios_set([[realtek_wakeonelan_type[lan_number], bios_status, 'item'],
                       ['RTC Wake system from S5', 'Enabled', 'item'],
                       ['Wake up minute', '5', 'value']]).act()

    # to set lan ic and connect with server
    lan_link = lan_link_initial(lan_number)

    # get client side object and ready to send MAC address to server
    mac_adr=get_mac[lan_number]

    #send MAC data to server
    try:
        lan_link.sendall(mac_adr.encode('utf-8'))
    except Exception as a:
        print('Error occured, while lan link.')
        lan_link.close()
        pytest.skip('server connection has error.')

    # enable lan device in OS device management
    lan = get_lan_name()
    device_wol_manage_action(lan[lan_number], os_wol_status)

    while True:
        recv=lan_link.recv(1024).decode()
        if recv=='ok':
            print(f'from server receive:{recv}')
            break

    if not os.path.exists('.\\temp\\shutdown.log'):
        with open('.\\temp\\shutdown.log','w') as file:
            now=datetime.datetime.now()
            file.write(datetime.datetime.strftime(now,'%Y-%m-%d-%H:%M:%S'))
        cmd('shutdown /s /t 1 /f')
        print('now sleep for 10 sec')
        time.sleep(10)

    if os.path.exists('.\\temp\\shutdown.log'):
        with open('.\\temp\\shutdown.log', 'r') as file:
            now=file.readlines()
            now=datetime.datetime.strptime(now[0],'%Y-%m-%d-%H:%M:%S')
    else:
        pytest.skip('look like shutdown.log did not save before')


    after=datetime.datetime.now()
    _re=(after-now).seconds

    #reset IP to dynamic status
    cmd(f'netsh interface ip set address "{lan_device_number_get[lan_number]}" dhcp')
    lan_link.close()
    assert _re < 300

# def test_lan1_surf_web(request, lan_device_number_get):
#     data = ActManage(item_total_path(), request.node.name)
#     data.bios_set([[None, None, 'default']]).act()
#
#     print('it is going to disable Lan2')
#     #disable lan2 first to make sure srufing web device is lan1
#     subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[1]}" admin=disabled')
#     #enable lan1
#     subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[0]}" admin=enabled')
#     time.sleep(20)
#
#     try:
#         _re=requests.get("https://www.google.com.tw/")
#     except Exception as a:
#         _re=a
#
#     subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[1]}" admin=enabled').wait()
#     time.sleep(20)
#     assert _re.status_code == 200


# def test_lan2_surf_web(request, item,lan_device_number_get):
#     data = ActManage(item_total_path(), request.node.name)
#     data.bios_set([[None, None, 'default']]).act()
#
#     print('it is going to disable Lan1')
#     # disable lan1 first to make sure srufing web device is lan2
#     subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[0]}" admin=disabled')
#     # enable lan2
#     subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[1]}" admin=enabled')
#     time.sleep(20)
#
#     try:
#         _re = requests.get("https://www.google.com.tw/")
#     except Exception as a:
#         _re = a
#
#     subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[0]}" admin=enabled').wait()
#     assert _re.status_code == 200
#
# def test_lan1_download_file(request, item, lan_device_number_get):
#     data = ActManage(item_total_path(), request.node.name)
#     data.bios_set([[None, None, 'default']]).act()
#
#     print('it is going to disable Lan2')
#     #disable lan2 first to make sure srufing web device is lan1
#     subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[1]}" admin=disabled')
#     #enable lan1
#     subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[0]}" admin=enabled')
#     time.sleep(30)
#
#     link='http://http.speed.hinet.net/test_010m.zip'
#     url=requests.get(link)
#     content=len(url.content)
#     assert content == 10485760
#
# def test_lan2_download_file(request, item, lan_device_number_get):
#     data = ActManage(item_total_path(), request.node.name)
#     data.bios_set([[None, None, 'default']]).act()

#     print('it is going to disable Lan1')
#     # disable lan1 first to make sure srufing web device is lan2
#     subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[0]}" admin=disabled')
#     # enable lan2
#     subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[1]}" admin=enabled')
#     time.sleep(30)
#
#     link='http://http.speed.hinet.net/test_010m.zip'
#     url=requests.get(link)
#     content=len(url.content)
#     assert content == 10485760
#
# def test_s3(request, item):
#     data = ActManage(item_total_path(), request.node.name)
#     data.bios_set([[None, None, 'default']]).act()

#     command='wmic nic where netEnabled=true get name, speed'
#     _re=subprocess.Popen(command,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     lan_chip=['intel','realtek']
#
#     first=[]
#     second=[]
#     while True:
#         output=_re.stdout.readline().decode().strip().lower()
#         if output == "":
#             break
#         for i in lan_chip:
#             if i in output:
#                 first.append(output)
#
#     cmd('.\\tool\\sleeper\\sleeper.exe -S0010 -R 30 -N 1 -E')
#     #wait for lan device recovery to be detected.
#     time.sleep(20)
#
#     _re = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     while True:
#         output=_re.stdout.readline().decode().strip().lower()
#         if output == "":
#             break
#         for m in first:
#             if m in output:
#                 second.append(output)
#
#     assert first == second
#
# def test_s4(request, item):

#     data = ActManage(item_total_path(), request.node.name)
#     data.bios_set([[None, None, 'default']]).act()

#     command='wmic nic where netEnabled=true get name, speed'
#     _re=subprocess.Popen(command,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     lan_chip=['intel','realtek']
#
#     first=[]
#     second=[]
#     while True:
#         output=_re.stdout.readline().decode().strip().lower()
#         if output == "":
#             break
#         for i in lan_chip:
#             if i in output:
#                 first.append(output)
#
#     cmd('.\\tool\\sleeper\\sleeper.exe -S0001 -R 60 -N 1 -E')
#
#     #wait for lan device recovery to be detected.
#     time.sleep(20)
#
#     _re = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     while True:
#         output=_re.stdout.readline().decode().strip().lower()
#         if output == "":
#             break
#         for m in first:
#             if m in output:
#                 second.append(output)
#
#     assert first == second
#
#
# def test_lan1_disable(request, item):
#     lan_chip = ['intel', 'realtek']
#     command = 'wmic nic where netEnabled=true get name'
#     before = []
#     after = []
#
#     #write all lan data info to file
#     if not os.path.exists('.\\temp\\before.txt'):
#         _re = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#
#         while True:
#             output = _re.stdout.readline().decode().strip().lower()
#             if output == "":
#                 break
#             for i in lan_chip:
#                 if i in output:
#                     with open('.\\temp\\before.txt', 'a') as a:
#                         a.write(output + '\n')
#
#     # read all lan info, before bios item is changed.
#     with open('.\\temp\\before.txt', 'r') as a:
#         before = a.read().strip()
#         before = before.split('\n')
#         print(before)
#
#     # start changing bios setting

#     data = ActManage(item_total_path(), request.node.name)
#     if 'intel' in before:
#         data.bios_set([[intel_lan_controller_type[0], 'Disabled', 'item']]).act()
#     else:
#         data.bios_set([[realtek_lan_controller_type[0], 'Disabled', 'item']]).act()
#
#     # read all lan info, after bios item is changed.
#     _re = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     while True:
#         output = _re.stdout.readline().decode().strip().lower()
#         if output == "":
#             break
#         for i in lan_chip:
#             if i in output:
#                 after.append(output)
#     os.unlink('.\\temp\\before.txt')
#     assert before[0] != after[0]
#
# def test_lan2_disable(request, item):
#     lan_chip = ['intel', 'realtek']
#     command = 'wmic nic where netEnabled=true get name'
#     before=[]
#     after=[]
#
#     #write all lan data info to file
#     if not os.path.exists('.\\temp\\before.txt'):
#         _re=subprocess.Popen(command,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#
#         while True:
#             output=_re.stdout.readline().decode().strip().lower()
#             if output == "":
#                 break
#             for i in lan_chip:
#                 if i in output:
#                     with open('.\\temp\\before.txt', 'a') as a:
#                         a.write(output+'\n')
#
#     #read all lan info, before bios item is changed.
#     with open('.\\temp\\before.txt','r') as a:
#         before=a.read().strip()
#         before=before.split('\n')
#         print(before)
#
#     #start changing bios setting

#     data = ActManage(item_total_path(), request.node.name)
#     if 'intel' in before:
#         data.bios_set([[intel_lan_controller_type[1], 'Disabled', 'item']]).act()
#     else:
#         data.bios_set([[realtek_lan_controller_type[1], 'Disabled', 'item']]).act()
#
#     #read all lan info, after bios item is changed.
#     _re = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     while True:
#         output = _re.stdout.readline().decode().strip().lower()
#         if output == "":
#             break
#         for i in lan_chip:
#             if i in output:
#                 after.append(output)
#     os.unlink('.\\temp\\before.txt')
#     assert before[1] != after[0]
#


def test_11(request):
    # name = item_name_filter(request.node.name)
    # # start changing bios setting
    # data = ActManage(name, item)
    #
    # # disable lan2 chip
    # data_re = data.bios_set([intel_wakeonlan_type[1], 'Enabled', 'item']).act()
    # if not data_re[0]:
    #     pytest.skip(data_re[1])
    # data = ActManage(item_total_path(), request.node.name)
    # data.bios_set([None, None, 'default']).act()
    # data.bios_set([]).act()
    data = ActManage(item_total_path(), request.node.name)
    data.bios_set([[None, None, 'default']]).act()
    assert 1==1


def test_22(request):
    # name = item_name_filter(request.node.name)
    # # start changing bios setting
    # data = ActManage(name, item)
    #
    # # disable lan2 chip
    # data_re = data.bios_set([intel_wakeonlan_type[1], 'Enabled', 'item']).act()
    # if not data_re[0]:
    #     pytest.skip(data_re[1])

    
    data = ActManage(item_total_path(), request.node.name)
    data.bios_set([None, None, 'default']).act()
    if not os.path.exists('.\\temp\\shutdown.log'):
        with open('.\\temp\\shutdown.log','w') as file:
            file.write('')
        cmd('shutdown /s /t 1 /f')
        time.sleep(10)
    # data.bios_set([]).act()
    with allure.step('test title'):
        print('i am good.')
    assert 1 == 1
#
# class TestOther:
#     def test_12(self,request):
#         aa=item_total_path()
#         data = ActManage(item_total_path(), request.node.name)
#         data.bios_set([None, None, 'default']).act()
#         # data.bios_set([]).act()
#         assert 11==11
#
# def test_44(request):
#     data = ActManage(item_total_path(), request.node.name)
#     data.bios_set([None, None, 'default']).act()
#     # data.bios_set([]).act()
#     assert 11==11
#
# def test_current(request):
#     data = ActManage(item_total_path(), request.node.name)
#     data.bios_set([None, None, 'default']).act()
#     # data.bios_set([]).act()
#     assert 11 == 11
#     # print(os.getenv('PYTEST_CURRENT_TEST'))
#








