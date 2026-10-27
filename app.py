
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="소재공학 설계 연구실",
    page_icon="🔬",
    layout="wide"
)

# 교육용 대표 물성값: 실제 제품 설계에는 제조사 자료 확인 필요
MATERIALS = {
    "구조용 강철": {
        "E": 200e9, "yield": 250e6,
        "density": 7850, "cost": 1.0
    },
    "알루미늄 합금": {
        "E": 69e9, "yield": 276e6,
        "density": 2700, "cost": 2.8
    },
    "티타늄 합금": {
        "E": 114e9, "yield": 800e6,
        "density": 4430, "cost": 18.0
    },
    "ABS 플라스틱": {
        "E": 2.3e9, "yield": 40e6,
        "density": 1050, "cost": 2.0
    },
}

st.title("🔬 소재공학 설계 연구실")
st.caption("소재 물성 · 구조 안전성 · 경량 설계 최적화")
st.info(
    "교육용 모델입니다. 직사각형 단면의 외팔보 끝에 "
    "하중이 수직으로 작용하는 상황을 단순화해 분석합니다."
)

with st.sidebar:
    st.header("⚙️ 설계 조건")

    material_name = st.selectbox(
        "소재 선택", list(MATERIALS.keys())
    )

    load_n = st.number_input(
        "끝단 하중 (N)", min_value=1.0,
        max_value=100000.0, value=500.0, step=50.0
    )
    length_mm = st.number_input(
        "보 길이 (mm)", min_value=50.0,
        max_value=5000.0, value=500.0, step=50.0
    )
    width_mm = st.number_input(
        "단면 너비 (mm)", min_value=5.0,
        max_value=500.0, value=30.0, step=5.0
    )
    height_mm = st.number_input(
        "단면 높이 (mm)", min_value=5.0,
        max_value=500.0, value=40.0, step=5.0
    )
    target_sf = st.slider(
        "목표 안전율", 1.0, 5.0, 2.0, 0.1
    )
    max_deflection_mm = st.number_input(
        "허용 끝단 변위 (mm)", min_value=0.1,
        max_value=100.0, value=5.0, step=0.5
    )

m = MATERIALS[material_name]
L = length_mm / 1000
b = width_mm / 1000
h = height_mm / 1000
F = load_n

# 직사각형 단면 외팔보의 끝단 집중하중 모델
I = b * h**3 / 12
c = h / 2
moment = F * L
stress_pa = moment * c / I
deflection_m = F * L**3 / (3 * m["E"] * I)
safety_factor = m["yield"] / stress_pa

volume = L * b * h
mass_kg = volume * m["density"]
estimated_cost = mass_kg * m["cost"]

stress_mpa = stress_pa / 1e6
deflection_mm = deflection_m * 1000
safe = (
    safety_factor >= target_sf
    and deflection_mm <= max_deflection_mm
)

# 상단 핵심 지표
st.subheader("📊 설계 분석 결과")
c1, c2, c3, c4 = st.columns(4)
c1.metric("최대 굽힘 응력", f"{stress_mpa:.2f} MPa")
c2.metric("끝단 변위", f"{deflection_mm:.2f} mm")
c3.metric("안전율", f"{safety_factor:.2f}")
c4.metric("보 질량", f"{mass_kg:.3f} kg")

if safe:
    st.success("설정한 안전율 및 변위 기준을 만족합니다.")
else:
    st.warning(
        "설정한 기준 중 하나 이상을 만족하지 못합니다. "
        "소재나 단면 치수를 변경해 비교하세요."
    )

st.caption(
    f"선택 소재: {material_name} · "
    f"항복강도: {m['yield'] / 1e6:.1f} MPa · "
    f"탄성계수: {m['E'] / 1e9:.1f} GPa"
)

tab1, tab2, tab3 = st.tabs(
    ["📈 소재 비교", "🧪 설계 최적화", "📋 계산 상세"]
)

