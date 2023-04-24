from wakeonlan import send_magic_packet
import subprocess,time,socket,sys,os,signal,select,msvcrt

def lan_device_number_get():
    _code=''
    try:
        sub = subprocess.Popen('netsh interface show interface', stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read().decode()
        _code='utf-8'
    except UnicodeDecodeError:
        _code='big5'
    sub = subprocess.Popen('netsh interface show interface', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    re = None
    got_data_length_times=0
    while True:
        data = sub.stdout.readline().strip().decode(_code).split(maxsplit=3)
        time.sleep(1)
        if len(data) == 0:
            got_data_length_times+=1
        if 'Connected' in data or '已連線' in data:
            for content in data:
                # if content.startswith('Ethernet') or content.startswith('區域連線'):
                if content.startswith('Ethernet') or content.startswith('乙太網路'):
                    re = content
        elif got_data_length_times < 3:
            continue

        # find the first ethernet device and then exit. it means the first connected lan device.
        # so before server launch, only one lan can be connected.
        if re or len(data) == 0:
            break

    return re

def wol(mac):
    print('client MAC=', mac)
    print('Server will send WOL package to client after 30 second.')
    time.sleep(30)
    print(f'Sending magic package ({mac})')
    try:
        send_magic_packet(mac)
    except Exception as a:
        print('error:',a)

clients=[]

#make server IP as static IP first
ip='10.0.1.19'
mask='255.255.255.0'
print('set up the first connected etherner device IP as static IP.')
print(f'IP= {ip}, MASK=255.255.255.0')

re=lan_device_number_get()
if not re:
    raise RuntimeError(f'ethernet={re}. Can not get the correct ethernet name from the system.')
subprocess.Popen(f'netsh interface ip set address name="{re}" static {ip} {mask}')

#start to launch server action
host=''
port=8000
server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port))
server.setblocking(False)
server.listen(5)

# launch the iperf server mode
iperf_server = subprocess.Popen('.\\tool\\iperf\\iperf3.exe -s',stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
try:
    iperf_server.wait(2)
except:
    pass
print('='*50)
print('Start Iperf server mode')
print('='*50)

# detect the return code if it is not 0, then report the error message
return_code=0 if iperf_server.returncode is None else iperf_server.returncode
if return_code > 0:
    print('\n')
    print('*'*50)
    print('Got something wrong, while launch the iperf server mode.')
    print(iperf_server.stdout.read().decode('utf-8'))
    print('*' * 50)
    print('\n')

print('='*50)
print('Start WOL server')
print('='*50)
print('Waiting for receiving the MAC address from client...')
print('Press [x] to exit the server process.')

while True:
    # time.sleep(0.1)
    if msvcrt.kbhit():
        key=msvcrt.getch().decode('utf-8')
        if key == 'x':
            subprocess.Popen(f'netsh interface ip set address name="{re}" dhcp')
            os.kill(iperf_server.pid, signal.SIGTERM)
            break
    try:
        conn, addr = server.accept()
        conn.setblocking(False)
        clients.append(conn)
    except:
        pass

    for client in clients:
        try:
            client_message = str(client.recv(1024), encoding='utf-8')
            client.sendall(b'ok')
            wol(client_message)
            client.close()
            clients.remove(client)
        except:
            pass


