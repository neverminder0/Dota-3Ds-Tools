[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/neverminder0/Dota-3Ds-Tools/blob/main/README.md)
[![ru](https://img.shields.io/badge/lang-ru-green.svg)](https://github.com/neverminder0/Dota-3Ds-Tools/blob/main/README.ru.md)
# Dota 3Ds Tools for **Blender**<img src="https://github.com/tandpfun/skill-icons/raw/main/icons/Blender-Dark.svg" width="40"> ![image]({https://img.shields.io/badge/blender-%23F5792A.svg?style=for-the-badge&logo=blender&logoColor=white)


### **Texture Scaling and Snap Tools Addon**

This addon provides several useful functions for working with textures and meshes in Blender, including automation of the texture scaling process, snapping objects to an armature, and other auxiliary functions.

#### **Main features of the addon:**

##### **1. Texture Upscaler:**
- **Texture Scaling:** The addon allows you to scale the textures of the active image in the image editor. You can specify the scaling factor or set a specific width for the output image.
- **Texture Replacement in Materials:** After scaling, the texture can be automatically replaced in the materials of objects.
- **Compression:** Ability to compress the output image to reduce its size.
- **GPU support:** You can select a GPU device to accelerate the scaling process.
- **Output Format:** Select the format for saving the output image (PNG, JPG, WEBP).
- **Control Panel:** Built-in panel in the image editor where you can adjust the scaling parameters and monitor the progress of the operation.

##### **2. Tools for snapping objects to armatures:**
- **Advanced Settings:**
- **Subdivision Surface Support:** Adds a Subdivision Surface modifier with the option to adjust the level of detail for Viewport and Render.
- **Clean Up Normals:** Clean up custom normals on meshes before snapping.
- **Merge Close Vertices:** Merge close vertices to eliminate duplicate points.
- **Smoothing:** Automatically apply smoothing (Shade Smooth) to meshes.
- **Remove Unnecessary Modifiers:** Remove unnecessary modifiers and armatures after snapping.
- **Apply Modifiers:** Automatically apply all modifiers after snapping is complete.

##### **3. Reset armature pose:**
- **Reset pose:** The addon allows you to reset the armature pose (including transformations)

##### **4. Additional panels and settings:**
- **Texture Upscaler panel:** Built-in panel in the image editor, where you can configure the texture scaling parameters.
- **Binding toolbar:** Built-in panel in the 3D viewport, where you can configure the parameters for binding objects to the armature.
- **Addon settings:** In the addon settings, you can specify the folder for saving textures, select the GPU device, output image format and other parameters.

#### **How ​​to use the addon:**

1. **Texture scaler:**
- Go to the image editor and select the texture you want to scale.
- In the Texture Upscaler panel, configure the scaling parameters (ratio, width, compression, format, etc.).
- Click the "Upscale" button to start the scaling process.

2. **Snap objects to the armature:**
- Select the armature to which you want to snap objects.
- Go to the Snap Tools panel and configure additional parameters (Subdivision, clear normals, merge vertices, etc.).
- Click the "Snap objects to skeleton" button.

3. **Reset armature pose:**
- Select the armature in the editor and click the "Reset pose" button on the Clear Animation and Pose panel.

#### **Addon settings:**
- **Texture save folder:** Specify the folder where the scaled textures will be saved.
- **GPU device:** Select the GPU device to speed up the scaling process.
- **Output image format:** Select the output image saving format (PNG, JPG, WEBP)
