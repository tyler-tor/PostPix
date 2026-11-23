# Postpix Modernization Plan

Audit date: 2026-11-23. Audited commit: `1e3945b` on `main` (last change Feb 2023).
This file is a plan only. No code has been changed.

**Total items: 48** (P1-P48). Each item is meant to be one git commit (or one small PR) and can be approved or skipped on its own. "Depends on" lists items that should land first.

## Top 5 recommendations

1. **P1 - Rotate the leaked AWS key now.** A real AWS access key (and a Flask SECRET_KEY) was committed in a `.env` file in Nov 2022. It was later deleted, but it is still in git history, and the GitHub repo is public. Deleting a file does not remove it from history.
2. **P3 - Close the authorization holes.** Any logged-in user can edit any other user's caption, and anyone (even logged out) can upload files into your S3 bucket.
3. **P12-P15 - Bring the backend to current Python 3.12 / Flask 3 / SQLAlchemy 2.** The pinned packages have **81 known vulnerabilities** (pip-audit), Python 3.9 is end-of-life, and one import (`from crypt import methods`) crashes on Python 3.13+.
4. **P16 - Replace Create React App with Vite.** `react-scripts` is abandoned; the lockfile reports **193 npm audit findings (16 critical, 56 high)**, almost all from the old build chain.
5. **P33-P36 - Docker + CloudFront "single front door" design.** Put the S3 site and the EC2 API behind one CloudFront distribution (`/api/*` goes to EC2). Same origin means login cookies and CSRF work with no CORS setup, and it is cheap.

## Confirmed bugs found during the audit (read the code to confirm; not run)

| Bug | Where | Fixed by |
|---|---|---|
| Any logged-in user can change any post's caption (no owner check) | `app/api/post_routes.py` `update_post` | P3 |
| `POST /api/posts/` has `@login_required` commented out, so logged-out users get a 500 error; it also returns "the newest post in the DB", which can be someone else's | `post_routes.py` `create_post` | P3 |
| `/api/img/upload` needs no login, so anyone can fill your bucket | `app/api/img_routes.py` | P3 |
| Upload file names use a comma instead of a dot (`abc123,jpg`) | `app/s3_helpers.py` `get_unique_filename` | P7 |
| Upload URLs are `http://`, and the `public-read` ACL is rejected by new S3 buckets (ACLs are off by default since 2023), so uploads would fail on a new bucket | `s3_helpers.py` | P7, P37 |
| A user can like the same post many times (no unique constraint, no check) | `post_routes.py` `like_post`, `app/models/postLike.py` | P6 |
| Unlike returns the old like count (dict built before the decrement) | `post_routes.py` `unlike_post` | P6 |
| Like counter disagrees with real likes: seed data has `posts.likes` summing to 130 but only 17 `post_likes` rows | `app/seeds/posts.py`, `app/dev.db` | P6 |
| Home feed is grouped by followed user, not sorted by time (one query per followed user, never merged/sorted; frontend does not sort either) | `app/api/me_routes.py` | P10 |
| `GET /api/posts/<id>` for a missing post crashes (calls `.to_dict()` before the None check) | `post_routes.py` `get_post_by_id` | P5 |
| Deleting another user's account crashes with `TypeError` (passes an Exception to a function expecting a dict) | `app/api/user_routes.py` `delete_user` | P5 |
| Several routes return nothing (Flask turns that into a 500) when a user is missing or not followed | `user_routes.py` follow/unfollow/following/likes | P5 |
| `CSRFProtect` is imported but never turned on; routes without forms (delete post, like, follow, delete account) have no CSRF check | `app/__init__.py` | P4 |
| A missing `csrf_token` cookie causes a 500 (`request.cookies['csrf_token']`) | every form route | P4 |
| `from crypt import methods` (an unused auto-import) breaks on Python 3.13+ | `post_routes.py`, `user_routes.py`, `comment_routes.py` | P9 |
| Raw SQL strings in `db.session.execute(...)` fail on SQLAlchemy 2.0 | `app/seeds/*.py` | P14 |
| Every user's email is returned to any logged-in user (`/api/users/` returns all users with emails) | `app/models/user.py` `to_dict` | P8 |
| No `<meta name="viewport">` and zero CSS media queries, so phones show a shrunken desktop page | `react-app/public/index.html`, all CSS | P27, P28 |
| `/:userId` route catches every unknown URL; no 404 page | `react-app/src/App.js` | P31 |
| One fetch uses a relative path (`api/comments/...` with no leading `/`) | `react-app/src/store/comments.js` | P5 |
| Site was flagged as phishing in Feb 2023 (several commits try to fix it) - the login page closely imitates Instagram | `react-app/src/components/LoginPage/*` | P11 |

## Secrets and committed files (names only)

- **`.env` in git history** (added/removed in commits between 2022-11-03 and 2022-11-05). Contains an AWS access key ID pattern (`AKIA...`), an S3 secret and a Flask SECRET_KEY. **Repo is public on GitHub.** -> P1.
- `app/dev.db` (SQLite) is committed even though `.gitignore` lists `*.db`. Contents are seed data only (15 demo users at `@aa.io`, hashed passwords). -> P2.
- 25+ `__pycache__/*.pyc` files are committed. -> P2.
- `.env.example` and `.envexample` are duplicates (placeholder values only, no real secrets). -> P2, P47.
- `.github/workflows/main.yml` deploys to Heroku (dead) using repo secrets `HEROKU_API_KEY` / `HEROKU_APP_NAME` - delete those secrets in GitHub settings too. -> P39.

## Quick glossary

