# MDL

Data is listed as it appears in the file

## Header

```c++
struct {
  char magic[4];
  int32_t format;
  byte padding[8];
  int32_t mesh_count;
  int32_t n1;
  byte garbage[72];
} mdl_header;
```

## Mesh Info

```c++
struct {
  int32_t u00;
  int32_t vertex_count;
  int32_t unk_flags;
  int32_t u0C;
  // position is X,Y,Z,1.0
  float position[4];
  float rotation_quaternion[4];
  // scale is X,Y,Z,1.0
  float scale[4];
  uint32_t mesh_id;
  int32_t u44;
  int32_t u48;
  int32_t u4C;
} mesh_info[mdl_header.mesh_count];
```

## Bone Info

```c++
typedef struct {
  float position[4];
  float rotation_quaternion[4];
  float unk[4];
  float scale[4];
  int32_t bone_parent;
  int32_t u44;
  int32_t u48;
  int32_t u4C;
} bone;

struct {
  int32_t bone_count;
  bone* bones_ptr[bone_count];
  byte padding[8];
} bone_info;
```

## Material Info

```c++
typedef struct {
  float ambient_color[4];
  float diffuse_color[4];
  int32_t diffuse_texture_index;
  int32_t material_id;
  int32_t u28;
  int32_t u2C;
  int8_t environment_texture_index;
  int8_t specular_texture_index;
  int8_t u32;
  int8_t u33;
  float shininess;
  float environment_strength;
  int32_t u3C;
} material;

struct {
  int32_t material_count;
  material* materials[material_count];
  byte padding[8];
} material_info;
```

## Texture Info

```c++
typedef struct {
  int32_t image_offset;
  int32_t image_size;
  int32_t image_unk;
  int32_t image_id;
} texture;

struct {
  int32_t texture_count;
  texture* textures[texture_count];
  byte padding[8];
} texture_info;
```

## Mesh Data

```c++
typedef struct {
  float position[3];
  float normal[3];
  float uv[2];
} vertex;

typedef struct {
  int16_t index_count;
  int16_t material_index;
  int16_t tristrip_indices[index_count];
} mesh;

typedef struct {
  int32_t bone_count;
  struct {
    int32_t bone_id;
    int32_t bone_weight;
  } skin_weights[bone_count];
} skin;

struct {
  vertex* vertex_offsets[mdl_header.mesh_count];
  mesh* mesh_offsets[mdl_header.mesh_count];
  skin* skin_offsets[mdl_header.mesh_count];
} mesh_data;
```
