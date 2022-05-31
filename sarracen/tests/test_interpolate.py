"""
pytest unit tests for interpolate.py functions.
"""
import pandas as pd
import numpy as np
from pytest import approx

from sarracen import SarracenDataFrame
from sarracen.kernels import CubicSplineKernel, QuarticSplineKernel, QuinticSplineKernel
from sarracen.interpolate import interpolate_2d, interpolate_2d_cross, interpolate_3d_cross, interpolate_3d


def test_interpolate_2d():
    df = pd.DataFrame({'x': [0],
                       'y': [0],
                       'P': [1],
                       'h': [1],
                       'rho': [1],
                       'm': [1]})
    sdf = SarracenDataFrame(df, params=dict())

    image = interpolate_2d(sdf, 'P', 'x', 'y', CubicSplineKernel(), 40, 40, -2, 2, -2, 2)

    assert image[0][0] == 0
    assert image[20][0] == approx(CubicSplineKernel().w(np.sqrt((-1.95) ** 2 + 0.05 ** 2), 2), rel=1e-8)
    assert image[20][20] == approx(CubicSplineKernel().w(np.sqrt(0.05 ** 2 + 0.05 ** 2), 2), rel=1e-8)
    assert image[12][17] == approx(CubicSplineKernel().w(np.sqrt(0.75 ** 2 + 0.25 ** 2), 2), rel=1e-8)

    # next, use a dataset where rho != 0, h != 0, m != 0.
    df = pd.DataFrame({'y': [0],
                       'x': [1],
                       'A': [4],
                       'h': [0.9],
                       'rho': [0.4],
                       'm': [0.03]})
    sdf = SarracenDataFrame(df, params=dict())
    kernel = QuinticSplineKernel()
    w = sdf['m'][0] / (sdf['rho'][0] * sdf['h'] ** 2)

    image = interpolate_2d(sdf, 'A', 'x', 'y', kernel, 10, 15, 0, 2, 0, 3)

    assert image[14][8] == 0
    assert image[14][5] == approx(w * sdf['A'][0] * kernel.w(np.sqrt(0.1 ** 2 + 2.9 ** 2) / sdf['h'][0], 2), rel=1e-8)
    assert image[5][1] == approx(w * sdf['A'][0] * kernel.w(np.sqrt(0.7 ** 2 + 1.1 ** 2) / sdf['h'][0], 2), rel=1e-8)
    assert image[0][4] == approx(w * sdf['A'][0] * kernel.w(np.sqrt(2 * (0.1 ** 2)) / sdf['h'][0], 2), rel=1e-8)
    assert image[0][0] == approx(image[0][9], rel=1e-8)


def test_interpolate_2d_cross():
    df = df = pd.DataFrame({'x': [0],
                            'y': [0],
                            'P': [1],
                            'h': [1],
                            'rho': [1],
                            'm': [1]})
    sdf = SarracenDataFrame(df, params=dict())

    # first, test a cross-section at y=0
    output = interpolate_2d_cross(sdf, 'P', 'x', 'y', CubicSplineKernel(), 40, -2, 2, 0, 0)

    assert output[0] == approx(CubicSplineKernel().w(np.sqrt((-1.95) ** 2), 2), rel=1e-8)
    assert output[20] == approx(CubicSplineKernel().w(np.sqrt(0.05 ** 2), 2), rel=1e-8)
    assert output[17] == approx(CubicSplineKernel().w(np.sqrt(0.25 ** 2), 2), rel=1e-8)

    # next, test a cross-section where x=y
    output = interpolate_2d_cross(sdf, 'P', 'x', 'y', CubicSplineKernel(), 40, -2, 2, -2, 2)

    assert output[0] == approx(CubicSplineKernel().w(np.sqrt(2 * (1.95 ** 2)), 2), rel=1e-8)
    assert output[20] == approx(CubicSplineKernel().w(np.sqrt(2 * (0.05 ** 2)), 2), rel=1e-8)
    assert output[17] == approx(CubicSplineKernel().w(np.sqrt(2 * (0.25 ** 2)), 2), rel=1e-8)

    # lastly, use a dataset where rho != 0, h != 0, m != 0.
    df = pd.DataFrame({'y': [0],
                       'x': [1],
                       'A': [2.1],
                       'h': [3],
                       'rho': [0.8],
                       'm': [0.05]})
    sdf = SarracenDataFrame(df, params=dict())
    kernel = QuarticSplineKernel()
    w = sdf['m'][0] / (sdf['rho'][0] * sdf['h'][0] ** 2)

    output = interpolate_2d_cross(sdf, 'A', 'x', 'y', kernel, 20, -3, 2, 3, -3)
    # delta_x = 5, delta_y = -6
    # therefore, the change in difference between pixels is dx=5/20, dy=-6/20

    # pixels are evenly spaced across the line, so the first pixel starts at (-3 + 5/40, 3 - 6/40)
    # difference from particle at (1, 0) -> (-3 + 5/40 - 1, 3 - 6/40)
    assert output[0] == approx(w * sdf['A'][0] * kernel.w(np.sqrt(3.875 ** 2 + 2.85 ** 2) / sdf['h'][0], 2), rel=1e-8)
    # (-3.875 + 10 * (5/20), 2.85 - 10 * (6/20))
    assert output[10] == approx(w * sdf['A'][0] * kernel.w(np.sqrt(1.375 ** 2 + 0.15 ** 2) / sdf['h'][0], 2), rel=1e-8)
    # (-3.875 + 19 * (5/20), 2.85 - 19 * (6/20))
    assert output[19] == approx(w * sdf['A'][0] * kernel.w(np.sqrt(0.875 ** 2 + 2.85 ** 2) / sdf['h'][0], 2), rel=1e-8)


