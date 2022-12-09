import pywinauto.element_info
from pywinauto.application import Application
import time,os,pytest
i=0


def filewriting(content):
    testresult = open('CrystalDiskMark_performance_result.csv', 'a')
    testresult.write(content)
    testresult.close()

def capture():
    global i
    global app
    img = app['CrystalDiskMark.*'].capture_as_image()
    img.save('ASSD_%s.jpg' %i)
    i+=1




def launchassd():
    global item
    global app
    for a in range(0,item-1):
        app['CrystalDiskMark.*']['ComboBox3'].select(a)

        app['CrystalDiskMark.*']['All'].click()
        time.sleep(1)
        try:
            if app['DiskMark64'].wait('exists', 5,1):
                app['DiskMark64']['Button'].click()
                continue
        except:
            pass
        app['Dialog']['Stop'].wait_not('enabled', 400, 5)

        hd_type = app['CrystalDiskMark.*']['ComboBox3'].ItemTexts()  # 回傳是字典，可以search 相關title去找key即可
        string = 'Device ' + ': ' + hd_type[a] + '\n'
        filewriting(string)

        Lable00 = app['CrystalDiskMark.*']['Button3'].texts()[0].replace('\n', '').replace('\r', '')
        Lable01 = app['CrystalDiskMark.*']['Button4'].texts()[0].replace('\n', '').replace('\r', '')
        Lable02 = app['CrystalDiskMark.*']['Button5'].texts()[0].replace('\n', '').replace('\r', '')
        Lable03 = app['CrystalDiskMark.*']['Button6'].texts()[0].replace('\n', '').replace('\r', '')
        read00_label = app['CrystalDiskMark.*']['Static'].texts()[0]
        read01_label = app['CrystalDiskMark.*']['Static2'].texts()[0]
        read02_label = app['CrystalDiskMark.*']['Static3'].texts()[0]
        read03_label = app['CrystalDiskMark.*']['Static4'].texts()[0]
        write00_label = app['CrystalDiskMark.*']['Static5'].texts()[0]
        write01_label = app['CrystalDiskMark.*']['Static6'].texts()[0]
        write02_label = app['CrystalDiskMark.*']['Static7'].texts()[0]
        write03_label = app['CrystalDiskMark.*']['Static8'].texts()[0]

        string = '(Read) ' + Lable00 + ', ' + read00_label+ '\n'
        filewriting(string)
        string = '(Read) ' + Lable01 + ', ' + read01_label + '\n'
        filewriting(string)
        string = '(Read) ' + Lable02 + ', ' + read02_label + '\n'
        filewriting(string)
        string = '(Read) ' + Lable03 + ', ' + read03_label + '\n'
        filewriting(string)

        string = '(Write) ' + Lable00 + ', ' + write00_label + '\n'
        filewriting(string)
        string = '(Write) ' + Lable01 + ', ' + write01_label + '\n'
        filewriting(string)
        string = '(Write) ' + Lable02 + ', ' + write02_label + '\n'
        filewriting(string)
        string = '(Write) ' + Lable03 + ', ' + write03_label + '\n'
        filewriting(string)
        # read_4k = app['CrystalDiskMark.*']['Static9'].get_properties()  # 回傳是字典，可以search 相關title去找key即可
        # print(read_4k['automation_id'], read_4k['texts'])
        # string = read_4k['automation_id'] + ': ' + str(read_4k['texts']).strip("[]''") + '\n'
        # filewriting(string)
        #
        # sync_4k_r = app['CrystalDiskMark.*']['Static13'].get_properties()  # 回傳是字典，可以search 相關title去找key即可
        # print(sync_4k_r['automation_id'], sync_4k_r['texts'])
        # string = sync_4k_r['automation_id'] + ': ' + str(sync_4k_r['texts']).strip("[]''") + '\n'
        # filewriting(string)
        #
        # access_time_r = app['CrystalDiskMark.*']['Static19'].get_properties()  # 回傳是字典，可以search 相關title去找key即可
        # print(access_time_r['automation_id'], access_time_r['texts'])
        # string = access_time_r['automation_id'] + ': ' + str(access_time_r['texts']).strip("[]''") + '\n'
        # filewriting(string)
        #
        # read_score_value = app['CrystalDiskMark.*']['Static2'].get_properties()  # 回傳是字典，可以search 相關title去找key即可
        # print(read_score_value['automation_id'], read_score_value['texts'])
        # string = read_score_value['automation_id'] + ': ' + str(read_score_value['texts']).strip("[]''") + '\n'
        # filewriting(string)
        #
        # seq_write_label = app['CrystalDiskMark.*']['Static12'].get_properties()  # 回傳是字典，可以search 相關title去找key即可
        # print(seq_write_label['automation_id'], seq_write_label['texts'])
        # string = seq_write_label['automation_id'] + ': ' + str(seq_write_label['texts']).strip("[]''") + '\n'
        # filewriting(string)
        #
        # write_4k = app['CrystalDiskMark.*']['Static7'].get_properties()  # 回傳是字典，可以search 相關title去找key即可
        # print(write_4k['automation_id'], write_4k['texts'])
        # string = write_4k['automation_id'] + ': ' + str(write_4k['texts']).strip("[]''") + '\n'
        # filewriting(string)
        #
        # async_4k_w = app['CrystalDiskMark.*']['Static11'].get_properties()  # 回傳是字典，可以search 相關title去找key即可
        # print(async_4k_w['automation_id'], async_4k_w['texts'])
        # string = async_4k_w['automation_id'] + ': ' + str(async_4k_w['texts']).strip("[]''") + '\n'
        # filewriting(string)
        #
        # access_time_w = app['CrystalDiskMark.*']['Static20'].get_properties()  # 回傳是字典，可以search 相關title去找key即可
        # print(access_time_w['automation_id'], access_time_w['texts'])
        # string = access_time_w['automation_id'] + ': ' + str(access_time_w['texts']).strip("[]''") + '\n'
        # filewriting(string)
        #
        # write_score_value = app['CrystalDiskMark.*']['Static4'].get_properties()  # 回傳是字典，可以search 相關title去找key即可
        # print(write_score_value['automation_id'], write_score_value['texts'])
        # string = write_score_value['automation_id'] + ': ' + str(write_score_value['texts']).strip("[]''") + '\n'
        # filewriting(string)
        #
        # score_value = app['CrystalDiskMark.*']['Static3'].get_properties()  # 回傳是字典，可以search 相關title去找key即可
        # print(score_value['automation_id'], score_value['texts'])
        # string = score_value['automation_id'] + ': ' + str(score_value['texts']).strip("[]''") + '\n'
        # filewriting(string)



        # capture()




def test_crystalmark():
    global item
    global app
    app = Application().start(cmd_line=r'..\tool\CrystalDiskMark\DiskMark64.exe')
    # app = Application().start(cmd_line=r'notepad.exe')
    # handle=pywinauto.findwindows.find_window(best_match='CrystalDiskMark')
    # app=Application().connect(handle=handle)
    app['CrystalDiskMark.*'].wait('exists',5)
    item = app['CrystalDiskMark.*']['ComboBox3'].item_count()
    # app['CrystalDiskMark'].menu_select('檔案(&F) -> 開新檔案(&N)	Ctrl+N')

    launchassd()











#app['CrystalDiskMark.*'].print_control_identifiers()

