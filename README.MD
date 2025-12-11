# 🚗 Equipe Zero22 - Portal Automotivo

> "Estilo de vida automotivo. Onde o grave bate forte."

Sistema de gerenciamento de conteúdo (CMS) desenvolvido sob medida para a **Equipe Zero22**. O site funciona como uma galeria digital para exibir álbuns de fotos de encontros, disponibilizar downloads de sets musicais e contar a história da equipe.

![Badge Concluído](http://img.shields.io/static/v1?label=STATUS&message=CONCLUÍDO&color=GREEN&style=for-the-badge)
![Badge Python](http://img.shields.io/static/v1?label=TECH&message=PYTHON+FLASK&color=blue&style=for-the-badge)

## 🖥️ Funcionalidades

### Área Pública (Visitantes)
- **Home:** Banner imponente, destaques dos últimos álbuns e link rápido para o Instagram.
- **Galeria de Álbuns:** Visualização de pastas de eventos organizadas por data.
- **Visualizador de Fotos:** Exibição de fotos em alta qualidade dentro de cada álbum.
- **Músicas & Downloads:** - Player de áudio integrado para ouvir prévias (.mp3).
  - Botão de download direto para packs e alinhamentos (.zip/.rar).
- **História:** Página institucional com texto editável pelo painel.
- **Design:** Tema "Dark Mode" (Preto e Verde Neon), 100% responsivo para celulares.

### Área Administrativa (Restrita)
- **Login Seguro:** Acesso protegido por senha.
- **Gestão de Álbuns:** Criar e **Excluir** álbuns inteiros (com limpeza automática de arquivos).
- **Upload em Massa:** Envio de múltiplas fotos de uma só vez para um álbum específico.
- **Gestão de Conteúdo:** Edição do texto da página "História" sem mexer em código.
- **Dashboard:** Visão geral de arquivos e álbuns criados.

---

## 🛠️ Tecnologias Utilizadas

- **Back-end:** Python 3 + Flask.
- **Banco de Dados:** SQLite (Nativo, leve e sem configuração complexa).
- **Front-end:** HTML5, CSS3 (Flexbox/Grid), Jinja2 (Templates).
- **Estilo:** CSS Customizado (Tema Zero22 Neon).

---

## 📂 Estrutura do Projeto

```text
projeto_zero22/
│
├── app.py                 # O coração da aplicação (Rotas e Lógica)
├── database.db            # Banco de dados (Criado automaticamente)
├── static/
│   ├── style.css          # Estilização visual (Cores, Layout)
│   └── uploads/           # Pasta onde as mídias são salvas
├── templates/
│   ├── layout.html        # Estrutura base (Menu + Rodapé)
│   ├── home.html          # Página inicial
│   ├── admin.html         # Painel de controle
│   └── ... (outras páginas HTML)
└── README.md              # Documentação