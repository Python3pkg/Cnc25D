=====================
Box Wood Frame Design
=====================

1. Box wood frame presentation
==============================

*Box wood frame* is the name of this piece of furniture:

.. image:: images/box_wood_frame_snapshot_overview_1.png
.. image:: images/box_wood_frame_snapshot_overview_2.png

Its main characteristic is its top and bottom fittings that lets pile-up a *Box wood frame* over an other:

.. image:: images/box_wood_frame_snapshot_fitting_top.png
.. image:: images/box_wood_frame_snapshot_fitting_down.png

This *pile-up* functionality has several goals:

- split the manufacturing of large wardrobe into several small modules
- make easier the move of furniture
- be part of the structure of *straw houses*.

The *Box wood frame* design uses complex and precise recessed fittings to assemble the planks. So the cuts of the planks must be done with a CNC_ or with a manual `wood router`_ and templates. Then the planks can be glued together.

2. Box wood frame creation
==========================

After installing FreeCAD_ and the Python package Cnc25D_ as described at the paragraph :ref:`cnc25d_installation`, run the executable *cnc25d_example_generator.py* in the directory where you want to create the *Box wood frame*::

  > cd /directory/where/I/want/to/create/a/box/wood/frame/
  > cnc25d_example_generator.py # answer 'y' or 'yes' when it asks you to generate the example  box_wood_frame_example.py
  > python box_wood_frame_example.py

After several minutes of computation, you get all files that let you manufacture a *Box wood frame*. Read the *text_report.txt* files to get further information on your generated *Box wood frame* and on the descriptions of the other generated files.

Your *Box wood frame* has been generated with the default parameters. You may want to changes these parameter values to adapt them to your need. Edit the file *box_wood_frame_example.py*, change some parameters values, save your changes and run again::

  > python box_wood_frame_example.py

Now you get the *Box wood frame* design files according to your parameters.

3. Box wood frame parameters
============================

3.1. bwf_box_width
------------------
bwf_box_width = 400.0

3.2. bwf_box_depth
------------------
bwf_box_depth = 400.0

recommendation: keep bwf_box_depth = bwf_box_width to get more pile up possibilities

3.3. bwf_box_height
-------------------
bwf_box_height = 400.0

3.4. bwf_fitting_height
-----------------------
bwf_fitting_height = 30.0

3.5. bwf_h_plank_width
----------------------
bwf_h_plank_width = 50.0

3.6. bwf_v_plank_width
----------------------
bwf_v_plank_width = 30.0

3.7. bwf_plank_height
---------------------
bwf_plank_height = 20.0

3.8. bwf_d_plank_width
----------------------
bwf_d_plank_width = 30.0

3.9. bwf_d_plank_height
-----------------------
bwf_d_plank_height = 10.0

3.10. bwf_crenel_depth
----------------------
bwf_crenel_depth = 5.0

3.11. bwf_wall_diagonal_size
----------------------------
bwf_wall_diagonal_size = 50.0

3.12. bwf_tobo_diagonal_size
----------------------------
bwf_tobo_diagonal_size = 100.0

3.13. bwf_diagonal_lining_top_height
------------------------------------
bwf_diagonal_lining_top_height = 20.0

3.14. bwf_diagonal_lining_bottom_height
---------------------------------------
bwf_diagonal_lining_bottom_height = 20.0

3.15. bwf_module_width
----------------------
bwf_module_width = 1

3.16. bwf_reamer_radius
-----------------------
bwf_reamer_radius = 2.0

3.17. bwf_cutting_extra
-----------------------
bwf_cutting_extra = 2.0 # doesn't affect the cnc cutting plan

3.18. bwf_slab_thickness
------------------------
bwf_slab_thickness = 0.0 # set it bigger than 0 if you want to get the slab too

3.19. bwf_output_file_basename
------------------------------
bwf_output_file_basename = "" # set a not-empty string if you want to generate the output files
#bwf_output_file_basename = "my_output_dir/" 
#bwf_output_file_basename = "my_output_dir/my_output_basename" 
#bwf_output_file_basename = "my_output_basename" 


4. Box wood frame conception
============================

The notes relative to process of conception of the *Box wood frame* are available in the chapter :doc:`box_wood_frame_conception`.

5. Box wood frame manufacturing
===============================
As you can see in the design files, the outline of the planks are quiet complex. Those many recessed fittings enable a solid assembly. To cut the planks precisely according to design files you have two methods:

- Use a 3-axis CNC_
- Use a manual `wood router`_ and templates for each type of planks.

Notice that you need a CNC to make the templates.

The CNC method is well adapted when you want just few pieces of *Box wood frame*. The planks are cut in large plywood slabs (long and wide). This increase the final price of a *Box wood frame* module.

After getting the templates fitting your *Box wood frame* parameters, you can use a manual route to duplicate the planks. As raw material you can use solid wood plank (long and narrow). This is cheaper and provide a stronger assembly.

.. _FreeCAD : http://www.freecadweb.org/
.. _Cnc25D : https://pypi.python.org/pypi/Cnc25D
.. _CNC : http://en.wikipedia.org/wiki/CNC_wood_router
.. _`wood router` : http://en.wikipedia.org/wiki/Wood_router
