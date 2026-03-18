import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Inmovision - Dashboard Corporativo", layout="wide")

# 2. CSS PARA DISEÑO UNIFICADO
st.markdown("""
    <style>
    /* BLOQUE PARA OCULTAR LA FLECHA DEL SIDEBAR */
    [data-testid="bundle-lib-sidebar-close-icon"], 
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
    
    .stApp { background-color: #0e1117 !important; }
    .asesor-header { color: #ffffff; font-size: 26px; font-weight: bold; margin-bottom: 20px; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
    .card-container { display: flex; gap: 15px; margin-bottom: 25px; margin-top: 10px; }
    .card-total { background-color: #f1f3f6; border-radius: 10px; padding: 15px; flex: 1; color: #1a1c24; text-align: center; border-left: 5px solid #4CAF50; box-shadow: 2px 2px 5px rgba(0,0,0,0.3); }
    .total-label { font-weight: 800; font-size: 12px; text-transform: uppercase; color: #666; margin-bottom: 5px; }
    .total-amount { font-size: 28px; font-weight: bold; color: #000; }
    [data-testid="stSidebar"] { background-color: #1a1c24; }
    .logo-sidebar { display: block; margin: auto; width: 150px; margin-bottom: 20px; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. CONFIGURACIÓN DE RECURSOS
URL_VENTAS = "https://docs.google.com/spreadsheets/d/18WS22r1Fml5a9qW3fJOj40d0h7aldJVj/edit?usp=sharing"
URL_INSTALACIONES = "https://docs.google.com/spreadsheets/d/1QqH8lGktix5YLV7seIL9cXUxWCaANauM/edit?usp=sharing"
URL_GESTION = "https://docs.google.com/spreadsheets/d/1z_Y-dSghRs0nuFwOm6Eh_ZTPE-RKRVcj/edit?usp=sharing"
URL_LOGO = "https://lh4.googleusercontent.com/proxy/SeW7l23MFgElfFnJzA8WsomRRdBeiXYsMuQMdiB6_m4J0N0j7RGAB09PNGAO-uUPhKMPITGfAgagRh76fzbODUl3jU3utoz20hT2W99Q7BODxV-g" 

VENDEDORES_PERMITIDOS = [
    "ALEXANDRA REINO", "ANDREA MENDOZA", "CESAR VERA", "DIANA RIVERA", 
    "EDISON SACA", "FRANKLIN QUEZADA", "GLENDA RAMOS AYORA", "JENNIFER ATANCURI", 
    "JORGE GARCIA", "LAURA MORAN", "MANCHENO KARLA", "MARIA JOSE PEÑAFIEL", 
    "MELANY GUZHÑAY", "NANCY JARAMA", "PRISCILA RAMOS", "SILVIA YUNGA", 
    "STALIN ROJAS", "SUSANA PACURUCO", "SUSANA PACURUCU", "VERONICA MALO", 
    "WILLIAM BRITO", "WILLIAN MOLINA", "RAMOS AYORA GLENDA"
]

@st.cache_data(ttl=600)
def cargar_datos(url, nombre_hoja):
    try:
        file_id = url.split('/')[-2]
        export_url = f'https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx'
        df = pd.read_excel(export_url, sheet_name=nombre_hoja)
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df
    except: return None

# --- SIDEBAR ---
st.sidebar.markdown(f'<img src="{URL_LOGO}" class="logo-sidebar">', unsafe_allow_html=True)
st.sidebar.title("Menú Principal")
seccion = st.sidebar.radio("Seleccione un Módulo:", 
                           ["📊 Control de Ventas", "🛠️ Reporte de Instalaciones", "📈 Gestión de Asesores"])
st.sidebar.markdown("---")

# ==========================================
# MÓDULO 1: CONTROL DE VENTAS
# ==========================================
if seccion == "📊 Control de Ventas":
    try:
        file_id_v = URL_VENTAS.split('/')[-2]
        export_url_v = f'https://docs.google.com/spreadsheets/d/{file_id_v}/export?format=xlsx'
        xls = pd.ExcelFile(export_url_v)
        hojas_reales = xls.sheet_names
        hojas_display = [str(h).lower() for h in hojas_reales]
        mapa_hojas = dict(zip(hojas_display, hojas_reales))
        mes_sel_display = st.sidebar.selectbox("📅 Mes a consultar:", hojas_display)
        df_ventas = cargar_datos(URL_VENTAS, mapa_hojas[mes_sel_display])

        if df_ventas is not None:
            col_vendedor = df_ventas.columns[0]
            df_ventas[col_vendedor] = df_ventas[col_vendedor].astype(str).str.strip().str.upper()
            vendedores_db = sorted([v for v in df_ventas[col_vendedor].unique() if v in VENDEDORES_PERMITIDOS])
            st.sidebar.markdown("### Filtros")
            ver_todo = st.sidebar.checkbox("Ver Resumen General del Mes")
            vendedor_sel = st.sidebar.selectbox("👤 Seleccionar Asesor:", vendedores_db)

            if ver_todo:
                st.markdown('<div class="asesor-header">📊 Resumen General de Ventas</div>', unsafe_allow_html=True)
                columnas_total = [c for c in df_ventas.columns if 'TOTAL' in str(c).upper() and c != col_vendedor]
                if columnas_total:
                    col_total_name = columnas_total[0]
                    resumen = df_ventas[df_ventas[col_vendedor].isin(VENDEDORES_PERMITIDOS)].copy()
                    resumen = resumen[[col_vendedor, col_total_name]]
                    resumen.columns = ['Vendedor', 'Monto Total']
                    resumen['Monto Total'] = pd.to_numeric(resumen['Monto Total'], errors='coerce').fillna(0)
                    resumen = resumen[resumen['Monto Total'] > 0].sort_values(by='Monto Total', ascending=False)
                    st.markdown(f'<div class="card-general" style="background-color:#1a1c24; border:1px solid #4CAF50; border-radius:12px; padding:25px; text-align:center; margin-bottom:20px;"><div class="total-label" style="color:#4CAF50">Venta Total Consolidada</div><div class="total-general-amount" style="font-size:45px; font-weight:bold; color:#4CAF50;">${resumen["Monto Total"].sum():,.2f}</div></div>', unsafe_allow_html=True)
                    c1, c2 = st.columns([1, 1])
                    with c1: st.dataframe(resumen, use_container_width=True, hide_index=True)
                    with c2:
                        fig_pie = px.pie(resumen, values='Monto Total', names='Vendedor', hole=0.4, title="Participación")
                        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
                        st.plotly_chart(fig_pie, use_container_width=True)

            elif vendedor_sel:
                st.markdown(f'<div class="asesor-header">👤 Asesor: {vendedor_sel}</div>', unsafe_allow_html=True)
                fila_v = df_ventas[df_ventas[col_vendedor] == vendedor_sel]
                cols_excluir = [col_vendedor] + [c for c in df_ventas.columns if 'TOTAL' in str(c).upper()]
                cols_datos = [c for c in df_ventas.columns if c not in cols_excluir]
                datos_fila = fila_v[cols_datos].T.reset_index()
                datos_fila = datos_fila.iloc[:, :2] 
                datos_fila.columns = ['Fecha', 'Venta']
                datos_fila['Fecha_DT'] = pd.to_datetime(datos_fila['Fecha'], errors='coerce')
                datos_fila['Venta'] = pd.to_numeric(datos_fila['Venta'], errors='coerce').fillna(0)
                ventas_ok = datos_fila[datos_fila['Venta'] > 0].copy().sort_values('Fecha_DT')
                ventas_ok['Fecha_Limpia'] = ventas_ok['Fecha_DT'].dt.strftime('%d-%m-%Y')
                st.markdown(f'''<div class="card-container"><div class="card-total"><div class="total-label">Monto Total Vendido</div><div class="total-amount">${ventas_ok["Venta"].sum():,.2f}</div></div><div class="card-total" style="border-left-color: #2196F3;"><div class="total-label">Cantidad de Ventas</div><div class="total-amount">{len(ventas_ok)}</div></div></div>''', unsafe_allow_html=True)
                if not ventas_ok.empty:
                    fig_vend = px.line(ventas_ok, x='Fecha_Limpia', y='Venta', title="Tendencia de Rendimiento", markers=True, color_discrete_sequence=['#00D4FF'])
                    fig_vend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                    st.plotly_chart(fig_vend, use_container_width=True)
                    st.markdown('<div class="detalle-titulo">📅 Detalle de Transacciones</div>', unsafe_allow_html=True)
                    st.dataframe(ventas_ok[['Fecha_Limpia', 'Venta']], use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error en ventas: {e}")

# ==========================================
# MÓDULO 2: REPORTE DE INSTALACIONES
# ==========================================
elif seccion == "🛠️ Reporte de Instalaciones":
    st.markdown('<div class="asesor-header">🛠️ Control de Instalaciones</div>', unsafe_allow_html=True)
    df_inst = cargar_datos(URL_INSTALACIONES, "Instalaciones")
    
    if df_inst is not None:
        if 'FECHA' in df_inst.columns:
            df_inst['FECHA'] = pd.to_datetime(df_inst['FECHA'], errors='coerce')
            df_inst = df_inst.dropna(subset=['FECHA'])
            anios = sorted(df_inst['FECHA'].dt.year.unique(), reverse=True)
            anio_sel = st.sidebar.selectbox("📅 Seleccionar Año:", anios)
            df_anio = df_inst[df_inst['FECHA'].dt.year == anio_sel].copy()

            if 'ESTADO' in df_anio.columns:
                estados_unicos = sorted(df_anio['ESTADO'].dropna().astype(str).unique().tolist())
                estados_sel = st.sidebar.multiselect("📋 Filtrar por Estado:", estados_unicos, default=estados_unicos)
                df_f = df_anio[df_anio['ESTADO'].isin(estados_sel)].copy()
            else: df_f = df_anio.copy()

            st.markdown(f"### 📋 Listado Detallado - Año {anio_sel}")
            st.dataframe(df_f[['CLIENTE', 'PRODUCTO', 'ESTADO']], use_container_width=True, hide_index=True)
            st.markdown("---")

            if 'PRODUCTO' in df_f.columns:
                st.markdown("### 📦 Análisis por Producto")
                df_prod = df_f['PRODUCTO'].value_counts().reset_index()
                df_prod.columns = ['Producto', 'Cantidad']
                fig_prod = px.bar(df_prod, x='Cantidad', y='Producto', orientation='h', text='Cantidad',
                                 color='Producto', color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_prod.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
                st.plotly_chart(fig_prod, use_container_width=True)

                prod_estrella = df_prod.iloc[0]['Producto'] if not df_prod.empty else "N/A"
                st.markdown(f"""
                <div class="card-container">
                    <div class="card-total"><div class="total-label">Producto Estrella</div><div class="total-amount">{prod_estrella}</div></div>
                    <div class="card-total" style="border-left-color: #2196F3;"><div class="total-label">Tipos de Venta</div><div class="total-amount">{len(df_prod)}</div></div>
                </div>
                """, unsafe_allow_html=True)

            if not df_f.empty and 'ESTADO' in df_f.columns:
                st.markdown("### 📊 Rendimiento por Estado")
                df_st = df_f['ESTADO'].value_counts().reset_index()
                df_st.columns = ['ESTADO', 'CANTIDAD']
                total_est = df_st['CANTIDAD'].sum()
                df_st['PORCENTAJE'] = (df_st['CANTIDAD'] / total_est * 100).map('{:.1f}%'.format)
                df_st['ETIQUETA'] = df_st['CANTIDAD'].astype(str) + " (" + df_st['PORCENTAJE'] + ")"
                color_map = {"INSTALADO": "#82e0aa", "RECOORDINAR": "#f7d16d", "POR INSTALAR": "#f2a679", "NO INSTALADO": "#b997f0"}
                fig_status = px.bar(df_st, x='CANTIDAD', y='ESTADO', orientation='h', text='ETIQUETA', color='ESTADO', color_discrete_map=color_map)
                fig_status.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
                st.plotly_chart(fig_status, use_container_width=True)

                total_reg = len(df_f)
                instalados = len(df_f[df_f['ESTADO'].astype(str).str.contains("INSTALADO", case=False, na=False)])
                st.markdown(f"""
                <div class="card-container">
                    <div class="card-total"><div class="total-label">Órdenes</div><div class="total-amount">{total_reg}</div></div>
                    <div class="card-total" style="border-left-color: #4CAF50;"><div class="total-label">Instalados</div><div class="total-amount">{instalados}</div></div>
                    <div class="card-total" style="border-left-color: #FF9800;"><div class="total-label">Otros</div><div class="total-amount">{total_reg-instalados}</div></div>
                </div>
                """, unsafe_allow_html=True)

# ==========================================
# MÓDULO 3: GESTIÓN DE ASESORES
# ==========================================
elif seccion == "📈 Gestión de Asesores":
    st.markdown('<div class="asesor-header">📈 Reporte Diario de Gestión Unificado</div>', unsafe_allow_html=True)
    
    try:
        file_id_g = URL_GESTION.split('/')[-2]
        export_url_g = f'https://docs.google.com/spreadsheets/d/{file_id_g}/export?format=xlsx'
        xls_g = pd.ExcelFile(export_url_g)
        
        hojas_excluir = ['VARIABLES', 'VENTAS', 'TELEVENTAS', 'FACEBOOK', 'RETENCION']
        hojas_asesores = [h for h in xls_g.sheet_names if h.strip().upper() not in hojas_excluir]
        
        asesor_gestion = st.sidebar.selectbox("👤 Seleccionar Asesor para Gestión:", hojas_asesores)
        df_g = cargar_datos(URL_GESTION, asesor_gestion)
        
        if df_g is not None:
            df_g.columns = [str(c).upper() for c in df_g.columns]

            col_fecha_g = 'FECHA INICIO GESTIÓN'
            if col_fecha_g in df_g.columns:
                df_g[col_fecha_g] = pd.to_datetime(df_g[col_fecha_g], errors='coerce').dt.strftime('%d-%m-%Y')

            col_est = 'ESTADO' if 'ESTADO' in df_g.columns else None
            
            if col_est:
                df_g[col_est] = df_g[col_est].astype(str).str.strip().str.upper()
                df_valido = df_g[df_g[col_est] != 'NAN'].copy()
                
                total = len(df_valido)
                firmados = len(df_valido[df_valido[col_est].str.contains("FIRMADO", na=False)])
                gestion = len(df_valido[df_valido[col_est].str.contains("GESTI", na=False)])
                
                st.markdown(f"""
                <div class="card-container">
                    <div class="card-total"><div class="total-label">Total Gestiones</div><div class="total-amount">{total}</div></div>
                    <div class="card-total" style="border-left-color: #4CAF50;"><div class="total-label">Firmados</div><div class="total-amount">{firmados}</div></div>
                    <div class="card-total" style="border-left-color: #FF9800;"><div class="total-label">En Gestión</div><div class="total-amount">{gestion}</div></div>
                </div>
                """, unsafe_allow_html=True)
                
                col_gr, col_tb = st.columns([1.2, 0.8])
                df_counts = df_valido[col_est].value_counts().reset_index()
                df_counts.columns = ['Estado', 'Total']

                with col_gr:
                    fig_g = px.pie(df_counts, values='Total', names='Estado', hole=0.4, title=f"Estados de {asesor_gestion}")
                    fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
                    st.plotly_chart(fig_g, use_container_width=True)
                with col_tb:
                    st.write("#### Resumen de Estados")
                    st.dataframe(df_counts, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("### 📄 Últimas Gestiones Registradas")
            cols_vista = [c for c in ['FECHA INICIO GESTIÓN', 'NOMBRE', 'ESTADO', 'COMENTARIOS'] if c in df_g.columns]
            
            st.dataframe(
                df_g[cols_vista].tail(20) if cols_vista else df_g.tail(20), 
                use_container_width=True,
                hide_index=True
            )
    except Exception as e:
        st.error(f"No se pudo cargar el módulo de gestión: {e}")