- **Docker image / container**: an image is a packaged app plus everything it needs to run; a container is a running copy of it.
- **docker compose**: a YAML file that starts several containers together (here: the API and Postgres).
- **EC2**: a rented virtual Linux server on AWS.
- **S3**: AWS file storage ("buckets"). Can host a static website's files.
- **CloudFront**: AWS's CDN (content delivery network). It caches files close to users and can route different URL paths to different backends ("origins").
- **OAC (Origin Access Control)**: lets CloudFront read a *private* S3 bucket, so the bucket never has to be public.
- **IAM role / instance profile**: AWS permissions attached to the EC2 server itself, so the app needs no access keys in `.env`.
- **SSM Session Manager**: open a shell on EC2 from the AWS console/CLI with no SSH key and no open port 22.
- **Terraform**: write your AWS setup as code (`.tf` files); `terraform apply` creates it, `terraform destroy` removes it.
- **OIDC (for GitHub Actions)**: GitHub proves its identity to AWS for each run, so you store no AWS keys in GitHub.
- **N+1 query**: loading a list with 1 query, then running 1 more query per item. 50 posts = 51 queries.
- **CSRF**: a malicious site tricking your browser into sending a request to Postpix with your login cookie.
- **IDOR**: changing an ID in a URL to act on someone else's data.
- **App factory**: a `create_app()` function that builds the Flask app, so tests and scripts can create fresh copies with different settings.

## Recommended order

1. **Safety first:** P1, P2
2. **Backend foundation:** P12, P42 (test skeleton), P13, P14, P15
3. **Backend fixes (each with a test):** P3, P4, P5, P6, P7, P8, P9, P10, P20, P21, P22, P23
4. **Local Docker:** P33, P34, P47
5. **CI:** P44, P45
6. **Frontend foundation:** P16, P17, P18, P25
7. **Look and feel:** P11, P27, P28, P29, P30, P31, P24, P32, (optional P19), P43
8. **AWS:** P35, P36, P37, P38, P39, P40, P41, P26
9. **Docs:** P46, P48 (P46 can also be done early and updated at the end)

---

## 1. Critical fixes & security

### P1 - Rotate the leaked AWS key and Flask secret (Tyler action, no code)
- **What:** In the AWS console (IAM -> Users -> Security credentials), deactivate and delete the access key that was in the old `.env`. Check CloudTrail / the bill for unexpected use. If the key belonged to a teammate's account, tell them. Generate a new long random `SECRET_KEY` for the new deployment. Optionally rewrite git history with `git filter-repo` to remove `.env` (see open questions; this needs a force-push).
- **Why:** The repo is public, and bots scan GitHub history for `AKIA...` keys within minutes. A live key can rack up large AWS bills.
- **Files:** none (history rewrite would touch all commits).
- **Risk:** low (rotation) / high (history rewrite). **Effort:** S. **Depends on:** nothing. Do this first.

### P2 - Repo hygiene: stop tracking files that should never be in git
- **What:** `git rm --cached app/dev.db` and all `__pycache__/` folders; delete the duplicate `.envexample`; add Python entries (`__pycache__/`, `*.pyc`, `.venv/`, `instance/`), `react-app/build/`, `.terraform/`, `*.tfstate*` to the root `.gitignore`.
- **Why:** Committed DB and bytecode files cause merge noise, leak data, and make the repo look unmaintained to reviewers.
- **Files:** `.gitignore`, `app/dev.db`, `**/__pycache__/*`, `.envexample`.
- **Risk:** low. **Effort:** S. **Depends on:** none.

### P3 - Close authorization holes
- **What:** (a) `update_post`: return 403 unless `post.user_id == current_user.id`. (b) `create_post`: restore `@login_required` and return the post you just created (`post.to_dict()` after commit) instead of "newest post in the table". (c) `/api/img/upload`: add `@login_required`. (d) Same owner check pattern reviewed on every PUT/DELETE.
- **Why:** Today any user can rewrite anyone's caption (IDOR), and anonymous users can upload to your S3 bucket (cost and abuse risk).
- **Files:** `app/api/post_routes.py`, `app/api/img_routes.py`.
- **Risk:** low. **Effort:** S. **Depends on:** none (P42 lets you add tests for it).

### P4 - Turn CSRF protection on properly
- **What:** Call `CSRFProtect(app)` so *every* POST/PUT/DELETE is checked. Make the `csrf_token` cookie readable by JS (not `httponly`; it is not a secret on its own) and send it from the frontend in an `X-CSRFToken` header through one shared `apiFetch()` helper. Remove the `form['csrf_token'].data = request.cookies['csrf_token']` lines. Change logout from GET to POST.
- **Why:** Copying the cookie into the form on the server defeats the "double submit" idea. Today protection mostly relies on browser cookie defaults, routes with no form have no check, and a missing cookie gives a 500.
- **Files:** `app/__init__.py`, all `app/api/*_routes.py`, new `react-app/src/utils/apiFetch.js`, all `react-app/src/store/*.js`.
- **Risk:** med (touches every write call). **Effort:** M. **Depends on:** P12 makes this cleaner; same-origin design in P36 keeps it simple.

### P5 - Consistent error handling and 404s
- **What:** Use `db.get_or_404()` / `abort(403)` everywhere; add JSON error handlers for 400/401/403/404/413/500 that return `{"errors": [...]}`; every route returns a response (no implicit `None`). Fix `get_post_by_id`, `delete_user` (TypeError), follow/unfollow/following/likes routes, comment update/create on missing objects. Fix the relative `api/comments/...` fetch path. Return 400 (not 401) for form validation errors.
- **Why:** Many normal mistakes (bad ID, already-following) currently produce 500 errors, which look broken and hide real bugs.
- **Files:** `app/__init__.py` (or new `app/errors.py`), all `app/api/*.py`, `react-app/src/store/comments.js`.
- **Risk:** low. **Effort:** M. **Depends on:** P14 (`db.get_or_404` is Flask-SQLAlchemy 3).

### P6 - Make likes correct
- **What:** Add a unique constraint on `post_likes(user_id, post_id)` (migration). In `like_post`, return 409 or no-op if already liked. Drop the denormalized `posts.likes` counter and compute counts with a grouped query (or keep the counter but update it atomically in SQL and recount in a migration). Fix `unlike_post` returning the stale count. Fix seed data so counts match real rows.
- **Why:** Double-likes are possible today, the count shown can be wrong, and seed data shows 130 "likes" backed by 17 real rows.
- **Files:** `app/models/postLike.py`, `app/models/posts.py`, `app/api/post_routes.py`, `app/seeds/posts.py`, `app/seeds/postLikes.py`, new migration.
- **Risk:** med (schema change). **Effort:** M. **Depends on:** P15.

