# import importlib
# import cadquery as cq
from watchy_sizes import *

# path to Watchy model downloaded from https://github.com/sqfmi/watchy-hardware/raw/main/3D/Watchy.step
watchy_model_path = '/path/to/Watchy.step'
show_watchy = False

# New params
p_tolerance = 0.5 # Tolerance for pcb w / h
p_ledge_h = pcb_y_to_slot + pcb_slot_h + 1.5 # top and bottom inner "ledge"
p_strap_width = 24 + 0.5 # strap width inc. tolerance
p_strap_dia = 4.0 # diameter of strap edge
p_tbar_space_height = p_strap_dia + 0.5 # space to cut in case for strap edge
p_tbar_hole_r = 0.5 # Radius of t-bar pin
p_under_pcb_depth = 8.0 # space for battery, etc.
p_inset_depth = pcb_t # depth of inset for pcb
p_flipFastener = True # should flip fastener (true for prod)
p_pcb_wall_thickness = 0.0 # thickness of walls around pcb inset
p_fastener_width = pcb_w * 0.5 # width of fasteners

# Cover params
p_screen_th = 1.2 # thickness of screen (including adhesive tape)
p_top_sheet_th = 0.6 # thickness of top "cover sheet" - should be as thin as possible
p_screen_from_pcb_top = 4.0
p_screen_h = 38.0
p_screen_w = 32.0
p_screen_margin = 1.5
p_flipTop = True # should flip the top

top_th = p_screen_th + p_top_sheet_th

pcb_inset_width = pcb_w + p_tolerance
pcb_inset_height = pcb_h + p_tolerance

#parameter definitions
p_thickness =  1.0 #Thickness of the box walls

p_outerWidth = pcb_inset_width + 2.0 * p_pcb_wall_thickness # Total outer width of box enclosure
p_outerLength = pcb_inset_height + 2.0 * p_pcb_wall_thickness #Total outer length of box enclosure
p_outerHeight = p_under_pcb_depth + p_thickness + p_inset_depth #Total outer height of box enclosure

p_sideRadius = pcb_radius #Radius for the curves around the sides of the box
p_topAndBottomRadius =  p_outerHeight * 0.5 #Radius for the curves on the top and bottom edges of the box
p_topAndBottomRadiusInner =  p_topAndBottomRadius

p_screwpostID = 2.5 #Inner Diameter of the screw post holes, should be roughly screw diameter not including threads

p_boreDiameter = 4.5 #Diameter of the counterbore hole, if any
p_boreDepth = 0.5 #Depth of the counterbore hole, if
p_countersinkDiameter = 0.0 #Outer diameter of countersink.  Should roughly match the outer diameter of the screw head
p_countersinkAngle = 90.0 #Countersink angle (complete angle between opposite sides, not from center to one side)

# Watchy model
if show_watchy:
  watchy = cq.importers.importStep(watchy_model_path)
  watchy = (watchy
    .rotateAboutCenter((0,1,0), 180)
    .translate((-pcb_w / 2.0 + 0.8, -pcb_h / 2.0, p_outerHeight - p_inset_depth - 0.5))
  )
  debug(watchy)

#outer shell
oshell = (cq.Workplane("XY")
  .rect(p_outerWidth, p_outerLength)
  .extrude(p_outerHeight)
)

#weird geometry happens if we make the fillets in the wrong order
if p_sideRadius > p_topAndBottomRadius:
    oshell = oshell.edges("|Z").fillet(p_sideRadius)
    oshell = oshell.edges("#Z").fillet(p_topAndBottomRadius)
else:
    #oshell = oshell.edges("#Z").fillet(p_topAndBottomRadius)
    #oshell = oshell.edges(cq.NearestToPointSelector((0,0,0))).fillet(p_topAndBottomRadius)
    oshell = oshell.edges("#Z and(not(>Z))").fillet(p_topAndBottomRadius)
    oshell = oshell.edges("|Z").fillet(p_sideRadius)

#inner shell
ishell = (oshell.faces("<Z").workplane(p_thickness,True)
    .rect((p_outerWidth - 2.0 * max(p_pcb_wall_thickness, p_thickness)),(pcb_h - 2.0*p_ledge_h))
    .extrude((p_outerHeight - p_thickness),False) #set combine false to produce just the new boss
)
ishell = (ishell.edges("|Z")
  .fillet(p_sideRadius - p_thickness)
  .edges(cq.NearestToPointSelector((0,0,0)))
  .fillet(p_topAndBottomRadiusInner)
)

