"""Validate, create review sheets/storyboard, and package the vector deliverables."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, re, math, html, zipfile, xml.etree.ElementTree as ET

P=Path(__file__).resolve().parent
D=json.loads((P/'scenes.json').read_text(encoding='utf-8'))
FONT='C:/Windows/Fonts/malgun.ttf'
NARRATION={
'S01':'LIMEN의 개발 기록입니다.',
'S03':'정면과 양옆 벽, 바닥으로 이루어진 네 면입니다.',
'S04':'네 면을 하나의 장면으로 연결합니다.',
'S05':'프로젝터 네 대로 나누어 출력합니다.',
'S06':'네 면이 같은 순간을 비추도록 구성했습니다.',
'S07':'키넥트 한 대로는 시야가 부족했습니다.',
'S08':'등을 돌리면 좌우 인식도 뒤바뀌었습니다.',
'S09':'키넥트와 컴퓨터를 두 대로 늘렸습니다.',
'S09L':'두 컴퓨터는 랜선으로 연결했습니다.',
'S11':'앞사람에 가려진 관객이 사라지고,',
'S12':'한 사람이 둘로 잡혀 없는 사람이 생겼습니다.',
'S13':'코드를 고치고 현장에서 시험하기를 반복했습니다.',
'S14':'보정과 반응, 여러 인원을 시험했습니다.',
'S15':'실패를 확인하고 다시 고쳤습니다.',
'S16':'시도는 계속 늘어났습니다.',
'S18':'자체 시험에서 개선을 확인했습니다.',
'S20':'먼저 두 센서의 좌표를 맞췄습니다.',
'S21':'같은 사람이 걸은 위치를 기준으로 보정합니다.',
'S22':'그리고 세이프존을 만들었습니다.',
'S23':'가려진 동안에는 마지막 자리를 유지합니다.',
'S24':'인원이 늘면 경우의 수도 늘어납니다.',
'S25':'시험 설정을 두 명으로 제한했습니다.',
'S26':'메인 컴퓨터에서 두 센서의 입력을 합치고,',
'S27':'하나의 장면을 네 면에 출력하는 구조입니다.',
'S28':'LIMEN의 개발은 이어집니다.'
}
NOTES={
'S06':'4면 동시 출력의 개념도. 최종 워핑·블렌딩 완료를 증명하는 화면이 아닙니다.',
'S06L':'L5 실제 4면 투사 영상 삽입 후, 8개 정합점을 촬영 화면에 맞춰 조정합니다.',
'S07':'40.5%는 참고 프롬프트의 시야 면적 계산값(가림 미반영)입니다. 실제 추적 성공률이 아닙니다. 이 도식은 수치 산출용 면적 차트가 아닙니다.',
'S09':'73.4% 역시 참고 문서의 시야 면적 계산값입니다. 랜선 연결은 현재 기준 2026-10-26 확정 내용을 따릅니다.',
'S09L':'L6 촬영본의 노트북·메인 PC 위치에 포물선 양 끝점을 맞춥니다.',
'S12L':'L7 실제 오류 영상의 유령 위치에 빨간 원을 맞춥니다. 현재 원 위치는 합성용 예시입니다.',
'S18':'SUCCESS는 자체 시험의 개선을 상징합니다. L4 실물 영상은 아직 삽입하지 않았으며, 현장 검증 완료를 뜻하지 않습니다. 대본은 S19까지 이어 읽을 수 있습니다.',
'S20':'선택 숫자 94cm를 생략했습니다. 두 점묶음은 동일한 사람을 본 센서 좌표의 개념 표현입니다.',
'S21':'선택 숫자 0.2cm를 생략했습니다. 보정 후 정확한 겹침은 개념도이며 현장 오차 0을 뜻하지 않습니다.',
'S22':'그려진 격자·40px 여백은 시각화 배치입니다. 실측 세이프존 경계를 새로 확정하지 않습니다.',
'S23':'가려진 동안 유지 타이머가 멈추는 상태. B 센서–앞사람–마지막 위치가 일직선이 되도록 앞사람 x 좌표를 980→1162로 조정했습니다.',
'S25':'개발 시험의 최대 2명 설정입니다. 전시 운영 인원을 2명으로 변경한 뜻이 아닙니다.',
'S26':'메인 PC 영역 안에 합치기 노드를 배치했습니다. 송출 PC는 센서 입력을 전달하며 보정·합치기를 담당하지 않습니다.',
'S27':'메인 PC 영역 안에서 두 센서 입력을 합치는 현재 구조를 표시합니다. 프로젝터는 4대입니다.',
'S28':'개발로그의 마무리 시각화입니다. 본편의 첫 장면은 개미이며 이 그림을 본편 첫 장면으로 설명하지 않습니다.'
}

# Structural checks target the actual delivery contract.
NS={'s':'http://www.w3.org/2000/svg'}
allowed_text={'7.2m','A','B','L','R','LAN','40.5%','73.4%','2','→ 3 → 4','4','10-12','10-15','10-23','10-28','FAIL','SUCCESS'}|{f'P{i}' for i in range(1,5)}|{f'L{i}' for i in range(1,8)}
allowed_colors={'#0B0C0E','#E8EAED','#5B626C','#22262C','#3D8BFF','#FF4B3A','#33E07A','#0E3B40','#D4F25A','#8A919B','#3A4048','#1A1D21','#2A2F36','#141619','#060708','#000000'}
elapsed=0
for s in D:
    mm,ss=map(int,s['t'].split(':'));assert mm*60+ss==elapsed,(s['id'],'time gap');elapsed+=s['d']
    src=(P/(s['id']+'.svg')).read_text(encoding='utf-8');root=ET.fromstring(src)
    assert root.attrib['viewBox']=='0 0 1920 1080'
    assert not root.findall('.//s:image',NS) and not root.findall('.//s:foreignObject',NS)
    assert not root.findall('.//s:filter',NS)
    ids=[e.attrib['id'] for e in root.iter() if 'id' in e.attrib];assert len(ids)==len(set(ids)),s['id']
    for e in root.iter():
        for k,v in e.attrib.items():
            for ref in re.findall(r'url\(#([^)]*)\)',v):assert ref in ids,(s['id'],ref)
            if k=='href':assert v.startswith('#') and v[1:] in ids
            if v.startswith('#') and k in ['fill','stroke','color','stop-color']:assert v.upper() in allowed_colors,(s['id'],v)
    for e in root.findall('.//s:text',NS):assert ''.join(e.itertext()) in allowed_text,(s['id'],e.text)
    with Image.open(P/(s['id']+'.png')) as im:assert im.size==(1920,1080)
    s['narration_draft']=NARRATION.get(s['id'],'')
    s['production_note']=NOTES.get(s['id'],'')
assert len(D)==31 and elapsed==90

# Four-column overview; IDs and titles are outside the actual artwork frames.
cw=480;ch=318;pad=24;header=95
sheet=Image.new('RGB',(cw*4+pad*2,header+ch*8+pad),'#141619')
dr=ImageDraw.Draw(sheet);ft=ImageFont.truetype(FONT,19);fh=ImageFont.truetype(FONT,28)
dr.text((pad,20),'LIMEN · 개발로그 키비주얼 v2',font=fh,fill='#E8EAED')
dr.text((pad,60),'31장면 / 90초 / 1920 × 1080 / 촬영본 자리는 L1–L7로 표시',font=ft,fill='#8A919B')
for i,s in enumerate(D):
    x=pad+(i%4)*cw;y=header+(i//4)*ch
    with Image.open(P/(s['id']+'.png')) as im:sheet.paste(im.convert('RGB').resize((480,270),Image.Resampling.LANCZOS),(x,y))
    dr.text((x+10,y+279),f'{s["id"]}  {s["t"]}  {s["title"]}',font=ft,fill='#E8EAED')
sheet.save(P/'contact_sheet.png')

qa=P/'검수';qa.mkdir(exist_ok=True)
for j in range(4):
    batch=D[j*8:(j+1)*8];im=Image.new('RGB',(1600,1960),'#141619');dr=ImageDraw.Draw(im)
    for i,s in enumerate(batch):
        x=(i%2)*800;y=(i//2)*490
        with Image.open(P/(s['id']+'.png')) as a:im.paste(a.convert('RGB').resize((800,450),Image.Resampling.LANCZOS),(x,y))
        dr.text((x+16,y+455),s['id']+'  '+s['title'],font=ImageFont.truetype(FONT,22),fill='#E8EAED')
    im.save(qa/f'preview_{j+1}.png')

notes='''LIMEN 개발로그 키비주얼 v2 — 제작 메모
작성일: 2026-10-29

산출물
• 31장면 × SVG/PNG 각 1개. PNG는 모두 1920×1080.
• contact_sheet.png: 시간 순서의 4열 확인용 시트.
• index.html / 상위 폴더 개발로그영상_콘티_v2.html: 그림·타임코드·모션 지시·대본 초안. 90초 정지 컷 미리보기 포함.
• build_svg.py, render.cjs, package.py: 도형 생성·PNG 렌더·검수 및 묶음 재생성 코드.
• 이번 산출물은 정지 키비주얼입니다. 완성 모션 영상, 음성, 실물 영상 합성은 포함하지 않습니다.

기준과 상태
• LIMEN_현재기준.md를 프로젝트 사실의 최우선 기준으로 적용했습니다.
• 기준 PDF 19쪽의 텍스트, 동기화 지침, 배포본 01, 키넥트 연구노트 및 중요.md를 대조했습니다.
• 직접 확인한 것은 문서와 생성 이미지입니다. 현장 센서 시험을 수행하지 않았습니다.
• S06·S27은 4면 출력 개념도입니다. 최종 워핑·다인 추적 완료의 증거가 아닙니다.
• 성공·실패 도장은 개발 과정의 시각화입니다. 합성용 L3·L4의 실제 촬영 증거는 추후 넣습니다.
• 대본은 기존 v1 대본을 참고해 v2 타이밍에 맞춰 줄인 AI 편집 초안입니다. 팀 확정 대본이 아닙니다.

프롬프트와 달리 조정한 부분
• S26·S27 합치기 노드를 메인 PC 경계 안에 넣어 송출 PC가 보정한다는 오해를 줄였습니다.
• S23 앞사람 x=980→1162: B 센서와 마지막 자리 사이의 가림 광선을 정렬했습니다.
• S20·S21의 선택 숫자 94cm/0.2cm는 넣지 않았습니다.
• 지정 폰트 Pretendard·JetBrains Mono가 설치되어 있지 않아 SVG 라벨은 Consolas, 확인 페이지는 맑은 고딕을 대체 폰트로 사용했습니다.
• 공통 120px 여백과 개별 지시가 충돌하는 곳은 개별 지시를 따랐습니다(전폭 바닥선, 2×2 분할, 화면 밖으로 밀리는 프레임, S09 LAN).
• 색 토큰 외 #3A4048·#1A1D21·#2A2F36·#141619·#060708은 장면 지시의 명시적 색상입니다. #000000은 보이지 않는 마스크 계산에만 사용했습니다.

시야 수치와 그림의 관계
• 40.5%/73.4%는 참고 프롬프트가 제시한 가림 미반영 바닥 시야 면적입니다. 실제 추적 성공률이 아닙니다.
• 도형은 지시된 1200×667 방, 모서리 센서, 70° 부채꼴, 83/750px 반경, 전방에서 안쪽으로 20° 회전을 따릅니다.
• 이 수치를 문자 그대로 적용한 도형 면적은 참고 비율과 일치하지 않습니다. 지시의 형상·라벨은 보존하되, 면적을 정확히 계량하는 차트로 사용하지 마십시오. 20°의 기준축·센서 실제 오프셋을 확정하면 함께 조정할 수 있습니다.
• 방 높이는 4m라는 확정값을 넣지 않았습니다. 아이소메트릭 높이는 프롬프트가 지정한 도식 비율입니다.

촬영본 교체
L1 코드 화면 → S13
L2 현장 전경 → S13
L3 실패 클립 → S14–S17
L4 성공 클립 → S18–S19
L5 실제 4면 투사 → S06L
L6 랜선·설치 → S09L
L7 오류 화면 → S12L
실물 화면 위 포물선·방 윤곽·오류 원은 촬영본 삽입 뒤 위치를 맞춰야 합니다.

편집
SVG는 외부 이미지·스크립트·폰트 다운로드 없이 열립니다. 반복 도형은 symbol/use로 재사용합니다.
Illustrator 등에서 SVG를 연 뒤 필요하면 심볼을 확장하고 AI로 저장하여 AE에 가져옵니다.
이번 작업은 기존 v1 산출물·콘티·현재 기준 문서를 수정하지 않았습니다.
'''
(P/'제작메모.txt').write_text(notes,encoding='utf-8')
(P/'manifest.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf-8')

TEMPLATE='''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LIMEN 개발로그 콘티 v2</title>
<style>
:root{color-scheme:dark;--bg:#0b0c0e;--panel:#141619;--line:#262a30;--ink:#e8eaed;--sub:#8a919b;--blue:#3d8bff;--green:#33e07a}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.65 'Malgun Gothic',sans-serif}a{color:inherit;text-underline-offset:4px}button{font:inherit;background:#1a1d21;color:var(--ink);border:1px solid #3a4048;padding:8px 14px;border-radius:5px;cursor:pointer}button:hover{border-color:var(--blue)}button:focus-visible,a:focus-visible{outline:2px solid var(--blue);outline-offset:4px}main{max-width:1250px;margin:auto;padding:36px 24px 100px}h1{font-size:28px;margin:0 0 8px}p{margin:8px 0}.sub{color:var(--sub)}.tools{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:20px 0}.viewer{border:1px solid var(--line);background:#000;border-radius:8px;overflow:hidden}.viewer img{display:block;width:100%;aspect-ratio:16/9}.controls{padding:14px 18px;background:var(--panel)}.controls .tools{margin:0}.controls input{width:100%;margin:18px 0 6px;accent-color:var(--blue)}#position{font-family:Consolas,monospace;font-size:13px;color:var(--sub)}#current{font-size:18px;font-weight:600;margin:6px 0}#caption{color:var(--sub);min-height:26px}.note{border-left:2px solid var(--blue);padding:12px 18px;background:var(--panel);margin:28px 0;color:#a3a9b3}.chap{margin:56px 0 18px;padding-bottom:12px;border-bottom:1px solid var(--line);font-size:20px}.card{border:1px solid var(--line);border-radius:8px;margin:16px 0 28px;background:var(--panel);overflow:hidden;scroll-margin-top:20px}.card .row{display:grid;grid-template-columns:1.65fr 1fr}.card img{width:100%;display:block;aspect-ratio:16/9}.desc{padding:20px}.desc h3{margin:7px 0 16px;font-size:18px}.meta{font:13px Consolas,monospace;color:var(--sub)}.label{font-size:12px;color:var(--blue);margin:14px 0 4px}.script{padding:15px 20px;border-top:1px solid var(--line)}.script p{font-size:17px}.production{font-size:13px;color:var(--sub);border-top:1px dashed var(--line);padding-top:12px}.links{font:13px Consolas,monospace;display:flex;gap:18px;margin-top:14px}.jump{display:flex;gap:8px;flex-wrap:wrap;margin:25px 0}.jump a{padding:3px 9px;border:1px solid var(--line);border-radius:4px;text-decoration:none;font:13px Consolas,monospace}.tag{font-size:12px;color:var(--green);margin-left:10px}details{padding:16px;border:1px solid var(--line);margin:26px 0}summary{cursor:pointer;font-weight:600}pre{white-space:pre-wrap;font:14px/1.8 'Malgun Gothic',sans-serif;color:var(--sub)}@media(max-width:800px){main{padding:22px 12px 60px}.card .row{grid-template-columns:1fr}.desc{padding:16px}h1{font-size:23px}.tools{gap:8px}}
</style></head><body><main>
<h1>LIMEN 개발로그 콘티 v2</h1><p class="sub">31장면 · 1분 30초 · SVG 벡터 키비주얼 · 1920×1080</p>
<p class="sub">장면별 대표 프레임과 모션 지시입니다. 실물 영상은 L1–L7 자리에 합성하며, 아래 대본은 v2 타이밍에 맞춘 AI 편집 초안입니다.</p>
<div class="tools"><a href="__BASE__contact_sheet.png">전체 확인용 시트</a><a href="__BASE__제작메모.txt">제작 메모</a><a href="__BASE__manifest.json">장면 데이터</a></div>
<section class="viewer" aria-label="정지 컷 미리보기"><img id="frame" src="__BASE__S01.png" alt="S01 커서와 로그"><div class="controls"><div class="tools"><button id="prev" aria-label="이전 장면">← 이전</button><button id="play">90초 컷 미리보기</button><button id="next" aria-label="다음 장면">다음 →</button><span id="position"></span></div><input id="seek" aria-label="장면 선택" type="range" min="0" max="30" value="0"><div id="current"></div><p id="caption"></p><p class="sub" style="font-size:12px">각 대표 프레임을 지정 시간 동안 보여줍니다. 모션·음성·실물 영상이 포함된 완성 영상은 아닙니다. ← → 키로 장면을 바꿀 수 있습니다.</p></div></section>
<div class="note">40.5%·73.4%는 문서의 시야 면적 계산값이며 추적 성공률이 아닙니다. S18의 성공 도장은 자체 시험 개선을 상징하고, S25의 두 명은 개발 시험 설정입니다. 전시 운영 인원·최종 4면 정합 완료와 구분합니다.</div>
<nav class="jump" aria-label="장면 바로가기">__JUMPS__</nav>
__CARDS__
<details><summary>제작 범위·자료 기준·도식 조정 사항</summary><pre>__NOTES__</pre></details>
</main><script id="scene-data" type="application/json">__DATA__</script><script>
const D=JSON.parse(document.getElementById('scene-data').textContent),base='__BASE__';let ix=0,timer=null,playing=false;
const frame=document.getElementById('frame'),seek=document.getElementById('seek'),play=document.getElementById('play');
function stop(){playing=false;clearTimeout(timer);timer=null;play.textContent='90초 컷 미리보기';}
function show(i){ix=Math.max(0,Math.min(D.length-1,i));const s=D[ix];frame.src=base+s.id+'.png';frame.alt=s.id+' '+s.title;seek.value=ix;document.getElementById('position').textContent=s.t+' · '+s.d+'초 · '+(ix+1)+'/31';document.getElementById('current').textContent=s.id+' — '+s.title;document.getElementById('caption').textContent=s.narration_draft||'말 없음 — 화면 전환';}
function run(){playing=true;play.textContent='일시정지';clearTimeout(timer);timer=setTimeout(()=>{if(ix>=D.length-1){stop();return;}show(ix+1);run();},D[ix].d*1000);}
play.onclick=()=>{if(playing){stop();return;}if(ix===D.length-1)show(0);run();};
document.getElementById('prev').onclick=()=>{stop();show(ix-1);};document.getElementById('next').onclick=()=>{stop();show(ix+1);};seek.oninput=()=>{stop();show(+seek.value);};
document.addEventListener('keydown',e=>{if(['INPUT','BUTTON','A','SUMMARY'].includes(document.activeElement.tagName))return;if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();stop();show(ix+(e.key==='ArrowRight'?1:-1));}});show(0);
</script></body></html>'''

cards=[];last=None
for s in D:
    if s['ch']!=last:cards.append('<h2 class="chap">'+html.escape(s['ch'])+'</h2>');last=s['ch']
    note='<p class="production">'+html.escape(s['production_note'])+'</p>' if s['production_note'] else ''
    cards.append(f'''<article class="card" id="{s['id']}"><div class="row"><a href="__BASE__{s['id']}.png" target="_blank"><img loading="lazy" src="__BASE__{s['id']}.png" alt="{html.escape(s['title'])}"></a><div class="desc"><div class="meta">{s['id']} · {s['t']} · {s['d']}초 <span class="tag">{ {'g':'그래픽','l':'실물','c':'합성'}[s['ty']]}</span></div><h3>{html.escape(s['title'])}</h3><div class="label">이해를 돕는 요소</div><p>{html.escape(s['aid'])}</p><div class="label">모션 · AE 편집 지시</div><p>{html.escape(s['motion'])}</p>{note}<div class="links"><a href="__BASE__{s['id']}.svg">SVG 원본</a><a href="__BASE__{s['id']}.png">PNG 1920×1080</a></div></div></div><div class="script"><div class="label">발표 대본 · AI 편집 초안</div><p>{html.escape(s['narration_draft']) if s['narration_draft'] else '<span class="sub">말 없음 — 화면 전환</span>'}</p></div></article>''')
doc=TEMPLATE.replace('__CARDS__',''.join(cards)).replace('__JUMPS__',''.join(f'<a href="#{s["id"]}">{s["id"]}</a>' for s in D)).replace('__NOTES__',html.escape(notes)).replace('__DATA__',json.dumps(D,ensure_ascii=False).replace('</','<\\/'))
(P/'index.html').write_text(doc.replace('__BASE__',''),encoding='utf-8')
(P.parent/'개발로그영상_콘티_v2.html').write_text(doc.replace('__BASE__','키비주얼_v2/'),encoding='utf-8')
report={'scene_count':31,'duration_seconds':90,'png_dimensions':[1920,1080],'svg_no_raster_elements':True,'svg_external_links':False,'all_internal_references_valid':True,'visible_text_allowlist_passed':True,'colors_passed':True,'timing_continuous':True,'source_prompt':str(P.parent/'개발로그영상_키비주얼_프롬프트_v2.html')}
(qa/'검수결과.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
dest=P.parent/'개발로그_키비주얼_v2_31장_SVG_PNG.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for file in sorted(P.iterdir()):
        if file.is_file():z.write(file,'키비주얼_v2/'+file.name)
    z.write(P.parent/'개발로그영상_콘티_v2.html','개발로그영상_콘티_v2.html')
    z.write(qa/'검수결과.json','키비주얼_v2/검수/검수결과.json')
print('Validated 31 SVG/PNG pairs; wrote contact sheet, v2 storyboard, notes, ZIP:',dest.name)
