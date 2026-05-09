import re
from typing import Any, Dict

MAX_INPUT_LENGTH = 50000


def validate_input(text: str) -> Dict[str, Any]:
    """
    Valida o texto de entrada do usuário

    Args:
        text: Texto a ser validado

    Returns:
        Dict com resultado da validação
    """

    if not text or not text.strip():
        return {"valid": False, "message": "Por favor, forneça uma descrição da sua iniciativa."}

    # Verifica tamanho mínimo
    if len(text.strip()) < 10:
        return {
            "valid": False,
            "message": "A descrição deve ter pelo menos 10 caracteres. Seja mais específico.",
        }

    # Verifica tamanho máximo (aumentado para suportar documentos anexados)
    if len(text) > MAX_INPUT_LENGTH:
        return {
            "valid": False,
            "message": f"A descrição é muito longa. Por favor, limite a {MAX_INPUT_LENGTH} caracteres.",
        }

    # Verifica se não é apenas espaços ou caracteres especiais
    if not re.search(r"[a-zA-ZÀ-ÿ]", text):
        return {"valid": False, "message": "A descrição deve conter palavras válidas."}

    return {"valid": True, "message": "Entrada válida"}


def sanitize_text(text: str) -> str:
    """
    Sanitiza o texto de entrada removendo caracteres perigosos

    Args:
        text: Texto a ser sanitizado

    Returns:
        Texto sanitizado
    """

    if not text:
        return ""

    # Remove caracteres de controle
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]", "", text)

    # Remove tags HTML básicas por segurança
    sanitized = re.sub(r"<[^>]*>", "", sanitized)

    # Remove excesso de espaços
    sanitized = re.sub(r"\s+", " ", sanitized)

    # Remove espaços no início e fim
    sanitized = sanitized.strip()

    return sanitized


def validate_api_response(response: Dict[str, Any], required_fields: list) -> bool:
    """
    Valida se a resposta da API contém os campos necessários

    Args:
        response: Resposta da API
        required_fields: Lista de campos obrigatórios

    Returns:
        True se válida, False caso contrário
    """

    if not isinstance(response, dict):
        return False

    for field in required_fields:
        if field not in response:
            return False

    return True


import os


def check_api_keys() -> bool:
    """Verifica se as chaves de API obrigatórias estão configuradas."""
    import streamlit as st  # lazy import: evita dependência em testes unitários

    if not os.getenv("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY não configurada")
        return False
    if not os.getenv("MISTRAL_API_KEY"):
        st.error("MISTRAL_API_KEY não configurada")
        return False
    return True
