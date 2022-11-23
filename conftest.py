import pytest,items_collection,os

# def pytest_addoption(parser):
#     parser.addoption('--item',action='store',default='all',help='input the function name you need to test, or input all for all items')
#
# def pytest_generate_tests(metafunc):
#     # print('all=',metafunc.fixturenames)
#
#     option_value=metafunc.config.option.item
#     # print('value=',option_value)
#     if 'item' in metafunc.fixturenames and option_value is not None:
#         metafunc.parametrize('item',[option_value])
#
@pytest.fixture(scope='session',autouse=True)
def final():
    items_collection.data_collection()
    yield None
    with open('.\\test_item.txt','r') as file:
        re=file.readlines()
        if len(re) >0:
            items=re[0].replace('\n','')
            del re[0]
        else:
            os.unlink('.\\test_item.txt')
            pytest.exit('All test items are finished, so exit the test.')
    with open('.\\test_item.txt','w') as file:
        file.writelines(re)
    print('test item=', items)
    input('any eky')
    pytest.main(['-vs',items])
    # re=subprocess.Popen('pytest --co',stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # print(re.stdout.read())
