"""LIMEN v2 key visuals. Hand-authored SVG geometry; deterministic output.
Run: python -X utf8 build_svg.py, then node render.cjs, then python -X utf8 package.py.
"""
from pathlib import Path
import math, random, re, json, html

OUT = Path(__file__).resolve().parent
SOURCE = OUT.parent / '개발로그영상_키비주얼_프롬프트_v2.html'
SCENES = json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>', SOURCE.read_text(encoding='utf-8'), re.S).group(1))
BG='#0B0C0E'; WHITE='#E8EAED'; SUB='#5B626C'; HAIR='#22262C'; BLUE='#3D8BFF'; RED='#FF4B3A'; GREEN='#33E07A'; TEAL='#0E3B40'; FLY='#D4F25A'; TEXT='#8A919B'; DIM='#3A4048'

def f(v):
    return f'{v:.3f}'.rstrip('0').rstrip('.') if isinstance(v,float) else str(v)
def attrs(**kw):
    return ' '.join(f'{k.replace("_","-")}="{html.escape(f(v),quote=True)}"' for k,v in kw.items() if v is not None)
def tag(name, inner='', **kw): return f'<{name} {attrs(**kw)}>{inner}</{name}>'
def group(inner, **kw): return tag('g',inner,**kw)
def rect(x,y,w,h,fill='none',stroke=None,sw=2,r=0,**kw): return tag('rect',x=x,y=y,width=w,height=h,rx=r,fill=fill,stroke=stroke,stroke_width=sw,**kw)
def line(x1,y1,x2,y2,c=WHITE,w=2,**kw): return tag('line',x1=x1,y1=y1,x2=x2,y2=y2,stroke=c,stroke_width=w,**kw)
def circle(x,y,r,c='none',stroke=None,w=2,**kw): return tag('circle',cx=x,cy=y,r=r,fill=c,stroke=stroke,stroke_width=w,**kw)
def path(d,c=WHITE,w=2,fill='none',**kw): return tag('path',d=d,stroke=c,stroke_width=w,fill=fill,**kw)
def poly(pts,c=WHITE,w=2,fill='none',**kw): return tag('polygon',points=' '.join(f'{f(x)},{f(y)}' for x,y in pts),stroke=c,stroke_width=w,fill=fill,**kw)
def text(x,y,t,size=24,c=TEXT,anchor='start',weight=400): return tag('text',html.escape(t),x=x,y=y,fill=c,font_size=size,font_family='Consolas, monospace',font_weight=weight,text_anchor=anchor)
def use(name,x,y,s=1,rot=0,c=WHITE,**kw): return tag('use',href='#'+name,transform=f'translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(s)})',color=c,**kw)
def arrow(d,c=SUB,w=1.5,**kw): return path(d,c,w,marker_end='url(#arrow-'+('blue' if c==BLUE else 'green' if c==GREEN else 'red' if c==RED else 'sub')+')',**kw)
def xmark(x,y,r=7,c=RED): return line(x-r,y-r,x+r,y+r,c,2)+line(x+r,y-r,x-r,y+r,c,2)
def check(x,y,r=18): return circle(x,y,r,'none',GREEN,2)+path(f'M{x-8} {y} l6 6 l11 -13',GREEN,2.5)
def dimline(x1,y1,x2,y2,label=''):
    dx=x2-x1;dy=y2-y1; l=math.hypot(dx,dy);nx=-dy/l*6;ny=dx/l*6
    return line(x1,y1,x2,y2,SUB,1)+line(x1-nx,y1-ny,x1+nx,y1+ny,SUB,1)+line(x2-nx,y2-ny,x2+nx,y2+ny,SUB,1)+(text((x1+x2)/2,(y1+y2)/2+32,label,24,TEXT,'middle') if label else '')
def flow(d,packets=()):
    return path(d,BLUE,3,stroke_dasharray='2 10')+''.join(rect(x-5,y-3,10,6,BLUE,r=1) for x,y in packets)
def lan(p0,pc,p1):
    t=.6;x=(1-t)**2*p0[0]+2*(1-t)*t*pc[0]+t*t*p1[0];y=(1-t)**2*p0[1]+2*(1-t)*t*pc[1]+t*t*p1[1]
    return path(f'M{p0[0]} {p0[1]} Q{pc[0]} {pc[1]} {p1[0]} {p1[1]}',RED,3,stroke_dasharray='2 10')+circle(x,y,6,RED)+circle(*p0,4,RED)+circle(*p1,4,RED)
def brackets(x,y,w,h,c=WHITE,l=40,pad=16):
    return ''.join(path(f'M{a+sx*l} {b} H{a} V{b+sy*l}',c,2) for a,b,sx,sy in [(x-pad,y-pad,1,1),(x+w+pad,y-pad,-1,1),(x-pad,y+h+pad,1,-1),(x+w+pad,y+h+pad,-1,-1)])
