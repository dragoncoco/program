
import streamlit as st

st.set_page_config(
    page_title="Material Finder",
    page_icon="🔬"
)

st.title("🔬 Material Finder")
st.write("원하는 조건에 맞는 소재를 추천해 드립니다.")

# 예시용 소재 데이터: 특성 점수는 1~5점
materials = {
    "알루미늄 합금": {
        "가벼움": 4,
        "강도": 3,
        "가격": 3,
        "내열성": 3,
    },
    "강철": {
        "가벼움": 2,
        "강도": 5,
        "가격": 5,
        "내열성": 4,
    },
    "탄소섬유 복합재": {
        "가벼움": 5,
        "강도": 5,
        "가격": 1,
        "내열성": 4,
    },
    "티타늄 합금": {
        "가벼움": 4,
        "강도": 5,
        "가격": 1,
        "내열성": 5,
    },
    "일반 플라스틱": {
        "가벼움": 5,
        "강도": 1,
        "가격": 5,
        "내열성": 1,
    },
}

st.subheader("1. 원하는 특성의 중요도를 선택하세요.")

light = st.slider("가벼움", 1, 5, 3)
strength = st.slider("강도", 1, 5, 3)
price = st.slider("저렴한 가격", 1, 5, 3)
heat = st.slider("내열성", 1, 5, 3)

weights = {
    "가벼움": light,
    "강도": strength,
    "가격": price,
    "내열성": heat,
}

if st.button("소재 추천받기"):
    results = []

    for name, properties in materials.items():
        total = sum(
            properties[key] * weights[key]
            for key in weights
        )
        score = total / sum(weights.values())

        results.append((name, score))

    results.sort(key=lambda item: item[1], reverse=True)

    st.subheader("2. 추천 결과")

    for rank, (name, score) in enumerate(results, start=1):
        st.write(f"{rank}위. {name} — 점수 {score:.2f}/5")

    best_name, best_score = results[0]

    st.success(f"가장 높은 점수의 소재: {best_name}")
    st.caption(
        "※ 예시용 특성 점수를 사용한 결과이며, "
        "실제 소재 선택에는 구체적인 사용 환경도 고려해야 합니다."
    )