### P7 - Harden image uploads
- **What:** Set `MAX_CONTENT_LENGTH` (e.g. 10 MB, returns 413). Accept only jpg/png/webp/gif (drop pdf). Open the file with Pillow to confirm it is really an image. Fix the comma-in-filename bug. Store under a prefix like `uploads/<uuid>.webp`; set `ContentType` from the detected type, not the client's claim. Remove `ACL='public-read'`; build `https://` URLs pointing at CloudFront (P37).
- **Why:** No size limit = memory/cost abuse; client-supplied type can be spoofed; public ACLs are disabled by default on new buckets so uploads would fail.
- **Files:** `app/s3_helpers.py`, `app/api/img_routes.py`, config, `requirements.txt` (Pillow).
- **Risk:** low. **Effort:** M. **Depends on:** P13; pairs with P24 (resizing) and P37 (bucket).

### P8 - Stop exposing private user data
- **What:** Split serialization into `to_public()` (id, username, names, picture, counts) and `to_self()` (adds email). Only `/api/auth/` and login/signup return `to_self()`.
- **Why:** Any logged-in user (including the shared demo account) can download every user's email from `/api/users/`.
- **Files:** `app/models/user.py`, `app/api/user_routes.py`, `app/api/auth_routes.py`, frontend stores that read `email` (check `react-app/src/store/*`).
- **Risk:** low. **Effort:** S. **Depends on:** none; P20 builds on it.

### P9 - Config and input hardening
- **What:** Fail fast if `SECRET_KEY` is missing in production; `SQLALCHEMY_ECHO` off by default (currently `True`, which logs every SQL query in prod); `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_SAMESITE='Lax'`, `REMEMBER_COOKIE_*`; remove `flask-cors` (not needed with same-origin, P36) or restrict to your domain; delete the three `from crypt import methods` lines; add `Length(max=...)` validators matching DB columns (caption 150, comment 255, username 40), real `Email()` + `PasswordField` with minimum length on signup; strip whitespace. Remove the Heroku `https_redirect` hook (CloudFront handles HTTPS redirects).
- **Why:** Over-long input currently hits the DB and errors (500); verbose SQL logs leak data and slow things down; the crypt import breaks on Python 3.13.
- **Files:** `app/config.py`, `app/__init__.py`, `app/forms/*.py`, `app/api/*.py`.
- **Risk:** low. **Effort:** S. **Depends on:** P12.

### P10 - Fix the home feed (bug + speed)
- **What:** Replace the per-followed-user loop with one query: posts where `user_id IN (select followed_id from follows where follower_id = me)`, `ORDER BY created_at DESC`, with `selectinload` for the author. Optionally include your own posts.
- **Why:** Today the feed shows all of user A's posts, then all of user B's, not newest-first, and runs 1 + N + M queries.
- **Files:** `app/api/me_routes.py`.
- **Risk:** low. **Effort:** S. **Depends on:** P14. Pagination added in P22.

### P11 - Distinct branding to avoid phishing flags
- **What:** Give Postpix its own logo, colors and login layout; remove the Instagram-style phone screenshot (`screenshot1-2x.png`), unused `Instagram_logo.png`, `alt="instagram"` / `alt="Instagram Post"`, and "Finstagram" text. Add a clear "portfolio demo" note on the login page.
- **Why:** Commit history shows the site was flagged as phishing (Feb 2023). A login page that looks like Instagram's on an unrelated domain is exactly what Google Safe Browsing flags; it also avoids trademark issues.
- **Files:** `react-app/src/components/LoginPage/*`, `react-app/src/images/*`, `NavBar/index.js`, `SinglePostModal.js`, `HomeFeed/SideStuff.js`.
- **Risk:** low. **Effort:** M. **Depends on:** none (easier after P16).

---

## 2. Dependency upgrades

Current vs latest (checked 2026-11-23 with `pip index versions` / `npm view`):

| Package | Pinned | Latest |
|---|---|---|
| Python (Dockerfile / Pipfile) | 3.9 (EOL Oct 2025) | 3.12 recommended (3.13/3.14 also fine after P9) |
| Flask / Werkzeug | 2.0.1 / 2.0.1 | 3.1.3 / 3.1.9 |
| Flask-SQLAlchemy / SQLAlchemy | 2.5.1 / 1.4.19 | 3.1.1 / 2.0.58 |
| Flask-Migrate / Alembic | 3.0.1 / 1.6.5 | 4.1.0 / 1.20.1 |
| Flask-Login / Flask-WTF / WTForms | 0.5.0 / 0.15.1 / 2.3.3 | 0.6.3 / 1.3.0 / 3.2.2 |
| gunicorn / boto3 | 20.1.0 / 1.26.4 | 27.0.1 / 1.44.10 |
| Postgres driver | `psycopg2` (unpinned, installed in Dockerfile) | `psycopg[binary]` 3.3.9 |
| react / react-dom | 17 | 19.3.1 |
| react-router-dom | 5 | 7.18.6 |
| react-redux / redux / redux-thunk | 7 / 4 / 2 | 9.3.1 / 5.0.1 / 3.1.0 (or @reduxjs/toolkit 2.15.0) |
| react-scripts (CRA) | 4.0.3 | 5.0.1, abandoned -> replace with Vite 8 |

pip-audit on `requirements.txt`: **81 known vulnerabilities in 10 packages** (werkzeug, urllib3, flask-cors, jinja2, mako, idna, gunicorn, flask, dnspython, python-dotenv). npm audit on `package-lock.json`: **193 (16 critical, 56 high)**.

