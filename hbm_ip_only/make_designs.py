from typing import List, Tuple, Dict
import os
import sys
sys.path.append('..')
from utils import hbm_ip_utils
from utils import vivado_utils
from datetime import datetime
import traceback

class TestCase:
    def __init__(
        self,
        mcs_enabled:List[int] = [0],
        saxi_enabled:List[int] = [0],
        board_repo:str = '/work/shared/users/phd/yd383/xilinx/boards'
    ) -> None:
        self.name = f'{len(mcs_enabled)}mc{len(saxi_enabled)}axi'
        self.mcs_enabled = mcs_enabled
        self.saxi_enabled = saxi_enabled
        self.build_dir = 'build_' + self.name
        self.report_dir = 'report'
        self.board_repo = board_repo

    def build_design(self):
        os.makedirs(self.build_dir, exist_ok=True)
        os.makedirs(self.report_dir, exist_ok=True)
        # generate tcl script
        os.system(f'cp make_design_template.tcl {self.build_dir}/make_design.tcl')
        lines = []
        with open(f'{self.build_dir}/make_design.tcl', 'r', newline='') as f:
            lines = f.readlines()

        insert_point = 1 + hbm_ip_utils.locate_insertion_point(lines, 'project path and anme settings')
        lines[insert_point:insert_point] = hbm_ip_utils.gen_tcl_path_settings(
            self.board_repo,
            os.path.abspath('.'),
            os.path.abspath(self.report_dir),
            self.build_dir
        )

        insert_point = 1 + hbm_ip_utils.locate_insertion_point(lines, 'AXI Interconnect property settings')
        lines[insert_point:insert_point] = hbm_ip_utils.gen_tcl_config_axiintercon_bd_cell(
            self.saxi_enabled
        )

        insert_point = 1 + hbm_ip_utils.locate_insertion_point(lines, 'HBM IP property settings')
        lines[insert_point:insert_point] = hbm_ip_utils.gen_tcl_config_hbmip_bd_cell(
            self.mcs_enabled,
            self.saxi_enabled
        )

        insert_point = 1 + hbm_ip_utils.locate_insertion_point(lines, 'AXI Interconnect to HBM IP SAXI connections')
        lines[insert_point:insert_point] = hbm_ip_utils.gen_tcl_connect_hbm(
            self.saxi_enabled
        )

        insert_point = 1 + hbm_ip_utils.locate_insertion_point(lines, 'Active low reset connections')
        lines[insert_point:insert_point] = hbm_ip_utils.gen_tcl_connect_reset(
            self.saxi_enabled
        )

        insert_point = 1 + hbm_ip_utils.locate_insertion_point(lines, 'HBM address allocation')
        lines[insert_point:insert_point] = hbm_ip_utils.gen_tcl_addr_map(
            self.mcs_enabled,
            self.saxi_enabled
        )
        with open(f'{self.build_dir}/make_design.tcl', 'w', newline='') as f:
            f.writelines(lines)

        # build design
        os.chdir(self.build_dir)
        err = os.system('vivado -mode batch -source make_design.tcl')
        if err != 0:
            raise RuntimeError(f'Vivado process failed with code {err}.')

    def collect_utilization_result(self):
        avail_on_device = vivado_utils.Utilization((0, 0), (0, 0), (0, 0), (0, 0), (0, 0))
        utilization = vivado_utils.UtilizationBreakdown()
        vivado_utils.read_full_util_report(
            f'{self.report_dir}/{self.name}_utilization.rpt',
            avail_on_device,
            utilization
        )
        return utilization.total


TEST_CASES = [
    TestCase(mcs_enabled=[0], saxi_enabled=[i for i in range(1)]),
    TestCase(mcs_enabled=[0], saxi_enabled=[i for i in range(2)]),
    TestCase(mcs_enabled=[0], saxi_enabled=[i for i in range(3)]),
    TestCase(mcs_enabled=[0], saxi_enabled=[i for i in range(4)]),
    TestCase(mcs_enabled=[0], saxi_enabled=[i for i in range(5)]),
    TestCase(mcs_enabled=[0], saxi_enabled=[i for i in range(6)]),
    TestCase(mcs_enabled=[0], saxi_enabled=[i for i in range(7)]),
    TestCase(mcs_enabled=[0], saxi_enabled=[i for i in range(8)]),
    TestCase(mcs_enabled=[i for i in range(1)], saxi_enabled=[0]),
    TestCase(mcs_enabled=[i for i in range(2)], saxi_enabled=[0]),
    TestCase(mcs_enabled=[i for i in range(3)], saxi_enabled=[0]),
    TestCase(mcs_enabled=[i for i in range(4)], saxi_enabled=[0]),
    TestCase(mcs_enabled=[i for i in range(5)], saxi_enabled=[0]),
    TestCase(mcs_enabled=[i for i in range(6)], saxi_enabled=[0]),
    TestCase(mcs_enabled=[i for i in range(7)], saxi_enabled=[0]),
    TestCase(mcs_enabled=[i for i in range(8)], saxi_enabled=[0]),
]

def main():
    curr_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    summary_file = f'summary_{curr_datetime}.rpt'
    for test_case in TEST_CASES:
        try:
            test_case.build_design()
            utilization = test_case.collect_utilization_result()
            with open(summary_file, 'a', newline='') as f:
                f.write(f'{test_case.name}\n')
                for k, v in utilization.__dict__.items():
                    f.write(f"    {k}: {v[0]} ({v[1] * 100:.2f}%)\n")
        except Exception as e:
            print(f"[ERROR] Test '{test_case.name}' failed with exception: {e}")
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    main()