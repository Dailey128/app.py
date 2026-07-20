import streamlit as st
import math
import statistics

# ---------- 页面配置 ----------
st.set_page_config(page_title="超声波声速测量", layout="centered")

# ---------- 理论声速函数 ----------
def theoretical_speed(T):
    return 331.45 + 0.607 * T

# ---------- 驻波法计算 ----------
def calc_standing_wave(f, T, positions):
    """
    计算驻波法结果，返回包含所有关键量的字典
    """
    pos_m = [p / 1000.0 for p in positions]          # mm → m
    diffs = [pos_m[i+1] - pos_m[i] for i in range(9)] # 9 个半波长
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
        'std_diff_m': std_diff,
        'wavelength_mm': wavelength * 1000,
        'wavelength_m': wavelength,
        'v': v,
        'v0': v0,
        'rel_error': rel_error,
        'u_v': u_v
    }

# ---------- 相位比较法计算 ----------
def calc_phase_method(f, T, positions):
    """
    计算相位比较法结果，返回包含所有关键量的字典
    """
    pos_m = [p / 1000.0 for p in positions]
    diffs = [pos_m[i+1] - pos_m[i] for i in range(9)]  # 相邻同相点间距 = 波长
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
        'std_wavelength_m': std_wavelength,
        'v': v,
        'v0': v0,
        'rel_error': rel_error,
        'u_v': u_v
    }

# ---------- 默认数据 ----------
DEFAULT_STANDING = [73.24, 77.88, 82.48, 86.98, 91.62, 96.24, 100.72, 105.24, 109.92, 114.58]
DEFAULT_PHASE = [123.82, 133.00, 142.24, 151.22, 160.82, 170.22, 179.40, 189.04, 198.20, 207.64]

# ==================== 页面主体 ====================
st.title("🔊 超声波声速测量计算平台")

# ---------- 1. 方法选择 ----------
method = st.radio(
    "请选择测量方法",
    ("驻波法（10个极大值位置）", "相位比较法（10个同相点位置）")
)

if method == "驻波法（10个极大值位置）":
    default_pos = DEFAULT_STANDING
else:
    default_pos = DEFAULT_PHASE
default_pos_str = ' '.join(map(str, default_pos))

# ---------- 2. 输入表单（包含公式区域） ----------
with st.form(key="input_form"):
    col_freq, col_temp = st.columns(2)
    with col_freq:
        f = st.number_input("声源频率 (Hz):", value=37654.0, format="%.2f")
    with col_temp:
        T = st.number_input("环境温度 (°C):", value=27.0, format="%.2f")
    
    positions_input = st.text_area(
        "位置数据 (mm，空格或逗号分隔):",
        value=default_pos_str,
        height=80,
        help="请输入10个位置数据"
    )

    # ---------- 公式区域（现在放在数据输入下方，按钮上方） ----------
    with st.expander("📐 计算公式（点击展开/收起）", expanded=True):
        st.markdown("""
        **1. 声速公式**
        - 驻波法：$v = f \\cdot \\lambda$，其中 $\\lambda = 2 \\cdot \\overline{\\Delta x}$（半波长平均值）
        - 相位比较法：$v = f \\cdot \\lambda$，其中 $\\lambda = \\overline{\\Delta x}$（相邻同相点间距平均值）

        **2. 相对误差**
        $$E = \\frac{|v - v_0|}{v_0} \\times 100\\%$$
        $$v_0 = 331.45 + 0.607 \\cdot T \\quad \\text{(理论声速)}$$

        **3. 合成标准不确定度**
        $$u(v) = f \\cdot u(\\lambda), \\quad u(\\lambda) = \\frac{\\sigma(\\Delta x)}{\\sqrt{n}}$$
        """)
        st.caption("其中 $n = 9$ 为差值个数，$\\sigma(\\Delta x)$ 为相邻间距（或波长）的实验标准差。")

    # 提交按钮
    submitted = st.form_submit_button("🚀 计算")

