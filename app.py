"""
淘宝/京东个性化定价模拟器 (垂直流式布局 + 神秘模式)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random

# ==========================================
# 1. 全局配置与状态管理
# ==========================================
st.set_page_config(
    page_title="揭秘大数据杀熟：电商个性化定价模拟器",
    page_icon="🛒",
    layout="wide"  # 保持wide模式，虽然是上下结构，但内部可以用列来排版参数
)

# 初始化Session State：用于控制"价格是否揭晓"
if 'is_revealed' not in st.session_state:
    st.session_state.is_revealed = False

# 商品配置库
PRODUCTS = {
    "无线耳机": {"base": 599, "desc": "🎧 热门款真无线蓝牙耳机", "category": "数码"},
    "运动鞋": {"base": 199, "desc": "👟 新款缓震运动跑鞋", "category": "服饰"},
    "轻薄笔记本": {"base": 4999, "desc": "💻 最新款超薄笔记本电脑", "category": "数码"},
    "智能手表": {"base": 1299, "desc": "⌚️ 多功能健康监测智能手表", "category": "数码"},
    "美妆礼盒": {"base": 899, "desc": "💄 高端护肤品套装", "category": "美妆"}
}

# ==========================================
# 2. 样式优化 (CSS)
# ==========================================
st.markdown("""
<style>
    /* 核心变量 */
    :root {
        --primary: #4ECDC4;
        --secondary: #FF6B6B;
    }
    
    /* 步骤标题样式 */
    .step-header {
        background: linear-gradient(90deg, rgba(78, 205, 196, 0.1) 0%, rgba(255, 255, 255, 0) 100%);
        border-left: 5px solid var(--primary);
        padding: 10px 20px;
        margin-top: 20px;
        margin-bottom: 20px;
        border-radius: 0 10px 10px 0;
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--primary);
    }

    /* 价格卡片容器 */
    .metric-container {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        transition: transform 0.2s;
    }
    
    /* 价格数字 */
    .price-big {
        font-size: 3.5rem; /* 放大价格字体 */
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #FF6B6B, #FFD93D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* 模糊遮罩效果 (用于神秘模式) */
    .mystery-box {
        filter: blur(8px);
        user-select: none;
        opacity: 0.5;
        pointer-events: none;
    }
    
    /* 揭晓按钮区域 */
    .reveal-area {
        text-align: center;
        margin: 2rem 0;
    }
    
    /* 因素卡片样式 */
    .factor-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        border-left: 4px solid var(--primary);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .positive-impact {
        border-left-color: #2ecc71 !important;
        background: linear-gradient(135deg, rgba(46, 204, 113, 0.05), rgba(46, 204, 113, 0.02)) !important;
    }
    
    .negative-impact {
        border-left-color: #FF6B6B !important;
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.05), rgba(255, 107, 107, 0.02)) !important;
    }
    
    /* 消费选项样式 */
    .spending-option {
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 12px;
        margin: 5px 0;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .spending-option:hover {
        background-color: rgba(255, 255, 255, 0.05);
        border-color: var(--primary);
    }
    
    .spending-option.selected {
        background-color: rgba(78, 205, 196, 0.1);
        border-color: var(--primary);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 核心算法逻辑
# ==========================================

def calculate_price_logic(base_price, user_profile):
    """
    高级定价算法
    """
    # 因素分析数据容器
    factors = []

    current_price = base_price

    # 1. 用户身份 (新客 vs 老用户)
    if user_profile["user_type"] == "new":
        change = -0.15 * base_price
        factors.append({"name": "新客首单礼", "change": change, "type": "优惠"})
    elif user_profile["user_type"] == "loyal":
        change = 0.05 * base_price
        factors.append({"name": "老客隐形溢价", "change": change, "type": "加价"})
    else:
        change = 0
        factors.append({"name": "普通用户", "change": 0, "type": "中性"})

    current_price += change

    # 2. 设备与消费能力 (交互效应)
    spending_score = user_profile["spending_level_norm"]
    device = user_profile["device"]

    device_markup = 0
    # 苹果(iPhone)/鸿蒙统一处理
    if device == "ios":
        # iOS/鸿蒙基础溢价
        markup_pct = 0.05
        # 高消费 + iOS/鸿蒙 = 协同溢价
        if spending_score > 80:
            markup_pct = 0.12
            factors.append({"name": "高端机型+高消费", "change": base_price * markup_pct, "type": "加价"})
        else:
            factors.append({"name": "苹果/鸿蒙设备差异", "change": base_price * markup_pct, "type": "加价"})
        device_markup = base_price * markup_pct
    else:
        # 安卓低消费保护
        if base_price > 500 and spending_score < 40:
            device_markup = -base_price * 0.05
            factors.append({"name": "价格敏感度保护", "change": device_markup, "type": "优惠"})
        else:
            factors.append({"name": "设备无差异", "change": 0, "type": "中性"})

    current_price += device_markup

    # 3. 活跃度 (粘性) - 修改：区分不同活跃度
    activity_score = user_profile["activity_score"]
    act_change = 0

    # 重新设计活跃度影响逻辑
    if activity_score >= 75:
        act_change = base_price * 0.02  # 高粘性溢价
        factors.append({"name": "高粘性溢价", "change": act_change, "type": "加价"})
    elif activity_score >= 25:
        act_change = base_price * 0.00  # 维持
        factors.append({"name": "固定查看意向溢价", "change": act_change, "type": "中性"})
    else:
        act_change = -base_price * 0.03  # 给予优惠以吸引购买
        factors.append({"name": "促活优惠", "change": act_change, "type": "优惠"})

    current_price += act_change

    # 4. 浏览频率 - 修改：首次浏览提供30元折扣
    freq_change = 0
    if user_profile["frequency"] == "often":
        freq_change = base_price * 0.08
        factors.append({"name": "急需(高频浏览)", "change": freq_change, "type": "加价"})
    elif user_profile["frequency"] == "rare":
        freq_change = -30  # 首次浏览提供30元固定折扣
        factors.append({"name": "首次浏览刺激消费", "change": freq_change, "type": "优惠"})
    else:  # sometimes
        factors.append({"name": "正常浏览频率", "change": 0, "type": "中性"})

    current_price += freq_change

    # 5. 退货量影响 - 修改：根据购买时期和退货率决定优惠
    return_change = 0
    purchase_period = user_profile["purchase_period"]  # 新增：平时 or 特殊时期
    return_rate = user_profile["return_rate"]
    
    # 特殊时期购买逻辑
    if purchase_period == "special":
        if return_rate == "high":
            # 频繁退货，不享受特殊时期优惠
            factors.append({"name": "特殊时期但频繁退货", "change": 0, "type": "中性"})
        else:
            # 一般或不退货，享受10%折扣
            return_change = -base_price * 0.10  # 改为10%折扣
            factors.append({"name": "大促期间折扣(10%)", "change": return_change, "type": "优惠"})
    else:
        # 平时购买逻辑
        if return_rate == "low":
            # 从不退货额外5元优惠
            return_change = -5
            factors.append({"name": "从不退货额外优惠", "change": return_change, "type": "优惠"})
        elif return_rate == "medium":
            factors.append({"name": "一般退货率", "change": 0, "type": "中性"})
        else:
            # 高退货率在平时无影响
            factors.append({"name": "高退货率", "change": 0, "type": "中性"})

    current_price += return_change

    # 6. 历史购买类型与当前商品差异 (新增)
    history_categories = user_profile["history_categories"]
    current_category = user_profile["current_category"]
    
    if history_categories:  # 如果用户选择了历史购买类型
        if current_category not in history_categories:
            # 当前商品类型不在历史购买类型中，给予小幅度优惠
            category_change = -20
            factors.append({"name": "尝试新品类优惠", "change": category_change, "type": "优惠"})
            current_price += category_change
        else:
            # 相同或相似，无影响
            factors.append({"name": "历史购买同类商品", "change": 0, "type": "中性"})
    else:
        # 用户没有选择任何历史购买类型，视为无历史数据，无影响
        factors.append({"name": "无历史购买记录", "change": 0, "type": "中性"})

    # 7. 购物车中是否有相同/相似产品 (新增)
    if user_profile.get("has_similar_in_cart", False):
        cart_change = 5  # 如果有相似产品，价格+5元
        current_price += cart_change
        factors.append({"name": "购物车有相似产品", "change": cart_change, "type": "加价"})

    return round(current_price, 2), factors

def normalize_spending(amount):
    if amount <= 100: return 10
    if amount <= 500: return 30
    if amount <= 1000: return 50
    if amount <= 3000: return 75
    return 90

def map_activity_to_score(activity):
    activity_map = {
        "每天都会看看价格": 80,
        "一周只看两三回": 50,
        "必须购买时再使用": 20
    }
    return activity_map.get(activity, 50)

def map_return_rate(return_option):
    return_map = {
        "没有/几乎不退货": "low",
        "看商品质量偶尔退货": "medium",
        "商品不合意或只留下合适的便退货": "high"
    }
    return return_map.get(return_option, "medium")

def get_spending_value(spending_range):
    """将消费区间转换为具体数值（用于用户选择）"""
    spending_map = {
        "0-100元": 50,
        "100-500元": 300,
        "500-1000元": 750,
        "1000-3000元": 2000,
        "3000元以上": 4000
    }
    return spending_map.get(spending_range, 1000)

def get_random_spending_value(spending_range):
    """将消费区间转换为随机数值（用于群体模拟）"""
    if spending_range == "0-100元":
        return random.randint(0, 100)
    elif spending_range == "100-500元":
        return random.randint(100, 500)
    elif spending_range == "500-1000元":
        return random.randint(500, 1000)
    elif spending_range == "1000-3000元":
        return random.randint(1000, 3000)
    elif spending_range == "3000元以上":
        return random.randint(3000, 5000)  # 假设上限为5000
    else:
        return 1000

# ==========================================
# 4. 可视化组件
# ==========================================

def create_factors_display(factors):
    """创建因素影响展示"""
    html = ""
    for factor in factors:
        change = factor["change"]
        factor_class = "positive-impact" if change < 0 else "negative-impact" if change > 0 else ""

        if change == 0:
            change_text = "无影响"
            change_display = "0"
        else:
            sign = "+" if change > 0 else ""
            change_text = f"{sign}{change:.0f}元"
            change_display = f"{sign}{change:.0f}"

        html += f"""
        <div class="factor-card {factor_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{factor['name']}</strong>
                    <div style="font-size: 0.9em; color: #888; margin-top: 4px;">{factor['type']}</div>
                </div>
                <div style="font-size: 1.2em; font-weight: bold; color: {'#2ecc71' if change < 0 else '#FF6B6B' if change > 0 else '#888'}">
                    {change_display}
                </div>
            </div>
        </div>
        """
    return html

# ==========================================
# 5. 主程序 UI (上中下结构)
# ==========================================

def main():
    st.markdown('<h1 style="text-align:center; margin-bottom: 2rem;">🕵️‍♂️ 电商个性化定价模拟器</h1>', unsafe_allow_html=True)

    # -------------------------------------------------------
    # 步骤 1: 设置用户特征 (Top)
    # -------------------------------------------------------
    st.markdown('<div class="step-header">👤 第一步：大数据如何标记你？</div>', unsafe_allow_html=True)
    st.caption("调整下方的选项，看看算法如何给你打标签。")

    # 使用三行布局，每行3列，整齐排列
    row1_c1, row1_c2, row1_c3 = st.columns(3)

    with row1_c1:
        st.markdown("**1. 你的用户身份？**")
        user_type = st.selectbox(
            "label_1",
            ["我是新用户！", "我是普通用户;)", "我是老用户☝🏼"],
            index=1,
            label_visibility="collapsed"
        )
        type_map = {"我是新用户！": "new", "我是普通用户;)": "regular", "我是老用户☝🏼": "loyal"}

    with row1_c2:
        st.markdown("**2. 你在淘宝APP 每月的消费？**")
        spending_range = st.selectbox(
            "label_2",
            ["0-100元", "100-500元", "500-1000元", "1000-3000元", "3000元以上"],
            index=2,
            label_visibility="collapsed"
        )
        monthly_spend = get_spending_value(spending_range)
        st.caption(f"¥{monthly_spend} (中位数)")

    with row1_c3:
        st.markdown("**3. 你使用的设备？**")
        device_display = st.radio(
            "label_3",
            ["安卓(Android)", "苹果(iPhone)/鸿蒙"],
            horizontal=True,
            label_visibility="collapsed"
        )
        device_val = "ios" if "苹果" in device_display else "android"

    st.markdown("---") # 分割线

    row2_c1, row2_c2, row2_c3 = st.columns(3)

    with row2_c1:
        st.markdown("**4. 你在淘宝的活跃度如何**")
        activity_level = st.selectbox(
            "label_4",
            ["每天都会看看价格", "一周只看两三回", "必须购买时再使用"],
            index=1,
            label_visibility="collapsed"
        )
        activity_score = map_activity_to_score(activity_level)
        st.caption(f"活跃分: {activity_score}")

    with row2_c2:
        st.markdown("**5. 你浏览该商品频率多高**")
        view_freq = st.selectbox(
            "label_5",
            ["第一次点开", "偶尔看看", "反复查看(急需)"],
            index=1,
            label_visibility="collapsed"
        )
        freq_map = {"第一次点开": "rare", "偶尔看看": "sometimes", "反复查看(急需)": "often"}

    with row2_c3:
        st.markdown("**6. 你有退货的习惯吗**")
        return_option = st.selectbox(
            "label_6",
            ["没有/几乎不退货", "看商品质量偶尔退货", "商品不合意或只留下合适的便退货"],
            index=1,
            label_visibility="collapsed"
        )
        return_rate = map_return_rate(return_option)

    st.markdown("---") # 分割线

    row3_c1, row3_c2, row3_c3 = st.columns(3)

    with row3_c1:
        st.markdown("**7. 平时与特殊时期购买**")
        purchase_period = st.selectbox(
            "label_7",
            ["平时购买", "双11/双12/618等大促期间购买"],
            index=0,
            label_visibility="collapsed"
        )
        # 映射购买时期
        purchase_period_map = {
            "平时购买": "normal",
            "双11/双12/618等大促期间购买": "special"
        }

    with row3_c2:
        st.markdown("**8. 购物车中有相似商品吗**")
        has_similar = st.selectbox(
            "label_8",
            ["否", "是"],
            index=0,
            help="购物车中是否有相同或相似产品",
            label_visibility="collapsed"
        )
        has_similar_in_cart = (has_similar == "是")

    with row3_c3:
        st.markdown("**9. 你之前购买过哪些类型的商品？**")
        # 使用多选组件，允许用户选择多个类型
        history_category_options = st.multiselect(
            "label_9",
            ["服装服饰类", "食品（水果蔬菜等）", "电子产品（电脑、手机、耳机等）", "美妆护肤类", "家居日用类", "其他"],
            default=["服装服饰类"],  # 默认选中一项
            help="可多选，之前购买过的商品类型",
            label_visibility="collapsed"
        )
        # 将选项映射为类别（与商品配置库的category对应）
        history_category_map = {
            "服装服饰类": "服饰",
            "食品（水果蔬菜等）": "食品",
            "电子产品（电脑、手机、耳机等）": "数码",
            "美妆护肤类": "美妆",
            "家居日用类": "家居",
            "其他": "其他"
        }
        # 将用户选择转换为对应的类别列表
        history_categories = [history_category_map[opt] for opt in history_category_options]

    # -------------------------------------------------------
    # 步骤 2: 选择商品 (Middle)
    # -------------------------------------------------------
    st.markdown('<div class="step-header">🛍️ 第二步：选择你想购买的商品</div>', unsafe_allow_html=True)

    # 使用列来限制选择框的宽度，不让它占满全屏
    c_p1, c_p2, c_p3 = st.columns([1, 2, 1])
    with c_p2:
        selected_product_name = st.selectbox(
            "点击下拉框选择商品",
            list(PRODUCTS.keys()),
            label_visibility="collapsed"
        )
        product_info = PRODUCTS[selected_product_name]

    # -------------------------------------------------------
    # 步骤 3: 揭晓价格 (Bottom)
    # -------------------------------------------------------
    st.markdown('<div class="step-header">💰 第三步：查看你的专属价格</div>', unsafe_allow_html=True)

    # 无论是否揭晓，先在后台计算好价格
    profile = {
        "user_type": type_map[user_type],
        "spending_level_norm": normalize_spending(monthly_spend),
        "device": device_val,
        "activity_score": activity_score,
        "frequency": freq_map[view_freq],
        "return_rate": return_rate,
        "purchase_period": purchase_period_map[purchase_period],
        "history_categories": history_categories,  # 修改：改为列表
        "current_category": product_info['category'],
        "has_similar_in_cart": has_similar_in_cart
    }
    base_price = product_info['base']
    final_price, factors = calculate_price_logic(base_price, profile)

    # 逻辑分支：显示按钮 还是 显示结果
    result_container = st.container()

    with result_container:
        if not st.session_state.is_revealed:
            # === 状态 A: 神秘模式 (未揭晓) ===
            st.markdown("""
            <div style="text-align: center; padding: 40px; background: rgba(255,255,255,0.05); border-radius: 10px;">
                <div style="font-size: 5rem;">🫣</div>
                <h3>价格已生成，但被隐藏了</h3>
                <p style="color: #888;">算法已经计算完毕，你敢看结果吗？</p>
            </div>
            """, unsafe_allow_html=True)

            # 巨大的揭晓按钮
            col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
            with col_b2:
                if st.button("🚀 点击揭晓我的个性化价格", use_container_width=True, type="primary"):
                    st.session_state.is_revealed = True
                    st.rerun() # 立即刷新页面以显示结果

        else:
            # === 状态 B: 结果展示模式 (已揭晓) ===
            # 顶部操作栏：隐藏按钮
            c_hide_1, c_hide_2 = st.columns([8, 2])
            with c_hide_2:
                if st.button("🔒 隐藏价格 (重置)", use_container_width=True):
                    st.session_state.is_revealed = False
                    st.rerun()

            # 价格核心展示区
            diff = final_price - base_price
            diff_pct = (diff / base_price) * 100

            c_res_1, c_res_2, c_res_3 = st.columns([1, 1, 1])

            with c_res_1:
                st.markdown(f"""
                <div class="metric-container">
                    <div style="color:#888;">平台基准价</div>
                    <h2 style="color:#888;">¥{base_price}</h2>
                    <div style="font-size: 0.9em; color: #888;">{product_info['desc']}</div>
                </div>
                """, unsafe_allow_html=True)

            with c_res_2:
                # 动画效果提示
                st.markdown(f"""
                <div class="metric-container" style="border: 2px solid var(--primary); box-shadow: 0 0 15px rgba(78, 205, 196, 0.3);">
                    <div style="color:var(--primary); font-weight:bold;">你的专属价</div>
                    <div class="price-big">¥{final_price}</div>
                    <div style="color:#888; margin-top: 10px;">基于你的用户画像</div>
                </div>
                """, unsafe_allow_html=True)

            with c_res_3:
                color = "#FF6B6B" if diff > 0 else "#2ecc71"
                sign = "+" if diff > 0 else ""
                st.markdown(f"""
                <div class="metric-container">
                    <div style="color:#888;">差异幅度</div>
                    <h2 style="color:{color};">{sign}{diff:.1f}</h2>
                    <div style="color:{color};">{sign}{diff_pct:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)

            # 影响因素分析
            st.markdown("### 📊 价格影响因素分析")
            st.markdown("以下是算法根据你的用户特征做出的价格调整：")

            # 创建因素展示
            factors_html = create_factors_display(factors)
            st.markdown(factors_html, unsafe_allow_html=True)

            # 总结说明
            if diff > 0:
                st.warning(f"💡 **分析结果**：你的用户画像显示你是高价值用户，算法判断你愿意支付更高价格，因此价格上浮{diff_pct:.1f}%")
            elif diff < 0:
                st.success(f"💡 **分析结果**：你的用户画像显示你是价格敏感型用户，算法为了吸引你购买，给予了{abs(diff_pct):.1f}%的优惠")
            else:
                st.info(f"💡 **分析结果**：你的用户画像较为均衡，算法给予你基准价格")

            st.success("💡 **提示**：保持此区域打开，现在去上方调整「月消费」或「设备」，价格会实时跳动！")

    # -------------------------------------------------------
    # 底部：群体模拟 (可选)
    # -------------------------------------------------------
    st.divider()
    with st.expander("📊 查看大数据群体模拟 (100个样本)"):
        if st.button("生成随机群体数据"):
            users = []
            for i in range(100):
                u_type = np.random.choice(["new", "regular", "loyal"], p=[0.2, 0.6, 0.2])
                u_spend_range = np.random.choice(["0-100元", "100-500元", "500-1000元", "1000-3000元", "3000元以上"])
                # 使用随机值而不是固定值
                u_spend = get_random_spending_value(u_spend_range)
                u_device = np.random.choice(["android", "ios"], p=[0.6, 0.4])
                u_activity = np.random.choice([90, 70, 40, 10], p=[0.2, 0.3, 0.3, 0.2])
                u_return = np.random.choice(["low", "medium", "high"], p=[0.3, 0.5, 0.2])
                u_period = np.random.choice(["normal", "special"], p=[0.7, 0.3])
                
                # 随机选择历史购买类型（多个）
                all_categories = ["服饰", "食品", "数码", "美妆", "家居", "其他"]
                num_categories = np.random.randint(0, 4)  # 0-3个历史购买类型
                u_history_cats = np.random.choice(all_categories, size=num_categories, replace=False).tolist()
                
                u_similar = np.random.choice([True, False], p=[0.3, 0.7])

                # 简化模拟计算
                sim_profile = {
                    "user_type": u_type,
                    "spending_level_norm": normalize_spending(u_spend),
                    "device": u_device,
                    "activity_score": u_activity,
                    "frequency": "sometimes",
                    "return_rate": u_return,
                    "purchase_period": u_period,
                    "history_categories": u_history_cats,
                    "current_category": product_info['category'],
                    "has_similar_in_cart": u_similar
                }
                p, _ = calculate_price_logic(base_price, sim_profile)
                users.append({
                    "价格": p,
                    "设备": u_device,
                    "消费区间": u_spend_range,
                    "消费值": u_spend,
                    "退货率": u_return,
                    "购买时期": u_period,
                    "历史品类数": len(u_history_cats),
                    "购物车相似": u_similar
                })

            df_sim = pd.DataFrame(users)
            # 修复报错：移除了 trendline="ols"
            fig_sim = px.scatter(
                df_sim, x="消费值", y="价格", color="设备",
                title="消费能力 vs 价格分布 (100个随机用户样本)",
                hover_data=["退货率", "消费区间", "购买时期", "历史品类数", "购物车相似"],
                labels={"消费值": "月消费金额 (元)", "价格": "个性化价格 (元)"}
            )

            # 更新图表布局
            fig_sim.update_layout(
                xaxis_title="月消费金额 (元)",
                yaxis_title="个性化价格 (元)",
                hovermode="closest"
            )

            st.plotly_chart(fig_sim, use_container_width=True)

            # 显示统计信息
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            with col_stats1:
                avg_price = df_sim["价格"].mean()
                st.metric("平均价格", f"¥{avg_price:.2f}")

            with col_stats2:
                price_std = df_sim["价格"].std()
                st.metric("价格标准差", f"¥{price_std:.2f}")

            with col_stats3:
                price_range = df_sim["价格"].max() - df_sim["价格"].min()
                st.metric("价格范围", f"¥{price_range:.2f}")

if __name__ == "__main__":
    main()
