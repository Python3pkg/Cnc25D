# epicyclic_gearing.py
# generates an epicyclic_gearing and simulates the sun/planet gear or the planet/annulus gear.
# created by charlyoleg on 2013/10/07
#
# (C) Copyright 2013 charlyoleg
#
# This file is part of the Cnc25D Python package.
# 
# Cnc25D is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Cnc25D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Cnc25D.  If not, see <http://www.gnu.org/licenses/>.


"""
epicyclic_gearing.py is a parametric generator of epicylic gearing.
The main function displays in a Tk-interface the epicyclic gearing, or generate the design as files or returns the design as FreeCAD Part object.
"""

################################################################
# header for Python / FreeCAD compatibility
################################################################

import cnc25d_api
cnc25d_api.importing_freecad()

#print("FreeCAD.Version:", FreeCAD.Version())
#FreeCAD.Console.PrintMessage("Hello from PrintMessage!\n") # avoid using this method because it is not printed in the FreeCAD GUI

################################################################
# import
################################################################

import math
import sys, argparse
#from datetime import datetime
#import os, errno
import re # to detect .dxf or .svg
#import Tkinter # to display the outline in a small GUI
#
import Part
from FreeCAD import Base
# 3rd parties
#import svgwrite
#from dxfwrite import DXFEngine
# cnc25d
import gearring
import gearwheel
import gear_profile # for simulation

################################################################
# epicyclic_gearing dictionary-arguments default values
################################################################

def epicyclic_gearing_dictionary_init():
  """ create and initiate an epicyclic_gearing_dictionary with the default value
  """
  r_egd = {}
  #### epicyclic_gearing dictionary entries
  ### structure
  r_egd['sun_gear_tooth_nb']       = 19
  r_egd['planet_gear_tooth_nb']    = 31
  r_egd['planet_nb']               = 3
  ### gear
  r_egd['gear_module']             = 1.0
  r_egd['gear_router_bit_radius']  = 0.1
  r_egd['gear_tooth_resolution']   = 2
  r_egd['gear_skin_thickness']     = 0.0
  r_egd['gear_addendum_dedendum_parity_slack'] = 0.0
  ### sun-gear
  r_egd['sun_axle_diameter']       = 3.0
  r_egd['sun_crenel_diameter']     = 0.0
  r_egd['sun_crenel_nb']           = 8
  r_egd['sun_crenel_width']        = 4.0
  r_egd['sun_crenel_height']       = 2.0
  r_egd['sun_crenel_router_bit_radius']   = 1.0
  ### planet-gear
  r_egd['planet_axle_diameter']      = 3.0
  r_egd['planet_crenel_diameter']    = 0.0
  r_egd['planet_crenel_nb']          = 8
  r_egd['planet_crenel_width']       = 4.0
  r_egd['planet_crenel_height']      = 2.0
  r_egd['planet_crenel_router_bit_radius']  = 1.0
  ### planet gear carrier
  r_egd['carrier_central_diameter']              = 20.0
  r_egd['carrier_leg_diameter']                  = 20.0
  r_egd['carrier_peripheral_external_diameter']  = 0.0
  r_egd['carrier_peripheral_internal_diameter']  = 0.0
  r_egd['carrier_smoothing_radius']             = 10.0
  r_egd['carrier_central_hole_diameter']   = 10.0
  r_egd['carrier_leg_hole_diameter']       = 10.0
  ## carrier central crenel: inherit from sun-gear
  #r_egd['carrier_central_crenel_diameter']     = r_egd['sun_crenel_diameter']     
  #r_egd['carrier_central_crenel_nb']           = r_egd['sun_crenel_nb']           
  #r_egd['carrier_central_crenel_width']        = r_egd['sun_crenel_width']        
  #r_egd['carrier_central_crenel_height']       = r_egd['sun_crenel_height']       
  #r_egd['carrier_central_router_bit_radius']   = r_egd['sun_crenel_router_bit_radius']   
  ## carrier peripheral crenel
  r_egd['carrier_crenel_width']                = 4.0
  r_egd['carrier_crenel_height']               = 2.0
  r_egd['carrier_crenel_router_bit_radius']    = 0.1
  ### annulus: inherit dictionary entries from gearring
  r_egd.update(gearring.gearring_dictionary_init(1))
  ### general
  r_egd['cnc_router_bit_radius']   = 1.0
  r_egd['gear_profile_height']     = 10.0
  ### output
  r_egd['tkinter_view']                    = False
  r_egd['simulation_sun_planet_gear']      = False
  r_egd['simulation_annulus_planet_gear']  = False
  r_egd['output_file_basename']            = ''
  ### optional
  r_egd['args_in_txt'] = ""
  r_egd['return_type'] = 'int_status' # possible values: 'int_status', 'cnc25d_figure', 'freecad_object'
  #### return
  return(r_egd)

################################################################
# epicyclic_gearing argparse
################################################################

