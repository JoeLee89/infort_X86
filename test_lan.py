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


def lan_info_collection():
    proc = subprocess.Popen(['ipconfig', '-all'], stdout=subprocess.PIPE)
    title = 0
    title_name=[]
    device=[]
    mac=[]
    search_title = re.compile(r'Ethernet adapter (Ethernet.*):')
    search_lan_name = re.compile(r'Description.*: (.*)')
    search_lan_address = re.compile(r'Physical Address.*: (.*)')
    # search_title = re.compile(r'乙太網路卡 (乙太網路.*):')
    # search_lan_name = re.compile(r'描述.*: (.*)')
    # search_lan_address = re.compile(r'實體位址.*: (.*)')
    lan_list=dict()
    _title=''
    _name = ''
    _mac=''
    for line in iter(proc.stdout.readline,''):
        # print(line.strip().decode('big5'))
        line=line.decode('utf-8')
        # line=line.decode('big5')
        # print(line)
        search_title_re = search_title.search(line)
        search_lan_name_re = search_lan_name.search(line)
        search_lan_mac_re = search_lan_address.search(line)

        if not title and search_title_re:
            _title=search_title_re.group(1).strip()
            title = 1
        if title and search_lan_name_re:
            _name=search_lan_name_re.group(1).strip()
            lan_list[_title]=''

        if title and search_lan_mac_re:
            _mac=search_lan_mac_re.group(1).replace('-', '').strip()
            lan_list[_title]=[_name,_mac]
            title = 0

        if not line:
            break

    title_name, device, mac=lan_oder_organize(lan_list)
    # if mac_list.txt is empty, then will return OS collection data without organization
    if not len(device) and not len(mac):
        title_name =list(lan_list.keys())
        for i in lan_list.values():
            print(i)
            device.append(i[0])
            mac.append(i[1])

    return title_name, device, mac


def lan_oder_organize(content):
    device=[]
    title=[]
    mac=[]
    orig=[]
    with open('mac_list.txt','r') as file:
        orig=file.readlines()
        orig=[i.strip() for i in orig]
    for address in orig:
        # each mac from mac_list.txt will be checked one by one from dut os collection
        # loop every content from OS collection, when each mac address is read from mac_list.txt
        # so result device/mac can be organized in order
        for title_name,value in content.items():
            if address in value[1]:
                mac.append(value[1])
                device.append(value[0])
                title.append(title_name)

    return title, device, mac


def get_lan_name():
    _,lan_list,_=lan_info_collection()
    return lan_list if lan_list else []

@pytest.fixture
def get_mac():
    _,_,mac_list=lan_info_collection()
    return mac_list if mac_list else []

@pytest.fixture()
def lan_device_number_get():
    # sub = subprocess.Popen('netsh interface show interface', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # i = 0
    # re = []
    # while True:
    #     data = sub.stdout.readline().decode().strip().split(maxsplit=3)
    #     for content in data:
    #         if content.startswith('Ethernet'):
    #             re.append(content)
    #     if len(data) == 0:
    #         i += 1
    #     if i == 2:
    #         break
    re, _, _ = lan_info_collection()
    return re

# get each ethernet lan device name for future usage
def lan_device_number_get_other():
    # sub = subprocess.Popen('netsh interface show interface', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # i = 0
    # re = []
    # while True:
    #     data = sub.stdout.readline().decode().strip().split(maxsplit=3)
    #     for content in data:
    #         if content.startswith('Ethernet'):
    #             re.append(content)
    #     if len(data) == 0:
    #         i += 1
    #     if i == 2:
    #         break

    re, _, _ = lan_info_collection()
    return re


# to set pointed dut ip as static ip, and to make a connecting with server
def lan_link_initial(lan_number):
    dut_ip='10.0.1.18'
    server_ip = '10.0.1.19'
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

def print_lan_info(name,mac):
    with allure.step('The Lan device:'):
        allure.step(f'Lan Name: {name}')
        allure.step(f'Lan MAC: {mac}')


