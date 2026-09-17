import pytest


@pytest.mark.parametrize(
    "papel, esperado",
    [
        ("admin", True),
        ("Administradora", True),
        ("Administrador", True),
        ("operador", False),
    ],
)
def test_regra_de_permissao_admin(papel, esperado):
    assert (papel in {"admin", "Administradora", "Administrador"}) is esperado