def epicyclic_gearing_add_argument(ai_parser):
  """
  Add arguments relative to the epicyclic-gearing in addition to the argument of gearring(variant=1)
  This function intends to be used by the epicyclic_gearing_cli, epicyclic_gearing_self_test
  """
  r_parser = ai_parser
  ### structure
  r_parser.add_argument('--sun_gear_tooth_nb','--sgn', action='store', type=int, default=19, dest='sw_sun_gear_tooth_nb',
    help="Set the number of gear-teeth of the sun-gear. Default: 19")
  r_parser.add_argument('--planet_gear_tooth_nb','--pgn', action='store', type=int, default=31, dest='sw_planet_gear_tooth_nb',
    help="Set the number of gear-teeth of the planet-gear. Default: 31")
  r_parser.add_argument('--planet_nb','--pn', action='store', type=int, default=0, dest='sw_planet_nb',
    help="Set the number of planets. If equal to zero, the maximum possible number of planets is set. Default: 0")
  ### gear
  r_parser.add_argument('--gear_module','--gm', action='store', type=float, default=1.0, dest='sw_gear_module',
    help="Set the module of the sun, planet and annulus gear. Default: 1.0")
  r_parser.add_argument('--gear_router_bit_radius','--grr', action='store', type=float, default=0.1, dest='sw_gear_router_bit_radius',
    help="Set the router_bit radius used to create the gear hollow of the first gear_profile. Default: 0.1")
  r_parser.add_argument('--gear_tooth_resolution','--gtr', action='store', type=int, default=2, dest='sw_gear_tooth_resolution',
    help="It sets the number of segments of the gear involute. Default: 2")
  r_parser.add_argument('--gear_skin_thickness','--gst', action='store', type=float, default=0.0, dest='sw_gear_skin_thickness',
    help="Add or remove radial thickness on the gear involute to compensate the fabrication process. Default: 0.0")
  r_parser.add_argument('--gear_addendum_dedendum_parity_slack','--gadps', action='store', type=float, default=0.0, dest='sw_gear_addendum_dedendum_parity_slack',
    help="Decrease the gear_addendum_dedendum_parity to add some slack. Default: 0.0")
  ### sun-gear
  r_parser.add_argument('--sun_axle_diameter','--sad', action='store', type=float, default=0.0, dest='sw_sun_axle_diameter',
    help="Set the diameter of the sun-gear cylindrical axle. Default: 0.0")
  r_parser.add_argument('--sun_crenel_diameter','--scd', action='store', type=float, default=0.0, dest='sw_sun_crenel_diameter',
    help="Set the diameter of the positioning circle for the sun-crenel. Default: 0.0")
  r_parser.add_argument('--sun_crenel_nb','--scn', action='store', type=int, default=0, dest='sw_sun_crenel_nb',
    help="Set the number of sun-crenels. If equal to zero, no sun-crenel is created. Default: 0")
  r_parser.add_argument('--sun_crenel_width','--scw', action='store', type=float, default=4.0, dest='sw_sun_crenel_width',
    help="Set the width of the sun-crenel. Default: 4.0")
  r_parser.add_argument('--sun_crenel_height','--sch', action='store', type=float, default=2.0, dest='sw_sun_crenel_height',
    help="Set the height of the sun-crenel. Default: 2.0")
  r_parser.add_argument('--sun_crenel_router_bit_radius','--scrbr', action='store', type=float, default=0.1, dest='sw_sun_crenel_router_bit_radius',
    help="Set the router_bit radius for the sun-crenel. Default: 0.1")
  ### planet-gear
  r_parser.add_argument('--planet_axle_diameter','--pad', action='store', type=float, default=0.0, dest='sw_planet_axle_diameter',
    help="Set the diameter of the planet-gear cylindrical axle. Default: 0.0")
  r_parser.add_argument('--planet_crenel_diameter','--pcd', action='store', type=float, default=0.0, dest='sw_planet_crenel_diameter',
    help="Set the diameter of the positioning circle for the planet-crenel. Default: 0.0")
  r_parser.add_argument('--planet_crenel_nb','--pcn', action='store', type=int, default=0, dest='sw_planet_crenel_nb',
    help="Set the number of planet-crenels. If equal to zero, no planet-crenel is created. Default: 0")
  r_parser.add_argument('--planet_crenel_width','--pcw', action='store', type=float, default=4.0, dest='sw_planet_crenel_width',
    help="Set the width of the planet-crenel. Default: 4.0")
  r_parser.add_argument('--planet_crenel_height','--pch', action='store', type=float, default=2.0, dest='sw_planet_crenel_height',
    help="Set the height of the planet-crenel. Default: 2.0")
  r_parser.add_argument('--planet_crenel_router_bit_radius','--pcrbr', action='store', type=float, default=0.1, dest='sw_planet_crenel_router_bit_radius',
    help="Set the router_bit radius for the planet-crenel. Default: 0.1")
  ### planet gear carrier
  r_parser.add_argument('--carrier_central_diameter','--ccd', action='store', type=float, default=20.0, dest='sw_carrier_central_diameter',
    help="Set the diameter of the outline of the central part of the planet-carrier. Default: 20.0")
  r_parser.add_argument('--carrier_leg_diameter','--cld', action='store', type=float, default=20.0, dest='sw_carrier_leg_diameter',
    help="Set the diameter of the outline of the leg part of the planet-carrier. Default: 20.0")
  r_parser.add_argument('--carrier_peripheral_external_diameter','--cped', action='store', type=float, default=0.0, dest='sw_carrier_peripheral_external_diameter',
    help="Set the diameter of the outline of the additional circle around the planet-carrier. If equal to 0, no additional circle is generated. Default: 0.0")
  r_parser.add_argument('--carrier_peripheral_internal_diameter','--cpid', action='store', type=float, default=0.0, dest='sw_carrier_peripheral_internal_diameter',
    help="Set the internal diameter of the additional circle around the planet-carrier. If equal to 0, the planet-carrier is filled (no hollow). Default: 0.0")
  r_parser.add_argument('--carrier_smoothing_radius','--csr', action='store', type=float, default=10, dest='sw_carrier_smoothing_radius',
    help="Set the router_bit radius for the planet-carrier. Default: 10")
  r_parser.add_argument('--carrier_central_hole_diameter','--cchd', action='store', type=float, default=10.0, dest='sw_carrier_central_hole_diameter',
    help="Set the diameter of the central hole of the planet-carrier. Default: 10.0")
  r_parser.add_argument('--carrier_leg_hole_diameter','--clhd', action='store', type=float, default=10.0, dest='sw_carrier_leg_hole_diameter',
    help="Set the diameter of the leg hole of the planet-carrier. Default: 10.0")
  ## carrier peripheral crenel
  r_parser.add_argument('--carrier_crenel_width','--ccw', action='store', type=float, default=4.0, dest='sw_carrier_crenel_width',
    help="Set the width of the carrier-crenel. Default: 4.0")
  r_parser.add_argument('--carrier_crenel_height','--cch', action='store', type=float, default=2.0, dest='sw_carrier_crenel_height',
    help="Set the height of the carrier-crenel. Default: 2.0")
  r_parser.add_argument('--carrier_crenel_router_bit_radius','--ccrbr', action='store', type=float, default=0.1, dest='sw_carrier_crenel_router_bit_radius',
    help="Set the router_bit radius for the carrier-crenel. Default: 0.1")
  ### annulus: inherit dictionary entries from gearring
  r_parser = gearring.gearring_add_argument(r_parser, 1)
  ### cnc router_bit constraint
  r_parser.add_argument('--cnc_router_bit_radius','--crr', action='store', type=float, default=0.1, dest='sw_cnc_router_bit_radius',
    help="Set the minimum router_bit radius of the epicyclic-gearing. Default: 0.1")
  r_parser.add_argument('--gear_profile_height','--gwh', action='store', type=float, default=10.0, dest='sw_gear_profile_height',
    help="Set the height of the linear extrusion of the first gear_profile. Default: 10.0")
  ### output
  r_parser.add_argument('--simulation_sun_planet_gear','--sspg', action='store_true', default=False, dest='sw_simulation_sun_planet_gear',
    help='Simulate the sun-planet gear with gear_profile.py')
  r_parser.add_argument('--simulation_annulus_planet_gear','--spag', action='store_true', default=False, dest='sw_simulation_annulus_planet_gear',
    help='Simulate the planet-annulus gear with gear_profile.py')
  # return
  return(r_parser)

    