class Test_WOL_LAN1:
    def test_lan1_wol_bios_enable_os_enable_s3(request, get_mac, lan_device_number_get):
        # def test_lan2_wol_bios_enable_os_enable(request, get_mac,item,lan_device_number_get):
        # confirm which lan device should be tested, starting from 0
        lan_number = 0
        os_wol_status = 'Enabled'
        bios_status = 'Enabled'
        allure.title('')

        command = 'wmic nic where netEnabled=true get name'

        # get all lan devices info
        sub = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = sub.stdout.read()
        result = [i for i in result.decode().lower().split() if 'intel' in i]
        result = result[0] if len(result) > 0 else ''

        # start changing bios setting
        data = ActManage(item_total_path(), request.node.name)

        # disable lan2 chip
        if 'intel' in result:
            data.bios_set([[intel_wakeonlan_type[lan_number], bios_status, 'item']]).act()
        else:
            data.bios_set([[realtek_wakeonelan_type[lan_number], bios_status, 'item']]).act()

        lan = get_lan_name()
        # print lan related info to allure report
        print_lan_info(lan[lan_number], get_mac[lan_number])
        # get link with wol server side
        lan_link = lan_link_initial(lan_number)
        # send MAC data to server
        try:
            lan_link.sendall(get_mac[lan_number].encode('utf-8'))
        except Exception as a:
            print('Error occurred, while lan link.')
            lan_link.close()
            pytest.skip('server connection has error.')

        # enable or disable lan device in OS device management
        device_wol_manage_action(lan[lan_number], os_wol_status)

        while True:
            recv = lan_link.recv(1024).decode()
            if recv == 'ok':
                print(f'from server receive:{recv}')
                break

        now = datetime.datetime.now()
        cmd('.\\tool\\sleeper\\sleeper.exe -S0010 -R 300 -N 1 -F -E')

        time.sleep(5)
        after = datetime.datetime.now()
        _re = (after - now).seconds

        # reset IP to dynamic status
        cmd(f'netsh interface ip set address "{lan_device_number_get[lan_number]}" dhcp')
        lan_link.close()
        assert _re < 300


    def test_lan1_wol_bios_enable_os_disable_s3(request, get_mac, lan_device_number_get):
        # def test_lan2_wol_bios_enable_os_enable(request, get_mac,item,lan_device_number_get):
        # confirm which lan device should be tested, starting from 0
        lan_number = 0
        os_wol_status = 'Disabled'
        bios_status = 'Enabled'

        command = 'wmic nic where netEnabled=true get name'

        # get all lan devices info
        sub = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = sub.stdout.read()
        result = [i for i in result.decode().lower().split() if 'intel' in i]
        result = result[0] if len(result) > 0 else ''

        # start changing bios setting
        data = ActManage(item_total_path(), request.node.name)

        # disable lan2 chip
        if 'intel' in result:
            data.bios_set([[intel_wakeonlan_type[lan_number], bios_status, 'item']]).act()
        else:
            data.bios_set([[realtek_wakeonelan_type[lan_number], bios_status, 'item']]).act()

        lan = get_lan_name()
        # print lan related info to allure report
        print_lan_info(lan[lan_number], get_mac[lan_number])
        # get link with wol server side
        lan_link = lan_link_initial(lan_number)
        # send MAC data to server
        try:
            lan_link.sendall(get_mac[lan_number].encode('utf-8'))
        except Exception as a:
            print('Error occurred, while lan link.')
            lan_link.close()
            pytest.skip('server connection has error.')

        # enable or disable lan device in OS device management
        device_wol_manage_action(lan[lan_number], os_wol_status)

        while True:
            recv = lan_link.recv(1024).decode()
            if recv == 'ok':
                print(f'from server receive:{recv}')
                break

        now = datetime.datetime.now()
        cmd('.\\tool\\sleeper\\sleeper.exe -S0010 -R 300 -N 1 -F -E')

        time.sleep(5)
        after = datetime.datetime.now()
        _re = (after - now).seconds

        # reset IP to dynamic status
        cmd(f'netsh interface ip set address "{lan_device_number_get[lan_number]}" dhcp')
        lan_link.close()
        assert _re > 300


    def test_lan1_wol_bios_disable_os_enable_s3(request, get_mac, lan_device_number_get):
        # def test_lan2_wol_bios_enable_os_enable(request, get_mac,item,lan_device_number_get):
        # confirm which lan device should be tested, starting from 0
        lan_number = 0
        os_wol_status = 'Enabled'
        bios_status = 'Disabled'

        command = 'wmic nic where netEnabled=true get name'

        # get all lan devices info
        sub = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = sub.stdout.read()
        result = [i for i in result.decode().lower().split() if 'intel' in i]
        result = result[0] if len(result) > 0 else ''

        # start changing bios setting
        data = ActManage(item_total_path(), request.node.name)

        # disable lan2 chip
        if 'intel' in result:
            data.bios_set([[intel_wakeonlan_type[lan_number], bios_status, 'item']]).act()
        else:
            data.bios_set([[realtek_wakeonelan_type[lan_number], bios_status, 'item']]).act()

        lan = get_lan_name()
        # print lan related info to allure report
        print_lan_info(lan[lan_number], get_mac[lan_number])
        # get link with wol server side
        lan_link = lan_link_initial(lan_number)
        # send MAC data to server
        try:
            lan_link.sendall(get_mac[lan_number].encode('utf-8'))
        except Exception as a:
            print('Error occurred, while lan link.')
            lan_link.close()
            pytest.skip('server connection has error.')

        # enable or disable lan device in OS device management
        device_wol_manage_action(lan[lan_number], os_wol_status)

        while True:
            recv = lan_link.recv(1024).decode()
            if recv == 'ok':
                print(f'from server receive:{recv}')
                break

        now = datetime.datetime.now()
        cmd('.\\tool\\sleeper\\sleeper.exe -S0010 -R 300 -N 1 -F -E')

        time.sleep(5)
        after = datetime.datetime.now()
        _re = (after - now).seconds

        # reset IP to dynamic status
        cmd(f'netsh interface ip set address "{lan_device_number_get[lan_number]}" dhcp')
        lan_link.close()
        assert _re > 300


    def test_lan1_wol_bios_disable_os_disable_s3(request, get_mac, lan_device_number_get):
        # def test_lan2_wol_bios_enable_os_enable(request, get_mac,item,lan_device_number_get):
        # confirm which lan device should be tested, starting from 0
        lan_number = 0
        os_wol_status = 'Disabled'
        bios_status = 'Disabled'

        command = 'wmic nic where netEnabled=true get name'

        # get all lan devices info
        sub = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = sub.stdout.read()
        result = [i for i in result.decode().lower().split() if 'intel' in i]
        result = result[0] if len(result) > 0 else ''

        # start changing bios setting
        data = ActManage(item_total_path(), request.node.name)

        # disable lan2 chip
        if 'intel' in result:
            data.bios_set([[intel_wakeonlan_type[lan_number], bios_status, 'item']]).act()
        else:
            data.bios_set([[realtek_wakeonelan_type[lan_number], bios_status, 'item']]).act()

        lan = get_lan_name()
        # print lan related info to allure report
        print_lan_info(lan[lan_number], get_mac[lan_number])
        # get link with wol server side
        lan_link = lan_link_initial(lan_number)
        # send MAC data to server
        try:
            lan_link.sendall(get_mac[lan_number].encode('utf-8'))
        except Exception as a:
            print('Error occurred, while lan link.')
            lan_link.close()
            pytest.skip('server connection has error.')

        # enable or disable lan device in OS device management
        device_wol_manage_action(lan[lan_number], os_wol_status)

        while True:
            recv = lan_link.recv(1024).decode()
            if recv == 'ok':
                print(f'from server receive:{recv}')
                break

        now = datetime.datetime.now()
        cmd('.\\tool\\sleeper\\sleeper.exe -S0010 -R 300 -N 1 -F -E')

        time.sleep(5)
        after = datetime.datetime.now()
        _re = (after - now).seconds

        # reset IP to dynamic status
        cmd(f'netsh interface ip set address "{lan_device_number_get[lan_number]}" dhcp')
        lan_link.close()
        assert _re > 300


    # @pytest.mark.skip('aaa')
    def test_lan1_wol_bios_enable_os_enable_s4(request, get_mac, lan_device_number_get):
        # def test_lan2_wol_bios_enable_os_enable(request, get_mac,item,lan_device_number_get):
        # confirm which lan device should be tested, starting from 0
        lan_number = 0
        os_wol_status = 'Enabled'
        bios_status = 'Enabled'

        command = 'wmic nic where netEnabled=true get name'

        # get all lan devices info
        sub = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = sub.stdout.read()
        result = [i for i in result.decode().lower().split() if 'intel' in i]
        result = result[0] if len(result) > 0 else ''

        # start changing bios setting
        data = ActManage(item_total_path(), request.node.name)

        # disable lan2 chip
        if 'intel' in result:
            data.bios_set([[intel_wakeonlan_type[lan_number], bios_status, 'item']]).act()
        else:
            data.bios_set([[realtek_wakeonelan_type[lan_number], bios_status, 'item']]).act()

        lan = get_lan_name()
        # print lan related info to allure report
        print_lan_info(lan[lan_number], get_mac[lan_number])
        # get link with wol server side
        lan_link = lan_link_initial(lan_number)
        # send MAC data to server
        try:
            lan_link.sendall(get_mac[lan_number].encode('utf-8'))
        except Exception as a:
            print('Error occurred, while lan link.')
            lan_link.close()
            pytest.skip('server connection has error.')

        # enable or disable lan device in OS device management
        device_wol_manage_action(lan[lan_number], os_wol_status)
        while True:
            recv = lan_link.recv(1024).decode()
            if recv == 'ok':
                print(f'from server receive:{recv}')
                break

        now = datetime.datetime.now()
        cmd('.\\tool\\sleeper\\sleeper.exe -S0001 -R 300 -N 1 -F -E')

        time.sleep(5)
        after = datetime.datetime.now()
        _re = (after - now).seconds

        # reset IP to dynamic status
        cmd(f'netsh interface ip set address "{lan_device_number_get[lan_number]}" dhcp')
        lan_link.close()
        assert _re < 300


    # @pytest.mark.skip('testing')
    def test_lan1_wol_bios_enable_os_enable_s5(request, get_mac, lan_device_number_get):
        # def test_lan2_wol_bios_enable_os_enable(request, get_mac,item,lan_device_number_get):
        # confirm which lan device should be tested, starting from 0
        lan_number = 0
        os_wol_status = 'Enabled'
        bios_status = 'Enabled'

        command = 'wmic nic where netEnabled=true get name'

        # get all lan devices info
        sub = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result = sub.stdout.read()
        result = [i for i in result.decode().lower().split() if 'intel' in i]
        result = result[0] if len(result) > 0 else ''

        # start changing bios setting
        data = ActManage(item_total_path(), request.node.name)

        # disable lan2 chip
        if 'intel' in result:
            data.bios_set([[intel_wakeonlan_type[lan_number], bios_status, 'item'],
                           ['RTC Wake system from S5', 'Fixed Time', 'item'],
                           ['Wake up minute', '5', 'value']]).act()
        else:
            data.bios_set([[realtek_wakeonelan_type[lan_number], bios_status, 'item'],
                           ['RTC Wake system from S5', 'Fixed Time', 'item'],
                           ['Wake up minute', '5', 'value']]).act()

        lan = get_lan_name()
        # print lan related info to allure report
        print_lan_info(lan[lan_number], get_mac[lan_number])
        # get link with wol server side
        lan_link = lan_link_initial(lan_number)
        # send MAC data to server
        try:
            lan_link.sendall(get_mac[lan_number].encode('utf-8'))
        except Exception as a:
            print('Error occurred, while lan link.')
            lan_link.close()
            pytest.skip('server connection has error.')

        # enable or disable lan device in OS device management
        device_wol_manage_action(lan[lan_number], os_wol_status)

        while True:
            recv = lan_link.recv(1024).decode()
            if recv == 'ok':
                print(f'from server receive:{recv}')
                break

        if not os.path.exists('.\\temp\\shutdown.log'):
            with open('.\\temp\\shutdown.log', 'w') as file:
                now = datetime.datetime.now()
                file.write(datetime.datetime.strftime(now, '%Y-%m-%d-%H:%M:%S'))
            cmd('shutdown /s /t 1 /f')
            print('now sleep for 10 sec')
            time.sleep(10)

        if os.path.exists('.\\temp\\shutdown.log'):
            with open('.\\temp\\shutdown.log', 'r') as file:
                now = file.readlines()
                now = datetime.datetime.strptime(now[0], '%Y-%m-%d-%H:%M:%S')
        else:
            pytest.skip('look like shutdown.log did not save before')

        after = datetime.datetime.now()
        _re = (after - now).seconds

        # reset IP to dynamic status
        cmd(f'netsh interface ip set address "{lan_device_number_get[lan_number]}" dhcp')
        lan_link.close()
        assert _re < 300

