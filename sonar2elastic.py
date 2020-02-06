"""Sonar to Elasticsearch v0.1.

Usage:
  sonar2elastic.py --sonarApiUrl="http://10.106.248.22:30310/sonar/api" --elasticApiUrl="logs-sul.mapfre.net" --elasticApiPort=80 --idReg=26 --indexName="sonarqube" --pipeline="Tronweb/Tronweb_build" --pipelineDescription="/PY/Newtron/Certificacion" --sonarProjectKey="com.mapfre.tronweb:twserver"
  sonar2elastic.py -h
  sonar2elastic.py --version

Options:
  -h                                                        Exibe esta ajuda.
  --version                                                 Exibe a versao
  --sonarApiUrl=<sonarApiUrl>                   <Stgring>   Url da API do SonarQube.
  --elasticApiUrl=<elasticApiUrl>               <String>    Url da API do Elasticsearch.
  --elasticApiPort=<elasticApiPort>             <Integer>   Porta da API do Elasticsearch.
  --idReg=<idReg>                               <Integer>   Id do registro que sera inserido no Elasticsearch, sugiro usar o numero do build do Jenkins.
  --indexName=<indexName>                       <String>    Nome do indice no Elastisearch: Ex.: "sonarqube".
  --pipeline=<pipeline>                         <String>    Nome completo da pipeline do Jenkins: Ex.: "Tronweb/Tronweb_build".
  --pipelineDescription=<pipelineDescription>   <String>    String contendo dados extras para graficos do Kiband: Ex.: "/PY/Newtron/Certificacion".
  --sonarProjectKey=<sonarProjectKey>           <string>    Key do projeto dentro do Sonar: Ex.: "com.mapfre.tronweb:twserver".
"""
import pip

def errorMsg(stage, error):
    print("Erro na integracao do sonar quando foi executar %s: %s" % (stage, error))

# componentes
def getComponet(projectKey):
    #/projects/search?projects=com.mapfre.tronweb:twserver
    components = "%s/components/show?component=%s" % (sonarApi, projectKey)
    payload = {}
    headers = {}
    try:
        print(components);
        response = requests.request("GET", components, headers=headers, data = payload)
        if response.status_code != 200:
            errorMsg('resComponents', "Erro[%s]" % response.status_code)
        return json.loads(response.text.encode('utf8'))

    except Exception as e:
        errorMsg('resComponents', "Erro[%s]\r\b" % e)
        exit()

def getMeasures(metricKeys, component):
    measures = "%s/measures/component?metricKeys=%s&component=%s" % (sonarApi, metricKeys, component)
    payload = {}
    headers = {}
    try:
        response = requests.request("GET", measures, headers=headers, data = payload)
        if response.status_code != 200:
            errorMsg('resComponents', "Erro[%s]" % response.status_code)
        return json.loads(response.text.encode('utf8'))
    except Exception as e:
        errorMsg('resComponents', "Erro[%s]\r\b" % e)
        exit()
def getIssues(issueKeys, page=1, pageSize= 500, responseJsonArg=[]):
    payload = {}
    headers = {}
    responseJson = {}

    if issueKeys == "":
        measures = "%s/issues/search?p=%s&ps=%s" % (sonarApi, str(page), str(pageSize))
    else:
        measures = "%s/issues/search?tags=%s&p=%s&ps=%s" % (sonarApi, issueKeys, str(page), str(pageSize))
    try:
        response = requests.request("GET", measures, headers=headers, data = payload)
        if response.status_code != 200:
            errorMsg('resComponents', "Erro[%s]" % response.status_code)
        responseJson = json.loads(response.text.encode('utf8'));

        if len(responseJsonArg) > 0:
            i = 0
            while i < len(responseJsonArg["issues"]):
                responseJson["issues"].append(responseJsonArg["issues"][i]);
                i = i+1;
        print("Pagina: %s -> %s" % (responseJson["p"], measures))

        if ((pageSize < responseJson["total"]) and (page < (responseJson["total"] / float(pageSize))) and (len(responseJson["issues"]) > 0)):
            page = page + 1;
            responseJson = getIssues(issueKeys, page, pageSize, responseJson);

        return responseJson;
    except Exception as e:
        errorMsg('resComponents', "Erro[%s]\r\b" % e)
        exit()

def getIssuesList(issues, rule):
    issuesItem = {}
    issuesReg = []
    i = 0
    print("GET-> Issues - Rule [%s]..." % rule)
    while i < len(issues["issues"]):
        if "severity" in issues["issues"][i]:
            issuesItem["severity"] = issues["issues"][i]["severity"]
        else:
            issuesItem["severity"] = "NULLO"

        if "type" in issues["issues"][i]:
            issuesItem["type"] = issues["issues"][i]["type"]

        if "creationDate" in issues["issues"][i]:
            issuesItem["creationDate"] = issues["issues"][i]["creationDate"]

        if "key" in issues["issues"][i]:
            issuesItem["key"] = issues["issues"][i]["key"]

        if "rule" in issues["issues"][i]:
            issuesItem["rule"] = issues["issues"][i]["rule"]

        if "project" in issues["issues"][i]:
            issuesItem["project"] = issues["issues"][i]["project"]

        if "updateDate" in issues["issues"][i]:
            issuesItem["updateDate"] = issues["issues"][i]["updateDate"]

        if "component" in issues["issues"][i]:
            issuesItem["component"] = issues["issues"][i]["component"]

        issuesReg.append(issuesItem)
        issuesItem = {}
        i += 1

    return issuesReg