################################################################
# the most important function to be used in other scripts
################################################################

def epicyclic_gearing(ai_constraints):
  """
  The main function of the script.
  It generates a epicyclic-gearing according to the constraint-arguments
  """
  ### check the dictionary-arguments ai_constraints
  egdi = epicyclic_gearing_dictionary_init()
  eg_c = egdi.copy()
  eg_c.update(ai_constraints)
  #print("dbg155: eg_c:", eg_c)
  if(len(eg_c.viewkeys() & egdi.viewkeys()) != len(eg_c.viewkeys() | egdi.viewkeys())): # check if the dictionary eg_c has exactly all the keys compare to epicyclic_gearing_dictionary_init()
    print("ERR157: Error, eg_c has too much entries as {:s} or missing entries as {:s}".format(eg_c.viewkeys() - egdi.viewkeys(), egdi.viewkeys() - eg_c.viewkeys()))
    sys.exit(2)
  #print("dbg164: new epicyclic_gearing constraints:")
  #for k in eg_c.viewkeys():
  #  if(eg_c[k] != egdi[k]):
  #    print("dbg166: for k {:s}, eg_c[k] {:s} != egdi[k] {:s}".format(k, str(eg_c[k]), str(egdi[k])))
  ### precision
  radian_epsilon = math.pi/1000
  ### check parameter coherence (part 1)
  ## get the router_bit_radius
  gear_router_bit_radius = eg_c['gear_router_bit_radius']
  if(eg_c['cnc_router_bit_radius']>gear_router_bit_radius):
    gear_router_bit_radius = eg_c['cnc_router_bit_radius']
  sun_crenel_router_bit_radius = eg_c['sun_crenel_router_bit_radius']
  if(eg_c['cnc_router_bit_radius']>sun_crenel_router_bit_radius):
    sun_crenel_router_bit_radius = eg_c['cnc_router_bit_radius']
  planet_crenel_router_bit_radius = eg_c['sun_crenel_router_bit_radius']
  if(eg_c['cnc_router_bit_radius']>planet_crenel_router_bit_radius):
    planet_crenel_router_bit_radius = eg_c['cnc_router_bit_radius']
  carrier_smoothing_radius = eg_c['carrier_smoothing_radius']
  if(eg_c['cnc_router_bit_radius']>carrier_smoothing_radius):
    carrier_smoothing_radius = eg_c['cnc_router_bit_radius']
  carrier_crenel_router_bit_radius = eg_c['carrier_crenel_router_bit_radius']
  if(eg_c['cnc_router_bit_radius']>carrier_crenel_router_bit_radius):
    carrier_crenel_router_bit_radius = eg_c['cnc_router_bit_radius']
  ## tooth number
  sun_gear_tooth_nb = eg_c['sun_gear_tooth_nb']
  planet_gear_tooth_nb = eg_c['planet_gear_tooth_nb']
  annulus_gear_tooth_nb = sun_gear_tooth_nb + 2 * planet_gear_tooth_nb
  smallest_gear_tooth_nb = min(sun_gear_tooth_nb, planet_gear_tooth_nb)
  ## maximal planet number
  # angle NOM
  NOM = 2*math.asin(1/(1+(float(sun_gear_tooth_nb)/planet_gear_tooth_nb)))
  security_coef = 1.1
  planet_number_max = int(2*math.pi/(NOM*security_coef))
  planet_nb = eg_c['planet_nb']
  if(planet_nb==0):
    planet_nb = planet_number_max
  if(planet_nb>planet_number_max):
    print("ERR270: Error, planet_nb {:d} is bigger than planet_number_max {:d}".format(planet_nb, planet_number_max))
  epicyclic_gearing_ratio = float(sun_gear_tooth_nb)/(sun_gear_tooth_nb+annulus_gear_tooth_nb)
  ## gear_addendum_dedendum_parity_slack
  if((eg_c['gear_addendum_dedendum_parity_slack']<0)or(eg_c['gear_addendum_dedendum_parity_slack']>30)):
    print("ERR274: Error, gear_addendum_dedendum_parity_slack {:0.3f} is out of the range 0..30".format(eg_c['gear_addendum_dedendum_parity_slack']))
    sys.exit(2)
  addendum_dedendum_parity = 50.0-eg_c['gear_addendum_dedendum_parity_slack']/2.0
  ##### gears
  ### gearring
  gr_c = {}
  gr_c['gear_tooth_nb']               = annulus_gear_tooth_nb
  gr_c['second_gear_tooth_nb']        = smallest_gear_tooth_nb
  gr_c['gear_module']                 = eg_c['gear_module']
  gr_c['gear_router_bit_radius']      = gear_router_bit_radius
  gr_c['gear_tooth_resolution']       = eg_c['gear_tooth_resolution']
  gr_c['gear_skin_thickness']         = eg_c['gear_skin_thickness']
  gr_c['gear_addendum_dedendum_parity']    = addendum_dedendum_parity
  gr_c['holder_diameter']             = eg_c['holder_diameter']
  gr_c['holder_crenel_number']        = eg_c['holder_crenel_number']
  gr_c['holder_position_angle']       = eg_c['holder_position_angle']
  gr_c['holder_hole_position_radius'] = eg_c['holder_hole_position_radius']
  gr_c['holder_hole_diameter']        = eg_c['holder_hole_diameter']
  gr_c['holder_crenel_position']      = eg_c['holder_crenel_position']
  gr_c['holder_crenel_height']        = eg_c['holder_crenel_height']
  gr_c['holder_crenel_width']         = eg_c['holder_crenel_width']
  gr_c['holder_crenel_skin_width']    = eg_c['holder_crenel_skin_width']
  gr_c['holder_crenel_router_bit_radius'] = eg_c['holder_crenel_router_bit_radius']
  gr_c['holder_smoothing_radius']     = eg_c['holder_smoothing_radius']
  gr_c['cnc_router_bit_radius']       = eg_c['cnc_router_bit_radius']
  gr_c['gear_profile_height']         = eg_c['gear_profile_height']
  gr_c['tkinter_view']                = False
  gr_c['simulation_enable']           = False
  gr_c['output_file_basename']        = ""
  gr_c['args_in_txt']                 = ""
  gr_c['return_type']                 = 'cnc25d_figure'
  annulus_figure = gearring.gearring(gr_c)
  ### planet
  pg_c = {}
  pg_c['gear_tooth_nb']             = planet_gear_tooth_nb # gear-profile
  pg_c['second_gear_tooth_nb']        = smallest_gear_tooth_nb
  pg_c['gear_module']               = eg_c['gear_module']
  pg_c['gear_router_bit_radius']    = eg_c['gear_router_bit_radius']
  pg_c['gear_tooth_resolution']     = eg_c['gear_tooth_resolution']
  pg_c['gear_skin_thickness']       = eg_c['gear_skin_thickness']
  pg_c['gear_addendum_dedendum_parity']  = addendum_dedendum_parity
  pg_c['axle_type']                 = 'none' # axle
  if(eg_c['sun_axle_diameter']>0):
    pg_c['axle_type']               = 'circle'
  pg_c['axle_x_width']              = eg_c['planet_axle_diameter']
  pg_c['axle_router_bit_radius']    = eg_c['planet_crenel_router_bit_radius']
  pg_c['crenel_diameter']           = eg_c['planet_crenel_diameter'] # crenel
  pg_c['crenel_number']             = eg_c['planet_crenel_nb']
  pg_c['crenel_angle']              = 0
  pg_c['crenel_width']              = eg_c['planet_crenel_width']
  pg_c['crenel_height']             = eg_c['planet_crenel_height']
  pg_c['crenel_router_bit_radius']  = eg_c['planet_crenel_router_bit_radius']
  pg_c['wheel_hollow_leg_number']   = 0 # wheel-hollow
  pg_c['cnc_router_bit_radius']     = eg_c['cnc_router_bit_radius'] # general
  pg_c['gear_profile_height']       = eg_c['gear_profile_height']
  pg_c['tkinter_view']              = False
  pg_c['output_file_basename']      = ""
  pg_c['args_in_txt']               = ""
  pg_c['return_type']               = 'cnc25d_figure'
  planet_figures = []
  sun_planet_length = eg_c['gear_module']*(sun_gear_tooth_nb+planet_gear_tooth_nb)/2.0
  planet_angle = 2*math.pi/planet_nb
  for i in range(planet_nb):
    pg_c['center_position_x'] = 0.0 + sun_planet_length * math.cos(i*planet_angle)
    pg_c['center_position_y'] = 0.0 + sun_planet_length * math.sin(i*planet_angle)
    pg_c['gear_initial_angle'] = 0.0
    planet_figures.append(gearwheel.gearwheel(pg_c))
  ### sun
  sg_c = {}
  sg_c['gear_tooth_nb']             = sun_gear_tooth_nb # gear-profile
  sg_c['second_gear_tooth_nb']        = smallest_gear_tooth_nb
  sg_c['gear_module']               = eg_c['gear_module']
  sg_c['gear_router_bit_radius']    = eg_c['gear_router_bit_radius']
  sg_c['gear_tooth_resolution']     = eg_c['gear_tooth_resolution']
  sg_c['gear_skin_thickness']       = eg_c['gear_skin_thickness']
  sg_c['gear_addendum_dedendum_parity']  = addendum_dedendum_parity
  sg_c['axle_type']                 = 'none' # axle
  if(eg_c['sun_axle_diameter']>0):
    sg_c['axle_type']               = 'circle'
  sg_c['axle_x_width']              = eg_c['sun_axle_diameter']
  sg_c['axle_router_bit_radius']    = eg_c['sun_crenel_router_bit_radius']
  sg_c['crenel_diameter']           = eg_c['sun_crenel_diameter'] # crenel
  sg_c['crenel_number']             = eg_c['sun_crenel_nb']
  sg_c['crenel_angle']              = 0
  sg_c['crenel_width']              = eg_c['sun_crenel_width']
  sg_c['crenel_height']             = eg_c['sun_crenel_height']
  sg_c['crenel_router_bit_radius']  = eg_c['sun_crenel_router_bit_radius']
  sg_c['wheel_hollow_leg_number']   = 0 # wheel-hollow
  sg_c['cnc_router_bit_radius']     = eg_c['cnc_router_bit_radius'] # general
  sg_c['gear_profile_height']       = eg_c['gear_profile_height']
  sg_c['tkinter_view']              = False
  sg_c['output_file_basename']      = ""
  sg_c['args_in_txt']               = ""
  sg_c['return_type']               = 'cnc25d_figure'
  sg_c['center_position_x']   = 0.0
  sg_c['center_position_y']   = 0.0
  sg_c['gear_initial_angle']  = 0.0
  sun_figure = gearwheel.gearwheel(sg_c)

  ### simulation
  gp_c = {}
  gp_c['gear_module']               = eg_c['gear_module']
  gp_c['gear_router_bit_radius']    = eg_c['gear_router_bit_radius']
  gp_c['gear_tooth_resolution']     = eg_c['gear_tooth_resolution']
  gp_c['gear_skin_thickness']       = eg_c['gear_skin_thickness']
  gp_c['gear_addendum_dedendum_parity']         = addendum_dedendum_parity
  gp_c['second_gear_addendum_dedendum_parity']  = addendum_dedendum_parity
  gp_c['output_file_basename']      = ""
  gp_c['args_in_txt']               = "simulation for epicyclic_gearing"
  gp_c['return_type']               = 'int_status'
  gp_c['center_position_x']   = 0.0
  gp_c['center_position_y']   = 0.0
  gp_c['gear_initial_angle']  = 0.0
  gp_c['second_gear_position_angle']          = 0.0
  gp_c['second_gear_additional_axis_length']  = 0.0
  gp_c['simulation_enable'] = True
  #print("dbg392: gp_c:", gp_c)
  if(eg_c['simulation_sun_planet_gear']):
    gp_c['gear_tooth_nb']             = sun_gear_tooth_nb
    gp_c['second_gear_tooth_nb']      = planet_gear_tooth_nb
    gear_profile.gear_profile(gp_c)
  if(eg_c['simulation_annulus_planet_gear']):
    gp_c['gear_tooth_nb']             = annulus_gear_tooth_nb
    gp_c['gear_type']                 = 'i'
    gp_c['second_gear_tooth_nb']      = planet_gear_tooth_nb
    gear_profile.gear_profile(gp_c)

  ### design output
  part_figure_list = []
  part_figure_list.append(annulus_figure)
  part_figure_list.append(sun_figure)
  part_figure_list.extend(planet_figures)
  #part_figure_list.append(front_planet_carrier_figure)
  #part_figure_list.append(rear_planet_carrier_figure)
  eg_assembly_figure = []
  for i in range(len(part_figure_list)):
    eg_assembly_figure.extend(part_figure_list[i])
  # ideal_outline in overlay
  eg_assembly_figure_overlay = []

  # eg_parameter_info
  eg_parameter_info = "\nepicyclic_gearing parameter info:\n"
  eg_parameter_info += "\n" + eg_c['args_in_txt'] + "\n\n"
