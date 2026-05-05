import streamlit as st
import requests

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap');
    
    .stApp {
        background-color: #001100;
        color: #00FF41;
        font-family: 'Courier Prime', monospace;
    }
    
    /* Linhas de scanline para efeito de monitor antigo */
    .stApp::before {
        content: " ";
        display: block;
        position: absolute;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), 
                    linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
        z-index: 2;
        background-size: 100% 2px, 3px 100%;
        pointer-events: none;
    }

    h1, h2, h3, p, span, label, .stMarkdown {
        color: #00FF41 !important;
        text-shadow: 0 0 5px #00FF41;
        text-transform: uppercase;
    }
    
    /* Estilização de botões e inputs */
    button {
        background-color: #003300 !important;
        color: #00FF41 !important;
        border: 2px solid #00FF41 !important;
    }
    
    input {
        background-color: #001100 !important;
        color: #00FF41 !important;
        border: 1px solid #00FF41 !important;
    }
    </style>
    """, unsafe_allow_html=True)

class PokemonNode:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = []

def get_evolution_chain(chain_id):
    """Puxa os dados da PokeAPI e transforma em árvore"""
    try:
        url = f"https://pokeapi.co/api/v2/evolution-chain/{chain_id}/"
        response = requests.get(url)
        if response.status_code != 200:
            return None
        data = response.json()
        
        def build_tree(current_data, parent=None):
            node = PokemonNode(current_data['species']['name'], parent)
            for evo in current_data['evolves_to']:
                node.children.append(build_tree(evo, node))
            return node
        
        return build_tree(data['chain'])
    except:
        return None

def traverse(node, mode):
    """Travessias obrigatórias: Pré-ordem e Pós-ordem"""
    res = []
    if not node: return res
    if mode == "PRE": res.append(node.name)
    for child in node.children:
        res.extend(traverse(child, mode))
    if mode == "POST": res.append(node.name)
    return res

def search_dfs(node, target, path=None):
    """Busca em Profundidade (DFS) retornando o caminho"""
    if path is None: path = []
    current_path = path + [node.name]
    if node.name.lower() == target.lower():
        return current_path
    for child in node.children:
        found = search_dfs(child, target, current_path)
        if found: return found
    return None

def get_height(node):
    """Métrica: Altura da árvore"""
    if not node or not node.children: return 0
    return 1 + max(get_height(c) for c in node.children)

st.title("📟 POKE-TERMINAL v1.0.26")
st.write("> ACESSANDO BANCO DE DADOS DA POKÉAPI...")

st.sidebar.header("CONFIGURAÇÕES DE ACESSO")
chain_id = st.sidebar.number_input("ID DA CADEIA GENÉTICA:", min_value=1, value=1, help="1:Bulba, 2:Ivysaur(igual 1), 4:Charmander")

if st.sidebar.button("REQUISITAR NOVA CADEIA"):
    new_tree = get_evolution_chain(chain_id)
    if new_tree:
        st.session_state.root = new_tree
        st.sidebar.success("CADEIA CARREGADA!")
    else:
        st.sidebar.error("ERRO NA REQUISIÇÃO.")

if 'root' not in st.session_state:
    st.session_state.root = get_evolution_chain(1)

query = st.text_input("LOCALIZAR ESPÉCIME NA ÁRVORE ATUAL (DFS):", placeholder="Ex: Charizard")
if query:
    path = search_dfs(st.session_state.root, query)
    if path:
        st.success(f"CAMINHO DETECTADO: {' -> '.join(path).upper()}")
    else:
        st.error("ERRO: ESPÉCIME NÃO ENCONTRADO NESTA HIERARQUIA.")

st.divider()

def draw_ui_tree(node, depth=0):
    indent = "...." * depth
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        st.text(f"{indent}> {node.name.upper()} (GRAU: {len(node.children)})")
    with col2:
        if st.button("ADD", key=f"add_{node.name}_{depth}"):
            node.children.append(PokemonNode("NEW_GEN", node))
            st.rerun()
    with col3:
        if st.button("DEL", key=f"del_{node.name}_{depth}"):
            if node.parent:
                node.parent.children.remove(node)
                st.rerun()
            else:
                st.warning("RAIZ PROTEGIDA")
    
    for child in node.children:
        draw_ui_tree(child, depth + 1)

draw_ui_tree(st.session_state.root)

st.sidebar.divider()
st.sidebar.header("MÉTRICAS EM TEMPO REAL")
if st.session_state.root:
    st.sidebar.text(f"ALTURA DA ÁRVORE: {get_height(st.session_state.root)}")
    mode = st.sidebar.selectbox("MODO DE TRAVESSIA:", ["PRE", "POST"])
    listagem = traverse(st.session_state.root, mode)
    st.sidebar.text(f"ORDEM {mode}:\n{', '.join(listagem).upper()}")