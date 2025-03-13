from flask import send_file
from subprocess import call

def render(request):
    location = '/tmp/'
    suffix = 'SadTom.stl'
    filename = location + suffix

    # http://localhost:8080/?top=HoodieJacket&bottom=Pants
    
    top = request.args.get('top', default = '', type = str)
    bottom = request.args.get('bottom', default = '', type = str)
    
    blender_file = "models/Assets.blend"
    python_script = "blender_script.py"

    # Make STL
    call('blender -b %s -P %s -- %s,%s' % (blender_file, python_script, top, bottom), shell=True)
    
    return send_file(filename, mimetype='model/stl', as_attachment=True)