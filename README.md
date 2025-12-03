# Sistema de Controle de Acesso com Reconhecimento Facial

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-green.svg)
![License](https://img.shields.io/badge/License-Academic-blue.svg)

Sistema desktop desenvolvido em Python para controle de acesso utilizando reconhecimento facial. O projeto utiliza algoritmos clássicos de visão computacional (Eigenfaces, Fisherfaces e LBPH) para identificar pessoas e controlar o acesso a áreas restritas.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Banco de Dados](#banco-de-dados)
- [Troubleshooting](#troubleshooting)
- [Autores](#autores)

---

## 🎯 Sobre o Projeto

Este projeto foi desenvolvido como trabalho final da disciplina de **Aprendizagem de Máquina (P2)**. O sistema permite:

- ✅ Cadastro de usuários com captura facial automática
- ✅ Reconhecimento facial em tempo real via webcam
- ✅ Controle de acesso baseado em permissões
- ✅ Histórico completo de acessos
- ✅ Gerenciamento completo de usuários

### Casos de Uso

- Controle de acesso em áreas restritas de faculdades
- Autenticação biométrica em empresas
- Controle de entrada em laboratórios
- Sistema de presença automatizado

---

## ⚙️ Funcionalidades

### 🔐 Cadastro de Usuários
- Formulário completo com validação
- Suporte a diferentes tipos: Alunos, Professores, Direção, Funcionários, Visitantes
- Captura automática de 30 imagens (3 por segundo)
- Treinamento automático dos classificadores

### 👁️ Reconhecimento Facial
- Detecção em tempo real usando SSD ou Haar Cascade
- Três algoritmos disponíveis: Eigenfaces, Fisherfaces, LBPH
- Processamento assíncrono (não trava a interface)
- Indicadores visuais de acesso liberado/negado

### 📊 Gerenciamento
- Listagem e edição de usuários
- Ativação/Desativação de usuários
- Histórico completo de acessos com filtros
- Sistema de permissões configurável

---

## 🛠️ Tecnologias

- **Python 3.7+**
- **OpenCV** - Visão computacional e reconhecimento facial
- **Tkinter** - Interface gráfica desktop
- **SQLite3** - Banco de dados
- **NumPy** - Processamento numérico
- **Pillow (PIL)** - Manipulação de imagens

---

## 📦 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.7 ou superior**
- **Webcam** conectada ao computador
- **Windows 10/11** (para notificações sonoras) ou Linux/Mac (funcionalidade limitada)

---

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/WebCamProject.git
cd WebCamProject
```

### 2. Crie um ambiente virtual (recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

Ou instale manualmente:

```bash
pip install opencv-python>=4.5.0
pip install numpy>=1.19.0
pip install Pillow>=8.0.0
```

### 4. Verifique os arquivos necessários

Certifique-se de que os seguintes arquivos estão presentes na raiz do projeto:

- ✅ `deploy.prototxt.txt` - Arquitetura SSD
- ✅ `res10_300x300_ssd_iter_140000.caffemodel` - Modelo SSD pré-treinado
- ✅ `haarcascade_frontalface_default.xml` - Classificador Haar Cascade

> **Nota**: Estes arquivos são necessários para detecção de faces. Se não estiverem presentes, você precisará baixá-los.

### 5. Execute a aplicação

```bash
python main.py
```

---

## 📖 Como Usar

### Primeira Execução

1. **Execute o programa**: `python main.py`
2. O sistema criará automaticamente:
   - Banco de dados em `database/access_control.db`
   - Pastas `dataset/` e `dataset_full/` (se não existirem)

### Cadastrar um Novo Usuário

1. Na janela principal, clique em **"➕ Cadastrar Usuário"**
2. Preencha o formulário:
   - **Nome**: Nome completo do usuário
   - **Tipo de Acesso**: Selecione (Aluno, Professor, etc.)
   - **Identificação**: RA (alunos), RM (professores/direção) ou RG (funcionários/visitantes)
3. Clique em **"▶ Iniciar Captura"**
4. Posicione-se em frente à câmera
5. Aguarde a captura automática de 30 imagens
6. Clique em **"💾 Salvar e Treinar"**
7. Aguarde o treinamento dos classificadores (pode levar alguns segundos)

> **Dica**: Mantenha boa iluminação e posicione-se de frente para a câmera durante a captura.

### Iniciar Reconhecimento

1. Na janela principal, clique em **"▶ Iniciar Reconhecimento"**
2. Posicione-se em frente à câmera
3. O sistema detectará e reconhecerá sua face automaticamente
4. O acesso será liberado ou negado conforme suas permissões

### Gerenciar Usuários

1. Clique em **"👥 Gerenciar Usuários"**
2. Visualize a lista de todos os usuários cadastrados
3. Use os botões para:
   - **Editar**: Modificar informações do usuário
   - **Ativar/Desativar**: Controlar acesso do usuário
   - **Remover**: Excluir usuário (com confirmação)

### Ver Histórico de Acessos

1. Clique em **"📊 Ver Histórico"**
2. Visualize todas as tentativas de acesso
3. Use os filtros para:
   - Filtrar por data
   - Filtrar por usuário
   - Filtrar por status (liberado/negado)

---

## 📁 Estrutura do Projeto

```
WebCamProject/
├── main.py                    # Ponto de entrada
├── requirements.txt           # Dependências
├── README.md                  # Este arquivo
│
├── database/                  # Módulo de banco de dados
│   ├── db_manager.py          # Gerenciador SQLite
│   └── migrate_db.py          # Migrações de schema
│
├── modules/                   # Módulos de negócio
│   ├── face_recognition_module.py
│   ├── face_capture_module.py
│   └── training_module.py
│
├── ui/                        # Interface gráfica
│   ├── main_window.py
│   ├── cadastro_window.py
│   ├── gerenciamento_window.py
│   └── historico_window.py
│
├── utils/                     # Utilitários
│   ├── permissions.py
│   └── notifications.py
│
├── dataset/                   # Imagens de treinamento (gerado)
├── dataset_full/              # Frames completos (gerado)
│
└── docs/                      # Documentação
    └── DOCUMENTACAO.md         # Documentação técnica completa
```

---

## 🗄️ Banco de Dados

### Migrações Automáticas

O sistema possui **migração automática** de schema. Se você atualizar o código e o banco tiver uma estrutura antiga, a migração será executada automaticamente na primeira execução.

### Resetar o Sistema

Se desejar começar do zero:

1. **Pare a aplicação** se estiver rodando
2. **Delete os seguintes arquivos/pastas**:
   ```bash
   # Pastas de imagens
   dataset/
   dataset_full/
   
   # Classificadores treinados
   eigen_classifier.yml
   fisher_classifier.yml
   lbph_classifier.yml
   face_names.pickle
   
   # Banco de dados (opcional)
   database/access_control.db
   ```
3. Execute novamente: `python main.py`

O sistema criará automaticamente as estruturas necessárias.

---

## 🔧 Troubleshooting

### Erro: "File can't be opened for reading"

**Causa**: Arquivos de classificadores não encontrados.

**Solução**: 
- É normal na primeira execução. Cadastre usuários e treine os classificadores.
- Se já havia usuários cadastrados, verifique se os arquivos `.yml` e `face_names.pickle` existem.

### Erro: "Não foi possível abrir a câmera"

**Causa**: Webcam não disponível ou sendo usada por outro programa.

**Solução**:
- Verifique se a webcam está conectada
- Feche outros programas que possam estar usando a câmera
- Reinicie o programa

### Erro ao instalar OpenCV

**Solução**:
```bash
# Tente instalar com versão específica
pip install opencv-python==4.8.0.76

# Ou instale opencv-contrib-python (inclui módulo face)
pip install opencv-contrib-python
```

### Reconhecimento não funciona bem

**Dicas**:
- Certifique-se de ter boa iluminação
- Posicione-se de frente para a câmera
- Capture pelo menos 30 imagens durante o cadastro
- Evite mudanças significativas de aparência (óculos, barba, etc.)

### Interface não responde durante captura

**Causa**: Processamento bloqueante (não deveria acontecer).

**Solução**: 
- Aguarde alguns segundos
- Se persistir, feche e reabra o programa
- Verifique se está usando a versão mais recente do código

---

## 📚 Documentação Adicional

Para documentação técnica completa, consulte:
- **[docs/DOCUMENTACAO.md](docs/DOCUMENTACAO.md)** - Documentação técnica detalhada

---

## 👥 Autores

- **Ronald Dantas**
- **Genis Ferreira**

**Orientador**: Prof° Denise Lemes

---

## 📄 Licença

Este projeto foi desenvolvido como trabalho acadêmico para a disciplina de **Aprendizagem de Máquina (P2)**.

---

## 🤝 Contribuindo

Este é um projeto acadêmico, mas sugestões e melhorias são bem-vindas! Sinta-se à vontade para:

- Reportar bugs
- Sugerir novas funcionalidades
- Enviar pull requests

---

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique a seção [Troubleshooting](#troubleshooting)
2. Consulte a [documentação técnica](docs/DOCUMENTACAO.md)
3. Abra uma issue no GitHub

---

**Desenvolvido com ❤️ para aprendizado de Machine Learning**