def live(x=240,y=135,w=1440,h=810,label='L3',br=True,fill='#1A1D21',border=WHITE,sw=1.5):
    return group(rect(x,y,w,h,fill,border,sw,12)+line(x+1,y+1,x+w-1,y+h-1,'#2A2F36',1)+line(x+w-1,y+1,x+1,y+h-1,'#2A2F36',1)+text(x+24,y+38,label,22)+(brackets(x,y,w,h) if br else ''),id='live-'+label+'-'+str(x)+'-'+str(y))

def make_defs():
    s=''
    icons={
      'KINECT_SIDE':rect(-32,-9,64,18,'none','currentColor',2,9)+circle(-14,0,4,'none','currentColor')+circle(14,0,4,'none','currentColor')+line(0,9,0,33,'currentColor')+line(-12,33,12,33,'currentColor'),
      'KINECT_TOP':rect(-20,-6,40,12,BG,'currentColor',2,6)+poly([(-5,-14),(0,-22),(5,-14)],'currentColor',1,'currentColor'),
      'PC':rect(-22,-32,44,64,BG,'currentColor',2,4)+line(-10,-17,10,-17,'currentColor')+line(-10,-10,10,-10,'currentColor')+circle(0,20,3,'none','currentColor'),
      'PROJECTOR':rect(-28,-16,56,32,BG,'currentColor',2,4)+circle(13,0,9,'none','currentColor')+line(-17,-5,-8,-5,'currentColor',1)+line(-17,1,-8,1,'currentColor',1),
      'PERSON_TOP':circle(0,0,10,'currentColor')+line(0,-10,0,-24,'currentColor',2),
      'PERSON_SIDE':circle(0,-107,14,'none','currentColor')+rect(-14,-90,28,90,'none','currentColor',2,14),
      'NODE':circle(0,0,22,BG,'currentColor',2),
      'NET_ICON':path('M-36 -40 H36 V0 H76 V40 H-76 V0 H-36 Z','currentColor',2,TEAL)+line(-36,0,36,0,SUB,1,stroke_dasharray='4 6')+line(-36,0,-36,40,SUB,1,stroke_dasharray='4 6')+line(36,0,36,40,SUB,1,stroke_dasharray='4 6')+path('M-68 24 C-30 -12 -14 50 25 14 S12 -10 14 -32',FLY,2)+circle(-47,13,2,FLY)+circle(52,26,2,FLY)+circle(-9,-21,2,FLY),
    }
    joints=[(0,-94),(0,-70),(0,-36),(0,0),(-28,-62),(28,-62),(-47,-22),(47,-22),(-62,12),(62,12),(-18,8),(18,8),(-24,55),(24,55),(-28,103)]
    bones=[(0,1),(1,2),(2,3),(1,4),(1,5),(4,6),(5,7),(6,8),(7,9),(3,10),(3,11),(10,12),(11,13),(12,14)]
    icons['SKELETON']=''.join(line(*joints[a],*joints[b],'currentColor',2) for a,b in bones)+line(24,55,28,103,'currentColor',2)+''.join(circle(x,y,4,'currentColor') for i,(x,y) in enumerate(joints) if i!=2)+circle(28,103,4,'currentColor')
    for k,v in icons.items(): s+=tag('symbol',v,id=k,overflow='visible')
    for k,c in [('sub',SUB),('blue',BLUE),('green',GREEN),('red',RED)]:
        s+=tag('marker',path('M1 1 L7 4 L1 7','none',0,c),id='arrow-'+k,viewBox='0 0 8 8',refX=7,refY=4,markerWidth=7,markerHeight=7,orient='auto',markerUnits='userSpaceOnUse')
    s+=tag('pattern',line(0,12,12,0,HAIR,1),id='hatch',width=12,height=12,patternUnits='userSpaceOnUse')
    s+=tag('clipPath',rect(360,207,1200,667),id='room-clip')
    # Single 70-degree annular cone, 20 degrees inward, shared by all plan views.
    def polar(r,a): return (r*math.sin(math.radians(a)),-r*math.cos(math.radians(a)))
    a,b,c,d=polar(750,-15),polar(750,55),polar(83,55),polar(83,-15)
    cone=f'M{f(a[0])} {f(a[1])} A750 750 0 0 1 {f(b[0])} {f(b[1])} L{f(c[0])} {f(c[1])} A83 83 0 0 0 {f(d[0])} {f(d[1])} Z'
    s+=tag('path',id='cone',d=cone)
    s+=tag('mask',rect(0,0,1920,1080,WHITE)+tag('use',href='#cone',transform='translate(360 874)',fill='#000000'),id='blind-a',maskUnits='userSpaceOnUse',x=0,y=0,width=1920,height=1080)
    s+=tag('mask',rect(0,0,1920,1080,WHITE)+tag('use',href='#cone',transform='translate(360 874)',fill='#000000')+tag('use',href='#cone',transform='translate(1560 874) scale(-1 1)',fill='#000000'),id='blind-ab',maskUnits='userSpaceOnUse',x=0,y=0,width=1920,height=1080)
    s+=tag('linearGradient',tag('stop',offset='0%',stop_color=DIM)+tag('stop',offset='35%',stop_color=WHITE)+tag('stop',offset='65%',stop_color=WHITE)+tag('stop',offset='100%',stop_color=DIM),id='landing',gradientUnits='userSpaceOnUse',x1=0,y1=760,x2=1920,y2=760)
    return s
