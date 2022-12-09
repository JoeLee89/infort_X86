from abc import ABC,abstractmethod
import shutil
import os,re,time
import subprocess

class SW:
    def __init__(self):
        # self.sour_url= 'c:\\tool\\'
        self.sour_url= 'C:\\Users\\sc1x\\Desktop\\temp\\'
        self.des_url='.\\tool\\'

    def check(self,name):
        # sta00=os.path.exists(f'{self.des_url}{name}')
        # sta01=os.path.exists(f'{self.des_url}{name}')
        return True if os.path.exists(f'{self.des_url}{name}') else False

    def install(self):
        pass

class Futuremark_ThreeDMark(SW):
    def __init__(self):
        super().__init__()
        self.name='3DMark'
        self.reg='3DM-PICFT-3MJ7T-DCLLC-C9M6W-6NKME'

    def install(self):
        if not self.check(self.name):
            try:
                shutil.copytree(self.sour_url + self.name, self.des_url+self.name)
            except Exception as a:
                print('can not find related files from the url.')
                print('Error as : ', a)
                return False

        print('Please wait, while the installation is processing.')
        if not os.path.exists('c:\\3DMark'):
            process=subprocess.Popen(self.des_url+self.name+'\\'+'3dmark-setup.exe /installpath=c:\\ /install /silent',shell=True)
            re=process.wait()
            if re>0:
                print('The installation got something wrong.')
                return False
            else:
                print('the installation is finished')
                self.registry()
                return True
        else:
            return True


    def registry(self):
        process=subprocess.Popen(f'c:\\3DMark\\3DMarkCmd.exe --register={self.reg}')
        re=process.wait()
        # print('re=',re)
        if re>0:
            print('The registration got something wrong.')

        else:
            print('the registration is finished')

class Futuremark_PCMark(SW):
    def __init__(self):
        super().__init__()
        self.name='PCMark10'
        self.reg='PCM10-TPRO-20230330-23H7Z-6S94D-4TSNE-T4USP'

    def install(self):
        if not self.check(self.name):
            try:
                shutil.copytree(self.sour_url + self.name, self.des_url+self.name)
            except Exception as a:
                print('can not find related files from the url.')
                print('Error as : ', a)
                return False

        print('Please wait, while the installation is processing.')
        process=subprocess.Popen(self.des_url+self.name+'\\'+'pcmark10-setup.exe /installpath=c:\\ /install /silent',shell=True)
        re=process.wait()
        if re>0:
            print('The installation got something wrong.')
            return False
        else:
            print('the installation is finished')
            self.registry()
            return True


    def registry(self):
        process=subprocess.Popen(f'c:\\PCMark 10\\PCMark10Cmd.exe --register={self.reg}')
        re=process.wait()
        # print('re=',re)
        if re>0:
            print('The registration got something wrong.')

        else:
            print('the registration is finished')


class Burnintest(SW):
    def __init__(self):
        super().__init__()
        self.name='burnintest'

    def search_file(self):
        file = os.listdir(r'.\tool\burnintest')
        target = ''
        for i in file:
            try:
                target = re.search(r'(^bit.*.exe)', i).group(1)
            except:
                pass
        return target

    def install(self):
        if not self.check(self.name):
            try:
                shutil.copytree(self.sour_url + self.name, self.des_url+self.name)
            except Exception as a:
                print('can not find related files from the url.')
                print('Error as : ', a)
                return False

        file_name=self.search_file()
        if file_name == '':
            print('Look like there is not related execute file in the folder. skip the installation.')
            return False
        print('Please wait, while the installation is processing.')
        process=subprocess.Popen(self.des_url+self.name+'\\' + file_name + ' /verysilent /suppressmsgboxes',shell=True)
        re=process.wait()
        time.sleep(15)
        if re>0:
            print('The installation got something wrong.')
            return False
        else:
            print('the installation is finished')
            os.kill('bit.exe',)
            self.registry()
            return True


    def registry(self):
        shutil.copy(self.sour_url + self.name + 'key.dat','C:\\Program Files\\BurnInTest')
        if os.path.exists('C:\\Program Files\\BurnInTest\\key.dat'):
            print('the registration is finished')
        else:
            print('The registration got something wrong.')
            print('Can not get the key.dat file in the burnin test folder')


class InstallManage:
    def __init__(self):
        self.sw=None

    @staticmethod
    def set_name(name):
        if name == '3dmark':
            sw = Futuremark_ThreeDMark()
            re = sw.install()

        elif name == 'pcmark10':
            sw = Futuremark_PCMark()
            re = sw.install()

        elif name=='sandra':
            sw = Futuremark_PCMark()
            re = sw.install()

        elif name=='burnintest':
            sw = Burnintest()
            re = sw.install()

        return re


InstallManage().set_name('burnintest')




