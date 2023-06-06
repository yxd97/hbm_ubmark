from typing import List,Tuple, Dict
import os
from dataclasses import dataclass
import sys
import re

def pinfo(*args, **kwargs):
    print("[INFO] ", *args, **kwargs, file=sys.stdout)

def pwarning(*args, **kwargs):
    print("[WARNING] ", *args, **kwargs, file=sys.stdout)

def perror(*args, **kwargs):
    print("[ERROR] ", *args, **kwargs, file=sys.stderr)

def echo_chdir(dir:str):
    pinfo(f'changing to directory {dir}')
    os.chdir(dir)

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

def collect_reports(abs_root:str, build_dir:str, output_dir:str) -> Dict[str, str]:
    reports = {}
    project_status = check_design_status(output_dir)
    # check if the design has been implemented
    if project_status ==  'not_implemented':
        raise ValueError(f"Project is in status '{project_status}', implementation results are not available.")
    # define report files
    if project_status == 'synthed':
        pwarning(f"Project is in status '{project_status}', timing results are not available, utilization results are not accurate.")
        reports['full_util'] = os.path.abspath(os.path.join(output_dir, 'link/report/full_util_synthed.rpt'))
        reports['kernel_util'] = os.path.abspath(os.path.join(output_dir, 'link/report/kernel_util_synthed.rpt'))
        reports['static_region_util'] = os.path.abspath(os.path.join(output_dir, 'link/report/sr_util_synthed.rpt'))
        reports['hmss_util'] = os.path.abspath(os.path.join(output_dir, 'link/report/hmss_util_synthed.rpt'))
    if project_status == 'placed':
        pwarning(f"Project is in status '{project_status}', timing results are not available.")
        reports['full_util'] = os.path.abspath(os.path.join(output_dir, 'link/report/full_util_placed.rpt'))
        reports['kernel_util'] = os.path.abspath(os.path.join(output_dir, 'link/report/kernel_util_placed.rpt'))
        reports['static_region_util'] = os.path.abspath(os.path.join(output_dir, 'link/report/sr_util_placed.rpt'))
        reports['hmss_util'] = os.path.abspath(os.path.join(output_dir, 'link/report/hmss_util_placed.rpt'))
    if project_status == 'routed':
        reports['full_util'] = os.path.abspath(os.path.join(output_dir, 'link/report/full_util_routed.rpt'))
        reports['kernel_util'] = os.path.abspath(os.path.join(output_dir, 'link/report/kernel_util_routed.rpt'))
        reports['static_region_util'] = os.path.abspath(os.path.join(output_dir, 'link/report/sr_util_routed.rpt'))
        reports['hmss_util'] = os.path.abspath(os.path.join(output_dir, 'link/report/hmss_util_routed.rpt'))
        reports['timing'] = os.path.abspath(os.path.join(output_dir, 'link/report/timing.rpt'))
    # copy existing reports to be tracked by git
    os.makedirs(os.path.join(output_dir, 'link/report'), exist_ok=True)
    for rpt in ['full_util', 'kernel_util']:
        dest = reports[rpt]
        src = os.path.basename(dest)
        src = "impl_1_" + src
        src = os.path.abspath(os.path.join(output_dir, 'link/imp', src))
        os.system(f'cp {src} {dest}')
    # generate other reports
    vpl_dir = os.path.join(build_dir, 'link_hw/link/vivado/vpl/prj')
    with open(os.path.join(vpl_dir, 'report_results.tcl'), 'w', newline='') as f:
        # open implemented design
        f.write("open_project prj.xpr\n")
        if project_status == 'synthed':
            f.write("open_run my_rm_synth_1\n")
        else:
            f.write("open_run impl_1\n")
        # report timing
        if project_status != 'synthed':
            f.write(f"report_timing_summary -no_detailed_paths -setup -hold -unique_pins -no_header -file {reports['timing']}\n")
        # report utilization
        f.write(f"report_utilization -file {reports['static_region_util']} -hierarchical -hierarchical_percentages -hierarchical_depth 2\n")
        f.write(f"report_utilization -file {reports['hmss_util']} -cells [get_cells -hierarchical -regexp .*hmss_0] -hierarchical -hierarchical_percentages -hierarchical_depth 1\n")
    echo_chdir(vpl_dir)
    err = os.system('vivado -mode batch -source report_results.tcl')
    if err != 0:
        raise RuntimeError(f"Vivado returned error code {err} when generating reports.")
    echo_chdir(abs_root)
    for k, v in reports.items():
        if os.path.exists(v):
            pinfo(f"Successfully generated report for {k}: {v}.")
        else:
            perror(f"Failed to generate report for {k}: {v}.")
    return reports

