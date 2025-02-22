import threading
import bpy
import os
import subprocess
from .model import *
from .model import get_models

def replace_image_nodes(old_image, new_image):
    """Заменяет ссылки на старое изображение на новое во всех материалах"""
    for material in bpy.data.materials:
        if material.use_nodes and material.node_tree:
            for node in material.node_tree.nodes:
                # Проверяем, является ли нода нодой текстуры и содержит ли она изображение
                if node.type == 'TEX_IMAGE' and hasattr(node, "image") and node.image == old_image:
                    node.image = new_image
                    print(f"Replaced image in material: {material.name}")

class TU_image_Panel(bpy.types.Panel):
    """Panel to Upscale Textures"""
    bl_idname = "IMAGE_EDITOR_PT_texture_upscaler"
    bl_label = "Texture Upscaler"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Texture Upscaler"

    def draw(self, context):
        layout = self.layout
        image = context.space_data.image
        prop = context.preferences.addons[__package__].preferences

        # Чекбокс для апскейла всех изображений


        # Если имеется активное изображение, выводим его информацию
        if image:
            if bpy.app.version >= (4, 1, 0):
                info_header, info_panel = layout.panel_prop(context.scene, "TU_info")
                info_header.label(text="Image Info")
            else:
                info_panel = layout.column(align=True)
            if info_panel:
                col = info_panel.column(align=True)
                box = col.box()
                box.label(text=f'Image: {image.name}')
                box = col.box()
                box.label(text=f'Current Res: {image.size[0]}X{image.size[1]}')
                box = col.box()

                if prop.use_custom_width:
                    text = f'Upscale Res: {prop.custom_width}X{int((prop.custom_width / image.size[0]) * image.size[1])}'
                else:
                    text = f'Upscale Res: {image.size[0] * int(prop.scale)}X{image.size[1] * int(prop.scale)}'
                box.label(text=text)

            row = layout.row(align=True)
            row.prop(prop, 'replace_image', text='Replace in Materials', expand=True)

            row.prop(prop, "use_compress", icon="OBJECT_DATAMODE", text="")
            row.prop(prop, "use_custom_width", icon="MOD_LENGTH", text="")
            row = layout.row(align=True)
            row.prop(prop, "upscale_all", text="Upscale All Images")
            row = layout.row(align=True)
            row.label(text="Image Scale:")
            row.prop(prop, 'scale', text="")

            if prop.use_custom_width:
                row.active = False
                c_row = layout.row(align=True)
                c_row.label(text="Custom Width: ")
                c_row.prop(prop, "custom_width", text="")

            if prop.use_compress:
                c_row = layout.row(align=True)
                c_row.label(text="Compression: ")
                c_row.prop(prop, "compress", text="")

        else:
            layout.label(text="No Active Image in Image Editor", icon='ERROR')

        layout.prop(context.scene, 'models')
        label = "Upscale" if not prop.runing else "Please Wait..."
        layout.operator(TU_image_Upscaler.bl_idname, icon='STICKY_UVS_VERT', text=label)


