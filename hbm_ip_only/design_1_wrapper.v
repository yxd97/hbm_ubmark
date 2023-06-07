//Copyright 1986-2020 Xilinx, Inc. All Rights Reserved.
//--------------------------------------------------------------------------------
//Tool Version: Vivado v.2020.2 (lin64) Build 3064766 Wed Nov 18 09:12:47 MST 2020
//Date        : Tue Jun  6 18:50:40 2023
//Host        : zhang-24.ece.cornell.edu running 64-bit unknown
//Command     : generate_target design_1_wrapper.bd
//Design      : design_1_wrapper
//Purpose     : IP block netlist
//--------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

module design_1_wrapper
   (apb_complete_0_0,
    clk_100MHz,
    pci_express_x16_rxn,
    pci_express_x16_rxp,
    pci_express_x16_txn,
    pci_express_x16_txp,
    pcie_perstn,
    pcie_refclk_clk_n,
    pcie_refclk_clk_p,
    resetn);
  output apb_complete_0_0;
  input clk_100MHz;
  input [15:0]pci_express_x16_rxn;
  input [15:0]pci_express_x16_rxp;
  output [15:0]pci_express_x16_txn;
  output [15:0]pci_express_x16_txp;
  input pcie_perstn;
  input pcie_refclk_clk_n;
  input pcie_refclk_clk_p;
  input resetn;

  wire apb_complete_0_0;
  wire clk_100MHz;
  wire [15:0]pci_express_x16_rxn;
  wire [15:0]pci_express_x16_rxp;
  wire [15:0]pci_express_x16_txn;
  wire [15:0]pci_express_x16_txp;
  wire pcie_perstn;
  wire pcie_refclk_clk_n;
  wire pcie_refclk_clk_p;
  wire resetn;

  design_1 design_1_i
       (.apb_complete_0_0(apb_complete_0_0),
        .clk_100MHz(clk_100MHz),
        .pci_express_x16_rxn(pci_express_x16_rxn),
        .pci_express_x16_rxp(pci_express_x16_rxp),
        .pci_express_x16_txn(pci_express_x16_txn),
        .pci_express_x16_txp(pci_express_x16_txp),
        .pcie_perstn(pcie_perstn),
        .pcie_refclk_clk_n(pcie_refclk_clk_n),
        .pcie_refclk_clk_p(pcie_refclk_clk_p),
        .resetn(resetn));
endmodule
