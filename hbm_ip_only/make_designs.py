from typing import List, Tuple, Dict

class HBMIPConfig:
    def __init__(self, name, ):
        self.name = name

    def enable_mcs(self, mcs:List[int]):
        pass


    def tcl_create_project(self):
        return [
            'create_project project_1 /work/shared/common/project_build/hbm_ubmark/hbm_ip_only/build/project_1 -part xcu280-fsvh2892-2L-e\n',
            'set_property board_part xilinx.com:au280:part0:1.2 [current_project]\n',
            'create_bd_design -dir {/work/shared/common/project_build/hbm_ubmark/hbm_ip_only} "design_1"\n',
            'update_compile_order -fileset sources_1\n',
            'create_bd_cell -type ip -vlnv xilinx.com:ip:hbm:1.0 hbm_0\n'
        ]

    def tcl_config_hbm(self):
        return [
            'set_property -dict [list CONFIG.USER_MC_ENABLE_07 {FALSE}] [get_bd_cells hbm_0]'
        ]