### P12 - Refactor to an app factory with config classes
- **What:** Move setup into `create_app(config_name)` in `app/__init__.py`; `DevConfig` (SQLite or compose Postgres), `TestConfig` (SQLite in memory, CSRF off), `ProdConfig`. Blueprints and extensions registered inside. Add a `wsgi.py` (`app = create_app()`) for gunicorn. Add `/api/health` returning `{"status":"ok"}` (used by Docker and CloudFront checks).
- **Why:** Needed for tests (P42), for Docker (P33), and to stop config crashing at import time (`DATABASE_URL.replace` throws if the variable is missing).
- **Files:** `app/__init__.py`, `app/config.py`, new `wsgi.py`, `migrations/env.py` (minor).
- **Risk:** med. **Effort:** M. **Depends on:** none.

### P13 - Upgrade Python to 3.12 and backend packages to current
- **What:** One dependency tool: drop `Pipfile`/`Pipfile.lock`, keep a short `requirements.in` (direct deps only) compiled to a pinned `requirements.txt` with `pip-compile` (or use `uv`). Remove unused pins (`GeoAlchemy2`, `python-editor`, `greenlet`, `click`, `six`, etc. come in transitively or are unused). Add `psycopg[binary]`, `Pillow`. Separate `requirements-dev.txt` (pytest, ruff, moto, pip-audit).
- **Why:** Clears the 81 known vulnerabilities, gets security fixes going forward, and removes the "two dependency files that disagree" problem (CI regenerates requirements.txt from Pipfile today).
- **Files:** `requirements.in`, `requirements.txt`, `requirements-dev.txt`, delete `Pipfile`, `Pipfile.lock`.
- **Risk:** med (Flask 3 / WTForms 3 / Flask-Login 0.6 small API changes). **Effort:** M. **Depends on:** P12; land together with P14.

### P14 - Update code to SQLAlchemy 2.0 / Flask-SQLAlchemy 3 style
- **What:** `Model.query.get(id)` -> `db.session.get(Model, id)` / `db.get_or_404`; `db.session.execute("...")` -> `text("...")` or ORM deletes in seeds; `lazy='dynamic'` -> `lazy='select'` or `WriteOnlyMapped`; `datetime.now` -> timezone-aware `func.now()` server defaults; return ISO-8601 timestamps instead of Flask's default HTTP-date strings.
- **Why:** `Query.get` and string SQL are removed/deprecated in 2.0; seeds would crash.
- **Files:** `app/models/*.py`, `app/api/*.py`, `app/forms/*.py`, `app/seeds/*.py`, frontend date formatting.
- **Risk:** med. **Effort:** M. **Depends on:** P13.