DEFS=make_defs()

def plan(two=True,opacity=.18,hatch=False,labels=True):
    s=''
    if hatch:s+=rect(360,207,1200,667,'url(#hatch)',mask='url(#blind-'+('ab' if two else 'a')+')')
    cones=tag('use',href='#cone',transform='translate(360 874)',fill=BLUE,fill_opacity=opacity,stroke=BLUE,stroke_opacity=.7,stroke_width=1.5)
    if two:cones+=tag('use',href='#cone',transform='translate(1560 874) scale(-1 1)',fill=BLUE,fill_opacity=opacity,stroke=BLUE,stroke_opacity=.7,stroke_width=1.5)
    s+=group(cones,clip_path='url(#room-clip)')
    s+=path('M360 874 V207 H1560 V874',WHITE,2)+line(360,874,1560,874,SUB,1.5,stroke_dasharray='6 8')
    s+=use('KINECT_TOP',360,874,rot=20)+(text(318,919,'A') if labels else '')
    if two:s+=use('KINECT_TOP',1560,874,rot=-20)+(text(1590,919,'B') if labels else '')
    return s
def percentage(value):
    return text(1470,320,f'{value:.1f}%',72,WHITE,'end',700)+rect(1230,350,240,6,HAIR,r=3)+rect(1230,350,240*value/100,6,BLUE,r=3)

# Room projection: equal world units, horizontal axes at +/-30 degrees.
def room(k=80,ox=849,oy=480,content=False,fold=False,pulses=False):
    def p(x,y,z=0):return (ox+(x-y)*math.cos(math.pi/6)*k,oy+(x+y)*.5*k-z*k)
    F=[p(0,0),p(7.2,0),p(7.2,4),p(0,4)]
    walls=[(p(0,0),p(7.2,0),p(7.2,0,4),p(0,0,4)),(p(0,0),p(0,4),p(0,4,4),p(0,0,4)),(p(7.2,0),p(7.2,4),p(7.2,4,4),p(7.2,0,4))]
    if fold:
        walls[1]=(p(0,0),p(0,4),p(-2,4,3.464),p(-2,0,3.464))
        walls[2]=(p(7.2,0),p(7.2,4),p(9.2,4,3.464),p(9.2,0,3.464))
    s=poly(F,WHITE,2,TEAL if content else BG)
    for x in range(1,12):s+=line(*p(x*.6,0),*p(x*.6,4),HAIR,1)
    for y in range(1,7):s+=line(*p(0,y*.6),*p(7.2,y*.6),HAIR,1)
    for w in walls:s+=poly(w,WHITE,2,TEAL if content else 'none',fill_opacity=.5 if content else 1)
    if content:
        rng=random.Random(404)
        maps=[lambda u,v:p(u*7.2,v*4),lambda u,v:p(u*7.2,0,v*4),lambda u,v:p(0,u*4,v*4),lambda u,v:p(7.2,u*4,v*4)]
        # One continuous surface path, linked across left/floor/right/back seams.
        route=[p(0,3,2.7),p(0,2.5,1.4),p(0,2,0),p(2,1.2,0),p(4.5,3,0),p(7.2,2,0),p(7.2,1,1.5),p(7.2,0,2),p(4.6,0,3),p(2,0,2.3)]
        d=f'M{f(route[0][0])} {f(route[0][1])}'
        for a,b in zip(route,route[1:]):
            mx=(a[0]+b[0])/2;my=(a[1]+b[1])/2
            d+=f' Q{f(mx)} {f(my-18)} {f(b[0])} {f(b[1])}'
        s+=path(d,FLY,2.5)
        for mp in maps:
            for i in range(18):s+=circle(*mp(rng.uniform(.05,.95),rng.uniform(.08,.93)),rng.uniform(1.7,3.7),FLY,opacity=rng.uniform(.4,.9))
        if pulses:
            for mp in maps:
                x,y=mp(.5,.5);s+=circle(x,y,30,'none',WHITE,2)+circle(x,y,48,'none',WHITE,2,opacity=.4)
    s+=line(*p(0,4),*p(7.2,4),WHITE,2,stroke_dasharray='5 8')
    return s,p

