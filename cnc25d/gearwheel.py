# gearwheel.py
# generates gearwheel and simulates gear.
# created by charlyoleg on 2013/06/19
#
# (C) Copyright 2013 charlyoleg
#
# This file is part of the Cnc25D Python package.
# 
# Cnc25D is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Cnc25D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with Cnc25D.  If not, see <http://www.gnu.org/licenses/>.


"""
gearwheel.py is a parametric generator of gearwheels.
The main function return the gear-wheel as FreeCAD Part object.
You can also simulate or view of the gearwheel and get a DXF, SVG or BRep or the gearwheel
"""

################################################################
# header for Python / FreeCAD compatibility
################################################################

import cnc25d_api
#cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())
#FreeCAD.Console.PrintMessage("Hello from PrintMessage!\n") # avoid using this method because it is not printed in the FreeCAD GUI

################################################################
# import
################################################################

import math
import sys, argparse
#from datetime import datetime
#import os, errno
#import re
#import Tkinter # to display the outline in a small GUI
#
import Part
from FreeCAD import Base
# 3rd parties
#import svgwrite
#from dxfwrite import DXFEngine
# cnc25d
import gear_profile

################################################################
# gearwheel argparse
################################################################

def gearwheel_add_argument(ai_parser):
  """
  Add arguments relative to the gearwheel in addition to the argument of gear_profile_add_argument()
  This function intends to be used by the gearwheel_cli, gearwheel_self_test
  """
  r_parser = ai_parser
  ### axle
  r_parser.add_argument('--axle_type','--at', action='store', default='none', dest='sw_axle_type',
    help="Select the type of axle for the first gearwheel. Possible values: 'none', 'circle' and 'rectangle'. Default: 'none'")
  r_parser.add_argument('--axle_x_width','--axw', action='store', type=float, default=10.0, dest='sw_axle_x_width',
    help="Set the axle cylinder diameter or the axle rectangle x-width of the first gearwheel. Default: 10.0")
  r_parser.add_argument('--axle_y_width','--ayw', action='store', type=float, default=10.0, dest='sw_axle_y_width',
    help="Set the axle rectangle y-width of the first gearwheel. Default: 10.0")
  r_parser.add_argument('--axle_router_bit_radius','--arr', action='store', type=float, default=1.0, dest='sw_axle_router_bit_radius',
    help="Set the router_bit radius of the first gearwheel rectangle axle. Default: 1.0")
  ### wheel-hollow = legs
  r_parser.add_argument('--wheel_hollow_leg_number','--whln', action='store', type=int, default=1, dest='sw_wheel_hollow_leg_number',
    help="Set the number of legs for the wheel-hollow of the first gearwheel. The legs are uniform distributed. The first leg is centered on the leg_angle. 0 means no wheel-hollow  Default: 0")
  r_parser.add_argument('--wheel_hollow_leg_width','--whlw', action='store', type=float, default=10.0, dest='sw_wheel_hollow_leg_width',
    help="Set the wheel-hollow leg width of the first gearwheel. Default: 10.0")
  r_parser.add_argument('--wheel_hollow_leg_angle','--whla', action='store', type=float, default=0.0, dest='sw_wheel_hollow_leg_angle',
    help="Set the wheel-hollow leg-angle of the first gearwheel. Default: 0.0")
  r_parser.add_argument('--wheel_hollow_internal_diameter','--whid', action='store', type=float, default=20.0, dest='sw_wheel_hollow_internal_diameter',
    help="Set the wheel-hollow internal diameter of the first gearwheel. Default: 20.0")
  r_parser.add_argument('--wheel_hollow_external_diameter','--whed', action='store', type=float, default=30.0, dest='sw_wheel_hollow_external_diameter',
    help="Set the wheel-hollow external diameter of the first gearwheel. It must be bigger than the wheel_hollow_internal_diameter and smaller than the gear bottom diameter. Default: 30.0")
  r_parser.add_argument('--wheel_hollow_router_bit_radius','--whrr', action='store', type=float, default=1.0, dest='sw_wheel_hollow_router_bit_radius',
    help="Set the router_bit radius of the wheel-hollow of the first gearwheel. Default: 1.0")
  ### cnc router_bit constraint
  r_parser.add_argument('--cnc_router_bit_radius','--crr', action='store', type=float, default=1.0, dest='sw_cnc_router_bit_radius',
    help="Set the minimum router_bit radius of the first gearwheel. It increases gear_router_bit_radius, axle_router_bit_radius and wheel_hollow_router_bit_radius if needed. Default: 1.0")
  # return
  return(r_parser)

    