#  eg_parameter_info += """
#split_nb:             \t{:d}
#split_initial_angle:  \t{:0.3f} (radian)  \t{:0.3f} (degree)
#high_split_radius:    \t{:0.3f} diameter: \t{:0.3f}
#high_split_type:      \t{:s}
#""".format(split_nb, sg_c['split_initial_angle'], sg_c['split_initial_angle']*180/math.pi, high_split_radius, 2*high_split_radius, sg_c['high_split_type'])
  #print(eg_parameter_info)

  ### display with Tkinter
  if(eg_c['tkinter_view']):
    print(eg_parameter_info)
    cnc25d_api.figure_simple_display(eg_assembly_figure, [], eg_parameter_info)
      
#  ### generate output file
#  output_file_suffix = ''
#  if(sg_c['output_file_basename']!=''):
#    output_file_suffix = 'brep'
#    output_file_basename = sg_c['output_file_basename']
#    if(re.search('\.dxf$', sg_c['output_file_basename'])):
#      output_file_suffix = 'dxf'
#      output_file_basename = re.sub('\.dxf$', '', sg_c['output_file_basename'])
#    elif(re.search('\.svg$', sg_c['output_file_basename'])):
#      output_file_suffix = 'svg'
#      output_file_basename = re.sub('\.svg$', '', sg_c['output_file_basename'])
#  if((output_file_suffix=='svg')or(output_file_suffix=='dxf')):
#    cnc25d_api.generate_output_file(sgw_assembly_figure, output_file_basename + "_assembly." + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
#    cnc25d_api.generate_output_file(sgw_assembly_A_figure, output_file_basename + "_assembly_A." + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
#    cnc25d_api.generate_output_file(sgw_assembly_B_figure, output_file_basename + "_assembly_B." + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
#    cnc25d_api.generate_output_file(sgw_list_of_parts, output_file_basename + "_part_list." + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
#    for i in range(split_nb):
#      cnc25d_api.generate_output_file(part_figure_list[2*i],    output_file_basename + "_part_A{:d}_placed.".format(i+1) + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
#      cnc25d_api.generate_output_file(part_figure_list[2*i+1],  output_file_basename + "_part_B{:d}_placed.".format(i+1) + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
#      cnc25d_api.generate_output_file(aligned_part_figure_list[2*i],    output_file_basename + "_part_A{:d}_aligned.".format(i+1) + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
#      cnc25d_api.generate_output_file(aligned_part_figure_list[2*i+1],  output_file_basename + "_part_B{:d}_aligned.".format(i+1) + output_file_suffix, sg_c['gear_profile_height'], sgw_parameter_info)
#  elif(output_file_suffix=='brep'):
#    #cnc25d_api.generate_output_file(sgw_assembly_figure, output_file_basename + "_assembly", sg_c['gear_profile_height'], sgw_parameter_info)
#    for i in range(split_nb):
#      cnc25d_api.generate_output_file(part_figure_list[2*i],    output_file_basename + "_part_A{:d}_placed".format(i+1), sg_c['gear_profile_height'], sgw_parameter_info)
#      cnc25d_api.generate_output_file(part_figure_list[2*i+1],  output_file_basename + "_part_B{:d}_placed".format(i+1), sg_c['gear_profile_height'], sgw_parameter_info)
#      cnc25d_api.generate_output_file(aligned_part_figure_list[2*i],    output_file_basename + "_part_A{:d}_aligned".format(i+1), sg_c['gear_profile_height'], sgw_parameter_info)
#      cnc25d_api.generate_output_file(aligned_part_figure_list[2*i+1],  output_file_basename + "_part_B{:d}_aligned".format(i+1), sg_c['gear_profile_height'], sgw_parameter_info)

  #### return
  if(eg_c['return_type']=='int_status'):
    r_eg = 1
  elif(eg_c['return_type']=='cnc25d_figure'):
    r_eg = eg_assembly_A_figure
  elif(eg_c['return_type']=='freecad_object'):
    fc_obj = []
    for i in range(len(part_figure_list)):
      fc_obj.append(cnc25d_api.figure_to_freecad_25d_part(part_figure_list[i], eg_c['gear_profile_height']))
      if(i==planet_crenel_nb+2): # front planet-carrier
        fc_obj[i].translate(Base.Vector(0,0,2*sg_c['gear_profile_height']))
      if(i==planet_crenel_nb+3): # rear planet-carrier
        fc_obj[i].translate(Base.Vector(0,0,-2*sg_c['gear_profile_height']))
    r_eg = Part.makeCompound(fc_obj)
  else:
    print("ERR508: Error the return_type {:s} is unknown".format(eg_c['return_type']))
    sys.exit(2)
  return(r_eg)