class Test_WOL_LAN2:
    def test_lan2_wol_bios_enable_os_enable_s3(request, get_mac,lan_device_number_get):
        # def test_lan2_wol_bios_enable_os_enable(request, get_mac,item,lan_device_number_get):
        #confirm which lan device should be tested, starting from 0
        lan_number=1
        os_wol_status = 'Enabled'
        bios_status='Enabled'

        command = 'wmic nic where netEnabled=true get name'

        # get all lan devices info
        sub = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result=sub.stdout.read()
        result = [i for i in result.decode().lower().split() if 'intel' in i]
        result = result[0] if len(result) > 0 else ''

        # start changing bios setting
        data = ActManage(item_total_path(), request.node.name)

        #disable lan2 chip
        if 'intel' in result:
            data.bios_set([[intel_wakeonlan_type[lan_number], bios_status, 'item']]).act()
        else:
            data.bios_set([[realtek_wakeonelan_type[lan_number], bios_status, 'item']]).act()

        lan = get_lan_name()
        # print lan related info to allure report
        print_lan_info(lan[lan_number], get_mac[lan_number])
        # get link with wol server side
        lan_link = lan_link_initial(lan_number)
        # send MAC data to server
        try:
            lan_link.sendall(get_mac[lan_number].encode('utf-8'))
        except Exception as a:
            print('Error occurred, while lan link.')
            lan_link.close()
            pytest.skip('server connection has error.')

        # enable or disable lan device in OS device management
        device_wol_manage_action(lan[lan_number], os_wol_status)

        while True:
            recv=lan_link.recv(1024).decode()
            if recv=='ok':
                print(f'from server receive:{recv}')
                break

        now = datetime.datetime.now()
        cmd('.\\tool\\sleeper\\sleeper.exe -S0010 -R 300 -N 1 -F -E')

        time.sleep(5)
        after=datetime.datetime.now()
        _re=(after-now).seconds

        #reset IP to dynamic status
        cmd(f'netsh interface ip set address "{lan_device_number_get[lan_number]}" dhcp')
        lan_link.close()
        assert _re < 300

    def test_lan2_wol_bios_enable_os_disable_s3(request, get_mac,lan_device_number_get):
        # def test_lan2_wol_bios_enable_os_enable(request, get_mac,item,lan_device_number_get):
        #confirm which lan device should be tested, starting from 0
        lan_number=1
        os_wol_status = 'Disabled'
        bios_status='Enabled'

        command = 'wmic nic where netEnabled=true get name'

        # get all lan devices info
        sub = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result=sub.stdout.read()
        result = [i for i in result.decode().lower().split() if 'intel' in i]
        result = result[0] if len(result) > 0 else ''

        # start changing bios setting
        data = ActManage(item_total_path(), request.node.name)

        #disable lan2 chip
        if 'intel' in result:
            data.bios_set([[intel_wakeonlan_type[lan_number], bios_status, 'item']]).act()
        else:
            data.bios_set([[realtek_wakeonelan_type[lan_number], bios_status, 'item']]).act()

        lan = get_lan_name()
        # print lan related info to allure report
        print_lan_info(lan[lan_number], get_mac[lan_number])
        # get link with wol server side
        lan_link = lan_link_initial(lan_number)
        # send MAC data to server
        try:
            lan_link.sendall(get_mac[lan_number].encode('utf-8'))
        except Exception as a:
            print('Error occurred, while lan link.')
            lan_link.close()
            pytest.skip('server connection has error.')

        # enable or disable lan device in OS device management
        device_wol_manage_action(lan[lan_number], os_wol_status)

        while True:
            recv=lan_link.recv(1024).decode()
            if recv=='ok':
                print(f'from server receive:{recv}')
                break

        now = datetime.datetime.now()
        cmd('.\\tool\\sleeper\\sleeper.exe -S0010 -R 300 -N 1 -F -E')

        time.sleep(5)
        after=datetime.datetime.now()
        _re=(after-now).seconds

        #reset IP to dynamic status
        cmd(f'netsh interface ip set address "{lan_device_number_get[lan_number]}" dhcp')
        lan_link.close()
        assert _re > 300

    def test_lan2_wol_bios_disable_os_enable_s3(request, get_mac,lan_device_number_get):
        # def test_lan2_wol_bios_enable_os_enable(request, get_mac,item,lan_device_number_get):
        #confirm which lan device should be tested, starting from 0
        lan_number=1
        os_wol_status = 'Enabled'
        bios_status='Disabled'

        command = 'wmic nic where netEnabled=true get name'

        # get all lan devices info
        sub = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result=sub.stdout.read()
        result = [i for i in result.decode().lower().split() if 'intel' in i]
        result = result[0] if len(result) > 0 else ''

        # start changing bios setting
        data = ActManage(item_total_path(), request.node.name)

        #disable lan2 chip
        if 'intel' in result:
            data.bios_set([[intel_wakeonlan_type[lan_number], bios_status, 'item']]).act()
        else:
            data.bios_set([[realtek_wakeonelan_type[lan_number], bios_status, 'item']]).act()

        lan = get_lan_name()
        # print lan related info to allure report
        print_lan_info(lan[lan_number], get_mac[lan_number])
        # get link with wol server side
        lan_link = lan_link_initial(lan_number)
        # send MAC data to server
        try:
            lan_link.sendall(get_mac[lan_number].encode('utf-8'))
        except Exception as a:
            print('Error occurred, while lan link.')
            lan_link.close()
            pytest.skip('server connection has error.')

        # enable or disable lan device in OS device management
        device_wol_manage_action(lan[lan_number], os_wol_status)

        while True:
            recv=lan_link.recv(1024).decode()
            if recv=='ok':
                print(f'from server receive:{recv}')
                break

        now = datetime.datetime.now()
        cmd('.\\tool\\sleeper\\sleeper.exe -S0010 -R 300 -N 1 -F -E')

        time.sleep(5)
        after=datetime.datetime.now()
        _re=(after-now).seconds

        #reset IP to dynamic status
        cmd(f'netsh interface ip set address "{lan_device_number_get[lan_number]}" dhcp')
        lan_link.close()
        assert _re > 300

    def test_lan2_wol_bios_disable_os_disable_s3(request, get_mac,lan_device_number_get):
        # def test_lan2_wol_bios_enable_os_enable(request, get_mac,item,lan_device_number_get):
        #confirm which lan device should be tested, starting from 0
        lan_number=1
        os_wol_status = 'Disabled'
        bios_status='Disabled'

        command = 'wmic nic where netEnabled=true get name'

        # get all lan devices info
        sub = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result=sub.stdout.read()
        result = [i for i in result.decode().lower().split() if 'intel' in i]
        result = result[0] if len(result) > 0 else ''

        # start changing bios setting
        data = ActManage(item_total_path(), request.node.name)

        #disable lan2 chip
        if 'intel' in result:
            data.bios_set([[intel_wakeonlan_type[lan_number], bios_status, 'item']]).act()
        else:
            data.bios_set([[realtek_wakeonelan_type[lan_number], bios_status, 'item']]).act()

        lan = get_lan_name()
        # print lan related info to allure report
        print_lan_info(lan[lan_number], get_mac[lan_number])
        # get link with wol server side
        lan_link = lan_link_initial(lan_number)
        # send MAC data to server
        try:
            lan_link.sendall(get_mac[lan_number].encode('utf-8'))
        except Exception as a:
            print('Error occurred, while lan link.')
            lan_link.close()
            pytest.skip('server connection has error.')

        # enable or disable lan device in OS device management
        device_wol_manage_action(lan[lan_number], os_wol_status)

        while True:
            recv=lan_link.recv(1024).decode()
            if recv=='ok':
                print(f'from server receive:{recv}')
                break

        now = datetime.datetime.now()
        cmd('.\\tool\\sleeper\\sleeper.exe -S0010 -R 300 -N 1 -F -E')

        time.sleep(5)
        after=datetime.datetime.now()
        _re=(after-now).seconds

        #reset IP to dynamic status
        cmd(f'netsh interface ip set address "{lan_device_number_get[lan_number]}" dhcp')
        lan_link.close()
        assert _re > 300

    # @pytest.mark.skip('aaa')
    def test_lan2_wol_bios_enable_os_enable_s4(request, get_mac,lan_device_number_get):
        # def test_lan2_wol_bios_enable_os_enable(request, get_mac,item,lan_device_number_get):
        #confirm which lan device should be tested, starting from 0
        lan_number=1
        os_wol_status = 'Enabled'
        bios_status='Enabled'

        command = 'wmic nic where netEnabled=true get name'

        # get all lan devices info
        sub = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        result=sub.stdout.read()
        result = [i for i in result.decode().lower().split() if 'intel' in i]
        result = result[0] if len(result) > 0 else ''

        # start changing bios setting
        data = ActManage(item_total_path(), request.node.name)

        #disable lan2 chip
        if 'intel' in result:
            data.bios_set([[intel_wakeonlan_type[lan_number], bios_status, 'item']]).act()
        else:
            data.bios_set([[realtek_wakeonelan_type[lan_number], bios_status, 'item']]).act()

        lan = get_lan_name()
        # print lan related info to allure report
        print_lan_info(lan[lan_number], get_mac[lan_number])
        # get link with wol server side
        lan_link = lan_link_initial(lan_number)
        # send MAC data to server
        try:
            lan_link.sendall(get_mac[lan_number].encode('utf-8'))
        except Exception as a:
            print('Error occurred, while lan link.')
            lan_link.close()
            pytest.skip('server connection has error.')

        # enable or disable lan device in OS device management
        device_wol_manage_action(lan[lan_number], os_wol_status)

        while True:
            recv=lan_link.recv(1024).decode()
            if recv=='ok':
                print(f'from server receive:{recv}')
                break

        now = datetime.datetime.now()
        cmd('.\\tool\\sleeper\\sleeper.exe -S0001 -R 300 -N 1 -F -E')

        time.sleep(5)
        after=datetime.datetime.now()
        _re=(after-now).seconds

        #reset IP to dynamic status
        cmd(f'netsh interface ip set address "{lan_device_number_get[lan_number]}" dhcp')
        lan_link.close()
        assert _re < 300

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
        result = [i for i in result.decode().lower().split() if 'intel' in i]
        result = result[0] if len(result) > 0 else ''

        # start changing bios setting
        data = ActManage(item_total_path(), request.node.name)

        #disable lan2 chip
        if 'intel' in result:
            data.bios_set([[intel_wakeonlan_type[lan_number], bios_status, 'item'],
                           ['RTC Wake system from S5', 'Fixed Time','item'],
                           ['Wake up minute', '5','value']]).act()
        else:
            data.bios_set([[realtek_wakeonelan_type[lan_number], bios_status, 'item'],
                           ['RTC Wake system from S5', 'Fixed Time', 'item'],
                           ['Wake up minute', '5', 'value']]).act()

        lan = get_lan_name()
        # print lan related info to allure report
        print_lan_info(lan[lan_number], get_mac[lan_number])
        # get link with wol server side
        lan_link = lan_link_initial(lan_number)
        # send MAC data to server
        try:
            lan_link.sendall(get_mac[lan_number].encode('utf-8'))
        except Exception as a:
            print('Error occurred, while lan link.')
            lan_link.close()
            pytest.skip('server connection has error.')

        # enable or disable lan device in OS device management
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