################################################################
# the most important function to be used in other scripts
################################################################

def gearwheel(
      ##### from gear_profile
      ### first gear
      # general
      #ai_gear_type = 'e',
      ai_gear_tooth_nb = 0,
      ai_gear_module = 0.0,
      ai_gear_primitive_diameter = 0.0,
      ai_gear_addendum_dedendum_parity = 50.0,
      # tooth height
      ai_gear_tooth_half_height = 0.0,
      ai_gear_addendum_height_pourcentage = 100.0,
      ai_gear_dedendum_height_pourcentage = 100.0,
      ai_gear_hollow_height_pourcentage = 25.0,
      ai_gear_router_bit_radius = 0.1,
      # positive involute
      ai_gear_base_diameter = 0.0,
      ai_gear_force_angle = 0.0,
      ai_gear_tooth_resolution = 3,
      ai_gear_skin_thickness = 0.0,
      # negative involute (if zero, negative involute = positive involute)
      ai_gear_base_diameter_n = 0.0,
      ai_gear_force_angle_n = 0.0,
      ai_gear_tooth_resolution_n = 0,
      ai_gear_skin_thickness_n = 0.0,
      ### second gear
      # general
      ai_second_gear_type = 'e',
      ai_second_gear_tooth_nb = 0,
      ai_second_gear_primitive_diameter = 0.0,
      ai_second_gear_addendum_dedendum_parity = 0.0,
      # tooth height
      ai_second_gear_tooth_half_height = 0.0,
      ai_second_gear_addendum_height_pourcentage = 100.0,
      ai_second_gear_dedendum_height_pourcentage = 100.0,
      ai_second_gear_hollow_height_pourcentage = 25.0,
      ai_second_gear_router_bit_radius = 0.0,
      # positive involute
      ai_second_gear_base_diameter = 0.0,
      ai_second_gear_tooth_resolution = 0,
      ai_second_gear_skin_thickness = 0.0,
      # negative involute (if zero, negative involute = positive involute)
      ai_second_gear_base_diameter_n = 0.0,
      ai_second_gear_tooth_resolution_n = 0,
      ai_second_gear_skin_thickness_n = 0.0,
      ### position
      # first gear position
      ai_center_position_x = 0.0,
      ai_center_position_y = 0.0,
      ai_gear_initial_angle = 0.0,
      # second gear position
      ai_second_gear_position_angle = 0.0,
      ai_second_gear_additional_axis_length = 0.0,
      ### portion
      #ai_portion_tooth_nb = 0,
      #ai_portion_first_end = 0,
      #ai_portion_last_end =0,
      ### output
      ai_gear_profile_height = 1.0,
      ai_simulation_enable = False,
      #ai_output_file_basename = '',
      ##### from gearwheel
      ### axle
      ai_axle_type                = 'circle',
      ai_axle_x_width             = 10.0,
      ai_axle_y_width             = 10.0,
      ai_axle_router_bit_radius   = 1.0,
      ### wheel-hollow = legs
      ai_wheel_hollow_leg_number        = 0,
      ai_wheel_hollow_leg_width         = 10.0,
      ai_wheel_hollow_leg_angle         = 0.0,
      ai_wheel_hollow_internal_diameter = 20.0,
      ai_wheel_hollow_external_diameter = 30.0,
      ai_wheel_hollow_router_bit_radius = 1.0,
      ### cnc router_bit constraint
      ai_cnc_router_bit_radius          = '1.0',
      ### view the gearwheel with tkinter
      ai_tkinter_view = False,
      ai_output_file_basename = ''):
  """
  The main function of the script.
  It generates a gearwheel according to the function arguments
  """
  ## check parameter coherence

  ## get the gear_profile
  gear_profile_B = gear_profile.gear_profile(
                        ### first gear
                        # general
                        ai_gear_type                      = 'e',
                        ai_gear_tooth_nb                  = ai_gear_tooth_nb,
                        ai_gear_module                    = ai_gear_module,
                        ai_gear_primitive_diameter        = ai_gear_primitive_diameter,
                        ai_gear_addendum_dedendum_parity  = ai_gear_addendum_dedendum_parity,
                        # tooth height
                        ai_gear_tooth_half_height           = ai_gear_tooth_half_height,
                        ai_gear_addendum_height_pourcentage = ai_gear_addendum_height_pourcentage,
                        ai_gear_dedendum_height_pourcentage = ai_gear_dedendum_height_pourcentage,
                        ai_gear_hollow_height_pourcentage   = ai_gear_hollow_height_pourcentage,
                        ai_gear_router_bit_radius           = ai_gear_router_bit_radius,
                        # positive involute
                        ai_gear_base_diameter       = ai_gear_base_diameter,
                        ai_gear_force_angle         = ai_gear_force_angle,
                        ai_gear_tooth_resolution    = ai_gear_tooth_resolution,
                        ai_gear_skin_thickness      = ai_gear_skin_thickness,
                        # negative involute (if zero, negative involute = positive involute)
                        ai_gear_base_diameter_n     = ai_gear_base_diameter_n,
                        ai_gear_force_angle_n       = ai_gear_force_angle_n,
                        ai_gear_tooth_resolution_n  = ai_gear_tooth_resolution_n,
                        ai_gear_skin_thickness_n    = ai_gear_skin_thickness_n,
                        ### second gear
                        # general
                        ai_second_gear_type                     = ai_second_gear_type,
                        ai_second_gear_tooth_nb                 = ai_second_gear_tooth_nb,
                        ai_second_gear_primitive_diameter       = ai_second_gear_primitive_diameter,
                        ai_second_gear_addendum_dedendum_parity = ai_second_gear_addendum_dedendum_parity,
                        # tooth height
                        ai_second_gear_tooth_half_height            = ai_second_gear_tooth_half_height,
                        ai_second_gear_addendum_height_pourcentage  = ai_second_gear_addendum_height_pourcentage,
                        ai_second_gear_dedendum_height_pourcentage  = ai_second_gear_dedendum_height_pourcentage,
                        ai_second_gear_hollow_height_pourcentage    = ai_second_gear_hollow_height_pourcentage,
                        ai_second_gear_router_bit_radius            = ai_second_gear_router_bit_radius,
                        # positive involute
                        ai_second_gear_base_diameter      = ai_second_gear_base_diameter,
                        ai_second_gear_tooth_resolution   = ai_second_gear_tooth_resolution,
                        ai_second_gear_skin_thickness     = ai_second_gear_skin_thickness,
                        # negative involute (if zero, negative involute = positive involute)
                        ai_second_gear_base_diameter_n    = ai_second_gear_base_diameter_n,
                        ai_second_gear_tooth_resolution_n = ai_second_gear_tooth_resolution_n,
                        ai_second_gear_skin_thickness_n   = ai_second_gear_skin_thickness_n,
                        ### position
                        # first gear position
                        ai_center_position_x                    = ai_center_position_x,
                        ai_center_position_y                    = ai_center_position_y,
                        ai_gear_initial_angle                   = ai_gear_initial_angle,
                        # second gear position
                        ai_second_gear_position_angle           = ai_second_gear_position_angle,
                        ai_second_gear_additional_axis_length   = ai_second_gear_additional_axis_length,
                        ### portion
                        ai_portion_tooth_nb     = 0,
                        ai_portion_first_end    = 0,
                        ai_portion_last_end     = 0,
                        ### output
                        ai_gear_profile_height  = ai_gear_profile_height,
                        ai_simulation_enable    = ai_simulation_enable,    # ai_simulation_enable,
                        ai_output_file_basename = '')

  ## axle
  axle_figure = []

  ## wheel hollow (a.k.a legs)
  wheel_hollow_figure = []

  ## design output
  gw_figure = [gear_profile_B]
  gw_figure.extend(axle_figure)
  gw_figure.extend(wheel_hollow_figure)

  # display with Tkinter
  if(ai_tkinter_view):
    cnc25d_api.figure_simple_display(gw_figure)
  # generate output file
  cnc25d_api.generate_output_file(gw_figure, ai_output_file_basename, ai_gear_profile_height)

  # return the gearwheel as FreeCAD Part object
  #r_gw = cnc25d_api.figure_to_freecad_25d_part(gw_figure, ai_gear_profile_height)
  r_gw = 1 # this is to spare the freecad computation time during debuging
  return(r_gw)