################################################################
# epicyclic_gearing wrapper dance
################################################################

def epicyclic_gearing_argparse_to_dictionary(ai_eg_args):
  """ convert a epicyclic_gearing_argparse into a epicyclic_gearing_dictionary
  """
  r_egd = {}
  #### epicyclic_gearing dictionary entries
  ### structure
  r_egd['sun_gear_tooth_nb']       = ai_eg_args.sw_sun_gear_tooth_nb
  r_egd['planet_gear_tooth_nb']    = ai_eg_args.sw_planet_gear_tooth_nb
  r_egd['planet_nb']               = ai_eg_args.sw_planet_nb
  ### gear
  r_egd['gear_module']             = ai_eg_args.sw_gear_module
  r_egd['gear_router_bit_radius']  = ai_eg_args.sw_gear_router_bit_radius
  r_egd['gear_tooth_resolution']   = ai_eg_args.sw_gear_tooth_resolution
  r_egd['gear_skin_thickness']     = ai_eg_args.sw_gear_skin_thickness
  r_egd['gear_addendum_dedendum_parity_slack'] = ai_eg_args.sw_gear_addendum_dedendum_parity_slack
  ### sun-gear
  r_egd['sun_axle_diameter']       = ai_eg_args.sw_sun_axle_diameter
  r_egd['sun_crenel_diameter']     = ai_eg_args.sw_sun_crenel_diameter
  r_egd['sun_crenel_nb']           = ai_eg_args.sw_sun_crenel_nb
  r_egd['sun_crenel_width']        = ai_eg_args.sw_sun_crenel_width
  r_egd['sun_crenel_height']       = ai_eg_args.sw_sun_crenel_height
  r_egd['sun_crenel_router_bit_radius']   = ai_eg_args.sw_sun_crenel_router_bit_radius
  ### planet-gear
  r_egd['planet_axle_diameter']      = ai_eg_args.sw_planet_axle_diameter
  r_egd['planet_crenel_diameter']    = ai_eg_args.sw_planet_crenel_diameter
  r_egd['planet_crenel_nb']          = ai_eg_args.sw_planet_crenel_nb
  r_egd['planet_crenel_width']       = ai_eg_args.sw_planet_crenel_width
  r_egd['planet_crenel_height']      = ai_eg_args.sw_planet_crenel_height
  r_egd['planet_crenel_router_bit_radius']  = ai_eg_args.sw_planet_crenel_router_bit_radius
  ### planet gear carrier
  r_egd['carrier_central_diameter']               = ai_eg_args.sw_carrier_central_diameter
  r_egd['carrier_leg_diameter']                   = ai_eg_args.sw_carrier_leg_diameter
  r_egd['carrier_peripheral_external_diameter']   = ai_eg_args.sw_carrier_peripheral_external_diameter
  r_egd['carrier_peripheral_internal_diameter']   = ai_eg_args.sw_carrier_peripheral_internal_diameter
  r_egd['carrier_smoothing_radius']               = ai_eg_args.sw_carrier_smoothing_radius
  r_egd['carrier_central_hole_diameter']   = ai_eg_args.sw_carrier_central_hole_diameter
  r_egd['carrier_leg_hole_diameter']       = ai_eg_args.sw_carrier_leg_hole_diameter
  ## carrier peripheral crenel
  r_egd['carrier_crenel_width']                = ai_eg_args.sw_carrier_crenel_width
  r_egd['carrier_crenel_height']               = ai_eg_args.sw_carrier_crenel_height
  r_egd['carrier_crenel_router_bit_radius']    = ai_eg_args.sw_carrier_crenel_router_bit_radius
  ### annulus: inherit dictionary entries from gearring
  r_egd.update(gearring.gearring_argparse_to_dictionary(ai_eg_args, 1))
  ### general
  r_egd['cnc_router_bit_radius']   = ai_eg_args.sw_cnc_router_bit_radius
  r_egd['gear_profile_height']     = ai_eg_args.sw_gear_profile_height
  ### output
  #r_egd['tkinter_view']                    = False
  r_egd['simulation_sun_planet_gear']      = ai_eg_args.sw_simulation_sun_planet_gear
  r_egd['simulation_annulus_planet_gear']  = ai_eg_args.sw_simulation_annulus_planet_gear
  r_egd['output_file_basename']            = ai_eg_args.sw_output_file_basename
  ### optional
  #r_egd['args_in_txt'] = ""
  r_egd['return_type'] = ai_eg_args.sw_return_type
  #### return
  return(r_egd)
  
