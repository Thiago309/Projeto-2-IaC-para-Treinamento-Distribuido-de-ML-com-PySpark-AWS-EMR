# Usar a imagem oficial do sistema operacional Linux Ubuntu na ultima versão como base da imagem
FROM ubuntu:latest

# Mantenedor da imagem
LABEL maintainer="Thiago_Vinicius"

# Definir a versão do Terraform ultima versão sem ser beta (evita bugs e erros)
ENV TERRAFORM_VERSION=1.14.4

# Atualizar os pacotes do sistema e instalar dependências necessarias (wget, curl, unzip, tree para visualização, git para o realizar o download dos modulos dos serviços AWS no GitHub)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    unzip \
    curl \
    tree \
    vim \
    git \
    openssh-client \
    iputils-ping \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Baixar e instalar Terraform
RUN wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    mv terraform /usr/local/bin/ && \
    rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip

# Instalar o AWS CLI em uma pasta temporária /tmp/ e a limpa no final, o que é mais eficiente.
RUN mkdir -p /tmp/aws_install && \
    cd /tmp/aws_install && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    cd / && \
    rm -rf /tmp/aws_install

# Criar a pasta /iac dentro do container
RUN mkdir /iac

# Cria um volume no container
VOLUME /iac

# Definir o diretório de trabalho padrão
WORKDIR /iac

# Definir o comando padrão para execução quando o container for iniciado
CMD ["/bin/bash"]