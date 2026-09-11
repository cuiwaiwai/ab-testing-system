# -*- coding: utf-8 -*-
'''
A/B测试实验设计与分析系统 - 假设检验模块
功能：t检验、比例Z检验、卡方检验、Mann-Whitney U检验
'''

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys, os
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ab_calculator import ABCalculator
from utils.plots_ab import ABPlotter
from utils.font_setup import setup_chinese_font

setup_chinese_font()


def render_hypothesis_test():
    '''渲染假设检验页面'''
    st.header('🧪 假设检验')

    if st.session_state.ab_data is None:
        st.warning('⚠️ 请先在「数据导入」页面加载数据')
        return

    df = st.session_state.ab_data

    # 分组列选择
    possible_group_cols = [c for c in df.columns if df[c].nunique() == 2]
    if not possible_group_cols:
        st.error('未检测到恰好2类的分组列')
        return

    group_col = st.selectbox('选择分组列', possible_group_cols, key='ht_group')
    groups = sorted(df[group_col].unique())

    df_a = df[df[group_col] == groups[0]]
    df_b = df[df[group_col] == groups[1]]

    st.info(f'分组: **{groups[0]}** (n={len(df_a)}) vs **{groups[1]}** (n={len(df_b)})')

    # 检验类型
    test_type = st.radio(
        '选择检验方法',
        ['📊 两样本t检验 (连续指标)', '📈 比例Z检验 (转化率/率)', '📋 卡方检验 (分类分布)', '📉 Mann-Whitney U检验 (非参数)'],
        horizontal=True
    )

    alpha = st.select_slider('显著性水平 (α)', [0.01, 0.025, 0.05, 0.10], 0.05)

    st.divider()

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c != group_col]

    if test_type == '📊 两样本t检验 (连续指标)':
        if not numeric_cols:
            st.warning('无可用数值型指标')
            return

        metric = st.selectbox('选择分析指标', numeric_cols, key='ttest_metric')
        alternative = st.radio('备择假设', ['two-sided', 'greater', 'less'],
                              format_func=lambda x: {'two-sided': '双侧: B ≠ A', 'greater': '单侧: B > A', 'less': '单侧: B < A'}[x],
                              horizontal=True)

        # 正态性检验
        st.subheader('🔬 正态性检验')
        norm_a = ABCalculator.check_normality(df_a[metric].dropna().values)
        norm_b = ABCalculator.check_normality(df_b[metric].dropna().values)

        col1, col2 = st.columns(2)
        with col1:
            st.metric(f'{groups[0]} 正态性', '✅ 正态' if norm_a['is_normal'] else '⚠️ 非正态')
            st.caption(f'{norm_a["method"]} p={norm_a["p_value"]:.4f}')
        with col2:
            st.metric(f'{groups[1]} 正态性', '✅ 正态' if norm_b['is_normal'] else '⚠️ 非正态')
            st.caption(f'{norm_b["method"]} p={norm_b["p_value"]:.4f}')

        if not norm_a['is_normal'] or not norm_b['is_normal']:
            st.warning('⚠️ 数据不完全满足正态性假设，建议使用 Mann-Whitney U 检验')

        # 执行t检验
        result = ABCalculator.two_sample_t_test(
            df_a[metric].values, df_b[metric].values,
            alpha=alpha, alternative=alternative
        )

        st.subheader('📊 t检验结果')
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric('t统计量', f'{result["t统计量"]:.4f}')
        with col2:
            st.metric('p值', f'{result["p值"]:.6f}')
        with col3:
            sig_text = '✅ 显著' if result['是否显著'] == '是' else '❌ 不显著'
            st.metric('结论', sig_text)

        st.json({k: v for k, v in result.items() if k not in ['t统计量', 'p值', '是否显著', '结论']})

        # 可视化
        st.subheader('📈 结果可视化')
        col1, col2 = st.columns(2)
        with col1:
            # 均值比较
            fig_bar = ABPlotter.mean_comparison_bar(
                result['对照组均值'], result['实验组均值'],
                result['对照组标准差'], result['实验组标准差'],
                label_a=groups[0], label_b=groups[1],
                metric_name=metric,
                ci_a=ABCalculator.calculate_confidence_interval(df_a[metric].dropna().values),
                ci_b=ABCalculator.calculate_confidence_interval(df_b[metric].dropna().values),
            )
            st.pyplot(fig_bar)
            plt.close()

        with col2:
            # 置信区间图
            ci_lower, ci_upper = result['置信区间']
            if ci_lower == float('-inf'):
                ci_lower = result['均值差异(B-A)'] - 3 * np.sqrt(result['对照组标准差']**2/result['对照组样本量'] + result['实验组标准差']**2/result['实验组样本量'])
            if ci_upper == float('inf'):
                ci_upper = result['均值差异(B-A)'] + 3 * np.sqrt(result['对照组标准差']**2/result['对照组样本量'] + result['实验组标准差']**2/result['实验组样本量'])

            fig_ci = ABPlotter.confidence_interval_plot(
                result['均值差异(B-A)'], ci_lower, ci_upper, alpha
            )
            st.pyplot(fig_ci)
            plt.close()

    elif test_type == '📈 比例Z检验 (转化率/率)':
        conversion_cols = [c for c in numeric_cols if set(df[c].dropna().unique()).issubset({0, 1})]

        if conversion_cols:
            metric = st.selectbox('选择二元指标', conversion_cols, key='ztest_metric')
            n_a = len(df_a)
            n_b = len(df_b)
            succ_a = int(df_a[metric].sum())
            succ_b = int(df_b[metric].sum())
        else:
            st.info('未检测到0/1二元指标，请手动输入数据')
            col1, col2 = st.columns(2)
            with col1:
                n_a = st.number_input(f'{groups[0]} 总样本', 1, 1000000, 1000)
                succ_a = st.number_input(f'{groups[0]} 成功数', 0, n_a, 100)
            with col2:
                n_b = st.number_input(f'{groups[1]} 总样本', 1, 1000000, 1000)
                succ_b = st.number_input(f'{groups[1]} 成功数', 0, n_b, 120)
            metric = '转化率'

        if st.button('🔬 执行比例Z检验', type='primary'):
            result = ABCalculator.proportions_z_test(succ_a, n_a, succ_b, n_b, alpha=alpha)

            st.subheader('📊 比例Z检验结果')
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric('Z统计量', f'{result["Z统计量"]:.4f}')
            with col2:
                st.metric('p值', f'{result["p值"]:.6f}')
            with col3:
                st.metric('结论', '✅ 显著' if result['是否显著'] == '是' else '❌ 不显著')

            st.json({k: v for k, v in result.items() if k not in ['Z统计量', 'p值', '是否显著', '结论']})

            # 转化率对比图
            rate_a = succ_a / n_a if n_a > 0 else 0
            rate_b = succ_b / n_b if n_b > 0 else 0
            fig = ABPlotter.conversion_rate_comparison(rate_a, rate_b, n_a, n_b,
                                                      label_a=groups[0], label_b=groups[1])
            st.pyplot(fig)
            plt.close()

    elif test_type == '📋 卡方检验 (分类分布)':
        cat_cols = [c for c in df.columns if c not in numeric_cols and c != group_col]

        if not cat_cols:
            st.warning('无可用的分类变量')
            return

        cat_metric = st.selectbox('选择分类变量', cat_cols, key='chi_metric')

        # 构建列联表
        ct = pd.crosstab(df[group_col], df[cat_metric])

        st.subheader('📋 列联表')
        st.dataframe(ct, use_container_width=True)

        if st.button('🔬 执行卡方检验', type='primary'):
            result = ABCalculator.chi_square_test(ct.values, alpha=alpha)

            st.subheader('📊 卡方检验结果')
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric('χ²统计量', f'{result["χ²统计量"]:.4f}')
            with col2:
                st.metric('p值', f'{result["p值"]:.6f}')
            with col3:
                st.metric('结论', '✅ 分布有差异' if result['是否显著'] == '是' else '❌ 分布无差异')

            st.json({k: v for k, v in result.items() if k not in ['χ²统计量', 'p值', '是否显著', '结论']})

    elif test_type == '📉 Mann-Whitney U检验 (非参数)':
        if not numeric_cols:
            st.warning('无可用数值型指标')
            return

        metric = st.selectbox('选择分析指标', numeric_cols, key='mw_metric')
        alternative = st.radio('备择假设', ['two-sided', 'greater', 'less'],
                              format_func=lambda x: {'two-sided': '双侧', 'greater': '单侧B>A', 'less': '单侧B<A'}[x],
                              horizontal=True, key='mw_alt')

        if st.button('🔬 执行Mann-Whitney U检验', type='primary'):
            result = ABCalculator.mann_whitney_u_test(
                df_a[metric].values, df_b[metric].values,
                alpha=alpha, alternative=alternative
            )

            st.subheader('📊 Mann-Whitney U检验结果')
            col1, col2 = st.columns(2)
            with col1:
                st.metric('p值', f'{result["p值"]:.6f}')
            with col2:
                st.metric('结论', '✅ 显著' if result['是否显著'] == '是' else '❌ 不显著')

            st.json({k: v for k, v in result.items() if k not in ['p值', '是否显著', '结论']})
