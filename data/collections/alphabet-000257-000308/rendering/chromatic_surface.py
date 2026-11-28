"""Continuous multicolour fields, independent of the sculptural light source.

Colour placement is an artistic field; it is not geographical classification.
The exact shoreline, terrain and directional illumination stay independent.
"""
import math
import numpy as np
from scipy.ndimage import gaussian_filter


def palette_rgb(palette):
    if len(palette) < 2:
        raise ValueError('A continuous palette needs at least two colours')
    return np.array([[int(c[k:k+2], 16) for k in (1, 3, 5)] for c in palette], dtype=np.float32)


def interpolate_palette(field, palette):
    colours = palette_rgb(palette)
    position = np.clip(field, 0, 1) * (len(colours) - 1)
    index = np.minimum(position.astype(int), len(colours) - 2)
    fraction = (position - index)[..., None]
    fraction = fraction * fraction * (3 - 2 * fraction)
    return colours[index] * (1 - fraction) + colours[index + 1] * fraction


def chromatic_surface(relief, coast_distance, land, tone, palette, design):
    if not 7 <= len(palette) <= 10:
        raise ValueError('Chromatic editions require seven to ten palette stops')
    yy, xx = np.mgrid[-1:1:complex(land.shape[0]), -1:1:complex(land.shape[1])]
    angle = math.radians(design['field_angle_degrees'])
    u = xx * math.cos(angle) + yy * math.sin(angle)
    v = -xx * math.sin(angle) + yy * math.cos(angle)
    mode = design['field_mode']
    phase = design['phase']
    if mode == 'sweeping':
        spatial = u + .22 * np.sin(2.1 * v + phase)
    elif mode == 'crossflow':
        spatial = .62 * u + .38 * np.sin(2.3 * v + phase)
    elif mode == 'confluence':
        spatial = .6 * np.sin(1.8 * u + phase) + .4 * v
    elif mode == 'halo':
        spatial = np.sqrt((xx-design['centre_x'])**2 + (yy-design['centre_y'])**2) + .23*u
    else:
        raise ValueError('Unknown colour field: ' + mode)
    lo, hi = np.percentile(spatial[land], [1, 99])
    spatial = np.clip((spatial-lo)/max(float(hi-lo), 1e-6), 0, 1)
    coastal = coast_distance / max(float(coast_distance.max()), 1)
    # Broad, smooth geographic colour placement, with light applied separately.
    field = gaussian_filter(.68*spatial + .22*relief + .10*coastal, 4)
    quantiles = np.quantile(field[land], np.linspace(0, 1, 257))
    unique, indices = np.unique(quantiles, return_index=True)
    field = np.interp(field, unique, indices/256)
    rgb = interpolate_palette(field, palette)
    shade = .52 + .54*tone
    rgb = rgb * shade[..., None]
    return np.clip(rgb, 0, 255), field
