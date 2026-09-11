# -*- coding: utf-8 -*-
'''
A/B测试实验设计与分析系统 - 决策建议模块
'''

import streamlit as st
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def render_decision():
    '''渲染决策建议页面'''
    st.header('📋 决策建议')

    st.markdown('''
    根据A/B测试结果，本模块提供科学的决策建议框架，
    帮助您从统计显著性和业务意义两个维度做出判断。
    ''')

    st.subheader('📊 决策矩阵')

    # 显著性选择
    col1, col2 = st.columns(2)
    with col1:
        is_significant = st.radio('统计显著性', ['✅ 显著 (p < α)', '❌ 不显著 (p ≥ α)'])
    with col2:
        effect_magnitude = st.radio('效应大小 (业务意义)', ['📈 有业务意义', '📉 无业务意义'])

    st.divider()

    # 决策建议
    sig = is_significant.startswith('✅')
    meaningful = effect_magnitude.startswith('📈')

    st.markdown('<div class="output-highlight"><div class="output-label">💡 决策建议</div>', unsafe_allow_html=True)

    if sig and meaningful:
        st.success('''
        ### ✅ 建议上线新方案
        
        **理由：** 统计显著且效应量具有业务意义
        
        **后续步骤：**
        1. 全量上线实验组方案
        2. 持续监控关键指标，关注长期效应
        3. 记录实验过程和结果，积累组织知识
        4. 评估实施成本和预期收益，制定推广计划
        
        **预估收益：** 效应量 × 目标人群规模 = 预期业务增量
        ''')

    elif sig and not meaningful:
        st.warning('''
        ### ⚠️ 统计显著但业务意义不大
        
        **理由：** 差异在统计上显著，但实际提升幅度不足以产生有价值的业务影响
        
        **建议：**
        1. 权衡实施成本与微薄收益
        2. 考虑是否继续优化以获得更大的效应
        3. 如果改动成本低，可以作为"无害改进"采用
        4. 重新审视实验指标是否真正反映业务目标
        ''')

    elif not sig and meaningful:
        st.info('''
        ### 🔍 效应有潜力但未达统计显著
        
        **理由：** 观察到了有意义的效应方向，但样本量可能不足
        
        **建议：**
        1. 计算所需样本量（回到"实验设计"模块）
        2. 延长实验时间收集更多数据
        3. 检查数据质量，排除异常值影响
        4. 考虑使用更敏感的指标或分析方法
        5. 警惕"数据窥探" — 不要为了显著而反复修改分析方案
        ''')

    else:
        st.error('''
        ### ❌ 建议保持现状
        
        **理由：** 既未达到统计显著，也没有观察到有意义的效应
        
        **建议：**
        1. 放弃当前方案，回到假设阶段
        2. 重新审视实验假设和设计
        3. 探索其他可能的改进方向
        4. 记录失败实验以供团队参考（避免重复尝试）
        ''')

    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()

    # 实验报告模板
    st.markdown('<div class="output-highlight"><div class="output-label">📝 AB测试报告模板</div>', unsafe_allow_html=True)

    report_sections = {
        '1. 实验背景': '简要描述实验目的、业务问题和假设',
        '2. 实验设计': '实验方案、随机分组方法、样本量计算依据',
        '3. 实验执行': '实验时间、流量分配、技术实现',
        '4. 数据分析': '描述性统计、假设检验方法、检验结果',
        '5. 结论与建议': '统计结论、业务判断、实施建议',
        '6. 附录': '详细数据、敏感性分析、圣洁性检查(Sanity Check)',
    }

    for section, desc in report_sections.items():
        st.markdown(f'**{section}** — {desc}')

    # 导出
    st.markdown("</div>", unsafe_allow_html=True)
    report_text = '\\n'.join([f'{s}: {d}' for s, d in report_sections.items()])
    st.download_button(
        '📥 下载报告模板',
        report_text,
        file_name='AB测试报告模板.txt',
        mime='text/plain'
    )

    st.divider()

    # 常见问题
    with st.expander('📖 AB测试常见误区'):
        st.markdown('''
        | 误区 | 说明 | 正确做法 |
        |------|------|----------|
        | **偷看问题** | 在实验未达预定样本量前多次查看结果 | 预先设定样本量和实验时长，避免过早下结论 |
        | **多重比较** | 同时检验多个指标，增加假阳性风险 | 预设主指标，或使用Bonferroni等方法校正 |
        | **混淆效应** | p<0.05就认为有实际意义 | 同时关注效应量和置信区间 |
        | **幸存者偏差** | 忽略退出实验的用户 | 关注全量用户(Intent-to-Treat分析) |
        | **新奇效应** | 新方案初期效果好但不可持续 | 实验周期至少覆盖1-2个完整业务周期 |
        ''')
