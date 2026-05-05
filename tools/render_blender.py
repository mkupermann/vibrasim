"""Headless Blender Cycles renderer for snapshot keyframes.

Invoke via:
    blender -b -P tools/render_blender.py -- --snapshot snap.npz --output frame.png

Inside Blender's Python:
- Load snapshot
- Build scene (camera, lights, instanced spheres per level)
- Render to PNG
"""
import sys
import argparse
from pathlib import Path

# Strip Blender's own argv before --
if "--" in sys.argv:
    argv = sys.argv[sys.argv.index("--") + 1:]
else:
    argv = []

parser = argparse.ArgumentParser()
parser.add_argument("--snapshot", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--quality", choices=["low", "medium", "high", "paper"], default="medium")
args = parser.parse_args(argv)

# Lazy imports — these only work inside Blender
try:
    import bpy
    import numpy as np
except ImportError:
    print("This script must be run inside Blender (blender -b -P ...).", file=sys.stderr)
    sys.exit(1)


SAMPLES = {"low": 64, "medium": 256, "high": 1024, "paper": 4096}[args.quality]


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def setup_camera_and_lights(box_size):
    # Camera at the long diagonal
    cam_pos = (box_size[0] * 1.6, -box_size[1] * 1.2, box_size[2] * 1.4)
    bpy.ops.object.camera_add(location=cam_pos)
    cam = bpy.context.object
    cam.rotation_euler = (1.0, 0, 0.7)
    bpy.context.scene.camera = cam

    # Three-point lighting
    for loc, energy in [
        ((box_size[0] * 1.5, -box_size[1] * 1.5, box_size[2] * 1.5), 1500.0),
        ((-box_size[0] * 0.5, box_size[1] * 1.0, box_size[2] * 0.5), 800.0),
        ((box_size[0] * 0.5, box_size[1] * 0.5, -box_size[2] * 0.3), 400.0),
    ]:
        bpy.ops.object.light_add(type="AREA", location=loc)
        light = bpy.context.object
        light.data.energy = energy


def add_node_meshes(positions, levels, alive):
    """Add one sphere per alive node, sized by level."""
    for i in range(len(positions)):
        if not alive[i]:
            continue
        level = int(levels[i])
        radius = {1: 1.5, 2: 2.0, 3: 2.5, 4: 4.0}.get(level, 1.0)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=positions[i].tolist())
        obj = bpy.context.object
        mat = bpy.data.materials.new(f"node_l{level}")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        color = {1: (1.0, 0.6, 0.07, 1), 4: (1.0, 1.0, 1.0, 1)}.get(level, (0.7, 0.7, 0.9, 1))
        bsdf.inputs["Base Color"].default_value = color
        if level == 4:
            bsdf.inputs["Emission Strength"].default_value = 2.0
            bsdf.inputs["Emission Color"].default_value = color
        obj.data.materials.append(mat)


def main():
    data = np.load(args.snapshot, allow_pickle=True)
    cfg_dict = eval(str(data["config_json"][0]))
    box_size = tuple(cfg_dict["box_size"])

    clear_scene()
    setup_camera_and_lights(box_size)
    add_node_meshes(data["k_pos"], data["k_level"], data["k_alive"])

    # Render settings
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = SAMPLES
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(args.output)
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    bpy.ops.render.render(write_still=True)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
