import streamlit as st
import math
import statistics

# ---------- 理论声速 ----------
def theoretical_speed(T):
    return 331.45 + 0.607 * T

# ---------- 驻波法 ----------
def standing_wave_calc(f, T, positions):
    if len(positions) != 10:
        return None, "需要输入恰好 10 个位置数据。"
    pos_m = [p / 1000.0 for p in positions]
    diffs = [pos_m[i+1] - pos_m[i] for i in range(9)]
    avg_diff = sum(diffs) / 9
    std_diff = statistics.stdev(diffs) if 9 > 1 else 0.0
    u_avg_diff = std_diff / math.sqrt(9)
    wavelength = 2 * avg_diff
    u_wavelength = 2 * u_avg_diff
    v = f * wavelength
    u_v = f * u_wavelength
    v0 = theoretical_speed(T)
    rel_error = abs(v - v0) / v0 * 100
    rel_unc = u_v / v * 100 if v != 0 else 0
    return {
        "diffs_mm": [round(d*1000, 4) for d in diffs],
        "avg_diff_mm": avg_diff * 1000,
        "wavelength_mm": wavelength * 1000,
        "v": v,
        "v0": v0,
        "rel_error": rel_error,
        "u_v": u_v,
        "rel_unc": rel_unc
    }, None

# ---------- 相位比较法 ----------
def phase_comparison_calc(f, T, positions):
    if len(positions) != 10:
        return None, "需要输入恰好 10 个位置数据。"
    pos_m = [p / 1000.0 for p in positions]
    diffs = [pos_m[i+1] - pos_m[i] for i in range(9)]
    avg_wavelength = sum(diffs) / 9
    std_wavelength = statistics.stdev(diffs) if 9 > 1 else 0.0
    u_avg_wavelength = std_wavelength / math.sqrt(9)
    v = f * avg_wavelength
    u_v = f * u_avg_wavelength
    v0 = theoretical_speed(T)
    rel_error = abs(v - v0) / v0 * 100
    rel_unc = u_v / v * 100 if v != 0 else 0
    return {
        "diffs_mm": [round(d*1000, 4) for d in diffs],
        "avg_wavelength_mm": avg_wavelength * 1000,
        "v": v,
        "v0": v0,
        "rel_error": rel_error,
        "u_v": u_v,
        "rel_unc": rel_unc
    }, None

# ---------- 时差法（自动计算相邻差值） ----------
def time_difference_calc(T, dists, times):
    if len(dists) != 10 or len(times) != 10:
        return None, "需要输入恰好 10 个距离和 10 个时间。"
    dist_diffs = [dists[i+1] - dists[i] for i in range(9)]
    time_diffs = [times[i+1] - times[i] for i in range(9)]
    speeds = []
    for dd, dt in zip(dist_diffs, time_diffs):
        if dt == 0:
            continue
        d_m = dd / 1000.0
        t_s = dt / 1_000_000.0
        speeds.append(d_m / t_s)
    if len(speeds) != 9:
        return None, "有效速度不足 9 组，请检查时间差是否为 0。"
    avg_v = sum(speeds) / 9
    std_v = statistics.stdev(speeds) if 9 > 1 else 0.0
    u_avg_v = std_v / math.sqrt(9)
    v0 = theoretical_speed(T)
    rel_error = abs(avg_v - v0) / v0 * 100
    rel_unc = u_avg_v / avg_v * 100 if avg_v != 0 else 0
    return {
        "dist_diffs_mm": [round(dd, 3) for dd in dist_diffs],
        "time_diffs_us": [round(dt, 2) for dt in time_diffs],
        "speeds": [round(v, 2) for v in speeds],
        "avg_v": avg_v,
        "v0": v0,
        "rel_error": rel_error,
        "u_v": u_avg_v,
        "rel_unc": rel_unc
    }, None

# ---------- Streamlit 界面 ----------
st.set_page_config(page_title="超声波声速测量平台", layout="centered")
st.title("🔊 超声波声速测量计算平台")
st.markdown("支持 **驻波法**、**相位比较法** 和 **时差法**。所有距离/波长单位均为 **mm**，时差法时间单位为 **μs**。")

method = st.selectbox("选择测量方法", ["驻波法", "相位比较法", "时差法"])

