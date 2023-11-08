import requests
import time

API_ENDPOINT = 'https://app.pipefy.com/graphql'
HEADERS = {
    'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJQaXBlZnkiLCJpYXQiOjE2OTc0NjczMDIsImp0aSI6ImM2YmM3MDEzLTM5YWYtNDY1Ni1hODM5LTU0YzI4ZGEzOTAwZiIsInN1YiI6MzAyMTIwNTMxLCJ1c2VyIjp7ImlkIjozMDIxMjA1MzEsImVtYWlsIjoidHJpYmUuZ21AdGVncnVzLnRlYW0iLCJhcHBsaWNhdGlvbiI6MzAwMjg0MDk0LCJzY29wZXMiOltdfSwiaW50ZXJmYWNlX3V1aWQiOm51bGx9.MydgEKIWMeLo085IEMRHmPeHhRHUQ_1uF_tWk8q1hTTjP9FVz32_StTYOU8Kk8nWTKMhCa7Ssz7CxDf-AvcLVw'
}

# Função para iniciar a exportação do relatório
def export_pipe_report():
    mutation = """
    mutation {
        exportPipeReport(input: {pipeId: 302274681, pipeReportId: 300547495}) {
            pipeReportExport {
                id
            }
        }
    }
    """
    response = requests.post(API_ENDPOINT, json={'query': mutation}, headers=HEADERS)
    if response.ok:
        report_id = response.json()['data']['exportPipeReport']['pipeReportExport']['id']
        print(f"ID do relatório obtido: {report_id}")
        return report_id
    else:
        print(f"Erro ao exportar relatório: {response.status_code}")
        print(response.text)
        return None

# Função para checar o status do relatório e obter a URL quando pronto
def get_report_status_and_url(report_id):
    query = f"""
    {{
        pipeReportExport(id: "{report_id}") {{
            fileURL
            state
        }}
    }}
    """
    while True:
        time.sleep(30)  # Aguarda 30 segundos antes de verificar o estado do relatório
        response = requests.post(API_ENDPOINT, json={'query': query}, headers=HEADERS)
        if response.ok:
            report_export = response.json()['data']['pipeReportExport']
            if report_export['state'] == "done":
                print("Relatório pronto para download.")
                return report_export['fileURL']
            else:
                print("Relatório ainda está sendo processado. Aguardando...")
        else:
            print(f"Erro ao obter o status do relatório: {response.status_code}")
            print(response.text)
            return None

# Função para fazer o download do relatório
def download_file(file_url):
    response = requests.get(file_url)
    if response.status_code == 200:
        with open('reportExported.xlsx', 'wb') as file:
            file.write(response.content)
        print("Download do arquivo concluído.")
    else:
        print(f"Erro ao fazer o download do arquivo: {response.status_code}")

def main():
    report_id = export_pipe_report()
    if report_id:
        file_url = get_report_status_and_url(report_id)
        if file_url:
            print(f"URL do arquivo obtida: {file_url}")
            download_file(file_url)
        else:
            print("Não foi possível obter a URL do arquivo ou o relatório ainda não está pronto.")
    else:
        print("Não foi possível obter o ID do relatório para exportação.")

if __name__ == "__main__":
    main()
