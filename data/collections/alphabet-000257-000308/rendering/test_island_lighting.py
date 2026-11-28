import unittest
from island_lighting import hillshade, horizontal_unit, shadow_offset, validate_design


class LightingTests(unittest.TestCase):
    def test_known_raster_slopes_face_the_correct_light(self):
        self.assertGreater(hillshade(1, 0, 270, 45), hillshade(1, 0, 90, 45))
        self.assertGreater(hillshade(0, 1, 0, 45), hillshade(0, 1, 180, 45))

    def test_south_up_recalculates_in_screen_coordinates(self):
        for azimuth in range(0, 360, 45):
            self.assertAlmostEqual(hillshade(.4, -.7, azimuth, 40, 180),
                                   hillshade(.4, -.7, (azimuth + 180) % 360, 40, 0))

    def test_cast_shadows_point_away_from_the_light(self):
        offsets = set()
        for azimuth in range(0, 360, 45):
            lx, ly = horizontal_unit(azimuth)
            sx, sy = shadow_offset(azimuth, 12)
            self.assertLess(lx * sx + ly * sy, 0)
            offsets.add((sx, sy))
        self.assertEqual(len(offsets), 8)

    def test_invalid_designs_cannot_reach_the_renderer(self):
        for key, bad in [('azimuth_degrees', 360), ('elevation_degrees', 0),
                         ('shadow_distance_px', -1), ('azimuth_degrees', float('nan'))]:
            design = dict(azimuth_degrees=90, elevation_degrees=45, shadow_distance_px=12)
            design[key] = bad
            with self.assertRaises(ValueError):
                validate_design(design)


if __name__ == '__main__':
    unittest.main()
