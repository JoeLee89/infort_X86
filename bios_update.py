import os,pytest
from pprint import pprint
import subprocess
from abc import ABC, abstractmethod
from tools_manage import InstallManage
class BiosData:
    def __init__(self):
        self.data=[]
        self.title_name=None
        self.target_name=None
        self.folder_path = '.\\tool\\AMISCE'
        self.list=[]
        self.extract()



    def extract(self):
        if not os.path.exists(f'{self.folder_path}\\nvram.txt'):
            process = subprocess.Popen(f'{self.folder_path}\\SCEWIN_64.exe /o /s {self.folder_path}\\nvram.txt', shell=True,
                                       stdout=subprocess.PIPE)
            print(process.stdout.read())

        #save the default bios setting at first initial.
        if not os.path.exists(f'{self.folder_path}\\default.txt'):
            process = subprocess.Popen(f'{self.folder_path}\\SCEWIN_64.exe /o /s {self.folder_path}\\default.txt', shell=True,
                                       stdout=subprocess.PIPE)
            print(process.stdout.read())

    def set_title_name(self,name):
        self.title_name=name

    def set_target_name(self,name):
        self.target_name=name

    def update(self,visitor):
        # re=self.search(self.name)

        visitor.action(self)


    def search(self,type='value'):
        with open(f'{self.folder_path}\\nvram.txt') as f:
            self.data=f.readlines()
            # print(self.data)

        result=1
        #find the needed title first, then find the end of the item
        for num,i in enumerate(self.data):
            # print('data=',i)
            if self.title_name in i:
                # re=self.data.index(i)
                # when set type = item, check if data from self.data[re + 6:re + 6 + 4] contain the string
                # from self.target_name, and then result=1 for further usage.
                if type == 'item':
                    for item in self.data[num+6:num+6+4]:
                        if self.target_name in item:
                            result=1
                            break
                        else:
                            result=0
                            continue
                if result == 1:
                    for i in self.data[num:]:
                        if i != '\n':
                            self.list.append(i)
                        else:
                            break
                    print('result============')
                    print(self.data[:6] + self.list)
                    return self.data[:6] + self.list
            else:
                continue
        raise LookupError('Can not find the assigned title name in bios setting')




class Method(ABC):
    def __init__(self):
        self.folder_path = '.\\tool\\AMISCE'
        self.data=None
        self.start_location=None
        self.target_location=None

    @abstractmethod
    def action(self,data):
        pass

    def search_title(self):
        for i in self.data:
            if 'Value	=' in i:
                re=self.data.index(i)
                return re
            if 'Options	=' in i:
                re=self.data.index(i)
                return re
        return False

    def search_target(self,name):
        for i in self.data[self.start_location:]:
            if name in i:
                re=self.data.index(i)
                return re
        return False

    def write_file(self):
        print('Start writing the searched result to temp.txt for further usage.')
        with open(f'{self.folder_path}\\temp.txt','w') as f:
            for i in self.data:
                f.write(i)

    def save_to_bios(self):
        process=subprocess.Popen(f'{self.folder_path}\\SCEWIN_64.exe /i /s {self.folder_path}\\temp.txt', shell=True, stdout=subprocess.PIPE)
        # process=subprocess.Popen('', stdout=subprocess.PIPE)
        process.stdout.read()
        # print('aa=',re)
        # for i in iter(process.stdout.readline,''):
        #     print(i.decode('utf-8'))
        #     if not i:
        #         break

    def save_default_bios(self):
        process = subprocess.Popen(f'{self.folder_path}\\SCEWIN_64.exe /i /s {self.folder_path}\\default.txt', shell=True,
                                   stdout=subprocess.PIPE)
        process.stdout.read()




class ChangeItems(Method):
    def __init__(self):
        super().__init__()

    def action(self,datanode):
        self.data=datanode.search('item')
        self.start_location = self.search_title()
        self.target_location= self.search_target(datanode.target_name)
        # clear the string * first
        for i in range(self.start_location,len(self.data)):
            self.data[i]=self.data[i].replace('*','')
        # add the * to the target line in data list
        index=self.data[self.target_location].find('[')
        self.data[self.target_location]=self.data[self.target_location][:index]+'*'+self.data[self.target_location][index:]
        pprint(self.data)
        self.write_file()
        self.save_to_bios()



class ChangeValue(Method):
    def __init__(self):
        super().__init__()

    def action(self, datanode):
        self.data = datanode.search()
        self.start_location = self.search_title()
        #find both = and // string position
        index01 = self.data[self.start_location].find('=')
        index02 = self.data[self.start_location].find('//')
        # replace the original value to expected value based on the index01/02 position
        self.data[self.start_location] = self.data[self.start_location][:index01+1]+ datanode.target_name+self.data[self.start_location][index02:]
        pprint(self.data)
        self.write_file()
        self.save_to_bios()

class DefaultBios(Method):
    def __init__(self):
        super().__init__()

    def action(self, datanode):
        self.save_default_bios()


class Manager:
    def __init__(self):
        # confirm if the amisce folder exists, and copy all files to project folder
        result = InstallManage().set_name('amisce')
        if not result:
            pytest.skip('The AMISCE installation process is failed, so skip the test.')
        self.data = BiosData()

    def set_bios_title_item(self,name):
        self.data.set_title_name(name)

    def set_bios_target_item(self,name):
        self.data.set_target_name(name)

    def do_update(self,act):
        self.data.update(act)

        # act.action(self.data)


class Action:
    def __init__(self):
        self.title=''
        self.target=''
        self.type=''

    def set_item(self,title,target,type):
        self.title=title
        self.target=target
        self.type=type

    def action(self):
        lan=Manager()
        lan.set_bios_title_item(self.title)
        lan.set_bios_target_item(self.target)
        item_change=ChangeItems()
        value_change=ChangeValue()
        default_bios=DefaultBios()
        print('=======changing bios item=======')
        print('title=',self.title)
        print('target=',self.target)
        print('type=',self.type)
        print('================================')

        if self.type == 'item':
            lan.do_update(item_change)
        if self.type == 'value':
            lan.do_update(value_change)
        if self.type == 'default':
            lan.do_update(default_bios)

# act=Action()
# act.set_item('Quiet Boot1', '0','value')
# act.action()



act=Action()
act.set_item('RTC Wake system from S5', 'abc','item')
act.action()
#

# act=Action()
# act.set_item('Wake up minute', '2','value')
# act.action()

# act=Action()
# act.set_item('Wake up second', '<30>','value')
# act.action()

#
# act=Action()
# act.set_item('RTC Lock', 'Enabled','item')
# act.action()

#make bios load default
# act=Action()
# act.set_item(None, None,'default')
# act.action()

