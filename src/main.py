"""Pi entryway dashboard, BME280/reed adapters and optional real BLE peripheral."""
import argparse,asyncio,json,math,struct,time,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
SERVICE='ce110001-9b71-4b58-bf08-907a20701100'
CHAR='ce110002-9b71-4b58-bf08-907a20701100'

# Legacy simulation API retained for downstream consumers and original regression tests.
from dataclasses import dataclass
@dataclass(frozen=True)
class Snapshot:
 timestamp:float
 values:list
 score:float
 valid:bool
class Controller:
 def __init__(self,threshold=0.56,confirmations=5):
  if not 0.0<=threshold<=1.0:raise ValueError('threshold must be between 0 and 1')
  self.threshold=threshold;self.confirmations_required=max(1,confirmations)
  self.confirmations=0;self.output_active=False
 def evaluate(self,values,timestamp=None):
  valid=bool(values) and all(math.isfinite(v) and 0<=v<=1 for v in values)
  score=sum(values)/len(values) if valid else 0.0
  self.confirmations=min(self.confirmations+1,self.confirmations_required) if valid and score>=self.threshold else 0
  self.output_active=valid and self.confirmations>=self.confirmations_required
  return Snapshot(time.time() if timestamp is None else timestamp,values,score,valid)

def reading(seq,temp,humidity,pressure,door):
 valid=all(math.isfinite(v) for v in (temp,humidity,pressure)) and -40<=temp<=85 and 0<=humidity<=100 and 300<=pressure<=1100
 return {'project_id':11,'seq':seq,'temperature_c':temp if valid else None,'humidity_pct':humidity if valid else None,'pressure_hpa':pressure if valid else None,'door_open':bool(door),'valid':valid}
def packet(r):
 return struct.pack('<HhHB',r['seq']%65536,round((r['temperature_c'] or 0)*100),round((r['humidity_pct'] or 0)*100),int(r['door_open'])|(int(r['valid'])<<1))
class Hardware:
 def __init__(self):
  from gpiozero import Button
  import bme280
  from smbus2 import SMBus
  self.door=Button(23,pull_up=True,bounce_time=0.05);self.bus=SMBus(1);self.bme=bme280
  self.cal=bme280.load_calibration_params(self.bus,0x76)
 def read(self):
  r=self.bme.sample(self.bus,0x76,self.cal)
  return r.temperature,r.humidity,r.pressure,not self.door.is_pressed
 def close(self):self.door.close();self.bus.close()
class BLE:
 async def start(self):
  from bless import BlessServer,GATTCharacteristicProperties as P,GATTAttributePermissions as A
  self.server=BlessServer(name='Entryway11',loop=asyncio.get_running_loop())
  self.server.read_request_func=lambda c,**kwargs:c.value
  await self.server.add_new_service(SERVICE)
  await self.server.add_new_characteristic(SERVICE,CHAR,P.read|P.notify,bytearray(7),A.readable)
  await self.server.start()
 def update(self,r):
  self.server.get_characteristic(CHAR).value=bytearray(packet(r));self.server.update_value(SERVICE,CHAR)
 async def close(self):await self.server.stop()
PAGE=b'''<!doctype html><html lang="en"><meta charset="utf-8"><title>Entryway live dashboard</title><h1>Entryway live dashboard</h1><p>Local lab data; no security alarm.</p><pre id="data">Waiting</pre><script>async function poll(){try{let r=await fetch('/api/status',{cache:'no-store'});document.getElementById('data').textContent=JSON.stringify(await r.json(),null,2);}catch(e){document.getElementById('data').textContent='Unavailable';}}poll();setInterval(poll,2000);</script></html>'''
async def run(a):
 latest={'valid':False};lock=threading.Lock()
 class Handler(BaseHTTPRequestHandler):
  def do_GET(self):
   if self.path=='/':body=PAGE;kind='text/html; charset=utf-8'
   elif self.path=='/api/status':
    with lock:body=json.dumps(latest,allow_nan=False).encode()
    kind='application/json'
   else:self.send_error(404);return
   self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
  def log_message(self,*args):pass
 server=ThreadingHTTPServer((a.bind,a.port),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 hw=None;ble=None
 try:
  if a.hardware:hw=Hardware()
  if a.ble:ble=BLE();await ble.start()
  seq=0
  while not a.iterations or seq<a.iterations:
   seq+=1
   try:t,h,p,d=hw.read() if hw else (22.0+(seq%10)/10,45.0,1013.2,seq%2==0)
   except OSError:t,h,p,d=math.nan,math.nan,math.nan,False
   r=reading(seq,t,h,p,d)
   with lock:latest.clear();latest.update(r)
   if ble:ble.update(r)
   print(json.dumps(r,allow_nan=False),flush=True);await asyncio.sleep(a.interval)
 finally:
  if ble:await ble.close()
  if hw:hw.close()
  server.shutdown();server.server_close()
def main():
 p=argparse.ArgumentParser();p.add_argument('--iterations',type=int,default=0);p.add_argument('--interval',type=float,default=1.0);p.add_argument('--port',type=int,default=8080);p.add_argument('--bind',default='127.0.0.1');p.add_argument('--hardware',action='store_true');p.add_argument('--ble',action='store_true')
 a=p.parse_args()
 if not math.isfinite(a.interval) or a.interval<0 or a.iterations<0:p.error('nonnegative finite interval and iterations required')
 asyncio.run(run(a))
if __name__=='__main__':main()
