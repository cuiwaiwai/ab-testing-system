# -*- coding: utf-8 -*-
'''
A/B测试实验设计与分析系统 - 实验设计模块
功能：样本量计算、实验方案设计指导
'''

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ab_calculator import ABCalculator
from utils.plots_ab import ABPlotter


def render_experiment_design():
    '''渲染实验设计页面'''
    st.header('🎯 实验设计')

    st.markdown('''
    在进行A/B测试之前，首先需要确定合适的样本量。
    样本量过小可能无法检测到实际存在的效应，样本量过大则会浪费资源。
    本模块帮助您计算出所需的每组最小样本量。
    ''')

    # 指标类型选择
    metric_type = st.radio(
        '选择指标类型',
        ['比例型指标 (转化率/点击率等)', '均值型指标 (客单价/时长等)'],
        horizontal=True
    )

    st.divider()

    if metric_type == '比例型指标 (转化率/点击率等)':
        col1, col2 = st.columns(2)

        with col1:
            baseline_rate = st.slider(
                '对照组基准转化率',
                min_value=0.01, max_value=0.50, value=0.10, step=0.01,
                format='%.0f%%',
                help='当前版本(对照组)的转化率'
            )
            st.caption(f'当前: {baseline_rate*100:.0f}%')

            minimum_effect = st.slider(
                '最小可检测效应 (绝对提升)',
                min_value=0.005, max_value=0.10, value=0.02, step=0.005,
                format='%.1f%%',
                help='您希望检测到的最小转化率提升幅度'
            )
            st.caption(f'最小检测效应: {minimum_effect*100:.1f}个百分点')

            # 预期提升说明
            expected_rate = baseline_rate + minimum_effect
            relative_lift = (minimum_effect / baseline_rate * 100) if baseline_rate > 0 else 0
            st.info(f'实验组预期转化率: **{expected_rate*100:.1f}%** (相对提升 {relative_lift:.1f}%)')

        with col2:
            alpha = st.select_slider(
                '显著性水平 (α)',
                options=[0.01, 0.025, 0.05, 0.10],
                value=0.05,
                format_func=lambda x: f'{x:.3f}'
            )
            st.caption('通常取0.05 (即95%置信度)')

            power = st.select_slider(
                '统计功效 (1-β)',
                options=[0.70, 0.75, 0.80, 0.85, 0.90, 0.95],
                value=0.80,
                format_func=lambda x: f'{x:.0%}'
            )
            st.caption('通常取0.80 (即80%的概率检测到真实效应)')

            alternative = st.radio(
                '检验方向',
                ['two-sided', 'greater'],
                format_func=lambda x: '双侧检验' if x == 'two-sided' else '单侧检验(实验组>对照组)',
                horizontal=True
            )

        if st.button('📊 计算所需样本量', type='primary', use_container_width=True):
            result = ABCalculator.sample_size_proportion(
                baseline_rate=baseline_rate,
                minimum_effect=minimum_effect,
                alpha=alpha,
                power=power,
                alternative=alternative
            )

            st.divider()
            st.markdown('<div class="output-highlight"><div class="output-label">📊 样本量计算结果</div>', unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric('每组所需样本量', f'{result["每组样本量"]:,}')
            with col2:
                st.metric('总样本量', f'{result["总样本量"]:,}')
            with col3:
                st.metric('最小可检测效应', f'{result["最小可检测效应"]*100:.1f}%')

            st.markdown("</div>", unsafe_allow_html=True)
            # 显示详细信息
            with st.expander('📋 详细参数'):
                st.json({k: v for k, v in result.items() if k not in ['每组样本量', '总样本量', '最小可检测效应']})

            # 功效曲线
            st.subheader('📈 统计功效曲线')
            fig = ABPlotter.power_curve(
                baseline_rate=baseline_rate,
                max_effect=min(minimum_effect*3, 0.10),
                n_per_group=result['每组样本量'],
                alpha=alpha
            )
            st.plotly_chart(fig, use_container_width=True)

    else:
        col1, col2 = st.columns(2)

        with col1:
            baseline_mean = st.number_input('对照组基准均值', value=100.0, step=1.0)
            baseline_std = st.number_input('对照组标准差', value=20.0, step=1.0, min_value=0.1)
            minimum_effect = st.number_input(
                '最小可检测效应 (绝对差值)',
                value=5.0, step=0.5,
                help='希望检测到的最小均值差异'
            )
            effect_pct = (minimum_effect / baseline_mean * 100) if baseline_mean != 0 else 0
            st.caption(f'相对变化: {effect_pct:.1f}%')

        with col2:
            alpha = st.select_slider(
                '显著性水平 (α)',
                options=[0.01, 0.025, 0.05, 0.10],
                value=0.05,
                format_func=lambda x: f'{x:.3f}',
                key='alpha_mean'
            )
            power = st.select_slider(
                '统计功效 (1-β)',
                options=[0.70, 0.75, 0.80, 0.85, 0.90, 0.95],
                value=0.80,
                format_func=lambda x: f'{x:.0%}',
                key='power_mean'
            )
            alternative = st.radio(
                '检验方向',
                ['two-sided', 'greater'],
                format_func=lambda x: '双侧检验' if x == 'two-sided' else '单侧检验',
                horizontal=True,
                key='alt_mean'
            )

        if st.button('📊 计算所需样本量', type='primary', use_container_width=True, key='calc_mean'):
            result = ABCalculator.sample_size_mean(
                baseline_mean=baseline_mean,
                baseline_std=baseline_std,
                minimum_effect=minimum_effect,
                alpha=alpha,
                power=power,
                alternative=alternative
            )

            st.divider()
            st.markdown('<div class="output-highlight"><div class="output-label">📊 样本量计算结果</div>', unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric('每组所需样本量', f'{result["每组样本量"]:,}')
            with col2:
                st.metric('总样本量', f'{result["总样本量"]:,}')
            with col3:
                st.metric('效应量(Cohens d)', f'{result["效应量(Cohens d)"]:.3f}')

            st.caption(f'效应量解释: {ABCalculator._interpret_cohens_d(result["效应量(Cohens d)"])}')
            st.markdown("</div>", unsafe_allow_html=True)

    # 实验设计建议
    st.divider()
    st.subheader('💡 实验设计最佳实践')

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('''
        **实验前注意事项：**
        - ✅ 随机分配用户到各组，避免选择偏差
        - ✅ 确保只有目标变量发生变化（控制变量法）
        - ✅ 预先确定主要指标（避免数据窥探）
        - ✅ 设定合理的实验时长（至少1-2个完整业务周期）
        - ✅ 计算并满足最小样本量要求
        ''')
    with col2:
        st.markdown('''
        **常见陷阱：**
        - ❌ 过早查看结果（偷看问题/Peeking）
        - ❌ 同时运行多个AB测试相互干扰
        - ❌ 用显著性过滤多个指标（多重比较问题）
        - ❌ 将不显著的结果解释为"无差异"
        - ❌ 忽略新奇效应(Novelty Effect)
        ''')