with tab1:
    st.subheader("같은 형상에서 소재별 성능 비교")
    rows = []

    for name, prop in MATERIALS.items():
        stress = stress_pa
        delta = F * L**3 / (3 * prop["E"] * I) * 1000
        sf = prop["yield"] / stress
        mass = volume * prop["density"]

        rows.append({
            "소재": name,
            "응력 (MPa)": round(stress / 1e6, 2),
            "변위 (mm)": round(delta, 3),
            "안전율": round(sf, 2),
            "질량 (kg)": round(mass, 3),
            "목표 만족": (
                "만족" if sf >= target_sf
                and delta <= max_deflection_mm else "미달"
            )
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    chart = px.bar(
        df, x="소재", y="변위 (mm)", color="소재",
        title="소재별 끝단 변위 비교"
    )
    st.plotly_chart(chart, use_container_width=True)

    chart2 = px.bar(
        df, x="소재", y="안전율", color="소재",
        title="소재별 안전율 비교"
    )
    chart2.add_hline(
        y=target_sf, line_dash="dash",
        annotation_text="목표 안전율"
    )
    st.plotly_chart(chart2, use_container_width=True)

with tab2:
    st.subheader("목표 기준을 만족하는 최소 높이 탐색")
    st.write(
        "너비와 길이는 고정하고, 단면 높이를 바꿔 "
        "목표 안전율과 허용 변위를 동시에 만족하는 "
        "가장 가벼운 후보를 찾습니다."
    )

    candidates = []

    for height_candidate_mm in np.arange(
        5.0, max(3 * height_mm, 100.0) + 1, 1.0
    ):
        hc = height_candidate_mm / 1000
        Ic = b * hc**3 / 12
        stress_c = F * L * (hc / 2) / Ic
        delta_c = F * L**3 / (3 * m["E"] * Ic) * 1000
        sf_c = m["yield"] / stress_c
        mass_c = L * b * hc * m["density"]

        candidates.append({
            "높이 (mm)": height_candidate_mm,
            "응력 (MPa)": stress_c / 1e6,
            "변위 (mm)": delta_c,
            "안전율": sf_c,
            "질량 (kg)": mass_c,
            "만족": (
                sf_c >= target_sf
                and delta_c <= max_deflection_mm
            )
        })

    opt_df = pd.DataFrame(candidates)
    valid = opt_df[opt_df["만족"]]

    if not valid.empty:
        best = valid.sort_values("질량 (kg)").iloc[0]
        st.success(
            f"추천 단면 높이: {best['높이 (mm)']:.0f} mm"
        )
        a, bcol, ccol = st.columns(3)
        a.metric("추천 높이", f"{best['높이 (mm)']:.0f} mm")
        bcol.metric("추천 질량", f"{best['질량 (kg)']:.3f} kg")
        ccol.metric("추천 안전율", f"{best['안전율']:.2f}")

        st.line_chart(
            opt_df.set_index("높이 (mm)")[
                ["안전율", "변위 (mm)"]
            ]
        )
        st.caption(
            "후보 범위 내에서 탐색한 결과이며, "
            "실제 구조물의 최적 설계를 보증하지 않습니다."
        )
    else:
        st.error(
            "탐색 범위에서 두 기준을 동시에 만족하는 "
            "설계를 찾지 못했습니다. 하중이나 기준을 조정해 보세요."
        )

with tab3:
    st.subheader("계산에 사용한 공식")
    st.latex(r"I = \frac{bh^3}{12}")
    st.latex(r"\sigma_{max} = \frac{FL(h/2)}{I}")
    st.latex(r"\delta = \frac{FL^3}{3EI}")
    st.latex(r"n = \frac{\sigma_y}{\sigma_{max}}")
    st.write(
        "I: 단면 2차 모멘트, F: 끝단 하중, L: 보 길이, "
        "b: 단면 너비, h: 단면 높이, E: 탄성계수, "
        "σy: 항복강도, n: 안전율"
    )

    st.subheader("설계 요약")
    summary = pd.DataFrame([{
        "소재": material_name,
        "하중 (N)": F,
        "길이 (mm)": length_mm,
        "너비 (mm)": width_mm,
        "높이 (mm)": height_mm,
        "응력 (MPa)": stress_mpa,
        "변위 (mm)": deflection_mm,
        "안전율": safety_factor,
        "질량 (kg)": mass_kg,
        "추정 상대 비용": estimated_cost,
        "기준 만족": "만족" if safe else "미달"
    }])
    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.download_button(
        "설계 결과 CSV 다운로드",
        data=summary.to_csv(index=False).encode("utf-8-sig"),
        file_name="design_result.csv",
        mime="text/csv"
    )

st.divider()
st.caption(
    "주의: 이 시뮬레이터는 선형 탄성, 작은 변형, "
    "이상적인 외팔보 및 균일 단면을 가정합니다. "
    "실제 제품의 안전성 인증이나 전문 구조해석을 대체하지 않습니다."
)
