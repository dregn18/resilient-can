
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
        fig=px.box(plot,x='Grupo',y='Força dorsal',points='all',color='Grupo',color_discrete_sequence=COLOR,labels={'Força dorsal':T('Força dorsal'),'Grupo':T('Grupo')})
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
