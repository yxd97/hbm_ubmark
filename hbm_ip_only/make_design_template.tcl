# Set the reference directory for source file relative paths (by default the value is script directory path)
#? project path and anme settings <

# Set the project name

# Create project
create_project ${_xil_proj_name_} ./${_xil_proj_name_} -part xcu280-fsvh2892-2L-e -force

# Set the directory path for the new project
set proj_dir [get_property directory [current_project]]

# Set project properties
set obj [current_project]
set_property -name "board_part_repo_paths" -value "[file normalize "$board_repo"]" -objects $obj
set_property -name "board_part" -value "xilinx.com:au280:part0:1.2" -objects $obj
set_property -name "default_lib" -value "xil_defaultlib" -objects $obj
set_property -name "enable_vhdl_2008" -value "1" -objects $obj
set_property -name "ip_cache_permissions" -value "read write" -objects $obj
set_property -name "ip_output_repo" -value "$proj_dir/${_xil_proj_name_}.cache/ip" -objects $obj
set_property -name "mem.enable_memory_map_generation" -value "1" -objects $obj
set_property -name "platform.board_id" -value "au280" -objects $obj
set_property -name "sim.central_dir" -value "$proj_dir/${_xil_proj_name_}.ip_user_files" -objects $obj
set_property -name "sim.ip.auto_export_scripts" -value "1" -objects $obj
set_property -name "simulator_language" -value "Mixed" -objects $obj
set_property -name "xpm_libraries" -value "XPM_CDC XPM_FIFO XPM_MEMORY" -objects $obj

# Create 'sources_1' fileset (if not found)
if {[string equal [get_filesets -quiet sources_1] ""]} {
    create_fileset -srcset sources_1
}

# Set 'sources_1' fileset object
set obj [get_filesets sources_1]
set files [list \
    [file normalize "${origin_dir}/design_1_wrapper.v"] \
]
add_files -norecurse -fileset $obj $files

# Set 'sources_1' fileset properties
set obj [get_filesets sources_1]
set_property -name "top" -value "design_1_wrapper" -objects $obj

# Create 'constrs_1' fileset (if not found)
if {[string equal [get_filesets -quiet constrs_1] ""]} {
  create_fileset -constrset constrs_1
}

# Set 'constrs_1' fileset object
set obj [get_filesets constrs_1]

# Empty (no sources present)

# Set 'constrs_1' fileset properties
set obj [get_filesets constrs_1]

# Create 'sim_1' fileset (if not found)
if {[string equal [get_filesets -quiet sim_1] ""]} {
  create_fileset -simset sim_1
}

# Set 'sim_1' fileset object
set obj [get_filesets sim_1]
# Empty (no sources present)

# Set 'sim_1' fileset properties
set obj [get_filesets sim_1]
set_property -name "hbs.configure_design_for_hier_access" -value "1" -objects $obj
set_property -name "top" -value "design_1_wrapper" -objects $obj
set_property -name "top_lib" -value "xil_defaultlib" -objects $obj

# Set 'utils_1' fileset object
set obj [get_filesets utils_1]
# Empty (no sources present)

# Set 'utils_1' fileset properties
set obj [get_filesets utils_1]

# Adding sources referenced in BDs, if not already added

