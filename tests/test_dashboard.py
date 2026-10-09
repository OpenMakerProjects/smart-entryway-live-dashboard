import math,struct,unittest
from src.main import reading,packet
class DashboardTests(unittest.TestCase):
 def test_packet(self):
  r=reading(65537,-5.12,40.25,1010,True);self.assertEqual(struct.unpack('<HhHB',packet(r)),(1,-512,4025,3))
 def test_invalid(self):
  for values in [(math.nan,40,1000),(22,101,1000),(22,40,200)]:
   r=reading(1,*values,False);self.assertFalse(r['valid']);self.assertIsNone(r['temperature_c']);self.assertEqual(packet(r)[-1],0)
