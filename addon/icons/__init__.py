import bpy
import bpy.utils.previews
import os


pcoll = None


def id(identifier):
    global pcoll
    return pcoll[identifier.lower()].icon_id


def register():
    global pcoll
    pcoll = bpy.utils.previews.new()
    directory = os.path.dirname(__file__)

    for filename in os.listdir(directory):
        if filename.lower().endswith('.png'):
            name = filename.lower()[0:-4]
            path = os.path.join(directory, filename)
            pcoll.load(name, path, 'IMAGE')


def unregister():
    global pcoll
    bpy.utils.previews.remove(pcoll)
