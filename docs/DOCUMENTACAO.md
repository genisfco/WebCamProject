# Documentação Técnica - Sistema de Controle de Acesso com Reconhecimento Facial

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Descrição do Projeto](#descrição-do-projeto)
3. [Funcionalidades](#funcionalidades)
4. [Tecnologias Utilizadas](#tecnologias-utilizadas)
5. [Arquitetura do Sistema](#arquitetura-do-sistema)
6. [Estrutura de Arquivos](#estrutura-de-arquivos)
7. [Banco de Dados](#banco-de-dados)
8. [Módulos Principais](#módulos-principais)
9. [Algoritmos de Reconhecimento](#algoritmos-de-reconhecimento)
10. [Sistema de Notificações](#sistema-de-notificações)
11. [Fluxo de Funcionamento](#fluxo-de-funcionamento)

---

## 🎯 Visão Geral

O **Sistema de Controle de Acesso com Reconhecimento Facial** é uma aplicação desktop desenvolvida em Python que utiliza técnicas de visão computacional e aprendizado de máquina para identificar pessoas e controlar o acesso a áreas restritas de uma instituição (faculdade, empresa, etc.).

O sistema permite cadastrar usuários, capturar suas faces através de webcam, treinar modelos de reconhecimento facial e realizar autenticação em tempo real.

---

## 📝 Descrição do Projeto

Este projeto foi desenvolvido como trabalho final da disciplina de **Aprendizagem de Máquina (P2)**, com o objetivo de demonstrar a aplicação prática de algoritmos clássicos de reconhecimento facial em um sistema funcional de controle de acesso.

### Objetivos

- **Autenticação Biométrica**: Identificar pessoas através de reconhecimento facial
- **Controle de Acesso**: Liberar ou negar acesso baseado em permissões configuradas
- **Registro de Acessos**: Manter histórico completo de tentativas de acesso
- **Gerenciamento de Usuários**: Interface completa para cadastro, edição e gerenciamento
- **Sistema de Permissões**: Controle granular de acesso por usuário, horário e setor

---

## ⚙️ Funcionalidades

### 1. **Cadastro de Usuários**
- Formulário completo com validação de dados
- Suporte a diferentes tipos de usuários:
  - **Alunos**: Identificação por RA (Registro Acadêmico)
  - **Professores**: Identificação por RM (Registro de Matrícula)
  - **Direção**: Identificação por RM
  - **Funcionários**: Identificação por RG
  - **Visitantes**: Identificação por RG
- Captura automática de 30 imagens por usuário (3 fotos por segundo)
- Validação de duplicidade de identificação
- Treinamento automático dos classificadores após cadastro

### 2. **Reconhecimento Facial em Tempo Real**
- Detecção de faces usando SSD (Single Shot Detector) ou Haar Cascade
- Reconhecimento usando três algoritmos diferentes:
  - **Eigenfaces**
  - **Fisherfaces**
  - **LBPH** (Local Binary Patterns Histograms) - padrão
- Processamento em thread separada para não travar a interface
- Exibição de vídeo em tempo real com anotações visuais

### 3. **Gerenciamento de Usuários**
- Listagem de todos os usuários cadastrados
- Edição de informações do usuário
- Ativação/Desativação de usuários
- Remoção de usuários (com confirmação)
- Visualização de dados completos

### 4. **Histórico de Acessos**
- Registro completo de todas as tentativas de acesso
- Filtros por:
  - Data
  - Usuário
  - Status (liberado/negado)
  - Tipo de evento (entrada/saída)
- Visualização detalhada com informações de confiança e motivos de negação

### 5. **Sistema de Permissões**
- Verificação de status do usuário (ativo/inativo)
- Controle de acesso por horário
- Controle de acesso por setor
- Mensagens personalizadas de negação

### 6. **Notificações**
- **Notificações Visuais**:
  - Quadro retangular grande exibido na tela durante reconhecimento
  - Formato vertical (altura maior que largura) para melhor visibilidade
  - Quadro verde com nome do usuário e "LIBERADO" para acesso permitido
  - Quadro vermelho com nome do usuário e "NEGADO" para acesso negado
  - Exibição automática por 3 segundos após reconhecimento
  - Centralizado na tela com fundo semi-transparente
  - Textos em fonte grande e legível
- **Notificações de Voz**:
  - Síntese de voz usando bibliotecas nativas do Windows (win32com) ou pyttsx3
  - Anuncia "ACESSO LIBERADO" quando acesso é permitido
  - Anuncia "ACESSO NEGADO" quando acesso é negado
  - Execução em thread separada para não bloquear o processamento
  - Configurável (velocidade e volume)
- **Outras Notificações**:
  - Log de eventos em tempo real na interface
  - Indicadores visuais (LED verde/vermelho) na janela principal
  - Mensagens detalhadas com informações de confiança e motivos

---

## 🛠️ Tecnologias Utilizadas

### Linguagem e Framework
- **Python 3.7+**: Linguagem de programação principal
- **Tkinter**: Framework GUI nativo do Python para interface gráfica

### Visão Computacional e Machine Learning
- **OpenCV (opencv-python)**: Biblioteca principal para processamento de imagens e visão computacional
  - Módulo `cv2.face`: Algoritmos de reconhecimento facial
  - Detecção de faces: SSD (Caffe) e Haar Cascade
- **NumPy**: Manipulação de arrays e operações matemáticas em imagens
- **Pillow (PIL)**: Processamento e manipulação de imagens

### Banco de Dados
- **SQLite3**: Banco de dados relacional embutido
  - Armazenamento de usuários, histórico e permissões
  - Migrações automáticas de schema

### Utilitários
- **Pickle**: Serialização de objetos Python (mapeamento de nomes)
- **Threading**: Processamento assíncrono de vídeo e síntese de voz
- **datetime**: Manipulação de datas e horários
- **winsound**: Notificações sonoras básicas (Windows)
- **pyttsx3**: Biblioteca de síntese de voz multiplataforma (opcional)
- **win32com.client**: API nativa do Windows para síntese de voz (SAPI.SpVoice)

### Arquivos de Modelos
- **deploy.prototxt.txt**: Arquitetura da rede SSD para detecção facial
- **res10_300x300_ssd_iter_140000.caffemodel**: Modelo pré-treinado SSD
- **haarcascade_frontalface_default.xml**: Classificador Haar Cascade

---

## 🏗️ Arquitetura do Sistema

O sistema segue uma arquitetura modular, separando responsabilidades em diferentes camadas:

```
┌─────────────────────────────────────────┐
│         Interface Gráfica (UI)          │
│  - main_window.py                       │
│  - cadastro_window.py                   │
│  - gerenciamento_window.py              │
│  - historico_window.py                  │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│      Módulos de Negócio                 │
│  - face_recognition_module.py           │
│  - face_capture_module.py               │
│  - training_module.py                   │
└─────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
┌──────────────┐    ┌──────────────┐
│   Database   │    │   Utils       │
│   Manager    │    │  - permissions│
│              │    │  - notifications│
└──────────────┘    └──────────────┘
```

### Camadas

1. **Camada de Apresentação (UI)**: Interface gráfica Tkinter
2. **Camada de Negócio**: Lógica de reconhecimento, captura e treinamento
3. **Camada de Dados**: Gerenciamento do banco de dados SQLite
4. **Camada de Utilitários**: Permissões e notificações

---

## 📁 Estrutura de Arquivos

```
WebCamProject/
├── main.py                          # Ponto de entrada da aplicação
├── requirements.txt                 # Dependências do projeto
├── README.md                        # Documentação principal
│
├── database/                        # Módulo de banco de dados
│   ├── __init__.py
│   ├── db_manager.py                # Gerenciador do banco SQLite
│   ├── migrate_db.py                # Script de migração de schema
│   └── access_control.db            # Banco de dados SQLite (gerado)
│
├── modules/                         # Módulos de negócio
│   ├── __init__.py
│   ├── face_recognition_module.py  # Módulo de reconhecimento facial
│   ├── face_capture_module.py       # Módulo de captura de faces
│   └── training_module.py           # Módulo de treinamento
│
├── ui/                              # Interface gráfica
│   ├── __init__.py
│   ├── main_window.py               # Janela principal
│   ├── cadastro_window.py           # Janela de cadastro
│   ├── gerenciamento_window.py      # Janela de gerenciamento
│   └── historico_window.py          # Janela de histórico
│
├── utils/                           # Utilitários
│   ├── __init__.py
│   ├── permissions.py               # Sistema de permissões
│   └── notifications.py             # Sistema de notificações
│
├── dataset/                         # Dataset de treinamento
│   └── [pasta_por_usuario]/         # Imagens de faces recortadas
│
├── dataset_full/                    # Frames completos
│   └── [pasta_por_usuario]/         # Imagens completas capturadas
│
├── docs/                            # Documentação
│   ├── DOCUMENTACAO.md              # Esta documentação
│   └── Prj_P2_AM_ControleDeAcesso.docx
│
├── helper_functions.py              # Funções auxiliares
│
├── # Arquivos de modelos treinados (gerados após treinamento)
├── eigen_classifier.yml              # Classificador Eigenfaces
├── fisher_classifier.yml             # Classificador Fisherfaces
├── lbph_classifier.yml              # Classificador LBPH
├── face_names.pickle                # Mapeamento de nomes
│
└── # Arquivos de modelos de detecção
    ├── deploy.prototxt.txt          # Arquitetura SSD
    ├── res10_300x300_ssd_iter_140000.caffemodel  # Modelo SSD
    └── haarcascade_frontalface_default.xml        # Haar Cascade
```

---

## 🗄️ Banco de Dados

### Tabela: `usuarios`

Armazena informações dos usuários cadastrados.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INTEGER | Chave primária (auto-incremento) |
| `nome` | TEXT | Nome completo do usuário |
| `numero_identificacao` | TEXT | Número de identificação (RA/RM/RG) |
| `tipo_identificacao` | TEXT | Tipo: 'RA', 'RM' ou 'RG' |
| `tipo_acesso` | TEXT | Tipo: 'aluno', 'professor', 'direcao', 'funcionario', 'visitante' |
| `ativo` | INTEGER | Status: 1 (ativo) ou 0 (inativo) |
| `data_cadastro` | TEXT | Data e hora do cadastro (ISO format) |
| `face_id` | INTEGER | ID da face no sistema de reconhecimento |

### Tabela: `historico_acessos`

Registra todas as tentativas de acesso.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INTEGER | Chave primária |
| `usuario_id` | INTEGER | FK para `usuarios.id` |
| `data_hora` | TEXT | Data e hora do acesso (ISO format) |
| `tipo_evento` | TEXT | 'entrada' ou 'saida' |
| `status` | TEXT | 'liberado' ou 'negado' |
| `confianca` | REAL | Nível de confiança do reconhecimento |
| `motivo_negacao` | TEXT | Motivo da negação (se aplicável) |

### Tabela: `permissoes`

Define permissões específicas de acesso.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INTEGER | Chave primária |
| `usuario_id` | INTEGER | FK para `usuarios.id` |
| `setor_permitido` | TEXT | Setor onde o acesso é permitido |
| `horario_inicio` | TEXT | Horário de início permitido (HH:MM) |
| `horario_fim` | TEXT | Horário de fim permitido (HH:MM) |
| `dias_semana` | TEXT | Dias da semana permitidos (0-6) |

---

## 🔧 Módulos Principais

### 1. `DatabaseManager` (`database/db_manager.py`)

Gerencia todas as operações do banco de dados SQLite.

**Principais métodos:**
- `criar_usuario()`: Cria novo usuário
- `buscar_usuario_por_id()`: Busca usuário por ID
- `buscar_usuario_por_identificacao()`: Busca por número de identificação
- `atualizar_usuario()`: Atualiza dados do usuário
- `listar_usuarios()`: Lista todos os usuários
- `registrar_acesso()`: Registra tentativa de acesso
- `buscar_historico()`: Consulta histórico de acessos
- `buscar_permissoes_usuario()`: Busca permissões de um usuário

### 2. `FaceRecognitionModule` (`modules/face_recognition_module.py`)

Módulo principal de reconhecimento facial em tempo real.

**Características:**
- Detecção de faces usando SSD ou Haar Cascade
- Reconhecimento usando Eigenfaces, Fisherfaces ou LBPH
- Processamento em thread separada
- Integração com banco de dados para verificação de permissões
- Callbacks para atualização da interface

**Principais métodos:**
- `start_recognition()`: Inicia reconhecimento
- `stop_recognition()`: Para reconhecimento
- `recognize_faces()`: Processa um frame e reconhece faces
- `reload_recognizer()`: Recarrega classificadores após novo treinamento

### 3. `FaceCaptureModule` (`modules/face_capture_module.py`)

Gerencia a captura de faces via webcam.

**Características:**
- Captura automática de múltiplas imagens
- Suporte a diferentes detectores (SSD, Haar Cascade)
- Callbacks de progresso
- Salvamento em duas pastas (recortada e completa)

**Principais métodos:**
- `capture_faces()`: Captura faces de um usuário
- `detect_face_ssd()`: Detecta face usando SSD
- `detect_face_haar()`: Detecta face usando Haar Cascade

### 4. `TrainingModule` (`modules/training_module.py`)

Gerencia o treinamento dos classificadores.

**Características:**
- Carrega imagens do dataset
- Treina três algoritmos simultaneamente
- Gera arquivos de classificadores (.yml)
- Cria mapeamento de nomes (pickle)

**Principais métodos:**
- `get_image_data()`: Carrega e processa imagens do dataset
- `train_all_recognizers()`: Treina todos os classificadores
- `get_face_names()`: Retorna mapeamento de nomes

### 5. `PermissionChecker` (`utils/permissions.py`)

Verifica permissões de acesso dos usuários.

**Lógica de verificação:**
1. Verifica se usuário existe e está ativo
2. Verifica permissões específicas (horário, setor)
3. Retorna resultado e motivo

### 6. `NotificationManager` (`utils/notifications.py`)

Gerencia notificações visuais e sonoras do sistema.

**Funcionalidades:**

**Notificações Visuais:**
- Quadro de notificação grande exibido sobre o vídeo
- Formato retangular vertical (50% largura, 75% altura do frame)
- Cores diferenciadas: verde para acesso liberado, vermelho para negado
- Exibição automática por 3 segundos após reconhecimento
- Controle de tempo usando timestamps para garantir duração exata
- Desenho sobre o frame usando OpenCV com transparência

**Síntese de Voz:**
- Suporte a múltiplas bibliotecas (win32com.client ou pyttsx3)
- Inicialização automática da melhor biblioteca disponível
- Execução em thread separada para não bloquear processamento
- Configuração de velocidade (150) e volume (0.8)
- Textos personalizáveis: "ACESSO LIBERADO" e "ACESSO NEGADO"

**Outras Funcionalidades:**
- Log de eventos com callbacks para interface
- Notificações informativas e de aviso
- Tratamento robusto de erros (sistema funciona mesmo sem voz)

**Principais métodos:**
- `acesso_liberado()`: Notifica acesso liberado (visual + voz)
- `acesso_negado()`: Notifica acesso negado (visual + voz)
- `draw_active_notification()`: Desenha notificação ativa no frame
- `_draw_notification_box()`: Desenha o quadro visual
- `_speak()`: Reproduz texto usando síntese de voz
- `_set_active_notification()`: Define notificação visual ativa
- `set_log_callback()`: Define callback para logs

---

## 🧠 Algoritmos de Reconhecimento

### 1. Eigenfaces

- **Baseado em**: Análise de Componentes Principais (PCA)
- **Vantagens**: Rápido, eficiente para grandes datasets
- **Desvantagens**: Sensível a variações de iluminação e pose
- **Uso**: Boa para ambientes controlados

### 2. Fisherfaces

- **Baseado em**: Análise Discriminante Linear (LDA)
- **Vantagens**: Melhor que Eigenfaces para variações de iluminação
- **Desvantagens**: Requer múltiplas imagens por pessoa no treinamento
- **Uso**: Ideal quando há variações de iluminação

### 3. LBPH (Local Binary Patterns Histograms)

- **Baseado em**: Padrões binários locais
- **Vantagens**: 
  - Robusto a variações de iluminação
  - Funciona bem com poucas imagens de treinamento
  - Bom para reconhecimento em tempo real
- **Desvantagens**: Pode ser mais lento que Eigenfaces
- **Uso**: **Algoritmo padrão** do sistema, recomendado para vídeo

---

## 🔊 Sistema de Notificações

O sistema implementa um conjunto completo de notificações visuais e sonoras para fornecer feedback imediato sobre o resultado do reconhecimento facial.

### Notificações Visuais

#### Quadro de Notificação

Quando um usuário é reconhecido e o acesso é liberado ou negado, um quadro grande é exibido sobre o vídeo da câmera:

**Características:**
- **Formato**: Retangular vertical (portrait)
  - Largura: 50% da largura do frame
  - Altura: 75% da altura do frame
  - Centralizado na tela
- **Cores**:
  - Verde (RGB: 0, 255, 0) para acesso liberado
  - Vermelho (RGB: 0, 0, 255) para acesso negado
- **Conteúdo**:
  - Nome do usuário em maiúsculas (fonte 1.0)
  - Status ("LIBERADO" ou "NEGADO") em fonte maior (1.3)
  - Textos centralizados e em branco para contraste
- **Duração**: Exatamente 3 segundos após o reconhecimento
- **Efeito Visual**:
  - Fundo semi-transparente (60% opacidade)
  - Borda espessa (4 pixels) na cor do status
  - Sobreposição sobre o vídeo sem bloquear completamente a visualização

#### Implementação Técnica

O sistema utiliza um mecanismo de controle de tempo baseado em timestamps:

1. Quando ocorre um reconhecimento, uma notificação é ativada com timestamp atual
2. A cada frame processado, verifica-se se ainda está dentro dos 3 segundos
3. Se sim, o quadro é desenhado sobre o frame usando OpenCV
4. Após 3 segundos, a notificação é automaticamente removida

**Métodos principais:**
- `_set_active_notification()`: Define notificação ativa com timestamp
- `draw_active_notification()`: Verifica tempo e desenha se necessário
- `_draw_notification_box()`: Desenha o quadro visual no frame

### Notificações de Voz

O sistema utiliza síntese de voz (Text-to-Speech) para anunciar verbalmente o resultado do reconhecimento.

#### Bibliotecas Suportadas

O sistema tenta usar bibliotecas na seguinte ordem de prioridade:

1. **win32com.client** (Windows nativo)
   - Usa a API SAPI (Speech API) do Windows
   - Não requer instalação adicional
   - Disponível apenas no Windows

2. **pyttsx3** (multiplataforma)
   - Biblioteca Python multiplataforma
   - Requer instalação: `pip install pyttsx3`
   - Funciona em Windows, Linux e macOS

#### Funcionalidades

- **Textos anunciados**:
  - "ACESSO LIBERADO" quando acesso é permitido
  - "ACESSO NEGADO" quando acesso é negado
- **Configurações**:
  - Velocidade: 150 palavras por minuto
  - Volume: 80% do máximo
- **Execução**:
  - Processamento em thread separada (não bloqueia o sistema)
  - Thread daemon para não impedir encerramento do programa
  - Tratamento de erros silencioso (sistema continua funcionando sem voz)

#### Personalização

Os textos de voz podem ser facilmente modificados no arquivo `utils/notifications.py`:

```python
# Linha 211 - Acesso liberado
self._speak("ACESSO LIBERADO")  # Pode ser alterado para qualquer texto

# Linha 234 - Acesso negado
self._speak("ACESSO NEGADO")  # Pode ser alterado para qualquer texto
```

### Integração com o Sistema

As notificações são integradas ao fluxo de reconhecimento:

1. **Reconhecimento bem-sucedido**:
   - Usuário identificado no banco de dados
   - Permissões verificadas
   - Notificação visual ativada (quadro verde/vermelho)
   - Notificação de voz reproduzida
   - Log registrado na interface

2. **Rate Limiting**:
   - Sistema evita spam de notificações
   - Cooldown de 5 segundos entre reconhecimentos do mesmo usuário
   - Durante cooldown, apenas desenha moldura no rosto sem notificações

### Outras Notificações

Além das notificações principais, o sistema também possui:

- **LED de Status**: Indicador visual na janela principal (verde/vermelho/cinza)
- **Log de Eventos**: Registro textual completo de todas as ações
- **Mensagens Informativas**: Notificações sobre estado do sistema
- **Alertas de Erro**: Mensagens quando ocorrem problemas

---

## 🔄 Fluxo de Funcionamento

### Cadastro de Novo Usuário

```
1. Usuário preenche formulário (nome, tipo, identificação)
2. Sistema valida dados e verifica duplicidade
3. Inicia captura via webcam
4. Captura 30 imagens automaticamente (3 por segundo)
5. Salva imagens em dataset/ e dataset_full/
6. Salva usuário no banco de dados
7. Treina todos os classificadores com TODAS as faces do dataset
8. Salva classificadores treinados (.yml)
9. Atualiza face_id do usuário no banco
10. Recarrega reconhecedor na interface principal
```

### Reconhecimento em Tempo Real

```
1. Sistema inicia captura de vídeo da webcam
2. Para cada frame:
   a. Detecta faces usando SSD
   b. Para cada face detectada:
      - Extrai ROI (Region of Interest)
      - Redimensiona para 90x120 pixels
      - Converte para escala de cinza
      - Executa predição usando classificador LBPH
      - Verifica nível de confiança
   c. Se confiança aceitável:
      - Busca usuário no banco por face_id
      - Verifica permissões
      - Registra acesso no histórico
      - Exibe resultado na interface
      - Emite notificação visual (quadro verde/vermelho por 3 segundos)
      - Emite notificação de voz ("ACESSO LIBERADO" ou "ACESSO NEGADO")
   d. A cada frame processado:
      - Verifica se há notificação visual ativa
      - Se ainda dentro dos 3 segundos, desenha o quadro no frame
      - Se tempo expirado, remove a notificação
```

### Treinamento dos Classificadores

```
1. Carrega todas as pastas do dataset/
2. Para cada pasta (usuário):
   a. Carrega todas as imagens .jpg
   b. Converte para escala de cinza
   c. Redimensiona para 90x120
   d. Associa ID numérico único
3. Cria arrays de faces e IDs
4. Treina cada classificador:
   - Eigenfaces: cv2.face.EigenFaceRecognizer_create()
   - Fisherfaces: cv2.face.FisherFaceRecognizer_create()
   - LBPH: cv2.face.LBPHFaceRecognizer_create()
5. Salva classificadores em arquivos .yml
6. Salva mapeamento nome->ID em face_names.pickle
```

---

## 📊 Considerações Técnicas

### Performance

- **Processamento de vídeo**: Executado em thread separada para não travar a UI
- **Taxa de captura**: 3 imagens por segundo durante cadastro
- **Taxa de reconhecimento**: ~30 FPS (depende do hardware)
- **Tamanho das imagens**: Faces recortadas em 90x120 pixels

### Limitações

- Requer boa iluminação para melhor precisão
- Funciona melhor com faces frontais
- Requer pelo menos 10-30 imagens por pessoa para treinamento eficaz
- Sistema desenvolvido para Windows (notificações sonoras e síntese de voz)
- Síntese de voz requer biblioteca pyttsx3 instalada (ou win32com nativo do Windows)

### Segurança

- Validação de dados de entrada
- Verificação de duplicidade de identificação
- Sistema de permissões configurável
- Histórico completo de acessos para auditoria

---

## 📝 Notas de Desenvolvimento

### Migrações de Banco de Dados

O sistema possui migração automática de schema. Se detectar uma estrutura antiga do banco (sem `tipo_identificacao`), executa automaticamente a migração.

### Tratamento de Erros

- Sistema funciona mesmo sem classificadores treinados (inicialização vazia)
- Tratamento robusto de erros em todas as operações críticas
- Mensagens de erro amigáveis ao usuário

### Extensibilidade

O sistema foi projetado para ser facilmente extensível:
- Novos tipos de usuários podem ser adicionados
- Novos algoritmos de reconhecimento podem ser integrados
- Sistema de permissões pode ser expandido
- Interface pode ser customizada

---

## 👥 Autores

- **Ronald Dantas**
- **Genis Ferreira**

**Orientador**: Prof° Denise Lemes

---

## 📄 Licença

Este projeto foi desenvolvido como trabalho acadêmico para a disciplina de Aprendizagem de Máquina (P2).

---

**Versão da Documentação**: 1.1  
**Data**: 2024  
**Última Atualização**: Sistema de Notificações Visuais e de Voz