def test_lan1_surf_web(request, lan_device_number_get):
    data = ActManage(item_total_path(), request.node.name)
    data.bios_set([[None, None, 'default']]).act()

    print('it is going to disable Lan2')
    #disable lan2 first to make sure srufing web device is lan1
    subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[1]}" admin=disabled')
    #enable lan1
    subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[0]}" admin=enabled')
    time.sleep(20)

    try:
        _re=requests.get("https://www.google.com.tw/")
    except Exception as a:
        _re=a

    subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[1]}" admin=enabled').wait()
    time.sleep(20)
    assert _re.status_code == 200


def test_lan2_surf_web(request,lan_device_number_get):
    data = ActManage(item_total_path(), request.node.name)
    data.bios_set([[None, None, 'default']]).act()

    print('it is going to disable Lan1')
    # disable lan1 first to make sure srufing web device is lan2
    subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[0]}" admin=disabled')
    # enable lan2
    subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[1]}" admin=enabled')
    time.sleep(20)

    try:
        _re = requests.get("https://www.google.com.tw/")
    except Exception as a:
        _re = a

    subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[0]}" admin=enabled').wait()
    assert _re.status_code == 200
#
def test_lan1_download_file(request, lan_device_number_get):
    data = ActManage(item_total_path(), request.node.name)
    data.bios_set([[None, None, 'default']]).act()

    print('it is going to disable Lan2')
    #disable lan2 first to make sure srufing web device is lan1
    subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[1]}" admin=disabled')
    #enable lan1
    subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[0]}" admin=enabled')
    time.sleep(30)

    link='http://http.speed.hinet.net/test_010m.zip'
    url=requests.get(link)
    content=len(url.content)
    assert content == 10485760