################################################################
# gearwheel argparse_to_function
################################################################

def gearwheel_argparse_wrapper(ai_gw_args):
  """
  wrapper function of gearwheel() to call it using the gearwheel_parser.
  gearwheel_parser is mostly used for debug and non-regression tests.
  """
  # view the gearwheel with Tkinter as default action
  tkinter_view = True
  if(ai_gw_args.sw_simulation_enable or (ai_gw_args.sw_output_file_basename!='')):
    tkinter_view = False
  # wrapper
  r_gw = gearwheel(
           ##### from gear_profile
           ### first gear
           # general
           #ai_gear_type                      = ai_gw_args.sw_gear_type,
           ai_gear_tooth_nb                  = ai_gw_args.sw_gear_tooth_nb,
           ai_gear_module                    = ai_gw_args.sw_gear_module,
           ai_gear_primitive_diameter        = ai_gw_args.sw_gear_primitive_diameter,
           ai_gear_addendum_dedendum_parity  = ai_gw_args.sw_gear_addendum_dedendum_parity,
           # tooth height
           ai_gear_tooth_half_height           = ai_gw_args.sw_gear_tooth_half_height,
           ai_gear_addendum_height_pourcentage = ai_gw_args.sw_gear_addendum_height_pourcentage,
           ai_gear_dedendum_height_pourcentage = ai_gw_args.sw_gear_dedendum_height_pourcentage,
           ai_gear_hollow_height_pourcentage   = ai_gw_args.sw_gear_hollow_height_pourcentage,
           ai_gear_router_bit_radius           = ai_gw_args.sw_gear_router_bit_radius,
           # positive involute
           ai_gear_base_diameter       = ai_gw_args.sw_gear_base_diameter,
           ai_gear_force_angle         = ai_gw_args.sw_gear_force_angle,
           ai_gear_tooth_resolution    = ai_gw_args.sw_gear_tooth_resolution,
           ai_gear_skin_thickness      = ai_gw_args.sw_gear_skin_thickness,
           # negative involute (if zero, negative involute = positive involute)
           ai_gear_base_diameter_n     = ai_gw_args.sw_gear_base_diameter_n,
           ai_gear_force_angle_n       = ai_gw_args.sw_gear_force_angle_n,
           ai_gear_tooth_resolution_n  = ai_gw_args.sw_gear_tooth_resolution_n,
           ai_gear_skin_thickness_n    = ai_gw_args.sw_gear_skin_thickness_n,
           ### second gear
           # general
           ai_second_gear_type                     = ai_gw_args.sw_second_gear_type,
           ai_second_gear_tooth_nb                 = ai_gw_args.sw_second_gear_tooth_nb,
           ai_second_gear_primitive_diameter       = ai_gw_args.sw_second_gear_primitive_diameter,
           ai_second_gear_addendum_dedendum_parity = ai_gw_args.sw_second_gear_addendum_dedendum_parity,
           # tooth height
           ai_second_gear_tooth_half_height            = ai_gw_args.sw_second_gear_tooth_half_height,
           ai_second_gear_addendum_height_pourcentage  = ai_gw_args.sw_second_gear_addendum_height_pourcentage,
           ai_second_gear_dedendum_height_pourcentage  = ai_gw_args.sw_second_gear_dedendum_height_pourcentage,
           ai_second_gear_hollow_height_pourcentage    = ai_gw_args.sw_second_gear_hollow_height_pourcentage,
           ai_second_gear_router_bit_radius            = ai_gw_args.sw_second_gear_router_bit_radius,
           # positive involute
           ai_second_gear_base_diameter      = ai_gw_args.sw_second_gear_base_diameter,
           ai_second_gear_tooth_resolution   = ai_gw_args.sw_second_gear_tooth_resolution,
           ai_second_gear_skin_thickness     = ai_gw_args.sw_second_gear_skin_thickness,
           # negative involute (if zero, negative involute = positive involute)
           ai_second_gear_base_diameter_n    = ai_gw_args.sw_second_gear_base_diameter_n,
           ai_second_gear_tooth_resolution_n = ai_gw_args.sw_second_gear_tooth_resolution_n,
           ai_second_gear_skin_thickness_n   = ai_gw_args.sw_second_gear_skin_thickness_n,
           ### position
           # first gear position
           ai_center_position_x                    = ai_gw_args.sw_center_position_x,
           ai_center_position_y                    = ai_gw_args.sw_center_position_y,
           ai_gear_initial_angle                   = ai_gw_args.sw_gear_initial_angle,
           # second gear position
           ai_second_gear_position_angle           = ai_gw_args.sw_second_gear_position_angle,
           ai_second_gear_additional_axis_length   = ai_gw_args.sw_second_gear_additional_axis_length,
           ### portion
           #ai_portion_tooth_nb     = ai_gw_args.sw_cut_portion[0],
           #ai_portion_first_end    = ai_gw_args.sw_cut_portion[1],
           #ai_portion_last_end     = ai_gw_args.sw_cut_portion[2],
           ### output
           ai_gear_profile_height  = ai_gw_args.sw_gear_profile_height,
           ai_simulation_enable    = ai_gw_args.sw_simulation_enable,    # ai_gw_args.sw_simulation_enable,
           #ai_output_file_basename = ai_gw_args.sw_output_file_basename,
           ##### from gearwheel
           ### axle
           ai_axle_type                = ai_gw_args.sw_axle_type,
           ai_axle_x_width             = ai_gw_args.sw_axle_x_width,
           ai_axle_y_width             = ai_gw_args.sw_axle_y_width,
           ai_axle_router_bit_radius   = ai_gw_args.sw_axle_router_bit_radius,
           ### wheel-hollow = legs
           ai_wheel_hollow_leg_number        = ai_gw_args.sw_wheel_hollow_leg_number,
           ai_wheel_hollow_leg_width         = ai_gw_args.sw_wheel_hollow_leg_width,
           ai_wheel_hollow_leg_angle         = ai_gw_args.sw_wheel_hollow_leg_angle,
           ai_wheel_hollow_internal_diameter = ai_gw_args.sw_wheel_hollow_internal_diameter,
           ai_wheel_hollow_external_diameter = ai_gw_args.sw_wheel_hollow_external_diameter,
           ai_wheel_hollow_router_bit_radius = ai_gw_args.sw_wheel_hollow_router_bit_radius,
           ### cnc router_bit constraint
           ai_cnc_router_bit_radius          = ai_gw_args.sw_cnc_router_bit_radius,
           ### design output : view the gearwheel with tkinter or write files
           ai_tkinter_view = tkinter_view,
           ai_output_file_basename = ai_gw_args.sw_output_file_basename)
  return(r_gw)

