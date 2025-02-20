[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/neverminder0/Dota-3Ds-Tools/blob/main/README.ru.md)
[![ru](https://img.shields.io/badge/lang-pt--br-green.svg)](https://github.com/neverminder0/Dota-3Ds-Tools/blob/main/README.md)
# Dota-3Ds-Tools
Blender Addon for snapping tools and texture scaling 
### **Texture Scaling and Snap Tools Addon**

This addon provides several useful functions for working with textures and meshes in Blender, including automating the texture scaling process, snapping objects to armatures, and other auxiliary functions.

#### **Main features of the addon:**

##### **1. Texture Upscaler:**
- **Texture Scaling:** The addon allows you to scale the textures of the active image in the image editor. You can specify a scaling factor or set a specific width for the output image.
- **Texture Replacement in Materials:** After scaling, the texture can be automatically replaced in the objects' materials.
- **Compression:** Ability to compress the output image to reduce its size.
- **GPU support:** You can select a GPU device to accelerate the scaling process.
- **Output format:** Select the format for saving the output image (PNG, JPG, WEBP).
- **Control panel:** Built-in panel in the image editor, where you can adjust the scaling parameters and monitor the progress of the operation.

##### **2. Tools for snapping objects to reinforcement:**
- **Snapping objects to reinforcement:** The addon allows you to automate the process of snapping objects (meshes) to reinforcement. Several types of snapping are supported: OBJECT, ARMATURE and ARMATURE_AUTO.
- **Additional settings:**
- **Subdivision Surface support:** Adds the Subdivision Surface modifier with the option to adjust the level of detail for Viewport and Render.
- **Cleaning normals:** Clearing custom normals for meshes before snapping.
- **Merge close vertices:** Merge close vertices to eliminate duplicate points.
- **Smoothing:** Automatically applies smoothing (Shade Smooth) to meshes.
- **Remove unnecessary modifiers:** Remove unnecessary modifiers and armatures after binding.
- **Apply modifiers:** Automatically apply all modifiers after completing the binding.

##### **3. Reset armature pose:**
- **Reset pose:** The addon allows you to reset the armature pose (including transformations), leaving the bones selected for further work.

##### **4. Additional panels and settings:**
- **Texture Upscaler panel:** Built-in panel in the image editor, where you can adjust the texture scaling parameters.
- **Bind toolbar:** Built-in panel in the 3D viewport, where you can adjust the parameters of binding objects to the armature.
- **Addon settings:** In the addon settings, you can specify the folder for saving textures, select the GPU device, output image format and other parameters.

#### **How ​​to use the addon:**

1. **Texture scaler:**
- Go to the image editor and select the texture you want to scale.
- In the Texture Upscaler panel, configure the scaling parameters (ratio, width, compression, format, etc.).
- Click the "Upscale" button to start the scaling process.

2. **Snapping objects to the armature:**
- Select the armature and objects to snap.
- Go to the Snap Tools panel and configure additional parameters (Subdivision, normal cleanup, vertex merging, etc.).
- Click the "Snap objects to skeleton" button.

3. **Reset Armature Pose:**
- Select the armature in the editor and click the "Reset Pose" button in the Clear Animation and Pose panel.

#### **Addon Settings:**
- **Texture Save Folder:** Specify the folder where the scaled textures will be saved.
- **GPU Device:** Select a GPU device to speed up the scaling process.
- **Output Image Format:** Select the output image format (PNG, JPG, WEBP).

