import ast
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def load_boxes(path):
    with open(path, "r") as f:
        return ast.literal_eval(f.read())


def draw_box(ax, center, half_size):
    x, y, z = center
    sx, sy, sz = half_size

    # Matplotlib coordinates: X, Z, Y
    corners = [
        (x - sx, z - sz, y - sy),
        (x + sx, z - sz, y - sy),
        (x + sx, z + sz, y - sy),
        (x - sx, z + sz, y - sy),
        (x - sx, z - sz, y + sy),
        (x + sx, z - sz, y + sy),
        (x + sx, z + sz, y + sy),
        (x - sx, z + sz, y + sy),
    ]

    faces = [
        [corners[0], corners[1], corners[2], corners[3]],
        [corners[4], corners[5], corners[6], corners[7]],
        [corners[0], corners[1], corners[5], corners[4]],
        [corners[2], corners[3], corners[7], corners[6]],
        [corners[1], corners[2], corners[6], corners[5]],
        [corners[0], corners[3], corners[7], corners[4]],
    ]

    ax.add_collection3d(
        Poly3DCollection(
            faces,
            alpha=0.35,
            edgecolor="black",
            linewidth=0.8,
        )
    )


def main():
    boxes = load_boxes("data/3d_boxes.txt")

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    for box in boxes:
        position = box[:3]
        half_size = box[3:]
        draw_box(ax, position, half_size)

    # Collect all box extents so the axes have a sensible scale.
    mins = []
    maxs = []

    for box in boxes:
        p = box[:3]
        s = box[3:]
        mins.append([p[0] - s[0], p[1] - s[1], p[2] - s[2]])
        maxs.append([p[0] + s[0], p[1] + s[1], p[2] + s[2]])

    mins = [min(v[i] for v in mins) for i in range(3)]
    maxs = [max(v[i] for v in maxs) for i in range(3)]

    ax.set_xlim(mins[0], maxs[0])
    ax.set_ylim(mins[1], maxs[1])
    ax.set_zlim(mins[2], maxs[2])

    ax.set_xlabel("X")
    ax.set_ylabel("Z")
    ax.set_zlabel("Y")

    # Y is up
    ax.set_zlim(mins[1], maxs[1])
    ax.set_ylim(mins[2], maxs[2])

    ax.view_init(elev=25, azim=45)

    # 3/4 inspection angle
    ax.view_init(elev=25, azim=45)

    ax.set_box_aspect((
        maxs[0] - mins[0],
        maxs[1] - mins[1],
        maxs[2] - mins[2],
    ))

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()