def epicyclic_gearing_argparse_wrapper(ai_eg_args, ai_args_in_txt=""):
  """
  wrapper function of epicyclic_gearing() to call it using the epicyclic_gearing_parser.
  epicyclic_gearing_parser is mostly used for debug and non-regression tests.
  """
  # view the epicyclic_gearing with Tkinter as default action
  tkinter_view = True
  if(ai_eg_args.sw_simulation_sun_planet_gear or ai_eg_args.sw_simulation_annulus_planet_gear or (ai_eg_args.sw_output_file_basename!='')):
    tkinter_view = False
  # wrapper
  egd = epicyclic_gearing_argparse_to_dictionary(ai_eg_args)
  egd['args_in_txt'] = ai_args_in_txt
  egd['tkinter_view'] = tkinter_view
  #egd['return_type'] = 'int_status'
  r_eg = epicyclic_gearing(egd)
  return(r_eg)

################################################################
# self test
################################################################

def epicyclic_gearing_self_test():
  """
  This is the non-regression test of epicyclic_gearing.
  Look at the Tk window to check errors.
  """
  test_case_switch = [
    ["simplest test"        , "--gear_tooth_nb 25 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2"],
    ["gear simulation"      , "--gear_tooth_nb 25 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --simulation_enable --second_gear_tooth_nb 19"],
    ["output file"          , "--gear_tooth_nb 25 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0 --high_hole_nb 2 --output_file_basename test_output/split_gearwheel_self_test.dxf"],
    ["last test"            , "--gear_tooth_nb 24 --gear_module 10.0 --low_split_diameter 50.0 --cnc_router_bit_radius 3.0"]]
  #print("dbg741: len(test_case_switch):", len(test_case_switch))
  epicyclic_gearing_parser = argparse.ArgumentParser(description='Command line interface for the function epicyclic_gearing().')
  epicyclic_gearing_parser = epicyclic_gearing_add_argument(epicyclic_gearing_parser)
  epicyclic_gearing_parser = cnc25d_api.generate_output_file_add_argument(epicyclic_gearing_parser, 1)
  for i in range(len(test_case_switch)):
    l_test_switch = test_case_switch[i][1]
    print("{:2d} test case: '{:s}'\nwith switch: {:s}".format(i, test_case_switch[i][0], l_test_switch))
    l_args = l_test_switch.split()
    #print("dbg414: l_args:", l_args)
    st_args = epicyclic_gearing_parser.parse_args(l_args)
    r_egst = epicyclic_gearing_argparse_wrapper(st_args)
  return(r_egst)

