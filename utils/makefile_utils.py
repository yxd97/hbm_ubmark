from typing import List,Tuple

def generate_baisc_config(
        board_repo_path:str,
        board_xsa_name:str,
        cpp_compiler:str='/usr/bin/g++',
        vitis_compiler:str='$(XILINX_VITIS)/bin/v++',
) -> List[str]:
    return [
        f'CXX := {cpp_compiler}\n',
        f'VPP := {vitis_compiler}\n',
        'TARGET := hw\n',
        f'BOARD = {board_xsa_name}\n',
        f'BOARD_REPO_PATH = {board_repo_path}\n',
        'PLATFORM := $(BOARD_REPO_PATH)/$(BOARD)/$(BOARD).xpfm\n',
        'HOST_ARCH := x86\n',
        '\n',
    ]

def generate_include_oclxcl(include_dir:str) -> List[str]:
    return [
        f'include {include_dir}/opencl/opencl.mk\n',
        f'include {include_dir}/xcl2/xcl2.mk\n',
        '\n',
    ]

def generate_dir_config(build_dir:str, output_dir:str) -> List[str]:
    return [
        f'BUILD_DIR := ../{build_dir}\n',
        f'OUTPUT_DIR := ../{output_dir}\n',
        'LOG_DIR := $(BUILD_DIR)/logs\n',
        'COMPILE_DIR := $(BUILD_DIR)/compile_$(TARGET)\n',
        'LINK_DIR := $(BUILD_DIR)/link_$(TARGET)\n',
        '\n',
    ]

def generate_kernel_config(kernel_name:str, target_frequency_mhz:int=300) -> List[str]:
    return [
        f'KRNL_NAME := {kernel_name}\n',
        'KRNL_SRC := ../../$(KRNL_NAME)/$(KRNL_NAME).cpp\n',
        'KRNL_OBJ := $(COMPILE_DIR)/$(KRNL_NAME).xo\n',
        'KRNL_COMPILE_OPTS := -t $(TARGET) --platform $(PLATFORM) --save-temps --temp_dir $(COMPILE_DIR) --report_dir $(OUTPUT_DIR) --log_dir $(LOG_DIR)\n',
        f'KRNL_COMPILE_OPTS += --kernel_frequency {target_frequency_mhz}\n',
        'KRNL_COMPILE_OPTS += -I../../$(KRNL_NAME)\n',
        'SYS_LINK_OPTS := -t $(TARGET) --platform $(PLATFORM) --save-temps --temp_dir $(LINK_DIR) --report_dir $(OUTPUT_DIR) --log_dir $(LOG_DIR)\n',
        f'SYS_LINK_OPTS += --kernel_frequency {target_frequency_mhz}\n',
        'SYS_LINK_OPTS += --config system.cfg\n',
        '\n',
    ]

def generate_host_config(include_dir:str) -> List[str]:
    return [
        'HOST_SRC := host.cpp\n',
        'HOST_EXE := host.exe\n',
        f'HOST_COMPILE_OPTS := -I{include_dir}/xcl2\n',
        f'HOST_COMPILE_OPTS += -I{include_dir}/hostlib\n',
        'HOST_COMPILE_OPTS += -O3 -std=c++1y\n',
        'HOST_COMPILE_OPTS += $(xcl2_CXXFLAGS)\n',
        'HOST_COMPILE_OPTS += $(opencl_CXXFLAGS)\n',
        'HOST_LINK_OPTS := $(xcl2_LDFLAGS)\n',
        'HOST_LINK_OPTS += $(opencl_LDFLAGS)\n',
        'HOST_LINK_OPTS += -lOpenCL -lxrt_coreutil -lrt\n',
        '\n',
    ]

def generate_emulation_config(
    emuconfig_util_binary:str='$(XILINX_VITIS)/bin/emconfigutil',
) -> List[str]:
    return [
        f'EMCONFIGUTIL := {emuconfig_util_binary}\n',
        'EMCONFIG_FILE := emconfig.json\n',
        'EMCONFIGUTIL_OPTS := --platform $(PLATFORM)\n',
        '\n',
    ]

def generate_build_targets(test_case_name:str) -> List[str]:
    return [
        f'FPGA_BINARY = $(OUTPUT_DIR)/{test_case_name}.$(TARGET).xclbin\n',
        '\n',
        '.PHONY: xclbin host emconfig\n',
        'xclbin: $(FPGA_BINARY)\n',
        'host: $(HOST_EXE)\n',
        'emconfig: $(EMCONFIG_FILE)\n',
        '\n',
        '$(KRNL_OBJ): $(KRNL_SRC)\n',
        '\t$(VPP) $(KRNL_COMPILE_OPTS) -c -k $(KRNL_NAME) -o $(KRNL_OBJ) $(KRNL_SRC)\n',
        '\n',
        '$(FPGA_BINARY): $(KRNL_OBJ)\n',
        '\t$(VPP) $(SYS_LINK_OPTS) -l -o $(FPGA_BINARY) $(KRNL_OBJ)\n',
        '\n',
        '$(HOST_EXE): $(HOST_SRC)\n',
        '\t$(CXX) $(HOST_COMPILE_OPTS) -o $(HOST_EXE) $(HOST_SRC) $(HOST_LINK_OPTS)\n',
        '\n',
        '$(EMCONFIG_FILE):\n',
        '\t$(EMCONFIGUTIL) --platform $(PLATFORM)\n',
        '\n',
    ]

def generate_clean_targets() -> List[str]:
    return [
        '.PHONY: clean cleanall\n',
        'clean:\n',
        '\trm -rf $(EMCONFIG_FILE)\n',
        '\trm -rf *.log *.jou\n',
        '\trm -rf .run\n',
        '\n',
        'cleanall: clean\n',
        '\trm -rf  $(HOST_EXE) $(BUILD_DIR) $(OUTPUT_DIR)/*\n',
        '\trm -rf .Xil .ipcache\n',
        '\n',
    ]

def generate_run_targets() -> List[str]:
    return [
        '.PHONY: run\n',
        'run: $(HOST_EXE) $(FPGA_BINARY)\n',
        '\t./$(HOST_EXE) $(FPGA_BINARY)\n',
        '\n',
    ]