def net_large():
    panels=[(600,140,720,400),(200,540,400,400),(600,540,720,400),(1320,540,400,400)]
    s=''.join(rect(x,y,w,h,TEAL,WHITE,2) for x,y,w,h in panels)
    s+=line(600,540,1320,540,SUB,1.5,stroke_dasharray='4 6')+line(600,540,600,940,SUB,1.5,stroke_dasharray='4 6')+line(1320,540,1320,940,SUB,1.5,stroke_dasharray='4 6')
    s+=path('M230 792 C390 580 470 830 600 734 S840 600 1000 735 S1220 880 1320 734 S1570 570 1690 700 M1000 735 C1130 660 1040 605 1060 540 S1170 320 930 200',FLY,3)
    rng=random.Random(404)
    for i in range(66):
        x,y,w,h=panels[i%4];s+=circle(rng.uniform(x+18,x+w-18),rng.uniform(y+18,y+h-18),rng.uniform(2,5),FLY,opacity=rng.uniform(.45,1))
    for x,y in [(600,734),(1320,734),(1060,540),(600,800)]:s+=circle(x,y,4,FLY)
    for x,y in [(600,734),(1060,540)]:
        s+=circle(x,y,16,'none',WHITE,1.5)+path(f'M{x+12} {y-12} l40 -40 h50',SUB,1)
    for d in ['M480 488 Q480 410 570 410','M1440 488 Q1440 410 1350 410','M1380 330 Q1460 330 1460 425']:s+=arrow(d)
    return s+brackets(200,140,1520,800)

def node(x,y,kind):
    s=use('NODE',x,y)
    shapes={
      'cube':path('M0 -12 L12 -6 V7 L0 14 L-12 7 V-6 Z M-12 -6 L0 0 L12 -6 M0 0 V14',WHITE,1.3),
      'transfer':path('M-12 -5 H10 M4 -11 L10 -5 L4 1 M-12 6 H10 M4 0 L10 6 L4 12',WHITE,1.5),
      'warp':path('M-12 -12 Q0 -17 12 -12 L15 13 Q0 8 -12 13 Z M-4 -14 V11 M5 -14 L7 11 M-12 -4 Q0 -8 13 -4 M-12 5 Q0 0 14 5',WHITE,1),
      'merge':path('M-13 -10 L-4 0 H12 M-13 10 L-4 0 M6 -6 L12 0 L6 6',WHITE,1.5)}
    return s+group(shapes[kind],transform=f'translate({x} {y})')
def projector(x,y,label=None,beam=True):
    s=''
    if beam:s+=poly([(x+28,y),(x+150,y-55),(x+150,y+55)],None,0,WHITE,opacity=.06)+line(x+28,y,x+150,y-55,SUB,1)+line(x+28,y,x+150,y+55,SUB,1)
    return s+use('PROJECTOR',x,y)+(text(x-44,y+51,label,22) if label else '')
def safe_grid():
    s=rect(400,247,1120,587,'none',GREEN,2)
    for x in range(460,1520,60):s+=line(x,247,x,834,GREEN,1,opacity=.18)
    for y in range(307,834,60):s+=line(400,y,1520,y,GREEN,1,opacity=.18)
    return s
def trail(x,y):return path(f'M{x-110} {y+48} Q{x-25} {y+60} {x} {y+20}',SUB,1.5,stroke_dasharray='3 8')
def stamp(x,y,scale=1,angle=0,success=False,op=1):
    w=340 if success else 260;c=GREEN if success else RED
    inner=rect(-w/2,-48,w,96,'none',c,6,10)+rect(-w/2+8,-40,w-16,80,'none',c,1,4)+text(0,20,'SUCCESS' if success else 'FAIL',54 if success else 56,c,'middle',800)
    return group(inner,transform=f'translate({x} {y}) rotate({angle}) scale({scale})',opacity=op)
def badge(x,y,kind,muted=False):
    c=SUB if muted else WHITE;s=circle(x,y,28,BG,c,1.5)
    if kind==0:
        for dx,dy in [(-5,-4),(5,5)]:s+=circle(x+dx,y+dy,10,'none',c,1)+line(x+dx-16,y+dy,x+dx+16,y+dy,c,1)+line(x+dx,y+dy-16,x+dx,y+dy+16,c,1)
    elif kind==1:
        for yy,rr in [(-10,4),(0,5),(11,7)]:s+=circle(x,y+yy,rr,'none',c,1.5)
        for yy in [-6,1,8]:s+=path(f'M{x-16} {y+yy-5} L{x-5} {y+yy} M{x+5} {y+yy} L{x+16} {y+yy-5}',c,1.5)
    elif kind==2:s+=line(x-6,y-12,x-6,y+12,c,3)+line(x+6,y-12,x+6,y+12,c,3)
    else:
        for dx,dy in [(0,-8),(-11,10),(11,10)]:s+=use('PERSON_TOP',x+dx,y+dy,.4,c=c)
    return s
