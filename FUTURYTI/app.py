import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Inmovision - Dashboard Corporativo", layout="wide")

# 2. CSS PARA DISEÑO UNIFICADO
st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; }
    .asesor-header { color: #ffffff; font-size: 26px; font-weight: bold; margin-bottom: 20px; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
    .card-container { display: flex; gap: 20px; margin-bottom: 25px; }
    .card-total { background-color: #f1f3f6; border-radius: 12px; padding: 20px; flex: 1; color: #1a1c24; text-align: center; border-left: 5px solid #4CAF50; }
    .total-label { font-weight: 800; font-size: 14px; text-transform: uppercase; color: #666; }
    .total-amount { font-size: 32px; font-weight: bold; color: #000; }
    .total-general-amount { font-size: 45px; font-weight: bold; color: #4CAF50; }
    .card-general { background-color: #1a1c24; border: 1px solid #4CAF50; border-radius: 12px; padding: 25px; text-align: center; margin-bottom: 20px; }
    [data-testid="stSidebar"] { background-color: #1a1c24; }
    .logo-sidebar { display: block; margin-left: auto; margin-right: auto; width: 150px; margin-bottom: 20px; filter: drop-shadow(0px 4px 8px rgba(0, 0, 0, 0.5)); }
    header, footer {visibility: hidden;}
    .detalle-titulo { color: #ffffff; font-size: 20px; font-weight: 600; margin-top: 20px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONFIGURACIÓN DE RECURSOS
URL_VENTAS = "https://docs.google.com/spreadsheets/d/18WS22r1Fml5a9qW3fJOj40d0h7aldJVj/edit?usp=sharing"
URL_INSTALACIONES = "https://docs.google.com/spreadsheets/d/1QqH8lGktix5YLV7seIL9cXUxWCaANauM/edit?usp=sharing"
URL_LOGO = "https://lh4.googleusercontent.com/proxy/SeW7l23MFgElfFnJzA8WsomRRdBeiXYsMuQMdiB6_m4J0N0j7RGAB09PNGAO-uUPhKMPITGfAgagRh76fzbODUl3jU3utoz20hT2W99Q7BODxV-g" 

# Lista de vendedores autorizados para la sección de ventas
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
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        return None

# --- NAVEGACIÓN LATERAL ---
st.sidebar.markdown(f'<img src="{URL_LOGO}" class="logo-sidebar">', unsafe_allow_html=True)
st.sidebar.title("Menú Principal")
seccion = st.sidebar.radio("Seleccione un Módulo:", ["📊 Control de Ventas", "🛠️ Reporte de Instalaciones"])
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
                    
                    st.markdown(f'''
                        <div class="card-general">
                            <div class="total-label" style="color:#4CAF50">Venta Total Consolidada</div>
                            <div class="total-general-amount">${resumen["Monto Total"].sum():,.2f}</div>
                        </div>''', unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.dataframe(resumen, use_container_width=True, hide_index=True)
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

                st.markdown(f'''
                    <div class="card-container">
                        <div class="card-total">
                            <div class="total-label">Monto Total Vendido</div>
                            <div class="total-amount">${ventas_ok["Venta"].sum():,.2f}</div>
                        </div>
                        <div class="card-total" style="border-left-color: #2196F3;">
                            <div class="total-label">Cantidad de Ventas</div>
                            <div class="total-amount">{len(ventas_ok)}</div>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
                
                if not ventas_ok.empty:
                    fig_vend = px.bar(ventas_ok, x='Fecha_Limpia', y='Venta', 
                                    title="Rendimiento por Fecha", 
                                    color_discrete_sequence=['#4CAF50'],
                                    labels={'Fecha_Limpia': 'Fecha', 'Venta': 'Monto ($)'})
                    fig_vend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                    st.plotly_chart(fig_vend, use_container_width=True)
                    
                    st.markdown('<div class="detalle-titulo">📅 Detalle de Transacciones</div>', unsafe_allow_html=True)
                    st.dataframe(ventas_ok[['Fecha_Limpia', 'Venta']].rename(columns={'Fecha_Limpia':'Fecha'}), use_container_width=True, hide_index=True)
                else:
                    st.info("Sin registros de ventas para este periodo.")

    except Exception as e:
        st.error(f"Error cargando módulo de ventas: {e}")

# ==========================================
# MÓDULO 2: REPORTE DE INSTALACIONES
# ==========================================
elif seccion == "🛠️ Reporte de Instalaciones":
    st.markdown('<div class="asesor-header">🛠️ Control de Instalaciones</div>', unsafe_allow_html=True)
    df_inst = cargar_datos(URL_INSTALACIONES, "Instalaciones")
    
    if df_inst is not None:
        df_inst.columns = [str(c).strip().upper() for c in df_inst.columns]
        
        if 'FECHA' in df_inst.columns:
            df_inst['FECHA'] = pd.to_datetime(df_inst['FECHA'], errors='coerce')
            df_inst = df_inst.dropna(subset=['FECHA'])
            
            # Filtros Sidebar
            anios = sorted(df_inst['FECHA'].dt.year.unique(), reverse=True)
            anio_sel = st.sidebar.selectbox("📅 Seleccionar Año:", anios)
            
            df_anio = df_inst[df_inst['FECHA'].dt.year == anio_sel].copy()
            
            if 'ESTADO' in df_anio.columns:
                estados_unicos = sorted(df_anio['ESTADO'].dropna().astype(str).unique().tolist())
                estados_sel = st.sidebar.multiselect("📋 Filtrar por Estado:", estados_unicos, default=estados_unicos)
                df_f = df_anio[df_anio['ESTADO'].isin(estados_sel)].copy()
            else:
                df_f = df_anio.copy()

            df_f['FECHA_L'] = df_f['FECHA'].dt.strftime('%d/%m/%Y')
            
            # Métricas
            total_reg = len(df_f)
            instalados = len(df_f[df_f['ESTADO'].astype(str).str.contains("INSTALADO", case=False, na=False)])
            otros = total_reg - instalados

            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f'<div class="card-total"><div class="total-label">Total Órdenes</div><div class="total-amount">{total_reg}</div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="card-total" style="border-left-color: #4CAF50;"><div class="total-label">Instalados</div><div class="total-amount">{instalados}</div></div>', unsafe_allow_html=True)
            with m3:
                st.markdown(f'<div class="card-total" style="border-left-color: #FF9800;"><div class="total-label">Otros / Pendientes</div><div class="total-amount">{otros}</div></div>', unsafe_allow_html=True)

            st.markdown(f"### 📋 Listado de Instalaciones - Año {anio_sel}")
            cols_ver = ['FECHA_L', 'CLIENTE', 'PRODUCTO', 'ESTADO']
            cols_finales = [c for c in cols_ver if c in df_f.columns]
            
            st.dataframe(df_f[cols_finales].rename(columns={'FECHA_L': 'FECHA'}), use_container_width=True, hide_index=True)
            
            if not df_f.empty and 'ESTADO' in df_f.columns:
                fig_inst = px.pie(df_f, names='ESTADO', title="Distribución de Estados", hole=0.4,
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_inst.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig_inst, use_container_width=True)
        else:
            st.error("No se encontró la columna 'FECHA' en el archivo de instalaciones.")
    else:  
        st.error("No se pudo conectar con la base de datos de Instalaciones.")
