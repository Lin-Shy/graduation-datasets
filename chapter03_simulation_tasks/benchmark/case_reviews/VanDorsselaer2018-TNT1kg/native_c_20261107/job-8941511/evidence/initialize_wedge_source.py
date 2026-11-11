"""Conservative spherical fill on the allocated native wedge mesh."""
import argparse
import json
import math
from pathlib import Path

from foam_fields_snapshot import read_field, read_internal_volume_scalar
from initialize_cartesian_products import initialize as initialize_products


def initialize(package, case):
    spec = json.loads((package / "specification.json").read_text())
    nx, nr = spec["mesh"]["counts"][:2]
    axial_half, outer = spec["mesh"]["axial_half_length_m"], spec["mesh"]["midplane_radius_m"]
    dx, dy = 2 * axial_half / nx, outer / nr
    theta = math.radians(spec["mesh"]["opening_deg"] / 2)
    tangent = math.tan(theta)
    source = spec["source"]
    radius = source["radius_m"]
    layout = {"byte_order": "little", "scalar_bits": 64, "label_bits": 32}
    initial = case / "0"
    centres = read_field(initial / "C", layout)["internal"]
    vfile = initial / "V"
    with vfile.open("rb") as stream:
        internal = b"volScalarField::Internal" in stream.read(1500)
    reader = read_internal_volume_scalar if internal else read_field
    volumes = reader(vfile, layout)["internal"]
    assert len(volumes) == nx * nr and len(centres) == 3 * len(volumes)
    alpha = [0.] * len(volumes)
    partial = []
    pieces = []
    angular_panels, axial_panels = 32, 64
    dphi = 2 * theta / angular_panels
    inv_cos_squared = [1 / math.cos(-theta + (j + .5) * dphi) ** 2 for j in range(angular_panels)]
    for cell, volume in enumerate(volumes):
        x, y, z = centres[3 * cell:3 * cell + 3]
        if abs(x) > radius + dx or y > radius + dy:
            continue
        i = math.floor((x + axial_half) / dx)
        j = math.floor(y / dy)
        xlo = -axial_half + i * dx
        ylo, yhi = j * dy, (j + 1) * dy
        assert 0 <= i < nx and 0 <= j < nr and abs(z) < 1e-9
        assert math.isclose(volume, dx * tangent * (yhi**2 - ylo**2), rel_tol=2e-7)
        dxx = dx / axial_panels
        overlap = 0.
        for ii in range(axial_panels):
            cap = radius**2 - (xlo + (ii + .5) * dxx)**2
            if cap > ylo**2:
                overlap += math.fsum(
                    max(0., min(yhi**2 * scale, cap) - ylo**2 * scale)
                    for scale in inv_cos_squared
                )
        fill = min(1., overlap * .5 * dphi * dxx / volume)
        if fill > 1 - 1e-12:
            fill = 1.
        alpha[cell] = fill
        if fill > 0:
            pieces.append(fill * volume)
        if 0 < fill < 1:
            partial.append(cell)
    target = source["mass_kg"] / source["density_kg_m3"]
    before = math.fsum(pieces)
    residual = target - before
    assert abs(residual) < .002 * target
    room = math.fsum((1 - alpha[k] if residual >= 0 else alpha[k]) * volumes[k] for k in partial)
    assert room > abs(residual)
    for k in partial:
        alpha[k] += residual * (1 - alpha[k] if residual >= 0 else alpha[k]) / room
    field = initial / "alpha.tnt"
    field.write_text(field.read_text().replace(
        "internalField uniform 0;", "internalField nonuniform List<scalar>\n"
        + str(len(alpha)) + "\n(\n" + "\n".join(format(v, ".17g") for v in alpha) + "\n);"
    ))
    initialize_products(package, case)
    receipt = package / "source_initialization.json"
    data = json.loads(receipt.read_text())
    data["full_sphere_equivalent_mass_kg"] = data["native_source_mass_kg"] * 360 / (2 * math.degrees(theta))
    assert math.isclose(data["full_sphere_equivalent_mass_kg"], 1., rel_tol=1e-10)
    data.update(uncorrected_wedge_volume_m3=before, correction_relative=residual / target,
                partial_source_cells=len(partial), source_volume_method="native C and V, bounded 64 x 32 quadrature")
    receipt.write_text(json.dumps(data, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--case", type=Path, required=True)
    args = parser.parse_args()
    initialize(args.package, args.case)
