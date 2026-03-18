import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(page_title="Control de Ventas - Inmovision", layout="wide")

# 2. CSS Mejorado
st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; }
    .asesor-header { color: #ffffff; font-size: 26px; font-weight: bold; margin-bottom: 20px; display: flex; align-items: center; gap: 15px; }
    .card-container { display: flex; gap: 20px; margin-bottom: 25px; }
    .card-total { background-color: #f1f3f6; border-radius: 12px; padding: 20px; flex: 1; color: #1a1c24; text-align: center; border-left: 5px solid #4CAF50; }
    .card-general { background-color: #1e2130; border-radius: 12px; padding: 30px; color: #ffffff; text-align: center; border: 1px solid #4CAF50; margin-top: 20px; }
    .total-label { font-weight: 800; font-size: 14px; text-transform: uppercase; color: #666; }
    .total-amount { font-size: 36px; font-weight: bold; color: #000; }
    .total-general-amount { font-size: 45px; font-weight: bold; color: #4CAF50; }
    .detalle-titulo { color: #ffffff; font-size: 20px; font-weight: 600; margin-top: 20px; margin-bottom: 10px; }
    [data-testid="stSidebar"] { background-color: #1a1c24; }
    [data-testid="sidebar-collapsed-control"], [data-testid="stSidebarCollapseButton"] { display: none !important; }
    header, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

URL_DRIVE = "https://docs.google.com/spreadsheets/d/18WS22r1Fml5a9qW3fJOj40d0h7aldJVj/edit?usp=sharing&ouid=109406393059970285073&rtpof=true&sd=true"
URL_LOGO_IMAGEN = "https://lh4.googleusercontent.com/proxy/SeW7l23MFgElfFnJzA8WsomRRdBeiXYsMuQMdiB6_m4J0N0j7RGAB09PNGAO-uUPhKMPITGfAgagRh76fzbODUl3jU3utoz20hT2W99Q7BODxV-g" 
URL_SITIO_WEB = "https://tu-sitio-web.com"

@st.cache_data(ttl=3600)
def cargar_datos(url, nombre_hoja):
    file_id = url.split('/')[-2]
    export_url = f'https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx'
    return pd.read_excel(export_url, sheet_name=nombre_hoja)

try:
    file_id = URL_DRIVE.split('/')[-2]
    export_url = f'https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx'

    # --- SIDEBAR: LOGO ---
    st.sidebar.markdown(
        f'<div style="text-align: center; padding-bottom: 20px;"><a href="{URL_SITIO_WEB}" target="_blank"><img src="{URL_LOGO_IMAGEN}" style="width: 85%; max-width: 250px;"></a></div>',
        unsafe_allow_html=True
    )

    # --- MANEJO DE HOJAS ---
    xls = pd.ExcelFile(export_url)
    hojas_reales = xls.sheet_names
    hojas_display = [str(h).lower() for h in hojas_reales]
    mapa_hojas = dict(zip(hojas_display, hojas_reales))

    mes_sel_display = st.sidebar.selectbox("📅 Seleccionar Mes:", hojas_display)
    mes_real = mapa_hojas[mes_sel_display]
    
    df = cargar_datos(URL_DRIVE, mes_real)

    # --- 1. LIMPIEZA DE COLUMNAS ---
    df.columns = [str(c).strip() for c in df.columns]
    col_vendedor = df.columns[0]

    # --- 2. LIMPIEZA DE DATOS ---
    df[col_vendedor] = df[col_vendedor].astype(str).str.strip().str.upper()

    vendedores_permitidos = [
        "ALEXANDRA REINO", "ANDREA MENDOZA", "CESAR VERA", "DIANA RIVERA", 
        "EDISON SACA", "FRANKLIN QUEZADA", "GLENDA RAMOS AYORA", "JENNIFER ATANCURI", 
        "JORGE GARCIA", "LAURA MORAN", "MANCHENO KARLA", "MARIA JOSE PEÑAFIEL", 
        "MELANY GUZHÑAY", "NANCY JARAMA", "PRISCILA RAMOS", "SILVIA YUNGA", 
        "STALIN ROJAS", "SUSANA PACURUCO", "SUSANA PACURUCU", "VERONICA MALO", 
        "WILLIAM BRITO", "WILLIAN MOLINA","RAMOS AYORA GLENDA"
    ]

    vendedores_existentes = df[col_vendedor].unique()
    vendedores_db = sorted([v for v in vendedores_existentes if v in vendedores_permitidos])
    
    st.sidebar.markdown("---")
    ver_todo = st.sidebar.button("📊 Ver Resumen General")
    
    if not vendedores_db:
        st.sidebar.warning("⚠️ No se encontraron vendedores válidos.")
        vendedor_sel = None
    else:
        vendedor_sel = st.sidebar.selectbox("👤 Seleccionar Vendedor:", vendedores_db)

    # --- LÓGICA DE VISUALIZACIÓN ---
    if ver_todo:
        st.markdown('<div class="asesor-header">📊 Resumen General de Ventas</div>', unsafe_allow_html=True)
        col_total_name = [c for c in df.columns if 'TOTAL' in c.upper()][0]
        
        resumen = df[df[col_vendedor].isin(vendedores_permitidos)][[col_vendedor, col_total_name]]
        resumen.columns = ['Vendedor', 'Monto Total']
        resumen = resumen[resumen['Monto Total'] > 0].sort_values(by='Monto Total', ascending=False)
        total_general_mes = resumen['Monto Total'].sum()
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.write("### Ranking de Ventas")
            st.dataframe(resumen, use_container_width=True, hide_index=True)
        with col2:
            fig_pie = px.pie(resumen, values='Monto Total', names='Vendedor', title="Participación por Vendedor", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        st.markdown(f"""
            <div class="card-general">
                <div class="total-label" style="color: #bbb;">Venta Total Consolidada del Mes</div>
                <div class="total-general-amount">${total_general_mes:,.2f}</div>
                <div style="font-size: 14px; color: #888; margin-top: 10px;">Hoja: {mes_sel_display}</div>
            </div>""", unsafe_allow_html=True)

    elif vendedor_sel:
        st.markdown(f'<div class="asesor-header">👤 Asesor: {vendedor_sel}</div>', unsafe_allow_html=True)
        
        columnas_fecha = [c for c in df.columns if any(m in str(c).lower() for m in ['-','/']) or 
                         any(m in str(c).lower() for m in ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'])]
        columnas_fecha = [c for c in columnas_fecha if c != col_vendedor]
        
        datos_fila = df[df[col_vendedor] == vendedor_sel][columnas_fecha]
        
        datos_v = datos_fila.T.reset_index()
        datos_v = datos_v.iloc[:, :2] 
        datos_v.columns = ['Fecha', 'Venta']
        
        # --- CORRECCIÓN DE FECHAS (SIN HORA Y FORMATO DÍA-MES-AÑO) ---
        # 1. Convertimos a formato fecha real para ordenar correctamente
        datos_v['Fecha_DT'] = pd.to_datetime(datos_v['Fecha'], errors='coerce')
        
        # 2. Creamos la columna visual limpia (DD-MM-YYYY)
        datos_v['Fecha_Limpia'] = datos_v['Fecha_DT'].dt.strftime('%d-%m-%Y')
        
        datos_v['Venta'] = pd.to_numeric(datos_v['Venta'], errors='coerce').fillna(0)
        
        # Filtramos solo ventas > 0 y ordenamos por la fecha real
        ventas_realizadas = datos_v[datos_v['Venta'] > 0].copy().sort_values('Fecha_DT')
        
        total_dinero = ventas_realizadas['Venta'].sum()
        numero_ventas = len(ventas_realizadas)

        st.markdown(f"""
            <div class="card-container">
                <div class="card-total">
                    <div class="total-label">Monto Total Vendido</div>
                    <div class="total-amount">${total_dinero:,.2f}</div>
                </div>
                <div class="card-total" style="border-left-color: #2196F3;">
                    <div class="total-label">Cantidad de Ventas</div>
                    <div class="total-amount">{numero_ventas}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        if not ventas_realizadas.empty:
            # Usamos la fecha limpia para el gráfico
            fig_bar = px.bar(ventas_realizadas, x='Fecha_Limpia', y='Venta', 
                             title="Rendimiento Diario", 
                             labels={'Fecha_Limpia': 'Fecha', 'Venta': 'Monto ($)'},
                             color_discrete_sequence=['#4CAF50'])
            st.plotly_chart(fig_bar, use_container_width=True)
            
            st.markdown('<div class="detalle-titulo">📅 Detalle de Ventas Diarias</div>', unsafe_allow_html=True)
            
            # Mostramos la tabla solo con la fecha formateada y la venta
            detalle_final = ventas_realizadas[['Fecha_Limpia', 'Venta']].rename(columns={'Fecha_Limpia': 'Fecha'})
            st.dataframe(detalle_final, use_container_width=True, hide_index=True)
        else:
            st.info(f"No se encontraron ventas para {vendedor_sel} en este periodo.")

except Exception as e:
    st.error(f"Se detectó un problema: {e}")
