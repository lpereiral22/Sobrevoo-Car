import streamlit as st
import hashlib
import time
import folium
import json
from streamlit_folium import st_folium
from PIL import Image

# 1. Configuração da página institucional e layout fluido
st.set_page_config(
    page_title="SobreVoo CAR Transformando o Produtor Rural em um Colaborador Ativo", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Injeção de CSS para identidade visual Gov.br / SICAR baseado na tela oficial
st.markdown("""
    <style>
    /* Forçar fundo branco e fontes limpas institucionais */
    .stApp {
        background-color: #FFFFFF;
        color: #333333;
    }
    html, body, [data-testid="stMarkdownContainer"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Topo azul oficial do Gov.br */
    .gov-bar {
        background-color: #004b82;
        padding: 8px 20px;
        color: white;
        font-family: 'Segoe UI', sans-serif;
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 20px;
        border-radius: 4px;
    }
    h1 {
        color: #004b82 !important;
        font-weight: 700 !important;
    }
    h2 {
        color: #004b82 !important;
    }
    h3 {
        color: #2E7D32 !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #2E7D32;
        padding-bottom: 5px;
    }
    h4, p, span, label, caption {
        color: #222222 !important;
    }
    /* Customização dos botões para o Verde Oficial das Ações do SICAR (image_354fc1.jpg) */
    div.stButton > button:first-child {
        background-color: #2E7D32 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 4px !important;
        border: 1px solid #1B5E20 !important;
        padding: 0.5rem 2rem !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #1B5E20 !important;
        color: white !important;
    }
    /* Caixas e alertas informativos estilizados de forma governamental */
    .stAlert {
        background-color: #F8F9FA !important;
        border-left: 5px solid #2E7D32 !important;
        color: #222222 !important;
    }
    code {
        color: #004b82 !important;
        background-color: #F5F5F5 !important;
        border-left: 3px solid #004b82;
    }
    .report-box {
        background-color: #ffffff;
        padding: 30px;
        border: 1px solid #DEE2E6;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Simulação da barra de navegação superior do Gov.br
st.markdown("<div class='gov-bar'>gov.br &nbsp;|&nbsp; Regularização Ambiental - Cadastro Ambiental Rural</div>", unsafe_allow_html=True)

# Inicialização das variáveis de estado (Session State)
if "dados_geojson" not in st.session_state:
    st.session_state.dados_geojson = None

if "voo_autorizado" not in st.session_state:
    st.session_state.voo_autorizado = False

if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "upload"

if "hash_gerado" not in st.session_state:
    st.session_state.hash_gerado = ""

if "codigo_car_salvo" not in st.session_state:
    st.session_state.codigo_car_salvo = ""

if "piloto_salvo" not in st.session_state:
    st.session_state.piloto_salvo = ""

if "sarpas_salvo" not in st.session_state:
    st.session_state.sarpas_salvo = ""

# ==========================================
# CARREGAMENTO DAS LOGOS LOCAIS
# ==========================================
# Tratamento com try/except para evitar crash caso os arquivos locais não existam durante o teste
# ==========================================
# CARREGAMENTO DAS LOGOS LOCAIS (CORRIGIDO)
# ==========================================

# Usando o caminho exato e as extensões corretas que você passou
# Mude para caminhos que funcionem em qualquer servidor:
logo_car = Image.open("sobrevoo_car/imagens/logo_car.png")
logo_sobrevoo = Image.open("sobrevoo_car/imagens/logo_sobrevoo.jpg")
# ==========================================
# PÁGINA 1: TELA DE UPLOAD E VALIDAÇÃO
# ==========================================
if st.session_state.pagina_atual == "upload":

    # Correção: Criação das colunas principais do cabeçalho que estavam faltando
    header_col1, header_col2 = st.columns([8, 4])

    with header_col1:
        # Colunas internas para posicionar as duas logos lado a lado
        logo_col1, logo_col2 = st.columns([1, 1])
        with logo_col1:
            if logo_car:
                st.image(logo_car, width=500)
            else:
                st.write("[Logo CAR]")
        with logo_col2:
            if logo_sobrevoo:
                st.image(logo_sobrevoo, width=150)
            else:
                st.write("[Logo SobreVoo]")

        st.markdown("<h1>SobreVoo CAR<br><span style='font-size: 26px; font-weight: 600;'>Produtor Ativo Cadastro Vivo</span></h1>", unsafe_allow_html=True)        
        st.caption("Proposta de Solução Para o HaCARthon 2026 - Soluções Para o Cadastro Rural Ambiental")

    with header_col2:
        st.markdown("""
            <div style="text-align: right; margin-top: 10px;">
                <img src="https://www.gov.br/++theme++padrao_govbr/img/govbr-logo-large.png" width="120" alt="Gov Br">
                <p style="font-size: 11px; color: #666; margin-top: 5px;">Ambiente de Homologação</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin-top: 0; border: 1px solid #004b82;'>", unsafe_allow_html=True)

    # Caixa de Seleção do Tipo de Coleta Exigida
    tipo_coleta = st.radio(
        "**Selecione o Tipo de Imagem Georreferenciadas:**",
        ["Imagens em Campo (Celular)", "Imagens Aéreas (Drone)"],
        horizontal=True
    )

    # Distribuição de Dados (Colunas da Interface)
    col1, col2 = st.columns([5, 7])

    with col1:
        # LÓGICA CONDICIONAL: Se for Drone, exige validação prévia. Se for Celular, libera direto.
        if tipo_coleta == "Imagens Aéreas (Drone)":
            st.markdown("### I. Comprovação de Conformidade Aeronáutica (ICA 100-40)")
            st.write("Em cumprimento às normas do DECEA e da ANAC, o recebimento de malhas geoespaciais exige a validação do plano de voo.")
            
            piloto = st.text_input("CPF ou Código do Piloto Remoto (SARPAS):", placeholder="000.000.000-00", value="123.456.789-00")
            num_sarpas = st.text_input("Número do Protocolo de Autorização de Voo (DECEA):", placeholder="SARPAS-2026-XXXXX", value="SARPAS-2026-98745")
            
            validar_api = st.button("Autenticar Operação")
            
            if validar_api:
                if piloto and num_sarpas:
                    with st.spinner("Conectando ao barramento de APIs unificadas do DECEA..."):
                        time.sleep(1.2)
                    st.success("✔️ [INTEGRAÇÃO DECEA] Protocolo validado. Voo em conformidade (Teto máximo: 120 metros).")
                    st.session_state.voo_autorizado = True
                    st.session_state.piloto_salvo = piloto
                    st.session_state.sarpas_salvo = num_sarpas
                else:
                    st.error("Erro de validação: Os campos são obrigatórios.")
        else:
            # Rito simplificado para imagens de celular em solo
            st.session_state.voo_autorizado = True
            st.session_state.piloto_salvo = "Dispositivo Móvel Cidadão"
            st.session_state.sarpas_salvo = "Isento - Coleta Terrestre"

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### II. Identificação e Upload")
        
        if st.session_state.voo_autorizado:
            codigo_car = st.text_input(
                "Código do Imóvel Rural (Recibo CAR):", 
                value="BR-5210567-3A2B.C4D5.E6F7.8901.G2H3.I4J5.K6L7"
            )
            st.session_state.codigo_car_salvo = codigo_car
            
            label_upload = "Selecione a imagem do campo (.jpeg):" if tipo_coleta == "Imagens em Campo (Celular)" else "Selecione a camada ortomosaico processada na borda (.geojson):"
            
            # Ajustado dinamicamente o tipo aceito para evitar travar se for celular
            tipos_aceitos = ["jpeg", "jpg"] if tipo_coleta == "Imagens em Campo (Celular)" else ["geojson"]
            uploaded_file = st.file_uploader(label_upload, type=tipos_aceitos)
            
            if uploaded_file is not None:
                st.success("Arquivo carregado na memória.")
                
                file_bytes = uploaded_file.getvalue()
                st.session_state.hash_gerado = hashlib.sha256(file_bytes).hexdigest()
                
                if tipo_coleta == "Imagens Aéreas (Drone)":
                    try:
                        uploaded_file.seek(0)
                        st.session_state.dados_geojson = json.loads(uploaded_file.read().decode("utf-8"))
                    except Exception as e:
                        st.error("Erro ao processar a estrutura do arquivo GeoJSON.")
                
                st.markdown("#### Integridade do Dado Público")
                st.info(f"O arquivo foi indexado com sucesso ao protocolo do CAR.")
                st.markdown(f"**Imóvel Alvo:** `{codigo_car}`")
                st.code(f"SHA-256: {st.session_state.hash_gerado.upper()}", language="text")
                
                st.markdown("<br>", unsafe_allow_html=True)
                enviar_sicar = st.button("🚀 TRANSMITIR PARA O SICAR")
                if enviar_sicar:
                    with st.spinner("Gravando metadados e gerando protocolo permanente..."):
                        time.sleep(1.8)
                    st.session_state.pagina_atual = "relatorio"
                    st.rerun()
        else:
            st.info("Aguardando liberação de conformidade aérea da ICA 100-40 para desbloquear os canais de identificação e upload.")

    with col2:
        st.markdown("### III. Visão de Acurácia do Solo e Malha Fundiária")
        st.write("Interpretação e validação rápida da cobertura do solo para analistas ambientais.")
        
        # URL da camada de Satélite Mundial da Esri
        satelite_tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
        satelite_attr = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EBP, and the GIS User Community'

        if st.session_state.dados_geojson:
            # Lógica de centralização automática
            try:
                coords = []
                for feature in st.session_state.dados_geojson['features']:
                    geom_type = feature['geometry']['type']
                    if geom_type == 'Polygon':
                        for poly in feature['geometry']['coordinates']:
                            coords.extend(poly)
                    elif geom_type == 'MultiPolygon':
                        for multi in feature['geometry']['coordinates']:
                            for poly in multi:
                                coords.extend(poly)
                
                if coords:
                    avg_lng = sum(p[0] for p in coords) / len(coords)
                    avg_lat = sum(p[1] for p in coords) / len(coords)
                    centro_mapa = [avg_lat, avg_lng]
                    zoom_ideal = 15 
                else:
                    centro_mapa = [-16.4523, -49.9376]
                    zoom_ideal = 15
            except Exception:
                centro_mapa = [-16.4523, -49.9376]
                zoom_ideal = 15

            m = folium.Map(location=centro_mapa, zoom_start=zoom_ideal, tiles=satelite_tiles, attr=satelite_attr)
            
            try:
                chaves_prop = list(st.session_state.dados_geojson['features'][0]['properties'].keys())[:2]
                aliases_prop = [f"{k}:" for k in chaves_prop]
            except Exception:
                chaves_prop, aliases_prop = [], []

            folium.GeoJson(
                st.session_state.dados_geojson,
                name="SobreVoo CAR - Camadas",
                style_function=lambda x: {
                    'fillColor': '#2E7D32' if 'properties' in x and 'Tipo' in x['properties'] and x['properties']['Tipo'] == 'Área de Preservação' else '#004b82',
                    'color': '#1B5E20' if 'properties' in x and 'Tipo' in x['properties'] and x['properties']['Tipo'] == 'Área de Preservação' else '#004b82',
                    'weight': 3, 
                    'fillOpacity': 0.35
                },
                tooltip=folium.GeoJsonTooltip(fields=chaves_prop, aliases=aliases_prop) if chaves_prop else None
            ).add_to(m)
        else:
            # Visão geral em modo Satélite antes do upload
            m = folium.Map(location=[-15.7801, -47.9292], zoom_start=4, tiles=satelite_tiles, attr=satelite_attr)
            
        st_folium(m, width="100%", height=480, key="mapa_sicar_satelite")
        
        st.markdown("""
            <div style="background-color: #F8F9FA; padding: 15px; border-left: 4px solid #2E7D32; border-radius: 4px; margin-top: 15px; border: 1px solid #DEE2E6; border-left-width: 4px;">
                <p style="font-size: 13px; margin: 0; color: #333;">
                    <strong>Nota Técnica de Arquitetura:</strong> O mapa em modo Satélite permite confrontar em tempo real a alta precisão dos polígonos do drone contra a base de referência, destacando com precisão cirúrgica as Áreas de Preservação Permanente (APP) e Reserva Legal (RL).
                </p>
            </div>
        """, unsafe_allow_html=True)


# ==========================================
# PÁGINA 2: RELATÓRIO TÉCNICO DE CONFORMIDADE
# ==========================================
elif st.session_state.pagina_atual == "relatorio":
    
    # Botão de retorno no topo (oculto na impressão por padrão)
    if st.button("⬅️ Voltar ao Painel de Transmissão"):
        st.session_state.pagina_atual = "upload"
        st.session_state.dados_geojson = None
        st.session_state.voo_autorizado = False
        st.rerun()
        
    st.markdown("---")
    
    # Bloco principal do Relatório (Simula a folha de papel)
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://www.gov.br/sicar/pt-br/logo-sicar.png" width="180" alt="Logo SICAR">
            <h2 style="color: #004b82; margin-top: 10px; font-size: 22px; font-weight: 700;">
                RELATÓRIO TÉCNICO DE VALIDAÇÃO GEOESPACIAL (MÓDULO DRONE)
            </h2>
            <p style="font-size: 13px; color: #555; margin-bottom: 5px;">
                Documento gerado automaticamente pelo Ecossistema de BENS PÚBLICOS DIGITAIS do CAR
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='border-bottom: 2px dashed #004b82; margin-bottom: 25px;'></div>", unsafe_allow_html=True)
    
    # Tabela de Dados estruturada
    with st.container():
        rep_col1, rep_col2 = st.columns([1, 2])
        
        with rep_col1:
            st.markdown("**Código Recibo CAR:**")
            st.markdown("**Status da Transmissão:**")
            st.markdown("**Data/Hora do Registro:**")
            st.markdown("**Operador Responsável:**")
            st.markdown("**Autorização de Voo:**")
            
        with rep_col2:
            st.markdown(f"`{st.session_state.codigo_car_salvo}`")
            st.markdown("<span style='color: #2E7D32; font-weight: bold;'>✔️ SUCESSO - DADO PROTOCOLADO</span>", unsafe_allow_html=True)
            st.markdown(f"{time.strftime('%d/%m/%Y às %H:%M:%S')} (Horário de Brasília)")
            st.markdown(f"CPF ativo nº {st.session_state.piloto_salvo}")
            st.markdown(f"`{st.session_state.sarpas_salvo}` (Protocolo Homologado DECEA)")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # ==========================================
    # MAPA IMPRESSO NO RELATÓRIO
    # ==========================================
    st.markdown("#### 🗺️ Cartografia Homologada (Malha de Campo Injetada)")
    st.write("Abaixo consta o registro geográfico dos polígonos validados que foram anexados ao recibo do CAR do imóvel:")
    
    # Recriando o mapa estático/interativo focado no GeoJSON enviado para sair no relatório impresso
    satelite_tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    satelite_attr = 'Tiles &copy; Esri &mdash; Source: Esri'

    if st.session_state.dados_geojson:
        try:
            coords = []
            for feature in st.session_state.dados_geojson['features']:
                geom_type = feature['geometry']['type']
                if geom_type == 'Polygon':
                    for poly in feature['geometry']['coordinates']:
                        coords.extend(poly)
                elif geom_type == 'MultiPolygon':
                    for multi in feature['geometry']['coordinates']:
                        for poly in multi:
                            coords.extend(poly)
            
            if coords:
                avg_lng = sum(p[0] for p in coords) / len(coords)
                avg_lat = sum(p[1] for p in coords) / len(coords)
                centro_relatorio = [avg_lat, avg_lng]
            else:
                centro_relatorio = [-16.4523, -49.9376]
        except Exception:
            centro_relatorio = [-16.4523, -49.9376]
            
        # Mapa com tamanho fixo ideal para visualização em folha A4
        m_relatorio = folium.Map(location=centro_relatorio, zoom_start=15, tiles=satelite_tiles, attr=satelite_attr)
        
        folium.GeoJson(
            st.session_state.dados_geojson,
            style_function=lambda x: {
                'fillColor': '#2E7D32',
                'color': '#1B5E20',
                'weight': 3, 
                'fillOpacity': 0.4
            }
        ).add_to(m_relatorio)
        
        # Renderiza o mapa fixo no relatório
        st_folium(m_relatorio, width="100%", height=350, key="mapa_relatorio_print")
    else:
        st.warning("Nenhum dado geográfico (GeoJSON) foi carregado para este relatório.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Seção de Rastreabilidade Criptográfica (Hash)
    st.markdown("#### 📌 Assinatura Digital e Rastreabilidade Criptográfica (SHA-256)")
    st.write(
        "A integridade jurídica e a imutabilidade da evidência apresentada estão integralmente asseguradas "
        "pela impressão digital criptográfica permanente abaixo:"
    )
    
    st.markdown(f"""
        <div style="background-color: #111; padding: 15px; border-radius: 4px; text-align: center; margin: 15px 0;">
            <code style="color: #00ff00; font-family: monospace; font-size: 15px; font-weight: bold;">
                HASH SECURE ID: {st.session_state.hash_gerado.upper() if st.session_state.hash_gerado else "NÃO GERADO"}
            </code>
        </div>
    """, unsafe_allow_html=True)
    
    # Seção de Amparo Jurídico
    st.markdown("#### ⚖️ Certificação de Amparo Jurídico contra Sanções Automáticas")
    st.markdown(
        "Este documento serve como contraprova jurídica oficial de acurácia de solo centimétrica. "
        "Fica atestado que os limites das feições de **Reserva Legal (RL)** e **Áreas de Preservação Permanente (APP)** "
        "mapeadas corrigem quaisquer distorções provindas de imagens de satélite defasadas na base de referência."
    )
    
    # Rodapé do Relatório
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; font-size: 12px; color: #777;">
            <p>____________________________________________________</p>
            <p>Sistema Autônomo de Auditoria e Geoprocessamento - SobreVoo CAR</p>
            <p>Selo de Segurança da Informação Governamental - Código Aberto</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Opção prática para simular a impressão
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🖨️ Emitir Cópia PDF / Imprimir Relatório"):
        st.success("Documento pronto para impressão.")
        # Script JS que abre a janela de impressão nativa do navegador capturando todo o layout
        st.components.v1.html("<script>window.print();</script>", height=0)