################################################################
# self test
################################################################

def gearwheel_self_test():
  """
  This is the non-regression test of gearwheel.
  Look at the simulation Tk window to check errors.
  """
  test_case_switch = [
    ["simplest test"                                    , ""],
    ["simplest test with simulation"                    , "--simulation_enable"],
    ["simple reduction (ratio<1)"                       , "--second_gear_tooth_nb 21 --simulation_enable"],
    ["simple transmission (ratio=1)"                    , "--gear_tooth_nb 13 --second_gear_tooth_nb 13 --simulation_enable"],
    ["simple multiplication (ratio>1)"                  , "--gear_tooth_nb 19 --second_gear_tooth_nb 16 --simulation_enable"],
    ["big ratio and zoom"                               , "--gear_tooth_nb 19 --second_gear_tooth_nb 137 --simulation_zoom 4.0 --simulation_enable"],
    ["single gear with same primitive and base circle"  , "--gear_tooth_nb 17 --gear_base_diameter 17.0 --simulation_enable"],
    ["single gear with small base circle"               , "--gear_tooth_nb 27 --gear_base_diameter 23.5 --simulation_enable"],
    ["with first and second angle and inter-axis length" , "--second_gear_tooth_nb 21 --gear_initial_angle {:f} --second_gear_position_angle {:f} --second_gear_additional_axis_length 0.2 --simulation_enable".format(15*math.pi/180, 40.0*math.pi/180)],
    ["other with first and second angle"                , "--second_gear_tooth_nb 15 --gear_initial_angle  {:f} --second_gear_position_angle  {:f} --simulation_enable".format(-5*math.pi/180, 170.0*math.pi/180)],
    ["with force angle constraint"                      , "--gear_tooth_nb 17 --second_gear_tooth_nb 27 --gear_force_angle {:f} --simulation_enable".format(20*math.pi/180)],
    ["first base radius constraint"                     , "--gear_tooth_nb 26 --second_gear_tooth_nb 23 --gear_base_diameter 23.0 --simulation_enable"],
    ["second base radius constraint"                    , "--second_gear_tooth_nb 23 --second_gear_primitive_diameter 20.3 --simulation_enable"],
    ["fine draw resolution"                             , "--second_gear_tooth_nb 19 --gear_tooth_resolution 10 --simulation_enable"],
    ["ratio 1 and dedendum at 30%%"                     , "--second_gear_tooth_nb 17 --gear_dedendum_height_pourcentage 30.0 --second_gear_addendum_height_pourcentage 30.0 --simulation_enable"],
    ["ratio > 1 and dedendum at 40%%"                   , "--second_gear_tooth_nb 23 --gear_dedendum_height_pourcentage 40.0 --second_gear_addendum_height_pourcentage 40.0 --simulation_enable"],
    ["ratio > 1 and addendum at 80%%"                   , "--second_gear_tooth_nb 17 --gear_addendum_height_pourcentage 80.0 --second_gear_dedendum_height_pourcentage 80.0 --simulation_enable"],
    ["ratio > 1 and dedendum at 160%%"                  , "--second_gear_tooth_nb 21 --gear_dedendum_height_pourcentage 160.0 --simulation_enable"],
    ["ratio > 1 and small tooth height"                 , "--second_gear_tooth_nb 29 --gear_tooth_half_height 1.3 --second_gear_tooth_half_height 1.3 --simulation_enable"],
    ["ratio > 1 and big tooth height"                   , "--second_gear_tooth_nb 29 --gear_tooth_half_height 2.3 --second_gear_tooth_half_height 2.3 --simulation_enable"],
    ["ratio > 1 and addendum-dedendum parity"           , "--gear_tooth_nb 30 --second_gear_tooth_nb 37 --gear_addendum_dedendum_parity 60.0 --second_gear_addendum_dedendum_parity 40.0 --simulation_enable"],
    ["file generation"                                  , "--center_position_x 100 --center_position_y 50 --output_file_basename self_test_output/"],
    ["interior gear"                                    , "--second_gear_tooth_nb 14 --gear_type ie --simulation_enable"],
    ["interior gear"                                    , "--gear_tooth_nb 25 --second_gear_tooth_nb 17 --gear_type ie --second_gear_position_angle {:f} --simulation_enable".format(30.0*math.pi/180)],
    ["interior second gear"                             , "--second_gear_tooth_nb 29 --gear_type ei --simulation_enable"],
    ["interior second gear"                             , "--second_gear_tooth_nb 24 --gear_type ei --second_gear_position_angle {:f} --simulation_enable".format(-75*math.pi/180)],
    ["interior gear"                                    , "--second_gear_tooth_nb 14 --gear_type ie --gear_addendum_height_pourcentage 75.0 --simulation_enable"],
    ["cremailliere"                                     , "--gear_type ce --gear_tooth_nb 3 --second_gear_tooth_nb 20 --gear_primitive_diameter 15 --gear_base_diameter 20 --simulation_enable"],
    ["cremailliere with angle"                          , "--gear_type ce --gear_tooth_nb 12 --second_gear_tooth_nb 20 --gear_primitive_diameter 40 --gear_base_diameter 20 --gear_initial_angle {:f} --simulation_enable".format(40*math.pi/180)]]
  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  gearwheel_parser = argparse.ArgumentParser(description='Command line interface for the function gear_profile().')
  gearwheel_parser = gear_profile.gear_profile_add_argument(gearwheel_parser, 1)
  gearwheel_parser = gearwheel_add_argument(gearwheel_parser)
  gearwheel_parser = cnc25d_api.generate_output_file_add_argument(gearwheel_parser)
  for i in range(len(test_case_switch)):
    l_test_switch = test_case_switch[i][1]
    print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i, test_case_switch[i][0], l_test_switch))
    l_args = l_test_switch.split()
    #print("dbg414: l_args:", l_args)
    st_args = gearwheel_parser.parse_args(l_args)
    r_gwst = gearwheel_argparse_wrapper(st_args)
  return(r_gwst)

