# Projeto2-IaC-para-Treinamento-Distribuido-de-ML-com-PySpark-AWS-EMR

![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-F37626?style=for-the-badge&logo=scikit-learn&logoColor=white)

> **Resumo:** Este projeto implementa um pipeline completo de Machine Learning e Engenharia de Dados (Data Lakehouse) utilizando processamento distribuído na nuvem. Toda a infraestrutura é provisionada de forma 100% automatizada utilizando Terraform (IaC), orquestrando um cluster Amazon EMR e buckets Amazon S3 para treinar modelos de Processamento de Linguagem Natural (NLP) com PySpark.

---
## 📂 Estrutura do Projeto
```bash
Projeto2/
├── IaC/                           # Diretório principal de Infraestrutura como Código
│   ├── dados/
│   │   └── dataset.csv            # Dados de entrada (Raw Data)
│   ├── modules/                   # Módulos reutilizáveis do Terraform
│   │   ├── emr/                   # Configuração do Cluster EMR
│   │   │   ├── iam.tf             # Definição de Roles e Políticas de Acesso
│   │   │   ├── main.tf            # Definição dos recursos do cluster
│   │   │   └── security_groups.tf # Regras de Firewall
│   │   └── s3/                    # Configuração de Armazenamento
│   │       ├── main.tf            # Criação dos Buckets
│   │       └── outputs.tf         # Outputs (nome do bucket criado)
│   ├── pipeline/                  # Scripts de Processamento e Machine Learning
│   │   ├── p2_log.py              # Gerenciamento de Logs
│   │   ├── p2_ml.py               # Script de modelagem/ML
│   │   ├── p2_processamento.py    # Script de processamento de dados
│   │   └── projeto2.py            # Script principal de execução
│   ├── scripts/
│   │   └── bootstrap.sh           # Script de inicialização (Bootstrap Actions para o EMR)
│   ├── config.tf                  # Configurações do Provider/Backend para o Estado Remoto, Versão do Terraform e Provider
│   ├── main.tf                    # Orquestrador principal da infraestrutura
│   ├── terraform.tfvars           # Definição dos valores das variáveis
│   └── variables.tf               # Declaração das variáveis
├── .gitattributes
├── .gitignore
├── Dockerfile                     # Ambiente Docker reprodutível
├── LEIAME.txt                     # Instruções adicionais
├── LICENSE
└── README.md                      # Documentação oficial
```

---
## ☁️ Diagrama de Arquitetura do Projeto
![Diagrama](./Projeto2/assets/arquitetura.gif)

---

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/thiagoviniciusbsantos/)
