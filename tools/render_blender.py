"""Headless Blender Cycles renderer for World of Vibrations snapshots.

Invoke via:
    blender -b -P tools/render_blender.py -- --snapshot snap.npz --output frame.png [--quality QUALITY] [--engine ENGINE]

Inside Blender's Python:
- Load snapshot NPZ.
- Build a scene with the box outlined, vibrations as point-instanced spheres,
  and individual node meshes (electrons, pairs/triads/atoms with halos).
- Render with Cycles (default) or Eevee Next.

Rendering 4096 vibrations as individual mesh objects is prohibitively slow
in Cycles. Vibrations are instanced via vertex instancing on a points mesh,
which is fast and memory-efficient.
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
parser.add_argument("--snapshot", type=Path, default=None,
                    help="path to a single snapshot NPZ (use this OR --snapshot-dir)")
parser.add_argument("--output", type=Path, default=None,
                    help="output PNG path (single-snapshot mode)")
parser.add_argument("--snapshot-dir", type=Path, default=None,
                    help="directory of snapshot NPZs to render in chronological order")
parser.add_argument("--output-dir", type=Path, default=None,
                    help="directory to write numbered frame_NNNNN.png files (batch mode)")
parser.add_argument("--no-nodes", action="store_true",
                    help="skip rendering nodes (electrons/pairs/atoms); show only the wave field")
parser.add_argument("--quality", choices=["low", "medium", "high", "paper"], default="medium")
parser.add_argument("--engine", choices=["cycles", "eevee"], default="cycles")
parser.add_argument("--resolution", type=int, default=1920,
                    help="output width in px; height is 9/16 of width")
args = parser.parse_args(argv)

# Validate mode
if args.snapshot_dir is not None:
    if args.output_dir is None:
        print("--snapshot-dir requires --output-dir", file=sys.stderr)
        sys.exit(2)
elif args.snapshot is not None:
    if args.output is None:
        print("--snapshot requires --output", file=sys.stderr)
        sys.exit(2)
else:
    print("Must supply either --snapshot+--output or --snapshot-dir+--output-dir",
          file=sys.stderr)
    sys.exit(2)

# Lazy imports — these only work inside Blender
try:
    import bpy
    import numpy as np
except ImportError:
    print("This script must be run inside Blender (blender -b -P ...).", file=sys.stderr)
    sys.exit(1)


SAMPLES = {"low": 64, "medium": 256, "high": 1024, "paper": 4096}[args.quality]


# ---------------------------------------------------------------------- helpers

def clear_scene():
    """Remove everything in the default scene — meshes, lights, cameras, materials."""
    for collection in bpy.data.collections:
        for obj in list(collection.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)
    for light in list(bpy.data.lights):
        bpy.data.lights.remove(light)
    for cam in list(bpy.data.cameras):
        bpy.data.cameras.remove(cam)


def make_emission_material(name, color, strength=1.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    # Clear default nodes
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1.0)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return mat


def make_glossy_material(name, color, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        out = nt.nodes.get("Material Output") or nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(bsdf.outputs[0], out.inputs[0])
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = 0.4
    return mat


# ---------------------------------------------------------------------- camera

def setup_camera_orthographic(box_size):
    """Orthographic camera framing the entire box.

    Looks at the box centre from outside one corner. Rotation set explicitly
    via mathutils.Vector — track-to constraint isn't always evaluated during
    background rendering.
    """
    import mathutils
    bx, by, bz = box_size
    centre = mathutils.Vector((bx * 0.5, by * 0.5, bz * 0.5))
    longest = max(bx, by, bz)

    # Camera along the (1, -1, 1) diagonal, far enough that it sees the whole box
    cam_offset = mathutils.Vector((longest * 1.5, -longest * 1.5, longest * 1.5))
    cam_pos = centre + cam_offset
    direction = (centre - cam_pos).normalized()
    rot_quat = direction.to_track_quat("-Z", "Y")

    cam_data = bpy.data.cameras.new("camera")
    cam_data.type = "ORTHO"
    # Hexagonal projection of the box has diameter sqrt(2)·longest along the diagonal axis;
    # use 1.8× to leave margin and accommodate node halos.
    cam_data.ortho_scale = longest * 1.8
    # Default clip_end is 100; our world is 1000+ units. Set explicit clip planes.
    cam_data.clip_start = 0.1
    cam_data.clip_end = longest * 10.0
    cam = bpy.data.objects.new("camera", cam_data)
    cam.location = cam_pos
    cam.rotation_euler = rot_quat.to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam


def setup_lights(box_size):
    bx, by, bz = box_size
    diag = max(bx, by, bz)
    # Three-point lighting. Area-light energy in Watts; for a 1000-unit box
    # values of a few thousand W give clean illumination in Eevee, ~10× that in Cycles.
    # Scale linearly with box size so larger worlds stay correctly lit.
    base = diag * 5.0  # 5000 W for a 1000-unit box; 50000 W for 10000-unit
    for loc, energy_mult, name in [
        ((bx * 1.4, -by * 0.4, bz * 1.5), 1.0, "key"),
        ((-bx * 0.4, by * 1.4, bz * 0.6), 0.5, "fill"),
        ((bx * 0.5, by * 0.5, -bz * 0.3), 0.25, "rim"),
    ]:
        light_data = bpy.data.lights.new(name=f"light_{name}", type="AREA")
        light_data.energy = base * energy_mult
        light_data.size = diag * 0.5
        light_obj = bpy.data.objects.new(name=f"light_{name}", object_data=light_data)
        light_obj.location = loc
        bpy.context.collection.objects.link(light_obj)


def setup_world_background():
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.04, 0.04, 0.06, 1.0)
        bg.inputs["Strength"].default_value = 0.8


def add_box_outline(box_size):
    """Wireframe box edges so the simulation volume is visible."""
    bx, by, bz = box_size
    corners = np.array([
        [0, 0, 0], [bx, 0, 0], [bx, by, 0], [0, by, 0],
        [0, 0, bz], [bx, 0, bz], [bx, by, bz], [0, by, bz],
    ], dtype=np.float64)
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
    ]
    mesh = bpy.data.meshes.new("box_outline")
    mesh.from_pydata(corners.tolist(), edges, [])
    mesh.update()
    obj = bpy.data.objects.new("box_outline", mesh)
    bpy.context.collection.objects.link(obj)
    # Wireframe modifier with a noticeable but not overwhelming width
    mod = obj.modifiers.new("wireframe", "WIREFRAME")
    mod.thickness = max(bx, by, bz) * 0.005
    mat = make_emission_material("box_edges", (0.5, 0.55, 0.7), strength=4.0)
    obj.data.materials.append(mat)


# ---------------------------------------------------------------------- vibrations

def add_vibration_waves(positions, velocities, frequencies, polarities, alive, box_size):
    """Render each vibration as a short wavy tube oriented along its velocity.

    Wave properties:
    - oriented along the velocity direction
    - amplitude direction: perpendicular to velocity, as close to world Z as possible
    - wavelength inversely scales with log10(frequency) — faster vibrations look
      tighter, slower vibrations look more stretched
    - colour: blue (even polarity) or red (odd polarity), emissive

    One Curve object per polarity, each with one POLY spline per vibration. The
    curve's bevel_depth turns every spline into a tube in a single render pass.
    """
    bx, by, bz = box_size
    diag = max(bx, by, bz)
    wave_length = diag * 0.05         # one wave is 5% of the box across
    wave_amplitude = diag * 0.012     # 1.2% of box for the amplitude
    n_samples = 28                     # control points per wave
    tube_radius = diag * 0.0008        # very thin tube
    z_axis = np.array([0.0, 0.0, 1.0])

    for pol_value, color, name in [
        (True, (0.36, 0.65, 0.98), "vibr_even"),
        (False, (0.96, 0.40, 0.32), "vibr_odd"),
    ]:
        mask = alive & (polarities == pol_value)
        if not mask.any():
            continue

        curve_data = bpy.data.curves.new(f"{name}_curve", type="CURVE")
        curve_data.dimensions = "3D"
        curve_data.bevel_depth = tube_radius
        curve_data.bevel_resolution = 1

        for idx in np.where(mask)[0]:
            pos = positions[idx]
            vel = velocities[idx]
            freq = float(frequencies[idx])

            v_norm_len = float(np.linalg.norm(vel))
            if v_norm_len < 1e-9:
                continue
            v_norm = vel / v_norm_len

            # Amplitude direction: world-Z component perpendicular to velocity.
            # If velocity is nearly parallel to Z, fall back to X-axis.
            amp_dir = z_axis - float(np.dot(z_axis, v_norm)) * v_norm
            amp_dir_len = float(np.linalg.norm(amp_dir))
            if amp_dir_len < 0.05:
                amp_dir = np.array([1.0, 0.0, 0.0])
            else:
                amp_dir = amp_dir / amp_dir_len

            # Wavelength: shorter for higher frequency.
            log_f = max(np.log10(freq), 1.0)  # log10(100)=2; log10(10000)=4
            wavelength = wave_length / log_f

            # Sample the wave centerline
            ts = np.linspace(-wave_length / 2, wave_length / 2, n_samples)
            spline = curve_data.splines.new("POLY")
            spline.points.add(n_samples - 1)
            for j, t in enumerate(ts):
                amp = wave_amplitude * np.sin(2 * np.pi * t / wavelength)
                p = pos + v_norm * t + amp_dir * amp
                spline.points[j].co = (float(p[0]), float(p[1]), float(p[2]), 1.0)

        obj = bpy.data.objects.new(f"{name}_obj", curve_data)
        bpy.context.collection.objects.link(obj)
        mat = make_emission_material(f"{name}_mat", color, strength=3.0)
        obj.data.materials.append(mat)


# Backward-compatibility alias kept for any external callers expecting the old name.
def add_vibrations_instanced(positions, polarities, alive, vibration_radius, box_size):
    """Legacy entry point — kept for backward compatibility but no longer used.

    Real-world callers should use add_vibration_waves(), which produces wavelet
    geometry instead of point-instanced spheres.
    """
    raise NotImplementedError(
        "add_vibrations_instanced is deprecated; use add_vibration_waves with "
        "velocity/frequency arrays for proper wave rendering."
    )


# ---------------------------------------------------------------------- nodes

def add_node_spheres(positions, levels, alive, box_size):
    """Add individual spheres for nodes (electrons, pairs, triads, atoms)."""
    bx, by, bz = box_size
    diag = max(bx, by, bz)

    # Sphere radii scaled to box size, large enough to be visible at 1920×1080
    radius_for_level = {
        1: diag * 0.020,    # electron: 2% of box diagonal
        2: diag * 0.026,    # pair
        3: diag * 0.032,    # triad
        4: diag * 0.045,    # atom: 4.5% of box diagonal — clearly visible
    }
    color_for_level = {
        1: (0.95, 0.61, 0.07),   # electron — orange
        2: (0.85, 0.85, 0.90),   # pair — pale white
        3: (0.95, 0.92, 0.85),   # triad — warm white
        4: (1.0, 0.98, 0.90),    # atom — bright warm white
    }
    emission_for_level = {1: 4.0, 2: 1.5, 3: 2.5, 4: 8.0}

    for i in range(len(positions)):
        if not alive[i]:
            continue
        level = int(levels[i])
        if level == 0:
            continue
        radius = radius_for_level.get(level, diag * 0.005)
        color = color_for_level.get(level, (0.7, 0.7, 0.9))
        emission = emission_for_level.get(level, 1.0)

        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=radius,
            segments=24, ring_count=12,
            location=positions[i].tolist()
        )
        obj = bpy.context.object
        obj.name = f"node_l{level}_i{i}"
        mat = make_glossy_material(f"node_l{level}_mat_{i}", color, emission_strength=emission)
        obj.data.materials.append(mat)


# ---------------------------------------------------------------------- main

def configure_render_settings():
    """Apply engine, samples, resolution, and output format. Called once per Blender process."""
    scene = bpy.context.scene
    if args.engine == "cycles":
        scene.render.engine = "CYCLES"
        scene.cycles.samples = SAMPLES
    else:
        for engine_name in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
            try:
                scene.render.engine = engine_name
                break
            except TypeError:
                continue
        if hasattr(scene, "eevee"):
            scene.eevee.taa_render_samples = SAMPLES
    scene.render.image_settings.file_format = "PNG"
    scene.render.resolution_x = args.resolution
    scene.render.resolution_y = int(args.resolution * 9 // 16)
    scene.render.film_transparent = False


def render_one(snapshot_path, output_path, hide_nodes):
    """Build the scene from one snapshot and render to one PNG."""
    data = np.load(snapshot_path, allow_pickle=True)
    cfg_dict = eval(str(data["config_json"][0]))
    box_size = tuple(cfg_dict["box_size"])

    s_pos = data["s_pos"]
    s_vel = data["s_vel"]
    s_freq = data["s_freq"]
    s_pol = data["s_pol"]
    s_alive = data["s_alive"]
    k_pos = data["k_pos"]
    k_level = data["k_level"]
    k_alive = data["k_alive"]

    n_vibrations = int(s_alive.sum())
    n_nodes_total = int(k_alive.sum())

    clear_scene()
    setup_world_background()
    setup_camera_orthographic(box_size)
    setup_lights(box_size)
    add_box_outline(box_size)

    add_vibration_waves(s_pos, s_vel, s_freq, s_pol, s_alive, box_size)
    if not hide_nodes:
        add_node_spheres(k_pos, k_level, k_alive, box_size)

    bpy.context.scene.render.filepath = str(output_path)
    bpy.ops.render.render(write_still=True)
    print(f"frame: t={float(data['t'][0]):.3f}s  vibr={n_vibrations}  nodes={n_nodes_total}  -> {output_path.name}")


def main():
    configure_render_settings()

    if args.snapshot_dir is not None:
        # Batch mode: render every snapshot in chronological order
        snapshots = sorted(args.snapshot_dir.glob("snapshot_*.npz"))
        if not snapshots:
            print(f"No snapshots in {args.snapshot_dir}", file=sys.stderr)
            sys.exit(1)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Batch render: {len(snapshots)} frames")
        for i, snap in enumerate(snapshots):
            output = args.output_dir / f"frame_{i:05d}.png"
            render_one(snap, output, hide_nodes=args.no_nodes)
        print(f"Wrote {len(snapshots)} frames to {args.output_dir}")
    else:
        render_one(args.snapshot, args.output, hide_nodes=args.no_nodes)


if __name__ == "__main__":
    main()
