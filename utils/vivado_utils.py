from typing import List,Tuple, Dict
import os
from dataclasses import dataclass
import sys
sys.path.append('.')
from logging_utils import pwarning

def check_design_status(output_dir:str) -> str:
    finished_runs = []
    for f in os.listdir(os.path.join(output_dir, 'link/imp')):
        if f.startswith('impl_1_full_util') and f.endswith('.rpt'):
            run = f.split('impl_1_full_util_')[-1].split('.rpt')[0]
            finished_runs.append(run)
    if 'routed' in finished_runs:
        return 'routed'
    if 'placed' in finished_runs:
        return 'placed'
    if 'synthed' in finished_runs:
        return 'synthed'
    return 'not_implemented'

def gen_tcl_collect_results(project_root:str, build_dir:str, output_dir:str) -> Dict[str, str]:
    reports = {}
    project_status = check_design_status(output_dir)
    if project_status ==  'not_implemented':
        raise ValueError(f"Project is in status '{project_status}', implementation results are not available.")
    if project_status == 'synthed':
        pwarning(f"Project is in status '{project_status}', timing results are not available, utilization results are not accurate.")
        reports['full_util'] = os.path.abspath(os.path.join(output_dir, 'link/imp/impl_1_full_util_synthed.rpt'))
        reports['kernel_util'] = os.path.abspath(os.path.join(output_dir, 'link/imp/impl_1_kernel_util_synthed.rpt'))
        reports['static_region_util'] = os.path.abspath(os.path.join(output_dir, 'link/imp/impl_1_static_region_util_synthed.rpt'))
    if project_status == 'placed':
        pwarning(f"Project is in status '{project_status}', timing results are not available.")
        reports['full_util'] = os.path.abspath(os.path.join(output_dir, 'link/imp/impl_1_full_util_placed.rpt'))
        reports['kernel_util'] = os.path.abspath(os.path.join(output_dir, 'link/imp/impl_1_kernel_util_placed.rpt'))
    if project_status == 'routed':
        reports['full_util'] = os.path.abspath(os.path.join(output_dir, 'link/imp/impl_1_full_util_routed.rpt'))
        reports['kernel_util'] = os.path.abspath(os.path.join(output_dir, 'link/imp/impl_1_kernel_util_routed.rpt'))
        reports['timing'] = os.path.abspath(os.path.join(output_dir, 'imp/timing.rpt'))
    with open(os.path.join(project_root, 'report_results.tcl'), 'w', newline='') as f:
        # open implemented design
        f.write("open_project prj.xpr\n")
        f.write("open_runs impl_1\n")
        # report timing
        f.write(f"report_timing_summary -no_detailed_paths -setup -hold -unique_pins -no_header -file {timing_report_file}\n")
    return reports

def gen_tcl_report_utilization(self):
    pinfo(f'Reporting utilization for {self.name} ')
    vpl_prj_dir = os.path.join(self.build_dir, 'link_hw/link/vivado/vpl/prj')
    echo_chdir(self.build_dir)
    with open('report_util.tcl', 'w', newline='') as f:
        f.write("open_project prj.xpr\n")
        f.write("open_runs impl_1\n")
        f.write("report_utilization -file hmss_util.rpt -cells [get_cells -hierarchical -regexp .*hmss_0]\n")
    os.system('make report')
    echo_chdir(ABS_ROOT)

def gen_tcl_report_timing(project_dir:str):


def generate_report_files(output_dir:str):
    pass

@dataclass
class TimingResult:
    status:str
    clock:str
    target:float
    worst_negative_setup_slack:float
    worst_negative_hold_slack:float

@dataclass
class UtilizationResult:
    lut:Tuple[int, float]
    ff:Tuple[int, float]
    bram:Tuple[int, float]
    uram:Tuple[int, float]
    dsp:Tuple[int, float]

class UtilizationBreakdown:
    def __init__(self, report_file:str):
        self.total = UtilizationResult((0, 0), (0, 0), (0, 0), (0, 0), (0, 0))
        self.breakdown = {
            'static_region': UtilizationResult((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
            'hmss': UtilizationResult((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
            'kernels': UtilizationResult((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
            'others': UtilizationResult((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
        }


def get_timing_results(report_file:str) -> TimingResult:
    return TimingResult('', '', 0, 0, 0)