def grid(n,state):
    w,h,gap={2:(800,450,24),3:(528,297,18),4:(392,220,14)}[n]
    x0=(1920-(w*n+gap*(n-1)))/2;y0=(1080-(h*n+gap*(n-1)))/2;s=''
    angles=[-9,6,-4,10,-7,4,8,-5,3,-8,5,-3,9,-6,7,2]
    for i in range(n*n):
        x=x0+(i%n)*(w+gap);y=y0+(i//n)*(h+gap);target=n==4 and i==6
        failed=state!='plain' and (n==2 or (n==3 and i<6) or (n==4 and not target))
        success=state=='success' and target
        part=live(x,y,w,h,'L4' if success else 'L3',False,'#141619' if failed else '#1A1D21',GREEN if success else WHITE,4 if success else 1.5)
        if n==2:part+=badge(x+52,y+52,i,failed)
        if failed:part+=stamp(x+w/2,y+h/2,{2:1,3:.65,4:.45}[n],angles[i])
        if n==3 and i==6:part+=stamp(x+w/2,y+h/2,.65*1.3,angles[i],op=.6)
        if success:part+=rect(x-8,y-8,w+16,h+16,'none',GREEN,1,16)+stamp(x+w/2,y+h/2,1,-6,True)
        s+=group(part,opacity=.35 if state=='success' and not target else 1)
    return s

def axes(x,y,c=WHITE,rot=0):return group(arrow('M0 0 H60',c)+arrow('M0 0 V-60',c)+circle(0,0,3,c),transform=f'translate({x} {y}) rotate({rot})')
def cluster(x,y,c=WHITE,rot=0,r=4,outline=False):
    pts=[(-7,-36),(7,-36),(0,-27),(-14,-14),(0,-14),(14,-14),(-22,0),(0,0),(22,0),(-12,14),(12,14),(-14,28),(14,28),(0,37)]
    return group(''.join(circle(a,b,r,'none' if outline else c,c if outline else None,1.7) for a,b in pts),transform=f'translate({x} {y}) rotate({rot})')

def multiverse(receding=False):
    # Shared trunks split into six groups, then 48 long parallel terminal lanes.
    s=line(160,540,420,540,WHITE,3)+circle(160,540,8,WHITE)
    for j,y in enumerate([340,740]):
        s+=path(f'M420 540 C510 540 550 {y} 640 {y}',SUB,1.5)+circle(640,y,3,SUB)
    for g in range(6):
        gy=156+(g*8+3.5)*16.35;py=340 if g<3 else 740
        c=RED if g in [1,4] else SUB
        s+=path(f'M640 {py} C730 {py} 770 {gy} 860 {gy}',c,1.5)+circle(860,gy,3,c)
        for j in range(8):
            i=g*8+j;ty=156+i*16.35;c=RED if i%3==0 else SUB if abs(ty-540)<190 else DIM
            s+=path(f'M860 {gy} C1080 {gy} 1100 {ty} 1320 {ty} H1750',c,1.5)
            ix=1778
            if i%5 in [0,1]:
                for a,b in ([(-5,-4),(5,-4),(0,4)] if i%5==0 else [(-5,-4),(5,-4),(-5,4),(5,4)]):s+=circle(ix+a,ty+b,2.5,c)
            elif i%5==2:s+=circle(ix,ty,8,'none',RED,1.5,stroke_dasharray='2 4')
            elif i%5==3:s+=xmark(ix,ty,6)
            else:s+=circle(ix-4,ty,6,'none',c,1)+circle(ix+4,ty,6,'none',c,1)
    if receding:s=group(s,transform='translate(160 260) scale(.53 .52)')
    return s

def structure(partial=False):
    s=''
    # Main PC is a grouped boundary containing fusion. Sender feeds this boundary.
    s+=rect(355,355,360,245,'none',SUB,1,16)
    s+=use('KINECT_SIDE',200,420)+text(200,385,'A',22,TEXT,'middle')+use('KINECT_SIDE',200,690)+text(200,655,'B',22,TEXT,'middle')
    s+=use('PC',400,420)+use('PC',400,690)
    s+=line(232,420,378,420)+line(232,690,378,690)
    s+=lan((378,690),(250,555),(378,420))+text(280,565,'LAN',22,RED,'middle')
    s+=flow('M422 420 H500 Q520 420 520 440 V520 Q520 540 540 540 H618',[(500,420),(573,540)])
    s+=flow('M422 690 H480 Q500 690 500 670 V580 Q500 560 520 560 H590 Q610 560 618 545',[(475,690),(548,560)])
    s+=node(640,540,'merge')
    if not partial:s+=flow('M662 540 H780',[(733,540)])
    nx,ny=(960,290) if partial else (900,540)
    s+=use('NET_ICON',nx,ny,1.74 if partial else 1.58,rot=-7 if partial else 0,opacity=.7 if partial else 1)
    if partial:s+=path('M960 150 V240',SUB,1.5,stroke_dasharray='3 7')
    for i,y in enumerate([360,480,600,720]):
        py=y+(i-1.5)*45 if partial else y;px=1240+(i%2)*40 if partial else 1180
        if not partial:
            s+=flow(f'M1020 540 C1090 540 1090 {y} 1150 {y}',[(1110,y+(540-y)*.06)])
            s+=poly([(1208,y),(1440,410+i*65),(1490,455+i*65)],None,0,WHITE,opacity=.06)
            s+=line(1208,y,1440,410+i*65,SUB,1)
        else:s+=path(f'M{px+180} {py-70} L{px+45} {py-10}',SUB,1.5,stroke_dasharray='3 7')
        s+=group(projector(px,py,'P'+str(i+1),False),opacity=.7 if partial else 1)
    rr,_=room(k=30 if partial else 28,ox=1650 if partial else 1565,oy=690 if partial else 500,content=True)
    s+=group(rr,opacity=.7 if partial else 1)
    if partial:s+=path('M1740 920 L1650 800',SUB,1.5,stroke_dasharray='3 7')
    return s

def scene(id):
    rng=random.Random(id);s=''
    if id=='S01':
        s=rect(360,430,4,36,WHITE,r=2)
        for row in range(7):
            x=360
            for i in range(rng.randint(3,6)):
                w=rng.randint(16,90)*(0.5 if row==4 and i==2 else 1)
                s+=rect(x,486+row*22,w,4,TEXT if row==4 else DIM,r=2,opacity=.18 if row>4 else 1);x+=w+10
    elif id=='S02':
        s=line(0,760,1920,760,'url(#landing)',2)
        for i in range(50):
            x=rng.uniform(350,1570);y=rng.uniform(200,725);h=min(750-y,30+130*(y-200)/525)
            s+=line(x,y,x,y+h,TEXT if y>580 else DIM,3)
        for y,w in [(748,28),(754,46),(766,18)]:s+=line(960-w/2,y,960+w/2,y,WHITE,1)
    elif id=='S03':
        s,p=room(fold=True)
        a=p(0,4);b=p(7.2,4);s+=dimline(a[0],a[1]+40,b[0],b[1]+40,'7.2m')
        s+=arrow('M490 620 C420 570 450 430 510 410',stroke_dasharray='4 6')+arrow('M1500 750 C1580 720 1550 580 1480 550',stroke_dasharray='4 6')
    elif id=='S04':s=net_large()
    elif id=='S05':
        s=use('NET_ICON',320,540,1.05)+flow('M400 540 H598',[(470,540),(550,540)])
        for x,k in [(620,'cube'),(860,'transfer'),(1100,'warp')]:
            if x<1100:s+=flow(f'M{x+22} 540 H{x+218}',[(x+110,540)])
            s+=node(x,540,k)
        for i,y in enumerate([300,460,620,780]):
            s+=flow(f'M1122 540 C1280 540 1310 {y} 1472 {y}',[(1420,y)])+projector(1500,y,'P'+str(i+1))
    elif id=='S06':
        rr,p=room(k=65,ox=870,oy=525,content=True,pulses=True)
        for i,(x,y) in enumerate([(570,250),(830,220),(1090,220),(1350,250)]):
            target=[p(0,2,2),p(3.6,0,2),p(3.6,2),p(7.2,2,2)][i]
            s+=flow(f'M960 120 C960 160 {x} 150 {x} {y-22}')
            s+=poly([(x+13,y), (target[0]-60,target[1]),(target[0]+60,target[1])],None,0,WHITE,opacity=.06)+line(x+13,y,target[0],target[1],SUB,1)
            s+=use('PROJECTOR',x,y)
        s+=rr+line(560,120,1360,120,SUB,1.5)+line(960,102,960,138,WHITE,2)+poly([(954,92),(966,92),(960,100)],None,0,WHITE)
    elif id=='S06L':
        s=live(label='L5')
        pts=[(650,320),(1270,320),(1270,650),(650,650),(360,210),(1560,210),(1560,850),(360,850)]
        for shape in [[pts[j] for j in [0,1,2,3]],[pts[j] for j in [4,0,3,7]],[pts[j] for j in [1,5,6,2]],[pts[j] for j in [3,2,6,7]]]:s+=poly(shape,WHITE,2)
        for x,y in pts:s+=circle(x,y,5,WHITE)
    elif id=='S07':s=plan(False,.18,True)+percentage(40.5)
    elif id=='S08':
        s=use('KINECT_SIDE',180,540,1.4)
        s+=line(225,540,1740,350,BLUE,1.5,stroke_dasharray='2 10')+line(225,540,1740,760,BLUE,1.5,stroke_dasharray='2 10')
        s+=use('SKELETON',700,560,2)+use('SKELETON',1220,560,2)+use('SKELETON',1250,560,2,c=RED,stroke_dasharray='3 5')
        for x,t,c in [(555,'L',BLUE),(830,'R',BLUE),(1075,'R',RED),(1355,'L',RED)]:s+=text(x,610,t,28,c,'middle')
        s+=arrow('M890 390 C840 320 1070 320 1030 390')+line(960,310,960,420,SUB,1,stroke_dasharray='3 7')
        s+=arrow('M1100 670 C1140 760 1300 760 1350 805',RED)+arrow('M1350 670 C1310 760 1150 760 1100 805',RED)
    elif id=='S09':
        s=plan(True,.18,True)+percentage(73.4)
        for x,kx in [(420,360),(1500,1560)]:s+=line(x,928,kx,895,SUB,1.5)+use('PC',x,960)
        s+=lan((442,960),(960,1100),(1478,960))+text(960,1060,'LAN',24,RED,'middle')
    elif id=='S09L':
        s=live(label='L6')+circle(550,710,20,'none',WHITE)+circle(1380,570,20,'none',WHITE)+lan((550,710),(870,90),(1380,570))
    elif id=='S10':
        s=poly([(510,390),(1410,390),(1610,830),(310,830)],WHITE,2)
        for x,y in [(310,830),(1610,830)]:
            s+=poly([(x,y),(650,360),(1280,360)],BLUE,1,BLUE,fill_opacity=.14)+poly([(x,y),(610,560),(1310,560)],BLUE,1,BLUE,fill_opacity=.14)
        for x,y in [(510,390),(1410,390),(1610,830),(310,830)]:s+=line(x,y,x,y-80,SUB,1.5)
        for i in range(8):s+=line(400+i*150,900,435+i*150,850,SUB,1)
    elif id=='S11':
        s=line(0,820,1920,820)
        for x in range(0,1920,22):s+=line(x,825,x-14,845,HAIR,1)
        s+=use('KINECT_SIDE',260,700)+line(260,733,260,820,SUB,2)
        shadow=[(806,578),(1780,360),(1780,1000),(806,820)]
        s+=poly(shadow,None,0,'url(#hatch)',clip_path='url(#section-clip)')
        s+=path('M806 578 L1780 360 M806 820 L1780 1000',SUB,1,stroke_dasharray='3 7',clip_path='url(#section-clip)')
        for i in range(9):
            ang=math.radians(-31+i*7.2);xx=1780;yy=700+math.tan(ang)*(xx-292)
            at=700+math.tan(ang)*(806-292)
            if 578<=at<=820:xx=806;yy=at;s+=circle(xx,yy,3,BLUE)
            s+=line(292,700,xx,yy,BLUE,1.5,stroke_dasharray='2 10',clip_path='url(#section-clip)')
        s+=use('PERSON_SIDE',820,820,2)+use('PERSON_SIDE',1240,820,2,c=RED,stroke_dasharray='4 6')+circle(1240,530,20,'none',RED,2)+path('M1255 515 l45 -45 h55',SUB,1)
    elif id=='S12':
        base=plan(True,.09)
        for x,y in [(860,520),(1080,600)]:base+=use('PERSON_TOP',x,y)+line(x+10,y,x+40,y,RED,1)+circle(x+50,y,10,'none',RED,2,stroke_dasharray='3 5')
        s=group(base,id='glitch-base')
        for y in [410,560,740]:
            s+=rect(358,y,1205,40,BG)+group(tag('use',href='#glitch-base',transform='translate(12 0)'),clip_path=f'url(#glitch-{y})')
        s+=text(1220,310,'2',40,WHITE)+text(1270,310,'→ 3 → 4',40,RED)
    elif id=='S12L':
        s=live(label='L7')+text(1730,140,'4',40,RED)
        for x,y in [(780,530),(1240,650)]:s+=circle(x,y,28,'none',RED,3)+xmark(x,y,7)
    elif id=='S13':
        s=group(live(130,378,576,324,'L1',False),opacity=.5)+live(1000,324,768,432,'L2',False)+live(480,270,960,540,'L1')
        s+=line(150,960,1770,960,SUB,1.5)+line(960,835,960,960,SUB,1,stroke_dasharray='3 7')
        for x in range(180,1770,40):s+=line(x,953,x,967,SUB,1)
        for x,t in [(280,'10-12'),(720,'10-15'),(1160,'10-23'),(1600,'10-28')]:s+=line(x,946,x,974,WHITE,2)+text(x,1010,t,24,TEXT,'middle')
    elif id=='S14':s=grid(2,'plain')
    elif id=='S15':s=grid(2,'fail')
    elif id=='S16':s=grid(3,'fail')
    elif id=='S17':s=grid(4,'fail')
    elif id=='S18':s=grid(4,'success')
    elif id=='S19':
        for x,y in [(-300,-110),(380,-210),(1320,-160),(1750,370),(-430,600),(20,1000),(820,1000),(1660,980)]:s+=group(live(x,y,392,220,'L3',False),opacity=.3)
        for i in range(24):
            a=2*math.pi*i/24;dx=math.cos(a);dy=math.sin(a);r=min(735/max(abs(dx),.001),420/max(abs(dy),.001))+20
            s+=line(960+dx*r,540+dy*r,960+dx*(r+70),540+dy*(r+70),SUB,1)
        s+=live(label='L4',border=GREEN,sw=4)+rect(232,127,1456,826,'none',GREEN,1,16)
    elif id in ['S20','S21']:
        good=id=='S21';s=plan(True,.10)+axes(420,790)+axes(1495,790,BLUE,0 if good else 25)
        s+=path('M740 530 C740 360 1150 360 1190 535 S810 750 740 530',SUB,1.5,stroke_dasharray='3 8',opacity=.3 if good else 1,marker_end='url(#arrow-sub)')
        s+=cluster(920,540)
        if good:
            s+=cluster(920,540,BLUE,r=5.3,outline=True)+check(1010,540)+arrow('M1430 805 A80 80 0 0 1 1450 715')
        else:s+=cluster(1010,540,BLUE,25)+dimline(920,630,1010,630)+line(920,590,920,642,SUB,1)+line(1010,590,1010,642,SUB,1)
    elif id=='S22':
        s=plan(True,.1)+safe_grid()
        for x,y in [(820,480),(1100,640)]:s+=trail(x,y)+use('PERSON_TOP',x,y)
    elif id=='S23':
        s=plan(True,.1)+safe_grid()
        # Wedge boundaries pass on either side of the foreground marker and the held position.
        wedge=[(1149,600),(635,247),(666,247),(1175,600)]
        s+=poly(wedge,SUB,1,'#060708',fill_opacity=.85,stroke_dasharray='3 7')+use('PERSON_TOP',1162,600)
        s+=trail(900,420)+circle(900,420,24,'none',GREEN,2)+line(894,410,894,430,GREEN,3)+line(906,410,906,430,GREEN,3)
        s+=path('M900 388 A32 32 0 1 1 868 420',GREEN,3)
    elif id=='S24':s=multiverse()
    elif id=='S25':
        s=group(multiverse(True),opacity=.12)+line(160,540,1060,540,WHITE,3)+circle(160,540,8,WHITE)+line(1100,540,1800,540,WHITE,3)
        s+=circle(1080,540,56,'none',GREEN,1,opacity=.4)+path('M1070 500 H1052 V580 H1070 M1090 500 H1108 V580 H1090',GREEN,3)
        for x in [1360,1560]:s+=use('PERSON_TOP',x,540,rot=90)+line(x-60,532,x-30,532,SUB,1.5)+line(x-47,548,x-26,548,SUB,1)
    elif id=='S26':s=structure(True)
    elif id=='S27':s=structure()
    elif id=='S28':
        s=group(structure(),opacity=.25,stroke_dasharray='2 12',clip_path='url(#fade-left)')
        for i in range(115):
            x=rng.uniform(660,1240);y=rng.uniform(300,590)-(x-660)*.24
            s+=circle(x,y,rng.uniform(2,3),WHITE,opacity=rng.uniform(.2,.65))
        for i in range(150):
            x=rng.uniform(1130,1770);y=rng.uniform(150,530)-(x-1130)*.05
            s+=circle(x,y,rng.uniform(2,6),FLY,opacity=rng.uniform(.3,1))
    else:raise ValueError(id)
    return s

EXTRA=tag('clipPath',rect(0,120,1920,700),id='section-clip')+tag('clipPath',rect(0,0,640,1080),id='fade-left')+''.join(tag('clipPath',rect(350,y,1230,40),id=f'glitch-{y}') for y in [410,560,740])
for item in SCENES:
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080" stroke-linecap="round" stroke-linejoin="round">'
    svg+=tag('title',html.escape(item['id']+' '+item['title']))+tag('desc',html.escape(item['prompt']))
    svg+=tag('defs',DEFS+EXTRA)+rect(0,0,1920,1080,BG)+group(scene(item['id']),id='artwork')+'</svg>'
    (OUT/(item['id']+'.svg')).write_text(svg,encoding='utf-8')
(OUT/'scenes.json').write_text(json.dumps(SCENES,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Wrote {len(SCENES)} SVGs; timeline {sum(x["d"] for x in SCENES)} seconds.')