#
def test_lan2_download_file(request, lan_device_number_get):
    data = ActManage(item_total_path(), request.node.name)
    data.bios_set([[None, None, 'default']]).act()

    print('it is going to disable Lan1')
    # disable lan1 first to make sure srufing web device is lan2
    subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[0]}" admin=disabled')
    # enable lan2
    subprocess.Popen(f'netsh interface set interface name="{lan_device_number_get[1]}" admin=enabled')
    time.sleep(30)

    link='http://http.speed.hinet.net/test_010m.zip'
    url=requests.get(link)
    content=len(url.content)
    assert content == 10485760

def test_s3(request):
    data = ActManage(item_total_path(), request.node.name)
    data.bios_set([[None, None, 'default']]).act()

    command='wmic nic where netEnabled=true get name, speed'
    _re=subprocess.Popen(command,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lan_chip=['intel','realtek']

    first=[]
    second=[]
    while True:
        output=_re.stdout.readline().decode().strip().lower()
        if output == "":
            break
        for i in lan_chip:
            if i in output:
                first.append(output)

    cmd('.\\tool\\sleeper\\sleeper.exe -S0010 -R 30 -N 1 -E')
    #wait for lan device recovery to be detected.
    time.sleep(20)

    _re = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        output=_re.stdout.readline().decode().strip().lower()
        if output == "":
            break
        for m in first:
            if m in output:
                second.append(output)

    assert first == second

def test_s4(request):
    data = ActManage(item_total_path(), request.node.name)
    data.bios_set([[None, None, 'default']]).act()

    command='wmic nic where netEnabled=true get name, speed'
    _re=subprocess.Popen(command,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lan_chip=['intel','realtek']

    first=[]
    second=[]
    while True:
        output=_re.stdout.readline().decode().strip().lower()
        if output == "":
            break
        for i in lan_chip:
            if i in output:
                first.append(output)

    cmd('.\\tool\\sleeper\\sleeper.exe -S0001 -R 60 -N 1 -E')

    #wait for lan device recovery to be detected.
    time.sleep(20)

    _re = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        output=_re.stdout.readline().decode().strip().lower()
        if output == "":
            break
        for m in first:
            if m in output:
                second.append(output)

    assert first == second


def test_lan1_disable(request):
    lan_chip = ['intel', 'realtek']
    command = 'wmic nic where netEnabled=true get name'
    before = []
    after = []

    #write all lan data info to file
    if not os.path.exists('.\\temp\\before.txt'):
        _re = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        while True:
            output = _re.stdout.readline().decode().strip().lower()
            if output == "":
                break
            for i in lan_chip:
                if i in output:
                    with open('.\\temp\\before.txt', 'a') as a:
                        a.write(output + '\n')

    # read all lan info, before bios item is changed.
    with open('.\\temp\\before.txt', 'r') as a:
        before = a.read().strip()
        before = before.split('\n')
        print(before)

    # start changing bios setting

    data = ActManage(item_total_path(), request.node.name)
    if 'intel' in before:
        data.bios_set([[intel_lan_controller_type[0], 'Disabled', 'item']]).act()
    else:
        data.bios_set([[realtek_lan_controller_type[0], 'Disabled', 'item']]).act()

    # read all lan info, after bios item is changed.
    _re = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        output = _re.stdout.readline().decode().strip().lower()
        if output == "":
            break
        for i in lan_chip:
            if i in output:
                after.append(output)
    os.unlink('.\\temp\\before.txt')
    assert before[0] != after[0]

def test_lan2_disable(request):
    lan_chip = ['intel', 'realtek']
    command = 'wmic nic where netEnabled=true get name'
    before=[]
    after=[]

    #write all lan data info to file
    if not os.path.exists('.\\temp\\before.txt'):
        _re=subprocess.Popen(command,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        while True:
            output=_re.stdout.readline().decode().strip().lower()
            if output == "":
                break
            for i in lan_chip:
                if i in output:
                    with open('.\\temp\\before.txt', 'a') as a:
                        a.write(output+'\n')

    #read all lan info, before bios item is changed.
    with open('.\\temp\\before.txt','r') as a:
        before=a.read().strip()
        before=before.split('\n')
        print(before)

    #start changing bios setting

    data = ActManage(item_total_path(), request.node.name)
    if 'intel' in before:
        data.bios_set([[intel_lan_controller_type[1], 'Disabled', 'item']]).act()
    else:
        data.bios_set([[realtek_lan_controller_type[1], 'Disabled', 'item']]).act()

    #read all lan info, after bios item is changed.
    _re = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        output = _re.stdout.readline().decode().strip().lower()
        if output == "":
            break
        for i in lan_chip:
            if i in output:
                after.append(output)
    os.unlink('.\\temp\\before.txt')
    assert before[1] != after[0]
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


# def test_22(request):
#     # name = item_name_filter(request.node.name)
#     # # start changing bios setting
#     # data = ActManage(name, item)
#     #
#     # # disable lan2 chip
#     # data_re = data.bios_set([intel_wakeonlan_type[1], 'Enabled', 'item']).act()
#     # if not data_re[0]:
#     #     pytest.skip(data_re[1])
#
#
#     data = ActManage(item_total_path(), request.node.name)
#     data.bios_set([None, None, 'default']).act()
#     if not os.path.exists('.\\temp\\shutdown.log'):
#         with open('.\\temp\\shutdown.log','w') as file:
#             file.write('')
#         cmd('shutdown /s /t 1 /f')
#         time.sleep(10)
#     # data.bios_set([]).act()
#     with allure.step('test title'):
#         print('i am good.')
#     assert 1 == 1
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








