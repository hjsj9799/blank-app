#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="Titanic Survival Dashboard",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("default")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

/* 메트릭 카드 스타일 */
[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
    color: white !important;
}

/* 메트릭 라벨 (텍스트 흰색) */
[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
  color: white !important;
}

/* 메트릭 값 (흰색) */
[data-testid="stMetricValue"] {
  color: white !important;
}

/* Delta 값 (Streamlit 기본 색상 유지) */
[data-testid="stMetricDelta"] {
  font-size: 0.9rem;
  font-weight: 600;
}

/* 화살표 아이콘 위치 초기화 → 겹침 방지 */
[data-testid="stMetricDeltaIcon-Up"],
[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 0;
    transform: none;
}

</style>
""", unsafe_allow_html=True)


#######################
# Load data
df_reshaped = pd.read_csv('titanic.csv') ## 분석 데이터 넣기


#######################
# Sidebar
with st.sidebar:
    st.title("🚢 Titanic Survival Dashboard")
    st.markdown("탑승객 데이터를 필터링하여 다양한 생존 패턴을 분석하세요.")

    # Pclass filter
    pclass_filter = st.multiselect(
        "선실 등급 선택 (Pclass)",
        options=df_reshaped['Pclass'].unique(),
        default=df_reshaped['Pclass'].unique()
    )

    # Sex filter
    sex_filter = st.multiselect(
        "성별 선택",
        options=df_reshaped['Sex'].unique(),
        default=df_reshaped['Sex'].unique()
    )

    # Embarked filter
    embarked_filter = st.multiselect(
        "탑승 항구 선택 (Embarked)",
        options=df_reshaped['Embarked'].dropna().unique(),
        default=df_reshaped['Embarked'].dropna().unique()
    )

    # Age range filter
    age_min = int(df_reshaped['Age'].min(skipna=True))
    age_max = int(df_reshaped['Age'].max(skipna=True))
    age_range = st.slider(
        "나이 범위 선택",
        min_value=age_min,
        max_value=age_max,
        value=(age_min, age_max)
    )

    # Theme selection (optional)
    theme = st.selectbox(
        "색상 테마 선택",
        options=["기본", "Blues", "Greens", "Reds", "Viridis"],
        index=0
    )


#######################
# Dashboard Main Panel
col = st.columns((1.5, 4.5, 2), gap='medium')

with col[0]:
    st.subheader("📊 요약 지표")

    df_filtered = df_reshaped[
        (df_reshaped['Pclass'].isin(pclass_filter)) &
        (df_reshaped['Sex'].isin(sex_filter)) &
        (df_reshaped['Embarked'].isin(embarked_filter)) &
        (df_reshaped['Age'].between(age_range[0], age_range[1]))
    ]

    total_passengers = len(df_filtered)
    survived_count = df_filtered['Survived'].sum()
    died_count = total_passengers - survived_count
    survived_rate = (survived_count / total_passengers) * 100 if total_passengers > 0 else 0

    st.metric(label="총 탑승객 수", value=total_passengers)
    st.metric(label="생존자 수", value=survived_count, delta=f"{survived_rate:.1f}%")
    st.metric(label="사망자 수", value=died_count, delta=f"{100-survived_rate:.1f}%")

    st.markdown("---")

    st.markdown("**성별 생존율**")
    sex_survival = (
        df_filtered.groupby("Sex")["Survived"]
        .mean()
        .mul(100)
        .reset_index()
    )
    chart_sex = alt.Chart(sex_survival).mark_bar().encode(
        x=alt.X("Sex:N", title="성별"),
        y=alt.Y("Survived:Q", title="생존율 (%)"),
        color="Sex"
    )
    st.altair_chart(chart_sex, use_container_width=True)

    st.markdown("**등급별 생존율 (Pclass)**")
    pclass_survival = (
        df_filtered.groupby("Pclass")["Survived"]
        .mean()
        .mul(100)
        .reset_index()
    )
    chart_pclass = alt.Chart(pclass_survival).mark_bar().encode(
        x=alt.X("Pclass:O", title="선실 등급"),
        y=alt.Y("Survived:Q", title="생존율 (%)"),
        color="Pclass:N"
    )
    st.altair_chart(chart_pclass, use_container_width=True)


with col[1]:
    st.subheader("📈 메인 시각화")

    st.markdown("**연령 분포와 생존 여부**")
    chart_age = px.histogram(
        df_filtered,
        x="Age",
        color="Survived",
        barmode="overlay",
        nbins=30,
        labels={"Survived": "생존 여부"},
        color_discrete_map={0: "red", 1: "green"}
    )
    st.plotly_chart(chart_age, use_container_width=True)

    st.markdown("---")

    st.markdown("**요금(Fare) vs 나이 (생존 여부 색상)**")
    chart_fare = px.scatter(
        df_filtered,
        x="Age",
        y="Fare",
        color="Survived",
        hover_data=["Pclass", "Sex", "Embarked"],
        labels={"Survived": "생존 여부"},
        color_discrete_map={0: "red", 1: "green"}
    )
    st.plotly_chart(chart_fare, use_container_width=True)

    st.markdown("---")

    st.markdown("**탑승 항구별 생존 현황**")
    embarked_survival = (
        df_filtered.groupby("Embarked")["Survived"]
        .mean()
        .mul(100)
        .reset_index()
    )
    chart_embarked = alt.Chart(embarked_survival).mark_bar().encode(
        x=alt.X("Embarked:N", title="탑승 항구"),
        y=alt.Y("Survived:Q", title="생존율 (%)"),
        color="Embarked:N"
    )
    st.altair_chart(chart_embarked, use_container_width=True)


with col[2]:
    st.subheader("🏅 보조 패널")

    st.markdown("**Top 10 높은 요금 지불 승객**")
    top_fare = df_filtered.sort_values(by="Fare", ascending=False).head(10)
    st.dataframe(
        top_fare[["Name", "Pclass", "Sex", "Age", "Fare", "Survived"]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    st.markdown("**특이 케이스**")
    survived_only = df_filtered[df_filtered["Survived"] == 1]

    if not survived_only.empty:
        youngest = survived_only.loc[survived_only["Age"].idxmin()]
        oldest = survived_only.loc[survived_only["Age"].idxmax()]

        st.markdown(f"- 👶 최연소 생존자: **{youngest['Name']}**, {int(youngest['Age'])}세, Pclass {youngest['Pclass']}")
        st.markdown(f"- 👴 최연장 생존자: **{oldest['Name']}**, {int(oldest['Age'])}세, Pclass {oldest['Pclass']}")
    else:
        st.info("생존자 데이터가 없습니다.")

    st.markdown("---")

    st.subheader("ℹ️ About")
    st.markdown("""
    - 데이터 출처: [Kaggle Titanic Dataset](https://www.kaggle.com/c/titanic)  
    - **Survived**: 1=생존, 0=사망  
    - **Pclass**: 선실 등급 (1=1등석, 2=2등석, 3=3등석)  
    - **Embarked**: C=쉘부르, Q=퀸즈타운, S=사우샘프턴  
    - 결측치: 일부 Age, Cabin 데이터는 비어 있음  
    """)

