import unittest
import numpy as np
from chromatic_surface import interpolate_palette, chromatic_surface


class ChromaticTests(unittest.TestCase):
    def test_all_stops_are_reachable_including_the_last_colour(self):
        for count in range(7, 11):
            palette=['#%02x%02x%02x'%(i*17, 255-i*11, 25+i*19) for i in range(count)]
            actual=interpolate_palette(np.linspace(0,1,count),palette)
            expected=np.array([[int(c[k:k+2],16) for k in (1,3,5)] for c in palette])
            np.testing.assert_allclose(actual,expected,atol=1e-8)

    def test_smooth_fields_are_deterministic_and_light_is_independent(self):
        yy,xx=np.mgrid[-1:1:64j,-1:1:64j]
        land=xx*xx+yy*yy<.8
        relief=np.exp(-3*(xx*xx+yy*yy))
        palette=['#12204b','#354cec','#a128a9','#e44058','#f47b2b','#d1d927','#35c3aa','#a5d6e2']
        for mode in ['sweeping','crossflow','confluence','halo']:
            design=dict(field_mode=mode,phase=.7,field_angle_degrees=135,centre_x=.2,centre_y=-.3)
            a,field=chromatic_surface(relief,relief,land,np.ones((64,64))*.2,palette,design)
            b,lit_field=chromatic_surface(relief,relief,land,np.ones((64,64))*.8,palette,design)
            np.testing.assert_array_equal(field,lit_field)
            self.assertTrue(np.isfinite(a).all())
            self.assertGreater(b[land].mean(),a[land].mean())
            self.assertGreater(np.quantile(field[land],.95)-np.quantile(field[land],.05),.85)


if __name__=='__main__':
    unittest.main()
