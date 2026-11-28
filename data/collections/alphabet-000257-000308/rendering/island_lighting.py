"""Screen-space lighting shared by the relief, coastal shading and cast shadow.

Azimuth is clockwise from screen top: 0=top, 90=right, 180=bottom,
270=left. Raster gradients use x right / y down. Canonical editions
are displayed at 0 or 180 degrees; cast shadows remain in screen space.
"""
import math
import numpy as np


def horizontal_unit(azimuth_degrees):
    angle = math.radians(azimuth_degrees)
    return math.sin(angle), -math.cos(angle)


def directional_component(gx, gy, azimuth_degrees, orientation_degrees=0):
    if orientation_degrees not in (0, 180):
        raise ValueError('Canonical orientation must be 0 or 180 degrees')
    lx, ly = horizontal_unit(azimuth_degrees)
    sign = 1 if orientation_degrees == 0 else -1
    return -sign * (gx * lx + gy * ly)


def hillshade(gx, gy, azimuth_degrees, elevation_degrees, orientation_degrees=0):
    elevation = math.radians(elevation_degrees)
    return (math.sin(elevation) + math.cos(elevation) *
            directional_component(gx, gy, azimuth_degrees, orientation_degrees)) / np.sqrt(1 + gx * gx + gy * gy)


def shadow_offset(azimuth_degrees, distance_px):
    lx, ly = horizontal_unit(azimuth_degrees)
    return round(-lx * distance_px), round(-ly * distance_px)


def validate_design(design):
    for key in ('azimuth_degrees', 'elevation_degrees', 'shadow_distance_px'):
        value = design[key]
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError('Invalid lighting parameter: ' + key)
    if not 0 <= design['azimuth_degrees'] < 360:
        raise ValueError('Azimuth must be within [0, 360)')
    if not 15 <= design['elevation_degrees'] <= 80:
        raise ValueError('Light elevation must be within [15, 80]')
    if not 0 < design['shadow_distance_px'] <= 30:
        raise ValueError('Shadow distance must be within (0, 30]')
    return design
