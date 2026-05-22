import json
import re
from decimal import Decimal


# ---------------------------------------------------------------------------
# Funções Auxiliares
# ---------------------------------------------------------------------------

def _clean_string(text: str) -> str:
    """
    Remove espaços de borda (trim) e colapsa múltiplos espaços internos em um só.
    Também remove caracteres de controle como \t, \n, \r.
    """
    if text is None:
        return ""
    text = re.sub(r'\s+', ' ', str(text))
    return text.strip()


# ---------------------------------------------------------------------------
# Funções de Parsing Especial
# ---------------------------------------------------------------------------

def _parse_parcelas(raw: str) -> list[dict]:
    try:
        if not raw: return []
        data = json.loads(raw)
        if isinstance(data, dict): data = [data]

        return [
            {
                "valor": Decimal(_clean_string(p.get("VALOR", 0)).replace(',', '.')),
                "venc": _clean_string(p.get("VENC", ""))
            }
            for p in data
        ]
    except:
        return []


def _parse_json_and_clean(raw: str) -> list[dict]:
    """
    Lê o JSON gerado pelo SQL e aplica o trim/limpeza em todos os valores internos.
    """
    if not raw:
        return []

    try:
        data = json.loads(raw)

        if isinstance(data, dict):
            data = [data]

        if isinstance(data, list):
            cleaned_list = []
            for item in data:
                cleaned_item = {k: _clean_string(v) for k, v in item.items()}
                cleaned_list.append(cleaned_item)
            return cleaned_list

        return []
    except json.JSONDecodeError:
        return []


# Mapeamento Centralizado de Campos Especiais
_SPECIAL_FIELDS = {
    "PSE_PARCE": _parse_parcelas,
    "ITENS_CONCATENADOS": _parse_json_and_clean,
    "PSU_CC": _parse_json_and_clean,
    "PSU_CONTA": _parse_json_and_clean,
    "PSU_GERAL": _parse_json_and_clean,
}


# ---------------------------------------------------------------------------
# Classe Data
# ---------------------------------------------------------------------------

class Data:
    def __init__(self, data_dict: dict):
        """Inicializa a classe diretamente com um dicionário já processado."""
        self._data = data_dict

    # --- Acesso estilo dicionário ---
    def __getitem__(self, key: str):
        return self._data.get(key.upper())

    def __setitem__(self, key: str, value):
        self._data[key.upper()] = value

    def __contains__(self, key: str):
        return key.upper() in self._data

    def keys(self):
        return self._data.keys()

    def get(self, key: str, default=None):
        return self._data.get(key.upper(), default)

    # --- Visualização e Debug ---
    def __repr__(self):
        return f"Data({list(self._data.keys())})"

    def __str__(self):
        """Retorna todos os dados convertidos em formato JSON bonito para printar."""
        return json.dumps(self._data, indent=4, default=str, ensure_ascii=False)

    def to_dict(self) -> dict:
        """Retorna o dicionário interno (útil para integrações)."""
        return self._data

    # --- Métodos de Construção (Factory) ---
    @classmethod
    def from_raw(cls, raw_input: str | list | dict) -> "Data":
        data = raw_input
        if isinstance(raw_input, str):
            try:
                data = json.loads(raw_input)
            except json.JSONDecodeError:
                return cls({})

        if isinstance(data, list) and len(data) > 0:
            data = data[0]

        if isinstance(data, dict) and "RPA_PARAMS" in data:
            params = data["RPA_PARAMS"]
            if isinstance(params, str):
                try:
                    data = json.loads(params)
                except json.JSONDecodeError:
                    pass
            else:
                data = params

        if isinstance(data, list) and len(data) > 0:
            data = data[0]

        if not isinstance(data, dict):
            return cls({})

        return cls._parse_logic(data)

    @classmethod
    def _parse_logic(cls, d: dict) -> "Data":
        processed = {}

        # 1. Primeiro passamos por todos os campos para fazer o parse básico
        for key, value in d.items():
            upper_key = key.upper()

            if upper_key in _SPECIAL_FIELDS:
                processed[upper_key] = _SPECIAL_FIELDS[upper_key](value)
            else:
                processed[upper_key] = _clean_string(value)

        # =========================================================================
        # 2. APLICAÇÃO DA REGRA DE FALLBACK (PSU_GERAL, PSU_CONTA, PSU_CC) (Adicional e especifico para rotinas de inserção de NF
        # =========================================================================
        # itens = processed.get("ITENS_CONCATENADOS", [])
        #
        # if itens:
        #     primeiro_item = itens[0]
        #
        #     # Captura tolerante a letras maiúsculas/minúsculas vindas do banco
        #     item_cc = primeiro_item.get("cc") or primeiro_item.get("CC", "")
        #     item_dcc = primeiro_item.get("dcc") or primeiro_item.get("DCC", "")
        #     item_conta = primeiro_item.get("conta") or primeiro_item.get("CONTA", "")
        #     item_dconta = primeiro_item.get("dconta") or primeiro_item.get("DCONTA", "")
        #
        #     # Valor: tenta pegar o total do item, se não achar usa o total geral da nota
        #     item_total = primeiro_item.get("total") or primeiro_item.get("TOTAL") or processed.get("PSE_TOTAL", "0")
        #
        #     item_total = Decimal(item_total) - Decimal(primeiro_item.get('vldesc'))
        #
        #     # Se o PSU_GERAL (usado na nova rotina) estiver vazio, gera a linha padrão
        #     if not processed.get("PSU_GERAL"):
        #         processed["PSU_GERAL"] = [{
        #             "cc": item_cc,
        #             "dcc": item_dcc,
        #             "conta": item_conta,
        #             "dconta": item_dconta,
        #             "valor": item_total
        #         }]
        #
        #     # Mantém compatibilidade com módulos antigos que usem PSU_CONTA
        #     if not processed.get("PSU_CONTA"):
        #         processed["PSU_CONTA"] = [{
        #             "conta": item_conta,
        #             "dconta": item_dconta,
        #             "valor": item_total
        #         }]
        #
        #     # Mantém compatibilidade com módulos antigos que usem PSU_CC
        #     if not processed.get("PSU_CC"):
        #         processed["PSU_CC"] = [{
        #             "cc": item_cc,
        #             "dcc": item_dcc,
        #             "valor": item_total
        #         }]

        return cls(processed)
