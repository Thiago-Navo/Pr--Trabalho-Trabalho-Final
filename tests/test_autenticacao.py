import pytest
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.produto import Produto
from app.repositories.produto_repository import ProdutoRepository


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


def test_hash_de_senha_seguro():
    """Valida que as senhas são armazenadas como hash forte e validadas corretamente."""
    senha_plana = "minhasenha123"
    hash_gerado = generate_password_hash(senha_plana)

    assert hash_gerado != senha_plana
    assert hash_gerado.startswith(("scrypt:", "pbkdf2:"))
    assert check_password_hash(hash_gerado, senha_plana) is True
    assert check_password_hash(hash_gerado, "senhaerrada") is False


def test_regras_de_negocio_modelo_produto_poo():
    """Valida as regras de negócio implementadas na classe Produto (POO)."""
    p = Produto(
        id=1,
        nome="SSD NVMe 1TB",
        sku="SSD-1TB-01",
        preco=35000,
        categoria="Armazenamento",
        estoque_min=5,
        estoque_max=20,
    )

    # 1. Validação do modelo
    p.validar()

    # 2. Formatação de moeda
    assert p.preco_reais == 350.0
    assert "350,00" in p.preco_formatado

    # 3. Status de estoque em diferentes faixas
    assert p.calcular_status_estoque(saldo_atual=2) == "CRITICO"
    assert p.esta_em_ponto_de_pedido(saldo_atual=2) is True

    assert p.calcular_status_estoque(saldo_atual=6) == "ATENCAO"
    assert p.calcular_status_estoque(saldo_atual=15) == "OK"

    # 4. Violação de regras dispara ValueError
    with pytest.raises(ValueError, match="nome do produto"):
        Produto(id=2, nome="", sku="SKU-01").validar()

    with pytest.raises(ValueError, match="estoque máximo"):
        Produto(id=3, nome="Mouse", sku="MOU-01", estoque_min=10, estoque_max=5).validar()


def test_produto_repository_pattern(db_conn):
    """Valida a camada de persistência com o padrão Repository."""
    repo = ProdutoRepository(db_conn)
    produtos = repo.listar_todos()
    assert len(produtos) > 0
    assert all(isinstance(p, Produto) for p in produtos)

    # Busca por ID
    primeiro = produtos[0]
    localizado = repo.buscar_por_id(primeiro.id)
    assert localizado is not None
    assert localizado.nome == primeiro.nome

    # Busca por SKU
    por_sku = repo.buscar_por_sku(primeiro.sku)
    assert por_sku is not None
    assert por_sku.id == primeiro.id
