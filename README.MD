# Equipe Zero22 - Site Oficial

Site da Equipe Zero22 - plataforma para gerenciar galerias de fotos, musicas/sets para download, eventos e historia da equipe.

## Tecnologias

- **Backend:** Python / Flask
- **Banco de Dados:** SQLite
- **Frontend:** HTML5, CSS3, JavaScript
- **Estilo:** Tema dark com neon verde (#00ff41), responsivo (mobile-first)

## Funcionalidades

### Paginas Publicas
- **Home** - Hero animado, albums em destaque, estatisticas
- **Fotos** - Galeria de albums com capas e contagem de fotos
- **Ver Album** - Visualizador de fotos com lightbox (tela cheia)
- **Musicas** - Lista de sets/audios com player e capa do CD
- **Historia** - Texto editavel sobre a equipe
- **Eventos** - Proximos encontros com imagem/banner

### Painel Admin (`/admin`)
- Dashboard com estatisticas (fotos, albums, audios)
- Criar album com capa + upload de fotos no mesmo passo
- Upload de musicas/sets com capa do CD
- Criar eventos com imagem/banner
- Editar texto da historia e URL do Instagram
- Alterar senha do admin
- Gerenciar albums (excluir com todas as fotos)
- Gerenciar eventos (excluir)
- Tabela de arquivos recentes com opcao de exclusao

### Seguranca
- Senhas hasheadas com Werkzeug (generate_password_hash)
- Protecao de rotas admin com login_required
- Limite de upload: 50MB por arquivo
- Flash messages para feedback ao usuario

## Como Rodar

### Requisitos
- Python 3.8+
- pip

### Instalacao

```bash
# Clone o repositorio
git clone https://github.com/richaferreira/site_zero22.git
cd site_zero22

# Instale as dependencias
pip install -r requirements.txt

# Execute o servidor
python app.py
```

O site estara disponivel em: http://localhost:5000

### Login Admin
- **Usuario:** admin
- **Senha:** admin (altere apos o primeiro login!)

## Estrutura do Projeto

```
site_zero22/
├── app.py                  # Aplicacao Flask principal
├── requirements.txt        # Dependencias Python
├── database.db            # Banco SQLite (criado automaticamente)
├── README.md              # Este arquivo
├── static/
│   ├── style.css          # Estilos CSS completos
│   └── uploads/           # Pasta de uploads (criada automaticamente)
└── templates/
    ├── layout.html        # Template base (header, footer, nav)
    ├── home.html          # Pagina inicial
    ├── fotos.html         # Galeria de albums
    ├── ver_album.html     # Visualizador de album individual
    ├── musicas.html       # Pagina de downloads/sets
    ├── historia.html      # Historia da equipe
    ├── eventos.html       # Pagina de eventos
    ├── login.html         # Tela de login
    ├── admin.html         # Painel administrativo
    └── 404.html           # Pagina de erro
```

## Uso do Admin

### Criar Album com Fotos
1. Acesse `/admin` e faca login
2. Na secao "Criar Novo Album", digite o nome
3. Selecione uma imagem de capa (opcional)
4. Selecione as fotos do album (pode selecionar varias)
5. Clique em "Criar Album"

### Upload de Musicas com Capa
1. Na secao "Upload de Arquivos", selecione os arquivos de audio (.mp3, .wav, .ogg) ou ZIP/RAR
2. Deixe "Nenhum (Musicas/Zips)" no campo de album
3. Selecione a imagem de capa do CD/Set (opcional)
4. Clique em "Enviar"

### Criar Evento com Imagem
1. Na secao "Criar Evento", preencha nome, data e local
2. Adicione uma descricao (opcional)
3. Selecione uma imagem/banner para o evento (opcional)
4. Clique em "Criar Evento"

## Personalizacao

### Cores
Edite as variaveis CSS no inicio de `static/style.css`:
```css
:root {
    --bg-color: #0a0a0a;      /* Fundo principal */
    --neon: #00ff41;            /* Cor destaque (neon verde) */
    --card-bg: #141414;         /* Fundo dos cards */
    --text: #ffffff;            /* Cor do texto */
}
```

### Logo
Altere o texto "ZERO22" no arquivo `templates/layout.html` na classe `.logo`.

## Licenca

Projeto da Equipe Zero22. Todos os direitos reservados.
