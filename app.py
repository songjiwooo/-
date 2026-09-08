import streamlit as st
from PIL import Image
import random
from io import BytesIO
from pathlib import Path

st.set_page_config(
    page_title="남친/여친 만들기 💘",
    page_icon="💘",
    layout="centered",
    initial_sidebar_state="collapsed",
)

SPRITE_PATH = Path("character_assets/sprite.png.PNG")
W, H = 1536, 1024

# ------------------------------------------------------------------
# 이 스프라이트 시트는 1536x1024 기준.
# 각 박스는 (left, top, right, bottom)이며, 필요하면 여기만 수정하면 됨.
# ------------------------------------------------------------------

# 얼굴: 귀엽고 평범한 얼굴 + 일부러 웃긴/이상한 얼굴까지 섞음
FACE_BOXES = [
    (275, 8, 370, 118), (365, 8, 455, 118), (450, 8, 540, 118),
    (535, 8, 625, 118), (620, 8, 710, 118), (705, 8, 795, 118),
    (790, 8, 880, 118), (875, 8, 1180, 118),  # 마지막은 아래에서 안전하게 다시 처리
]
# 정확히 분리하기 어려운 오른쪽의 코믹 얼굴들은 별도 박스
FUNNY_FACE_BOXES = [
    (1175, 5, 1270, 115), (1260, 5, 1360, 115), (1350, 5, 1450, 115),
    (1270, 105, 1360, 205), (1360, 105, 1455, 205),
    (1270, 175, 1360, 275), (1360, 175, 1455, 275),
]

# 헤어스타일
HAIR_BOXES = [
    (0, 285, 125, 430), (105, 285, 225, 430), (205, 285, 325, 430),
    (300, 285, 425, 430), (400, 285, 525, 430), (500, 285, 625, 430),
    (600, 285, 725, 430), (700, 285, 825, 430), (800, 285, 430+425, 430),
    (900, 285, 1025, 430), (1000, 285, 1125, 430), (1100, 285, 1225, 430),
    (0, 420, 125, 570), (105, 420, 225, 570), (205, 420, 325, 570),
    (300, 420, 425, 570), (400, 420, 525, 570), (500, 420, 625, 570),
    (600, 420, 725, 570), (700, 420, 825, 570), (800, 420, 925, 570),
    (900, 420, 1025, 570), (1000, 420, 1125, 570), (1100, 420, 1225, 570),
    (0, 535, 125, 660), (105, 535, 225, 660), (205, 535, 325, 660),
    (300, 535, 425, 660), (400, 535, 525, 660), (500, 535, 625, 660),
    (600, 535, 725, 660),
]

# 상의
TOP_BOXES = [
    (0, 620, 105, 755), (95, 620, 205, 755), (190, 620, 305, 755),
    (290, 620, 405, 755), (390, 620, 505, 755), (490, 620, 605, 755),
    (585, 620, 700, 755), (680, 620, 795, 755),
    (0, 735, 105, 875), (95, 735, 205, 875), (190, 735, 305, 875),
    (290, 735, 405, 875), (390, 735, 505, 875), (490, 735, 605, 875),
    (585, 735, 700, 875), (680, 735, 795, 875),
]

# 하의
BOTTOM_BOXES = [
    (785, 620, 875, 755), (875, 620, 965, 755), (965, 620, 1055, 755),
    (1050, 620, 1140, 755), (1140, 620, 1230, 755),
    (785, 735, 875, 885), (875, 735, 965, 885), (965, 735, 1055, 885),
    (1050, 735, 1140, 885), (1140, 735, 1230, 885),
]

# 신발
SHOE_BOXES = [
    (0, 905, 100, 1023), (95, 905, 195, 1023), (190, 905, 290, 1023),
    (285, 905, 385, 1023), (380, 905, 480, 1023), (475, 905, 575, 1023),
    (570, 905, 670, 1023), (665, 905, 765, 1023), (760, 905, 860, 1023),
    (855, 905, 955, 1023), (950, 905, 1050, 1023), (1045, 905, 1145, 1023),
]

