import streamlit as st
import math

st.set_page_config(page_title="声速不确定度计算器", layout="centered")
st.title("🔊 超声波声速不确定度计算工具")

with st.form("calc_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        wavelength = st.number_input("平均波长 (m)", value=0.01, format="%.6f")
    with col2:
        frequency = st.number_input("频率 (Hz)", value=34000.0, format="%.1f")
    with col3:
        temperature = st.number_input("温度 (°C)", value=25.0, format="%.1f")
    
    submitted = st.form_submit_button("计算声速与不确定度")

if submitted:
    if wavelength == 0 or frequency == 0:
        st.error("波长和频率不能为零！")
    else:
        # 核心计算
        v = frequency * wavelength
        v_theory = 331.45 + 0.6 * temperature

        # 仪器误差（可调整）
        delta_lambda = 0.001
        delta_f = 1.0
        delta_t = 0.5

        # B类不确定度
        u_lambda = delta_lambda / math.sqrt(3)
        u_f = delta_f / math.sqrt(3)
        u_t = delta_t / math.sqrt(3)

        # 合成相对不确定度
        rel_u = math.sqrt((u_lambda / wavelength)**2 + (u_f / frequency)**2 + (0.6 * u_t / v)**2)
        u_v = v * rel_u
        rel_percent = rel_u * 100

        # 显示结果
        st.divider()
        col_a, col_b = st.columns(2)
        col_a.metric("计算声速", f"{v:.2f} m/s")
        col_b.metric("空气理论声速", f"{v_theory:.2f} m/s")
        
        st.success(f"**最终结果**: v = **{v:.2f}** ± **{u_v:.4f}** m/s")
        st.info(f"📊 **相对不确定度**: **{rel_percent:.4f}%**")
        
