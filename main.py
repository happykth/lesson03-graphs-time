import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
# 구역 2. 일관객 합계 상위 5편 비교 (선 그래프)
# ═════════════════════════════════════════════
st.header("2. 관객 합계 상위 5편 비교")

# 이 기간 일관객 합계가 가장 큰 5편
top5 = df.groupby("영화명")["일관객"].sum().nlargest(5).index.tolist()
top5_df = df[df["영화명"].isin(top5)].sort_values("날짜")

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    category_orders={"영화명": top5},  # 범례를 합계 순서대로
    title="일관객 합계 상위 5편의 날짜별 일관객",
    color_discrete_sequence=["#E8743B", "#C0392B", "#F4B942", "#8E5A3C", "#D98880"],
)
fig2.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra>%{fullData.name}</extra>"
)
fig2.update_layout(
    xaxis_title="날짜",
    yaxis_title="일관객(명)",
    legend_title_text="영화 (클릭하면 켜고 끌 수 있어요)",
    hovermode="closest",
    plot_bgcolor="white",
)
st.plotly_chart(fig2, use_container_width=True)

insight_box("graph2", default="")

st.divider()

# ═════════════════════════════════════════════
# 구역 3. 날짜별 10위권 일관객 합계 (영역 그래프)
# ═════════════════════════════════════════════
st.header("3. 날짜별 10위권 일관객 합계")

# 날짜별로 그날 10위권 일관객을 모두 더하기
daily = df.groupby("날짜", as_index=False)["일관객"].sum()

# 합계가 가장 컸던 3일 (표시할 때 겹치지 않게 날짜순으로 정렬)
top3_days = daily.nlargest(3, "일관객").sort_values("날짜")

fig3 = px.area(
    daily,
    x="날짜",
    y="일관객",
    title="하루 10위권 일관객 합계",
    color_discrete_sequence=[WARM_ORANGE],
)
fig3.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>10위권 합계: %{y:,}명<extra></extra>"
)

# 가장 컸던 3일을 점과 날짜 글자로 표시 (글자 위치를 달리해 서로 안 겹치게 함)
fig3.add_trace(
    go.Scatter(
        x=top3_days["날짜"],
        y=top3_days["일관객"],
        mode="markers+text",
        text=[f"{d:%Y-%m-%d}" for d in top3_days["날짜"]],
        textposition=["top center", "top left", "top right"],
        marker=dict(size=11, color="#C0392B", line=dict(width=2, color="white")),
        hovertemplate="날짜: %{x|%Y-%m-%d}<br>10위권 합계: %{y:,}명<extra>합계 TOP 3</extra>",
        name="합계 TOP 3",
        showlegend=False,
    )
)
fig3.update_layout(
    xaxis_title="날짜",
    yaxis_title="10위권 일관객 합계(명)",
    yaxis_range=[0, daily["일관객"].max() * 1.15],  # 글자가 잘리지 않게 위쪽 여백
    plot_bgcolor="white",
)
st.plotly_chart(fig3, use_container_width=True)

insight_box("graph3", default="")

st.divider()

# ═════════════════════════════════════════════
# 구역 4. 영화별 일관객 합계 TOP 10 (가로 막대그래프)
# ═════════════════════════════════════════════
st.header("4. 영화별 일관객 합계 TOP 10")

# 영화별로 일관객 합계와, 10위권에 든 날수(= 그 영화가 나온 행의 개수) 구하기
movie_sum = (
    df.groupby("영화명")
    .agg(일관객합계=("일관객", "sum"), 십위권날수=("날짜", "count"))
    .reset_index()
    .nlargest(10, "일관객합계")
)

fig4 = px.bar(
    movie_sum,
    x="일관객합계",
    y="영화명",
    orientation="h",
    custom_data=["십위권날수"],
    title="이 기간 일관객 합계 TOP 10",
    color_discrete_sequence=[WARM_ORANGE],
)
fig4.update_traces(
    hovertemplate=(
        "%{y}<br>일관객 합계: %{x:,}명"
        "<br>10위권에 든 날수: %{customdata[0]}일<extra></extra>"
    )
)
fig4.update_layout(
    xaxis_title="일관객 합계(명)",
    yaxis_title="",
    yaxis=dict(categoryorder="total ascending"),  # 관객이 많은 영화가 위로
    plot_bgcolor="white",
)
st.plotly_chart(fig4, use_container_width=True)

insight_box("graph4", default="")

st.divider()

# ═════════════════════════════════════════════
# 구역 5. 월 × 요일별 일관객 합계 (히트맵)
# ═════════════════════════════════════════════
st.header("5. 월 × 요일별 일관객 합계")

WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]  # 월요일부터 일요일 순서

heat = df.copy()
# 2025-09와 2026-09가 섞이지 않도록 '연-월'로 뽑기
heat["월"] = heat["날짜"].dt.strftime("%Y-%m")
heat["요일"] = heat["날짜"].dt.dayofweek.map(dict(enumerate(WEEKDAYS)))  # 0=월 ... 6=일

pivot = (
    heat.pivot_table(index="월", columns="요일", values="일관객", aggfunc="sum")
    .reindex(columns=WEEKDAYS)  # 열 순서를 월~일로 고정
    .sort_index()  # 행은 시간 순서
)

fig5 = px.imshow(
    pivot,
    aspect="auto",
    color_continuous_scale="Oranges",  # 진할수록 관객이 많음
    title="월 × 요일별 일관객 합계",
)
fig5.update_traces(
    hovertemplate="%{y} %{x}요일<br>일관객 합계: %{z:,}명<extra></extra>"
)
fig5.update_layout(
    xaxis_title="요일",
    yaxis_title="월",
    xaxis=dict(side="top"),
    coloraxis_colorbar=dict(title="일관객(명)"),
    plot_bgcolor="white",
)
st.plotly_chart(fig5, use_container_width=True)

insight_box("graph5", default="")

st.divider()

# ═════════════════════════════════════════════
# 구역 6. (다음 그래프가 들어갈 자리)
# ═════════════════════════════════════════════
# st.header("6. 제목")
# ... 그래프 코드 ...
# insight_box("graph6")
# st.divider()
