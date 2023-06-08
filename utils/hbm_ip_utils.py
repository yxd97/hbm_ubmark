from typing import List, Tuple, Dict

def locate_insertion_point(lines:List[str], keyword:str, start:int = 0, end:int = -1) -> int:
    mark = f"#? {keyword} <"
    if end == -1:
        endpoint = len(lines)
    for i in range(start, endpoint):
        if mark in lines[i]:
            return i
    raise ValueError(f'Cannot find insertion point for {keyword}.')

def gen_tcl_path_settings(
    board_repo:str,
    source_dir:str,
    report_dir:str,
    proj_name:str,
    indent:int = 0
) -> List[str]:
    indentation = '\t' * indent
    tcl = []
    tcl.append(indentation + f'set board_repo {board_repo}\n')
    tcl.append(indentation + f'set origin_dir {source_dir}\n')
    tcl.append(indentation + f'set report_dir {report_dir}\n')
    tcl.append(indentation + f'set _xil_proj_name_ {proj_name}\n')
    return tcl


def gen_tcl_config_hbmip_bd_cell(
    mc_enabled:List[int], saxi_enabled:List[int], indent:int = 1
) -> List[str]:
    indentation = '\t' * indent
    tcl = []
    tcl.append(indentation + 'set_property -dict [list  \\\n')
    tcl.append(indentation + '\tCONFIG.USER_CLK_SEL_LIST0 {AXI_00_ACLK} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_CLK_SEL_LIST1 {AXI_23_ACLK} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_HBM_CP_1 {3} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_HBM_DENSITY {4GB} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_HBM_FBDIV_1 {5} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_HBM_HEX_CP_RES_1 {0x0000B300} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_HBM_HEX_FBDIV_CLKOUTDIV_1 {0x00000142} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_HBM_HEX_LOCK_FB_REF_DLY_1 {0x00000a0a} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_HBM_LOCK_FB_DLY_1 {10} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_HBM_LOCK_REF_DLY_1 {10} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_HBM_RES_1 {11} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_HBM_STACK {1} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_MC_ENABLE_APB_01 {FALSE} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_MEMORY_DISPLAY {4096} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_PHY_ENABLE_08 {FALSE} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_PHY_ENABLE_09 {FALSE} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_PHY_ENABLE_10 {FALSE} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_PHY_ENABLE_11 {FALSE} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_PHY_ENABLE_12 {FALSE} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_PHY_ENABLE_13 {FALSE} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_PHY_ENABLE_14 {FALSE} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_PHY_ENABLE_15 {FALSE} \\\n')
    tcl.append(indentation + '\tCONFIG.USER_SWITCH_ENABLE_01 {FALSE} \\\n')
    for i in range(16):
        if i in saxi_enabled:
            tcl.append(indentation + f'\tCONFIG.USER_SAXI_{i:02d} {{true}} \\\n')
        else:
            tcl.append(indentation + f'\tCONFIG.USER_SAXI_{i:02d} {{false}} \\\n')
    for i in range(8):
        if i in mc_enabled:
            tcl.append(indentation + f'\tCONFIG.USER_MC_ENABLE_{i:02d} {{true}} \\\n')
        else:
            tcl.append(indentation + f'\tCONFIG.USER_MC_ENABLE_{i:02d} {{false}} \\\n')
    tcl.append(indentation + '] $hbm_0\n')
    return tcl

def gen_tcl_config_axiintercon_bd_cell(
    saxi_enabled:List[int], indent:int = 1
) -> List[str]:
    indentation = '    ' * indent
    return [indentation + f'set_property -dict [list CONFIG.NUM_MI {len(saxi_enabled) + 1}] $axi_mem_intercon\n']

def gen_tcl_connect_clkrst(
    saxi_enabled:List[int], indent:int = 1
) -> List[str]:
    tcl = []
    indentation = '    ' * indent
    cmd = 'connect_bd_net -net resetn_1 [get_bd_ports resetn] [get_bd_pins hbm_0/APB_0_PRESET_N]'
    for saxi in saxi_enabled:
        cmd += f' [get_bd_pins hbm_0/AXI_{saxi:02d}_ARESET_N]'
    cmd += ' [get_bd_pins resetn_inv_0/Op1]'
    tcl.append(indentation + cmd + '\n')
    cmd = 'connect_bd_net -net clk_wiz_clk_out1 [get_bd_pins clk_wiz/clk_out1]'
    cmd += ' [get_bd_pins axi_apb_bridge_0/s_axi_aclk] [get_bd_pins hbm_0/APB_0_PCLK] [get_bd_pins hbm_0/HBM_REF_CLK_0] [get_bd_pins rst_clk_wiz_100M/slowest_sync_clk]'
    cmd += ' [get_bd_pins axi_mem_intercon/M00_ACLK]'
    for i in range(len(saxi_enabled)):
        cmd += f' [get_bd_pins axi_mem_intercon/M{(i+1):02d}_ACLK]'
        cmd += f' [get_bd_pins hbm_0/AXI_{saxi_enabled[i]:02d}_ACLK]'
    tcl.append(indentation + cmd + '\n')
    return tcl

def gen_tcl_connect_hbm(
    saxi_enabled:List[int], indent:int = 1
) -> List[str]:
    indentation = '    ' * indent
    tcl = []
    for saxi in saxi_enabled:
        from_port = f'axi_mem_intercon/M{(saxi + 1):02d}_AXI'
        to_port = f'hbm_0/SAXI_{saxi:02d}'
        net_name = f'axi_mem_intercon_M{(saxi + 1):02d}_AXI'
        tcl.append(
            indentation +
            f'connect_bd_intf_net -intf_net {net_name} [get_bd_intf_pins {from_port}] [get_bd_intf_pins {to_port}]\n')
    return tcl

def hex_addr(addr:int, hex_digits:int = 8) -> str:
    return f'{addr:#0{hex_digits + 2}x}'

def gen_tcl_addr_map(
    mc_enabled:List[int], saxi_enabled:List[int], indent:int = 1
) -> List[str]:
    mc_list = sorted(mc_enabled)
    pc_list = []
    for mc in mc_list:
        pc_list += [mc * 2, mc * 2 + 1]
    pc_size = 256 * 1024 * 1024 # 256 MB per channel
    segment_size = pc_size // len(saxi_enabled)
    last_segment_size = pc_size - segment_size * (len(saxi_enabled) - 1)
    saxi_list = sorted(saxi_enabled)
    command = 'assign_bd_address -offset {offset} -range {range} -target_address_space [get_bd_addr_spaces qdma_0/M_AXI] [get_bd_addr_segs hbm_0/SAXI_{saxi:02d}/HBM_MEM{pc:02d}] -force\n'
    indentation = '    ' * indent
    tcl = []
    # divide one pc to multiple saxi
    for pc in pc_list:
        for saxi in saxi_list:
            if saxi == saxi_list[-1]:
                range = hex_addr(last_segment_size)
            else:
                range = hex_addr(segment_size)
            offset = hex_addr(saxi * segment_size + pc * pc_size)
            tcl.append(indentation + command.format(saxi=saxi, pc=pc, offset=offset, range=range))
    return tcl


