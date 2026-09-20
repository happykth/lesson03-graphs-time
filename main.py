import pandas as pd
import plotly.express as px
import streamlit as st

# ─────────────────────────────────────────────
# 기본 설정
# ─────────────────────────────────────────────
st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", page_icon="🎬", layout="wide")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

# 따뜻한 색 팔레트
WARM_ORANGE = "#E8743B"
WARM_BG = "#FFF8F0"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {WARM_BG}; }}
    .insight {{
        background-color: #FFE8D1;
        border-left: 6px solid {WARM_ORANGE};
        padding: 0.8rem 1rem;
        border-radius: 6px;
        margin-top: 0.5rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# 데이터 불러오기 (한 번 불러오면 캐시에 저장)
# ─────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    # 파일 맨 앞에 BOM이 있어서 utf-8-sig로 읽어야 열 이름이 깨지지 않아요
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")
    # 20250901 같은 여덟 자리 숫자를 진짜 날짜로 바꾸기
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")
    return df


df = load_data()


# ─────────────────────────────────────────────
# '이 그래프로 알 수 있는 것' 입력칸 + 표시 상자
# 그래프마다 insight_box("고유이름") 한 줄만 부르면 돼요.
# default에 문장을 적어 두면 앱을 다시 열어도 그 문장이 기본으로 보여요.
# ─────────────────────────────────────────────
def insight_box(key: str, default: str = ""):
    text = st.text_input(
        "✏️ 이 그래프로 알 수 있는 것 (한 문장)",
        value=default,
        key=f"insight_{key}",
        placeholder="여기에 클릭해서 한 문장을 적고 Enter를 눌러 주세요",
    )
    if text.strip():
        st.markdown(
            f"<div class='insight'>💡 <b>이 그래프로 알 수 있는 것</b><br>{text}</div>",
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
# 제목
# ─────────────────────────────────────────────
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption(
    f"{df['날짜'].min():%Y-%m-%d} ~ {df['날짜'].max():%Y-%m-%d} · "
    "일별 박스오피스 10위권 기록"
)

# ═════════════════════════════════════════════
# 구역 1. 영화별 일관객 변화 (선 그래프)
# ═════════════════════════════════════════════
st.header("1. 영화별 일관객 변화")

# 관객이 많았던 영화가 위에 오도록 정렬
movie_order = (
    df.groupby("영화명")["일관객"].sum().sort_values(ascending=False).index.tolist()
)
movie = st.selectbox("영화를 골라 보세요", movie_order, key="graph1_movie")

one = df[df["영화명"] == movie].sort_values("날짜")

fig1 = px.line(
    one,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"{movie} - 날짜별 일관객",
    color_discrete_sequence=[WARM_ORANGE],
)
fig1.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
)
fig1.update_layout(
    xaxis_title="날짜",
    yaxis_title="일관객(명)",
    hovermode="x unified",
    plot_bgcolor="white",
)
st.plotly_chart(fig1, use_container_width=True)

insight_box("graph1", default="")

st.divider()

# ═════════════════════════════════════════════
# 구역 2. (다음 그래프가 들어갈 자리)
# ═════════════════════════════════════════════
# st.header("2. 제목")
# ... 그래프 코드 ...
# insight_box("graph2")
# st.divider()
