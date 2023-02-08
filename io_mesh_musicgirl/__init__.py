bl_info = {
    "name": "Music Girl Hatsune Miku mdl Importer",
    "author": "Thatrandomlurker",
    "version": (0, 0, 1),
    "blender": (3, 1, 2),
    "location": "File > Import-Export",
    "description": "Import Music Girl Hatsune Miku model files",
    "warning": "",
    "doc_url": "",
    "support": 'TESTING',
    "category": "Import-Export",
}



# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

import bmesh
import struct
import os
import mathutils
def LoadMDL(path):
    with open(path, 'rb') as f:
        magic = f.read(4)
        if magic != b"mdl ":
            raise Exception("Invalid file.")
        unk04 = struct.unpack("<I", f.read(4))[0]
        unk08 = struct.unpack("<I", f.read(4))[0]
        unk0C = struct.unpack("<I", f.read(4))[0]
        mesh_count = struct.unpack("<I", f.read(4))[0]
        mesh_info = []
        n1 = f.read(4)
        garbage = f.read(72)
        for i in range(mesh_count):
            mi = {}
            mi["UsuallyOne"] = struct.unpack("<I", f.read(4))[0]
            mi["VertexCount"] = struct.unpack("<I", f.read(4))[0]
            mi["Unsure"] = struct.unpack("<I", f.read(4))[0]
            mi["OneIfNotFirst"] = struct.unpack("<I", f.read(4))[0]
            mi["Position"] = struct.unpack("<ffff", f.read(16))[0]
            mi["Rotation"] = struct.unpack("<ffff", f.read(16))[0]
            mi["Scale"] = struct.unpack("<ffff", f.read(16))[0]
            mi["Hash"] = struct.unpack("<I", f.read(4))[0]
            mi["Null0"] = struct.unpack("<I", f.read(4))[0]
            mi["Null1"] = struct.unpack("<I", f.read(4))[0]
            mi["Null2"] = struct.unpack("<I", f.read(4))[0]
            mesh_info.append(mi)
        bone_count = struct.unpack("<I", f.read(4))[0]
        bone_offset = struct.unpack("<I", f.read(4))[0]
        f.seek(8, 1)
        mat_count = struct.unpack("<I", f.read(4))[0]
        mat_offset = struct.unpack("<I", f.read(4))[0]
        f.seek(8, 1)
            
        tex_count = struct.unpack("<I", f.read(4))[0]
        tex_offset = struct.unpack("<I", f.read(4))[0]
        f.seek(8, 1)
        pre = f.tell()
        f.seek(bone_offset)
        # create armature
        bpy.ops.object.armature_add(enter_editmode=True, location=(0, 0, 0))
        arm = bpy.context.active_object
        for b in range(bone_count):
            bone_m0 = struct.unpack("<ffff", f.read(16))
            bone_m1 = struct.unpack("<ffff", f.read(16))
            bone_m2 = struct.unpack("<ffff", f.read(16))
            bone_m3 = struct.unpack("<ffff", f.read(16))
            bone_parent = struct.unpack("<i", f.read(4))[0]
            bone_unk = struct.unpack("<I", f.read(4))[0]
            bone_length = struct.unpack("<f", f.read(4))[0]
            bone_unk2 = struct.unpack("<I", f.read(4))[0]
            bone_mat = mathutils.Matrix([bone_m0, bone_m1, bone_m2, bone_m3])
            abone = arm.data.edit_bones.new(f"bone_{b}")
            abone.tail = [0, 0.1, 0]
            abone.matrix = bone_mat
            if bone_parent != -1:
                abone.parent = arm.data.edit_bones.get(f"bone_{bone_parent}")
                abone.matrix = abone.parent.matrix @ bone_mat
        f.seek(tex_offset)
        if not os.path.exists(os.path.splitext(path)[0]):
            os.mkdir(os.path.splitext(path)[0])
        texmap = []
        for t in range(tex_count):
            image_offset = struct.unpack("<I", f.read(4))[0]
            image_size = struct.unpack("<I", f.read(4))[0]
            image_unk = struct.unpack("<I", f.read(4))[0]
            image_hash = struct.unpack("<I", f.read(4))[0]
            texmap.append(image_hash)
            with open(os.path.splitext(path)[0] + "/" + str(image_hash) + ".png", 'wb') as o:
                c = f.tell()
                f.seek(image_offset)
                o.write(f.read(image_size))
                f.seek(c)
        # mats after to know we can load images
        f.seek(mat_offset)
        mats = []
        for m in range(mat_count):
            mat_ambient = struct.unpack("<ffff", f.read(16))
            mat_diffuse = struct.unpack("<ffff", f.read(16))
            mat_diffuse_tex_id = struct.unpack("<I", f.read(4))[0]
            mat_hash = struct.unpack("<I", f.read(4))[0]
            mat_unk1 = struct.unpack("<I", f.read(4))[0]
            mat_unk2 = struct.unpack("<I", f.read(4))[0]
            mat_env_tex_id = struct.unpack("b", f.read(1))[0]
            mat_specular_tex_id = struct.unpack("b", f.read(1))[0]
            mat_unk3 = struct.unpack("b", f.read(1))[0]
            mat_unk4 = struct.unpack("b", f.read(1))[0]
            mat_reflectivity = struct.unpack("<f", f.read(4))[0]
            mat_env_strength = struct.unpack("<f", f.read(4))[0]
            mat_unk5 = struct.unpack("<I", f.read(4))[0]
            print(mat_hash)
            
            material = bpy.data.materials.get(str(mat_hash))
            if material == None:
                material = bpy.data.materials.new(str(mat_hash))
                material.use_nodes = True
                diff_img = bpy.data.images.get(str(texmap[mat_diffuse_tex_id]) + ".png")
                if diff_img == None:
                    bpy.data.images.load(os.path.splitext(path)[0] + "/" + str(texmap[mat_diffuse_tex_id]) + ".png", )
                print(str(texmap[mat_diffuse_tex_id]) + ".png")                
                img_node = material.node_tree.nodes.new('ShaderNodeTexImage')
                img_node.image = bpy.data.images[str(texmap[mat_diffuse_tex_id]) + ".png"]
                material.node_tree.links.new(img_node.outputs['Color'], material.node_tree.nodes['Principled BSDF'].inputs['Base Color'], verify_limits=True)
                material.node_tree.links.new(img_node.outputs['Alpha'], material.node_tree.nodes['Principled BSDF'].inputs['Specular'], verify_limits=True)
            mats.append(material)
            
        f.seek(pre)
        vert_offsets = struct.unpack("<" + "I" * mesh_count, f.read(4*mesh_count))
        index_offsets = struct.unpack("<" + "I" * mesh_count, f.read(4*mesh_count))
        skin_offsets = struct.unpack("<" + "I" * mesh_count, f.read(4*mesh_count))
        # might as well build the meshes now
        for i in range(mesh_count):
            mesh = bpy.data.meshes.new(str(mesh_info[i]["Hash"]))
            bm = bmesh.new()
            f.seek(vert_offsets[i])
            print("POS", f.tell())
            print("VC", mesh_info[i]["VertexCount"])
            normals = []
            uvs = []
            for v in range(mesh_info[i]["VertexCount"]):
                bm.verts.new(struct.unpack("<fff", f.read(12)))
                normals.append(struct.unpack("<fff", f.read(12)))
                tuvs = struct.unpack("<ff", f.read(8))
                uvs.append((tuvs[0], -tuvs[1]))
            bm.verts.ensure_lookup_table()
            bm.verts.index_update()
            f.seek(index_offsets[i])
            idxCount = struct.unpack("<H", f.read(2))[0]
            material_index = struct.unpack("<H", f.read(2))[0]
            # now we need to add the mat to the mesh
            mesh.materials.append(mats[material_index])
            uv = bm.loops.layers.uv.new("VertexUV")
            # initial face
            f0 = struct.unpack("<H", f.read(2))[0]
            f1 = struct.unpack("<H", f.read(2))[0]
            f2 = struct.unpack("<H", f.read(2))[0]
            if f0 != f1 and f0 != f2 and f1 != f2:
                face = bm.faces.new([bm.verts[f0], bm.verts[f1], bm.verts[f2]])
                face.material_index = 0
                for loop in face.loops:
                    loop[uv].uv = uvs[loop.vert.index]
            reverse = True
            for e in range(idxCount - 3):
                f0 = f1
                f1 = f2
                f2 = struct.unpack("<H", f.read(2))[0]
                if f0 != f1 and f0 != f2 and f1 != f2:
                    if reverse:
                        face = bm.faces.new([bm.verts[f2], bm.verts[f1], bm.verts[f0]])
                        face.material_index = 0
                        for loop in face.loops:
                            loop[uv].uv = uvs[loop.vert.index]
                    else:
                        face = bm.faces.new([bm.verts[f0], bm.verts[f1], bm.verts[f2]])
                        face.material_index = 0
                        for loop in face.loops:
                            loop[uv].uv = uvs[loop.vert.index]
                reverse = not reverse
            
            bm.to_mesh(mesh)
            bm.free()
            mesh.use_auto_smooth = True
            mesh.normals_split_custom_set_from_vertices(normals)
            obj = bpy.data.objects.new(str(mesh_info[i]["Hash"]), mesh)
            obj.parent = arm
            armModifier = obj.modifiers.new(name='Armature', type='ARMATURE')
            armModifier.object = arm
            f.seek(skin_offsets[i])
            for s in range(mesh_info[i]["VertexCount"]):
                num_weights = struct.unpack("<I", f.read(4))[0]
                for w in range(num_weights):
                    bone_id = struct.unpack("<I", f.read(4))[0]
                    bone_weight = struct.unpack("<f", f.read(4))[0]
                    group = obj.vertex_groups.get(f"bone_{bone_id}")
                    if group == None:
                        group = obj.vertex_groups.new(name=f"bone_{bone_id}")
                    # now we have the group. add the vert
                    group.add([s], bone_weight, 'ADD')
            bpy.context.collection.objects.link(obj)
    return {'FINISHED'}

class ImportMusicGirlModel(Operator, ImportHelper):
    """Import a model file from Music Girl Hatsune Miku"""
    bl_idname = "music_girl.import_music_girl_model"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Music Girl Hatsune Miku Model"

    # ImportHelper mixin class uses this
    filename_ext = ".mdl"

    filter_glob: StringProperty(
        default="*.mdl",
        options={'HIDDEN'}
    )

    def execute(self, context):
        return LoadMDL(self.filepath)

def menu_func_import(self, context):
    self.layout.operator(ImportMusicGirlModel.bl_idname, text="Import Music Girl Hatsune Miku Model")

# Register and add to the "file selector" menu (required to use F3 search "Text Import Operator" for quick access)
def register():
    bpy.utils.register_class(ImportMusicGirlModel)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportMusicGirlModel)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
