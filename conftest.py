import pytest
import bios_update
def pytest_addoption(parser):
    parser.addoption('--item',action='store',default='all',help='input the function name you need to test, or input all for all items')

def pytest_generate_tests(metafunc):
    # print('all=',metafunc.fixturenames)

    option_value=metafunc.config.option.item
    # print('value=',option_value)
    if 'item' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize('item',[option_value])

@pytest.fixture(autouse=True)
def bios_load_default():
    bios = bios_update.Action()
    bios.set_item(None, None, 'default')
    bios.action()