#make the box outer box
box = oshell.cut(ishell)
# Emboss initials
box = (box
  .faces(cq.NearestToPointSelector((0,0,p_thickness)))
  .workplane()
  .text("GD", 5, -0.3, cut=True, kind='bold', font='Courier')
)

# Top strap hole
tbar_hole_depth = 1.5
strap_hole_y_offset = p_outerLength / 2.0 - p_strap_dia / 2.0 + 1.0
tbar_top = (cq.Workplane("ZY")
  .workplane(
    origin=(0, strap_hole_y_offset, 0), 
    offset=(-p_strap_width / 2.0))
  .circle(p_tbar_space_height)
  .extrude(p_strap_width)
  .workplane(
    origin=(0, p_outerLength / 2.0 - p_topAndBottomRadius + p_strap_dia / 2.0 + 0.3, p_strap_dia / 2.0 + 0.1), 
    offset=(-p_strap_width / 2.0 - tbar_hole_depth))
  .circle(p_tbar_hole_r)
  .extrude(p_strap_width + tbar_hole_depth * 2.0)
)

# Bottom strap hole
tbar_bottom = (cq.Workplane("ZY")
  .workplane(
    origin=(0, -strap_hole_y_offset, 0), 
    offset=(-p_strap_width / 2.0))
  .circle(p_tbar_space_height)
  .extrude(p_strap_width)
  .workplane(
    origin=(0, -(p_outerLength / 2.0 - p_topAndBottomRadius + p_strap_dia / 2.0 + 0.3), p_strap_dia / 2.0 + 0.1), 
    offset=(-p_strap_width / 2.0 - tbar_hole_depth))
  .circle(p_tbar_hole_r)
  .extrude(p_strap_width + tbar_hole_depth * 2.0)
)
with_tbars = box.cut(tbar_top).cut(tbar_bottom)

# side cuts (buttons, etc)
pcb_top = pcb_h / 2.0
pcb_top_to_top_button = 7.5
top_button_to_usb = 7.5
usb_to_bottom_button = 6.5
button_width  = 4.6
button_height = 2.0
usb_b_width  = 7.4
usb_b_height = 3.0

holes_left = (cq.Workplane("YZ")
  .moveTo(pcb_top - (pcb_top_to_top_button - button_height), p_outerHeight)
  .vLine(-p_inset_depth)
  .tangentArcPoint((-button_height, -button_height))
  .hLine(-button_width)
  .hLine(-(top_button_to_usb - (usb_b_height - button_height)))
  .line(-(usb_b_height - button_height), -(usb_b_height - button_height))
  .hLine(-usb_b_width)
  .line(-(usb_b_height - button_height), (usb_b_height - button_height))
  .hLine(-(usb_to_bottom_button - (usb_b_height - button_height)))
  .hLine(-button_width)
  .tangentArcPoint((-button_height, button_height))
  .vLine(p_inset_depth)
  .close()
  .extrude(-p_outerWidth / 2.0)
)

top_button_to_vib = 5.5
vib_to_bottom_button = 6.0
vib_motor_width  = 10.0
vib_motor_height = 2.8

holes_right = (cq.Workplane("YZ")
  .moveTo(pcb_top - (pcb_top_to_top_button - button_height), p_outerHeight)
  .vLine(-p_inset_depth)
  .tangentArcPoint((-button_height, -button_height))
  .hLine(-button_width)
  .hLine(-(top_button_to_vib - (vib_motor_height - button_height)))
  .line(-(vib_motor_height - button_height), -(vib_motor_height - button_height))
  .hLine(-vib_motor_width)
  .line(-(vib_motor_height - button_height), (vib_motor_height - button_height))
  .hLine(-(vib_to_bottom_button - (vib_motor_height - button_height)))
  .hLine(-button_width)
  .tangentArcPoint((-button_height, button_height))
  .vLine(p_inset_depth)
  .close()
  .extrude(p_outerWidth / 2.0)
)

with_side_holes = with_tbars.cut(holes_left).cut(holes_right)

# pcb inset
slot_post_dia = pcb_slot_h - 0.1
pcb_inset = (cq.Workplane("XY")
  .workplane(offset=p_outerHeight)
  .rect(pcb_inset_width, pcb_inset_height)
  .moveTo(0,0)
  .rect(pcb_w - 2.0 * pcb_x_to_slot - pcb_slot_h, pcb_h - 2.0 * pcb_y_to_slot - pcb_slot_h, forConstruction=True)
  .vertices()
  .circle(slot_post_dia / 2.0)
  .extrude(-p_inset_depth)
  .edges("|Z")
  .fillet(pcb_radius)
)
with_inset = with_side_holes.cut(pcb_inset)

