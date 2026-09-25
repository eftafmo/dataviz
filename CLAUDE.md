# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Data and results portal for the EEA & Norway Grants (data.eeagrants.org). It is a Django 5.2 backend (Python 3.14, managed with `uv`) with a Vue 3 + D3 frontend bundled by Vite (Node 24, see `.nvmrc`). Further docs are in `docs/`: install, import, tests, map layers and local ES.

## Commands

Backend (run from the repo root; settings come from `dv/localsettings.py`, copied from `dv/localsettings.py.example`):
- `uv sync` installs dependencies, including the dev group.
- `uv run ./manage.py runserver 0:8000` starts the dev server. Run `npm run dev` next to it: the Vite dev server listens on :3000.
- `uv run pytest` runs the backend tests (`--ds=dv.settings` is set in pyproject). Run a single file with `uv run pytest dv/tests/test_import/test_import_news.py`, or a single test with `…::test_name`. Add `--cov` for coverage.
- `uv run ruff check` and `uv run ruff format --check` are the Python lint checks CI runs. Drop `--check` / add `--fix` to apply fixes.

Frontend:
- `npm run dev` starts the dev server. `npm run build` does a production build.
- `npm run lint` auto-fixes ESLint on `assets/**/*.{js,vue}` and Prettier on `assets/css/`. `npm run lint:check` is the CI version.
- `npm run test` runs the Cypress E2E suite headless against a running app on :8000. Run a single spec with `npm run test -- -s cypress/e2e/2014-2021/test-overview.cy.js`, or open the interactive runner with `npm run test:open`. E2E tests need seeded data first: `./manage.py seed_db` (or `docker compose exec web ./manage.py seed_db`).

Data:
- The DB is SQLite. Its path is set by the `DJANGO_DB_PATH` env var and defaults to `../db/eeag.sqlite3`; locally it is usually `.data/eeag.sqlite3`, copied from prod.
- Search uses Elasticsearch 7 through django-haystack (`dv/lib/es7.py`). Pinned to ES7 because haystack doesn't support ES8. Rebuild the index with `./manage.py rebuild_index --noinput`.
- `./manage.py import` pulls data for the three funding periods: 2014-2021 from MSSQL (needs `MSSQL_*` env vars and firewall access), 2009-2014 from xlsx files, 2004-2009 from JSON. See `docs/import.md`. Other commands: `import_news`, `load_fixtures initial`, `import_nuts`.

CI (`.github/workflows/tests.yml`) runs everything in docker compose: `pytest --cov`, then `seed_db`, then `npm run test`.

## Architecture

**Periods and scenarios.** `ALLOCATION_PERIODS` in `dv/views/dataviz.py` maps each period (`2014-2021`, `2009-2014`, `compare`) to its scenarios (pages such as overview, funding, cooperation, projects, global_goals, beneficiary_states, sectors). `dv/urls/frontend.py` builds the `/<period>/<scenario>/` routes from that dict. `dataviz.render` renders `templates/<scenario>.html`. To add a page, update the dict, add a template, and add a root instance (see below).

**Backend layout.** The whole project is a single Django app, `dv`:
- `dv/models.py` holds the domain models: State, PrioritySector, ProgrammeArea, Allocation, Programme, Project, Indicator, Organisation, BilateralInitiative, News, NUTS.
- `dv/views/api.py` serves the JSON endpoints under `/api/*.json` (`dv/urls/api.py`) that feed the charts. They are wrapped in `cache_page(API_CACHE_SECONDS)`.
- `dv/views/frontend.py` serves the haystack faceted search views (facet logic in `facets_rules.py`), the exports, and embeds.
- Templates use both Django templates and Jinja2 (`templates/`).
- `dv/lib/utils.py` holds shared constants: financial mechanisms and funding periods.

**Frontend layout.** There are two Vite entries, `assets/entry.js` (the dataviz app) and `assets/site.js`. `entry.js` exposes `window._createApp` and `window.Dataviz`. Templates mount Vue "content islands" by picking a root instance from `assets/js/root-instances.js`: `Index`, `Grants`, `Partners`, `Projects`, `Goals`, `Compare`, and so on. Each root instance lists its chart components in a `components: {…}` block.
- `assets/js/components/` holds the large components. `mixins/` has the shared building blocks and `includes/` the sub-components. See `docs/development.md`.
- Data flow in a component: data comes in through the `initial` prop or is fetched from the `datasource` URL prop. `processDataset()` turns it into `dataset` (CSV components also have `processRow()`). The computed `data` holds the filtered and processed view.
- Aliases are `@js` → `assets/js` and `@css` → `assets/css`. Constants live in `assets/js/constants/*.json5`.

**Gotchas.**
- `dv/views/frontend.py` parses `assets/js/root-instances.js` with a regex to discover embeddable components. When you edit that file, keep the `export const Name = { … components: { key: components.X, … } }` shape.
- Components can be embedded in third-party pages through `templates/embed.js.jinja`. Test changes both in the app and in the embed sandbox at `/embed_sandbox/`.
- The build fails if any file in `assets/sprites/` is over 8 KB (`vite-plugin-check-sprites.js`). Sprites must stay inlineable for downloadable charts, so put larger images in `assets/imgs/`.
- `vite build` writes to `../build`, outside the repo (`BUILD_DIR = ROOT_DIR/build`). Django reads `build/.vite/manifest.json` through `dv/lib/assets.py`.
- Ruff config (pyproject) enables bandit, bugbear, the django rules and more. Print statements (`T20`) are flagged.
