import streamlit as st
import math

# 页面配置
st.set_page_config(page_title="声速不确定度计算器", layout="centered")
st.title("🔊 超声波声速不确定度计算工具")
st.markdown("支持驻波法、相位比较法、时差法、直接输入波长")

# 用户输入频率和温度
col_freq, col_temp = st.columns(2)
with col_freq:
    frequency = st.number_input("频率 (Hz)", value=34000.0, step=100.0, format="%.1f")
with col_temp:
    temperature = st.number_input("温度 (°C)", value=25.0, step=0.5, format="%.1f")

# 方法选择
method = st.selectbox(
    "选择测量方法",
    ["驻波法", "相位比较法", "时差法", "直接输入平均波长"]
)

wavelength = None  # 最终用于计算的波长（m）

# ------------------ 驻波法 ------------------
if method == "驻波法":
    st.markdown("**驻波法公式**：$\\lambda = 2 \\times \\frac{\\sum_{i=0}^{4}(X_{i+6}-X_{i+1})}{25}$")
    st.markdown("请输入 **10个相邻极大值的位置**（单位：cm），用空格分隔，例如：`0.0 2.0 4.0 ...`")
    pos_input = st.text_area("位置数据（cm）", value="0.0 2.0 4.0 6.0 8.0 10.0 12.0 14.0 16.0 18.0")
    if st.button("计算波长（驻波法）"):
        try:
            positions_cm = [float(x) for x in pos_input.split()]
            if len(positions_cm) != 10:
                st.error("❌ 必须输入恰好10个数据！")
            else:
                positions_cm.sort()
                positions = [x / 100 for x in positions_cm]  # cm → m
                sum_diff = 0
                with st.expander("查看逐项计算过程"):
                    for i in range(5):
                        diff = positions[i+5] - positions[i]
                        sum_diff += diff
                        st.write(f"X{i+6} - X{i+1} = {positions_cm[i+5]:.2f}cm - {positions_cm[i]:.2f}cm = {diff*100:.2f}cm")
                wavelength = 2 * sum_diff / 25
                st.success(f"✅ 平均波长 λ = **{wavelength*100:.4f} cm**（即 **{wavelength:.6f} m**）")
                st.session_state['wavelength'] = wavelength
        except Exception as e:
            st.error(f"输入解析错误：{e}")

# ------------------ 相位比较法 ------------------
elif method == "相位比较法":
    st.markdown("**相位比较法公式**：$\\lambda = \\frac{\\sum_{i=0}^{4}(X_{i+6}-X_{i+1})}{25}$")
    st.markdown("请输入 **10个同相位点的位置**（单位：cm），用空格分隔，例如：`0.0 1.0 2.0 ...`")
    pos_input = st.text_area("位置数据（cm）", value="0.0 1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0 9.0")
    if st.button("计算波长（相位法）"):
        try:
            positions_cm = [float(x) for x in pos_input.split()]
            if len(positions_cm) != 10:
                st.error("❌ 必须输入恰好10个数据！")
            else:
                positions_cm.sort()
                positions = [x / 100 for x in positions_cm]
                sum_diff = 0
                with st.expander("查看逐项计算过程"):
                    for i in range(5):
                        diff = positions[i+5] - positions[i]
                        sum_diff += diff
                        st.write(f"X{i+6} - X{i+1} = {positions_cm[i+5]:.2f}cm - {positions_cm[i]:.2f}cm = {diff*100:.2f}cm")
                wavelength = sum_diff / 25
                st.success(f"✅ 平均波长 λ = **{wavelength*100:.4f} cm**（即 **{wavelength:.6f} m**）")
                st.session_state['wavelength'] = wavelength
        except Exception as e:
            st.error(f"输入解析错误：{e}")