if method == "驻波法":
    st.subheader("驻波法")
    f = st.number_input("声源频率 (Hz)", value=37654.0, step=1.0)
    T = st.number_input("环境温度 (°C)", value=27.0, step=0.1)
    pos_input = st.text_area(
        "输入 10 个极大值位置 (mm)，用空格或逗号分隔",
        "73.2 77.4 82.6 86.8 92.0 97.0 101.2 105.4 110.6 115.0"
    )
    if st.button("计算"):
        try:
            positions = [float(x) for x in pos_input.replace(',', ' ').split() if x.strip()]
            result, err = standing_wave_calc(f, T, positions)
            if err:
                st.error(err)
            else:
                st.success("计算完成")
                st.write(f"**相邻间距 (mm):** {result['diffs_mm']}")
                st.write(f"**平均间距:** {result['avg_diff_mm']:.4f} mm = {result['avg_diff_mm']/1000:.6f} m")
                st.write(f"**波长:** {result['wavelength_mm']:.4f} mm = {result['wavelength_mm']/1000:.6f} m")
                st.write(f"**实验声速:** {result['v']:.2f} m/s")
                st.write(f"**理论声速 (T={T}°C):** {result['v0']:.2f} m/s")
                st.write(f"**相对误差:** {result['rel_error']:.2f} %")
                st.write(f"**合成标准不确定度 u(v):** {result['u_v']:.2f} m/s")
                st.write(f"**相对不确定度:** {result['rel_unc']:.2f} %")
        except Exception as e:
            st.error(f"输入错误: {e}")

elif method == "相位比较法":
    st.subheader("相位比较法")
    f = st.number_input("声源频率 (Hz)", value=37654.0, step=1.0)
    T = st.number_input("环境温度 (°C)", value=27.0, step=0.1)
    pos_input = st.text_area(
        "输入 10 个同相点位置 (mm)，用空格或逗号分隔",
        "60 69 78 87 96 105 114 123 132 141"
    )
    if st.button("计算"):
        try:
            positions = [float(x) for x in pos_input.replace(',', ' ').split() if x.strip()]
            result, err = phase_comparison_calc(f, T, positions)
            if err:
                st.error(err)
            else:
                st.success("计算完成")
                st.write(f"**相邻同相点间距（波长）(mm):** {result['diffs_mm']}")
                st.write(f"**平均波长:** {result['avg_wavelength_mm']:.4f} mm = {result['avg_wavelength_mm']/1000:.6f} m")
                st.write(f"**实验声速:** {result['v']:.2f} m/s")
                st.write(f"**理论声速 (T={T}°C):** {result['v0']:.2f} m/s")
                st.write(f"**相对误差:** {result['rel_error']:.2f} %")
                st.write(f"**合成标准不确定度 u(v):** {result['u_v']:.2f} m/s")
                st.write(f"**相对不确定度:** {result['rel_unc']:.2f} %")
        except Exception as e:
            st.error(f"输入错误: {e}")

else:  # 时差法
    st.subheader("时差法")
    st.markdown("建议每隔 20 mm 记录一次位置和到达时间，共 10 组数据。程序将自动计算相邻差值并求各段声速。")
    T = st.number_input("环境温度 (°C)", value=24.2, step=0.1)
    dist_input = st.text_area(
        "输入 10 个位置 (mm)，用空格或逗号分隔",
        "60 70 80 90 100 110 120 130 140 150"
    )
    time_input = st.text_area(
        "输入对应的 10 个时间 (μs)，用空格或逗号分隔",
        "335 364 393 422 450 479 508 536 565 593"
    )
    if st.button("计算"):
        try:
            dists = [float(x) for x in dist_input.replace(',', ' ').split() if x.strip()]
            times = [float(x) for x in time_input.replace(',', ' ').split() if x.strip()]
            result, err = time_difference_calc(T, dists, times)
            if err:
                st.error(err)
            else:
                st.success("计算完成")
                st.write(f"**距离差 (mm):** {result['dist_diffs_mm']}")
                st.write(f"**时间差 (μs):** {result['time_diffs_us']}")
                st.write(f"**各段声速 (m/s):** {result['speeds']}")
                st.write(f"**平均声速:** {result['avg_v']:.2f} m/s")
                st.write(f"**理论声速 (T={T}°C):** {result['v0']:.2f} m/s")
                st.write(f"**相对误差:** {result['rel_error']:.2f} %")
                st.write(f"**合成标准不确定度 u(v):** {result['u_v']:.2f} m/s")
                st.write(f"**相对不确定度:** {result['rel_unc']:.2f} %")
        except Exception as e:
            st.error(f"输入错误: {e}")

st.markdown("---")
st.caption("所有计算基于 A 类不确定度评定（测量重复性）。理论声速采用 v = 331.45 + 0.607·T")