################################################################
# gearwheel command line interface
################################################################

def gearwheel_cli(ai_args=None):
  """ command line interface of gearwheel.py when it is used in standalone
  """
  # gearwheel parser
  gearwheel_parser = argparse.ArgumentParser(description='Command line interface for the function gearwheel().')
  gearwheel_parser = gear_profile.gear_profile_add_argument(gearwheel_parser, 1)
  gearwheel_parser = gearwheel_add_argument(gearwheel_parser)
  gearwheel_parser = cnc25d_api.generate_output_file_add_argument(gearwheel_parser)
  # switch for self_test
  gearwheel_parser.add_argument('--run_test_enable','--rst', action='store_true', default=False, dest='sw_run_self_test',
  help='Generate several corner cases of parameter sets and display the Tk window where you should check the gear running.')
  effective_args = cnc25d_api.get_effective_args(ai_args)
  gw_args = gearwheel_parser.parse_args(effective_args)
  print("dbg111: start making gearwheel")
  if(gw_args.sw_run_self_test):
    r_gw = gearwheel_self_test()
  else:
    r_gw = gearwheel_argparse_wrapper(gw_args)
  print("dbg999: end of script")
  return(r_gw)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("gearwheel.py says hello!\n")
  #my_gw = gearwheel_cli()
  #my_gw = gearwheel_cli("--gear_tooth_nb 17 --output_file_basename test_output/toto2".split())
  my_gw = gearwheel_cli("--gear_tooth_nb 17".split())
  #Part.show(my_gw)


