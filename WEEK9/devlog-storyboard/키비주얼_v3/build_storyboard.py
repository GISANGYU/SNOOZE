"""Assemble the documentary 3D storyboard, production prompts and contact sheets."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, html, zipfile
P=Path(__file__).resolve().parent
D=json.loads((P/'scenes.json' if (P/'scenes.json').exists() else P.parent/'키비주얼_v2/manifest.json').read_text(encoding='utf-8'))

# id | title | camera | physical action | cut connection | still-frame composition
ROWS='''S01|입체 로그의 시작|거의 탑뷰인 사선 카메라를 고정한다. 시선이 얕은 두께와 바닥 그림자를 읽을 만큼만 기울인다.|흑연색 작업대 위 작은 흰 커서가 깜빡이고, 얇은 로그 막대가 짧은 입체 조각으로 차례로 생긴다.|마지막 로그 조각이 아래로 빠져나가며 S02의 낙하 조각이 된다.|화면 왼쪽 1/3에 얇은 회색 로그 조각 7줄과 흰 커서. 넓은 여백. 로고·코드 문장은 넣지 않는다.
S02|로그가 공간의 모서리가 됨|카메라를 살짝 낮추며 로그 조각의 낙하 방향과 바닥의 깊이를 드러낸다.|조각들이 떨어져 긴 바닥 앞 모서리에 모인다. 착지한 조각은 전시장 모형의 바닥선으로 이어진다.|카메라 위치를 이어 받아 같은 모서리에서 바닥과 벽이 생기는 매치 컷.|중앙 바닥 앞쪽에 가로 모서리, 그 위와 뒤에 떨어지는 짧은 입체 막대. 실제 그림자로 높이 차이를 보여준다.
S03|전시장 모형이 조립됨|입구 오른쪽 위에서 보는 3/4 시점. 벽이 올라오는 동안 10° 이내로만 천천히 이동한다.|7.2×4 바닥 슬래브가 생기고 정면 벽이 올라선다. 양옆 벽은 바닥 경첩을 축으로 60°까지 일어선다.|벽의 움직임을 반대로 이어 S04에서 펼쳐지는 이미지 판으로 전환.|두께가 있는 밝은 회색 바닥, 정면 벽, 반쯤 올라온 양옆 벽. 앞쪽은 열린 입구. 높이 치수는 쓰지 않는다.
S04|네 면을 한 장으로 펼침|높은 사선 시점에서 판들의 위쪽 면이 모두 보이게 한다. 펼침 완료 후 짧게 정지한다.|벽 판이 눕고 네 면이 두께 있는 T자 이미지 판으로 펼쳐진다. 연두 곡선과 점은 판 이음매를 건너 이어진다.|펼친 판이 작아져 S05 장비 흐름의 입력 자리에 들어간다.|청록색 T자 판 4개, 얇은 판 두께와 접지 그림자. 투사 예시인 연두 곡선과 점이 표면을 연결한다.
S05|한 장에서 네 프로젝터로|전체를 읽는 높은 사선 와이드. 데이터가 갈라질 때만 카메라를 오른쪽으로 짧게 따라간다.|이미지 판에서 작은 처리 블록 세 개로 신호가 이동한다. 마지막에서 네 갈래로 나뉘어 프로젝터 4대에 동시에 닿는다.|프로젝터의 빛이 켜지는 순간 S06 전시장 모형의 실제 네 면으로 연결.|작은 이미지 판, 엔진·전송·워핑을 상징하는 무광 처리 블록, 네 대의 흰 프로젝터. P1~P4만 작게 표시한다.
S06|한 공간의 같은 순간|S03의 모형과 같은 방향에서 입구 쪽으로 부드럽게 접근한다. 네 면이 모두 읽히는 위치에서 멈춘다.|4개의 프로젝터가 같은 순간의 청록 면과 연두 점·곡선을 투사한다. 면마다 같은 박자의 얇은 링이 한 번 나타난다.|모형의 벽 모서리를 L5 실제 투사 화면 모서리에 겹치는 매치 디졸브.|정면·양옆·바닥 4면을 가진 컷어웨이 모형. 카메라 쪽 벽은 투시 처리. 투사광은 약한 반투명 쐐기로만 표현한다.
S06L|모형에서 실제 4면 투사로|3D 모형의 시선을 실제 L5 촬영 시선으로 맞춘 뒤 촬영본 고정 카메라를 유지한다.|모형 표면을 실제 영상으로 디졸브하고 모서리 정합점만 잠시 남긴다. 마지막에 정합점도 지운다.|실제 화면의 바닥을 다시 모형 바닥으로 교체하며 S07 센서 설명으로 전환.|대표 이미지는 L5 촬영본이 들어갈 두꺼운 슬레이트 판과 방 윤곽·기준점. 실제 촬영본 삽입 후 최종 위치를 맞춘다.
S07|한 대의 센서가 보는 범위|입구 상공의 높은 사선 시점. 센서→반투명 시야→보이지 않는 바닥 순서로 시선을 옮긴다.|왼쪽 입구의 키넥트 A에서 푸른 시야가 펼쳐진다. 시야 안은 푸른 바닥, 바깥은 회색 바닥으로 남는다.|A는 그대로 두고 반대쪽 입구에 B를 더하는 S09까지 공간 방향을 유지한다.|회색 컷어웨이 방, 작은 키넥트 모형 A, 바닥에 닿는 푸른 시야와 얇은 반투명 시야 면. 면적 숫자는 주 화면에서 생략한다.
S08|몸의 방향과 관절의 혼동|사람 높이에 가까운 비교 샷. 앞모습과 뒷모습 두 모형을 같은 크기로 나란히 놓는다.|왼쪽 사람이 반 바퀴 돌며 오른쪽 뒷모습으로 이어진다. 센서 관측 뼈대가 살짝 어긋나고 좌우 표식이 붉게 바뀐다.|다시 전시장 와이드로 빠져나오며 두 번째 키넥트의 필요성을 연결한다.|무광 흰 인체 모형 2개. 오른쪽에 붉은 관측 뼈대가 겹친다. L/R만 표시하고 인체 복제가 작품 인터랙션이라는 뜻으로 쓰지 않는다.
S09|두 센서와 두 컴퓨터|S07과 같은 방의 높은 사선 시점. B를 추가한 뒤 입구 아래 PC 두 대까지 프레임을 조금 넓힌다.|오른쪽 입구에 키넥트 B와 두 번째 시야가 나타난다. 메인 PC와 송출 노트북이 등장하고 붉은 랜선이 둘을 잇는다.|붉은 랜선의 곡선을 L6 실제 케이블 설치 촬영에 맞춘다.|같은 방 모형과 센서 2대. 입구 밖 메인 PC·노트북, 두 장비를 잇는 물리적 붉은 케이블. 프로젝터 수는 늘리지 않는다.
S09L|실제 케이블 설치|실제 L6 촬영 카메라를 유지한다. 움직이는 손에 카메라를 따로 따라붙이지 않는다.|실물 두 장비의 위치를 3D 케이블 곡선이 잠시 연결한다. 커넥터가 꽂히면 곡선을 촬영본으로 디졸브한다.|케이블 곡선이 푸른 시야 광선으로 변하며 S10 입체 시야 설명으로 넘어간다.|L6 판 위 두 장비 위치 표시와 살짝 떠오른 붉은 케이블 곡선. 촬영본이 들어온 뒤 커브 양 끝을 맞춘다.
S10|상공에서 센서 높이로|탑뷰에 가까운 방 시점에서 카메라를 센서 높이로 낮춘다. 축을 넘지 않고 같은 입구 방향을 유지한다.|평면에 붙어 보이던 시야가 높이를 가진 투시 쐐기로 읽힌다. 카메라가 내려오며 사람의 앞뒤 관계가 드러난다.|바닥과 센서를 고정한 상태로 옆 단면 S11에 연결한다.|방 모형을 낮은 사선에서 본다. 두 푸른 시야 면은 공중에서 서 있고 바닥에는 시야 흔적이 남는다.
S11|앞사람이 시선을 막음|방의 옆면을 잘라낸 눈높이 단면에 가까운 시점. 카메라는 정지하고 가려짐만 관찰한다.|키넥트에서 나온 광선이 앞사람 몸에서 멈춘다. 그 뒤에 어두운 가림 쐐기가 생기고 뒷사람은 붉은 반투명 관측 모형으로 바뀐다.|뒷사람의 붉은 관측 모형이 S12 중복 인식 모형으로 이어진다.|두께 있는 밝은 단면 바닥, 왼쪽 키넥트, 중앙 흰 앞사람, 오른쪽 붉은 뒷사람. 가림 영역은 푸른 감지 영역과 구별되는 어두운 반투명 부피.
S12|두 사람이 여러 관측으로 갈림|다시 높은 사선으로 올라와 같은 방의 두 사람을 내려다본다. 분리 순간에는 카메라를 멈춘다.|실제 사람 2명 옆에 붉은 관측 뼈대가 각각 하나씩 밀려 나온다. 실제 몸과 관측값을 짧은 연결선으로 묶어 원인을 읽게 한다.|붉은 관측값의 위치를 L7 오류 화면의 표시로 넘긴다.|방 안 흰 사람 2명과 옆으로 어긋난 붉은 관측 뼈대 2개. 네 사람이 실제로 들어왔다는 장면으로 그리지 않는다.
S12L|실제 오류를 가리킴|실제 L7 지도·오류 촬영 화면의 고정 시점.|오류 화면에 붉은 링 2개를 맞춰 붙인다. 새 인원이 생기는 순간 링만 짧게 강조한다.|오류 화면이 뒤로 물러나 첫 번째 시험 기록 카드가 된다.|L7 촬영본 자리 판 위에 얇고 입체감 있는 붉은 링. 실제 유령 위치는 영상 삽입 후 정한다.
S13|반복된 개발 기록|깊이가 다른 기록 판 사이로 카메라가 짧게 이동한다. 다음 장면의 정면 그리드로 서서히 정렬한다.|코드·현장 영상 판 3장이 서로 다른 높이에서 교차한다. 아래 날짜 눈금은 시험 기록이 쌓이는 방향으로 이동한다.|가장 앞의 판이 4개 판으로 갈라지며 S14가 된다.|L1·L2·L1 촬영본 판 3개가 앞뒤로 겹친다. 날짜는 10-12·10-15·10-23·10-28. 과한 회전이나 유리 반사는 쓰지 않는다.
S14|네 가지 시험을 나란히|거의 정면인 높은 사선 시점. 네 판의 두께와 그림자가 보일 정도만 기울인다.|영상 판 1장이 2×2의 물리적 카드로 나뉜다. 보정·개미·정지·여러 인원을 뜻하는 작은 모형 표식이 칸마다 붙는다.|카메라는 같은 위치에서 S15의 결과 표시를 받는다.|서로 일정하게 떨어진 L3 카드 4장. 각 카드 위 작은 보정 원·개미·일시정지·3명 표식을 배치한다.
S15|실패 결과가 찍힘|S14 카메라 고정. 결과가 찍힐 때만 아주 작은 깊이 방향 진동을 준다.|빨간 FAIL 프레임이 위에서 내려와 카드 바로 위에 얇은 입체 도장처럼 붙는다. 카드마다 순차적으로 처리한다.|카드 틈이 더 잘게 벌어지면서 S16 3×3이 된다.|무광 영상 카드 4장 위에 두께가 얕은 붉은 FAIL 윤곽과 글자. 고무도장 잉크 질감은 쓰지 않는다.
S16|시험이 아홉 칸으로 늘어남|판 수가 늘어날 때 카메라를 조금 후퇴해 전체 크기를 유지한다.|카드가 3×3으로 나뉘고 앞선 실패가 차례로 표시된다. 한 도장은 아직 내려오는 중, 나머지 두 칸은 결과 전 상태다.|한 번 더 분할되어 S17 4×4가 된다.|9개 카드 중 6개 결과 완료, 1개 도장 진행, 2개는 미완료. 도장과 판 사이의 높이 차이를 읽게 한다.
S17|열여섯 칸 중 하나가 남음|S16보다 약간 후퇴한 같은 축의 카메라. 마지막 남은 칸이 오른쪽 위로 치우치지 않게 중심을 유지한다.|4×4의 판 중 15개에 실패 표시가 들어간다. 두 번째 줄 세 번째 칸만 평평하고 밝게 남는다.|그 한 칸에 S18 초록 결과가 들어오고 주변 조명이 낮아진다.|16개 L3 카드. 15개 작은 붉은 FAIL, 2행 3열 하나만 결과 없이 남긴다.
S18|하나의 개선 결과|카메라가 2행 3열의 초록 칸 쪽으로 움직이기 시작한다. 초록 칸을 프레임 중심으로 데려온다.|남은 칸 테두리가 초록으로 바뀌고 얕은 SUCCESS 프레임이 붙는다. 나머지 카드는 채도와 밝기가 낮아진다.|초록 칸의 깊이 이동을 이어 받아 S19에서 그 칸이 화면 앞으로 나온다.|15개 실패 카드와 초록 L4 카드 1개. 성공은 자체 시험의 개선을 뜻하며 실물 성공 장면은 아직 자리표시자다.
S19|성공 기록 안으로 들어감|카메라가 L4 판을 향해 직선으로 돌리 인. 주변 판은 카메라를 지나 옆과 뒤로 빠진다.|초록 프레임의 실제 시험 기록이 앞으로 나온다. 얇은 판 두께가 보이다가 촬영본이 화면을 채운다.|촬영본 속 사람의 위치를 두 센서의 관측 점으로 교체해 S20으로 연결한다.|초록 L4 영상 판이 전경을 채운다. 실패 카드가 화면 가장자리와 뒤쪽으로 멀어진다.
S20|같은 사람이 두 좌표로 보임|낮은 사선의 보정 스테이지에 가까이 들어간다. 관측 점이 겹쳐 가려지지 않는 위치를 택한다.|흰 관측 점 묶음과 파란 관측 점 묶음이 같은 사람을 서로 다른 자리와 방향에서 나타낸다. 두 좌표축과 짧은 오차 막대가 드러난다.|S21에서 파란 묶음과 좌표축이 함께 회전·이동하며 하나로 포개진다.|한 사람 형태의 관측 점 2묶음, 두 개의 좌표축, 사이의 짧은 붉은 오차 막대. 점은 설명용 관절 표식이며 사실적인 점구름은 쓰지 않는다.
S21|두 관측 좌표를 맞춤|S20 카메라를 고정해 전후 차이를 직접 비교한다.|파란 좌표축이 회전하고 관측 점이 흰 점과 겹친다. 오차 막대가 줄어들며 작은 초록 확인 표시가 나타난다.|관측 점들이 실제 흰 인체 모형으로 돌아오고 넓은 방 S22가 드러난다.|흰 점과 파란 점이 같은 인체 형태로 포개진 상태, 같은 방향의 좌표축, 작은 초록 체크. 실측 오차 0이라는 수치는 쓰지 않는다.
S22|방 안의 유지 영역|보정 스테이지에서 빠져나와 방 전체를 높은 사선으로 본다.|방 안쪽에 초록 경계가 바닥 표면을 따라 그려진다. 두 흰 사람이 그 안을 이동한다.|그중 한 사람이 다른 사람 뒤로 들어가는 동작을 이어 S23으로 연결한다.|같은 전시장 모형, 바닥 안쪽 초록 사각 경계, 사람 2명. 초록 영역은 설명용이며 새 실측 경계를 확정하지 않는다.
S23|가려져도 마지막 자리를 유지|카메라는 앞사람과 마지막 자리가 한 시선에 겹치지 않도록 사선으로 본다. 센서의 가림은 장면 안 광선으로 설명한다.|한 사람이 앞사람 뒤로 들어가 관측에서 사라진다. 마지막 위치에 반투명 초록 인체와 링을 남기고 바닥의 진행 호·일시정지 표시를 멈춘다.|멈춘 호를 길게 펼쳐 S24 경우의 수 타임라인으로 연결한다.|흰 앞사람, 가림 방향의 어두운 바닥 쐐기, 뒷자리의 반투명 초록 사람·정지 링. 가려진 동안 유지 타이머가 흐르지 않는 상태.
S24|경우의 수가 공간으로 갈라짐|흑연색 스테이지 위를 높은 사선으로 본다. 가지를 따라 짧게 전진한 뒤 전체가 보이게 멈춘다.|한 줄이 부드럽게 분기하여 48개의 평행한 얇은 물리적 경로로 펼쳐진다. 끝의 작은 관측 사례 표식으로 여러 판단을 보여준다.|가운데 한 줄을 S25의 초록 클램프가 잡고 다른 가지가 되감긴다.|책상 위 회색·붉은 가는 경로 48개. 1/3 정도를 붉게 강조한다. 번개·뿌리·우주 터널이 아닌 판단 과정의 입체 도식이다.
S25|시험 조건을 두 명으로 정리|S24와 같은 시선을 유지하다 남은 한 줄을 따라 짧게 전진한다.|초록 클램프가 가운데 경로를 잡는다. 다른 경로는 낮고 짧게 남다가 사라진다. 남은 길 위에 두 흰 사람 모형이 움직인다.|남은 경로가 S26 전체 구조도의 연결선으로 이어진다.|초록 클램프, 남은 물리적 한 줄, 사람 2명. 두 명은 개발 시험 설정이며 전시 운영 인원 확정으로 표현하지 않는다.
S26|장비 모형들이 구조를 이룸|넓은 설명 스테이지를 비스듬히 내려다본다. 입력부터 출력으로 천천히 시선을 옮긴다.|키넥트 2대와 메인 PC·송출 노트북이 먼저 놓인다. 합치기 공간은 메인 PC 영역 안에 드러난다. 이미지 판·프로젝터·방 모형이 자리에 들어온다.|마지막 장비가 놓이면 S27에서 카메라와 모형 모두 정지한다.|왼쪽 입력·메인 PC 합치기는 조립 완료, 오른쪽 이미지 판과 프로젝터는 공중에서 이동 중. 조립 방향을 읽는 얇은 꼬리만 사용한다.
S27|전체 흐름을 한 번에 읽음|S26의 와이드 시점에서 완성 상태를 1초 이상 유지한다. 마지막에 방 모형을 향해 아주 조금 접근한다.|B→송출 노트북→메인 PC와 A→메인 PC 경로가 들어오고 메인 PC 안에서 합친다. 이미지 판→P1~P4→4면 방으로 한 번 신호가 흐른다.|방 표면의 연두 점이 S28의 마무리 입자로 이어진다.|키넥트 A·B, 메인 PC·노트북, LAN, 메인 PC 내부 합치기 모형, T자 이미지 판, 프로젝터 4대, 4면 방 모형. 노트북에 보정 기능을 두지 않는다.
S28|모형의 선이 작은 점으로 남음|완성 구조도에서 시선을 조금 올린다. 점들이 올라가도 카메라가 따라 날아가지 않고 정지한다.|구조도의 선과 모형 모서리가 작은 흰 점으로 줄어든다. 점 일부가 연두로 바뀌어 낮게 떠오르다 꺼진다.|암전. 본편 첫 장면이라는 설명을 붙이지 않고 개발로그를 마무리한다.|흑연색 스튜디오 위 낮게 떠오르는 작고 선명한 흰·연두 구. 화면 아래는 비워 두고 성운·광무리·우주 배경은 넣지 않는다.'''
custom={}
for row in ROWS.splitlines():
    cols=row.split('|');assert len(cols)==6,row
    sid,title,camera,action,cut,frame=cols;custom[sid]={'title':title,'camera':camera,'action':action,'cut':cut,'frame':frame}

COMMON='''[작업]
LIMEN 발표 보조 개발로그 90초의 v3 콘티를 제작한다. 다큐멘터리에서 장치·공간·원리를 설명하는 절제된 3D 그래픽이다.
동일한 장면 ID 31개와 타임코드를 사용한다. 프로젝트 본편의 러닝타임과 이 개발로그 90초를 구분한다.
산출물은 1920×1080 PNG 대표 프레임 31장, 장면별 카메라·모형 동작·전환 설명, 4열 contact sheet, 수정 가능한 3D 원본이다.

[형태와 재질]
실제로 두께와 깊이가 있는 모형을 만든다. 바닥과 벽은 무광 회색 슬래브, 사람은 도자기 같은 단순한 무표정 모형, 장비는 단순화한 키넥트·PC·노트북·프로젝터다.
모서리에는 작고 일정한 베벨. 과도한 플라스틱 광택·유리 재질·HUD·홀로그램 효과를 쓰지 않는다. 모든 선을 네온 튜브로 만들지 않는다.
색을 넣어야 설명되는 부분만 강조한다: 입력·시야=차분한 청색 / 연결 LAN·오류=주황을 띤 적색 / 유지·개선=연한 초록 / 투사 예시=청록 면과 연두 점·곡선.

[조명과 카메라]
흑연색 무한 스튜디오 바닥에 큰 면광원 1개, 약한 보조광과 뒷윤곽광을 둔다. 부드러운 접지 그림자로 두께·높이·앞뒤가 읽히게 한다.
설명 컷은 약한 원근 또는 정투영을 사용한다. 심도는 깊게 유지한다. 개념을 보여줄 이유가 있을 때만 돌리·상승·하강한다.
방향을 잃는 지속 회전, 과장된 광각, 흔들림, 과도한 모션블러, 빠른 줌, 렌즈 플레어, 안개·성운·파티클 폭발을 넣지 않는다.
대표 프레임은 카메라 동선 중 원리가 가장 잘 읽히는 순간이다. 실제 제작에서는 한 컷에 한 개의 원리만 변화시킨다.

[같은 공간을 재사용]
모든 방 컷은 같은 7.2×4 바닥, 정면·좌·우 벽과 열린 입구를 사용한다. 네 면은 같은 순간의 한 공간이다.
높이는 미확정이다. 대표 모형의 벽 높이·장비 크기·센서 설치 높이는 설명용 조형 비율이며 현장 실측값으로 쓰지 않는다.
카메라 가까운 벽은 투시·컷어웨이 처리할 수 있다. 실제로 벽이 없다고 해석하지 않게 윤곽을 남긴다.
시야는 수평 70°를 참고한 개념 면이다. 바닥 시야 면적 계산값 40.5%·73.4%는 v3 주 화면에서 생략한다. 설치축이 미확인인 도식으로 그 수치를 검증했다고 말하지 않는다.
센서 몸체의 실제 보는 방향, 시야가 나오는 방향, 가림을 만드는 앞사람의 위치를 일관되게 맞춘다.

[실물·합성]
L1~L7 촬영본은 실제 영상이 들어갈 무광 슬레이트 판으로 남긴다. 판 안에 대각선 2개와 작은 L 번호만 넣는다.
랜선 곡선·오류 링·모형 윤곽은 촬영본을 넣은 뒤 실제 장비·유령 위치·전시장 모서리에 정합한다.
실제 오류나 성공 현장을 새로 꾸며 만든 촬영본으로 대체하지 않는다. 완성 영상은 CG 설명→실물 근거→CG 설명의 리듬으로 편집한다.

[기술 사실과 상태]
키넥트 2대·PC 2대·프로젝터 4대. 메인 PC가 A를 연결하고 B의 UDP 입력을 받아 보정·합치기·Unity·Spout→MadMapper를 처리한다. 송출 노트북은 B 입력을 전달한다.
세이프존에서 가려진 동안 유지 타이머는 정지한 모습이다. 관측이 끊겼다는 이유로 실제 사람이 이동했다고 그리지 않는다.
S18의 개선·S25의 최대 2명은 개발 시험 맥락이다. 전시 운영 인원이나 최종 다인 추적·4면 정합 완료를 확정하지 않는다.
공식 장면명과 기준 상태는 LIMEN_현재기준.md를 따른다. 인체 모형·스켈레톤은 센서 설명용이며 F05 스켈레톤 복제 채택을 뜻하지 않는다.

[글자]
장면 안에는 A/B·P1~P4·L1~L7·LAN·L/R·날짜·FAIL/SUCCESS처럼 필요한 표식만 넣는다. 제목·설명·대본은 콘티 페이지에 둔다.
'''

for s in D:
    s.update(custom[s['id']]);s['motion']=s['action'];s['prompt']='[장면 '+s['id']+' / '+s['title']+' / '+s['t']+'부터 '+str(s['d'])+'초]\n[대표 프레임]\n'+s['frame']+'\n[카메라]\n'+s['camera']+'\n[동작]\n'+s['action']+'\n[다음 컷]\n'+s['cut']
    s.pop('aid',None)
    if s['id'] in ['S07','S09']:s['production_note']='v2에 있던 면적 비율은 주 화면에서 생략했습니다. 실제 시야·가림·인식 성공률을 구분합니다.'
    if s['id']=='S06L':s['production_note']='L5 촬영본 삽입 후 카메라 시선과 모서리 기준점을 실제 네 면에 맞춰 조정합니다.'
    if s['id']=='S23':s['production_note']='가림 동안 마지막 위치를 유지하는 원리의 시각화입니다. 가려진 동안 유지 타이머가 멈춘 상태로 제작합니다.'
    s['version']='v3 / 다큐멘터리 설명용 3D'
    assert (P/(s['id']+'.png')).exists(),s['id']+' render missing'
    with Image.open(P/(s['id']+'.png')) as im:assert im.size==(1920,1080)
assert len(D)==31 and sum(s['d'] for s in D)==90
(P/'scenes.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf-8')
(P/'공통_3D제작프롬프트.txt').write_text(COMMON,encoding='utf-8')

# Overview and review sheets are outside the rendered scene.
font='C:/Windows/Fonts/malgun.ttf';f=ImageFont.truetype(font,18);fh=ImageFont.truetype(font,29)
cw,ch,pad,head=480,322,24,108
sheet=Image.new('RGB',(cw*4+pad*2,head+ch*8+pad),'#12181F');dr=ImageDraw.Draw(sheet)
dr.text((pad,18),'LIMEN 개발로그 · 콘티 v3',font=fh,fill='#E8E7DF');dr.text((pad,62),'다큐멘터리 설명용 3D / 31장면 / 90초 / Blender 렌더 1920×1080',font=f,fill='#A7B6C2')
for i,s in enumerate(D):
    x=pad+i%4*cw;y=head+i//4*ch
    with Image.open(P/(s['id']+'.png')) as im:sheet.paste(im.convert('RGB').resize((480,270),Image.Resampling.LANCZOS),(x,y))
    dr.text((x+10,y+280),s['id']+'  '+s['t']+'  '+s['title'],font=f,fill='#E8E7DF')
sheet.save(P/'contact_sheet.png')
q=P/'검수';q.mkdir(exist_ok=True)
for batch in range(4):
    sh=Image.new('RGB',(1600,1960),'#12181F');dd=ImageDraw.Draw(sh)
    for i,s in enumerate(D[batch*8:(batch+1)*8]):
        x=i%2*800;y=i//2*490
        with Image.open(P/(s['id']+'.png')) as im:sh.paste(im.convert('RGB').resize((800,450),Image.Resampling.LANCZOS),(x,y))
        dd.text((x+12,y+455),s['id']+'  '+s['title'],font=ImageFont.truetype(font,22),fill='#E8E7DF')
    sh.save(q/f'preview_{batch+1}.png')

NOTES='''LIMEN 개발로그 콘티 v3 / 2026-10-29

요청 방향: 다큐멘터리에서 기술·장치·공간의 원리를 설명하는 3D 그래픽.
제작: Blender 5.1.1 / Cycles / OptiX / 32 samples / denoise / 1920×1080 PNG.
31개 대표 프레임과 90초 타임코드를 구성했다. 카메라 동선과 모형 동작은 콘티의 제작 지시이며, 현재 .blend는 대표 상태를 만든 정지 장면 원본이다.
씬을 바꾸려면 Blender 상단 Scene 목록에서 S01~S28 및 S06L·S09L·S12L을 선택한다.

v2에서 v3로 바뀐 것
• 벡터 윤곽·평면 아이콘 → 두께 있는 건축·장비 모형, 단순화한 인체, 부드러운 그림자.
• 고정 평면도 → 필요에 따른 탑뷰·3/4·센서 높이·옆 단면 카메라.
• 점선 포물선 → 공간 안의 케이블 곡선. 연결·오류 맥락은 콘티에서 구분한다.
• 점·선 분기 → 책상 위에 놓인 얕은 3D 경로, 한 줄을 잡는 입체 클램프.
• 분할 화면 → 서로 다른 높이·깊이에 놓인 실제 영상 카드.

자료와 상태
프로젝트 사실은 LIMEN_현재기준.md를 따랐고, 개발 설명의 흐름은 키비주얼 프롬프트 v2와 v2 콘티를 바탕으로 했다.
이 v3는 사용자가 요청한 개발로그 표현 방향이다. 작품 본편의 장면·인터랙션 기획 변경이 아니다.
본편 인터랙션은 개미·F01 반딧불이·F05 사람·군중이며, 센서 설명용 인체·뼈대가 F05 스켈레톤 복제 채택을 뜻하지 않는다.
90초는 이 개발로그의 길이이며 본편 러닝타임은 미정이다.
최종 4면 정합·다인 추적·현장 개선 효과를 새로 검증하지 않았다. S18·S25는 자체 시험·개발 설정의 설명이다.

도식의 크기
바닥 7.2×4 비율은 유지했다. 벽 높이 2.6, 장비 크기·센서 높이·인체 비례는 코드 안의 설명용 모델링 값이며 실제 장비·현장 치수의 확정값이 아니다. 화면에는 높이 수치를 표기하지 않았다.
카메라 쪽 벽을 투명하게 해 내부를 보였고 윤곽을 남겼다. 실제 전시의 벽을 뺐다는 뜻이 아니다.
키넥트 시야는 개념 면이다. v2의 20° 기준축·센서 오프셋이 불명확하므로 v3에서는 읽기 쉬운 사선 배치를 사용했고 40.5%/73.4%를 주 화면에 넣지 않았다. 실측 인식률로 해석하지 않는다.

실물 영상
L1~L7은 촬영본 자리표시자다. 파일에 실제 촬영본·내레이션·완성 모션은 넣지 않았다.
S06L·S09L·S12L의 윤곽·케이블·링은 촬영본을 넣고 위치를 맞춰야 한다.
대본은 v2의 AI 편집 초안을 가져온 것으로 팀 확정 대본이 아니다.
'''
(P/'제작메모.txt').write_text(NOTES,encoding='utf-8')

CSS='''*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:22px}body{margin:0;background:#10161d;color:#ebe9e1;font:15px/1.7 'Malgun Gothic',sans-serif}a{color:inherit;text-underline-offset:4px}button{cursor:pointer;background:#202b36;border:1px solid #425565;color:#ebe9e1;border-radius:5px;padding:8px 14px;font:inherit}button:hover{border-color:#80d5a0}button:focus-visible,a:focus-visible,input:focus-visible{outline:2px solid #80d5a0;outline-offset:4px}main{max-width:1340px;padding:40px 26px 100px;margin:auto}h1{font-size:32px;margin:4px 0 10px;line-height:1.4;letter-spacing:-.6px}h2{font-size:22px;margin:56px 0 16px}h3{font-size:19px;margin:5px 0 17px}p{margin:7px 0}.eyebrow{color:#80d5a0;font:12px Consolas,monospace;letter-spacing:.16em}.sub{color:#a7b6c2}.intro{max-width:850px}.links,.tools{display:flex;align-items:center;gap:18px;flex-wrap:wrap}.links{margin:20px 0;font-size:13px}.summary{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:26px 0}.summary>div{border:1px solid #34424f;border-radius:8px;padding:15px 18px;background:#17212b}.summary b{display:block;font-size:15px;margin-bottom:6px}.summary p{font-size:13px;color:#a7b6c2}.viewer{overflow:hidden;border:1px solid #34424f;border-radius:9px;background:#1a2028}.viewer img{width:100%;aspect-ratio:16/9;display:block}.controls{padding:15px 20px;background:#17212b}.controls input{width:100%;margin:16px 0 5px;accent-color:#80d5a0}.mono{font:13px Consolas,monospace;color:#a7b6c2}#current{font-weight:600;font-size:18px}.note{font-size:13px;color:#a7b6c2;background:#17212b;border-left:2px solid #80d5a0;padding:12px 18px;margin:24px 0}.nav{display:flex;flex-wrap:wrap;gap:6px;margin:24px 0}.nav a{font:12px Consolas,monospace;text-decoration:none;border:1px solid #34424f;border-radius:4px;padding:5px 9px}.chap{margin:50px 0 15px;padding:0 0 12px;border-bottom:1px solid #34424f}.card{border:1px solid #34424f;border-radius:9px;overflow:hidden;margin:18px 0 30px;background:#17212b;scroll-margin-top:20px}.row{display:grid;grid-template-columns:1.65fr 1fr}.visual img{width:100%;display:block;aspect-ratio:16/9}.visual{align-self:start;background:#1a2028}.desc{padding:20px}.k{font-size:11px;color:#80d5a0;margin:15px 0 4px;letter-spacing:.08em}.desc p{color:#c6cfd5;font-size:14px}.script{border-top:1px solid #34424f;padding:14px 20px;display:grid;grid-template-columns:110px 1fr;gap:16px}.script p{font-size:16px}.small{font-size:12px;color:#a7b6c2}details{border-top:1px solid #34424f;padding:14px 20px}summary{cursor:pointer;font-size:13px;color:#a7b6c2}pre{white-space:pre-wrap;word-break:break-word;color:#c6cfd5;font:13px/1.85 'Malgun Gothic',sans-serif}details button{float:right;padding:3px 12px;font-size:12px}.fullprompt{background:#17212b;border:1px solid #34424f;border-radius:8px}.production{border-top:1px dashed #34424f;padding-top:10px;font-size:12px!important;color:#a7b6c2!important}.tag{font-size:11px;color:#80d5a0;margin-left:8px}@media(max-width:900px){.row{grid-template-columns:1fr}.summary{grid-template-columns:1fr}.script{grid-template-columns:1fr;gap:2px}h1{font-size:26px}main{padding:24px 14px 70px}.summary{gap:8px}.summary>div{padding:10px 14px}}'''

def header(title):return '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+'</title><style>'+CSS+'</style></head><body><main>'
def esc(s):return html.escape(s,quote=True)
def make_doc(base='',prompt_only=False):
    doc=header('LIMEN 개발로그 '+('3D 제작 프롬프트 v3' if prompt_only else '콘티 v3'))
    doc+='''<p class="eyebrow">LIMEN / DEVELOPMENT DOCUMENTARY / V3</p><h1>공간과 장치의 원리를 보여주는 3D 콘티</h1><p class="intro sub">무광 전시장 모형, 단순화한 사람, 반투명 시야와 접지 그림자로 기술의 작동 원리를 설명합니다. 기존 31장면·90초 흐름을 다큐멘터리의 설명용 3D 그래픽으로 옮겼습니다.</p>'''
    doc+='<div class="links"><a href="'+base+'contact_sheet.png">31장면 확인용 시트</a><a href="'+base+'LIMEN_개발로그_콘티_v3.blend">Blender 원본</a><a href="'+base+'제작메모.txt">제작 메모</a><a href="'+base+'공통_3D제작프롬프트.txt">공통 제작 프롬프트</a></div>'
    doc+='''<div class="summary"><div><b>공간은 같은 모형으로</b><p>높은 사선·센서 높이·옆 단면을 오가며, 보고 있는 위치와 가려지는 이유를 보여줍니다.</p></div><div><b>빛과 그림자로 깊이를</b><p>무광 회색·작은 베벨·부드러운 그림자. 파랑은 시야, 붉은색은 오류·연결, 초록은 유지·개선에 씁니다.</p></div><div><b>CG 설명과 실물 근거를 연결</b><p>모형의 윤곽·케이블·오류 링이 실제 촬영본의 같은 위치로 넘어가는 편집입니다.</p></div></div>'''
    if not prompt_only:
        doc+='''<section class="viewer" aria-label="3D 대표 컷 미리보기"><img id="frame" src="__BASE__S11.png" alt="가려짐을 설명하는 3D 모형"><div class="controls"><div class="tools"><button id="prev" aria-label="이전 장면">← 이전</button><button id="play">90초 컷 미리보기</button><button id="next" aria-label="다음 장면">다음 →</button><span class="mono" id="position"></span></div><input id="seek" aria-label="장면 선택" type="range" min="0" max="30" value="12"><p id="current"></p><p id="caption" class="sub"></p><p class="small">실제 Blender 3D 렌더의 대표 상태입니다. 모형·카메라의 움직임은 아래 콘티에 적힌 제작 지시입니다.</p></div></section>'''
    doc+='<div class="note">촬영본은 L1~L7 자리로 남겼습니다. 90초는 개발로그 길이이며 본편 러닝타임은 미정입니다. 성공·두 명 제한은 개발 시험 맥락으로 표시했습니다.</div>'
    doc+='<nav class="nav" aria-label="장면 바로가기">'+''.join('<a href="#'+s['id']+'">'+s['id']+'</a>' for s in D)+'</nav>'
    doc+='<details class="fullprompt"'+(' open' if prompt_only else '')+'><summary>v3 공통 3D 제작 지시</summary><button data-copy="common">복사</button><pre id="common">'+esc(COMMON)+'</pre></details>'
    last=None
    for s in D:
        if s['ch']!=last:doc+='<h2 class="chap">'+esc(s['ch'])+'</h2>';last=s['ch']
        doc+='<article class="card" id="'+s['id']+'"><div class="row"><a class="visual" href="__BASE__'+s['id']+'.png" target="_blank"><img loading="lazy" src="__BASE__'+s['id']+'.png" alt="'+esc(s['title'])+'"></a><div class="desc"><div class="mono">'+s['id']+' · '+s['t']+' · '+str(s['d'])+'초 <span class="tag">'+{'g':'3D 그래픽','l':'실물 연결','c':'3D + 실물 합성'}[s['ty']]+'</span></div><h3>'+esc(s['title'])+'</h3>'
        for k,label in [('camera','CAMERA · 카메라'),('action','ACTION · 모형의 동작'),('cut','CUT · 다음 컷으로')]:doc+='<div class="k">'+label+'</div><p>'+esc(s[k])+'</p>'
        if s.get('production_note'):doc+='<p class="production">'+esc(s['production_note'])+'</p>'
        doc+='</div></div>'
        if not prompt_only:doc+='<div class="script"><span class="small">발표 대본 초안</span><p>'+esc(s.get('narration_draft') or '말 없음 — 화면 전환')+'</p></div>'
        doc+='<details'+(' open' if prompt_only else '')+'><summary>이 장면의 3D 제작 프롬프트</summary><button data-full="'+s['id']+'">공통 포함 복사</button><pre>'+esc(s['prompt'])+'</pre></details></article>'
    doc+='<details><summary>제작 범위·기준·도식의 한계</summary><pre>'+esc(NOTES)+'</pre></details>'
    doc+='</main><script id="data" type="application/json">'+json.dumps(D,ensure_ascii=False).replace('</','<\\/')+'</script><script>const D=JSON.parse(document.getElementById("data").textContent);'
    doc+='''document.addEventListener('click',async e=>{const b=e.target.closest('button[data-copy],button[data-full]');if(!b)return;const value=b.dataset.copy?document.getElementById('common').textContent:document.getElementById('common').textContent+'\\n\\n'+D.find(s=>s.id===b.dataset.full).prompt;try{await navigator.clipboard.writeText(value);const old=b.textContent;b.textContent='복사됨';setTimeout(()=>b.textContent=old,1400);}catch{const pre=b.parentElement.querySelector('pre'),range=document.createRange();range.selectNodeContents(pre);const sel=window.getSelection();sel.removeAllRanges();sel.addRange(range);b.textContent='선택됨 · Ctrl+C';}});'''
    if not prompt_only:
        doc+='''const base='__BASE__',frame=document.getElementById('frame'),seek=document.getElementById('seek'),play=document.getElementById('play');let ix=D.findIndex(s=>s.id==='S11'),timer=null,playing=false;function stop(){clearTimeout(timer);playing=false;play.textContent='90초 컷 미리보기';}function show(i){ix=Math.max(0,Math.min(D.length-1,i));const s=D[ix];frame.src=base+s.id+'.png';frame.alt=s.title;seek.value=ix;document.getElementById('position').textContent=s.t+' · '+s.d+'초 · '+(ix+1)+'/31';document.getElementById('current').textContent=s.id+' — '+s.title;document.getElementById('caption').textContent=s.narration_draft||'말 없음 — 화면 전환';}function run(){playing=true;play.textContent='일시정지';timer=setTimeout(()=>{if(ix===D.length-1){stop();return;}show(ix+1);run();},D[ix].d*1000);}play.onclick=()=>{if(playing){stop();return;}show(0);run();};document.getElementById('prev').onclick=()=>{stop();show(ix-1);};document.getElementById('next').onclick=()=>{stop();show(ix+1);};seek.oninput=()=>{stop();show(+seek.value);};document.addEventListener('keydown',e=>{if(['INPUT','BUTTON','A','SUMMARY'].includes(document.activeElement.tagName))return;if(e.key==='ArrowLeft'||e.key==='ArrowRight'){e.preventDefault();stop();show(ix+(e.key==='ArrowRight'?1:-1));}});show(ix);'''
    return (doc+'</script></body></html>').replace('__BASE__',base)

(P/'index.html').write_text(make_doc(),encoding='utf-8')
(P.parent/'개발로그영상_콘티_v3.html').write_text(make_doc('키비주얼_v3/'),encoding='utf-8')
(P.parent/'개발로그영상_키비주얼_프롬프트_v3.html').write_text(make_doc('키비주얼_v3/',True),encoding='utf-8')
(q/'검수결과.json').write_text(json.dumps({'frames':31,'size':[1920,1080],'duration_seconds':90,'renderer':'Blender 5.1.1 / Cycles / OptiX','assets':'procedural 3D geometry','motion_status':'static representative states / camera and object motion specified in storyboard','live_footage':'L1-L7 placeholders','editable_source':(P/'LIMEN_개발로그_콘티_v3.blend').exists()},ensure_ascii=False,indent=2),encoding='utf-8')
zip_path=P.parent/'개발로그_콘티_v3_3D_31장.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for file in sorted(P.iterdir()):
        if file.is_file() and file.suffix not in ['.log','.blend1'] and file.name not in {'repair_framing.py','finish_scene.py'}:z.write(file,'키비주얼_v3/'+file.name)
    for name in ['개발로그영상_콘티_v3.html','개발로그영상_키비주얼_프롬프트_v3.html']:z.write(P.parent/name,name)
    for report in sorted(q.glob('*.json')):z.write(report,'키비주얼_v3/검수/'+report.name)
print('V3 package: 31 rendered frames, 90 seconds, storyboard, production prompts, editable Blender file, ZIP.')
