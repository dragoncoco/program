
import streamlit as st

st.set_page_config(
    page_title="Material Finder",
    page_icon="🔬"
)

st.title("🔬 Material Finder")
st.write("원하는 조건에 맞는 소재를 추천해 드립니다.")

# 소재별 특성 점수 데이터 (1~5점)
materials = {
    "알루미늄 합금": {
        "가벼움": 4, "강도": 3, "가격": 3, "내열성": 3
    },
    "강철": {
        "가벼움": 2, "강도": 5, "가격": 5, "내열성": 4
    },
    "탄소섬유 복합재": {
        "가벼움": 5, "강도": 5, "가격": 1, "내열성": 4
    },
    "티타늄 합금": {
        "가벼움": 4, "강도": 5, "가격": 1, "내열성": 5
    },
    "일반 플라스틱": {
        "가벼움": 5, "강도": 1, "가격": 5, "내열성": 1
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
    try:
        # 중요도 데이터 검증
        if not weights or sum(weights.values()) <= 0:
            st.error("중요도 점수의 합은 0보다 커야 합니다.")

        elif not materials:
            st.error("추천할 소재 데이터가 없습니다.")

        else:
            results = []
            total_weight = sum(weights.values())

            # 소재 데이터 확인 및 점수 계산
            for name, properties in materials.items():

                for key in weights:
                    if key not in properties:
                        raise KeyError(
                            f"{name}의 '{key}' 데이터가 없습니다."
                        )

                    if not isinstance(properties[key], (int, float)):
                        raise TypeError(
                            f"{name}의 '{key}' 점수가 숫자가 아닙니다."
                        )

                    if not 1 <= properties[key] <= 5:
                        raise ValueError(
                            f"{name}의 '{key}' 점수는 1~5여야 합니다."
                        )

                total = sum(
                    properties[key] * weights[key]
                    for key in weights
                )

                score = total / total_weight
                results.append((name, score))

            # 점수가 높은 순서대로 정렬
            results.sort(
                key=lambda item: item[1],
                reverse=True
            )

            st.subheader("2. 추천 결과")

            for rank, (name, score) in enumerate(results, start=1):
                st.write(
                    f"{rank}위. {name} — 점수 {score:.2f}/5"
                )

            # 가장 높은 점수의 소재 추천
            best_name, best_score = results[0]

            st.success(
                f"가장 높은 점수의 소재: {best_name}"
            )

            st.caption(
                "※ 예시용 특성 점수를 사용한 결과입니다. "
                "실제 소재 선택에는 사용 환경과 실제 성능 및 가격도 "
                "고려해야 합니다."
            )

    except (ZeroDivisionError, KeyError, TypeError, ValueError) as e:
        st.error(f"계산 중 오류가 발생했습니다: {e}")

    except Exception:
        st.error(
            "예상하지 못한 오류가 발생했습니다. "
            "소재 데이터와 프로그램 코드를 확인해 주세요."
        )
