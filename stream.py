import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sistema de Biorremediação", layout="wide")
st.title("🌱 Sistema de Biorremediação: Simulador Edge AI")

# --- CONAMA (Atualização Setembro 2026) ---
LIMITE_DQO = 250.0   
LIMITE_P = 1.0       
LIMITE_N = 20.0      
LIMITE_S = 1.0       

# --- CARGA POLUIDORA INICIAL (Dia 0) ---
st.sidebar.header("⚙️ Carga Poluidora (Dia 0)")
DQO_INICIAL = st.sidebar.number_input("DQO (mg/L)", value=20000.0, step=100.0)
P_INICIAL = st.sidebar.number_input("Fósforo (mg/L)", value=650.0, step=10.0)
N_INICIAL = st.sidebar.number_input("Nitrogénio (mg/L)", value=5500.0, step=100.0)
S_INICIAL = st.sidebar.number_input("Enxofre (mg/L)", value=250.0, step=10.0)

st.sidebar.divider()

# --- SENSORES EM TEMPO REAL ---
st.sidebar.header("🎛️ Sensores do Tanque")
# Mudei o valor inicial do Dia para 7.0 (meio do processo) para ver bem a variação
dia = st.sidebar.slider("Dia do Processo", 0.0, 15.0, 7.0, 0.5)
ph = st.sidebar.slider("Nível de pH", 4.0, 10.0, 7.0, 0.1)
temp = st.sidebar.slider("Temperatura (°C)", 20.0, 35.0, 26.0, 0.5)
turbidez = st.sidebar.slider("Turbidez (NTU)", 0, 3500, 1000, 50)
co2 = st.sidebar.slider("Gás CO2 (ppm)", 300, 1200, 1000, 10)

# ==========================================
# CÁLCULO DIRETO (SEM BOTÃO!)
# Assim que arrastar um slider, as barras do gráfico dançam.
# Estas fórmulas provisórias foram ajustadas para reagirem muito mais aos sliders.
# (No futuro, você substituirá isto pelo seu modelo Keras: model.predict([dia, ph, temp...]))
# ==========================================
dqo_saida = max(50.0, DQO_INICIAL - (dia * 1300) + (turbidez * 1.5) - (temp * 15))
p_saida = max(0.1, P_INICIAL - (dia * 40) - (ph * 5) + (temp * 1.5))
n_saida = max(5.0, N_INICIAL - (dia * 300) + (co2 * 0.8) - (turbidez * 0.2))
s_saida = max(0.1, S_INICIAL - (dia * 15) - (ph * 2) + (co2 * 0.05))

# --- CÁLCULO DE EFICIÊNCIA DE REMOÇÃO (%) ---
eficiencia_dqo = ((DQO_INICIAL - dqo_saida) / DQO_INICIAL) * 100
eficiencia_p = ((P_INICIAL - p_saida) / P_INICIAL) * 100
eficiencia_n = ((N_INICIAL - n_saida) / N_INICIAL) * 100
eficiencia_s = ((S_INICIAL - s_saida) / S_INICIAL) * 100

# --- VERIFICAÇÃO CONAMA ---
aprovado_conama = (dqo_saida <= LIMITE_DQO and p_saida <= LIMITE_P and n_saida <= LIMITE_N and s_saida <= LIMITE_S)

if aprovado_conama:
    st.success("✅ STATUS CONAMA: Aprovado. Efluente dentro dos novos padrões para descarte (Set/2026).")
else:
    st.error("🚨 STATUS CONAMA: Reprovado. Efluente ainda fora dos padrões de descarte.")

# --- MÉTRICAS INTEGRADAS ---
st.subheader("Resultados de Saída e Performance")
r1, r2, r3, r4 = st.columns(4)

r1.metric("DQO (mg/L)", f"{dqo_saida:.1f}", f"{dqo_saida - LIMITE_DQO:.1f} do limite", delta_color="inverse")
r1.caption(f"**🌱 Eficiência:** `{eficiencia_dqo:.1f}%`")

r2.metric("Fósforo (mg/L)", f"{p_saida:.1f}", f"{p_saida - LIMITE_P:.1f} do limite", delta_color="inverse")
r2.caption(f"**🌱 Eficiência:** `{eficiencia_p:.1f}%`")

r3.metric("Nitrogénio (mg/L)", f"{n_saida:.1f}", f"{n_saida - LIMITE_N:.1f} do limite", delta_color="inverse")
r3.caption(f"**🌱 Eficiência:** `{eficiencia_n:.1f}%`")

r4.metric("Enxofre (mg/L)", f"{s_saida:.1f}", f"{s_saida - LIMITE_S:.1f} do limite", delta_color="inverse")
r4.caption(f"**🌱 Eficiência:** `{eficiencia_s:.1f}%`")

st.divider()

# --- TABELA COMPARATIVA ---
st.subheader("Análise Regulatória e Biológica")
tabela_markdown = f"""
| Parâmetro | Limite Legal (Set/2026) | Faixa Ideal (Biorremediação) | Status Atual |
| :--- | :--- | :--- | :--- |
| **DQO** | ≤ {LIMITE_DQO} mg/L | 50 - 150 mg/L | **{dqo_saida:.1f} mg/L** |
| **Fósforo (P)** | ≤ {LIMITE_P} mg/L | 0.1 - 0.5 mg/L | **{p_saida:.1f} mg/L** |
| **Nitrogénio (N)**| ≤ {LIMITE_N} mg/L | 5.0 - 10.0 mg/L | **{n_saida:.1f} mg/L** |
| **Enxofre (S)** | ≤ {LIMITE_S} mg/L | < 0.5 mg/L | **{s_saida:.1f} mg/L** |
"""
st.markdown(tabela_markdown)

st.divider()

# --- GRÁFICO DE BARRAS DINÂMICO ---
st.subheader("Visualização dos Nutrientes Restantes")
# Adicionámos o DQO ao gráfico e usámos a vista nativa do Streamlit que ajusta melhor as escalas
dados_grafico = pd.DataFrame({
    "Concentração (mg/L)": [dqo_saida, p_saida, n_saida, s_saida]
}, index=["DQO", "Fósforo", "Nitrogénio", "Enxofre"])

st.bar_chart(dados_grafico)