### P15 - Remove the Heroku schema hack and reset migrations
- **What:** Delete `SCHEMA` / `add_prefix_for_prod` / `environment == "production"` branches (they existed because App Academy's shared Heroku Postgres put each student in a schema). Replace the 4 old migrations (one is empty, one swaps a `followers` table for `follows`) with one clean baseline migration generated from the models, then add P6/P21 changes as new migrations. Delete the commented-out `app/seeds/follows.py` model/seed leftovers and `app/models/follows.py`.
- **Why:** You own a dedicated Postgres container now; the hack makes every model harder to read and has broken prod deploys before. No production data needs preserving (Heroku is gone).
- **Files:** `app/models/*.py`, `app/seeds/*.py`, `migrations/versions/*`, `migrations/env.py`.
- **Risk:** med (fine because there is no live data). **Effort:** M. **Depends on:** P14. **Open question:** confirm no old data must be kept.

### P16 - Replace Create React App with Vite
- **What:** Add `vite.config.js` with the React plugin and a dev proxy (`/api` -> `http://localhost:5000`), move `public/index.html` to `react-app/index.html`, rename `.js` files containing JSX to `.jsx`, switch `process.env.NODE_ENV` checks to `import.meta.env`, remove `react-scripts`, `http-proxy-middleware` and the CRA testing libs (re-added in P43 with Vitest). Use Node 22 LTS.
- **Why:** CRA is unmaintained and is the source of most of the 193 audit findings; Vite builds in seconds and produces smaller bundles.
- **Files:** `react-app/package.json`, `react-app/package-lock.json`, new `react-app/vite.config.js`, `react-app/index.html`, `react-app/src/**/*`.
- **Risk:** med. **Effort:** M. **Depends on:** none (frontend track).

### P17 - Upgrade React 17 -> 19
- **What:** `ReactDOM.render` -> `createRoot`; bump `react`, `react-dom`, `react-redux` (9), FontAwesome / react-icons; fix any StrictMode double-effect issues (effects that fetch twice in dev).
- **Why:** React 17 is out of support; React 19 removed `ReactDOM.render`. Newer libraries require 18+.
- **Files:** `react-app/src/index.js(x)`, `react-app/package.json`, components with effects.
- **Risk:** med. **Effort:** S-M. **Depends on:** P16.

### P18 - Upgrade react-router v5 -> v7
- **What:** `Switch` -> `Routes`, `useHistory` -> `useNavigate`, rewrite `ProtectedRoute` as a layout route with `<Outlet/>`, add a `*` 404 route, and move profiles to `/u/:username` (or keep `/:userId` but put it last).
- **Why:** v5 is unmaintained and does not support React 19 well; the current catch-all `/:userId` swallows unknown URLs.
- **Files:** `react-app/src/App.js(x)`, `ProtectedRoute.js`, every component using `useHistory`/`NavLink`/`useParams`.
- **Risk:** med. **Effort:** M. **Depends on:** P17.

### P19 - (Optional) Move to Redux Toolkit
- **What:** Replace 15 hand-written reducers (several duplicate the same data: `follow`, `followers`, `profileFollowing`, `notFollowed`, `users`, `searchUsers`; `comments` is registered twice) with a few RTK slices, or RTK Query for server data (handles caching, loading states, refetch).
- **Why:** Less code, fewer stale-data bugs, built-in loading/error state for P31. Optional because it is the biggest frontend change.
- **Files:** `react-app/src/store/*`, most components.
- **Risk:** high. **Effort:** L (split into one commit per slice). **Depends on:** P17.

---

## 3. Performance

### P20 - Lightweight user payloads (biggest backend speed win)
- **What:** `User.to_dict()` loads full follower list, following list and likes for *every* user it serializes (3 extra queries each). Return counts (`followerCount`, `followingCount`) via SQL `COUNT` subqueries and `isFollowedByMe` instead of lists; load the full follower list only in the followers modal endpoint (paginated). Rewrite `/notfollowing` as one `NOT IN (subquery)` query with `LIMIT` (it currently loads all users and filters by username in Python). Use `selectinload` wherever authors/comments are attached.
- **Why:** `/api/users/` with 15 users is ~46 queries; with 1,000 users it is thousands, plus megabytes of JSON. Login and `/api/auth/` pay the same cost.
- **Files:** `app/models/user.py`, `app/api/user_routes.py`, `app/api/auth_routes.py`, frontend components that read `user.followers` arrays (`UserInfoBox`, follow buttons, stores).
- **Risk:** med (frontend shape change). **Effort:** M. **Depends on:** P8, P14.

### P21 - Add database indexes
- **What:** Index the foreign keys the app filters on: `posts(user_id, created_at DESC)`, `comments(post_id)`, `post_likes(post_id)`, `follows(followed_id)` (the unique `(follower_id, followed_id)` already covers follower lookups); make follow columns `NOT NULL` with `ON DELETE CASCADE`.
- **Why:** Postgres does not index foreign keys automatically; feeds and profile pages will scan whole tables as data grows.
- **Files:** `app/models/*.py`, new migration.
- **Risk:** low. **Effort:** S. **Depends on:** P15.

### P22 - Pagination and infinite scroll
- **What:** Cursor pagination (`?before=<created_at>,<id>&limit=12`) on feed, explore, profile posts, comments, followers/following lists. Frontend loads the next page with an `IntersectionObserver` "sentinel" at the bottom.
- **Why:** Every list endpoint currently returns everything; explore returns every post ever made.
- **Files:** `app/api/post_routes.py`, `me_routes.py`, `user_routes.py`, `react-app/src/store/*`, `ExplorePage`, `HomeFeed`, `UserProfile`, `PostGrid`.
- **Risk:** med. **Effort:** M. **Depends on:** P10, P21 (P19 makes it easier).

### P23 - Server-side user search
- **What:** Add `GET /api/users/search?q=ab&limit=10` (case-insensitive prefix match on username, index on `lower(username)`), debounced 250 ms in the search bar.
- **Why:** The NavBar downloads *all* users with all their relations every time it mounts, just to filter in the browser.
- **Files:** `app/api/user_routes.py`, `react-app/src/components/NavBar/SearchBar.js`, `react-app/src/store/search_users.js`, `users.js`, migration for the index.
- **Risk:** low. **Effort:** S. **Depends on:** P20.

### P24 - Image optimization
- **What:** (a) Delete the unused 4.7 MB `src/images/stock.jpg` and its import; convert `screenshot1-2x.png` (650 KB, also replaced in P11) and other images to WebP/SVG. (b) On upload, resize with Pillow to max 1080 px wide WebP plus a ~320 px thumbnail for grids. (c) Add `loading="lazy"`, `decoding="async"`, `width`/`height` (or `aspect-ratio` CSS) to post images to stop layout jumps. (d) Long cache headers on uploads (unique filenames never change).
- **Why:** Phone photos are often 3-8 MB; the explore grid would download full-size images for tiny thumbnails.
- **Files:** `react-app/src/images/*`, `PostGrid.js`, `SinglePostModal.js`, `HomeFeed/ActualFeed.js`, `app/s3_helpers.py`, `app/api/img_routes.py`, `models/posts.py` (thumbnail URL column).
- **Risk:** low. **Effort:** M. **Depends on:** P7.

### P25 - Bundle and dead-code cleanup
- **What:** Remove unused `Temp*` components (`TempFollow`, `TempLogin`, `TempLogout`, `TempPost`, `TempComment`, `UsersList`, `User.js`) and their hard-coded test fetches (`/api/posts/1`, `/api/comments/4`); remove ~92 `console.log` calls; pick one icon library (FontAwesome *or* react-icons); lazy-load routes with `React.lazy`; delete large commented-out blocks.
- **Why:** Smaller download, faster first paint, easier code for reviewers.
- **Files:** `react-app/src/components/**`, `App.js`, `package.json`.
- **Risk:** low. **Effort:** S. **Depends on:** P16 (can be done before).

### P26 - Server tuning and caching
- **What:** `gunicorn.conf.py` with 2-3 workers (`gthread`, 2-4 threads) sized for a small instance, `--preload`, access logs to stdout. Postgres container tuned for small memory (`shared_buffers` ~128 MB). CloudFront cache policy: long TTL for hashed JS/CSS and uploads, no caching for `/api/*` and `index.html`. Turn on gzip/Brotli in CloudFront.
- **Why:** A t4g.micro/small has 1-2 GB RAM; default settings can run it out of memory.
- **Files:** new `gunicorn.conf.py`, `docker-compose.yml`, Terraform CloudFront module.
- **Risk:** low. **Effort:** S. **Depends on:** P33, P36.

---

## 4. UI/UX & accessibility

### P27 - Fix the HTML shell
- **What:** Add `<meta name="viewport" content="width=device-width, initial-scale=1">`, a meta description, `theme-color`, Open Graph tags for link previews, a proper favicon/app icons; consistent title "Postpix".
- **Why:** Without the viewport tag, phones render a zoomed-out desktop page.
- **Files:** `react-app/index.html` (after P16) / `react-app/public/index.html`.
- **Risk:** low. **Effort:** S. **Depends on:** none.

### P28 - Responsive layout
- **What:** There are zero `@media` queries today. Mobile-first CSS: top bar + bottom tab bar on phones, 3-column grid that shrinks gracefully, full-screen post modal on small screens, side suggestions hidden under ~1000 px. Use CSS Grid, `clamp()` for spacing/typography.
- **Why:** Recruiters often open portfolio links on phones.
- **Files:** all `*.css` under `react-app/src`, `NavBar`, `HomeFeed`, `SinglePostModal`, `PostGrid`, `UserProfile`.
- **Risk:** low. **Effort:** L (split per page). **Depends on:** P27; easier after P30 tokens (P32).

### P29 - Accessible modals
- **What:** Rebuild `context/Modal.js` on the native `<dialog>` element (or add `role="dialog"`, `aria-modal`, `aria-labelledby`): Escape closes, focus moves into the modal and returns to the opener, background scroll locked, close button with a label.
- **Why:** Keyboard and screen-reader users can't use or leave the current modals; the app relies on modals for posts, likes, followers and editing.
- **Files:** `react-app/src/context/Modal.js`, `Modal.css`, every `*Modal.js`.
- **Risk:** low. **Effort:** M. **Depends on:** P17 preferred.

### P30 - Semantic HTML, alt text, keyboard and contrast
- **What:** Give every image real `alt` text (7 `<img>` lack it; post images use the caption); turn clickable `<div>/<span>/<img>` into `<button>` or `<Link>`; visible focus styles; `<label>` for every input; `aria-pressed` on like/follow buttons; check color contrast (WCAG AA); `<main>`, `<nav>`, heading order.
- **Why:** Basic WCAG 2.1 AA; you already know this area from the company website work.
- **Files:** most components under `react-app/src/components`.
- **Risk:** low. **Effort:** M. **Depends on:** none.

### P31 - Loading, empty, error states, 404 page, optimistic updates
- **What:** App shows a spinner/skeleton instead of a blank page (`return null`) while checking login; empty states ("Follow people to fill your feed"); a toast for API errors; a 404 page for unknown routes/users; likes and follows update the UI instantly and roll back on failure.
- **Why:** Feels fast and finished; current failures are silent.
- **Files:** `App.js`, `HomeFeed`, `ExplorePage`, `UserProfile`, like/follow components, new `components/Toast`, `components/NotFound`.
- **Risk:** low. **Effort:** M. **Depends on:** P5, P18.

### P32 - Visual refresh with design tokens
- **What:** CSS custom properties for colors, spacing, radius, font sizes; one font stack; consistent buttons/inputs; optional dark mode with `prefers-color-scheme`; refreshed screenshots.
- **Why:** "Look great" goal; tokens make P28 and P11 consistent and future changes cheap.
- **Files:** `react-app/src/index.css`, all component CSS.
- **Risk:** low. **Effort:** M-L. **Depends on:** P11.

---

## 5. Docker & AWS deployment

### Target architecture

```
                       https://postpix.example.com
                                 |
                          CloudFront (CDN, HTTPS)
               /  default  |   /api/*   |   /uploads/*
                v           v            v
     S3 "site" bucket   EC2 instance    S3 "uploads" bucket
     (React build,      docker compose: (user photos,
      private + OAC)     - api (gunicorn+Flask)   private + OAC)
                         - db  (postgres, EBS volume)
                         IAM role -> can PutObject to uploads bucket
```

Why one CloudFront in front of everything: the browser sees one domain, so the session cookie and CSRF cookie are "same-site", no CORS configuration is needed, and HTTPS comes free from CloudFront (with an ACM certificate if you use a custom domain).

Rough monthly cost (verify current AWS pricing): one `t4g.micro` or `t4g.small` (ARM/Graviton) ~ $6-12 on-demand, 20-30 GB gp3 EBS ~ $2-3, public IPv4 address ~ $3.60 (AWS charges for every public IPv4 since 2024), S3 + CloudFront pennies at demo traffic (CloudFront has a monthly free allowance). About **$12-20/month**; less with a Savings Plan, or $0 while stopped except storage/IP.

### P33 - New API-only Dockerfile
- **What:** Multi-stage `Dockerfile`: build stage installs wheels; runtime stage `python:3.12-slim`, non-root user, only `app/`, `migrations/`, `wsgi.py`, `gunicorn.conf.py` copied; `HEALTHCHECK` hitting `/api/health`; `CMD gunicorn -c gunicorn.conf.py wsgi:app`. Add `.dockerignore` (node_modules, react-app, .git, *.db, .env). Remove the Heroku `REACT_APP_BASE_URL`, the `COPY react-app/build` step (the React app no longer ships in this image), and `SQLALCHEMY_ECHO=True`. Build for `linux/arm64` if using Graviton.
- **Why:** Current image is ~1 GB `python:3.9`, runs as root, bakes in the frontend and Heroku settings, and installs psycopg2 separately.
- **Files:** `Dockerfile`, new `.dockerignore`.
- **Risk:** low. **Effort:** S. **Depends on:** P12, P13.

### P34 - docker compose for local dev and production
- **What:** `docker-compose.yml` with `api` and `db` (`postgres:17-alpine`, named volume, healthcheck); `api` waits for `db` healthy, an entrypoint runs `flask db upgrade` on start; seeding is a one-off command (`docker compose run --rm api flask seed all`). `compose.override.yml` for dev (bind-mount code, Flask debug reload); `compose.prod.yml` uses the pushed image, restart policy, log size limits, no Postgres port exposed. Frontend dev still runs with `npm run dev` (Vite proxy to the API).
- **Why:** One command gives you a working local stack identical to production, which is the core Docker skill to learn here.
- **Files:** new `docker-compose.yml`, `compose.override.yml`, `compose.prod.yml`, `docker/entrypoint.sh`.
- **Risk:** low. **Effort:** M. **Depends on:** P33.

### P35 - Terraform: foundation (EC2, network, IAM)
- **What:** `infra/` folder with Terraform: default VPC, a security group allowing port 80 only from the CloudFront managed prefix list (no SSH; use SSM Session Manager), `t4g.small` (or micro) Amazon Linux 2023 instance with a `user_data` script that installs Docker + compose plugin and adds a 1-2 GB swap file, separate EBS volume for Postgres data, Elastic IP, IAM instance profile (SSM core + S3 put on uploads bucket + read from image registry), AWS Budget alarm (e.g. $25). Local state file to start (gitignored); remote state in S3 later.
- **Why:** Reproducible, destroyable infrastructure, and the main Terraform learning piece.
- **Files:** new `infra/main.tf`, `variables.tf`, `outputs.tf`, `ec2.tf`, `iam.tf`, `user_data.sh`, `infra/README` section in docs.
- **Risk:** med (costs money once applied). **Effort:** M. **Depends on:** P33.

### P36 - Terraform: frontend bucket + CloudFront with /api routing
- **What:** Private S3 bucket for the React build, CloudFront distribution with OAC, default behavior -> S3 (SPA fallback: 403/404 -> `/index.html` for client-side routes), `/api/*` behavior -> EC2 origin (caching disabled, forward cookies/headers/query strings, all HTTP methods), optional ACM certificate + Route 53 records for a custom domain.
- **Why:** Cheap, fast global hosting of the React app and the same-origin design described above.
- **Files:** `infra/frontend.tf`, `infra/cloudfront.tf`.
- **Risk:** med. **Effort:** M. **Depends on:** P35.

### P37 - Uploads bucket, no more access keys, own the seed images
- **What:** Private uploads bucket (Block Public Access on, bucket-owner-enforced), served through the same CloudFront under `/uploads/*`. boto3 uses the EC2 instance role automatically, so remove `S3_KEY`/`S3_SECRET` from code and `.env` (local dev uses your AWS CLI profile or a MinIO container). Copy the seed photos (currently hot-linked from a bucket named `capstone-strava-clone-aktiv`, imgur and vecteezy) into this bucket and point seeds at it. Optional lifecycle rule to delete non-seed uploads after N days.
- **Why:** Static keys are what leaked in P1; the seed images depend on buckets/hosts you may not control and can disappear.
- **Files:** `infra/uploads.tf`, `app/s3_helpers.py`, `app/config.py`, `app/seeds/*.py`, `.env.example`.
- **Risk:** low. **Effort:** M. **Depends on:** P7, P36. **Open question:** who owns `capstone-strava-clone-aktiv`?

### P38 - Protect the EC2 origin
- **What:** Besides the CloudFront-only security group (P35), have CloudFront add a secret custom header (`X-Origin-Verify`) that the API (or a tiny Caddy/nginx in front) requires; set `ProxyFix` in Flask so `request.scheme`/client IP come from CloudFront headers. Decide on CloudFront -> EC2 transport: plain HTTP (simplest, traffic between CloudFront and EC2 unencrypted) or HTTPS via Caddy + a subdomain certificate.
- **Why:** Stops people bypassing CloudFront and hitting the server directly.
- **Files:** `infra/cloudfront.tf`, `app/__init__.py`, optional `docker/Caddyfile`.
- **Risk:** low. **Effort:** S. **Depends on:** P36. **Open question:** custom domain + HTTPS to origin?

### P39 - Replace the Heroku workflow with an AWS deploy pipeline
- **What:** Delete `.github/workflows/main.yml` (Heroku). New `deploy.yml` on push to `main` after tests pass: authenticate to AWS with GitHub OIDC (an IAM role trusted for this repo only), build the API image (arm64) and push to ECR or GitHub Container Registry, `aws ssm send-command` to the instance to `docker compose pull && up -d` (migrations run in the entrypoint), build the frontend with Vite, `aws s3 sync --delete` to the site bucket, create a CloudFront invalidation for `/index.html`. Remove the old Heroku secrets from GitHub.
- **Why:** Push-to-deploy with no long-lived AWS keys stored anywhere. The old workflow also wiped and reseeded the database on every deploy.
- **Files:** delete `.github/workflows/main.yml`, new `.github/workflows/deploy.yml`, `infra/github_oidc.tf`.
- **Risk:** med. **Effort:** M. **Depends on:** P34-P37, P44.

### P40 - Backups and basic operations
- **What:** Nightly `pg_dump` (a small cron container or systemd timer) gzipped to a private S3 prefix with a 14-30 day lifecycle; AWS Data Lifecycle Manager snapshots of the EBS volume; Docker log rotation; CloudWatch agent or just `docker compose logs` documented; a restore drill in the runbook.
- **Why:** Postgres in a container on one instance means one disk failure loses everything unless backed up.
- **Files:** `compose.prod.yml`, `docker/backup.sh`, `infra/backups.tf`.
- **Risk:** low. **Effort:** S-M. **Depends on:** P35.

### P41 - Keep the demo account clean
- **What:** Make seeding idempotent (safe to run twice), add `flask seed reset-demo` that restores demo-user posts/follows/likes, and run it nightly (cron on EC2). Optionally block destructive actions for the demo user (delete account, change email).
- **Why:** The demo login is shared with every visitor; someone will delete posts or the account. Must keep "Demo Login" (demo@aa.io) working.
- **Files:** `app/seeds/*.py`, `app/api/user_routes.py`, `compose.prod.yml` or a cron file.
- **Risk:** low. **Effort:** S. **Depends on:** P15. **Open question:** allow demo account deletion?

---

## 6. Testing & CI

There are no tests today (backend or frontend). The only workflow is the Heroku deploy.

### P42 - Backend test suite (pytest)
- **What:** `tests/` with fixtures from the app factory (SQLite in memory or Postgres service in CI), a logged-in client fixture, and tests for: login/logout/signup + demo login, post CRUD + ownership (P3), likes (P6), follows, comments, upload with S3 mocked by `moto`, 404/403 shapes (P5). Start with a skeleton right after P12, then each fix adds its test.
- **Why:** Locks in the security fixes and makes the dependency upgrades safe.
- **Files:** new `tests/conftest.py`, `tests/test_*.py`, `requirements-dev.txt`, `pyproject.toml` (pytest config).
- **Risk:** low. **Effort:** M. **Depends on:** P12.

### P43 - Frontend tests and linting
- **What:** Vitest + React Testing Library for login/demo login, post card like toggle, modal keyboard behavior; ESLint (react, react-hooks, jsx-a11y) + Prettier; `npm run lint`, `npm test`.
- **Why:** Catches broken effects and accessibility regressions automatically.
- **Files:** `react-app/package.json`, `react-app/vitest.config.js` (or inside `vite.config.js`), `react-app/eslint.config.js`, `react-app/src/**/*.test.jsx`.
- **Risk:** low. **Effort:** M. **Depends on:** P16.

### P44 - CI workflow on every pull request
- **What:** `.github/workflows/ci.yml`: Python job (ruff, pytest against a Postgres service container, pip-audit), frontend job (npm ci, lint, test, build), Docker build check. Add Dependabot (`.github/dependabot.yml`) for pip, npm, GitHub Actions and Docker base images.
- **Why:** Green checks on the repo are a visible quality signal; Dependabot keeps it from rotting again.
- **Files:** new `.github/workflows/ci.yml`, `.github/dependabot.yml`.
- **Risk:** low. **Effort:** S. **Depends on:** P42 (and P43 for the frontend job).

### P45 - Secret scanning and pre-commit hooks
- **What:** `pre-commit` with ruff (lint + format), prettier, end-of-file fixes and `gitleaks`; turn on GitHub secret scanning + push protection in repo settings.
- **Why:** Prevents another P1.
- **Files:** new `.pre-commit-config.yaml`, `pyproject.toml` (ruff config).
- **Risk:** low. **Effort:** S. **Depends on:** none.

---

## 7. Docs / README

### P46 - Rewrite the README
- **What:** Present Postpix as Tyler's maintained version: one-line pitch, live demo link + "Demo Login" note, screenshots/GIF, feature list, tech stack badges, architecture diagram (from section 5), quick start (`docker compose up`), project structure, roadmap, and a **Credits** section: "Originally built in 2022 as a team project with Alan De Leon and Theo Fandrich; modernized and maintained by Tyler Torrero since 2026" (wording to approve). Remove dead screenshot links if they break.
- **Why:** The README is the first thing a recruiter reads; today it says "our group project" with outdated setup steps (pipenv, Heroku).
- **Files:** `README.md`, `react-app/README.md` (delete the CRA boilerplate).
- **Risk:** low. **Effort:** S. **Depends on:** none (update again at the end).

### P47 - One documented `.env.example`
- **What:** Single `.env.example` listing every variable with a comment and safe placeholder (`SECRET_KEY`, `DATABASE_URL`, `POSTGRES_*`, `S3_BUCKET`, `AWS_REGION`, `CDN_BASE_URL`, `FLASK_ENV`/`APP_ENV`); remove `REACT_APP_BASE_URL` (not used by the code) and `S3_KEY`/`S3_SECRET` once P37 lands.
- **Why:** Clear setup; no guessing which of two example files is right.
- **Files:** `.env.example` (`.envexample` removed in P2).
- **Risk:** low. **Effort:** S. **Depends on:** P2, P34.

### P48 - Deployment runbook, architecture notes, license
- **What:** `docs/DEPLOY.md`: first-time AWS setup (account, budget alarm, `terraform init/plan/apply`), how deploys work, how to SSH-less shell in with SSM, how to restore a backup, how to tear everything down (`terraform destroy`), cost notes. Add a `LICENSE` (MIT is common) if teammates agree.
- **Why:** You'll forget the steps in 6 months; it also shows DevOps understanding to reviewers.
- **Files:** new `docs/DEPLOY.md`, `LICENSE`.
- **Risk:** low. **Effort:** S. **Depends on:** P35-P40.

---

## Open questions for Tyler

1. **Leaked key (P1):** Whose AWS account was that key in (yours, a teammate's, or App Academy's)? Do you want git history rewritten to remove `.env` (requires force-push; teammates' forks/clones keep the old history anyway, so rotation is the real fix)?
2. **Seed images (P37):** Who owns the `capstone-strava-clone-aktiv` bucket? Is it still online? (Network checks from the audit shell were blocked.) OK to copy those images into your own bucket?
3. **Domain:** Use a custom domain (needs Route 53 or DNS at Cloudflare + ACM certificate) or the default `*.cloudfront.net` URL? Do you want HTTPS between CloudFront and EC2 (P38)?
4. **Region and instance size:** AWS region? `t4g.micro` (cheapest, 1 GB RAM, needs swap) or `t4g.small` (2 GB)? Image registry: ECR (AWS) or GitHub Container Registry (free for public)?
5. **Old data (P15):** Confirm nothing from the old Heroku database needs keeping, so migrations can be reset.
6. **Demo account (P41):** Nightly reset? Block deleting the demo account?
7. **Redux Toolkit (P19):** Worth the large refactor, or keep plain Redux and just clean it up?
8. **Branding (P11/P32):** Any preferred colors/logo, or should a new look be proposed?
9. **Credits/license (P46/P48):** Approve the credit wording; do Alan and Theo agree to an MIT license? Include their GitHub profile links?
10. **Signup on the public demo:** Keep open sign-ups (spam/abuse risk with uploads) or limit to the demo account plus rate limiting (e.g. Flask-Limiter on login/signup/upload)?

## Audit notes

- Read: all of `app/` (factory, config, models, routes, forms, seeds, S3 helper), `migrations/`, `Dockerfile`, `requirements.txt`, `Pipfile`, the GitHub workflow, `.gitignore`s, `react-app/package.json`, `App.js`, `index.js`, store setup, session store, modal, search bar, post grid, and grep scans of all components.
- Not done: did not run the app, `npm install`, or the build (read-only phase; audit used `npm audit --package-lock-only` and `pip-audit -r requirements.txt` in a throwaway venv outside the repo). External image URLs could not be checked (network blocked from the audit shell).