# 얼굴 아래쪽에 있는 눈/입/귀는 "표정 추가 파츠"로 사용.
# 기본 얼굴 자체가 이미 눈/입을 포함하므로, 앱에서는 별도 파츠를 억지로
# 겹치지 않고 얼굴 랜덤 + 헤어 + 옷 조합으로 안정적으로 동작시킴.

FEMALE_NAMES = ["김하은", "최유진", "박서연", "이채원", "정다은", "한유나", "윤서아", "강민지"]
MALE_NAMES = ["김민준", "이도윤", "박지호", "최현우", "정우진", "한지호", "윤도현", "강민재"]

DESCRIPTIONS = [
    "첫인상은 무난한데 자꾸 생각나는 타입",
    "패션은 조금 독특하지만 은근 매력 있음",
    "친구들이 왜 좋아하냐고 물어보는데 본인은 좋음",
    "처음엔 차가워 보이지만 알고 보면 다정함",
    "학교에서 한 번쯤 본 것 같은 친근한 느낌",
    "사진보다 실물이 더 괜찮을 것 같은 타입",
    "오늘은 스타일이 살짝 망했지만 내일은 괜찮을 예정",
    "얼굴과 옷의 조합이 묘하게 웃기지만 이상하게 귀여움",
    "꾸미는 날과 안 꾸미는 날의 차이가 큰 타입",
    "본인만의 취향이 확실해서 호불호가 갈릴 스타일",
]

def load_sprite():
    if not SPRITE_PATH.exists():
        st.error(f"이미지 파일을 찾을 수 없습니다: {SPRITE_PATH}")
        st.info("GitHub에서 character_assets 폴더 안에 sprite.png.PNG 파일이 있는지 확인하세요.")
        st.stop()
    try:
        img = Image.open(SPRITE_PATH).convert("RGBA")
        return img
    except Exception as e:
        st.error("스프라이트 이미지를 읽을 수 없습니다.")
        st.exception(e)
        st.stop()

@st.cache_data
def get_sprite_bytes():
    img = load_sprite()
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def crop(img, box):
    l, t, r, b = box
    l = max(0, min(img.width, l))
    r = max(0, min(img.width, r))
    t = max(0, min(img.height, t))
    b = max(0, min(img.height, b))
    if r <= l or b <= t:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    part = img.crop((l, t, r, b))
    # 완전 투명 여백 제거
    bbox = part.getbbox()
    if bbox:
        part = part.crop(bbox)
    return part

def fit(part, max_w, max_h):
    if part.width <= 1 or part.height <= 1:
        return part
    scale = min(max_w / part.width, max_h / part.height)
    size = (max(1, int(part.width * scale)), max(1, int(part.height * scale)))
    return part.resize(size, Image.Resampling.LANCZOS)

def paste_center(canvas, part, cx, cy):
    x = int(cx - part.width / 2)
    y = int(cy - part.height / 2)
    canvas.alpha_composite(part, (x, y))

def make_character(sprite, gender):
    # 640x760 작업 캔버스
    canvas = Image.new("RGBA", (640, 760), (255, 255, 255, 0))

    # 기본 몸통. 시트 왼쪽 위의 두 인체를 이용.
    body_box = (0, 0, 155, 285) if gender == "여친" else (150, 0, 300, 285)
    body = crop(sprite, body_box)
    body = fit(body, 330, 560)
    paste_center(canvas, body, 320, 455)

    # 얼굴: 약 25% 확률로 일부러 코믹한 얼굴을 넣음
    if random.random() < 0.25:
        face_box = random.choice(FUNNY_FACE_BOXES)
    else:
        face_box = random.choice(FACE_BOXES[:7])

    face = fit(crop(sprite, face_box), 245, 180)
    paste_center(canvas, face, 320, 175)

    # 헤어
    hair = fit(crop(sprite, random.choice(HAIR_BOXES)), 315, 235)
    paste_center(canvas, hair, 320, 120)

    # 상의
    top = fit(crop(sprite, random.choice(TOP_BOXES)), 300, 210)
    paste_center(canvas, top, 320, 365)

    # 하의
    bottom = fit(crop(sprite, random.choice(BOTTOM_BOXES)), 290, 240)
    paste_center(canvas, bottom, 320, 510)

    # 신발
    shoes = fit(crop(sprite, random.choice(SHOE_BOXES)), 260, 125)
    paste_center(canvas, shoes, 320, 675)

    # 최종 투명 여백 정리
    bbox = canvas.getbbox()
    if bbox:
        canvas = canvas.crop(bbox)

    # 보기 좋은 크기로 통일
    canvas.thumbnail((520, 650), Image.Resampling.LANCZOS)
    return canvas

