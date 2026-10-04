"""fengfeng: renders project JSON, complete events and keyframes without losing >9 events."""
import argparse,json,html,base64,mimetypes
from pathlib import Path
def build_html(project,base=Path('.')):
 esc=lambda x:html.escape(str(x or ''));parts=['<!doctype html><meta charset="utf-8"><title>剧宫导演离线看板</title><style>body{max-width:1200px;margin:30px auto;font:16px/1.6 sans-serif;background:#f5f3ee}article{padding:24px;background:white;margin:20px 0}img{max-width:100%}pre{white-space:pre-wrap}table{border-collapse:collapse;width:100%}td,th{border:1px solid #bbb;padding:6px}</style><h1>'+esc(project.get('script_name'))+'</h1>']
 for b in project.get('segments',[]):
  parts.append('<article><h2>'+esc(b['segment_id'])+'</h2><p>'+('已确认' if b.get('completed') else '草稿／未审核')+'</p>');src=b.get('image_data_url','')
  if src and not src.startswith('data:'):
   if src.startswith(('http:','https:')):raise ValueError('离线看板不下载远程图；先保存为内嵌工作JSON')
   f=(base/src).resolve();src='data:'+str(mimetypes.guess_type(f.name)[0] or 'image/png')+';base64,'+base64.b64encode(f.read_bytes()).decode()
  if src:parts.append('<img src="'+esc(src)+'">')
  parts.append('<h3>完整事件时间轴</h3>')
  for e in b.get('events',[]):parts.append('<h4>'+esc(f'{e["start"]}—{e["end"]}s {e["title"]}')+'</h4><pre>'+esc(e.get('body'))+'</pre>')
  parts.append('<h3>九格映射</h3><table><tr><th>格</th><th>事件</th><th>观察时刻</th><th>画面</th></tr>')
  for x in b['panels']:parts.append('<tr>'+''.join('<td>'+esc(v)+'</td>' for v in [x['id'],','.join(x.get('event_ids',[])),x.get('sample_time'),x['action']])+'</tr>')
  parts.append('</table></article>')
 return ''.join(parts)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('-o','--out');a=ap.parse_args();f=Path(a.input);p=json.loads(f.read_text(encoding='utf-8-sig'))
 if p.get('package_type')!='drama-grid-director-project':raise ValueError('需要本版本可编辑项目JSON')
 out=Path(a.out) if a.out else f.with_suffix('.html');out.write_text(build_html(p,f.parent),encoding='utf-8');print(out)
if __name__=='__main__':main()
