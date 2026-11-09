#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Entrada antiga. A geração de HTML ficou só em gerar-site-lead.py.

O motor anterior está em jobs/geradores/aholic-generator-template.py, só como histórico.
"""
import subprocess
import sys
from pathlib import Path

ALVO = Path(__file__).resolve().with_name("gerar-site-lead.py")


if __name__ == "__main__":
    print("A geração usa scripts/gerar-site-lead.py e a pasta temas/.", file=sys.stderr)
    raise SystemExit(subprocess.call([sys.executable, str(ALVO)] + sys.argv[1:]))
