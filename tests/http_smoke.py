import json,subprocess,sys,time
from urllib.request import urlopen
p=subprocess.Popen([sys.executable,'-m','src.main','--port','18081','--iterations','20','--interval','0.1'],stdout=subprocess.PIPE,text=True)
try:
 for i in range(30):
  try:
   with urlopen('http://127.0.0.1:18081/api/status',timeout=1) as r:data=json.load(r)
   if data.get('valid'):break
  except OSError:pass
  time.sleep(0.1)
 assert data['project_id']==11 and data['valid']
 with urlopen('http://127.0.0.1:18081/',timeout=1) as r:assert b'Entryway live dashboard' in r.read()
 p.communicate(timeout=10);assert p.returncode==0
 print('Live HTTP dashboard and JSON endpoint passed')
finally:
 if p.poll() is None:p.terminate();p.wait(timeout=5)
