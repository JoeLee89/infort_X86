from abc import ABC,abstractmethod
import shutil
import os,re,time
import subprocess
import pywinauto
from pywinauto.application import Application

class SW:
    def __init__(self):
        # self.sour_url= 'c:\\tool\\'
        self.sour_url= 'C:\\tool\\'
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
        self.name='3dmark'
        try:
            with open(self.des_url+self.name+'\\'+ 'sn.txt') as file:
                self.reg=file.readlines()[0]
        except FileNotFoundError:
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
                re=self.registry()
                print('The installation is finished')
                return True if re else False
        else:
            return True

    def registry(self):
        process=subprocess.Popen(f'c:\\{self.name}\\3DMarkCmd.exe --register={self.reg}', stdout=subprocess.PIPE)
        reg_result=process.stdout.readlines()
        re=True
        for i in reg_result:
            mesg='could not get hashed key'
            if mesg in i.decode('utf8'):
               re=False

        if re:
            print('the registration is finished')
        else:
            print('The registration got something wrong.')
        return True



class Futuremark_PCMark(SW):
    def __init__(self):
        super().__init__()
        self.name='pcmark'
        try:
            with open(self.des_url+self.name+'\\'+ 'sn.txt') as file:
                self.reg=file.readlines()[0]
        except FileNotFoundError:
            self.reg='PCM10-TPRO-20230330-23H7Z-6S94D-4TSNE-T4USP'

    def install(self):
        if not self.check(self.name):
            try:
                shutil.copytree(self.sour_url + self.name, self.des_url+self.name)
            except Exception as a:
                print('can not find related files from the url.')
                print('Error as : ', a)
                return False
        if not os.path.exists('c:\\PCMark 10'):
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
        else:
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
        file_name = ''
        if not self.check(self.name):
            try:
                shutil.copytree(self.sour_url + self.name, self.des_url+self.name)
                # to get the burnin test file name
                file_name = self.search_file()
            except Exception as a:
                print('can not find related files from the url.')
                print('Error as : ', a)
                return False
            # # to get the burnin test file name
            # file_name=self.search_file()
        if file_name == '':
            print('Look like there is not related executable file in the folder. skip the installation.')
            return False
        if not os.path.exists('C:\\Program Files\\BurnInTest'):
            print('Please wait, while the installation is processing.')
            process=subprocess.Popen(self.des_url+self.name+'\\' + file_name + ' /verysilent /suppressmsgboxes',shell=True)
            re=process.wait()
            time.sleep(15)
            if re>0:
                print('The installation got something wrong.')
                return False
            else:
                print('the installation is finished')
                os.system('taskkill /F /IM bit.exe')
                self.registry()
                return True
        else:
            return True

    def registry(self):
        shutil.copy(self.sour_url + self.name + '\\' + 'key.dat', 'C:\\Program Files\\BurnInTest')
        if os.path.exists('C:\\Program Files\\BurnInTest\\key.dat'):
            print('the registration is finished')
        else:
            print('The registration got something wrong.')
            print('Can not get the key.dat file in the burnin test folder')


class HWinfo64(SW):
    def __init__(self):
        super().__init__()
        self.name = 'hwinfo64'

    def install(self):
        if not self.check(self.name):
            try:
                shutil.copytree(self.sour_url + self.name, self.des_url + self.name)
            except Exception as a:
                print('can not find related files from the url.')
                print('Error as : ', a)
                return False
        print('the installation is finished')
        return True


class Sleeper(SW):
    def __init__(self):
        super().__init__()
        self.name = 'sleeper'

    def install(self):
        if not self.check(self.name):
            try:
                shutil.copytree(self.sour_url + self.name, self.des_url + self.name)
            except Exception as a:
                print('can not find related files from the url.')
                print('Error as : ', a)
                return False
        print('the installation is finished')
        return True


class Amisce(SW):
    def __init__(self):
        super().__init__()
        self.name = 'amisce'

    def install(self):
        if not self.check(self.name):
            try:
                shutil.copytree(self.sour_url + self.name, self.des_url + self.name)
            except Exception as a:
                print('can not find related files from the url.')
                print('Error as : ', a)
                return False
        print('the installation is finished')
        return True

class Sandra(SW):
    def __init__(self):
        super().__init__()
        self.name='sandra'

    def search_file(self):
        file = os.listdir(r'.\tool\sandra')
        target = ''
        for i in file:
            try:
                target = re.search(r'(.*.exe)', i).group(1)
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
            print('Look like there is not related execute file in the .\\tool\\. skip the installation.')
            return False
        if not os.path.exists('C:\\Program Files\\SiSoftware'):
            print('Please wait, while the installation is processing.')
            process=subprocess.Popen(self.des_url+self.name+'\\' + file_name + ' /verysilent ',shell=True)
            re=process.wait()
            time.sleep(15)
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
        with open(f'{self.des_url}sandra\\sn.txt') as file:
            sn=file.readlines()
        app_path = 'C:\\Program Files\\SiSoftware'
        target_folder = os.listdir(app_path)
        app = Application().start(cmd_line=f'{app_path}\\{target_folder[0]}\\sandra.exe')
        try:
            app['Register'].wait('exists', 15)
            app['Register']['Edit'].type_keys(sn[0])
            app['Register'].type_keys('{ENTER}')
        except:
            pass

        try:
            app[u'Local Computer - SiSoftware Sandra'].wait('exists', timeout=10)
            print('the registration is finished')
            return True
        except (pywinauto.timings.TimeoutError, pywinauto.findbestmatch.MatchError):
            print('The registration got something wrong.')
            return False

        finally:
            app.kill()


class CrystalDiskMark(SW):
    def __init__(self):
        super().__init__()
        self.name='crystaldiskmark'

    def install(self):
        if not self.check(self.name):
            try:
                shutil.copytree(self.sour_url + self.name, self.des_url+self.name)
                print('the installation is finished')
                return True
            except Exception as a:
                print('can not find related files from the url.')
                print('Error as : ', a)
                return False
        print('the installation is finished')
        return True



class InstallManage:
    def __init__(self):
        self.sw=None

    @staticmethod
    def set_name(name):
        re=False
        if name == '3dmark':
            sw = Futuremark_ThreeDMark()
            re = sw.install()

        elif name == 'pcmark':
            sw = Futuremark_PCMark()
            re = sw.install()

        elif name=='sandra':
            sw = Sandra()
            re = sw.install()

        elif name=='burnintest':
            sw = Burnintest()
            re = sw.install()

        elif name=='hwinfo64':
            sw = HWinfo64()
            re = sw.install()

        elif name=='crystaldiskmark':
            sw = CrystalDiskMark()
            re = sw.install()

        elif name=='amisce':
            sw = Amisce()
            re = sw.install()

        elif name=='sleeper':
            sw = Sleeper()
            re = sw.install()

        return re


InstallManage().set_name('amisce')




