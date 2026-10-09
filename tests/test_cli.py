import json,subprocess,sys,unittest
class CLICompatibility(unittest.TestCase):
 def test_established_command(self):
  p=subprocess.run([sys.executable,'-m','src.main','--iterations','2','--interval','0'],capture_output=True,text=True,timeout=10,check=True)
  rows=[json.loads(s) for s in p.stdout.splitlines()]
  self.assertEqual([r['seq'] for r in rows],[1,2]);self.assertTrue(all(r['project_id']==11 and r['valid'] for r in rows))
