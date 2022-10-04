import subprocess,os

def cmd(command):
    subp=subprocess.Popen(command,shell=True)
    subp.wait(300)
    if subp.poll() != 0:
        print('Failed to launch the tool with the command.')

# reboot mainly check if the ***_rebooted.txt exists, if not then create file and reboot DUT
# it also help program to know if DUT is done to the reboot process or not.
# reboot process will create the run.bat file in strartup folder at the same time
# return false = reboot is finish.
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

    else:
        return False
        # os.unlink(f'{script_location}{name}_rebooted.txt')
        # os.unlink(f'{auto_location}run.bat')

# check if the test item has been tested or not.
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