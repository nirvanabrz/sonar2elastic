## Sonar to Elasticsearch v0.1.

Esse escript é bem específico, mas a ideia é servir com base para o seu caso de uso. Espero que ajude!

#### Description

Script Python responsável por integrar SonarQube e Elasticsearch via REST APIs.

#### Python Modules Dependences

O único módulo que é necessário ser instalado manualmente é o pip, os demais o script consegue instalar.

* pip
* elasticsearch
* requests
* json
* docopt

#### Usage:

      sonar2elastic.py --sonarApiUrl="http://10.0.0.1:30310/sonar/api" \
      --elasticApiUrl="10.0.0.2" \
      --elasticApiPort=9000 \
      --idReg=26 \
      --indexName="sonarqube" \
      --pipeline="MyJob" \
      --pipelineDescription="MyJobData" \
      --sonarProjectKey="br.com.teste.app:server"

      sonar2elastic.py -h

      sonar2elastic.py --version

#### Options:
      -h                                                        Exibe esta ajuda.
      --version                                                 Exibe a versão
      --sonarApiUrl=<sonarApiUrl>                   <Stgring>   Url da API do SonarQube.
      --elasticApiUrl=<elasticApiUrl>               <String>    Url da API do Elasticsearch.
      --elasticApiPort=<elasticApiPort>             <Integer>   Porta da API do Elasticsearch.
      --idReg=<idReg>                               <Integer>   Id do registro que sera inserido no Elasticsearch, sugiro usar o numero do build do Jenkins.
      --indexName=<indexName>                       <String>    Nome do indice no Elastisearch: Ex.: "sonarqube".
      --pipeline=<pipeline>                         <String>    Nome completo da pipeline do Jenkins: Ex.: "MyJob".
      --pipelineDescription=<pipelineDescription>   <String>    String contendo dados extras para graficos do Kiband: Ex.: "MyJobData".
      --sonarProjectKey=<sonarProjectKey>           <string>    Key do projeto dentro do Sonar: Ex.: "br.com.teste.app:server".
