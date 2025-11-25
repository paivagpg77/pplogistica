## 🚚 Projeto Logística (Django)

Sistema web para gerenciamento de operações internas: cargos/salários, funcionários, metas/avaliações e locação de caminhões.

### Funcionalidades
- CRUD de funcionários e cargos
- Importação automática de JSONs (cargos e funcionários)
- Registro de metas e avaliações trimestrais
- Locação de caminhões com verificação de permissões
- Painel administrativo via Django Admin

### Rodando localmente
1. `python -m venv venv && source venv/bin/activate`
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
4. `python manage.py importar_cargos`
5. `python manage.py importar_funcionarios`
6. `python manage.py runserver`