def getAllIssues(norma, component):
    listIssue = getIssuesList(getIssues(norma), norma)
    issueRegList = []
    reg =[]
    i = 0
    while i < len(listIssue):
        reg = {
            "_index": "%s_issues" % indexName,
            "_type": "issue",
            "_id": norma + "-" + listIssue[i]["key"],
            "_source": {
                "description": pipelineDescription,
                "norma": norma,
                "rule": listIssue[i]["rule"],
                "project": listIssue[i]["project"],
                "severity": listIssue[i]["severity"],
                "type": listIssue[i]["type"],
                "component": listIssue[i]["component"],
                "@analysisDate": component['component']['analysisDate'],
                "@creationDate": listIssue[i]["creationDate"],
                "@updateDate": listIssue[i]["updateDate"],
            }
        }

        issueRegList.append(reg)
        reg = []
        i += 1

    return issueRegList

def getMeasuresList(projectKey):
    measuresRes = {}
    measures = ["duplicated_lines", "duplicated_blocks", "code_smells", "vulnerabilities", "bugs", "complexity",
                "cognitive_complexity", "sqale_debt_ratio"]
    i = 0
    while i < len(measures):
        print("GET-> Metricas [%s]..." % measures[i])
        measuresRes[measures[i]] = getMeasures(measures[i], projectKey)
        i += 1
    return measuresRes

if __name__ == '__main__':
    try:
        from elasticsearch import Elasticsearch
        from elasticsearch import helpers
    except ImportError:
        print("instalando modulo [elasticsearch]...")
        pip.main(['install', 'elasticsearch'])
        from elasticsearch import Elasticsearch
        from elasticsearch import helpers

    #requests
    try:
        import requests
    except ImportError:
        print("instalando modulo [request]...")
        pip.main(['install', 'requests'])
        import requests

    #docopt
    try:
        from docopt import docopt
    except ImportError:
        print("instalando modulo [docopt]...")
        pip.main(['install', 'docopt'])
        from docopt import docopt

    #json
    try:
        import json
    except ImportError:
        print("instalando modulo [json]...")
        pip.main(['install', 'json'])
        import json

    version = 'Sonar to Elasticsearch v0.1 By Silvio Mendes Pedrosa - nirvana.brz@gmail.com'
    arguments = docopt(__doc__, version=version, help=True, options_first=True)
    sonarApi = arguments["--sonarApiUrl"] #"http://10.106.248.22:30310/sonar/api"
    esHost = arguments["--elasticApiUrl"] #"logs-sul.mapfre.net"
    esPort = arguments["--elasticApiPort"] #80
    esApi = [{'host': esHost, 'port': esPort}]
    idReg = arguments["--idReg"] #24
    indexName = arguments["--indexName"] #"sonarqube"
    pipeline = arguments["--pipeline"] #"Tronweb/Tronweb_build"
    pipelineDescription = arguments["--pipelineDescription"]
    sonarProjectKey = arguments["--sonarProjectKey"] #"com.mapfre.tronweb:twserver"
    es = Elasticsearch(esApi, timeout=300)

    print("==============================[SonarQube]==============================")
    print("GET -> SonarQube...")
    print("GET-> SonarQube Project Key: %s..." % sonarProjectKey)

    component = getComponet(sonarProjectKey)
    measuresRes = getMeasuresList(sonarProjectKey)
    allIssuesCwe = getAllIssues('cwe', component)
    allIssuesOwasp = getAllIssues('owasp-a3', component)
    allIssuesCert = getAllIssues('cert', component)

    register = {
        "pipeline": pipeline,
        "description": pipelineDescription,
        "project_id": component['component']['id'],
        "project_name": component['component']['name'],
        "project_key": component['component']['key'],
        "@analysisDate": component['component']['analysisDate'],
        "version": component['component']['version'],
        "duplicated_lines": int(measuresRes['duplicated_lines']['component']['measures'][0]["value"]),
        "duplicated_blocks": int(measuresRes['duplicated_blocks']['component']['measures'][0]["value"]),
        "vulnerabilities": int(measuresRes['vulnerabilities']['component']['measures'][0]["value"]),
        "bugs": int(measuresRes['bugs']['component']['measures'][0]["value"]),
        "code_smells": int(measuresRes['code_smells']['component']['measures'][0]["value"]),
        "complexity": int(measuresRes['complexity']['component']['measures'][0]["value"]),
        "cognitive_complexity": int(measuresRes['cognitive_complexity']['component']['measures'][0]["value"]),
        "sqale_debt_ratio": float(measuresRes['sqale_debt_ratio']['component']['measures'][0]["value"]),
    }
    print("==============================[Elasticsearch]==============================")
    print("POST -> Elasticsearch...")

    indexNameCurrent = "%s_measures" % indexName

    if es.indices.exists(indexNameCurrent) == False:
        print("Criando o index [%s]..." % indexNameCurrent)
        res = es.indices.create(indexNameCurrent)
    else:
        print("Inserindo no index [%s]..." % indexNameCurrent)

    res = es.index(index=indexNameCurrent, id=idReg, doc_type='measures', body=register)

    indexNameCurrent ="%s_issues" % indexName
    if es.indices.exists(indexNameCurrent) == False:
        print("Criando o index [%s]..." % indexNameCurrent)
        res = es.indices.create(indexNameCurrent)
    else:
        print("Inserindo no index [%s]..." % indexNameCurrent)

    print("Inserindo no index [%s] Bulk[CWE]..." % indexNameCurrent)
    helpers.bulk(es, allIssuesCwe, ignore=400)

    print("Inserindo no index [%s] Bulk[Owasp]..." % indexNameCurrent)
    helpers.bulk(es, allIssuesOwasp, ignore=400)

    print("Inserindo no index [%s] Bulk[Cert]..." % indexNameCurrent)
    helpers.bulk(es, allIssuesCert, ignore=400)

    print("==============================[Finalizado]==============================")
