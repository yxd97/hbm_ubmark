import os
import sys
from typing import List,Tuple

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils.syscfg_utils import *

CONNECTIVITIES = [
    'all2all',
    'grp4_all2all',
    'grp8_all2all',
    'one2all',
    'one2one'
]

def pinfo(*args, **kwargs):
    print("[INFO] ", *args, **kwargs, file=sys.stdout)

def pwarning(*args, **kwargs):
    print("[WARNING] ", *args, **kwargs, file=sys.stdout)

def perror(*args, **kwargs):
    print("[ERROR] ", *args, **kwargs, file=sys.stderr)

class TestCase:
    def __init__(self, connectivity:str, ntg:int, nch:int):
        if connectivity not in CONNECTIVITIES:
            perror(f'Unsupported connectivity: {connectivity}')
            raise ValueError(f'Unsupported connectivity: {connectivity}')
        self.connectivity = connectivity
        self.ntg = ntg
        self.nch = nch
        self.name = f'{connectivity}_{ntg}t{nch}c'
        abs_root_path = os.path.abspath(os.path.dirname(__file__))
        self.build_dir = os.path.join(abs_root_path, 'build_' + self.name)

    def apply_floorplan(self, ntg_slrs:Tuple[int, int, int]):
        if len(ntg_slrs) != 3:
            raise ValueError('The number of SLRs must be 3.')
        if sum(ntg_slrs) != self.ntg:
            raise ValueError('The number of TGs in each SLR must sum up to the total number of TGs.')
        self.floorplan = ntg_slrs

    def create_sys_cfg(self):
        with open(os.path.join(self.build_dir, 'system.cfg'), 'w', newline='') as f:
            f.write(f"# Testcase: {self.name}")
            f.write('[connectivity]\n')
            f.writelines(generate_nk_tags(self.ntg))
            if self.floorplan is not None:
                f.writelines(generate_slr_tags(self.floorplan))
            f.writelines(generate_sp_tags(self.ntg, self.nch, self.connectivity))

    def create_makefile(self):
        with open(os.path.join(self.build_dir, 'Makefile'), 'w', newline='') as f:
            f.write(f"# Testcase: {self.name}")

    def create_host_cpp(self):
        with open(os.path.join(self.build_dir, 'host.cpp'), 'w', newline='') as f:
            f.write(f"// Testcase: {self.name}")

    def create_build_files(self):
        pinfo(f'Creating build files in {self.build_dir}...')
        os.makedirs(self.build_dir, exist_ok=True)
        self.create_sys_cfg()
        self.create_makefile()
        self.create_host_cpp()

    def build_test(self, no_host:bool=False):
        pinfo(f'Building test {self.name}...')
        os.chdir(self.build_dir)
        if not no_host:
            os.system('make xclbin host')
        else:
            os.system('make xclbin')

    def run_test(self):
        pinfo(f'Running test {self.name}...')
        os.chdir(self.build_dir)
        os.system('make run')

WORK_DISTRIBUTION = {
    'zhang-21.ece.cornell.edu' : [TestCase('all2all', 32, 32),      TestCase('one2one', 32, 32)] ,
    'zhang-22.ece.cornell.edu' : [TestCase('grp4_all2all', 32, 32), TestCase('grp4_all2all', 16, 32)],
    'zhang-23.ece.cornell.edu' : [TestCase('grp8_all2all', 32, 32), TestCase('grp8_all2all', 16, 32)],
    'zhang-24.ece.cornell.edu' : [TestCase('one2all', 1, 1),        TestCase('one2all', 1, 4), TestCase('one2all', 1, 8), TestCase('one2all', 1, 16), TestCase('one2all', 1, 32)],
}

def get_hostname():
    return os.uname()[1]

def main():
    hostname = get_hostname()
    if hostname not in WORK_DISTRIBUTION:
        perror(f'Unknown hostname: {hostname}. Please add it in the WORK_DISTRIBUTION dictionary.')
        return

    test_cases = WORK_DISTRIBUTION[hostname]
    for test_case in test_cases:
        try:
            test_case.create_build_files()
            test_case.build_test()
            # test_case.run_test()
        except Exception as e:
            perror(f'Failed to build test case {test_case.name} with exception: {e}')

if __name__ == '__main__':
    main()