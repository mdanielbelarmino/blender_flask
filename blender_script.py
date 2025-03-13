import bpy
import math
import datetime
import sys

# Get arguments passed to the script (after the '--' separator)
args = sys.argv[sys.argv.index('--') + 1:]

args_str = ''.join(args)

lists = args_str.split(',')
object_lists = ['Body'] + lists + ['Eyes']


current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

# Set the filepath where you want to save the STL file
output_filepath = f"/tmp/SadTom.stl"  # Change this to your desired path


for obj in bpy.context.scene.objects:
   if obj.name in object_lists:#'Body', 'Eyes', 'Shirt', 'HoodieJacket', 'Pants', '']:
       obj.hide_set(False)
       obj.select_set(True)


# Join
# Ensure you're in Object mode
if bpy.context.object:
   bpy.ops.object.mode_set(mode='OBJECT')

# Deselect all objects first
bpy.ops.object.select_all(action='DESELECT')

# Loop through all objects in the scene and select only the visible ones
for obj in bpy.context.scene.objects:
   if obj.visible_get():  # Check if the object is visible in the viewport
       obj.select_set(True)  # Select the visible object

# # Subsurf
# for obj in bpy.context.selected_objects:    
#    if obj.type == 'MESH':    
#        bpy.context.view_layer.objects.active = obj
#        bpy.ops.object.modifier_add(type='SUBSURF')
#        # Get the modifier reference
#        modifier = bpy.context.object.modifiers[-1]

#        # Set subdivision levels for viewport and render
#        modifier.levels = 2  # For viewport
#        modifier.render_levels = 2  # For render
#        bpy.ops.object.modifier_apply(modifier=modifier.name)

# If any object is selected, set the first selected object as the active one and join
selected_objects = bpy.context.selected_objects
if selected_objects:
   bpy.context.view_layer.objects.active = selected_objects[0]  # Set the first selected object as active
   bpy.ops.object.join()  # Join all selected objects into the active one

# Remesh
for obj in bpy.context.selected_objects:
   if obj.type == 'MESH':    
       bpy.context.view_layer.objects.active = obj
       bpy.ops.object.modifier_add(type='REMESH')
       bpy.context.object.modifiers["Remesh"].mode = 'VOXEL'
       bpy.context.object.modifiers["Remesh"].voxel_size = 0.02 #0.01
       bpy.ops.object.modifier_apply(modifier="Remesh")
       
# Decimate
for obj in bpy.context.selected_objects:
   if obj.type == 'MESH':    
       bpy.context.view_layer.objects.active = obj
       bpy.ops.object.modifier_add(type='DECIMATE')
       bpy.context.object.modifiers["Decimate"].ratio = 0.8
       bpy.ops.object.modifier_apply(modifier="Decimate")

# geometry_cleaner.py

'''
Get percentage of files processed

Parameters: 'params' as dictionary
Returns: float
'''
def get_percentage(params):
   return math.floor(
       (params['processed'] / params['total']) * 100
   )

'''
Get estimated time remaining in minutes

Parameters: 'params' as dictionary
Returns: float
'''
def get_time_remaining(params):
   delta = datetime.datetime.today() - params['start_time']
   
   if (params['processed'] == 0):
       return -1
   else:
       time_per_object = delta.total_seconds() / params['processed'] / 60
       return time_per_object * (params['total'] - params['processed'])

'''
Print statistics for object

Parameters: 'params' as dictionary, 'ob' as Blender object
Returns: nothing
'''
def print_statistics(params, ob):
   percentage = get_percentage(params)
   
   time_remaining = get_time_remaining(params)
   if (time_remaining == -1):
       time_remaining = "---"
   else:
       time_remaining = round(time_remaining, 2)
       
   print(
       "({0}% / {1} min remaining) Processing '{2}'...".format(
           str(percentage),
           str(time_remaining),
           ob.name
       )
   )

'''
Cleans object-specific data

Parameters: 'ob' as Blender object
Returns: nothing
'''
def clean_object_data(ob):
   # Ensure object mode
   if ob.mode != 'OBJECT':
       bpy.ops.object.mode_set(mode='OBJECT')
   
   # Set object as active
   bpy.context.view_layer.objects.active = ob
   
   # Remove custom normals
   bpy.ops.mesh.customdata_custom_splitnormals_clear()
   
   # Remove parenting and normalize transforms
   bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
   bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
   
   # Set autosmooth
   # bpy.context.object.data.use_auto_smooth = True

'''
Cleans geometry-specific data

Parameters: 'ob' as Blender object
Returns: nothing
'''
def clean_geometry_data(ob):
   # Ensure edit mode
   if ob.mode != 'EDIT':
       bpy.ops.object.mode_set(mode='EDIT')
       
   bpy.ops.mesh.select_all(action='SELECT')
               
   # Recalculate normals
   bpy.ops.mesh.normals_make_consistent(inside=False)
               
   # Convert tris to quads
   bpy.ops.mesh.tris_convert_to_quads()
           
   # Remove doubles
   bpy.ops.mesh.remove_doubles()
   
   # Return to object mode before exiting
   bpy.ops.object.mode_set(mode='OBJECT')
   
'''
Clean scene meshes
Returns: nothing
'''
def clean(selected_only=True):
   view_layer = bpy.context.view_layer
   
   params = {
       "processed": 0,
       "total": len(view_layer.objects),
       "start_time": datetime.datetime.today()
   }

   if selected_objects:
      obj = bpy.context.active_object
      print_statistics(params, obj)
      clean_object_data(obj)
      clean_geometry_data(obj)
       
      params['processed'] += 1
   else:
   
      for ob in view_layer.objects:
         if ob.type == 'MESH':
            print_statistics(params, ob)
            clean_object_data(ob)
            clean_geometry_data(ob)
               
            params['processed'] += 1
           
   bpy.ops.object.select_by_type(type='EMPTY')
   bpy.ops.object.delete(use_global=False)

   print("\nDone!\n")

clean()


# Export STL

# Ensure you are in object mode
if bpy.context.object:
    bpy.ops.object.mode_set(mode='OBJECT')

## Deselect all objects again
#bpy.ops.object.select_all(action='DESELECT')

# Export the selected objects to an STL file
bpy.ops.wm.stl_export(filepath=str(output_filepath))