"""fengfeng: local read-only static workbench; Ctrl+C stops the service."""
import argparse,functools,http.server,json,webbrowser
from pathlib import Path
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,fmt,*args):pass
 def end_headers(self):
  self.send_header('Cache-Control','no-store');super().end_headers()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--port',type=int,default=0);ap.add_argument('--no-open',action='store_true');ap.add_argument('--receipt',help='可选启动回执文件');a=ap.parse_args();root=Path(__file__).resolve().parents[1]/'assets/workbench'
 server=http.server.ThreadingHTTPServer(('127.0.0.1',a.port),functools.partial(Handler,directory=str(root)));url=f'http://127.0.0.1:{server.server_port}/nine-grid.html';r={'url':url,'bind':'127.0.0.1','root':str(root)}
 if a.receipt:Path(a.receipt).write_text(json.dumps(r,ensure_ascii=False),encoding='utf-8')
 print(url,flush=True)
 if not a.no_open:webbrowser.open(url)
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:server.server_close()
if __name__=='__main__':main()
