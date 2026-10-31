import os
import io
import json
from html import escape
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from src.config import CATEGORIES, GOALS, CURRENCIES, DISCLAIMER
from src.financial_calculator import calculate, score_band
from src.cache_manager import configure_cache
from src.chains import make_llm, run_analysis, stream_recommendations

st.set_page_config(page_title='FinWise AI | Financial Intelligence',page_icon='💠',layout='wide',initial_sidebar_state='expanded')
st.markdown('''<style>
.block-container{padding-top:2rem;max-width:1350px}
.hero{background:linear-gradient(110deg,#172554,#0f766e);border:1px solid #375e77;border-radius:22px;padding:32px;margin-bottom:22px;box-shadow:0 12px 36px #00000018}
.hero h1{color:#fff;font-size:2.6rem;margin:0}.hero p{color:#cbd5ed;margin-bottom:0}
[data-testid="stMetric"]{background:rgba(75,115,150,.10);border:1px solid rgba(100,116,139,.25);border-radius:15px;padding:18px}
[data-testid="stSidebar"]{border-right:1px solid rgba(100,116,139,.25)}
</style>''',unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>◈ FinWise AI</h1><p>Personal finance intelligence · Smart budgets · Actionable educational insights</p></div>',unsafe_allow_html=True)
st.caption('⚠️ '+DISCLAIMER)
with st.sidebar:
    st.title('◈ FinWise AI')
    st.caption('LangChain + Streamlit • Educational prototype')
    st.warning(DISCLAIMER)
    st.subheader('AI settings')
    model=st.selectbox('OpenAI model',['gpt-4o-mini','gpt-4o'])
    temperature=st.slider('Creativity',0.0,1.0,0.2,0.1)
    cache_mode=st.selectbox('LLM cache',['Memory','SQLite','Off'])
    st.caption('SQLite persistence depends on deployment storage; ephemeral hosting may clear the cache.')
    if st.button('↺ Reset session',use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.divider()
    st.caption('Your inputs are processed in the session. AI requests send the submitted financial figures to OpenAI. Avoid entering private account details.')

key=os.getenv('OPENAI_API_KEY','')
try:
    key=st.secrets.get('OPENAI_API_KEY',key)
except (FileNotFoundError,KeyError):
    pass

with st.form('finance_form'):
    st.subheader('01 / Financial profile')
    left,right=st.columns(2)
    with left:
        income=st.number_input('Monthly income',min_value=0.0,value=5000.0,step=100.0)
        savings=st.number_input('Current monthly savings',min_value=0.0,value=500.0,step=50.0,help='Monthly savings figure; not automatically added to expenses.')
    with right:
        currency=st.selectbox('Currency',CURRENCIES,index=1)
        goal=st.selectbox('Financial goal',GOALS)
    st.subheader('02 / Monthly expense breakdown')
    st.caption('Enter each category once. Savings are tracked separately; ensure figures are consistent with your personal budget.')
    cols=st.columns(2)
    defaults=[1200,500,200,150,100,100,100,200,100,100]
    expenses={}
    for i,cat in enumerate(CATEGORIES):
        with cols[i%2]:
            expenses[cat]=st.number_input(cat,min_value=0.0,value=float(defaults[i]),step=25.0,key='expense_'+str(i))
    submitted=st.form_submit_button('✦ Analyze my finances',type='primary',use_container_width=True)

if submitted:
    metrics=calculate(income,expenses,savings)
    if savings > max(0, metrics['remaining_income']):
        st.warning('Monthly savings exceed the unspent balance. Check whether savings are already included in an expense category or funded from other sources.')
    st.session_state['profile']={'metrics':metrics,'expenses':expenses,'goal':goal,'currency':currency,'date':date.today().isoformat()}
    st.session_state.pop('analysis',None)
    st.session_state.pop('narrative',None)

profile=st.session_state.get('profile')
if profile:
    m=profile['metrics']; cur=profile['currency']; ex=profile['expenses']
    st.divider()
    st.subheader('03 / Your financial overview')
    cols=st.columns(4)
    for col,label,value in zip(cols,['Monthly income','Total expenses','Remaining balance','Monthly savings'],[m['monthly_income'],m['total_expenses'],m['remaining_income'],m['savings']]):
        col.metric(label,f'{cur} {value:,.2f}')
    a,b=st.columns([1,2])
    with a:
        st.metric('Python financial health score',f"{m['preliminary_score']}/100",score_band(m['preliminary_score']),delta_color='off')
        st.progress(m['preliminary_score']/100)
        st.metric('Rule-based risk',m['risk_level'])
        st.metric('Savings ratio',f"{m['savings_ratio']:.1f}%")
        st.metric('Expense ratio',f"{m['expense_ratio']:.1f}%")
        st.caption('Score and risk are rule-based Python calculations, not AI predictions.')
    with b:
        chart_df=pd.DataFrame({'Category':list(ex),'Amount':list(ex.values())})
        tabs=st.tabs(['Expense distribution','Expense comparison'])
        with tabs[0]:
            nonzero=chart_df[chart_df.Amount>0]
            if len(nonzero): st.plotly_chart(px.pie(nonzero,names='Category',values='Amount',hole=.55),use_container_width=True)
            else: st.info('No expenses to visualize.')
        with tabs[1]:
            st.plotly_chart(px.bar(chart_df.sort_values('Amount'),x='Amount',y='Category',orientation='h'),use_container_width=True)
    st.subheader('04 / AI-powered analysis')
    inputs={**m,'financial_goal':profile['goal'],'expense_breakdown':json.dumps(ex,sort_keys=True),'currency':cur}
    if not key or key=='your_openai_api_key_here':
        st.info('Add OPENAI_API_KEY to .env (local) or Streamlit Cloud Secrets to enable AI analysis. All Python calculations and charts work without an API key.')
    else:
        if st.button('Generate structured AI insights',type='primary'):
            try:
                configure_cache(cache_mode)
                llm=make_llm(model,temperature)
                with st.spinner('Validating structured AI response...'):
                    st.session_state['analysis']=run_analysis(llm,inputs,m)
            except Exception as exc:
                st.error('AI analysis failed. Check the API key, model access, network and JSON schema. '+str(exc)[:300])
        result=st.session_state.get('analysis')
        if result:
            st.success('AI analysis validated against Python score and risk.')
            st.info(result['financial_summary'])
            st.metric('AI-reported score (validated)',f"{result['financial_health_score']}/100")
            st.progress(result['financial_health_score']/100)
            st.warning('Risk level: '+result['risk_level']) if result['risk_level']=='HIGH' else st.info('Risk level: '+result['risk_level'])
            tabs=st.tabs(['Spending analysis','Priorities','Budget strategy','Savings strategy','Next-month plan'])
            with tabs[0]:
                for item in result['spending_analysis']:
                    with st.expander(item['category'],expanded=True):
                        st.write(item['observation']);st.write('**Suggested action:** '+item['recommendation'])
            for tab,field in zip(tabs[1:],['top_priorities','budget_recommendations','savings_strategy','next_month_action_plan']):
                with tab:
                    for i,point in enumerate(result[field],1): st.write(f'{i}. {point}')
            if st.button('▶ Stream live next-month recommendations'):
                try:
                    configure_cache(cache_mode)
                    st.session_state['narrative']=st.write_stream(stream_recommendations(make_llm(model,temperature),inputs))
                except Exception as exc:
                    st.error('Streaming failed: '+str(exc)[:250])
            elif st.session_state.get('narrative'):
                st.markdown('**Latest streamed recommendations**\n\n'+st.session_state['narrative'])
    st.subheader('05 / Reports and tracking')
    report={'profile':profile,'ai_analysis':st.session_state.get('analysis'),'narrative':st.session_state.get('narrative')}
    st.download_button('Download JSON report',json.dumps(report,indent=2),file_name='finwise_report.json',mime='application/json')
    def pdf_bytes():
        buffer=io.BytesIO();doc=SimpleDocTemplate(buffer)
        styles=getSampleStyleSheet(); story=[Paragraph('FinWise AI — Educational Financial Report',styles['Title']),Spacer(1,15),Paragraph(DISCLAIMER,styles['Normal']),Spacer(1,12)]
        for label,value in m.items(): story.append(Paragraph(f'{label.replace("_"," ").title()}: {value}',styles['Normal']))
        if st.session_state.get('analysis'):
            analysis=st.session_state['analysis']
            story.append(Spacer(1,14));story.append(Paragraph('AI Summary',styles['Heading2']))
            story.append(Paragraph(escape(analysis['financial_summary']),styles['Normal']))
            for section in ['top_priorities','budget_recommendations','savings_strategy','next_month_action_plan']:
                story.append(Paragraph(section.replace('_',' ').title(),styles['Heading2']))
                for item in analysis[section]: story.append(Paragraph('• '+escape(item),styles['Normal']))
        doc.build(story);return buffer.getvalue()
    st.download_button('Download PDF report',pdf_bytes(),file_name='finwise_report.pdf',mime='application/pdf')
    with st.expander('CSV expense history / month-to-month comparison'):
        uploaded=st.file_uploader('Upload CSV with columns month, category, amount',type=['csv'])
        if uploaded:
            try:
                history=pd.read_csv(uploaded)
                if not {'month','category','amount'}.issubset(history.columns): raise ValueError('Required columns: month, category, amount')
                history['amount']=pd.to_numeric(history['amount'],errors='raise')
                if history['amount'].lt(0).any(): raise ValueError('Amounts must be nonnegative')
                monthly=history.groupby('month',as_index=False)['amount'].sum().sort_values('month')
                st.dataframe(monthly,use_container_width=True)
                st.plotly_chart(px.line(monthly,x='month',y='amount',markers=True,title='Monthly spending trend'),use_container_width=True)
            except Exception as exc: st.error('Invalid CSV: '+str(exc))
    with st.expander('Financial goal tracker'):
        target=st.number_input('Goal amount',min_value=1.0,value=10000.0,step=100.0)
        accumulated=st.number_input('Amount already saved toward goal',min_value=0.0,value=0.0,step=100.0)
        st.progress(min(1.0,accumulated/target))
        st.write(f'{min(100,accumulated/target*100):.1f}% of {cur} {target:,.2f} achieved')
        if m['savings']>0 and accumulated<target:
            import math
            st.caption(f'At current monthly savings, approximately {math.ceil((target-accumulated)/m["savings"])} months to target (illustrative only).')
    st.caption('⚠️ '+DISCLAIMER)
