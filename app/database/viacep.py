import json
import urllib.request

def buscar_endereco_por_cep(cep: str) -> dict:
    """Busca dados de endereço diretamente na API pública do ViaCEP."""
    cep_limpo = "".join(filter(str.isdigit, cep or ""))
    
    if len(cep_limpo) != 8:
        return {"erro": "CEP inválido. Forneça exatamente 8 dígitos numéricos."}

    url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TechStock-App'})
        with urllib.request.urlopen(req, timeout=5) as response:
            dados = json.loads(response.read().decode('utf-8'))
            
            if dados.get("erro"):
                return {"erro": "CEP não localizado na base do ViaCEP."}
                
            return {
                "cep": dados.get("cep"),
                "logradouro": dados.get("logradouro"),
                "complemento": dados.get("complemento"),
                "bairro": dados.get("bairro"),
                "cidade": dados.get("localidade"),
                "uf": dados.get("uf")
            }
    except Exception as e:
        return {"erro": f"Erro na comunicação com o ViaCEP: {str(e)}"}
