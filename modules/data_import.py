# -*- coding: utf-8 -*-
'''
A/B测试实验设计与分析系统 - 数据导入模块
'''

import streamlit as st
import pandas as pd
import numpy as np
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ab_calculator import ABCalculator


def render_data_import():
    '''渲染数据导入页面'''
    st.header('📥 数据导入')

    if 'ab_data' not in st.session_state:
        st.session_state.ab_data = None

    tab1, tab2, tab3 = st.tabs(['📂 上传数据', '🎲 生成示例', '✏️ 手动输入'])

    with tab1:
        st.subheader('上传AB测试数据文件')
        uploaded_file = st.file_uploader(
            '选择数据文件 (需包含分组列)',
            type=['csv', 'xlsx', 'xls'],
            help='数据文件应包含分组标识列(如group列，值为A和B)'
        )

        if uploaded_file is not None:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            try:
                if uploaded_file.name.endswith('.csv'):
                    try:
                        df = pd.read_csv(tmp_path, encoding='utf-8')
                    except:
                        df = pd.read_csv(tmp_path, encoding='gbk')
                else:
                    df = pd.read_excel(tmp_path)

                st.session_state.ab_data = df
                st.success(f'成功读取 {df.shape[0]} 行 × {df.shape[1]} 列')

                st.subheader('📋 数据预览')
                st.dataframe(df.head(20), use_container_width=True)

                # 列信息
                col_types = {}
                for col in df.columns:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        if df[col].nunique() <= 10:
                            col_types[col] = '数值型(可能是分组列)'
                        else:
                            col_types[col] = '数值型(连续)'
                    else:
                        col_types[col] = '文本型/分类型'

                st.subheader('🔍 列信息')
                st.dataframe(
                    pd.DataFrame({'列名': col_types.keys(), '类型': col_types.values()}),
                    use_container_width=True,
                    hide_index=True
                )

            except Exception as e:
                st.error(f'读取失败: {e}')
            finally:
                try:
                    os.unlink(tmp_path)
                except:
                    pass

    with tab2:
        st.subheader('生成示例AB测试数据')

        col1, col2 = st.columns(2)
        with col1:
            n_a = st.number_input('对照组样本量', 100, 10000, 1000, 100)
            n_b = st.number_input('实验组样本量', 100, 10000, 1000, 100)
        with col2:
            effect_size = st.slider('效应量 (Cohens d)', 0.0, 1.0, 0.3, 0.05)
            st.caption(f'当前: d={effect_size:.2f} ({ABCalculator._interpret_cohens_d(effect_size)})')

        if st.button('🎲 生成示例数据', type='primary', use_container_width=True):
            df = ABCalculator.generate_sample_ab_data(
                n_a=n_a, n_b=n_b, effect_size=effect_size
            )
            st.session_state.ab_data = df
            st.success(f'已生成 {df.shape[0]} 条AB测试数据')

            st.subheader('📋 数据预览')
            st.dataframe(df.head(20), use_container_width=True)

            # 分组统计
            st.subheader('📊 分组概况')
            group_stats = df.groupby('group').agg({
                'visit_duration': ['count', 'mean', 'std'],
                'page_views': ['mean'],
                'purchase_amount': ['mean'],
                'converted': ['mean']
            }).round(3)
            st.dataframe(group_stats, use_container_width=True)

    with tab3:
        st.subheader('手动输入汇总数据')
        metric_type = st.radio('指标类型', ['比例型(转化率)', '均值型(连续指标)'], horizontal=True)

        if metric_type == '比例型(转化率)':
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('**对照组 (A)**')
                n_a = st.number_input('对照组样本量', 1, 1000000, 1000, key='man_n_a')
                succ_a = st.number_input('对照组成功数', 0, n_a, int(n_a*0.1), key='man_succ_a')
                st.caption(f'转化率: {succ_a/n_a*100:.2f}%' if n_a > 0 else '')

            with col2:
                st.markdown('**实验组 (B)**')
                n_b = st.number_input('实验组样本量', 1, 1000000, 1000, key='man_n_b')
                succ_b = st.number_input('实验组成功数', 0, n_b, int(n_b*0.12), key='man_succ_b')
                st.caption(f'转化率: {succ_b/n_b*100:.2f}%' if n_b > 0 else '')

            alpha = st.select_slider('显著性水平 α', [0.01, 0.025, 0.05, 0.10], 0.05, key='man_alpha')

            if n_a > 0 and n_b > 0:
                result = ABCalculator.proportions_z_test(
                    succ_a, n_a, succ_b, n_b, alpha=alpha
                )
                st.divider()
                st.subheader('📊 比例Z检验结果')
                st.metric('p值', f'{result["p值"]:.6f}')
                ab_result = '✅ 显著' if result['是否显著'] == '是' else '❌ 不显著'
                st.metric('结论', f'{ab_result} ({result["结论"]})')

        else:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('**对照组 (A)**')
                n_a = st.number_input('样本量', 1, 100000, 30, key='mma_n')
                mean_a = st.number_input('均值', value=100.0, key='mma_mean')
                std_a = st.number_input('标准差', value=20.0, min_value=0.01, key='mma_std')
            with col2:
                st.markdown('**实验组 (B)**')
                n_b = st.number_input('样本量', 1, 100000, 30, key='mmb_n')
                mean_b = st.number_input('均值', value=105.0, key='mmb_mean')
                std_b = st.number_input('标准差', value=22.0, min_value=0.01, key='mmb_std')

            alpha = st.select_slider('显著性水平 α', [0.01, 0.025, 0.05, 0.10], 0.05, key='mma_alpha')

            # 使用汇总数据进行t检验
            pooled_se = np.sqrt(std_a**2/n_a + std_b**2/n_b)
            from scipy import stats as scipy_stats
            t_stat = (mean_b - mean_a) / pooled_se if pooled_se > 0 else 0
            # Welch df
            v_num = (std_a**2/n_a + std_b**2/n_b)**2
            v_den = ((std_a**2/n_a)**2/(n_a-1) + (std_b**2/n_b)**2/(n_b-1))
            df = v_num/v_den if v_den > 0 else n_a+n_b-2
            p_value = 2 * scipy_stats.t.sf(abs(t_stat), df)

            st.divider()
            st.subheader('📊 t检验结果')
            st.metric('t统计量', f'{t_stat:.4f}')
            st.metric('p值', f'{p_value:.6f}')
            st.metric('结论', f'{"✅ 显著" if p_value < alpha else "❌ 不显著"} (p{"<" if p_value<alpha else "≥"} {alpha})')
