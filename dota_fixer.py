import bpy
from bpy.props import IntProperty, BoolProperty, EnumProperty, FloatProperty, PointerProperty

def update_merge_threshold(self, context):
    new_val = round(self.merge_threshold / 0.0001) * 0.0001
    if new_val != self.merge_threshold:
        self.merge_threshold = new_val

class ParentToolSettings(bpy.types.PropertyGroup):
    use_subdivision: BoolProperty(
        name="Добавить Subdivision",
        description="Если включено, к мешам будет добавлен модификатор Subdivision Surface",
        default=False,
    )
    subdivision_viewport: IntProperty(
        name="Subdivision (Viewport)",
        description="Уровень детализации Subdivision для Viewport",
        default=2,
        min=0,
        max=6,
    )
    subdivision_render: IntProperty(
        name="Subdivision (Render)",
        description="Уровень детализации Subdivision для Render",
        default=2,
        min=0,
        max=6,
    )
    clear_normals: BoolProperty(
        name="Очистка нормалей",
        description="Очистить кастомные нормали у мешей",
        default=True,
    )
    merge_by_distance: BoolProperty(
        name="Merge by Distance",
        description="Объединить близкие вершины в мешах",
        default=True,
    )
    merge_threshold: FloatProperty(
        name="Merge порог",
        description="Порог для объединения близких вершин",
        default=0.0001,
        min=0.0001,
        max=0.005,
        precision=6,
        update=update_merge_threshold,
    )
    apply_shade_smooth: BoolProperty(
        name="Shade Smooth",
        description="Применить Shade Smooth к мешам",
        default=True,
    )
    remove_extraneous: BoolProperty(
        name="Удаление лишних костей",
        description="Удалить лишние модификаторы и арматуры (оставить только выбранную)",
        default=True,
    )
    parent_binding: EnumProperty(
        name="Тип родительского связывания",
        description="Выбор типа родительского связывания",
        items=[
            ('OBJECT', "OBJECT", "Привязка как OBJECT"),
            ('ARMATURE', "ARMATURE", "Привязка как ARMATURE"),
            ('ARMATURE_AUTO', "ARMATURE_AUTO", "Автоматическое назначение веса (ARMATURE_AUTO)"),
        ],
        default='OBJECT',
    )
    apply_modifiers: BoolProperty(
        name="Применить модификаторы",
        description="Автоматически применить все модификаторы после привязки",
        default=False,
    )

