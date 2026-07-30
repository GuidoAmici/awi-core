"""Tests del trace_id y de la cadena de fallback.

El que da razón de ser al trace_id es `test_reconstruye_los_commits_de_un_issue`:
es la pregunta que hoy no se puede contestar — «qué commits salieron de este
issue».

En la cadena, el que importa es
`test_completar_con_una_salida_invalida_no_es_un_exito`: un delegado que corrió y
produjo algo que no era lo pedido no puede reportarse como éxito, porque el
operador creería que salió bien.
"""

import json

import pytest

import delegate_trace as dt


# ── trace_id ──────────────────────────────────────────────────────────────────

def test_deriva_del_issue_y_es_legible():
    tid = dt.nuevo(42)

    assert tid.startswith("awi-42-")
    assert dt.issue_de(tid) == 42


def test_acepta_el_issue_con_numeral():
    assert dt.issue_de(dt.nuevo("#42")) == 42


def test_dos_delegados_sobre_el_mismo_issue_se_distinguen():
    a, b = dt.nuevo(42), dt.nuevo(42)

    assert a != b
    assert dt.issue_de(a) == dt.issue_de(b) == 42


def test_un_issue_que_no_es_numero_falla():
    with pytest.raises(ValueError, match="número"):
        dt.nuevo("el-del-lunes")


def test_un_trace_id_mal_formado_falla():
    with pytest.raises(ValueError, match="forma"):
        dt.issue_de("cualquier-cosa")


def test_extrae_los_trace_id_de_un_texto():
    texto = f"corrieron {dt.nuevo(7, 'aaaaaa')} y {dt.nuevo(9, 'bbbbbb')}, más ruido"

    assert dt.extraer(texto) == ["awi-7-aaaaaa", "awi-9-bbbbbb"]


def test_el_delegado_recibe_su_trace_id_por_entorno():
    tid = dt.nuevo(42)

    assert dt.entorno(tid) == {dt.ENV_TRACE: tid}


def test_la_instruccion_de_commit_nombra_el_trailer():
    tid = dt.nuevo(42)
    texto = dt.instruccion_de_commit(tid)

    assert f"AWI-Trace: {tid}" in texto


def test_reconstruye_los_commits_de_un_issue():
    """La pregunta que hoy no tiene respuesta en ninguna parte."""
    mio, ajeno = dt.nuevo(42, "a3f1c8"), dt.nuevo(99, "ffffff")
    log = "\x00".join([
        f"aaaaaaa\nfeat: algo\n\nAWI-Trace: {mio}\n",
        "bbbbbbb\nfix: otra cosa a mano\n",
        f"ccccccc\ndocs: y otra\n\nAWI-Trace: {ajeno}\n",
        f"ddddddd\ntest: la última\n\nCo-Authored-By: X\nAWI-Trace: {mio}\n",
    ])

    assert dt.commits_de(log, mio) == ["aaaaaaa", "ddddddd"]
    assert dt.commits_de(log, ajeno) == ["ccccccc"]


def test_un_log_sin_trailers_no_devuelve_nada():
    log = "aaaaaaa\nfeat: algo sin trailer\n"

    assert dt.commits_de(log, dt.nuevo(42)) == []


# ── Cadena de fallback ────────────────────────────────────────────────────────

def test_completar_con_salida_valida_se_acepta():
    d = dt.decidir("completed", 0, salida_valida=True)

    assert d.accion == "aceptar"
    assert d.termina


def test_completar_con_una_salida_invalida_no_es_un_exito():
    """El que importa: el operador creería que salió bien."""
    d = dt.decidir("completed", 0, salida_valida=False)

    assert d.accion == "degradar"
    assert "no cumple el esquema" in d.motivo


def test_un_timeout_se_reintenta_una_vez():
    d = dt.decidir("timed-out", None, salida_valida=False, reintentos_hechos=0)

    assert d.accion == "reintentar"
    assert d.reintento == 1
    assert not d.termina


def test_un_timeout_reintentado_escala():
    d = dt.decidir("timed-out", None, salida_valida=False, reintentos_hechos=1)

    assert d.accion == "escalar"


