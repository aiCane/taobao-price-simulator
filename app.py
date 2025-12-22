"""
淘宝/京东个性化定价模拟器
模拟不同用户特征下的价格差异
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 页面配置
st.set_page_config(
    page_title="网购平台个性化定价模拟器",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4ECDC4;
        margin-top: 2rem;
    }
    .price-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .price-number {
        font-size: 3.5rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 25px;
        font-size: 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .info-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #4ECDC4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# 模拟定价算法
def calculate_price(base_price, user_profile):
    """
    模拟个性化定价算法
    base_price: 基础价格（元）
    user_profile: 用户特征字典
    返回：最终价格、价格构成详情
    """
    price = base_price
    adjustments = []

    # 1. 新老用户调整（新用户优惠）
    if user_profile["user_type"] == "new":
        price *= 0.85  # 85折
        adjustments.append(("新用户优惠", "-15%"))
    elif user_profile["user_type"] == "loyal":
        price *= 1.10  # 涨价10%（假设对忠诚用户）
        adjustments.append(("忠诚用户溢价", "+10%"))

    # 2. 消费能力调整（基于历史消费）
    if user_profile["spending_level"] == "high":
        price *= 1.15  # 高消费用户涨价15%
        adjustments.append(("高消费用户", "+15%"))
    elif user_profile["spending_level"] == "low":
        price *= 0.90  # 低消费用户降价10%
        adjustments.append(("低消费用户优惠", "-10%"))

    # 3. 设备类型调整（苹果税）
    if user_profile["device"] == "ios":
        price *= 1.08  # iOS用户涨价8%
        adjustments.append(("iOS设备", "+8%"))

    # 4. 活跃度调整
    if user_profile["activity"] == "high":
        price *= 1.05  # 高活跃用户涨价5%
        adjustments.append(("高活跃度", "+5%"))
    elif user_profile["activity"] == "low":
        price *= 0.95  # 低活跃用户降价5%
        adjustments.append(("低活跃度", "-5%"))

    # 5. 时间敏感度（看商品频率）
    if user_profile["frequency"] == "often":
        price *= 1.12  # 经常看的商品涨价12%
        adjustments.append(("高频浏览", "+12%"))

    # 6. 是否使用优惠券（虚假降价）
    if user_profile["has_coupon"]:
        adjustments.append(("优惠券已选择", "待抵扣"))

    # 7. 会员等级
    if user_profile["vip_level"] == "high":
        price *= 0.88  # 高级会员88折
        adjustments.append(("高级会员", "-12%"))

    # 添加随机波动 (±3%)
    random_factor = np.random.uniform(0.97, 1.03)
    price *= random_factor
    adjustments.append(("实时波动", f"{((random_factor - 1) * 100):+.1f}%"))

    return round(price, 2), adjustments


# 生成用户数据（用于图表）
def generate_user_data(num_users=50):
    """生成模拟用户数据"""
    users = []
    for i in range(num_users):
        user_type = np.random.choice(["new", "regular", "loyal"], p=[0.2, 0.5, 0.3])
        spending = np.random.choice(["low", "medium", "high"], p=[0.3, 0.4, 0.3])
        device = np.random.choice(["android", "ios"], p=[0.6, 0.4])
        activity = np.random.choice(["low", "medium", "high"], p=[0.2, 0.5, 0.3])

        base_price = 199
        price, _ = calculate_price(base_price, {
            "user_type": user_type,
            "spending_level": spending,
            "device": device,
            "activity": activity,
            "frequency": "sometimes",
            "has_coupon": False,
            "vip_level": "none"
        })

        users.append({
            "用户ID": i + 1,
            "用户类型": {"new": "新用户", "regular": "普通用户", "loyal": "忠诚用户"}[user_type],
            "消费水平": {"low": "低", "medium": "中", "high": "高"}[spending],
            "设备类型": {"android": "Android", "ios": "iOS"}[device],
            "活跃度": {"low": "低", "medium": "中", "high": "高"}[activity],
            "看到的价格(元)": price
        })

    return pd.DataFrame(users)


# 主程序
def main():
    # 标题
    st.markdown('<h1 class="main-header">🛒 网购平台个性化定价模拟器</h1>', unsafe_allow_html=True)
    st.markdown("**探究为什么你和朋友看到的同一商品价格会相差80元**")

    # 创建两列布局
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown('<h3 class="sub-header">🎯 1. 设置商品基础信息</h3>', unsafe_allow_html=True)

        # 商品选择
        product = st.selectbox(
            "选择商品类型",
            ["运动鞋（参考价：199元）", "无线耳机（参考价：599元）",
             "轻薄笔记本（参考价：4999元）", "智能手表（参考价：1299元）"]
        )

        # 根据商品设置基础价格
        base_prices = {
            "运动鞋（参考价：199元）": 199,
            "无线耳机（参考价：599元）": 599,
            "轻薄笔记本（参考价：4999元）": 4999,
            "智能手表（参考价：1299元）": 1299
        }
        base_price = base_prices[product]

        st.markdown(f"**商品基础参考价：** ¥{base_price}")

    with col2:
        st.markdown('<h3 class="sub-header">👤 2. 设置你的用户特征</h3>', unsafe_allow_html=True)

        # 用户特征输入
        user_type = st.radio(
            "用户类型",
            ["新用户（首次使用）", "普通用户（偶尔使用）", "忠诚用户（高频使用）"],
            horizontal=True
        )
        user_type_map = {
            "新用户（首次使用）": "new",
            "普通用户（偶尔使用）": "regular",
            "忠诚用户（高频使用）": "loyal"
        }

        spending_level = st.select_slider(
            "历史消费水平",
            options=["低消费", "中等消费", "高消费"],
            value="中等消费"
        )
        spending_map = {"低消费": "low", "中等消费": "medium", "高消费": "high"}

        device = st.radio(
            "常用设备",
            ["Android手机", "iPhone (iOS)"],
            horizontal=True
        )
        device_map = {"Android手机": "android", "iPhone (iOS)": "ios"}

        activity = st.select_slider(
            "平台活跃度",
            options=["不活跃", "一般活跃", "非常活跃"],
            value="一般活跃"
        )
        activity_map = {"不活跃": "low", "一般活跃": "medium", "非常活跃": "high"}

        frequency = st.radio(
            "浏览此商品的频率",
            ["第一次看", "看过几次", "经常查看"],
            horizontal=True
        )
        freq_map = {"第一次看": "rare", "看过几次": "sometimes", "经常查看": "often"}

        has_coupon = st.checkbox("领过此商品优惠券")
        vip_level = st.selectbox("会员等级", ["非会员", "普通会员", "高级会员"])
        vip_map = {"非会员": "none", "普通会员": "medium", "高级会员": "high"}

    # 分隔线
    st.divider()

    # 计算按钮
    if st.button("🚀 计算我的个性化价格", use_container_width=True):
        # 构建用户画像
        user_profile = {
            "user_type": user_type_map[user_type],
            "spending_level": spending_map[spending_level],
            "device": device_map[device],
            "activity": activity_map[activity],
            "frequency": freq_map[frequency],
            "has_coupon": has_coupon,
            "vip_level": vip_map[vip_level]
        }

        # 计算价格
        final_price, adjustments = calculate_price(base_price, user_profile)

        # 显示结果卡片
        st.markdown('<h3 class="sub-header">💰 你的个性化价格</h3>', unsafe_allow_html=True)

        # 价格卡片
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.markdown(f"""
            <div class="price-card">
                <div>基础价格</div>
                <div class="price-number">¥{base_price}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_b:
            st.markdown(f"""
            <div class="price-card">
                <div>最终价格</div>
                <div class="price-number">¥{final_price}</div>
                <div>差异: ¥{final_price - base_price:+.1f}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_c:
            st.markdown(f"""
            <div class="price-card">
                <div>价格变动</div>
                <div class="price-number">{(final_price / base_price * 100 - 100):+.1f}%</div>
                <div>vs 基础价</div>
            </div>
            """, unsafe_allow_html=True)

        # 价格构成详情
        st.markdown("### 📊 价格构成分析")
        adjustments_df = pd.DataFrame(adjustments, columns=["影响因素", "调整幅度"])
        st.dataframe(adjustments_df, use_container_width=True, hide_index=True)

        # 经济学解释
        st.markdown("""
        <div class="info-box">
        <h4>💡 经济学原理解释</h4>
        <p><strong>1. 三级价格歧视：</strong>平台根据用户画像（新老、消费能力、设备等）将用户分组，实施不同的定价策略。</p>
        <p><strong>2. 消费者剩余提取：</strong>高消费能力、高活跃度的用户被认为价格敏感度低，平台通过涨价获取更多消费者剩余。</p>
        <p><strong>3. 行为定价：</strong>基于你的浏览历史、购买记录等行为数据，动态调整价格，利用"锚定效应"影响你的支付意愿。</p>
        <p><strong>4. 数据资产化：</strong>你的每一次点击、浏览都成为平台的"数据资产"，用于构建更精准的定价模型。</p>
        </div>
        """, unsafe_allow_html=True)

        # 建议
        st.markdown("""
        <div class="info-box">
        <h4>🔧 大学生应对策略</h4>
        <ol>
        <li><strong>清理浏览记录：</strong>定期清理缓存、使用无痕模式浏览商品</li>
        <li><strong>比价技巧：</strong>用不同设备（Android vs iOS）、不同账号（新账号）查看同一商品</li>
        <li><strong>购物时机：</strong>大促期间价格相对统一，差异较小</li>
        <li><strong>价格追踪工具：</strong>使用比价插件（如喵喵折、慢慢买）查看历史价格</li>
        <li><strong>理性消费：</strong>设置预算上限，避免被"个性化推荐"诱导过度消费</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)

    # 数据分析部分
    st.divider()
    st.markdown('<h3 class="sub-header">📈 群体价格分布模拟</h3>', unsafe_allow_html=True)

    # 生成模拟数据
    if st.button("生成50个模拟用户的价格分布"):
        df = generate_user_data(50)

        # 图表1: 价格分布直方图
        fig1 = px.histogram(
            df,
            x="看到的价格(元)",
            nbins=20,
            title="50个模拟用户看到的价格分布",
            color_discrete_sequence=['#4ECDC4']
        )
        fig1.update_layout(
            xaxis_title="价格 (元)",
            yaxis_title="用户数量",
            showlegend=False
        )
        st.plotly_chart(fig1, use_container_width=True)

        # 图表2: 价格 vs 用户特征
        fig2 = px.box(
            df,
            x="用户类型",
            y="看到的价格(元)",
            color="设备类型",
            title="不同用户类型和设备的价格差异"
        )
        st.plotly_chart(fig2, use_container_width=True)

        # 显示数据表
        st.markdown("### 📋 模拟用户数据（前10行）")
        st.dataframe(df.head(10), use_container_width=True)

        # 价格差异统计
        max_price = df["看到的价格(元)"].max()
        min_price = df["看到的价格(元)"].min()
        st.info(f"🔍 **模拟发现**：最高价 ¥{max_price} vs 最低价 ¥{min_price}，最大差异 **¥{max_price - min_price:.1f}**")


if __name__ == "__main__":
    main()