def parent_objects_to_armature(context, settings):
    bpy.ops.object.mode_set(mode='OBJECT')

    armature = None
    if context.object and context.object.type == 'ARMATURE':
        armature = context.object
    else:
        for obj in context.selected_objects:
            if obj.type == 'ARMATURE':
                armature = obj
                break
    if not armature:
        context.window_manager.popup_menu(
            lambda self, context: self.layout.label(text="Выберите арматуру!"),
            title="Ошибка", icon='ERROR'
        )
        return {'CANCELLED'}

    context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')

    selected_bones = [pbone.bone.name for pbone in armature.pose.bones if pbone.bone.select]
    if not selected_bones:
        bpy.ops.object.mode_set(mode='OBJECT')
        context.window_manager.popup_menu(
            lambda self, context: self.layout.label(text="Выберите кости в арматуре!"),
            title="Ошибка", icon='ERROR'
        )
        return {'CANCELLED'}

    bpy.ops.object.mode_set(mode='EDIT')
    for bone in list(armature.data.edit_bones):
        if bone.name not in selected_bones:
            armature.data.edit_bones.remove(bone)
    bpy.ops.object.mode_set(mode='OBJECT')

    current_bones = [bone.name for bone in armature.data.bones]

    for obj in list(context.scene.objects):
        if obj.type == 'MESH' and obj != armature:
            context.view_layer.objects.active = obj

            if settings.clear_normals and obj.data.has_custom_normals:
                prev_mode = obj.mode
                if prev_mode != 'EDIT':
                    bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
                bpy.ops.object.mode_set(mode='OBJECT')

            if settings.merge_by_distance:
                prev_mode = obj.mode
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.remove_doubles(threshold=settings.merge_threshold)
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.mesh.select_mode(type='FACE')
                bpy.ops.mesh.select_interior_faces()
                bpy.ops.mesh.delete(type='FACE')
                bpy.ops.object.mode_set(mode=prev_mode)

            if settings.use_subdivision:
                found_subsurf = False
                for mod in obj.modifiers:
                    if mod.type == 'SUBSURF':
                        mod.levels = settings.subdivision_viewport
                        mod.render_levels = settings.subdivision_render
                        mod.subdivision_type = 'SIMPLE'
                        found_subsurf = True
                if not found_subsurf:
                    subsurf_mod = obj.modifiers.new("Subdivision", 'SUBSURF')
                    subsurf_mod.levels = settings.subdivision_viewport
                    subsurf_mod.render_levels = settings.subdivision_render
                    subsurf_mod.subdivision_type = 'SIMPLE'

            if settings.apply_shade_smooth:
                bpy.ops.object.shade_smooth()

            if settings.remove_extraneous:
                for mod in obj.modifiers[:]:
                    if mod.type == 'ARMATURE':
                        obj.modifiers.remove(mod)

            for vg in obj.vertex_groups[:]:
                if vg.name not in current_bones:
                    obj.vertex_groups.remove(vg)

            if settings.parent_binding == 'ARMATURE_AUTO':
                bpy.ops.object.select_all(action='DESELECT')
                armature.select_set(True)
                obj.select_set(True)
                context.view_layer.objects.active = armature
                bpy.ops.object.parent_set(type='ARMATURE_AUTO')
            else:
                obj.parent = armature
                obj.parent_type = settings.parent_binding
                arm_mod = obj.modifiers.new("Armature", 'ARMATURE')
                arm_mod.object = armature

    if settings.remove_extraneous:
        for obj in list(context.scene.objects):
            if obj.type == 'ARMATURE' and obj != armature:
                bpy.data.objects.remove(obj, do_unlink=True)

    if settings.apply_modifiers:
        for obj in list(context.scene.objects):
            if obj.type == 'MESH' and obj != armature:
                context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='OBJECT')
                mod_names = [mod.name for mod in obj.modifiers]
                for mod_name in mod_names:
                    try:
                        bpy.ops.object.modifier_apply(modifier=mod_name)
                    except Exception as e:
                        print("Ошибка применения модификатора", mod_name, "для объекта", obj.name, ":", e)

    return {'FINISHED'}

class PARENT_OT_ObjectsToArmature(bpy.types.Operator):
    """Привязывает меши к выбранной арматуре с дополнительными настройками"""
    bl_idname = "object.parent_to_armature"
    bl_label = "Привязать объекты к скелету"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.parent_tool_settings
        result = parent_objects_to_armature(context, settings)
        if result == {'CANCELLED'}:
            self.report({'WARNING'}, "Ошибка: выберите арматуру с выделенными костями!")
        return result

class PARENT_PT_Panel(bpy.types.Panel):
    """Панель для привязки объектов к скелету с дополнительными настройками"""
    bl_label = "Инструмент Привязки"
    bl_idname = "PARENT_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '3Ds Dota Fixer'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.parent_tool_settings

        box_options = layout.box()
        box_options.label(text="Дополнительные настройки", icon='PREFERENCES')
        box_options.prop(settings, "use_subdivision", text="Добавить Subdivision")
        if settings.use_subdivision:
            box_options.label(text="Настройки Subdivision", icon='MOD_SUBSURF')
            box_options.prop(settings, "subdivision_viewport", text="Viewport")
            box_options.prop(settings, "subdivision_render", text="Render")
        box_options.prop(settings, "clear_normals")
        box_options.prop(settings, "merge_by_distance")
        box_options.prop(settings, "apply_shade_smooth")

        layout.separator()
        layout.operator(PARENT_OT_ObjectsToArmature.bl_idname, text="Привязать объекты к скелету", icon='ARMATURE_DATA')

