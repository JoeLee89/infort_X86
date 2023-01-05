from wakeonlan import send_magic_packet
import subprocess,time,socket

def lan_device_number_get():
    _code=''
    try:
        sub = subprocess.Popen('netsh interface show interface', stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read().decode()
        _code='utf-8'
    except UnicodeDecodeError:
        _code='big5'
    sub = subprocess.Popen('netsh interface show interface', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    re = None
    while True:
        data = sub.stdout.readline().strip().decode(_code).split(maxsplit=3)
        if 'Connected' in data or '已連線' in data:
            for content in data:
                if content.startswith('Ethernet') or content.startswith('區域連線'):
                    re=content
        else:
            continue
        # find the first ethernet device and then exit. it means the first connected lan device.
        # so before server launch, only one lan can be connected.
        if re or len(data) == 0:
            break
    return re

def wol(mac):
    time.sleep(30)
    print(f'Sending magic package ({mac})')
    send_magic_packet(mac)

#make server IP as static IP first

ip='10.0.0.1.19'
mask='255.255.255.0'
print('set up the first connected etherner device IP as static IP.')
print(f'IP= {ip}, MASK=255.255.255.0')
re=lan_device_number_get()
subprocess.Popen(f'netsh interface ip set address name="{re}" static {ip} {mask}')

#start to launch server action
host=ip
port=8000
server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port))
server.listen(5)
print('Waiting for any message from client...')
while True:
    conn,addr=server.accept()
    try:
        client_message=str(conn.recv(1024),encoding='utf-8')
    except Exception as a:
        print('Error message occurs:', a)
        continue
    print('client MAC=', client_message)
    print('Server will send WOL package to client after 30 second.')
    conn.sendall(b'ok')
    wol(client_message)
    conn.close()