# Proc to create BD design_1
proc cr_bd_design_1 { parentCell } {
    # CHANGE DESIGN NAME HERE
    set design_name design_1
    create_bd_design $design_name

    set bCheckIPsPassed 1
    ##################################################################
    # CHECK IPs
    ##################################################################
    set bCheckIPs 1
    if { $bCheckIPs == 1 } {
        set list_check_ips "\
            xilinx.com:ip:axi_apb_bridge:3.0\
            xilinx.com:ip:clk_wiz:6.0\
            xilinx.com:ip:hbm:1.0\
            xilinx.com:ip:qdma:4.0\
            xilinx.com:ip:util_vector_logic:2.0\
            xilinx.com:ip:proc_sys_reset:5.0\
            xilinx.com:ip:util_ds_buf:2.1\
        "

        set list_ips_missing ""
        common::send_gid_msg -ssname BD::TCL -id 2011 -severity "INFO" "Checking if the following IPs exist in the project's IP catalog: $list_check_ips ."

        foreach ip_vlnv $list_check_ips {
            set ip_obj [get_ipdefs -all $ip_vlnv]
            if { $ip_obj eq "" } {
                lappend list_ips_missing $ip_vlnv
            }
        }

        if { $list_ips_missing ne "" } {
            catch {common::send_gid_msg -ssname BD::TCL -id 2012 -severity "ERROR" "The following IPs are not found in the IP Catalog:\n  $list_ips_missing\n\nResolution: Please add the repository containing the IP(s) to the project." }
            set bCheckIPsPassed 0
        }

    }

    if { $bCheckIPsPassed != 1 } {
        common::send_gid_msg -ssname BD::TCL -id 2023 -severity "WARNING" "Will not continue with creation of design due to the error(s) above."
        return 3
    }

    if { $parentCell eq "" } {
        set parentCell [get_bd_cells /]
    }

    # Get object for parentCell
    set parentObj [get_bd_cells $parentCell]
    if { $parentObj == "" } {
        catch {common::send_gid_msg -ssname BD::TCL -id 2090 -severity "ERROR" "Unable to find parent cell <$parentCell>!"}
        return
    }

    # Make sure parentObj is hier blk
    set parentType [get_property TYPE $parentObj]
    if { $parentType ne "hier" } {
        catch {common::send_gid_msg -ssname BD::TCL -id 2091 -severity "ERROR" "Parent <$parentObj> has TYPE = <$parentType>. Expected to be <hier>."}
        return
    }

    # Save current instance; Restore later
    set oldCurInst [current_bd_instance .]

    # Set parent object as current
    current_bd_instance $parentObj

    # Create interface ports
    set pci_express_x16 [ create_bd_intf_port -mode Master -vlnv xilinx.com:interface:pcie_7x_mgt_rtl:1.0 pci_express_x16 ]

    set pcie_refclk [ create_bd_intf_port -mode Slave -vlnv xilinx.com:interface:diff_clock_rtl:1.0 pcie_refclk ]
    set_property -dict [ list \
        CONFIG.FREQ_HZ {100000000} \
    ] $pcie_refclk

    # Create ports
    set apb_complete_0_0 [ create_bd_port -dir O apb_complete_0_0 ]
    set clk_100MHz [ create_bd_port -dir I -type clk -freq_hz 100000000 clk_100MHz ]
    set pcie_perstn [ create_bd_port -dir I -type rst pcie_perstn ]
    set_property -dict [ list \
        CONFIG.POLARITY {ACTIVE_LOW} \
    ] $pcie_perstn
    set resetn [ create_bd_port -dir I -type rst resetn ]
    set_property -dict [ list \
        CONFIG.POLARITY {ACTIVE_LOW} \
    ] $resetn

    # Create instance: axi_apb_bridge_0, and set properties
    set axi_apb_bridge_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_apb_bridge:3.0 axi_apb_bridge_0 ]
    set_property -dict [ list \
        CONFIG.C_APB_NUM_SLAVES {1} \
    ] $axi_apb_bridge_0

    # Create instance: axi_mem_intercon, and set properties
    set axi_mem_intercon [ create_bd_cell -type ip -vlnv xilinx.com:ip:axi_interconnect:2.1 axi_mem_intercon ]
    #? AXI Interconnect property settings <

    # Create instance: clk_wiz, and set properties
    set clk_wiz [ create_bd_cell -type ip -vlnv xilinx.com:ip:clk_wiz:6.0 clk_wiz ]
    set_property -dict [ list \
        CONFIG.RESET_BOARD_INTERFACE {resetn} \
        CONFIG.USE_BOARD_FLOW {true} \
    ] $clk_wiz

    # Create instance: hbm_0, and set properties
    set hbm_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:hbm:1.0 hbm_0 ]
    #? HBM IP property settings <

    # Create instance: qdma_0, and set properties
    set qdma_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:qdma:4.0 qdma_0 ]
    set_property -dict [ list \
        CONFIG.PCIE_BOARD_INTERFACE {pci_express_x16} \
        CONFIG.SYS_RST_N_BOARD_INTERFACE {pcie_perstn} \
        CONFIG.axilite_master_en {false} \
    ] $qdma_0

    # Create instance: resetn_inv_0, and set properties
    set resetn_inv_0 [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_vector_logic:2.0 resetn_inv_0 ]
    set_property -dict [ list \
        CONFIG.C_OPERATION {not} \
        CONFIG.C_SIZE {1} \
    ] $resetn_inv_0

    # Create instance: rst_clk_wiz_100M, and set properties
    set rst_clk_wiz_100M [ create_bd_cell -type ip -vlnv xilinx.com:ip:proc_sys_reset:5.0 rst_clk_wiz_100M ]

    # Create instance: util_ds_buf, and set properties
    set util_ds_buf [ create_bd_cell -type ip -vlnv xilinx.com:ip:util_ds_buf:2.1 util_ds_buf ]
    set_property -dict [ list \
        CONFIG.C_BUF_TYPE {IBUFDSGTE} \
        CONFIG.DIFF_CLK_IN_BOARD_INTERFACE {pcie_refclk} \
        CONFIG.USE_BOARD_FLOW {true} \
    ] $util_ds_buf

    # Create interface connections
    connect_bd_intf_net -intf_net axi_apb_bridge_0_APB_M [get_bd_intf_pins axi_apb_bridge_0/APB_M] [get_bd_intf_pins hbm_0/SAPB_0]
    connect_bd_intf_net -intf_net axi_mem_intercon_M00_AXI [get_bd_intf_pins axi_apb_bridge_0/AXI4_LITE] [get_bd_intf_pins axi_mem_intercon/M00_AXI]
    connect_bd_intf_net -intf_net pcie_refclk_1 [get_bd_intf_ports pcie_refclk] [get_bd_intf_pins util_ds_buf/CLK_IN_D]
    connect_bd_intf_net -intf_net qdma_0_M_AXI [get_bd_intf_pins axi_mem_intercon/S00_AXI] [get_bd_intf_pins qdma_0/M_AXI]
    connect_bd_intf_net -intf_net qdma_0_pcie_mgt [get_bd_intf_ports pci_express_x16] [get_bd_intf_pins qdma_0/pcie_mgt]
    #? AXI Interconnect to HBM IP SAXI connections <

    # Create port connections
    connect_bd_net -net clk_100MHz_1 [get_bd_ports clk_100MHz] [get_bd_pins clk_wiz/clk_in1]
    connect_bd_net -net clk_wiz_locked [get_bd_pins clk_wiz/locked] [get_bd_pins rst_clk_wiz_100M/dcm_locked]
    connect_bd_net -net hbm_0_apb_complete_0 [get_bd_ports apb_complete_0_0] [get_bd_pins hbm_0/apb_complete_0]
    connect_bd_net -net pcie_perstn_1 [get_bd_ports pcie_perstn] [get_bd_pins qdma_0/sys_rst_n]
    connect_bd_net -net qdma_0_axi_aclk [get_bd_pins axi_mem_intercon/ACLK] [get_bd_pins axi_mem_intercon/S00_ACLK] [get_bd_pins qdma_0/axi_aclk]
    connect_bd_net -net qdma_0_axi_aresetn [get_bd_pins axi_mem_intercon/ARESETN] [get_bd_pins axi_mem_intercon/S00_ARESETN] [get_bd_pins qdma_0/axi_aresetn]
    connect_bd_net -net resetn_inv_0_Res [get_bd_pins clk_wiz/reset] [get_bd_pins resetn_inv_0/Res] [get_bd_pins rst_clk_wiz_100M/ext_reset_in]
    connect_bd_net -net rst_clk_wiz_100M_peripheral_aresetn [get_bd_pins axi_apb_bridge_0/s_axi_aresetn] [get_bd_pins axi_mem_intercon/M00_ARESETN] [get_bd_pins axi_mem_intercon/M01_ARESETN] [get_bd_pins axi_mem_intercon/M02_ARESETN] [get_bd_pins rst_clk_wiz_100M/peripheral_aresetn]
    connect_bd_net -net util_ds_buf_IBUF_DS_ODIV2 [get_bd_pins qdma_0/sys_clk] [get_bd_pins util_ds_buf/IBUF_DS_ODIV2]
    connect_bd_net -net util_ds_buf_IBUF_OUT [get_bd_pins qdma_0/sys_clk_gt] [get_bd_pins util_ds_buf/IBUF_OUT]
    #? clock and reset connections <



    # Create address segments
    assign_bd_address -offset 0x001000000000 -range 0x00400000 -target_address_space [get_bd_addr_spaces qdma_0/M_AXI] [get_bd_addr_segs hbm_0/SAPB_0/Reg] -force
    #? HBM address allocation <

    # Restore current instance
    current_bd_instance $oldCurInst

    validate_bd_design
    save_bd_design
    close_bd_design $design_name
}
# End of cr_bd_design_1()
cr_bd_design_1 ""
set_property REGISTERED_WITH_MANAGER "1" [get_files design_1.bd ]
set_property SYNTH_CHECKPOINT_MODE "Hierarchical" [get_files design_1.bd ]