@dataclass
class ClockTiming:
    level:int
    status:str
    frequency:float
    wns:float
    whs:float

    def update_status(self):
        if self.wns < 0 and self.whs < 0:
            self.status = 'setup & hold violation'
        elif self.wns < 0:
            self.status = 'setup violation'
        elif self.whs < 0:
            self.status = 'hold violation'
        else:
            self.status = 'met'

class TimingResult:
    def __init__(self) -> None:
        self.hbm_clk = ClockTiming('', 0, '', 0, 0)
        self.kernel_clk = ClockTiming('', 0, '', 0, 0)
        self.kernel_clk2 = ClockTiming('', 0, '', 0, 0)
        self.other_clks:Dict[str: ClockTiming] = {}

    def print_results(self):
        print(f"HBM clock {self.hbm_clk.frequency} MHz: {self.hbm_clk.status}, WNS: {self.hbm_clk.wns} ns, WHS: {self.hbm_clk.whs} ns")
        print(f"Kernel clock {self.kernel_clk.frequency} MHz: {self.kernel_clk.status}, WNS: {self.kernel_clk.wns} ns, WHS: {self.kernel_clk.whs} ns")
        print(f"Kernel clock2 {self.kernel_clk2.frequency} MHz: {self.kernel_clk2.status}, WNS: {self.kernel_clk2.wns} ns, WHS: {self.kernel_clk2.whs} ns")
        print("Other clocks:")
        for k, v in self.other_clks.items():
            print(f"{k} {v.frequency} MHz: {v.status}, WNS: {v.wns} ns, WHS: {v.whs} ns")

def read_clock_level(line:str, nspaces:int = 2) -> int:
    indent = 0
    for c in line:
        if c == ' ':
            indent += 1
        else:
            break
    return indent // nspaces

def locate_table(lines:List[str], pattern:str, start:int = 0, advancement:int = 6) -> int:
    ptr = start
    for i in range(ptr, len(lines)):
        if lines[i].startswith(pattern):
            ptr = i + advancement
            # print(f"Located table '{pattern}' at line {ptr}")
            return ptr
        i += 1
    return ptr

def get_timing_results(report_file:str) -> TimingResult:
    result = TimingResult()
    lines = []
    with open(report_file, 'r') as f:
        lines = f.readlines()
    ptr = 0

    # read clock summary
    ptr = locate_table(lines, '| Clock Summary', ptr)
    # clock,waveform,waveform,period,frequency
    for i in range(ptr, len(lines)):
        line = lines[i].rstrip()
        if line == '':
            ptr = i
            break
        clk_level = read_clock_level(line)
        line = line.lstrip()
        line = re.sub('\s+', ' ', line)
        fields = line.split(' ')
        name = fields[0]
        if clk_level != 1:
            # pwarning(f"Ignoring level {clk_level} clock {name}")
            continue
        if name == 'clk_out1_pfm_top_clkwiz_hbm_aclk_0':
            result.hbm_clk.level = clk_level
            result.hbm_clk.frequency = float(fields[4])
        elif name == 'clk_out1_pfm_top_clkwiz_kernel_0':
            result.kernel_clk.level = clk_level
            result.kernel_clk.frequency = float(fields[4])
        elif name == 'clk_out1_pfm_top_clkwiz_kernel2_0':
            result.kernel_clk2.level = clk_level
            result.kernel_clk2.frequency = float(fields[4])
        else:
            clk = ClockTiming(clk_level, '', float(fields[4]), 0, 0)
            result.other_clks[name] = clk
        i += 1

    # read intra clock table
    ptr = locate_table(lines, '| Intra Clock Table', ptr)
    # clock,WNS(ns),TNS(ns),TNS Failing Endpoints,TNS Total Endpoints,WHS(ns),THS(ns),THS Failing Endpoints,THS Total Endpoints,WPWS(ns),TPWS(ns),TPWS Failing Endpoints,TPWS Total Endpoints
    for i in range(ptr, len(lines)):
        line = lines[i].strip()
        if line == '':
            ptr = i
            break
        line = re.sub('\s+', ' ', line)
        fields = line.split(' ')
        name = fields[0]
        if len(fields) != 13:
            pwarning(f"Ignoring constraint-free clock {name}.")
            continue
        if name == 'clk_out1_pfm_top_clkwiz_hbm_aclk_0':
            result.hbm_clk.wns = float(fields[1])
            result.hbm_clk.whs = float(fields[5])
            result.hbm_clk.update_status()
        elif name == 'clk_out1_pfm_top_clkwiz_kernel_0':
            result.kernel_clk.wns = float(fields[1])
            result.kernel_clk.whs = float(fields[5])
            result.kernel_clk.update_status()
        elif name == 'clk_out1_pfm_top_clkwiz_kernel2_0':
            result.kernel_clk2.wns = float(fields[1])
            result.kernel_clk2.whs = float(fields[5])
            result.kernel_clk2.update_status()
        elif name in result.other_clks:
            result.other_clks[name].wns = float(fields[1])
            result.other_clks[name].whs = float(fields[5])
            result.other_clks[name].update_status()
        i += 1
    return result

