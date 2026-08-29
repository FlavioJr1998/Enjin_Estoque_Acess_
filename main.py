import gspread


CAMINHO_CREDENCIAL = "credentials/estoque-minimo-acess-0fc284ebb331.json"

SPREADSHEET_ID = "1KTwTGhmgD5qhBZk9rKAY18ju-GiEWv2wpRN7TF2ahbU"

COLUNA_CODIGO = 2
 

def conectar_google_sheets():
    cliente = gspread.service_account(
        filename=CAMINHO_CREDENCIAL
    )

    planilha = cliente.open_by_key(SPREADSHEET_ID)

    return planilha


def extrair_codigos(planilha):
    codigos = []

    abas = planilha.worksheets()

    for aba in abas:
        print(f"Processando aba: {aba.title}")

        dados = aba.get_all_values()

        for linha in dados[1:]:
            if len(linha) >= COLUNA_CODIGO:
                codigo = linha[COLUNA_CODIGO - 1].strip()

                if codigo:
                    codigos.append({
                        "aba": aba.title,
                        "codigo": codigo
                    })

    return codigos


def main():
    planilha = conectar_google_sheets()

    print(f"Planilha conectada: {planilha.title}\n")

    codigos = extrair_codigos(planilha)

    print(f"\nTotal de códigos encontrados: {len(codigos)}")

    for item in codigos:
        print(
            f"Aba: {item['aba']} | "
            f"Código: {item['codigo']}"
        )


if __name__ == "__main__":
    main()