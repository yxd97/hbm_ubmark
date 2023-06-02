import os
import sys
import argparse
from typing import List,Tuple

from utils import syscfg_utils
from utils import makefile_utils

CONNECTIVITIES = [
    'all2all',
    'grp4_all2all',
    'grp8_all2all',
    'one2all',
    'one2one'
]

ABS_ROOT = os.path.abspath(os.path.dirname(__file__))

def pinfo(*args, **kwargs):
    print("[INFO] ", *args, **kwargs, file=sys.stdout)

def pwarning(*args, **kwargs):
    print("[WARNING] ", *args, **kwargs, file=sys.stdout)

def perror(*args, **kwargs):
    print("[ERROR] ", *args, **kwargs, file=sys.stderr)

def echo_chdir(dir:str):
    pinfo(f'changing to directory {dir}')
    os.chdir(dir)

class TestCase:
    def __init__(self, connectivity:str, ntg:int, nch:int):
        if connectivity not in CONNECTIVITIES:
            perror(f'Unsupported connectivity: {connectivity}')
            raise ValueError(f'Unsupported connectivity: {connectivity}')
        self.connectivity = connectivity
        self.ntg = ntg
        self.nch = nch
        self.name = f'{connectivity}_{ntg}t{nch}c'
        self.project_root = self.name
        self.build_dir_name = 'build'
        self.output_dir_name = 'output'
        self.build_dir = os.path.join(self.project_root, self.build_dir_name)
        self.output_dir = os.path.join(self.project_root, self.output_dir_name)
        self.include_dir = os.path.join('..', '..', 'include') # relative to build dir
        self.floorplan = None

    def apply_floorplan(self, ntg_slrs:Tuple[int, int, int]):
        if len(ntg_slrs) != 3:
            raise ValueError('The number of SLRs must be 3.')
        if sum(ntg_slrs) != self.ntg:
            raise ValueError('The number of TGs in each SLR must sum up to the total number of TGs.')
        self.floorplan = ntg_slrs

    def create_sys_cfg(self):
        with open(os.path.join(self.build_dir, 'system.cfg'), 'w', newline='') as f:
            f.write(f"# Testcase: {self.name}\n")
            f.write('[connectivity]\n')
            f.writelines(syscfg_utils.generate_nk_tags(self.ntg))
            if self.floorplan is not None:
                f.writelines(syscfg_utils.generate_slr_tags(self.floorplan))
            f.writelines(syscfg_utils.generate_sp_tags(self.ntg, self.nch, self.connectivity))

    def create_makefile(self, board_repo_path:str, board_xsa:str):
        with open(os.path.join(self.build_dir, 'Makefile'), 'w', newline='') as f:
            f.write(f"# Testcase: {self.name}\n")
            f.writelines(makefile_utils.generate_baisc_config(board_repo_path, board_xsa))
            f.writelines(makefile_utils.generate_include_oclxcl(self.include_dir))
            f.writelines(makefile_utils.generate_dir_config(self.build_dir_name, self.output_dir_name))
            f.writelines(makefile_utils.generate_kernel_config('hbm_tg'))
            f.writelines(makefile_utils.generate_host_config(self.include_dir))
            f.writelines(makefile_utils.generate_emulation_config())
            f.writelines(makefile_utils.generate_build_targets(self.name))
            f.writelines(makefile_utils.generate_run_targets())
            f.writelines(makefile_utils.generate_clean_targets())

    def create_host_cpp(self):
        with open(os.path.join(self.build_dir, 'host.cpp'), 'w', newline='') as f:
            f.write(f"// Testcase: {self.name}\n")

    def create_build_files(self, board_repo_path:str, board_xsa:str):
        pinfo(f'Creating build files in {self.build_dir} ')
        os.makedirs(self.build_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        self.create_sys_cfg()
        self.create_makefile(board_repo_path, board_xsa)
        self.create_host_cpp()

    def build_test(self, no_host:bool=False):
        pinfo(f'Building test {self.name} ')
        echo_chdir(self.build_dir)
        if not no_host:
            os.system('make xclbin host')
        else:
            os.system('make xclbin')
        echo_chdir(ABS_ROOT)

    def run_test(self):
        pinfo(f'Running test {self.name} ')
        echo_chdir(self.build_dir)
        os.system('make run')
        echo_chdir(ABS_ROOT)

    def clean_logs(self):
        pinfo(f'Cleaning logs for {self.name} ')
        echo_chdir(self.build_dir)
        os.system('make clean')
        echo_chdir(ABS_ROOT)

    def delete_build(self):
        pinfo(f'Cleaning build temp files for {self.name} ')
        echo_chdir(self.build_dir)
        os.system('make cleanall')
        echo_chdir(ABS_ROOT)

    def delete_all(self):
        pinfo(f'Deleting all files for {self.name} ')
        os.system(f'rm -rf {self.project_root}')

#TODO: move them to a separate file (maybe json?)
WORK_DISTRIBUTION = {
    'zhang-21.ece.cornell.edu' : [
        TestCase('all2all', 32, 32),
        TestCase('one2one', 32, 32) ,
    ],
    'zhang-22.ece.cornell.edu' : [
        TestCase('grp4_all2all', 32, 32),
        TestCase('grp4_all2all', 16, 32),
    ],
    'zhang-23.ece.cornell.edu' : [
        TestCase('grp8_all2all', 32, 32),
        TestCase('grp8_all2all', 16, 32),
    ],
    'zhang-24.ece.cornell.edu' : [
        TestCase('one2all', 1, 1),
        TestCase('one2all', 1, 4),
        TestCase('one2all', 1, 8),
        TestCase('one2all', 1, 16),
        TestCase('one2all', 1, 32)
    ],
}
#TODO: move them to a separate file (maybe json?)
BORAD_REPO_PATH = '/work/shared/common/CAD_tool/xilinx/platforms/'
U280_XSA = 'xilinx_u280_xdma_201920_3'


def get_hostname():
    return os.uname()[1]

def main():
    parser = argparse.ArgumentParser(description='Test case generator')
    parser.add_argument(
        'option', type=str,
        choices=['setup', 'build', 'run', 'clean', 'cleanall', 'delete'],
        help = "setup: create build files; "
               "build: build the test case; "
               "run: run the test case; "
               "clean: clean the logs; "
               "cleanall: clean the logs and build temp files; "
               "delete: delete the test cases' outputs; "
    )
    args = parser.parse_args()

    hostname = get_hostname()
    if hostname not in WORK_DISTRIBUTION:
        perror(f'Unknown hostname: {hostname}. Please add it in the WORK_DISTRIBUTION dictionary.')
        return

    test_cases = WORK_DISTRIBUTION[hostname]
    for test_case in test_cases:
        try:
            if args.option == 'setup':
                if test_case.ntg == 32:
                    test_case.apply_floorplan((10,11,11))
                test_case.create_build_files(BORAD_REPO_PATH, U280_XSA)
            elif args.option == 'build':
                test_case.build_test(no_host=True)
            elif args.option == 'run':
                test_case.run_test()
            elif args.option == 'clean':
                test_case.clean_logs()
            elif args.option == 'cleanall':
                test_case.delete_build()
            elif args.option == 'delete':
                test_case.delete_all()
        except Exception as e:
            perror(f'Failed to execute "{args.option}" on test case {test_case.name} with exception: {e}')

if __name__ == '__main__':
    main()