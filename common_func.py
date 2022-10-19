import subprocess,os,sys,pytest
import bios_update

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
    script_location=f'{location}\\Desktop\\other_test\\automation\\'
    auto_location=f'{location}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\'
    file_name=None
    print('name=',name)

    #to rememmber command line file name needed to be tested. so it each reboot will launch the same setting
    # as it is set at first by user
    for i in sys.argv:
        if '.py' in i:
            file_name=i

    if not os.path.exists(f'{script_location}{name}_rebooted.txt'):
        data=f'{script_location}venv\\Scripts\\activate.bat && pytest -vs {script_location}{file_name} --item={item}'
        print('name=',name)
        with open(f'{auto_location}run.bat','w') as f:
            f.write(data)
        with open(f'{script_location}{name}_rebooted.txt','w') as a:
            a.write('')
        # cmd('shutdown /r')
        pytest.skip('first reboot will not test the function.')
        exit()

    else:
        return False
        # os.unlink(f'{script_location}{name}_rebooted.txt')
        # os.unlink(f'{auto_location}run.bat')



# check if the test item has been tested or not.
def process_finish(name):
    location = os.path.expanduser('~')
    script_location = f'{location}\\Desktop\\other_test\\automation\\'
    auto_location = f'{location}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\'
    if not os.path.exists(f'{script_location}{name}_finish.txt'):
        with open(f'{script_location}{name}_finish.txt','w') as a:
            a.write('')
        return True
    else:
        # try:
        #     os.unlink(f'{auto_location}run.bat')
        # except:
        #     pass
        return False

class PreSetting:
    def __init__(self):
        self.bios_setting=[]
        self.name=None
        self.item=None

    def bios_set(self,content:list):
        self.bios_setting=content

    def bios_act(self):
        location = os.path.expanduser('~')
        script_location = f'{location}\\Desktop\\other_test\\automation\\'
        if not os.path.exists(f'{script_location}{self.name}_rebooted.txt'):
            act = bios_update.Action()
            # act.set_item('i219 Wake on LAN', 'Disabled', 'item')
            act.set_item(self.bios_setting[0], self.bios_setting[1], self.bios_setting[2])
            act.action()

    def func_set(self,name,item):
        self.name=name
        self.item=item

    def act(self):
        if self.item in ['all', self.name]:
            pass

        else:
            return [False,'The function is not selected.']
            # pytest.skip('The function is not selected.')

        #bios item update
        self.bios_act()
        _reboot = reboot(self.name, self.item)
        _process = process_finish(self.name)

        #launch first time reboot=none process=true
        #launch second time reboot=false process=true
        #launch third time reboot=false process=false
        if not _reboot and not _process:
            return [False, 'The function is finished, so skip']
            # pytest.skip('The function is finished, so skip')
        else:
            return [True,'']

# presetting=PreSetting()
# presetting.bios_set(['i219 Wake on LAN', 'Disabled', 'item'])
# presetting.func_set('name','item')
# presetting.act()