class ClearPoseOperator(bpy.types.Operator):
    """Сбросить позу и выбрать все кости"""
    bl_idname = "pose.clear_pose_and_select_all"
    bl_label = "Сбросить позу (без Rest Pose)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if not obj or obj.type != 'ARMATURE':
            self.report({'WARNING'}, "Выберите объект с арматурой")
            return {'CANCELLED'}
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()
        bpy.ops.object.mode_set(mode='OBJECT')
        self.report({'INFO'}, "Поза сброшена")
        return {'FINISHED'}


class AnimationFixOperator(bpy.types.Operator):
    """Применить фильтр Discontinuity (Euler) ко всем ключам анимации"""
    bl_idname = "pose.animation_fix_v1"
    bl_label = "Animation Fix v1"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if not obj or obj.type != 'ARMATURE':
            self.report({'WARNING'}, "Выберите арматуру!")
            return {'CANCELLED'}

        # Переключиться в режим позы и выбрать все кости
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')

        # Сохраняем текущий тип области и регион
        original_area_type = context.area.type
        original_region = context.region

        try:
            # Меняем тип области на Graph Editor
            context.area.type = 'GRAPH_EDITOR'

            # Находим регион 'WINDOW' в Graph Editor
            region = None
            for r in context.area.regions:
                if r.type == 'WINDOW':
                    region = r
                    break
            if not region:
                self.report({'ERROR'}, "Не удалось найти регион WINDOW в Graph Editor")
                return {'CANCELLED'}

            # Создаем override контекста
            override = {
                'window': context.window,
                'screen': context.screen,
                'area': context.area,
                'region': region,
                'active_object': obj,
                'selected_objects': [obj],
            }

            # Применяем фильтр
            with context.temp_override(**override):
                bpy.ops.graph.select_all(action='SELECT')
                bpy.ops.graph.euler_filter()

        except Exception as e:
            self.report({'ERROR'}, f"Ошибка: {str(e)}")
            return {'CANCELLED'}

        finally:
            # Восстанавливаем исходный тип области
            context.area.type = original_area_type
            bpy.ops.object.mode_set(mode='OBJECT')
        self.report({'INFO'}, "Фильтр применен")
        return {'FINISHED'}

class ClearPosePanel(bpy.types.Panel):
    """Панель для сброса позы"""
    bl_label = "Clear Animation and Pose"
    bl_idname = "POSE_PT_clear_pose_and_animation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '3Ds Dota Fixer'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        if obj and obj.type == 'ARMATURE':
            layout.operator("pose.clear_pose_and_select_all", text="Сбросить позу", icon='TRACKING_BACKWARDS')
            layout.operator("pose.animation_fix_v1", text="Animation Fix v1", icon='GRAPH')
        else:
            layout.label(text="Выберите арматуру")

class PARENT_PT_InfoPanel(bpy.types.Panel):
    bl_label = "Информация"
    bl_idname = "PARENT_PT_info"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '3Ds Dota Fixer'
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Информация (Addon v1.6.0)", icon='INFO')
        box_info = layout.box()
        box_info.label(text="Three Dimensions:", icon='URL')
        op = box_info.operator("wm.url_open", text="Обучалки по Dota 3D")
        op.url = "https://t.me/dimension3Ds"
        box_info.separator()
        box_info.label(text="Баги и предложение писать мне:", icon='ERROR')
        op = box_info.operator("wm.url_open", text="t.me/neverminder_3ds")
        op.url = "https://t.me/neverminder_3ds"

classes_dota = [
    ParentToolSettings,
    PARENT_OT_ObjectsToArmature,
    PARENT_PT_Panel,
    ClearPoseOperator,
    AnimationFixOperator,
    ClearPosePanel,
    PARENT_PT_InfoPanel,
]

def register():
    for cls in classes_dota:
        bpy.utils.register_class(cls)
    bpy.types.Scene.parent_tool_settings = PointerProperty(type=ParentToolSettings)

def unregister():
    for cls in reversed(classes_dota):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.parent_tool_settings

if __name__ == "__main__":
    register()