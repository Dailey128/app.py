import streamlit as st
import math
import statistics

# ---------- 页面配置 ----------
st.set_page_config(page_title="超声波声速测量", layout="centered")

# ---------- 理论声速 ----------
def theoretical_speed(T):
    return 331.45 + 0.607 * T

# ---------- 驻波法计算 ----------
def calc_standing_wave(f, T, positions):
    """返回驻波法结果字典"""
    pos_m = [p / 1000.0 for p in positions]
    diffs = [pos_m[i+1] - pos_m[i] for i in range(9)]
    avg_diff = sum(diffs) / 9
    std_diff = statistics.stdev(diffs) if len(diffs) > 1 else 0.0
    u_avg_diff = std_diff / math.sqrt(9)
    wavelength = 2 * avg_diff
    u_wavelength = 2 * u_avg_diff
    v = f * wavelength
    u_v = f * u_wavelength
    v0 = theoretical_speed(T)
    rel_error = abs(v - v0) / v0 * 100

    return {
        'diffs_mm': [round(d*1000, 4) for d in diffs],
        'avg_diff_mm': avg_diff * 1000,
        'avg_diff_m': avg_diff,
        'wavelength_mm': wavelength * 1000,
        'wavelength_m': wavelength,
        'v': v,
        'v0': v0,
        'rel_error': rel_error,
        'u_v': u_v
    }

# ---------- 相位比较法计算 ----------
def calc_phase_method(f, T, positions):
    pos_m = [p / 1000.0 for p in positions]
    diffs = [pos_m[i+1] - pos_m[i] for i in range(9)]
    avg_wavelength = sum(diffs) / 9
    std_wavelength = statistics.stdev(diffs) if len(diffs) > 1 else 0.0
    u_avg_wavelength = std_wavelength / math.sqrt(9)
    v = f * avg_wavelength
    u_v = f * u_avg_wavelength
    v0 = theoretical_speed(T)
    rel_error = abs(v - v0) / v0 * 100

    return {
        'diffs_mm': [round(d*1000, 4) for d in diffs],
        'avg_wavelength_mm': avg_wavelength * 1000,
        'avg_wavelength_m': avg_wavelength,
        'v': v,
        'v0': v0,
        'rel_error': rel_error,
        'u_v': u_v
    }

# ---------- 默认数据 ----------
DEFAULT_STANDING = [73.24, 77.88, 82.48, 86.98, 91.62, 96.24, 100.72, 105.24, 109.92, 114.58]
DEFAULT_PHASE = [123.82, 133.00, 142.24, 151.22, 160.82, 170.22, 179.40, 189.04, 198.20, 207.64]

# ---------- 主界面 ----------
st.title("超声波声速测量计算平台")

# 选择方法
method = st.radio(
    "请选择测量方法",
    ("驻波法（10个极大值位置）", "相位比较法（10个同相点位置）")
)

# 输入参数
with st.form(key="input_form"):
    f = st.number_input("请输入声源频率 (Hz):", value=37654.0, format="%.2f")
    T = st.number_input("请输入环境温度 (°C):", value=27.0, format="%.2f")
    
    use_default = st.checkbox("使用默认示例数据")
    
    if use_default:
        if method == "驻波法（10个极大值位置）":
            default_pos = DEFAULT_STANDING
            pos_str = ' '.join(map(str, default_pos))
        else:
            default_pos = DEFAULT_PHASE
            pos_str = ' '.join(map(str, default_pos))
        positions_input = st.text_area("位置数据 (mm，空格或逗号分隔):", value=pos_str, disabled=True)
        positions = default_pos
    else:
        positions_input = st.text_area("请输入10个位置数据 (mm，空格或逗号分隔):", height=68)
        submitted = st.form_submit_button("计算")

if not use_default:
    submitted = st.form_submit_button("计算")

# ---------- 处理计算结果 ----------
if use_default or ('submitted' in locals() and submitted):
    if not use_default:
        try:
            positions = [float(x.strip()) for x in positions_input.replace(',', ' ').split() if x.strip()]
            if len(positions) != 10:
                st.error(f"错误：需要10个位置数据，您输入了{len(positions)}个。")
                st.stop()
        except Exception as e:
            st.error(f"输入错误: {e}")
            st.stop()

    if method == "驻波法（10个极大值位置）":
        result = calc_standing_wave(f, T, positions)
    else:
        result = calc_phase_method(f, T, positions)

    # ---------- 显示结果 ----------
    st.subheader("计算结果")
    col1, col2 = st.columns(2)

    if method == "驻波法（10个极大值位置）":
        with col1:
            st.metric("平均间距", f"{result['avg_diff_mm']:.4f} mm")
            st.metric("波长", f"{result['wavelength_mm']:.4f} mm")
        with col2:
            st.metric("实验声速", f"{result['v']:.2f} m/s")
            st.metric("理论声速", f"{result['v0']:.2f} m/s")
        st.write(f"**相邻间距 (mm):** {result['diffs_mm']}")
    else:
        with col1:
            st.metric("平均波长", f"{result['avg_wavelength_mm']:.4f} mm")
        with col2:
            st.metric("实验声速", f"{result['v']:.2f} m/s")
            st.metric("理论声速", f"{result['v0']:.2f} m/s")
        st.write(f"**相邻同相点间距（波长） (mm):** {result['diffs_mm']}")

    st.write(f"**相对误差:** {result['rel_error']:.2f} %")
    st.write(f"**合成标准不确定度 u(v):** {result['u_v']:.1f} m/s")