def test_interpolate_3d():
    df = pd.DataFrame({'x': [0.25],
                       'y': [0.25],
                       'z': [0],
                       'P': [0.5],
                       'h': [0.125],
                       'rho': [0.5],
                       'm': [0.01],
                       'A': [3]})
    sdf = SarracenDataFrame(df, params=dict())
    kernel = QuarticSplineKernel()

    image = interpolate_3d(sdf, 'A', 'x', 'y', 'z', kernel, 10000, None, None, 10, 10, 0, 0.5, 0, 0.5)
    column_kernel = kernel.get_column_kernel(10000)

    # w = 0.01 / (0.5 * 0.125^3) = 10.24
    w = (sdf['m'] / (sdf['rho'] * sdf['h'] ** 3))[0]

    assert image[0][0] == 0
    # 10.24 * 0.125 * 3 * F(sqrt(0.025^2 + 0.225^2)/0.125) ~= 3.84 * 0.000409322579272
    F = np.interp(np.sqrt(0.025 ** 2 + 0.225 ** 2) / df['h'][0], np.linspace(0, kernel.get_radius(), 10000),
                  column_kernel)
    assert image[0][4] == approx(w * sdf['h'][0] * sdf['A'][0] * F)
    # 10.24 * 0.125 * 3 * F(sqrt(0.025^2 + 0.025^2)/0.125) ~= 3.84 * 0.427916515256
    F = np.interp(np.sqrt(2 * (0.025 ** 2)) / df['h'][0], np.linspace(0, kernel.get_radius(), 10000),
                  column_kernel)
    assert image[5][5] == approx(w * sdf['h'][0] * sdf['A'][0] * F)

    df = pd.DataFrame({'y': [0],
                       'x': [2],
                       'A': [3.1],
                       'h': [1.5],
                       'z': [-0.5],
                       'rho': [0.21],
                       'm': [0.15]})
    sdf = SarracenDataFrame(df, params=dict())
    kernel = QuinticSplineKernel()

    image = interpolate_3d(sdf, 'A', 'x', 'y', 'z', kernel, 10000, None, None, 20, 15, 0, 2, 0, 0.9)
    column_kernel = kernel.get_column_kernel(10000)

    # w = 0.15 / (0.21 * 1.5^3) = 0.21164
    w = (sdf['m'] / (sdf['rho'] * sdf['h'] ** 3))[0]

    # r = sqrt(dx ^ 2 + dy ^ 2) = sqrt((2 - (0.1 * 0.5))^2 + (0 + (0.06 * 0.5))^2)
    F = np.interp(np.sqrt(1.95 ** 2 + 0.03 ** 2) / df['h'][0], np.linspace(0, kernel.get_radius(), 10000),
                  column_kernel)
    assert image[0][0] == approx(w * sdf['h'][0] * sdf['A'][0] * F)

    # r = sqrt((2 - (0.1 * 19.5)) ^ 2 + (0 + (0.06 * 0.5)) ^ 2)
    F = np.interp(np.sqrt(0.05 ** 2 + 0.03 ** 2) / df['h'][0], np.linspace(0, kernel.get_radius(), 10000),
                  column_kernel)
    assert image[0][19] == approx(w * sdf['h'][0] * sdf['A'][0] * F)

    # r = sqrt((2 - (0.1 * 14.5)) ^ 2 + (0 + (0.06 * 9.5)) ^ 2)
    F = np.interp(np.sqrt(0.55 ** 2 + 0.57 ** 2) / df['h'][0], np.linspace(0, kernel.get_radius(), 10000),
                  column_kernel)
    assert image[9][14] == approx(w * sdf['h'][0] * sdf['A'][0] * F)


