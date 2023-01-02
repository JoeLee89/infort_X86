import subprocess,os,sys,pytest,time, re
import bios_update
from abc import ABC,abstractmethod

def item_total_path():
    return re.search(r'(.*) \(call\)', os.getenv('PYTEST_CURRENT_TEST')).group(1)


def cmd(command):
    subp=subprocess.Popen(command,shell=True)
    # subp.wait(300)
    if subp.poll() != 0:
        print('Failed to launch the tool with the command.')


class Process(ABC):
    def __init__(self,data):
        self.data=data
        self.name=self.data.name
        self.path=self.data.path
        self.location=os.path.expanduser('~')
        self.bios_setting=self.data.bios
        # self.script_location=f'{self.location}\\Desktop\\other_test\\automation\\'
        self.script_location=f'{os.getcwd()}\\'
        self.temp_log_location='.\\temp\\'
        self.auto_location = f'{self.location}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\'


    @abstractmethod
    def act(self):
        pass


# class PreCheck(Process):
#     def __init__(self,data):
#         super().__init__(data)
#         self.next_duty=None
#
#     def set_deputy(self,deputy):
#         self.next_duty=deputy
#
#     def act(self):
#
#         if self.item in ['all', self.name]:
#             print('Assigned item=', self.item)
#             print('Function name=', self.name)
#             return self.next_duty.act()
#             # pytest.skip("Assigned item doesn't match, so skip the test")
#         else:
#             print('Assigned item=', self.item)
#             print('Function name=', self.name)
#             return [False, f'The function is not selected. so far the function={self.item}']


class Bios(Process):
    def __init__(self,data):
        super().__init__(data)
        self.next_duty=None
        self.bios=bios_update.Action()

    def bios_update_default(self):
        print('Start making BIOS load default first.')
        self.bios.set_item(None, None, 'default')
        self.bios.action()

    def set_duputy(self,deputy):
        self.next_duty=deputy

    def bios_set(self,content:list):
        self.bios_setting=content

    def act(self):
        if len(self.bios_setting[0]) == 0:
            print('bios setting has not been assigned, so skip bios update process')
            return self.next_duty.act()
        # if not os.path.exists(f'{self.script_location}{self.name}_rebooted.txt'):
        if not os.path.exists(f'{self.temp_log_location}{self.name}_rebooted.txt'):
            # act.set_item('i219 Wake on LAN', 'Disabled', 'item')
            self.bios_update_default()
            for bios_setting in self.bios_setting:
                self.bios.set_item(bios_setting[0], bios_setting[1], bios_setting[2])
                try:
                    self.bios.action()
                except LookupError:
                    pytest.skip('can not find the assigned BIOS title, so will skip the test.')

        return self.next_duty.act()


# reboot mainly check if the ***_rebooted.txt exists, if not then create file and reboot DUT
# it also help program to know if DUT is done to the reboot process or not.
# reboot process will create the run.bat file in strartup folder at the same time
# return false = reboot is finish.
class Reboot(Process):
    def __init__(self,data):
        super().__init__(data)
        self.next_duty=None

    def set_deputy(self,deputy):
        self.next_duty=deputy

    def act(self):
        file_name=None
        #to rememmber command line file name needed to be tested. so it each reboot will launch the same setting
        # as it is set at first by user
        for i in sys.argv:
            if '.py' in i:
                file_name=i

        # _data = f'{self.script_location}venv\\Scripts\\activate.bat && pytest -vs {self.script_location}{file_name} --item={self.item}'
        _data = f'{self.script_location}venv\\Scripts\\activate.bat && cd {self.script_location} && pytest -vs {self.path} --alluredir=.\\report '
        # if not os.path.exists(f'{self.script_location}{self.name}_rebooted.txt'):
        if not os.path.exists(f'{self.temp_log_location}{self.name}_rebooted.txt'):
            if len(self.bios_setting) > 0:

                with open(f'{self.auto_location}run.bat','w') as f:
                    f.write(_data)
                with open(f'{self.temp_log_location}{self.name}_rebooted.txt','w') as a:
                # with open(f'{self.script_location}{self.name}_rebooted.txt','w') as a:
                    a.write('')
                cmd('shutdown /r /t 1 /f')
                print(f'Test item={self.name}. Reboot first, Function will not test, while bios item is being changing')
                # pytest.skip(f'Test item={self.name}. First reboot will not test the function.')
                time.sleep(10)
                exit()
            else:
                with open(f'{self.temp_log_location}{self.name}_rebooted.txt','w') as a:
                    a.write('')
                    # return self.next_duty.act()

        else:
            print('Test item has rebooted before, so skip the reboot process.')
            # return self.next_duty.act()

            #if the test item has rebooted before, then should delete the run.bat batch file
            # try:
            #     os.unlink(f'{self.auto_location}run.bat')
            # except FileNotFoundError:
            #     print('There is no file in auto start folder.')


# check if the test item has been tested or not.
# class ProcessFinishConfirm(Process):
#
#     def act(self):
#         # if self.item in ['all', self.name]:
#         #     pass
#         #
#         # else:
#         #     return [False,f'The function is not selected. so far the function={self.item}']
#
#         if not os.path.exists(f'{self.script_location}{self.name}_finish.txt'):
#             with open(f'{self.script_location}{self.name}_finish.txt','w') as a:
#                 a.write('')
#             return [True]
#         else:
#             # try:
#             #     os.unlink(f'{auto_location}run.bat')
#             # except:
#             #     pass
#             return [False, 'The function is finished, so skip']
class Data:
    def __init__(self,path,name,bios):
        self._name = name
        self._path=path
        self._bios_setting = bios

    @property
    def bios(self):
        return self._bios_setting

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

class ActManage:
    def __init__(self,path,name):
        self.bios_setting = None
        self.name=name
        self.path=path

    def bios_set(self,value:list):
        self.bios_setting=value
        return self

    def act(self):
        data=Data(self.path,self.name,self.bios_setting)
        # precheck=PreCheck(data)
        bios=Bios(data)
        reboot = Reboot(data)
        # process_confirm=ProcessFinishConfirm(data)

        # precheck.set_deputy(bios)
        bios.set_duputy(reboot)
        bios.bios_set(self.bios_setting)
        # reboot.set_deputy(process_confirm)
        # return bios.act()
        bios.act()


# data = ActManage('abc', 'all')
# data.bios_set(['Quiet Boot1', '0','value']).act()
# print(data_re)

# data = ActManage('abc', 'all')
# data.bios_set([None, None, 'default']).act()
# print(re)

#won't be able to flash bios, and skip reboot if bios update data as [] none data
# data = ActManage('abc', 'all')
# data.bios_set([]).act()
# print(re)


# data = ActManage('abc', 'all')
# data.bios_set([[None, None, 'default'],
#                ['RTC Wake system from S5', 'Enabled','item'],
#                ['Wake up minute', '2','value']]).act()