################################################################
# epicyclic_gearing command line interface
################################################################

def epicyclic_gearing_cli(ai_args=None):
  """ command line interface of epicyclic_gearing.py when it is used in standalone
  """
  # epicyclic_gearing parser
  epicyclic_gearing_parser = argparse.ArgumentParser(description='Command line interface for the function epicyclic_gearing().')
  epicyclic_gearing_parser = epicyclic_gearing_add_argument(epicyclic_gearing_parser)
  epicyclic_gearing_parser = cnc25d_api.generate_output_file_add_argument(epicyclic_gearing_parser, 1)
  # switch for self_test
  epicyclic_gearing_parser.add_argument('--run_test_enable','--rst', action='store_true', default=False, dest='sw_run_self_test',
    help='Generate several corner cases of parameter sets and display the Tk window where you should check the gear running.')
  effective_args = cnc25d_api.get_effective_args(ai_args)
  effective_args_in_txt = "epicyclic_gearing arguments: " + ' '.join(effective_args)
  eg_args = epicyclic_gearing_parser.parse_args(effective_args)
  print("dbg111: start making epicyclic_gearing")
  if(eg_args.sw_run_self_test):
    r_eg = epicyclic_gearing_self_test()
  else:
    r_eg = epicyclic_gearing_argparse_wrapper(eg_args, effective_args_in_txt)
  print("dbg999: end of script")
  return(r_eg)

################################################################
# main
################################################################

# this works with python and freecad :)
if __name__ == "__main__":
  FreeCAD.Console.PrintMessage("epicyclic_gearing.py says hello!\n")
  #my_eg = epicyclic_gearing_cli()
  #my_eg = epicyclic_gearing_cli("--sun_gear_tooth_nb 19 --planet_gear_tooth_nb 31 --return_type freecad_object".split())
  my_eg = epicyclic_gearing_cli("--sun_gear_tooth_nb 19 --planet_gear_tooth_nb 31 --gear_module 1.0".split())
  #Part.show(my_eg)
  try: # depending on eg_c['return_type'] it might be or not a freecad_object
    Part.show(my_eg)
    print("freecad_object returned")
  except:
    pass
    #print("return_type is not a freecad-object")