# Top
fastener_hole_point = (0, p_outerHeight * 0.75 - 0.2)
poleCenters = [(0, pcb_h / 2.0 - pcb_y_to_slot - pcb_slot_h / 2.0), (0, -(pcb_h / 2.0 - pcb_y_to_slot - pcb_slot_h / 2.0))]
screen_window_size = p_screen_w - 2.0 * p_screen_margin
pole_hole_depth = p_outerHeight / 2.0 - 0.5

# basic shape
top = (cq.Workplane("XY")
  .workplane(offset=p_outerHeight)
  .rect(pcb_inset_width, pcb_inset_height)
  .extrude(top_th)
  .edges("|Z")
  .fillet(pcb_radius)
)  
# poles
pole_thickness = pcb_slot_h - 0.5
top = (top.faces("<Z")
  .workplane(offset=0)
  .pushPoints(poleCenters)
  .rect(p_fastener_width, pole_thickness)
  .extrude(pole_hole_depth)
  .faces(">Y")
  .workplane(origin=(0, 0, 0), offset=0.0)
  .pushPoints( [ fastener_hole_point])
  .hole(p_screwpostID, p_outerLength)
)
# screen holes
top = (top.faces(">Z")
  # inset
  .workplane(origin=(0, pcb_inset_height/2.0 - p_screen_from_pcb_top - p_screen_h / 2.0, 0),offset=-p_top_sheet_th)
  .rect(p_screen_w + p_tolerance, p_screen_h)
  .cutBlind(-p_screen_th)
   # window
  .faces(">Z")
  .workplane(origin=(0, pcb_inset_height/2.0 - p_screen_from_pcb_top - p_screen_margin - screen_window_size / 2.0, 0), offset=0)
  .rect(screen_window_size, screen_window_size + 2.0 * p_tolerance)
  .cutBlind(-p_screen_th)
  .edges(">Z")
  .fillet(0.5)
)

# decorations
top = (top.faces(">Z")
  .workplane(origin=(0, 0, 0), offset=0)
  .pushPoints( [ 
    (0, -pcb_inset_height/2.0, 0),
    (0, pcb_inset_height/2.0, 0)
  ])
  .rect(p_strap_width ,5.0)
  .cutBlind(-0.5, taper=60)
)

# Add "WATCHY" text
#top = (top.faces(">Z")
#  .workplane(origin=(0, -p_screen_h/2.0 + 2.5, 0))
#  .text("WATCHY", 4, 0.3, cut=False, combine=True, kind='bold', font='Sans')
#)

debug(top)

pole_holes = (cq.Workplane("XY")
  .workplane(offset=p_outerHeight)
  .pushPoints(poleCenters)
  .rect(p_fastener_width + p_tolerance, pole_thickness + p_tolerance)
  .extrude(-(pole_hole_depth  + p_tolerance / 2.0))
)

with_top_holes = (with_inset
  .faces("|Y and >Y")
  .workplane(origin=(0, 0, 0), offset=0.0)
  .pushPoints( [ fastener_hole_point])
  #.hole(p_screwpostID, p_outerLength)
  .cboreHole(p_screwpostID, p_boreDiameter, p_boreDepth)
  .faces("|Y and <Y")
  .workplane(origin=(0, 0, 0), offset=0.0)
  .pushPoints( [ fastener_hole_point])
  #.hole(p_screwpostID, p_outerLength)
  .cboreHole(p_screwpostID, p_boreDiameter, p_boreDepth)
  .cut(pole_holes) 
)

if p_flipTop:
  top = (top
    .translate((-p_outerWidth - 1.0, 0, -(p_outerHeight+top_th)))
    .rotate((0,0,0),(0,1,0), 180)
    #.rotate((0,0,0),(0,1,0), 90)
    #.translate((p_outerWidth/2.0, 0, (p_outerWidth/2.0)))
)
else:
  top = (top
    .translate((-p_outerWidth - 1.0, 0, -(p_outerHeight-pole_hole_depth)))
  )

result = (with_top_holes
  .union(top)
)

#return the combined result
show_object(result)
cq.exporters.export(result, "watchy-layers.stl")
#cq.exporters.export(top, "watchy-layers-top-only.stl")