# ------------------ 时差法 ------------------
elif method == "时差法":
    st.markdown("**时差法公式**：$v = \\frac{1}{5} \\sum_{i=0}^{4} \\frac{X_{i+6}-X_{i+1}}{t_{i+6}-t_{i+1}}$，$\\lambda = v/f$")
    st.markdown("请输入 **10个位置**（单位：cm）和对应的 **10个时间**（单位：s），用空格分隔。建议每隔2cm记录。")
    col_pos, col_time = st.columns(2)
    with col_pos:
        pos_input = st.text_area("位置（cm）", value="0.0 2.0 4.0 6.0 8.0 10.0 12.0 14.0 16.0 18.0")
    with col_time:
        time_input = st.text_area("时间（s）", value="0.000000 0.0000588 0.0001176 0.0001764 0.0002352 0.0002940 0.0003528 0.0004116 0.0004704 0.0005292")
    if st.button("计算波长（时差法）"):
        try:
            positions_cm = [float(x) for x in pos_input.split()]
            times = [float(x) for x in time_input.split()]
            if len(positions_cm) != 10 or len(times) != 10:
                st.error("❌ 位置和时间必须各为10个数据！")
            else:
                # 按位置排序
                pairs = sorted(zip(positions_cm, times))
                positions_cm = [p[0] for p in pairs]
                times = [p[1] for p in pairs]
                positions = [x / 100 for x in positions_cm]
                v_sum = 0
                with st.expander("查看逐项计算过程"):
                    for i in range(5):
                        dx = positions[i+5] - positions[i]
                        dt = times[i+5] - times[i]
                        if dt == 0:
                            st.error("时间差为零，无法计算")
                            st.stop()
                        vi = dx / dt
                        v_sum += vi
                        st.write(f"v{i+1} = ({positions_cm[i+5]:.2f}cm - {positions_cm[i]:.2f}cm) / ({times[i+5]:.6f}s - {times[i]:.6f}s) = {vi:.2f} m/s")
                v_sound = v_sum / 5
                wavelength = v_sound / frequency
                st.success(f"✅ 平均速度 v = **{v_sound:.2f} m/s**")
                st.success(f"✅ 平均波长 λ = **{wavelength*100:.4f} cm**（即 **{wavelength:.6f} m**）")
                st.session_state['wavelength'] = wavelength
        except Exception as e:
            st.error(f"输入解析错误：{e}")

# ------------------ 直接输入 ------------------
else:
    st.markdown("直接输入已知的平均波长（单位：m）")
    wavelength = st.number_input("平均波长 (m)", value=0.01, step=0.001, format="%.6f")
    if st.button("确认波长"):
        st.session_state['wavelength'] = wavelength
        st.success(f"已设置波长 = {wavelength:.6f} m")

# ------------------ 公用计算结果 ------------------
if 'wavelength' in st.session_state and st.session_state['wavelength'] is not None:
    wavelength = st.session_state['wavelength']
    # 计算声速
    v = frequency * wavelength
    v_theory = 331.45 + 0.59 * temperature   # 使用0.59系数

    # 相对误差
    relative_error = abs(v - v_theory) / v_theory * 100 if v_theory != 0 else float('inf')

    # 仪器误差（B类不确定度）
    delta_lambda = 0.001   # m
    delta_f = 1.0          # Hz
    delta_t = 0.5          # °C
    u_lambda = delta_lambda / math.sqrt(3)
    u_f = delta_f / math.sqrt(3)
    u_t = delta_t / math.sqrt(3)

    # 合成相对不确定度
    rel_u = math.sqrt(
        (u_lambda / wavelength) ** 2 +
        (u_f / frequency) ** 2 +
        (0.6 * u_t / v) ** 2
    )
    u_v = v * rel_u
    rel_percent = rel_u * 100

    # 显示结果
    st.divider()
    st.subheader("📊 计算结果")
    col1, col2 = st.columns(2)
    col1.metric("计算声速", f"{v:.2f} m/s")
    col2.metric("空气中理论声速", f"{v_theory:.2f} m/s")
    st.metric("📌 相对误差 (测量 vs 理论)", f"{relative_error:.2f} %")
    st.metric("合成标准不确定度", f"{u_v:.4f} m/s")
    st.metric("相对不确定度", f"{rel_percent:.2f} %")
    st.success(f"**最终结果**: v = **{v:.2f}** ± **{u_v:.4f}** m/s  (即 ± **{rel_percent:.2f}**%)")
    