@dataclass
class Utilization:
    lut:Tuple[float, float]
    ff:Tuple[float, float]
    bram:Tuple[float, float]
    uram:Tuple[float, float]
    dsp:Tuple[float, float]

    def print_results(self, indent:int = 0):
        indent_str = ' ' * indent
        print(indent_str + f"LUT: {self.lut[0]} ({self.lut[1] * 100:.2f}%)", end = '\t')
        print(f"FF: {self.ff[0]} ({self.ff[1] * 100:.2f}%)", end = '\t')
        print(f"BRAM: {self.bram[0]} ({self.bram[1] * 100:.2f}%)", end = '\t')
        print(f"URAM: {self.uram[0]} ({self.uram[1] * 100:.2f}%)", end = '\t')
        print(f"DSP: {self.dsp[0]} ({self.dsp[1] * 100:.2f}%)")

    def export_csv(self) -> str:
        s = ''
        s += f"{self.lut[0]} ({self.lut[1] * 100:.2f}%), "
        s += f"{self.ff[0]} ({self.ff[1] * 100:.2f}%), "
        s += f"{self.bram[0]} ({self.bram[1] * 100:.2f}%), "
        s += f"{self.uram[0]} ({self.uram[1] * 100:.2f}%), "
        s += f"{self.dsp[0]} ({self.dsp[1] * 100:.2f}%)"
        return s

