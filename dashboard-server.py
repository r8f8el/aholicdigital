#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prospector — servidor local do dashboard (SQLite). Sem dependências: só Python padrão.
Uso: python dashboard-server.py  (ou duplo clique em iniciar-dashboard.bat)
Abre em http://localhost:8765 — edições, exclusões e drag&drop salvam no prospector.db

A biblioteca de temas é referencias/biblioteca/catalogo.json. /api/presets e /api/temas
leem e gravam esse mesmo catálogo.
"""
import json, sqlite3, os, sys, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

CODIGO = os.path.dirname(os.path.abspath(__file__))
PASTA = os.environ.get('AHOLIC_RAIZ') or CODIGO
sys.path.insert(0, os.path.join(CODIGO, 'scripts'))
from biblioteca_temas import Biblioteca

DB = os.path.join(PASTA, 'prospector.db')
CONFIG = os.path.join(PASTA, 'prospector-config.json')
_BIB = None

def biblioteca():
    global _BIB
    if _BIB is None:
        _BIB = Biblioteca(PASTA)
        _BIB.garantir()
    return _BIB

def ler_config():
    try: return json.load(open(CONFIG, encoding='utf-8'))
    except Exception: return {}
PORTA = 8765
CAMPOS = ['slug','nome','nicho','cidade','nota','avaliacoes','email','telefone','whatsapp',
          'siteAntigo','motivo','status','urlNova','dataProposta','valor','obs',
          'contratoStatus','contratoEm','manutencao','pago','docCliente','endCliente','direcaoCriativa']

def valor_para_sqlite(valor):
    """SQLite não grava dict. A direção criativa precisa ir como JSON e voltar como objeto."""
    if isinstance(valor, (dict, list)):
        return json.dumps(valor, ensure_ascii=False)
    return valor

def valor_da_api(valor):
    if isinstance(valor, str):
        texto = valor.strip()
        if texto[:1] in '{[':
            try:
                return json.loads(texto)
            except Exception:
                return valor
    return valor

def conexao():
    c = sqlite3.connect(DB)
    c.execute('''CREATE TABLE IF NOT EXISTS leads(
        slug TEXT PRIMARY KEY, nome TEXT, nicho TEXT, cidade TEXT, nota REAL, avaliacoes INTEGER,
        email TEXT, telefone TEXT, whatsapp TEXT, siteAntigo TEXT, motivo TEXT,
        status TEXT DEFAULT 'novo', urlNova TEXT, dataProposta TEXT, valor REAL, obs TEXT,
        contratoStatus TEXT DEFAULT 'pendente', contratoEm TEXT, manutencao REAL, pago INTEGER DEFAULT 0,
        atualizado TEXT DEFAULT (datetime('now','localtime')))''')
    for col, tipo in [('contratoStatus',"TEXT DEFAULT 'pendente'"),('contratoEm','TEXT'),('manutencao','REAL'),('pago','INTEGER DEFAULT 0'),('docCliente','TEXT'),('endCliente','TEXT'),('direcaoCriativa','TEXT')]:
        try: c.execute('ALTER TABLE leads ADD COLUMN %s %s' % (col, tipo))
        except sqlite3.OperationalError: pass
    return c

def lead_por_slug(slug):
    if not slug:
        return None
    c = conexao()
    c.row_factory = sqlite3.Row
    row = c.execute('SELECT * FROM leads WHERE slug=?', (slug,)).fetchone()
    c.close()
    if not row:
        return None
    dados = dict(row)
    dados['direcaoCriativa'] = valor_da_api(dados.get('direcaoCriativa'))
    return dados

def importar_snapshot():
    """Primeira execução sem banco: importa os leads embutidos no dashboard.html."""
    try:
        html = open(os.path.join(PASTA, 'dashboard.html'), encoding='utf-8').read()
        ini = html.index('<script id="dados" type="application/json">') + len('<script id="dados" type="application/json">')
        fim = html.index('</script>', ini)
        dados = json.loads(html[ini:fim])
        c = conexao()
        for l in dados.get('leads', []):
            c.execute('INSERT OR IGNORE INTO leads (%s) VALUES (%s)' % (','.join(CAMPOS), ','.join('?'*len(CAMPOS))),
                      [valor_para_sqlite(l.get(k)) for k in CAMPOS])
        c.commit(); c.close()
        print('Snapshot importado do dashboard.html para o prospector.db')
    except Exception as e:
        print('(sem snapshot para importar: %s)' % e)

class App(SimpleHTTPRequestHandler):
    def _json(self, code, obj):
        corpo = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(corpo)))
        self.end_headers(); self.wfile.write(corpo)
    def _html(self, code, texto):
        corpo = (texto or '').encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(corpo)))
        self.end_headers(); self.wfile.write(corpo)
    def _path(self):
        bruto = unquote(self.path.split('?')[0])
        if len(bruto) > 1 and bruto.endswith('/'):
            bruto = bruto[:-1]
        return bruto
    def _corpo(self):
        n = int(self.headers.get('Content-Length', 0))
        if n > 2_000_000:
            raise ValueError('O conteúdo passa de 2 MB.')
        return json.loads(self.rfile.read(n).decode('utf-8')) if n else {}
    def _tema_partes(self):
        partes = self._path().strip('/').split('/')
        if len(partes) >= 2 and partes[0] == 'api' and partes[1] == 'temas':
            return partes
        return None
    def _ler_tema(self, tid):
        try:
            return biblioteca().resolver(tid)
        except ValueError:
            return None
    def do_GET(self):
        path = self._path()
        if path == '/api/presets':
            try:
                return self._json(200, biblioteca().listar())
            except Exception as e:
                return self._json(500, {'erro': str(e)})
        partes = self._tema_partes()
        if partes is not None:
            if len(partes) == 2:
                temas = biblioteca().listar()
                return self._json(200, {'temas': temas, 'total': len(temas)})
            tema = self._ler_tema(partes[2])
            if not tema:
                return self._json(404, {'erro': 'Tema não encontrado na biblioteca.'})
            if len(partes) == 3:
                return self._json(200, tema)
            if len(partes) == 4 and partes[3] == 'html':
                return self._html(200, biblioteca().ler_html_geracao(tema))
            if len(partes) == 4 and partes[3] == 'preview':
                return self._html(200, biblioteca().ler_preview(tema))
            return self._json(404, {'erro': 'rota'})
        if path == '/api/config':
            cfg = ler_config()
            hg = dict(cfg.get('hostgator', {}))
            hg['senhaDefinida'] = bool(hg.get('senha'))
            hg.pop('senha', None)  # a senha NUNCA sai do arquivo
            return self._json(200, {'contratante': cfg.get('contratante', {}), 'hostgator': hg})
        if path == '/api/leads':
            c = conexao(); c.row_factory = sqlite3.Row
            rows = [dict(r) for r in c.execute('SELECT * FROM leads').fetchall()]
            for r in rows:
                r['direcaoCriativa'] = valor_da_api(r.get('direcaoCriativa'))
                try:
                    v_rows = c.execute('SELECT numero, nome_estilo, descricao, arquivo, criado_em, ativo FROM versoes_site WHERE lead_slug = ? ORDER BY numero DESC', (r['slug'],)).fetchall()
                    r['versoes'] = [dict(v) for v in v_rows]
                except Exception:
                    r['versoes'] = []
            c.close()
            return self._json(200, rows)
        if path in ('/', ''):
            self.path = '/dashboard.html'
        return SimpleHTTPRequestHandler.do_GET(self)
    def _salvar_tema_corpo(self, corpo):
        if not isinstance(corpo, dict):
            return self._json(400, {'erro': 'Tema inválido.'})
        try:
            tema = biblioteca().salvar(corpo)
        except ValueError as e:
            return self._json(400, {'erro': str(e)})
        except Exception as e:
            return self._json(500, {'erro': str(e)})
        return self._json(200, {'ok': True, 'tema': tema})
    def _salvar_lista(self, lista):
        salvos = []
        try:
            for item in lista:
                if isinstance(item, dict) and (item.get('id') or item.get('nome')):
                    salvos.append(biblioteca().salvar(item))
        except ValueError as e:
            return self._json(400, {'erro': str(e)})
        except Exception as e:
            return self._json(500, {'erro': str(e)})
        return self._json(200, {'ok': True, 'temas': salvos, 'total': len(biblioteca().listar())})
    def do_POST(self):
        path = self._path()
        try:
            corpo = self._corpo()
        except Exception as e:
            return self._json(400, {'erro': str(e)})
        if path == '/api/temas/a-partir-do-site':
            if not isinstance(corpo, dict):
                return self._json(400, {'erro': 'Pedido inválido.'})
            slug = corpo.get('slug') or ''
            try:
                tema = biblioteca().salvar_de_site(slug, corpo.get('nome') or '', corpo.get('html') or '', lead_por_slug(slug))
            except ValueError as e:
                return self._json(400, {'erro': str(e)})
            except Exception as e:
                return self._json(500, {'erro': str(e)})
            return self._json(200, {'ok': True, 'tema': tema})
        if path == '/api/temas':
            return self._salvar_tema_corpo(corpo)
        if path == '/api/presets':
            if isinstance(corpo, list):
                return self._salvar_lista(corpo)
            if isinstance(corpo, dict):
                return self._salvar_tema_corpo(corpo)
            return self._json(400, {'erro': 'Lista de temas inválida.'})
        if path == '/api/leads':
            l = corpo if isinstance(corpo, dict) else {}
            c = conexao()
            c.execute('INSERT OR REPLACE INTO leads (%s) VALUES (%s)' % (','.join(CAMPOS), ','.join('?'*len(CAMPOS))),
                      [valor_para_sqlite(l.get(k)) for k in CAMPOS])
            c.commit(); c.close(); return self._json(200, {'ok': True})
        return self._json(404, {'erro': 'rota'})
    def do_PUT(self):
        path = self._path()
        try:
            corpo = self._corpo()
        except Exception as e:
            return self._json(400, {'erro': str(e)})
        if path == '/api/temas':
            return self._salvar_tema_corpo(corpo)
        if path == '/api/presets':
            if isinstance(corpo, list):
                return self._salvar_lista(corpo)
            if isinstance(corpo, dict):
                return self._salvar_tema_corpo(corpo)
            return self._json(400, {'erro': 'Lista de temas inválida.'})
        if path == '/api/config':
            cfg = ler_config()
            if 'contratante' in corpo or 'hostgator' in corpo:
                if 'contratante' in corpo:
                    ct = cfg.get('contratante', {})
                    ct.update({k: v for k, v in corpo['contratante'].items() if isinstance(v, str)})
                    cfg['contratante'] = ct
                if 'hostgator' in corpo:
                    hg = cfg.get('hostgator', {})
                    for k, v in corpo['hostgator'].items():
                        if not isinstance(v, str): continue
                        if k == 'senha' and v == '': continue  # em branco = mantém a atual
                        hg[k] = v
                    cfg['hostgator'] = hg
            else:  # compatibilidade: corpo plano = contratante
                ct = cfg.get('contratante', {})
                ct.update({k: v for k, v in corpo.items() if isinstance(v, str)})
                cfg['contratante'] = ct
            json.dump(cfg, open(CONFIG, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
            return self._json(200, {'ok': True})
        partes = path.split('/')
        if len(partes) == 4 and partes[1] == 'api' and partes[2] == 'leads':
            slug, ch = partes[3], corpo if isinstance(corpo, dict) else {}
            sets = [k for k in ch if k in CAMPOS and k != 'slug']
            if sets:
                try:
                    c = conexao()
                    c.execute('UPDATE leads SET %s, atualizado=datetime("now","localtime") WHERE slug=?' %
                              ','.join('%s=?' % k for k in sets), [valor_para_sqlite(ch[k]) for k in sets] + [slug])
                    c.commit(); c.close()
                except Exception as e:
                    return self._json(500, {'erro': str(e)})
            return self._json(200, {'ok': True})
        return self._json(404, {'erro': 'rota'})
    def do_DELETE(self):
        partes = self._path().split('/')
        if len(partes) == 4 and partes[1] == 'api' and partes[2] == 'leads':
            c = conexao(); c.execute('DELETE FROM leads WHERE slug=?', (partes[3],)); c.commit(); c.close()
            return self._json(200, {'ok': True})
        return self._json(404, {'erro': 'rota'})
    def log_message(self, *a): pass

if __name__ == '__main__':
    os.chdir(PASTA)
    novo = not os.path.exists(DB)
    conexao().close()
    if novo: importar_snapshot()
    biblioteca()
    print('Prospector rodando em http://localhost:%d  (Ctrl+C para parar)' % PORTA)
    print('Biblioteca de temas: %s' % biblioteca().caminho)
    try: webbrowser.open('http://localhost:%d' % PORTA)
    except Exception: pass
    try: ThreadingHTTPServer(('127.0.0.1', PORTA), App).serve_forever()
    except KeyboardInterrupt: print('\nEncerrado.')
