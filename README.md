# Experimento Livre Tribologia - User Interface

Interface de usuário em Python para controle da bancada de tribologia em modo de experimento livre.

## Características

- Interface gráfica intuitiva com abas para configuração, controle e análise
- Comunicação serial com o dispositivo de tribologia
- Configuração de parâmetros do experimento (RPM, duração, modo de força)
- Visualização em tempo real dos dados de força
- Barra de progresso do experimento
- Salvamento automático e manual dos dados
- Exportação de relatórios
- Plotagem em tempo real das forças X e Z

## Instalação

1. Clone este repositório:
```bash
git clone <repository-url>
cd Experimento_livre_tribologia_userinterface
```

2. Execute o script de setup:
```bash
python setup.py
```

Ou instale manualmente as dependências:
```bash
pip install -r requirements.txt
```

## Uso

1. Execute a aplicação:
```bash
python UI_experimento_livre_main.py
```

2. Configure a conexão serial:
   - Selecione a porta COM correta
   - Configure o baudrate (padrão: 115200)
   - Clique em "Connect"

3. Configure os parâmetros do experimento:
   - USE_FORCE_CONTROL_MODE: false (para modo simples)
   - RPM_PUMP: 500.0
   - RPM_AXIS: 80.0
   - RPM_FORCE: 60.0
   - EXPERIMENT_DURATION_S: 282.1

4. Inicie o experimento:
   - Clique em "Start Experiment"
   - Monitore o progresso na barra de status
   - Visualize os dados em tempo real na aba "Data & Analysis"

5. Salve os dados:
   - Os dados são salvos automaticamente ao final
   - Use "Save Data" para salvar manualmente
   - Use "Export Report" para gerar relatório de resumo

## Estrutura do Projeto

```
├── UI_experimento_livre_main.py    # Aplicação principal
├── config.py                       # Gerenciamento de configuração
├── serial_comm.py                  # Comunicação serial
├── data_manager.py                 # Gerenciamento de dados
├── requirements.txt                # Dependências Python
├── setup.py                       # Script de instalação
├── README.md                      # Este arquivo
├── experiment_data/               # Diretório para dados salvos
└── config.json                    # Arquivo de configuração (criado automaticamente)
```

## Comunicação Serial

A aplicação se comunica com o firmware da bancada de tribologia através de comandos serial:

- `"3"`: Inicia o experimento (simula pressionar botão)
- `"stop"`: Para o experimento

### Formato dos Dados Recebidos

```
Time:123.45,Fixed_X:1.23,Fixed_Z:4.56
```

Dados de experimento são marcados com `>` no início da linha:
```
>Time:123.45,Fixed_X:1.23,Fixed_Z:4.56
```

## Configuração

A configuração é salva automaticamente em `config.json` e inclui:

- Parâmetros do experimento (RPM, duração, modo)
- Configurações de comunicação serial
- Configurações de dados (diretório de salvamento, etc.)

## Dependências

- `pyserial`: Comunicação serial
- `matplotlib`: Plotagem de dados
- `pandas`: Manipulação de dados
- `numpy`: Cálculos numéricos
- `ttkthemes`: Temas para interface (opcional)

## Solução de Problemas

### Erro de Conexão Serial
- Verifique se a porta COM está correta
- Certifique-se de que o dispositivo está conectado
- Verifique se outro software não está usando a porta

### Dados Não Aparecem
- Verifique a conexão serial
- Confirme que o dispositivo está enviando dados no formato correto
- Verifique os logs de status na aba "Experiment Control"

### Performance
- Para experimentos longos, considere reduzir a frequência de atualização dos gráficos
- Feche outras aplicações que possam usar muita CPU/memória

## Desenvolvimento

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Crie um Pull Request

## Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## Criando Executável Standalone

Para criar um executável standalone que pode ser distribuído sem necessidade de instalar Python:

### Método 1: Script Automático (Recomendado)

```bash
python build_script.py
```

### Método 2: Usando PyInstaller Diretamente

```bash
# Instalar PyInstaller
pip install pyinstaller

# Construir executável
pyinstaller tribology_experiment.spec
```

### Método 3: Usando Batch File (Windows)

```bash
build_executable.bat
```

### Arquivos Gerados

Após a construção, você encontrará:

- `dist/TribologyExperiment.exe` - Executável standalone
- `dist/TribologyExperiment_Portable/` - Pacote portable completo

### Distribuição

Para distribuir a aplicação:

1. **Executável simples**: Distribute apenas o arquivo `TribologyExperiment.exe`
2. **Pacote completo**: Distribute a pasta `TribologyExperiment_Portable` completa

### Requisitos para Construção

- Python 3.7+
- PyInstaller 5.13.2+
- Todas as dependências listadas em `requirements.txt`

### Estrutura do Projeto para Build

```
├── UI_experimento_livre_main.py    # Aplicação principal
├── config.py                       # Gerenciamento de configuração
├── serial_comm.py                  # Comunicação serial
├── data_manager.py                 # Gerenciamento de dados
├── requirements.txt                # Dependências Python
├── tribology_experiment.spec       # Especificação PyInstaller
├── build_script.py                # Script de construção Python
├── build_executable.bat            # Script de construção Windows
├── setup.py                       # Script de instalação
├── .gitignore                     # Arquivos ignorados pelo Git
├── README.md                      # Este arquivo
├── experiment_data/               # Diretório para dados salvos
└── config.json                    # Arquivo de configuração
```