class UtilizationBreakdown:
    def __init__(self):
        self.total = Utilization((0, 0), (0, 0), (0, 0), (0, 0), (0, 0))
        self.breakdown = {
            'kernels': Utilization((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
            'hmss': Utilization((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
            'static_region': Utilization((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
            'others': Utilization((0, 0), (0, 0), (0, 0), (0, 0), (0, 0)),
        }

    def print_results(self):
        print('Overall utilization:')
        self.total.print_results(indent = 2)
        print('Breakdown:')
        for k, v in self.breakdown.items():
            print(f"  {k}")
            v.print_results(indent = 4)


def parse_total_util_table_line(
    start:int, lines:List[str], keywords:List[str],
    avail_on_device:Utilization, results:UtilizationBreakdown
):
    FULLUTIL_ATTR_LOOKUP = {
        'CLB LUTs': 'lut',
        'CLB Registers': 'ff',
        'Block RAM Tile': 'bram',
        'URAM': 'uram',
        'DSPs': 'dsp'
    }
    finished = {k:False for k in keywords}
    for line in lines[start:]:
        line = re.sub(r'\|', '', line.strip())
        line = re.sub(r'\s\s+', ',', line.strip())
        fields = line.split(',')
        if fields[0] in keywords and not finished[fields[0]]:
            avail = float(fields[3])
            used = float(fields[1])
            setattr(avail_on_device, FULLUTIL_ATTR_LOOKUP[fields[0]], (avail, 1.0))
            setattr(results.total, FULLUTIL_ATTR_LOOKUP[fields[0]], (used, used / avail))
            finished[fields[0]] = True
        if all(finished.values()):
            return

def parse_kernel_util_table_line(
    start:int, lines:List[str], inst_names:List[str],
    avail_on_device:Utilization, results:UtilizationBreakdown
):
    KERNELUTIL_ATTR_LOOKUP = {
        'lut': 1,
        'ff': 3,
        'bram': 4,
        'uram': 5,
        'dsp': 6
    }
    finished = {k:False for k in inst_names}
    lut = 0
    ff = 0
    bram = 0
    uram = 0
    dsp = 0
    for line in lines[start:]:
        line = re.sub(r'\|', '', line.strip())
        line = re.sub(r'\[\s+\d+\.\d+\%\]', '', line.strip())
        line = re.sub(r'\s\s+', ',', line)
        fields = line.split(',')
        if fields[0] in inst_names and not finished[fields[0]]:
            lut += float(fields[KERNELUTIL_ATTR_LOOKUP['lut']])
            ff += float(fields[KERNELUTIL_ATTR_LOOKUP['ff']])
            bram += float(fields[KERNELUTIL_ATTR_LOOKUP['bram']])
            uram += float(fields[KERNELUTIL_ATTR_LOOKUP['uram']])
            dsp += float(fields[KERNELUTIL_ATTR_LOOKUP['dsp']])
            finished[fields[0]] = True
        if all(finished.values()):
            break
    results.breakdown['kernels'].lut = (lut, lut / avail_on_device.lut[0])
    results.breakdown['kernels'].ff = (ff, ff / avail_on_device.ff[0])
    results.breakdown['kernels'].bram = (bram, bram / avail_on_device.bram[0])
    results.breakdown['kernels'].uram = (uram, uram / avail_on_device.uram[0])
    results.breakdown['kernels'].dsp = (dsp, dsp / avail_on_device.dsp[0])

def parse_hier_util_table_line(
    start:int, lines:List[str], inst_names:List[str],
    avail_on_device:Utilization, results:UtilizationBreakdown,
    result_key:str
):
    HIERUTIL_ATTR_LOOKUP = {
        'lut': 4,
        'ff': 8,
        'bram': 9,
        'uram': 11,
        'dsp': 12
    }
    finished = {k:False for k in inst_names}
    lut = 0
    ff = 0
    bram = 0
    uram = 0
    dsp = 0
    for line in lines[start:]:
        line = re.sub(r'\(\d+\.\d+\%\)', '', line.strip())
        line = re.sub(r'\|', ',', line.strip('|'))
        fields = line.split(',')
        inst_name = fields[0].strip()
        if inst_name in inst_names and not finished[inst_name]:
            lut += float(fields[HIERUTIL_ATTR_LOOKUP['lut']])
            ff += float(fields[HIERUTIL_ATTR_LOOKUP['ff']])
            bram += float(fields[HIERUTIL_ATTR_LOOKUP['bram']]) # for RAMB36
            bram += float(fields[HIERUTIL_ATTR_LOOKUP['bram'] + 1]) * 0.5 # for RAMB18
            uram += float(fields[HIERUTIL_ATTR_LOOKUP['uram']])
            dsp += float(fields[HIERUTIL_ATTR_LOOKUP['dsp']])
            finished[inst_name] = True
        if all(finished.values()):
            break
    results.breakdown[result_key].lut = (lut, lut / avail_on_device.lut[0])
    results.breakdown[result_key].ff = (ff, ff / avail_on_device.ff[0])
    results.breakdown[result_key].bram = (bram, bram / avail_on_device.bram[0])
    results.breakdown[result_key].uram = (uram, uram / avail_on_device.uram[0])
    results.breakdown[result_key].dsp = (dsp, dsp / avail_on_device.dsp[0])


def get_utilization_breakdown(report_files:Dict[str, str]) -> UtilizationBreakdown:
    results = UtilizationBreakdown()
    # read full util report
    available_on_device = Utilization((0, 1), (0, 1), (0, 1), (0, 1), (0, 1))
    lines = []
    with open(report_files['full_util'], 'r') as f:
        lines = f.readlines()
    ptr = 31 # get rid of the table of contents
    # find CLB Logic Table to get LUT and FF metrics
    ptr = locate_table(lines, '1. CLB Logic', ptr)
    parse_total_util_table_line(ptr, lines, ['CLB LUTs', 'CLB Registers'], available_on_device, results)
    # find BLOCKRAM table to get BRAM and URAM metrics
    ptr = locate_table(lines, '3. BLOCKRAM', ptr)
    parse_total_util_table_line(ptr, lines, ['Block RAM Tile', 'URAM'], available_on_device, results)
    # find ARITHMETIC table to get DSP metrics
    ptr = locate_table(lines, '4. ARITHMETIC', ptr)
    parse_total_util_table_line(ptr, lines, ['DSPs'], available_on_device, results)

    # read kernels report
    with open(report_files['kernel_util'], 'r') as f:
        lines = f.readlines()
    ptr = 17 # get rid of the table of contents
    # find system utilization table
    ptr = locate_table(lines, '1. System Utilization', ptr)
    parse_kernel_util_table_line(ptr, lines, ['hbm_tg'], available_on_device, results)

    # read hmss report
    with open(report_files['hmss_util'], 'r') as f:
        lines = f.readlines()
    ptr = 17 # get rid of the table of contents
    # find utilization by hierarchiy table
    ptr = locate_table(lines, '1. Utilization by Hierarchy', ptr)
    parse_hier_util_table_line(ptr, lines, ['hmss_0'], available_on_device, results, 'hmss')

    # read static region report
    with open(report_files['static_region_util'], 'r') as f:
        lines = f.readlines()
    ptr = 17 # get rid of the table of contents
    # find utilization by hierarchiy table
    ptr = locate_table(lines, '1. Utilization by Hierarchy', ptr)
    parse_hier_util_table_line(ptr, lines, ['static_region'], available_on_device, results, 'static_region')

    # calculate the rest
    TYPE_OF_RESOURCE = ['lut', 'ff', 'bram', 'uram', 'dsp']
    for rsc in TYPE_OF_RESOURCE:
        total = getattr(results.total, rsc)[0]
        kernel = getattr(results.breakdown['kernels'], rsc)[0]
        hmss = getattr(results.breakdown['hmss'], rsc)[0]
        static_region = getattr(results.breakdown['static_region'], rsc)[0]
        other = total - kernel - hmss - static_region
        other_percent = other / getattr(available_on_device, rsc)[0]
        setattr(results.breakdown['others'], rsc, (other, other_percent))

    return results

if __name__ == '__main__':
    trpt = '/home/yd383/hbm_ubmark/one2all_1t1c/output/link/report/timing.rpt'
    timing_results = get_timing_results(trpt)
    timing_results.print_results()
    hbm_timing = f'{timing_results.hbm_clk.frequency} MHz'
    kernel_timing = f'{timing_results.kernel_clk.frequency} MHz'
    furpt = '/home/yd383/hbm_ubmark/one2all_1t1c/output/link/report/full_util_routed.rpt'
    kurpt = '/home/yd383/hbm_ubmark/one2all_1t1c/output/link/report/kernel_util_routed.rpt'
    hurpt = '/home/yd383/hbm_ubmark/one2all_1t1c/output/link/report/hmss_util_routed.rpt'
    surpt = '/home/yd383/hbm_ubmark/one2all_1t1c/output/link/report/sr_util_routed.rpt'
    util_breakdown = get_utilization_breakdown({
        'full_util': furpt,
        'kernel_util': kurpt,
        'hmss_util': hurpt,
        'static_region_util': surpt
    })
    util_breakdown.print_results()
    summary_file = 'test.csv'
    with open(summary_file, 'w', newline='') as f:
        f.write(f"Design, HBM Timing, Kernel Timing, LUT, FF, BRAM, URAM, DSP\n")
        f.write(f"test, {hbm_timing}, {kernel_timing}, , , , , , \n")
        f.write(f", Total, ,{util_breakdown.total.export_csv()}\n")
        f.write(f", Breakdown, , , , , , , \n")
        f.write(f", , TGs, {util_breakdown.breakdown['kernels'].export_csv()}\n")
        f.write(f", , HMSS, {util_breakdown.breakdown['hmss'].export_csv()}\n")
        f.write(f", , Static Region, {util_breakdown.breakdown['static_region'].export_csv()}\n")
        f.write(f", , Others, {util_breakdown.breakdown['others'].export_csv()}\n")