class TU_image_Upscaler(bpy.types.Operator):
    """Upscales the active image or all images in the scene"""
    bl_idname = "active_image.upscale"
    bl_label = "Texture Upscaler"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return not context.preferences.addons[__package__].preferences.runing

    def modal(self, context, event: bpy.types.Event) -> set:
        prop = context.preferences.addons[__package__].preferences

        if event.type == 'TIMER':
            if self._is_updated:
                self.report({"INFO"}, f"Progress: {self._callback_rep}")
                self._is_updated = False
                return {'PASS_THROUGH'}

            if not prop.runing:
                if self._is_error:
                    self.report({"INFO"}, "Upscaling Failed 👎")
                else:
                    self.report({"INFO"}, "Upscaling Done 👍")
                return {'FINISHED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        prop = context.preferences.addons[__package__].preferences
        prop.runing = True

        model = context.scene.models
        scale = prop.scale
        addon_dir = os.path.dirname(os.path.realpath(__file__))
        ncnn_file = get_ncnn_path(addon_dir)

        self._callback_rep = None
        self._is_updated = False
        self._is_error = False

        if prop.upscale_all:
            # Обработка всех изображений в сцене
            def process_all_images():
                images = list(bpy.data.images)
                total = len(images)
                for idx, image in enumerate(images):
                    file_path = os.path.join(prop.path, f'{image.name}.{image.file_format.lower()}')
                    try:
                        image.save(filepath=file_path, quality=100)
                    except Exception as e:
                        print(f"Error saving image {image.name}: {e}")
                        continue
                    base, ext = os.path.splitext(image.name)
                    form = prop.out_format if prop.out_format != "Auto" else image.file_format.lower()
                    new_path = os.path.join(prop.path, f'{base}_{scale}x.{form}')
                    # Запускаем модель апскейла для данного изображения
                    self.run_model(image, prop, file_path, new_path, model, scale, ncnn_file,
                                   callback=lambda np, img: replace_image_nodes(img, bpy.data.images.load(np)) if prop.replace_image else None)
                    self._callback_rep = f"Upscaled {idx+1} of {total}"
                    self._is_updated = True
                prop.runing = False

            threading.Thread(target=process_all_images).start()
            self.report({"INFO"}, "Upscaling all images... 😎")
        else:
            # Обработка только активного изображения
            image = context.space_data.image
            if not image:
                self.report({"ERROR"}, "No active image!")
                prop.runing = False
                return {'CANCELLED'}
            file_path = os.path.join(prop.path, f'{image.name}.{image.file_format.lower()}')
            image.save(filepath=file_path, quality=100)
            base, ext = os.path.splitext(image.name)
            form = prop.out_format if prop.out_format != "Auto" else image.file_format.lower()
            new_path = os.path.join(prop.path, f'{base}_{scale}x.{form}')

            def callback(new_path, image):
                try:
                    upscaled_image = bpy.data.images.load(new_path)
                except Exception as e:
                    self._is_error = True
                    self._callback_rep = f"Error: {e}"
                    return
                if prop.replace_image:
                    replace_image_nodes(image, upscaled_image)
                context.space_data.image = upscaled_image
                prop.runing = False

            threading.Thread(
                target=self.run_model,
                args=(image, prop, file_path, new_path, model, scale, ncnn_file, callback)
            ).start()
            self.report({"INFO"}, "Upscaling... 😎")

        self._timer = context.window_manager.event_timer_add(0.01, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def run_model(self, image, prop, file_path, new_path, model, scale, ncnn_file, callback):
        command = [
            ncnn_file,
            "-i", file_path,
            "-o", new_path,
            "-n", model,
        ]
        if prop.use_custom_width:
            command.extend(["-w", str(prop.custom_width)])
        else:
            command.extend(["-s", str(scale)])
        if prop.use_compress:
            command.extend(["-c", str(prop.compress)])
        if prop.gpu != "Auto":
            command.extend(["-g", str(prop.gpu)])
        if prop.out_format != "Auto":
            command.extend(["-f", prop.out_format])
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       universal_newlines=True)
            for line in iter(process.stdout.readline, ""):
                print(line.strip())
                if "%" in line.strip():
                    self._callback_rep = line.strip()
                    self._is_updated = True
                elif " Error:" in line.strip():
                    prop.runing = False
                    self._is_error = True
                    self.report({'ERROR'}, f"{line.strip()}")
                    return {'CANCELLED'}
        except Exception as e:
            prop.runing = False
            self._is_error = True
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        callback(new_path, image)


class TU_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    path: bpy.props.StringProperty(
        name='Save Folder',
        description='Set the folder where you want to save images textures \nMake sure folder has permission to write',
        default='C:/temp',
        subtype='DIR_PATH'
    )
    scale: bpy.props.IntProperty(
        name="Image Scale",
        description="Number of Times the image get Scaled",
        default=4,
        min=1,
        max=16,
        subtype='FACTOR',
    )
    replace_image: bpy.props.BoolProperty(
        name='Replace Image',
        description='Replace texture in materials with upscaled texture',
        default=False
    )
    runing: bpy.props.BoolProperty(default=False)
    use_custom_width: bpy.props.BoolProperty(
        name="Use Custom Width",
        description="Upscale image to custom width instead of xScale",
        default=False
    )
    custom_width: bpy.props.IntProperty(
        name="Custom Width",
        description="Width of Upscaled Images in px",
        default=1920,
        min=200, max=10000,
        subtype="PIXEL"
    )
    use_compress: bpy.props.BoolProperty(
        name="Use Compression",
        description="Compress the Upscaled image to reduce size",
        default=False
    )
    compress: bpy.props.IntProperty(
        name="Amount of Compression in %",
        default=0,
        min=0, max=100,
        subtype="PERCENTAGE"
    )
    gpu: bpy.props.EnumProperty(items=[
        ('Auto', 'Auto', 'Auto'),
        ('0', 'Device 0', '0'),
        ('1', 'Device 1', '1'),
        ('2', 'Device 2', '2'),
    ],
        name='Select Gpu device',
        description="Gpu device to use For Upscaling \nLeave Auto if you are not sure \nDevice 0 is mostly Cpu and Device 1 and Device 2 is mostly Gpu",
        default='Auto'
    )
    out_format: bpy.props.EnumProperty(items=[
        ('Auto', 'Auto', 'Auto'),
        ('png', 'png', 'png'),
        ('jpg', 'jpg', 'jpg'),
        ('webp', 'webp', 'webp'),
    ],
        name='Select Output Format',
        description="Output Format of Upscaled Images. Leave it at Auto if you want the upscaled image to have the same format as original",
        default='Auto'
    )
    # Чекбокс для апскейла всех изображений
    upscale_all: bpy.props.BoolProperty(
        name="Upscale All Images",
        description="Upscale all images in the scene",
        default=False
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Add the path where the images will be saved.")
        layout.prop(self, "path")
        layout.prop(self, "gpu")
        layout.prop(self, "out_format")
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Option to add your custom ncnn Model", icon='INFO')
        col.operator("texture_upscaler.import_model", text="Add Model", icon='FILE_FOLDER')


classes_texture = (
    TU_image_Upscaler,
    TU_image_Panel,
    model_importer,
    TU_Preferences,
)

def register():
    bpy.types.Scene.models = bpy.props.EnumProperty(items=get_models())
    setattr(bpy.types.Scene, "TU_info", bpy.props.BoolProperty(default=True))
    for cls in classes_texture:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes_texture:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.models
    del bpy.types.Scene.TU_info

if __name__ == "__main__":
    register()
