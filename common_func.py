import subprocess,os,sys,pytest
import bios_update
from abc import ABC,abstractmethod

def cmd(command):
    subp=subprocess.Popen(command,shell=True)
    subp.wait(300)
    if subp.poll() != 0:
        print('Failed to launch the tool with the command.')


class Process(ABC):
    def __init__(self, name, item):
        self.name = name
        self.item = item
        self.location = os.path.expanduser('~')
        self.script_location = f'{self.location}\\Desktop\\other_test\\automation\\'
        self.auto_location = f'{self.location}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\'

    @abstractmethod
    def act(self):
        pass


class Bios(Process):
    def __init__(self, name, item):
        super().__init__(name, item)
        self.next_duty = None
        self.bios_setting = None

    def set_duputy(self, deputy):
        self.next_duty = deputy

    def bios_set(self, content: list):
        self.bios_setting = content

    def act(self):
        location = os.path.expanduser('~')
        script_location = f'{location}\\Desktop\\other_test\\automation\\'
        if len(self.bios_setting) == 0:
            print('bios setting has not been assigned, so skip bios update process')
            return self.next_duty.act()
        if not os.path.exists(f'{script_location}{self.name}_rebooted.txt'):
            act = bios_update.Action()
            # act.set_item('i219 Wake on LAN', 'Disabled', 'item')
            act.set_item(self.bios_setting[0], self.bios_setting[1], self.bios_setting[2])
            act.action()

        return self.next_duty.act()


# reboot mainly check if the ***_rebooted.txt exists, if not then create file and reboot DUT
# it also help program to know if DUT is done to the reboot process or not.
# reboot process will create the run.bat file in strartup folder at the same time
# return false = reboot is finish.
class Reboot(Process):
    def __init__(self, name, item):
        super().__init__(name, item)
        self.next_duty = None

    def set_deputy(self, deputy):
        self.next_duty = deputy

    def act(self):
        file_name = None
        # to rememmber command line file name needed to be tested. so it each reboot will launch the same setting
        # as it is set at first by user
        for i in sys.argv:
            if '.py' in i:
                file_name = i

        if not os.path.exists(f'{self.script_location}{self.name}_rebooted.txt'):
            data = f'{self.script_location}venv\\Scripts\\activate.bat && pytest -vs {self.script_location}{file_name} --item={self.item}'
            with open(f'{self.auto_location}run.bat', 'w') as f:
                f.write(data)
            with open(f'{self.script_location}{self.name}_rebooted.txt', 'w') as a:
                a.write('')
            # cmd('shutdown /r')
            pytest.skip(f'Test item={self.name}. First reboot will not test the function.')
            exit()

        else:
            return self.next_duty.act()
        #     return False
        # os.unlink(f'{script_location}{name}_rebooted.txt')
        # os.unlink(f'{auto_location}run.bat')


# check if the test item has been tested or not.
class ProcessFinishConfirm(Process):

    def act(self):
        if self.item in ['all', self.name]:
            pass

        else:
            return [False, 'The function is not selected.']

        if not os.path.exists(f'{self.script_location}{self.name}_finish.txt'):
            with open(f'{self.script_location}{self.name}_finish.txt', 'w') as a:
                a.write('')
            return [True]
        else:
            # try:
            #     os.unlink(f'{auto_location}run.bat')
            # except:
            #     pass
            return [False, 'The function is finished, so skip']


class Data:
    def __init__(self):
        self.name = None
        self.item = None
        self.bios_setting = []

    def bios_set(self, value: list):
        self.bios_setting = value

    def set_name_item(self, name, item):
        self.name = name
        self.item = item

    def act(self):
        bios = Bios(self.name, self.item)
        reboot = Reboot(self.name, self.item)
        process_confirm = ProcessFinishConfirm(self.name, self.item)

        bios.set_duputy(reboot)
        bios.bios_set(self.bios_setting)
        reboot.set_deputy(process_confirm)
        return bios.act()


# data = Data()
# data.set_name_item('abc', 'all')
# data.bios_set([None, None, 'default'])
# re = data.act()
# print(re)
