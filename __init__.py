bl_info = {
    "name": "Combined Addon: Texture Upscaler & 3Ds Dota Fixer",
    "author": "neverminder",
    "version": (1, 5, 0),
    "blender": (3, 6, 0),
    "location": "Image Editor > N-Panel and View3D > Sidebar",
    "description": "Addon that combines functionalities of Texture Upscaler and 3Ds Dota Fixer",
    "category": "System",
}

import bpy
from .model import *
from . import texture_upscaler
from . import dota_fixer

def register():
    texture_upscaler.register()
    dota_fixer.register()

def unregister():
    dota_fixer.unregister()
    texture_upscaler.unregister()

if __name__ == "__main__":
    register()
