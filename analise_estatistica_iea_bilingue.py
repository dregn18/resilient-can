import io, os, re, datetime
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import spearmanr, mannwhitneyu

st.set_page_config(page_title='Resilient Enterprise | Análise Estatística', page_icon='📊', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
.block-container{padding-top:1.7rem;max-width:1450px}.hero{padding:25px 30px;border-radius:16px;background:linear-gradient(115deg,#142b49,#275b84);color:white;margin-bottom:18px}.hero h1{color:white;font-size:2.1rem;margin:0}.hero p{color:#d9e8f6;margin:7px 0 0}.small{color:#64748b;font-size:.9rem}.stMetric{background:#f3f7fb;border:1px solid #e3eaf2;padding:13px;border-radius:12px}div[data-testid="stSidebar"]{background:#f3f6fb}
</style>''', unsafe_allow_html=True)
COLOR=['#2879b8','#e49b42','#22a69a','#7b65ba','#d86c83']

@st.cache_data
def load_excel(data):
    return pd.read_excel(data)

LANGUAGE_OPTIONS={'Português':'pt','English':'en'}
with st.sidebar:
    language_choice=st.selectbox('🌐 Idioma / Language',list(LANGUAGE_OPTIONS),key='language_choice')
LANG=LANGUAGE_OPTIONS[language_choice]
TRANSLATIONS={
 'Análises inferenciais · IEA 2027':'Inferential analyses · IEA 2027',
 'Carregar matriz Excel':'Upload Excel dataset',
 'Navegação':'Navigation',
 'Visão geral':'Overview',
 '1 · Dor e sono':'1 · Pain and sleep',
 '2 · Experiência profissional':'2 · Professional experience',
 '3 · Capacidade física':'3 · Physical capacity',
 '4 · Composição corporal':'4 · Body composition',
 '5 · Estilo de vida':'5 · Lifestyle',
 'Qualidade dos dados':'Data quality',
 'Spearman e Mann–Whitney U · testes exploratórios · α = 0,05':'Spearman and Mann–Whitney U · exploratory tests · α = 0.05',
 'Participantes elegíveis':'Eligible participants',
 'A amostra identificada não tem N=15; verifica os dados.':'The identified sample is not N=15; check the data.',
 'Filtrar IDs (exploratório)':'Filter IDs (exploratory)',
 'Filtro ativo: a amostra deixou de ter N=15.':'Active filter: the sample is no longer N=15.',
 'Carrega o ficheiro dados_mestre_completo.xlsx na barra lateral ou coloca-o na mesma pasta do programa.':'Upload dados_mestre_completo.xlsx in the sidebar or place it next to the script.',
 'Não foi possível abrir o Excel:':'Could not open the Excel file:',
 'Comparação':'Comparison','Estado':'Status','Dados/variabilidade insuficientes':'Insufficient data/variability',
 'Interpretação exploratória: N pequeno, múltiplas comparações e testes não paramétricos. p ≥ 0,05 não demonstra ausência de associação; correlação não implica causalidade. Valores de p sem ajuste por multiplicidade.':'Exploratory interpretation: small N, multiple comparisons and nonparametric tests. p ≥ 0.05 does not prove the absence of association; correlation does not imply causation. P-values are unadjusted for multiple testing.',
 'Dashboard de análise estatística · Protocolo completo · Congresso IEA 2027':'Statistical analysis dashboard · Complete protocol · IEA 2027 Congress',
 'Panorama da amostra':'Sample overview','Registos na matriz':'Dataset records','Protocolo completo':'Complete protocol',
 'Variáveis disponíveis':'Available variables','Regiões de dor':'Pain regions','Intensidade da dor por região':'Pain intensity by region',
 'Intensidade média (END 0–10)':'Mean pain intensity (NRS 0–10)','Sono efetivo':'Actual sleep duration',
 'Horas de sono':'Hours of sleep','Trabalhadores':'Workers',
 'O ficheiro mestre contém os questionários originais. O score global PSQI não está disponível como coluna calculada; os testes com esse score não são substituídos pela qualidade subjetiva.':'The master dataset contains the original questionnaires. The global PSQI score is not available as a calculated column; tests requiring this score are not replaced with subjective sleep quality.',
 'Dor mecânica e fragmentação do sono':'Mechanical pain and sleep fragmentation',
 'Correlação de Spearman entre END nos ombros/região lombar e latência, despertares e duração efetiva do sono.':'Spearman correlations between shoulder/lower-back pain (NRS) and sleep latency, nighttime awakenings and actual sleep duration.',
 'Dor nos ombros × latência':'Shoulder pain × sleep latency','Dor lombar × despertares':'Lower-back pain × awakenings',
 'Experiência profissional e sintomas músculo-esqueléticos':'Professional experience and musculoskeletal symptoms',
 'Anos em altura × dor nos ombros':'Years working at height × shoulder pain',
 'Anos em altura × dor lombar':'Years working at height × lower-back pain',
 'Capacidade física · Sintomáticos vs. assintomáticos':'Physical capacity · Symptomatic vs. asymptomatic',
 'Definição operacional: sintomático = END > 0; assintomático = END = 0. Comparar com a classificação prevista no protocolo.':'Operational definition: symptomatic = NRS > 0; asymptomatic = NRS = 0. Check against the protocol classification.',
 'Sintomáticos':'Symptomatic','Assintomáticos':'Asymptomatic','Força dorsal':'Back strength',
 'Região':'Region','Indicador':'Measure','n sint.':'n sympt.','n assint.':'n asympt.',
 'Mediana [IIQ] sint.':'Median [IQR] sympt.','Mediana [IIQ] assint.':'Median [IQR] asympt.',
 'O pedido inclui comparação de scores globais PSQI. O Excel tem os itens individuais, mas não o score global validado; esse teste permanece pendente. Não se substitui pelo item de qualidade subjetiva.':'The request includes comparisons of global PSQI scores. The Excel contains individual items but no validated global score; this test remains pending. Subjective sleep quality is not a substitute.',
 'Composição corporal e dor lombar':'Body composition and lower-back pain',
 'IMC × dor lombar':'BMI × lower-back pain','Gordura corporal × dor lombar':'Body fat × lower-back pain',
 'Consumo de bebidas açucaradas e dor':'Sugar-sweetened beverage consumption and pain',
 'Frequência MEDAS codificada ordinalmente: menos de 1 = 0; 1 = 1; mais de 1 = 2. Não são quantidades exatas.':'MEDAS frequency coded ordinally: less than 1 = 0; 1 = 1; more than 1 = 2. These are not exact quantities.',
 'Bebidas açucaradas × carga total de dor':'Sugary drinks × total pain burden',
 'Bebidas açucaradas × regiões afetadas':'Sugary drinks × affected regions',
 'Carga global de dor = soma das END das nove regiões; indicador exploratório derivado, não score validado do Questionário Nórdico.':'Global pain burden = sum of NRS values across nine regions; an exploratory derived measure, not a validated Nordic Questionnaire score.',
 'Auditoria dos dados e correspondência das colunas':'Data audit and column mapping',
 'IDs sem os campos-chave necessários:':'IDs missing required key fields:',
 'Variável':'Variable','Coluna detetada':'Detected column','Valores válidos (amostra)':'Valid values (sample)',
 'NÃO ENCONTRADA':'NOT FOUND',
 'O PSQI global não consta do Excel. A avaliação completa desse score requer recodificação rigorosa dos itens e verificação das regras do instrumento, antes da comparação Mann–Whitney.':'The global PSQI score is not included in the Excel. Computing it requires rigorous item recoding and verification of the instrument scoring rules before Mann–Whitney comparisons.',
 'Exportar auditoria (.csv)':'Export audit (.csv)',
 'Ombros':'Shoulders','Lombar':'Lower back','Punhos/mãos':'Wrists/hands',
 'Experiência em altura':'Experience working at height','Latência do sono':'Sleep latency',
 'Despertares noturnos':'Nighttime awakenings','Duração do sono':'Sleep duration',
 'Dinamometria dorsal':'Back dynamometry','Preensão direita':'Right grip strength',
 'Preensão esquerda':'Left grip strength','IMC':'BMI','Gordura corporal':'Body fat',
 'Bebidas açucaradas':'Sugar-sweetened beverages',
 'Qualidade subjetiva do sono':'Subjective sleep quality','Carga global de dor':'Global pain burden',
 'Regiões com dor':'Pain-affected regions',
 'NÃO ENCONTRADA':'NOT FOUND'
}
def T(value):
    if LANG!='en':return value
    if isinstance(value,str):
        return TRANSLATIONS.get(value,value)
    return value
PAGE_KEYS=['Visão geral','1 · Dor e sono','2 · Experiência profissional','3 · Capacidade física','4 · Composição corporal','5 · Estilo de vida','Qualidade dos dados']
with st.sidebar:
    st.title('📊 Resilient Enterprise')
    st.caption(T('Análises inferenciais · IEA 2027'))
    upload=st.file_uploader(T('Carregar matriz Excel'),type=['xlsx'])
    st.divider()
    selected_page=st.radio(T('Navegação'),PAGE_KEYS,format_func=T,label_visibility='collapsed')
    page=selected_page
    st.divider()
    st.caption(T('Spearman e Mann–Whitney U · testes exploratórios · α = 0,05'))

path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'dados_mestre_completo.xlsx')
if upload is None and not os.path.isfile(path):
    st.info(T('Carrega o ficheiro dados_mestre_completo.xlsx na barra lateral ou coloca-o na mesma pasta do programa.'))
    st.stop()
try:
    df=load_excel(upload if upload is not None else path)
except Exception as exc:
    st.error(f"{T('Não foi possível abrir o Excel:')} {exc}")
    st.stop()
df.columns=[str(c).strip() for c in df.columns]

def find(part):
    return next((c for c in df.columns if part.casefold() in c.casefold()),None)
def num(col):
    if col is None:return pd.Series(np.nan,index=df.index,dtype=float)
    return pd.to_numeric(df[col].astype(str).str.replace(',','.',regex=False).str.strip(),errors='coerce')
def hours(col):
    if col is None:return pd.Series(np.nan,index=df.index,dtype=float)
    def convert(x):
        if pd.isna(x):return np.nan
        if isinstance(x,(datetime.time,datetime.datetime,pd.Timestamp)):return x.hour+x.minute/60
        s=str(x).strip()
        if ':' in s:
            try:
                h,m=s.split(':')[:2];return float(h)+float(m)/60
            except: return np.nan
        try:return float(s.replace(',','.'))
        except:return np.nan
    return df[col].apply(convert).astype(float)

def ordinal(col):
    if col is None:return pd.Series(np.nan,index=df.index,dtype=float)
    def convert(x):
        if pd.isna(x):return np.nan
        s=str(x).lower().strip()
        if 'não ocorreu' in s or 'nao ocorreu' in s or 'nunca' in s:return 0
        if 'menos de 1' in s:return 1
        if '1 ou 2' in s:return 2
        if '3 ou mais' in s:return 3
        return np.nan
    return df[col].apply(convert).astype(float)

def sugarcode(col):
    if col is None:return pd.Series(np.nan,index=df.index,dtype=float)
    def convert(x):
        if pd.isna(x):return np.nan
        s=str(x).lower().strip()
        if 'menos de 1' in s:return 0
        if 'mais de 1' in s:return 2
        if s in ['1','1.0']:return 1
        try:return float(s.replace(',','.'))
        except:return np.nan
    return df[col].apply(convert).astype(float)

cols={
 'Ombros':find('OMBROS - ESCALA NUMÉRICA'), 'Lombar':find('REGIÃO LOMBAR - ESCALA NUMÉRICA'),
 'Punhos/mãos':find('PUNHOS/MÃOS - ESCALA NUMÉRICA'),
 'Experiência em altura':find('TEMPO DE EXPERIÊNCIA EM TRABALHOS EM ALTURA'),
 'Latência do sono':find('QUANTO TEMPO DEMOROU A ADORMECER'),
 'Despertares noturnos':find('ACORDAR A MEIO DA NOITE OU MUITO CEDO'),
 'Duração do sono':find('QUANTAS HORAS DE SONO EFETIVO'),
 'Dinamometria dorsal':find('MÉDIA Din Dor'),
 'Preensão direita':find('MÉDIA Din PP D'), 'Preensão esquerda':find('MÉDIA Din PP E'),
 'IMC':find('Índice de Massa Corporal'), 'Gordura corporal':find('Gordura Corporal (%)'),
 'Bebidas açucaradas':find('QUANTAS BEBIDAS AÇUCARADAS OU REFRIGERANTES'),
 'Qualidade subjetiva do sono':find('COMO CLASSIFICARIA A QUALIDADE GERAL'),
}
# Os registos 2, 4 e 7 não completaram as avaliações; usar critérios objetivos, não apenas o N esperado.
needed=['Ombros','Lombar','IMC','Latência do sono','Bebidas açucaradas']
mask=pd.Series(True,index=df.index)
for v in needed:
    if cols[v]:mask &= df[cols[v]].notna()
full=df.copy()
df=df.loc[mask].copy()
with st.sidebar:
    st.metric(T('Participantes elegíveis'),len(df))
    if len(df)!=15:st.warning(T('A amostra identificada não tem N=15; verifica os dados.'))
    if 'ID' in df:
        ids=sorted(df.ID.dropna().tolist())
        chosen=st.multiselect(T('Filtrar IDs (exploratório)'),ids,default=ids)
        df=df[df.ID.isin(chosen)].copy()
        if len(df)!=15:st.warning(T('Filtro ativo: a amostra deixou de ter N=15.'))

v={k:(hours(c) if k=='Duração do sono' else ordinal(c) if k=='Despertares noturnos' else sugarcode(c) if k=='Bebidas açucaradas' else num(c)) for k,c in cols.items() if k!='Qualidade subjetiva do sono'}
for k in v:v[k]=v[k].reindex(df.index)
region_cols=[c for c in df.columns if c.endswith('ESCALA NUMÉRICA DE DOR (END)')]
if region_cols:
    pain=df[region_cols].apply(lambda s:pd.to_numeric(s,errors='coerce'))
    v['Carga global de dor']=pain.sum(axis=1,min_count=1)
    v['Regiões com dor']=(pain>0).sum(axis=1).where(pain.notna().any(axis=1))
else:
    v['Carga global de dor']=pd.Series(np.nan,index=df.index)
    v['Regiões com dor']=pd.Series(np.nan,index=df.index)

def fmt(x,n=2):return '—' if pd.isna(x) else f'{x:.{n}f}'.replace('.',',')
def desc(s):
    s=s.dropna();return f'{fmt(s.median())} [{fmt(s.quantile(.25))}–{fmt(s.quantile(.75))}]' if len(s) else '—'
def corr(a,b,label_a,label_b):
    pair=pd.concat([v[a],v[b]],axis=1).dropna()
    if len(pair)<4 or pair.iloc[:,0].nunique()<2 or pair.iloc[:,1].nunique()<2:
        return dict(Comparação=f'{T(label_a)} × {T(label_b)}',N=len(pair),rho=np.nan,p=np.nan,Estado=T('Dados/variabilidade insuficientes'))
    r,p=spearmanr(pair.iloc[:,0],pair.iloc[:,1]);return dict(Comparação=f'{T(label_a)} × {T(label_b)}',N=len(pair),rho=r,p=p,Estado='p < 0,05' if p<.05 else 'p ≥ 0,05')
def scatter(a,b,title):
    t=pd.DataFrame({'x':v[a],'y':v[b],'ID':df.ID if 'ID' in df else df.index}).dropna()
    if t.empty:return
    fig=px.scatter(t,x='x',y='y',hover_data=['ID'],color_discrete_sequence=[COLOR[0]],opacity=.82)
    fig.update_traces(marker=dict(size=12,line=dict(width=1,color='white')))
    fig.update_layout(title=T(title),xaxis_title=T(a),yaxis_title=T(b),height=380,margin=dict(t=55,l=30,r=20,b=35),plot_bgcolor='#f7f9fc',paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig,use_container_width=True)
def result_table(rows):
    table=pd.DataFrame(rows)
    if table.empty:return
    view=table.copy()
    for c in ['rho','p','U']:
        if c in view:view[c]=view[c].map(lambda x:fmt(x,3))
    view=view.rename(columns=T)
    st.dataframe(view,use_container_width=True,hide_index=True)
    return table

def note():st.caption(T('Interpretação exploratória: N pequeno, múltiplas comparações e testes não paramétricos. p ≥ 0,05 não demonstra ausência de associação; correlação não implica causalidade. Valores de p sem ajuste por multiplicidade.'))

st.markdown(f'<div class="hero"><h1>Resilient Enterprise</h1><p>{T("Dashboard de análise estatística · Protocolo completo · Congresso IEA 2027")}</p></div>',unsafe_allow_html=True)

if page=='Visão geral':
    st.subheader(T('Panorama da amostra'))
    a,b,c,d=st.columns(4)
    a.metric('Registos na matriz',len(full));b.metric('Protocolo completo',len(df));c.metric('Variáveis disponíveis',sum(x is not None for x in cols.values()));d.metric('Regiões de dor',len(region_cols))
    st.divider()
    l,r=st.columns(2)
    with l:
        st.subheader(T('Intensidade da dor por região'))
        if region_cols:
            p=df[region_cols].apply(pd.to_numeric,errors='coerce')
            labels=[x.split(' - ')[0].title() for x in region_cols]
            fig=go.Figure(go.Bar(x=labels,y=p.mean().values,marker_color=COLOR[0],text=[fmt(x,1) for x in p.mean()],textposition='outside'))
            fig.update_layout(height=420,yaxis_title=T('Intensidade média (END 0–10)'),xaxis_tickangle=-35,margin=dict(t=25,b=85),plot_bgcolor='#f7f9fc')
            st.plotly_chart(fig,use_container_width=True)
    with r:
        st.subheader(T('Sono efetivo'))
        t=v['Duração do sono'].dropna()
        if len(t):
            fig=px.histogram(x=t,nbins=8,color_discrete_sequence=[COLOR[2]],labels={'x':T('Horas de sono')})
            fig.add_vline(x=7,line_dash='dash',line_color='#d44e4e',annotation_text='7 h')
            fig.update_layout(height=420,xaxis_title=T('Horas de sono'),yaxis_title=T('Trabalhadores'),plot_bgcolor='#f7f9fc')
            st.plotly_chart(fig,use_container_width=True)
    st.info(T('O ficheiro mestre contém os questionários originais. O score global PSQI não está disponível como coluna calculada; os testes com esse score não são substituídos pela qualidade subjetiva.'))

elif page=='1 · Dor e sono':
    st.header(T('Dor mecânica e fragmentação do sono'))
    st.write(T('Correlação de Spearman entre END nos ombros/região lombar e latência, despertares e duração efetiva do sono.'))
    rows=[corr(a,b,a,b) for a in ['Ombros','Lombar'] for b in ['Latência do sono','Despertares noturnos','Duração do sono']]
    result_table(rows)
    a,b=st.columns(2)
    with a:scatter('Ombros','Latência do sono','Dor nos ombros × latência')
    with b:scatter('Lombar','Despertares noturnos','Dor lombar × despertares')
    note()
elif_placeholder=False
if page=='2 · Experiência profissional':
    st.header(T('Experiência profissional e sintomas músculo-esqueléticos'))
    rows=[corr('Experiência em altura',b,'Experiência em altura',b) for b in ['Ombros','Lombar','Punhos/mãos']]
    result_table(rows)
    a,b=st.columns(2)
    with a:scatter('Experiência em altura','Ombros','Anos em altura × dor nos ombros')
    with b:scatter('Experiência em altura','Lombar','Anos em altura × dor lombar')
    note()
if page=='3 · Capacidade física':
    st.header(T('Capacidade física · Sintomáticos vs. assintomáticos'))
    st.caption(T('Definição operacional: sintomático = END > 0; assintomático = END = 0. Comparar com a classificação prevista no protocolo.'))
    rows=[]
    for reg in ['Ombros','Lombar']:
        group=v[reg]>0
        st.subheader(T(reg))
        n1=int(((v[reg]>0)&v[reg].notna()).sum());n0=int(((v[reg]==0)&v[reg].notna()).sum())
        st.write(f"**{T('Sintomáticos')}: {n1}** · **{T('Assintomáticos')}: {n0}**")
        for metric in ['Dinamometria dorsal','Preensão direita','Preensão esquerda']:
            x=v[metric][group & v[reg].notna()].dropna();y=v[metric][~group & v[reg].notna()].dropna()
            if len(x)>0 and len(y)>0:
                U,p=mannwhitneyu(x,y,alternative='two-sided',method='auto')
            else:U,p=np.nan,np.nan
            rows.append({'Região':reg,'Indicador':metric,'n sint.':len(x),'n assint.':len(y),'Mediana [IIQ] sint.':desc(x),'Mediana [IIQ] assint.':desc(y),'U':U,'p':p})
        plot=pd.DataFrame({'Força dorsal':v['Dinamometria dorsal'],'Grupo':np.where(group,T('Sintomáticos'),T('Assintomáticos'))}).dropna()
        fig=px.box(plot,x='Grupo',y=T('Força dorsal'),points='all',color='Grupo',color_discrete_sequence=COLOR)
        fig.update_layout(height=340,showlegend=False,plot_bgcolor='#f7f9fc')
        st.plotly_chart(fig,use_container_width=True)
    result_table(rows)
    st.warning(T('O pedido inclui comparação de scores globais PSQI. O Excel tem os itens individuais, mas não o score global validado; esse teste permanece pendente. Não se substitui pelo item de qualidade subjetiva.'))
    note()
if page=='4 · Composição corporal':
    st.header(T('Composição corporal e dor lombar'))
    result_table([corr(x,'Lombar',x,'Lombar') for x in ['IMC','Gordura corporal']])
    a,b=st.columns(2)
    with a:scatter('IMC','Lombar','IMC × dor lombar')
    with b:scatter('Gordura corporal','Lombar','Gordura corporal × dor lombar')
    note()
if page=='5 · Estilo de vida':
    st.header(T('Consumo de bebidas açucaradas e dor'))
    st.write(T('Frequência MEDAS codificada ordinalmente: menos de 1 = 0; 1 = 1; mais de 1 = 2. Não são quantidades exatas.'))
    result_table([corr('Bebidas açucaradas',x,'Bebidas açucaradas',x) for x in ['Carga global de dor','Regiões com dor']])
    a,b=st.columns(2)
    with a:scatter('Bebidas açucaradas','Carga global de dor','Bebidas açucaradas × carga total de dor')
    with b:scatter('Bebidas açucaradas','Regiões com dor','Bebidas açucaradas × regiões afetadas')
    st.caption(T('Carga global de dor = soma das END das nove regiões; indicador exploratório derivado, não score validado do Questionário Nórdico.'))
    note()
if page=='Qualidade dos dados':
    st.header(T('Auditoria dos dados e correspondência das colunas'))
    st.write((f'Dataset: **{len(full)} records × {len(full.columns)} columns**. Eligible after completeness screening: **{len(df)}**.' if LANG=='en' else f'Matriz: **{len(full)} registos × {len(full.columns)} colunas**. Elegíveis após filtro de completude: **{len(df)}**.'))
    if 'ID' in full:
        st.write(T('IDs sem os campos-chave necessários:'),full.loc[~mask,'ID'].tolist())
    audit=[]
    for label,c in cols.items():
        audit.append({T('Variável'):T(label),T('Coluna detetada'):c or T('NÃO ENCONTRADA'),T('Valores válidos (amostra)'):int(df[c].notna().sum()) if c else 0})
    st.dataframe(pd.DataFrame(audit),use_container_width=True,hide_index=True)
    st.warning(T('O PSQI global não consta do Excel. A avaliação completa desse score requer recodificação rigorosa dos itens e verificação das regras do instrumento, antes da comparação Mann–Whitney.'))
    st.download_button(T('Exportar auditoria (.csv)'),pd.DataFrame(audit).to_csv(index=False).encode('utf-8-sig'),'auditoria_iea.csv','text/csv')