def test_una_muerte_por_senal_se_reintenta():
    assert dt.decidir("killed", -15, salida_valida=False).accion == "reintentar"


def test_un_fallo_del_agente_no_se_reintenta():
    """Corrió y decidió que no podía: reintentarlo idéntico gasta otros 45 minutos
    para llegar al mismo lugar."""
    d = dt.decidir("failed", 1, salida_valida=False)

    assert d.accion == "escalar"
    assert "mismo lugar" in d.motivo


def test_el_tope_de_reintentos_es_de_costo_y_no_de_resiliencia():
    assert dt.MAX_REINTENTOS == 1


# ── El sistema siempre produce algo ───────────────────────────────────────────

def test_el_informe_degradado_cumple_el_mismo_esquema_que_uno_exitoso():
    """Así el consumidor no necesita dos caminos de lectura."""
    import brief_boundary as bb

    tid = dt.nuevo(42)
    informe = dt.informe_degradado(tid, 42, "timed-out", None, "se pasó del tope")

    assert bb.validate(json.dumps(informe))
    assert informe["resultado"] == "no-pudo"


def test_el_informe_degradado_dice_que_no_lo_escribio_el_delegado():
    informe = dt.informe_degradado(dt.nuevo(1), 1, "failed", 1, "x")

    assert "cadena de fallback" in informe["generado_por"]


def test_el_informe_degradado_trae_el_final_del_log():
    """Sin esto, «no pudo» no dice nada sobre por qué."""
    log = "línea vieja\n" * 500 + "ERROR: no encontró el repo\n"
    informe = dt.informe_degradado(dt.nuevo(1), 1, "failed", 1, "x", ultimas_lineas=log)

    assert "ERROR: no encontró el repo" in informe["ultimas_lineas_del_log"]
    assert len(informe["ultimas_lineas_del_log"]) <= 2000


def test_la_linea_de_inbox_lleva_el_trace_id():
    """Antes traía una línea sin identificador: no se podía correlacionar nada."""
    tid = dt.nuevo(42)
    linea = dt.linea_de_inbox(tid, "arreglar-x", dt.decidir("completed", 0, True), "3m 12s")

    assert tid in linea
    assert "arreglar-x" in linea
    assert linea.startswith("- ✓")


def test_cada_accion_tiene_su_icono():
    for estado, exit_code, valida in (
        ("completed", 0, True), ("completed", 0, False), ("failed", 1, False), ("timed-out", None, False)
    ):
        d = dt.decidir(estado, exit_code, valida)
        linea = dt.linea_de_inbox(dt.nuevo(1), "x", d, "1m")
        assert linea.startswith("- ")


def test_escalar_deja_el_informe_donde_el_operador_lo_encuentra(tmp_path):
    tid = dt.nuevo(42)
    informe = dt.informe_degradado(tid, 42, "failed", 1, "no pudo")

    destino = dt.escalar(tmp_path / "delegates", tid, informe)

    assert destino.is_file()
    assert json.loads(destino.read_text())["trace_id"] == tid


def test_escalar_no_levanta_si_no_puede_escribir(tmp_path):
    """Es el último eslabón: un fallback que falla deja al sistema sin producir
    nada, que es exactamente lo que viene a evitar."""
    ocupado = tmp_path / "archivo"
    ocupado.write_text("no soy un directorio")

    destino = dt.escalar(ocupado / "delegates", dt.nuevo(1), {"x": 1})

    assert not destino.exists()  # no escribió, pero tampoco reventó


# ── Trazado, todo junto ───────────────────────────────────────────────────────

def test_el_trazado_va_a_status_json():
    """`status.json` no tenía ninguno de estos campos."""
    t = dt.Trazado.para(42, "arreglar-x")
    t.registrar("despachado")
    t.registrar("terminó en completed")

    s = t.para_status()

    assert s["trace_id"] == t.trace_id
    assert s["issue"] == 42
    assert s["reintentos"] == 0
    assert len(s["eventos"]) == 2
    assert "despachado" in s["eventos"][0]
