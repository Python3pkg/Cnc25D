# cnc25d_design.py
# the unified interface to use the cnc25d designs
# created by charlyoleg on 2013/10/01
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
cnc25d_design.py provides a unified interface of the cnc25d designs
to be used by the design examples or external scripts
"""

################################################################
# import
################################################################

from . import box_wood_frame
from . import gear_profile
from . import gearwheel
from . import gearring
from . import gearbar
from . import split_gearwheel
from . import epicyclic_gearing
from . import axle_lid
from . import motor_lid
from . import bell
from . import bagel
from . import bell_bagel_assembly
from . import crest
from . import cross_cube
from . import gimbal
from . import low_torque_transmission

################################################################
# Cnc25d Designs
################################################################

## wood structure
box_wood_frame = box_wood_frame.box_wood_frame
#hexa_bone = hexa_bone.hexa_bone

## gear
# gear back-office
gear_profile = gear_profile.gear_profile
# standard gear
gearwheel = gearwheel.gearwheel
gearring = gearring.gearring
gearbar = gearbar.gearbar
# advanced gear
split_gearwheel = split_gearwheel.split_gearwheel
#gearlever = gearlever.gearlever
# gear system
epicyclic_gearing = epicyclic_gearing.epicyclic_gearing
axle_lid = axle_lid.axle_lid
motor_lid = motor_lid.motor_lid
#gear_train = gear_train.gear_train
ltt = low_torque_transmission.ltt

## gimbal
bell = bell.bell
bagel = bagel.bagel
bba = bell_bagel_assembly.bba
crest = crest.crest
cross_cube = cross_cube.cross_cube
gimbal = gimbal.gimbal


