from math import sqrt

import numpy as np


def habitat_to_genesis_transform(translation, rotation_quat):
    """Convert Habitat (Y-up) pose to Genesis (Z-up) pose."""
    # Rotation of +90° about X-axis (to raise former Y to Z):
    Rx90 = np.array([[1, 0, 0],
                     [0, 0, -1],
                     [0, 1,  0]])
    trans = np.array(translation, dtype=float)
    new_pos = Rx90.dot(trans)  # (x, y, z)_gen = (x, -z, y)_hab
    # Quaternion (w, x, y, z) apply Rx90:
    qx90 = np.array([sqrt(2)/2, sqrt(2)/2, 0, 0])  # 90° about X
    q = np.array(rotation_quat, dtype=float)         # Habitat quaternion (w, x, y, z)
    # Quaternion multiply: new_q = qx90 * q  (apply X-90 first, then original rotation)
    w1,x1,y1,z1 = qx90
    w2,x2,y2,z2 = q
    new_quat = np.array([
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2
    ], dtype=float)
    new_quat /= np.linalg.norm(new_quat)
    return tuple(new_pos), tuple(new_quat)