# Create 'synth_1' run (if not found)
if {[string equal [get_runs -quiet synth_1] ""]} {
    create_run -name synth_1 -part xcu280-fsvh2892-2L-e -flow {Vivado Synthesis 2020} -strategy "Vivado Synthesis Defaults" -report_strategy {No Reports} -constrset constrs_1
} else {
  set_property strategy "Vivado Synthesis Defaults" [get_runs synth_1]
  set_property flow "Vivado Synthesis 2020" [get_runs synth_1]
}
set obj [get_runs synth_1]
set_property set_report_strategy_name 1 $obj
set_property report_strategy {Vivado Synthesis Default Reports} $obj
set_property set_report_strategy_name 0 $obj
set_property -name "strategy" -value "Vivado Synthesis Defaults" -objects $obj

# set the current synth run
current_run -synthesis [get_runs synth_1]

# Create 'impl_1' run (if not found)
if {[string equal [get_runs -quiet impl_1] ""]} {
    create_run -name impl_1 -part xcu280-fsvh2892-2L-e -flow {Vivado Implementation 2020} -strategy "Vivado Implementation Defaults" -report_strategy {No Reports} -constrset constrs_1 -parent_run synth_1
} else {
  set_property strategy "Vivado Implementation Defaults" [get_runs impl_1]
  set_property flow "Vivado Implementation 2020" [get_runs impl_1]
}
set obj [get_runs impl_1]
set_property set_report_strategy_name 1 $obj
set_property report_strategy {Vivado Implementation Default Reports} $obj
set_property set_report_strategy_name 0 $obj
set_property -name "strategy" -value "Vivado Implementation Defaults" -objects $obj
set_property -name "steps.write_bitstream.args.readback_file" -value "0" -objects $obj
set_property -name "steps.write_bitstream.args.verbose" -value "0" -objects $obj

# set the current impl run
current_run -implementation [get_runs impl_1]

puts "INFO: Project created:${_xil_proj_name_}"

# Launch the synthesis and implementation runs
launch_runs synth_1 -jobs 24
wait_on_run synth_1
launch_runs impl_1 -jobs 24
wait_on_run impl_1

# report utilization
open_run impl_1
report_utilization -file $report_dir/${_xil_proj_name_}_utilization.rpt
report_utilization -hierarchical -file $report_dir/${_xil_proj_name_}_hierarchical_utilization.rpt
