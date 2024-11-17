# sys.path.insert(0, '../')

import main as lib
from main import Visualizator

instance = Visualizator('test_config.json')
instance.result = lib.Path(r'../trials/test_result.dot')
instance.debug_mode = False


def test_full_process_1():
    instance.package = 'https://pkgs.alpinelinux.org/package/edge/main/x86_64/busybox-binsh'
    assert instance.parse() == {'busybox': ['so:libc.musl-x86_64.so.1'], 'busybox-binsh': ['busybox'], 'musl': []}
    assert instance.graph_render() == True


def test_full_process_2():
    instance.package = 'https://pkgs.alpinelinux.org/package/edge/community/x86_64/vivid'
    assert instance.parse() == {'libgcc': ['so:libc.musl-x86_64.so.1'], 'musl': [],
                                'vivid': ['so:libc.musl-x86_64.so.1', 'so:libgcc_s.so.1']}
    assert instance.graph_render() == True


def test_set_dependencies_1():
    instance.package = 'https://pkgs.alpinelinux.org/package/edge/main/x86_64/busybox-binsh'
    assert instance.set_dependencies() == True


def test_set_dependencies_2():
    instance.package = 'https://pkgs.alpinelinux.org/package/edge/main/x86_64/busybox-binsh'
    instance.result = lib.Path(r'C:\Users\Inter\Desktip\fuckingShit!.dot')
    assert instance.set_dependencies() == False