def test_interpolate_3d_cross():
    df = df = pd.DataFrame({'x': [0],
                            'y': [0],
                            'z': [0],
                            'P': [1],
                            'h': [1],
                            'rho': [1],
                            'm': [1]})
    sdf = SarracenDataFrame(df, params=dict())

    # first, test a cross-section at z=0
    image = interpolate_3d_cross(sdf, 'P', 0, 'x', 'y', 'z', CubicSplineKernel(), None, None, 40, 40, -2, 2, -2,
                                 2)

    # should be exactly the same as for a 2D rendering, except q values are now taken from the 3D kernel.
    assert image[0][0] == 0
    assert image[20][0] == approx(CubicSplineKernel().w(np.sqrt((-1.95) ** 2 + 0.05 ** 2), 3), rel=1e-8)
    assert image[20][20] == approx(CubicSplineKernel().w(np.sqrt(0.05 ** 2 + 0.05 ** 2), 3), rel=1e-8)
    assert image[12][17] == approx(CubicSplineKernel().w(np.sqrt(0.75 ** 2 + 0.25 ** 2), 3), rel=1e-8)

    # next, test a cross-section at z=0.5
    image = interpolate_3d_cross(sdf, 'P', 0.5, 'x', 'y', 'z', CubicSplineKernel(), None, None, 40, 40, -2, 2, -2,
                                 2)

    assert image[0][0] == 0
    assert image[20][0] == approx(CubicSplineKernel().w(np.sqrt((-1.95) ** 2 + 0.05 ** 2 + (0.5 ** 2)), 3), rel=1e-8)
    assert image[20][20] == approx(CubicSplineKernel().w(np.sqrt(2 * (0.05 ** 2) + (0.5 ** 2)), 3), rel=1e-8)
    assert image[12][17] == approx(CubicSplineKernel().w(np.sqrt(0.75 ** 2 + 0.25 ** 2 + (0.5 ** 2)), 3), rel=1e-8)

    # lastly, use a dataset where rho != 0, h != 0, m != 0.
    df = pd.DataFrame({'x': [0],
                            'y': [0],
                            'z': [-1],
                            'A': [4],
                            'h': [2],
                            'rho': [0.5],
                            'm': [0.1]})
    sdf = SarracenDataFrame(df, params=dict())

    w = sdf['m'][0] / (sdf['rho'][0] * sdf['h'][0] ** 3)
    kernel = QuarticSplineKernel()
    image = interpolate_3d_cross(sdf, 'A', 0, 'x', 'y', 'z', kernel, None, None, 15, 11, -0.75, 0.75, -0.825,
                                 0.825)

    # r = sqrt(dx ** 2 + dy ** 2 + dz ** 2)
    assert image[0][0] == approx(w * sdf['A'][0] * kernel.w(np.sqrt(0.7 ** 2 + 0.75 ** 2 + 1) / sdf['h'][0], 3))
    assert image[4][0] == approx(w * sdf['A'][0] * kernel.w(np.sqrt(0.7 ** 2 + 0.15 ** 2 + 1) / sdf['h'][0], 3))
    assert image[7][10] == approx(w * sdf['A'][0] * kernel.w(np.sqrt(0.3 ** 2 + 0.3 ** 2 + 1) / sdf['h'][0], 3))
