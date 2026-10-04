"""fengfeng: arbitrary-count emotion curve PNG using Pillow, no matplotlib installation."""
import argparse,json
from pathlib import Path
def plot_emotion_curve(beats,output):
 from PIL import Image,ImageDraw,ImageFont
 if not beats:raise ValueError('节拍不能为空')
 values=[float(b['value'] if isinstance(b,dict) else b[1]) for b in beats]
 if any(v<0 or v>10 for v in values):raise ValueError('张力需在0—10范围')
 im=Image.new('RGB',(1000,480),'white');d=ImageDraw.Draw(im);font=ImageFont.load_default()
 for v in range(11):
  y=420-v*36;d.line([(60,y),(950,y)],fill='#dddddd');d.text((30,y-6),str(v),fill='black',font=font)
 points=[(60+i*890/max(1,len(values)-1),420-v*36) for i,v in enumerate(values)]
 if len(points)>1:d.line(points,fill='#247a6b',width=4)
 for i,(x,y) in enumerate(points):d.ellipse((x-5,y-5,x+5,y+5),fill='#247a6b');d.text((x,435),str(i+1),fill='black',font=font)
 d.text((60,20),'Emotion tension 0-10 / beat index',fill='black',font=font);im.save(output)
 # Companion retains Chinese labels without font dependencies.
 Path(str(output)+'.json').write_text(json.dumps(beats,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('-i','--input',required=True);ap.add_argument('-o','--out',default='emotion_curve.png');a=ap.parse_args();beats=json.loads(Path(a.input).read_text(encoding='utf-8-sig'));plot_emotion_curve(beats,a.out);print(a.out)
if __name__=='__main__':main()
