import bpy
from math import radians, degrees, cos, acos, sin


def makeMaterial(name, diffuse, specular, alpha):
    # color changing code from http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Materials_and_textures
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5
    mat.alpha = alpha
    mat.ambient = 1
    return mat


def setMaterial(ob, mat):
    me = ob.data
    me.materials.append(mat)


def setName(ob, name):
    ob.name = name


def placeSphere(x, y, z=0, size=1):
    '''Places a sphere at a specific location '''
    bpy.ops.mesh.primitive_uv_sphere_add(location=(x, y, z), size=size)


def selectGroup(group):
    ''' Selects objects in group '''
    for ob in group:
        ob.select = True


def groupSpheres(group, groupName=''):
    '''Puts objects in group in a blender group '''
    deselectAll()
    selectGroup(group)
    bpy.ops.group.create(name=groupName)
    deselectAll()


def rotateGroupByLocation(group, angle, location=(0, 0, 0)):
    '''Rotates the objects in group by an angle (in degrees) around a location (origin by default) '''
    radianAngle = radians(angle)
    deselectAll()
    selectGroup(group)
    # we need to override the context of our operator
    override = get_override('VIEW_3D', 'WINDOW')
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces[0].pivot_point = 'CURSOR'
    bpy.context.scene.cursor_location = location
    bpy.ops.transform.rotate(override, value=radianAngle, axis=(1, 0, 0))
    deselectAll()


def get_override(area_type, region_type):
    '''Black magic to enable rotating around the origin for all selected objects '''
    for area in bpy.context.screen.areas:
        if area.type == area_type:
            for region in area.regions:
                if region.type == region_type:
                    override = {'area': area, 'region': region}
                    return override
    # error message if the area or region wasn't found
    raise RuntimeError("Wasn't able to find", region_type, " in area ", area_type,
                       "\n Make sure it's open while executing script.")


def deselectAll():
    bpy.ops.object.select_all(action='DESELECT')


def clearScene():
    # cleaning the scene from http://wiki.blender.org/index.php/Dev:2.5/Py/Scripts/Cookbook/Code_snippets/Interface
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()


def calculateTiltAngle(first, second):
    '''http://onlinelibrary.wiley.com/doi/10.1002/jemt.1070280512/pdf'''
    keys = ['xAngle', 'yAngle']
    (a1, a2), (b1, b2) = [(radians(first[key]), radians(second[key])) for key in keys]
    total = acos(cos(b2 - b1) * cos(a1) * cos(a2) + sin(a1) * sin(a2))
    return degrees(total)


def parseInputFile(fileName):
    '''
    Parses an input file. The format is:
    ID: ID
    x: "x tilt angle"
    y: "y tilt angle"
    x0, y0
    x1, y1
    x2, x3
    ...
    Keep one space between each dataset


    '''
    data = {}
    with open(fileName) as f:

        while True:
                line = f.readline()
                if line == '':  # EOF
                    break
                if line.strip() == '':  # empty line
                    continue
                ID = line.split('ID:')[-1].strip()
                dataSet = dict()
                dataSet['xAngle'] = float(f.readline().split('x:')[-1].strip())
                dataSet['yAngle'] = float(f.readline().split('y:')[-1].strip())

                for line in iter(lambda: f.readline().strip(), ''):  # untill EOF or empty line
                    xy = [float(i) for i in line.split(',')]
                    dataSet.setdefault('Positions', []).append(xy)
                data[ID] = dataSet
    return data


def addDataToScene(data):
    print(data)
    first = None
    COLORS = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1)]
    for (ID, data), color in zip(data.items(), COLORS):
        if not first:
            first = data
        angle = calculateTiltAngle(data, first)
        color = makeMaterial(ID, color, (1, 1, 1), 1)
        group = []
        for j, spot in enumerate(data['Positions']):
            x, y = spot
            placeSphere(x, y, size=0.5)
            setName(bpy.context.object, '{0}_{1}'.format(ID, str(j)))
            setMaterial(bpy.context.object, color)
            group.append(bpy.context.object)
        groupSpheres(group, ID)
        rotateGroupByLocation(group, angle)