# ---------- 3. 处理计算（仅在点击按钮后） ----------
if submitted:
    # 解析输入
    try:
        positions = [float(x.strip()) for x in positions_input.replace(',', ' ').split() if x.strip()]
        if len(positions) != 10:
            st.error(f"❌ 错误：需要 10 个位置数据，您输入了 {len(positions)} 个。")
            st.stop()
    except Exception as e:
        st.error(f"❌ 输入错误: {e}")
        st.stop()

    # 执行计算
    if method == "驻波法（10个极大值位置）":
        result = calc_standing_wave(f, T, positions)
    else:
        result = calc_phase_method(f, T, positions)

    # ---------- 显示结果 ----------
    st.subheader("📊 计算结果")
    
    # 通用结果（两种方法共有）
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("实验声速", f"{result['v']:.2f} m/s")
    with col2:
        st.metric("理论声速", f"{result['v0']:.2f} m/s")
    with col3:
        st.metric("相对误差", f"{result['rel_error']:.2f} %")
    
    st.metric("合成标准不确定度 u(v)", f"{result['u_v']:.1f} m/s")
    
    # 方法特定的中间量
    if method == "驻波法（10个极大值位置）":
        st.write("**相邻间距 (半波长) (mm):**", result['diffs_mm'])
        st.write(f"**平均间距:** {result['avg_diff_mm']:.4f} mm = {result['avg_diff_m']:.6f} m")
        st.write(f"**波长:** {result['wavelength_mm']:.4f} mm = {result['wavelength_m']:.6f} m")
        # 显示公式与变量代入
        st.markdown("---")
        st.markdown("**📝 计算公式与代入值**")
        st.latex(f"v = f \\cdot \\lambda = {f:.2f} \\times {result['wavelength_m']:.6f} = {result['v']:.2f} \\; \\text{{m/s}}")
        st.latex(f"\\lambda = 2 \\cdot \\overline{{\\Delta x}} = 2 \\times {result['avg_diff_m']:.6f} = {result['wavelength_m']:.6f} \\; \\text{{m}}")
        st.latex(f"u(\\lambda) = \\frac{{\\sigma(\\Delta x)}}{{\\sqrt{{9}}}} = \\frac{{{result['std_diff_m']:.6f}}}{{3}} = {result['u_v']/f:.6f} \\; \\text{{m}}")
        st.latex(f"u(v) = f \\cdot u(\\lambda) = {f:.2f} \\times {result['u_v']/f:.6f} = {result['u_v']:.1f} \\; \\text{{m/s}}")
        st.latex(f"E = \\frac{{|{result['v']:.2f} - {result['v0']:.2f}|}}{{{result['v0']:.2f}}} \\times 100\\% = {result['rel_error']:.2f}\\%")
    else:  # 相位比较法
        st.write("**相邻同相点间距（波长） (mm):**", result['diffs_mm'])
        st.write(f"**平均波长:** {result['avg_wavelength_mm']:.4f} mm = {result['avg_wavelength_m']:.6f} m")
        st.markdown("---")
        st.markdown("**📝 计算公式与代入值**")
        st.latex(f"v = f \\cdot \\lambda = {f:.2f} \\times {result['avg_wavelength_m']:.6f} = {result['v']:.2f} \\; \\text{{m/s}}")
        st.latex(f"\\lambda = \\overline{{\\Delta x}} = {result['avg_wavelength_m']:.6f} \\; \\text{{m}}")
        st.latex(f"u(\\lambda) = \\frac{{\\sigma(\\Delta x)}}{{\\sqrt{{9}}}} = \\frac{{{result['std_wavelength_m']:.6f}}}{{3}} = {result['u_v']/f:.6f} \\; \\text{{m}}")
        st.latex(f"u(v) = f \\cdot u(\\lambda) = {f:.2f} \\times {result['u_v']/f:.6f} = {result['u_v']:.1f} \\; \\text{{m/s}}")
        st.latex(f"E = \\frac{{|{result['v']:.2f} - {result['v0']:.2f}|}}{{{result['v0']:.2f}}} \\times 100\\% = {result['rel_error']:.2f}\\%")
else:
    # 未点击按钮时显示提示
    st.info("👆 请确认参数无误后，点击 **“计算”** 按钮查看结果。")
