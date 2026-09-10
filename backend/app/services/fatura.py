"""Geração de faturas/recibos em PDF a partir de um trabalho."""
from datetime import date
from decimal import Decimal
from html import escape

from weasyprint import HTML

from app.config import get_settings
from app.models.trabalho import Trabalho


def _fmt_eur(v) -> str:
    if v is None:
        return "—"
    return f"{Decimal(str(v)):.2f} €"


def _fmt_data(d: date | None) -> str:
    return d.strftime("%d/%m/%Y") if d else "—"


def _linha(rotulo: str, valor: str) -> str:
    return (
        f'<tr><td class="rot">{escape(rotulo)}</td>'
        f'<td class="val">{escape(valor)}</td></tr>'
    )


def render_fatura_html(trabalho: Trabalho) -> str:
    """Constrói o HTML da fatura/recibo de um trabalho (com os seus itens)."""
    s = get_settings()

    numero = trabalho.referencia or f"#{trabalho.id}"

    empresa_linhas = "<br/>".join(
        escape(x)
        for x in [s.empresa_morada, s.empresa_contacto, f"NIF: {s.empresa_nif}" if s.empresa_nif else ""]
        if x
    )

    linhas_itens = ""
    total = Decimal("0")
    for item in trabalho.itens:
        cod = item.especialidade.codigo if item.especialidade else "—"
        if item.valor is not None:
            total += Decimal(str(item.valor))
        linhas_itens += (
            f"<tr><td>{escape(cod)}</td>"
            f"<td>{_fmt_data(item.data_adjudicacao)}</td>"
            f"<td>{_fmt_data(item.data_entrega)}</td>"
            f'<td class="num">{_fmt_eur(item.valor)}</td></tr>'
        )
    if not linhas_itens:
        linhas_itens = '<tr><td colspan="4" style="text-align:center;color:#999">Sem especialidades</td></tr>'

    return f"""<!doctype html>
<html lang="pt">
<head>
<meta charset="utf-8"/>
<style>
  @page {{ size: A4; margin: 2cm; }}
  body {{ font-family: sans-serif; color: #222; font-size: 12px; }}
  .cabecalho {{ display: flex; justify-content: space-between; border-bottom: 2px solid #333;
                padding-bottom: 12px; margin-bottom: 24px; }}
  .empresa h1 {{ margin: 0 0 4px 0; font-size: 18px; }}
  .empresa p {{ margin: 0; color: #555; font-size: 11px; }}
  .doc {{ text-align: right; }}
  .doc h2 {{ margin: 0; font-size: 16px; color: #333; }}
  .doc p {{ margin: 2px 0; color: #555; }}
  table.dados {{ width: 100%; border-collapse: collapse; margin-top: 8px; margin-bottom: 20px; }}
  table.dados td {{ padding: 5px 8px; border-bottom: 1px solid #eee; }}
  td.rot {{ color: #666; width: 35%; }}
  td.val {{ font-weight: 600; }}
  table.itens {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
  table.itens th {{ text-align: left; background: #f2f2f2; padding: 6px 8px; font-size: 11px; }}
  table.itens td {{ padding: 6px 8px; border-bottom: 1px solid #eee; }}
  table.itens td.num, table.itens th.num {{ text-align: right; }}
  .total {{ margin-top: 20px; text-align: right; }}
  .total .valor {{ font-size: 22px; font-weight: 700; }}
  .rodape {{ margin-top: 48px; color: #888; font-size: 10px; text-align: center;
             border-top: 1px solid #eee; padding-top: 8px; }}
</style>
</head>
<body>
  <div class="cabecalho">
    <div class="empresa">
      <h1>{escape(s.empresa_nome)}</h1>
      <p>{empresa_linhas}</p>
    </div>
    <div class="doc">
      <h2>Recibo</h2>
      <p>Ref.: {escape(numero)}</p>
      <p>Data: {_fmt_data(date.today())}</p>
    </div>
  </div>

  <table class="dados">
    {_linha("Cliente", trabalho.cliente or "—")}
    {_linha("Contacto", trabalho.contacto or "—")}
    {_linha("Localidade", trabalho.localidade or "—")}
    {_linha("Endereço", trabalho.endereco or "—")}
  </table>

  <table class="itens">
    <thead>
      <tr><th>Especialidade</th><th>Adjudicação</th><th>Entrega</th><th class="num">Valor</th></tr>
    </thead>
    <tbody>
      {linhas_itens}
    </tbody>
  </table>

  <div class="total">
    <div>Total</div>
    <div class="valor">{_fmt_eur(total)}</div>
  </div>

  <div class="rodape">
    Documento gerado por {escape(s.empresa_nome)} — {_fmt_data(date.today())}
  </div>
</body>
</html>"""


def gerar_fatura_pdf(trabalho: Trabalho) -> bytes:
    """Gera o PDF (bytes) da fatura/recibo de um trabalho."""
    html = render_fatura_html(trabalho)
    return HTML(string=html).write_pdf()