def reroll(gender):
    sprite = load_sprite()
    st.session_state.character = make_character(sprite, gender)
    names = FEMALE_NAMES if gender == "여친" else MALE_NAMES
    st.session_state.name = random.choice(names)
    st.session_state.description = random.choice(DESCRIPTIONS)
    st.session_state.like = random.randint(45, 99)

# CSS
st.markdown("""
<style>
.main .block-container {
    max-width: 760px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}
.title {
    text-align:center;
    font-size: 2.4rem;
    font-weight: 900;
    margin-bottom: .2rem;
}
.subtitle {
    text-align:center;
    color:#777;
    margin-bottom:1.2rem;
}
.card {
    padding: 1.2rem;
    border-radius: 28px;
    background: linear-gradient(145deg,#fff7fc,#f5f3ff);
    box-shadow: 0 8px 28px rgba(80,50,100,.12);
    text-align:center;
}
.name {
    font-size:1.8rem;
    font-weight:900;
}
.like {
    font-size:1.25rem;
    font-weight:800;
}
.small {
    color:#777;
    font-size:.95rem;
}
</style>
""", unsafe_allow_html=True)

# Session state
if "gender" not in st.session_state:
    st.session_state.gender = None
if "character" not in st.session_state:
    st.session_state.character = None
if "dating" not in st.session_state:
    st.session_state.dating = False

# 시작 화면
if st.session_state.gender is None:
    st.markdown('<div class="title">💘 남친 / 여친 만들기</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">랜덤으로 나만의 이상형을 만들어보자!</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("💗 여친 만들기", use_container_width=True):
            st.session_state.gender = "여친"
            reroll("여친")
            st.rerun()
    with c2:
        if st.button("💙 남친 만들기", use_container_width=True):
            st.session_state.gender = "남친"
            reroll("남친")
            st.rerun()

    st.caption("얼굴 + 헤어 + 옷 + 신발이 매번 랜덤으로 바뀝니다. 가끔 패션 테러리스트도 등장합니다.")
    st.stop()

# 결과 화면
gender = st.session_state.gender
st.markdown(f'<div class="title">{"💗" if gender=="여친" else "💙"} {gender} 만들기</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">🎲 버튼을 누를 때마다 새로운 사람이 나타납니다</div>', unsafe_allow_html=True)

if st.session_state.character is not None:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.image(st.session_state.character, use_container_width=True)
    st.markdown(f'<div class="name">{st.session_state.name}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="like">💕 호감도 {st.session_state.like}%</div>', unsafe_allow_html=True)
    st.write(st.session_state.description)
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")
if st.button("🎲 다시 랜덤으로 만들기", use_container_width=True, type="primary"):
    reroll(gender)
    st.session_state.dating = False
    st.rerun()

if st.button("💘 이 사람과 사귀기", use_container_width=True):
    st.session_state.dating = True
    st.rerun()

if st.session_state.dating:
    messages = [
        "축하합니다! 오늘부터 1일입니다 💕",
        "친구들에게 자랑했더니 다들 놀랐습니다. 그래도 커플 성사! 💘",
        "운명은 랜덤 버튼에서 시작되었습니다. 💞",
        "이 조합을 누가 예상했을까요. 아무튼 커플입니다. 🎉",
        "호감도는 숫자일 뿐, 일단 사귀는 데 성공했습니다. 💗",
    ]
    st.success(f"💘 **커플 성사!**\n\n{st.session_state.name}님과 사귀게 되었습니다!\n\n{random.choice(messages)}")

if st.button("↩️ 처음으로 돌아가기", use_container_width=True):
    st.session_state.gender = None
    st.session_state.character = None
    st.session_state.dating = False
    st.rerun()

st.divider()
st.caption("※ 캐릭터 이미지는 저장소의 character_assets/sprite.png.PNG 한 장만 사용합니다.'')
