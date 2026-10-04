"""fengfeng: source-general checks adapted to continuous prose; warnings require review, not video-quality guarantees."""
import re,json,argparse
from pathlib import Path
NODE=re.compile(r'^\s*[—－-]*\s*\[\s*(\d+(?:\.\d+)?)\s*[—–‑－-]\s*(\d+(?:\.\d+)?)\s*(?:s|秒)?\s*\]\s*[：:]?\s*【([^】]+)】',re.M)
DIALOGUE=re.compile(r'【台词】\s*\[\s*(\d+(?:\.\d+)?)\s*[—–‑－-]\s*(\d+(?:\.\d+)?)\s*(?:s|秒)?\s*\]([^\n]*)')
def validate_text(text,duration=None,characters=None,max_duration=None,aspect=None):
 errors=[];warnings=[];nodes=list(NODE.finditer(text));last=0;spans=[];bodies=[]
 if not nodes:errors.append('没有可识别的事件时间轴')
 ratios=re.findall(r'(?<!\d)(?:16\s*[:：]\s*9|9\s*[:：]\s*16|1\s*[:：]\s*1|4\s*[:：]\s*3)(?!\d)',text)
 if not ratios:warnings.append('未明确画幅，需核对项目选择')
 if aspect and ratios and any(re.sub(r'\s','',x).replace('：',':')!=aspect for x in ratios):errors.append('画幅与明确目标不一致')
 for i,m in enumerate(nodes):
  start,end=map(float,m.group(1,2));body=text[m.end():nodes[i+1].start() if i+1<len(nodes) else len(text)];bodies.append(body);spans.append(end-start)
  if end<=start or start<0:errors.append(f'节点{i+1}时长无效')
  if start<last-0.001:errors.append(f'节点{i+1}时间重叠')
  elif start>last+0.001:errors.append(f'节点{i+1}时间空缺')
  last=end
  for d in DIALOGUE.finditer(body):
   ds,de=map(float,d.group(1,2));line=d.group(3)
   if ds<start or de>end or de<=ds:errors.append(f'节点{i+1}台词时间越界')
   if not re.search(r'[（(][^）)]+[）)]',line):warnings.append(f'节点{i+1}对白语气未明确')
   words=re.search(r'[“"](.*?)[”"]',line)
   if words and de>ds:
    count=len(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]',words.group(1)))
    if count/(de-ds)>5:warnings.append(f'节点{i+1}对白容量偏紧（估算超过5字/秒，须另计停顿）')
  if re.search(r'\bOS\b|\bVO\b|内心独白|画外',body,re.I) and re.search(r'嘴唇.*?开合|张嘴|开口|口型',body):warnings.append(f'节点{i+1}画外声与可见开口词同段，核对是否为同一人物；不是自动判错')
  if re.search(r'手部特写|紧特写|大特写',body) and re.search(r'全屋|屋顶崩|房顶|整个房间',body):warnings.append(f'节点{i+1}景别可能无法容纳空间级事件')
  if re.search(r'宣判|厉声|怒吼|命令',body) and re.search(r'把玩|摩挲|摆弄',body):warnings.append(f'节点{i+1}强语气与闲适道具动作同段，核对是否同一人物或有意反差')
  if re.search(r'[（(](开心|难过|愤怒|悲伤|高兴)[）)]',body):warnings.append(f'节点{i+1}语气位仅情绪结果词，核对声线、气息、速度或重音')
  if re.search(r'玉佩|银镯|镜面|铜镜',body) and re.search(r'举向|举起.*对着|映出.*火苗|倒映.*灯火',body):warnings.append(f'节点{i+1}反光道具光路触发词，核对材质反射是否被误写成自发光；剧情明确发光可保留')
  if re.search(r'不发光|不透光|面无笑意|不要出现|禁止出现',body):warnings.append(f'节点{i+1}正文含否定式结果约束，考虑正向可见描述；不自动删原文')
  if re.search(r'末态继承|拼接节点|换机位规则',body):warnings.append(f'节点{i+1}正文混入流程规则名词')
  if end-start>6:warnings.append(f'节点{i+1}较长，核对是否包含多个动作/反应阶段；不强制切镜')
  if not DIALOGUE.search(body) and end-start>5 and re.search(r'空镜|氛围|静止',body):warnings.append(f'节点{i+1}无对白静态/氛围较长，核对戏剧任务，不能自动判为拉伸')
  if re.search(r'这只手|那张脸|那个身影|这道光',body):warnings.append(f'节点{i+1}悬空指代，核对是否有具名主体/来源锚点')
  if re.search(r'极具压迫感|极为震撼|极其炫酷',body):warnings.append(f'节点{i+1}抽象结果词，考虑可见动作、表情或材质反馈')
  if '【音效】' not in body:warnings.append(f'节点{i+1}未独立填写音效，请确认是否有意静默')
 if duration is not None and abs(last-duration)>0.01:errors.append('时间轴总时长与目标不一致')
 if max_duration is not None and last>max_duration:errors.append('超过用户明确设置的片段时长上限')
 if len(spans)>=4 and max(spans.count(x) for x in spans)/len(spans)>=.7:warnings.append('节点时长高度雷同，核对是否按动作/对白容量而非机械等分')
 for previous,current in zip(bodies,bodies[1:]):
  if re.search(r'撑起|坐起|起身',previous) and re.search(r'躺|卧',current) and not re.search(r'躺回|跌回|倒回|另一人',current):warnings.append('可能有姿态回退，需按具体角色核对')
 if characters and bodies and not any(name in bodies[0] for name in characters) and '空镜' not in bodies[0]:warnings.append('首节点缺少明确主体锚点，核对镜头任务')
 body_all='\n'.join(bodies)
 for name in characters or []:
  if name not in body_all:warnings.append('已声明角色未在画面正文出现：'+name+'；核对离画/未入镜例外')
 for label in ['【站位声明】','【资产绑定】','【接续状态】','【SHOT动作脚本】','【参数契约】']:
  if label in text:errors.append('混入非默认框架字段：'+label)
 if re.search(r'SEG\d+-P\d+|\bTMP-(?:CH|SC|PR)|REF[:：]',text):errors.append('混入内部制作标识')
 return {'valid':not errors,'nodes':len(nodes),'duration':last,'errors':errors,'warnings':list(dict.fromkeys(warnings)),'scope':'结构与启发式告警，非自动语义/图像/成片质量判定'}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('--duration',type=float);ap.add_argument('--model',help='目标记录，不沿用历史硬参数');ap.add_argument('--characters',help='明确需核对的人名，以逗号分隔');ap.add_argument('--max-duration',type=float);ap.add_argument('--aspect');ap.add_argument('-o','--output');a=ap.parse_args();r=validate_text(Path(a.input).read_text(encoding='utf-8-sig'),a.duration,a.characters.split(',') if a.characters else None,a.max_duration,a.aspect);r['model_record']=a.model;s=json.dumps(r,ensure_ascii=False,indent=2)
 if a.output:Path(a.output).write_text(s,encoding='utf-8')
 print(s);raise SystemExit(0 if r['valid'] else 1)
if __name__=='__main__':main()
