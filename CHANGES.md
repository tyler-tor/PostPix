# Postpix Change Log (Modernization)

This file explains every change made on the `modernize` branch, item by item, using the
numbering from `MODERNIZATION_PLAN.md` (P1-P48). Each section says what was wrong, what
changed, which files, how to check it yourself, and what to watch out for.

Batch 1 = security and bug fixes (P2-P11) on the **current** stack (Flask 2.0 /
SQLAlchemy 1.4 / Create React App). Batch 2 = safe seeding (P0) and the stack upgrades
(P12-P19); see "Batch 2 items" below.

---

## Tyler action: P1 key rotation (step by step)

A real AWS access key (ID starts with `AKIA`), its secret, and a Flask `SECRET_KEY` were
committed in a `.env` file in early Nov 2022 (deleted a couple of days later). Deleting a
file does **not** remove it from git history, and the GitHub repo is public.

**Whose key is it?** Not Tyler's. The key belongs to the **original teammate's** AWS
account (the project started as a teammate's repo), and Tyler no longer has any old AWS
account. So Tyler cannot deactivate it himself; only the key owner can. Nothing in this
branch can fix it from code either.

1. **Identify the key (privately).** On your own machine run
   `git log --all --diff-filter=A --name-only -- .env` to find the commit, then
   `git show <hash>:.env | grep S3_KEY` to see the access key **ID** (the `AKIA...` part,
   not the secret). Do not paste the secret anywhere; the ID alone is enough for the owner
   to find it.
2. **Notify the original key owner (teammate).** Send a short private message (not a
   public GitHub issue), for example: "The Postpix/Instagram clone repo is public and an old
   `.env` in its git history contains your AWS access key `AKIA...<last 4 chars>` and
   the S3 secret. Please go to AWS console -> IAM -> Users -> Security credentials ->
   Access keys, **deactivate and delete** that key, and check CloudTrail and Billing for
   unexpected use (unknown EC2 instances/regions). AWS Support often waives charges from
   leaked keys." If the key no longer appears in their account, it was already deleted;
   ask them to confirm.
3. **If you cannot reach them, report it.** Options: (a) GitHub: if secret scanning /
   push protection is enabled on the repo (Settings -> Code security), GitHub flags
   `AKIA` keys and also notifies AWS automatically through its secret-scanning partner
   program; enable it on your repo so the leak is reported. (b) AWS: report the exposed
   key through AWS's abuse/security contact (aws.amazon.com/security -> "Report a
   security issue / vulnerability"); AWS can quarantine an exposed key on the owner's
   account. Write down whom you notified and when (useful if asked in an interview).
4. **Brand-new AWS account for Batch 4.** Tyler is creating a new AWS account. The plan
   (P37) uses an EC2 IAM role there, so the app needs **no** access keys at all. Until
   then, if you need uploads locally, create a key for an IAM user that only has
   `s3:PutObject` on your own bucket, keep it in your local `.env` (git-ignored), never commit it.
   Turn on MFA for the new account's root user and set a billing alarm on day one.
5. **New Flask SECRET_KEY.** Generate one with
   `python -c "import secrets; print(secrets.token_hex(32))"` and put it in `.env` /
   the server's environment. The old one is public, so anyone could forge session cookies
   for any deployment that still uses it. Never reuse it.
6. **GitHub repo secrets.** Repo -> Settings -> Secrets and variables -> Actions: delete
   `HEROKU_API_KEY` / `HEROKU_APP_NAME` (Heroku deploy is dead; see P39).

**Why deactivating the key matters more than rewriting history:** the key was public for
years. Bots scrape GitHub for `AKIA...` strings within minutes, and anyone who forked or
cloned the repo still has the old history. Rewriting history cannot "un-leak" it; it only
hides it from people browsing later. A deactivated key is useless no matter who has a copy.
So: get the key deactivated first (required), rewrite history second (optional, cosmetic).

**If you want to rewrite history later (optional, destructive):**
1. Make a full backup: `git clone --mirror <repo-url> postpix-backup.git`.
2. Install git-filter-repo: `brew install git-filter-repo` (or `pip install git-filter-repo`).
3. In a **fresh** clone: `git filter-repo --invert-paths --path .env --path app/dev.db`
   (removes those files from every commit; every commit hash changes).
4. Re-add the remote (filter-repo removes it): `git remote add origin <repo-url>`.
5. Force-push all branches and tags: `git push --force --all && git push --force --tags`.
6. Ask GitHub Support to purge cached views of old commits if needed; other clones must
   re-clone (old clones and forks still contain the key - another reason the owner's
   deactivation is the real fix).
Do this only after the `modernize` branch is merged or rebased, because it rewrites it too.

---

## Deviations from plan

- **P5:** used `Model.query.get_or_404()` (works on the current Flask-SQLAlchemy 2.5) instead of `db.get_or_404()` (Flask-SQLAlchemy 3). Switched to `db.get_or_404()` in P14 (done).
- **P6:** kept the `posts.likes` counter (the plan's alternative option) but made it race-safe and recounted, instead of dropping the column; the new migration sits on top of the existing chain because P15 (migration reset) is Batch 2.
- **P3:** the signup profile-picture upload had to move into the signup request (multipart) because `/api/img/upload` now requires login; not spelled out in the plan.
- **P11:** the plan said "own logo, colors and login layout"; done as a text wordmark + accent colour + demo note + new favicon; the larger layout change is left to P32.
- **P14:** API timestamps were switched to ISO-8601 as the plan says; the frontend got a small `formatDate()` helper (the plan listed "frontend date formatting" without detail). `created_at`/`updated_at` also keep `default=func.now()` until P15 so the app keeps working on the old-migration schema between the two commits.
- **P13:** installed SQLAlchemy 2.1.9 (newest; the plan named 2.0); all checks pass. Also touched the old `Dockerfile` (Python 3.12, `gunicorn wsgi:app` in P12, no separate psycopg2, echo off) and the README install steps so they are not broken before P33/P46.
- **P15:** the plan said "add P6/P21 changes as new migrations" on top of the baseline; as instructed for Batch 2, the P6 unique constraint is folded **into** the baseline instead (no data to migrate). P21 indexes are still a future migration. Also added a constraint naming convention, `NOT NULL` on `follows` columns and `render_as_batch=True` (small, needed for clean future migrations).
- **P17:** removed the unused FontAwesome packages instead of bumping them, and bumped redux/redux-thunk to 5/3 here (needed by react-redux 9) rather than waiting for P19.
- **P19:** done as one commit (the plan suggested one per slice) and as the minimal safe version: each reducer became an RTK slice with the same state shape and thunks; duplicate slices were not merged and RTK Query was not added (see P19 "Things to watch").
- **P16 regression, fixed in P19:** the P16 change `require("redux-logger").default` -> `import logger from "redux-logger"` broke the development build (`npm run dev`) for the P16-P18 commits; production builds were unaffected. History was not rewritten; P19 fixes it.
- **P22:** cursor parameter names differ by list: posts use `before=<created_at>,<id>` as planned (newest first), comments use `after=<created_at>,<id>` (read oldest first) and people lists use `after=<user id>`. `/api/users/<id>` and `/api/auth/` also stopped embedding `Posts` (unbounded).
- **P26:** only the Flask-side half was done (gunicorn config and cache headers). Postgres memory tuning, compose, and the CloudFront cache policy/compression depend on P33, P34 and P36, which are not part of this batch; the matching headers are already in place for them.
- **Batch 3 order:** P25 (dead code) ran before Z1, and P29 (dialogs) before P28 (page layouts), because the layouts use the new dialogs and the store merge is simpler without the dead components.
- **P21:** the posts indexes are plain ascending columns instead of `created_at DESC`, because Alembic's autogenerate check reports false differences for descending indexes on SQLite; the planner reads an ascending index backwards, so the speed is the same.
- **P27/P32:** icons are Feather (`react-icons/fi`, MIT) instead of the previous mix of Ai/Fa/Hi icon sets, so `react-icons` is now used from one family; fonts are self-hosted Bricolage Grotesque and Figtree (OFL) via `@fontsource-variable`, which needs one `npm install`.
- **P28/P30/P31:** there was no real browser, so every screen was checked as markup in jsdom (structure, roles, focus, request counts); spacing, breakpoints and animation were written from the design and not seen. The accessibility audit is my own script, not axe.

---

## Open questions for Tyler

1. **Home feed (P10):** should your own posts appear in your home feed? **Answered in Batch 3: yes, done in Z4.**
2. **Branding (P11):** OK with the teal "postpix" wordmark and accent, or do you have preferred colours/logo for P32?
3. **Repo name:** rename the GitHub repo from `Instagram-Group-Project` to something like `postpix` (GitHub redirects old URLs)? Avoids the trademark name in your portfolio URL.
4. **Deep links (found during P11):** refreshing `/explore` on the Flask-served build returns 404 (pre-existing). Fix in P31/P33, or earlier as a small separate change? **Answered in Batch 2: fixed in P18.**
5. **Look and feel (Batch 3):** please open the app at 375, 768 and 1200 px and tell me what to change. The palette (teal `#0F766E` on cool grey, Bricolage Grotesque headings) is easy to adjust in `src/styles/tokens.css`.
6. **Share preview image:** `index.html` has Open Graph tags but no `og:image`. Do you want a 1200x630 card made for link previews (needs a hosted absolute URL)?
7. **Credits:** the home page rail lists Derek Torrero, Theo Fandrich and Alan Deleon with GitHub/LinkedIn links, kept from the old version. Keep, edit or remove?

---

# Batch 1 items

## P2 — Repo hygiene: stop tracking files that should never be in git
- **Problem:** `app/dev.db` (a SQLite database with seed users and password hashes), 30+
  compiled Python files (`__pycache__/*.pyc`) and two copies of the env example
  (`.env.example` and `.envexample`) were committed. The root `.gitignore` was the default
  React one, so it did not ignore Python bytecode, virtualenvs, build output or
  Terraform state. Committed DB/bytecode files cause noisy diffs and merge conflicts, can
  leak data, and look unmaintained to reviewers.
- **What changed:** Stopped tracking `app/dev.db`, every `__pycache__/*.pyc` file and the
  duplicate `.envexample` with `git rm --cached` (the files stay on your disk, git just
  forgets them). Rewrote the root `.gitignore` with sections for secrets (`.env`, `.env.*`
  but **not** `.env.example`), Python (`__pycache__/`, `*.pyc`, `.venv/`, `instance/`),
  databases (`*.db`, `*.sqlite*`), Node (`node_modules/`, `react-app/build/`) and
  Terraform (`.terraform/`, `*.tfstate*`, `*.tfvars`). `.env.example` is now the single,
  commented template with placeholder values only. Git history was **not** rewritten.
- **Files:** `.gitignore`, `.env.example`, removed from index: `.envexample`, `app/dev.db`,
  `app/**/__pycache__/*.pyc`, `migrations/versions/__pycache__/*.pyc`.
- **How to verify:** `git ls-files | grep -E 'pyc|\.db$|envexample'` prints nothing.
  `git check-ignore -v app/dev.db .env app/__pycache__/x.pyc` shows the matching rules.
  `git check-ignore .env.example` prints nothing (it is still tracked on purpose).
- **Things to watch / follow-ups:** The local copies of `app/dev.db`, `.envexample` and the
  `.pyc` files still exist on your Mac (deleting needs your permission); you can delete
  `.envexample` and the `__pycache__` folders yourself any time. When this branch is merged,
  `git pull` on other clones will **delete** their `app/dev.db` - recreate it with
  `flask db upgrade && flask seed all`. The old `.env` is still in history (see P1 above).
  P47 will finish documenting `.env.example`; the react-app has its own `.gitignore` which
  is unchanged.

## P3 — Close authorization holes
- **Problem:** (a) `PUT /api/posts/<id>` never checked who owned the post, so any logged-in
  user could rewrite anyone's caption just by changing the ID (an "IDOR" bug). (b)
  `POST /api/posts/` had `@login_required` commented out (logged-out requests crashed with
  a 500), and it returned "the newest post in the whole table", which could be someone
  else's post if two people posted at the same time. (c) `POST /api/img/upload` had no
  login check, so anyone on the internet could upload files into the S3 bucket (cost and
  abuse risk). (d) Delete post / edit+delete comment / delete account returned `200 OK`
  with an error message for non-owners, and crashed (500) for missing IDs.
- **What changed:** Edit caption now returns 404 if the post does not exist and 403 if you
  are not the author. Create post requires login and returns the post object that was just
  inserted. The upload endpoint requires login. Delete post, edit/delete comment and
  delete account return 404 (missing) or 403 (not yours) with `{"errors": [...]}`.
  Because uploads now need a logged-in user, the **signup profile picture** could no
  longer be uploaded before the account existed, so signup now sends a multipart form
  (fields + optional `image` file) in one request; the server validates the form first,
  then uploads the image, then creates the user. The client can no longer set an
  arbitrary `profile_picture` URL at signup.
- **Files:** `app/api/post_routes.py`, `app/api/img_routes.py`, `app/api/comment_routes.py`,
  `app/api/user_routes.py`, `app/api/auth_routes.py`, `app/forms/signup_form.py`,
  `react-app/src/store/session.js`, `react-app/src/components/LoginPage/SignUpForm.js`,
  `react-app/src/components/LoginPage/ProPicImageUpload.js`.
- **How to verify:** Log in as demo (`demo@aa.io` / `password`), then
  `PUT /api/posts/2` with `{"caption":"x"}` -> **403** (post 2 belongs to marnie).
  `PUT /api/posts/<your post>` -> 200. `PUT /api/posts/99999` -> 404.
  Logged out: `POST /api/img/upload` and `POST /api/posts/` -> redirected to
  `/api/auth/unauthorized` (401). Create a post -> response `userId` is yours. In the UI:
  sign up with and without a picture (picture needs S3 configured).
  Verified with a Flask test-client script (13/13 checks).
- **Things to watch / follow-ups:** With S3 not configured, signing up **with** a picture
  returns a 400 "upload failed" error (signup without a picture works). Logged-out API
  calls get a 302 redirect to the 401 endpoint (Flask-Login default); P5 makes them a
  direct JSON 401. P42 should turn these checks into pytest tests.

## P4 — Turn CSRF protection on properly
- **Problem:** `CSRFProtect` was imported but never switched on. Only routes that used a
  WTForm checked a token, and they did it by copying the `csrf_token` **cookie** into the
  form on the server (`form['csrf_token'].data = request.cookies['csrf_token']`). That
  defeats the point: a malicious site that makes your browser send a request also makes it
  send the cookie, so the "check" always passes. Routes without a form (like/unlike,
  follow/unfollow, delete post, delete account) had no check at all, so another site could
  trigger them for a logged-in visitor (CSRF). A request with no cookie crashed with a 500
  (`KeyError`). Logout was a `GET`, so any `<img src="/api/auth/logout">` logged you out.
- **What changed:** `CSRFProtect(app)` now checks every POST/PUT/PATCH/DELETE. The
  `csrf_token` cookie is now readable by JavaScript (`httponly=False`; the token is not a
  secret by itself), and a new `react-app/src/utils/apiFetch.js` wrapper copies it into
  an `X-CSRFToken` header on every non-GET request. All `fetch(` calls in the stores and
  components now use `apiFetch(`. The cookie-copy lines were removed. A failed check now
  returns `400 {"errors": ["CSRF check failed: ..."]}` (JSON) instead of an HTML page or
  a 500. Logout is now `POST /api/auth/logout`.
- **Files:** `app/__init__.py`, `app/api/auth_routes.py`, `app/api/post_routes.py`,
  `app/api/comment_routes.py`, new `react-app/src/utils/apiFetch.js`, all
  `react-app/src/store/*.js` that call the API, `components/User.js`,
  `components/UsersList.js`, `components/NavBar/ImageUploadComponent/ImageUploadComponent.js`,
  and the unused `Temp*` dev components.
- **How to verify:** `curl -i -X POST localhost:5000/api/auth/login -H 'Content-Type: application/json' -d '{"email":"demo@aa.io","password":"password"}'`
  -> **400** CSRF error (no token). In the browser, the login form still works; DevTools ->
  Network shows an `X-CSRFToken` request header on POST/PUT/DELETE. Liking a post without
  the header -> 400. Test-client script: 9/9 checks (login with/without/bad token, like
  without token, create post with token, logout via POST).
- **Things to watch / follow-ups:** Any new frontend call must use `apiFetch`, not raw
  `fetch`, or writes will fail with 400. The token expires after 1 hour by default but the
  cookie is refreshed on every response, so normal use is fine; a tab left open overnight
  needs one page load. `curl` testing now needs the cookie and header: first
  `curl -c jar localhost:5000/api/auth/`, then send `-b jar -H "X-CSRFToken: <cookie value>"`.
  SameSite is still `Strict` in production / unset in dev; P9 changes it to `Lax`.

## P5 — Consistent error handling and 404s
- **Problem:** Many ordinary mistakes produced `500 Internal Server Error`:
  `GET /api/posts/<missing id>` called `.to_dict()` on `None`; `GET /api/users/<missing>`
  and `/followers` did the same; `/following`, `/notfollowing`, `/follow`, `/likes` and
  unfollow/unlike simply **returned nothing** when the user/post was missing or you were
  not following (Flask turns a `None` return into a 500); commenting on a missing post
  crashed. "Already following" returned `200` with an `error` key, which made the
  frontend crash (`data.followingUser` was undefined). Validation errors used `401`
  (which means "not logged in"). Logged-out API calls were **redirected** (302) instead of
  getting a 401. Unknown `/api/...` URLs returned the React HTML page. Two comment
  fetches used a relative path (`api/comments/...`), which breaks on nested pages like
  `/users/3` (the browser requests `/users/api/comments/...`).
- **What changed:** New `app/errors.py` registers JSON error handlers so every API error
  is `{"errors": ["message"]}` with the right status (400/401/403/404/405/409/413/500);
  unexpected exceptions are logged server-side and return a generic 500 (no traceback
  leaks). Flask-Login's unauthorized handler returns a JSON 401. Unknown `/api/*` paths
  return a JSON 404. Every route now always returns a response: 404 for missing
  posts/users, 409 for "already following" / "not following", 404 for unliking a post you
  did not like. Form validation errors return **400**. Comment fetch paths now start
  with `/`. (The `delete_user` `TypeError` was already fixed by the owner check in P3.)
- **Files:** new `app/errors.py`, `app/__init__.py`, `app/api/post_routes.py`,
  `app/api/user_routes.py`, `app/api/comment_routes.py`, `app/api/auth_routes.py`,
  `react-app/src/store/comments.js`.
- **How to verify:** Logged in as demo: `GET /api/posts/99999` -> 404
  `{"errors":["Post not found"]}`; `GET /api/users/99999/following` -> 404;
  `POST /api/users/2/follow` (already followed) -> 409; `GET /api/nope` -> 404 JSON;
  `PUT /api/posts/1` with an empty caption -> 400. Logged out: `GET /api/posts/` -> 401
  `{"errors":["Unauthorized"]}`. Test-client script: 20/20 checks, plus P3/P4 re-run.
- **Things to watch / follow-ups:** Used `Model.query.get_or_404()` (Flask-SQLAlchemy 2.x)
  instead of the plan's `db.get_or_404()` (Flask-SQLAlchemy 3, Batch 2); swap during P14.
  The frontend still mostly ignores error bodies (no toast/message); P31 adds proper
  error states. In debug/testing mode unexpected exceptions are re-raised so you still
  see the traceback locally.

## P6 — Make likes correct
- **Problem:** Nothing stopped a user liking the same post many times: `like_post` never
  checked for an existing like and the `post_likes` table had no unique constraint, so
  double-clicking (or a script) inflated counts. The count lived in a separate
  `posts.likes` column updated in Python (`post.likes += 1`), so two simultaneous likes
  could overwrite each other. `unlike_post` built its response **before** decrementing, so
  it returned the old count. Seed data hard-coded fake counts: `posts.likes` summed to
  130 while only 17 real `post_likes` rows existed.
- **What changed:** New Alembic migration `a1f3c9d2e7b4` deletes duplicate like rows
  (keeps the oldest), adds a unique constraint `uq_post_likes_user_post` on
  `(user_id, post_id)`, and recounts every `posts.likes` from the real rows. The model
  declares the same constraint. `like_post` returns **409** if you already liked the
  post, increments the counter in SQL (`likes = likes + 1`, race-safe), and also turns a
  racing duplicate (`IntegrityError`) into a 409. `unlike_post` deletes your like,
  decrements in SQL (never below 0) and returns the **new** count; unliking a post you
  have not liked is a 404. Seeds no longer hard-code `likes=`; `seed_post_likes()` ends
  with `recount_post_likes()` so counts always match rows.
- **Files:** `app/models/postLike.py`, `app/api/post_routes.py`, `app/seeds/posts.py`,
  `app/seeds/postLikes.py`, new `migrations/versions/a1f3c9d2e7b4_unique_post_likes.py`.
- **How to verify:** `flask db upgrade && flask seed undo && flask seed all`. Logged in
  as demo: `POST /api/posts/5/likes` -> `{"likes": 1}`; again -> 409; `DELETE` ->
  `{"likes": 0}`; again -> 404. In SQL:
  `SELECT id FROM posts p WHERE likes != (SELECT COUNT(*) FROM post_likes WHERE post_id=p.id);`
  returns no rows. Also tested the migration on a DB with injected duplicate likes and a
  wrong counter (downgrade -> insert duplicates -> upgrade): duplicates removed, counts fixed.
  Test-client script: 8/8.
- **Things to watch / follow-ups:** The demo feed will show **much lower** like numbers
  than before (17 total instead of 130) because the old numbers were fake. The plan's
  other option (drop `posts.likes` and count with a grouped query) was not done in Batch
  1; the counter is kept but now always matches. The migration was added on top of the
  existing chain; P15 (reset migrations) should fold the constraint into the new initial
  migration. The `flask seed all` production branch still uses raw SQL strings (fixed in P14).

## P7 — Harden image uploads
- **Problem:** No size limit (one huge upload could eat server memory and S3 money). Only
  the file **name** was checked, so `evil.html` renamed to `evil.jpg` was accepted, and
  the S3 `Content-Type` came from the browser's claim (could be `text/html`, which turns
  a bucket into a phishing/XSS host). PDFs were allowed for no reason. A typo built names
  like `abc123,jpg` (comma instead of dot). URLs were `http://`, and every upload sent
  `ACL='public-read'`, which **fails** on S3 buckets created since April 2023 (ACLs are
  disabled by default), so uploads would break on any new bucket.
- **What changed:** `MAX_CONTENT_LENGTH = 10 MB` (bigger requests get a JSON **413**).
  Allowed types are jpg/jpeg/png/webp/gif. Each file is opened with **Pillow** and
  `verify()`'d; the real detected format decides the extension and `ContentType`
  (a PNG named `.jpg` is stored as `.png`). Very large pixel counts (decompression bombs)
  are refused. Keys are `uploads/<random-uuid>.<ext>`. The ACL argument was removed;
  URLs are `https://`, using `S3_PUBLIC_URL_BASE` if set (for CloudFront later) or
  `https://<bucket>.s3.amazonaws.com/`. All the logic lives in one helper,
  `process_and_upload_image()`, used by both `/api/img/upload` and signup. S3 errors are
  logged on the server and the client only sees "upload failed" (502). The file pickers
  only offer the four allowed types.
- **Files:** `app/s3_helpers.py`, `app/api/img_routes.py`, `app/api/auth_routes.py`,
  `app/config.py`, `requirements.txt` (adds `Pillow==10.4.0`),
  `react-app/src/components/NavBar/ImageUploadComponent/ImageUploadComponent.js`,
  `react-app/src/components/LoginPage/ProPicImageUpload.js`.
- **How to verify:** Logged in, upload a real PNG -> 200 with
  `https://.../uploads/<uuid>.png`. Upload a text/HTML file renamed `.jpg` -> 400
  "file is not a valid image". Upload an 11 MB file -> 413. Upload a PDF -> 400.
  Tested with the S3 call mocked (no real bucket): 7/7 checks, including signup with a
  picture.
- **Things to watch / follow-ups:** **Not tested against real S3** (no bucket/keys in this
  environment). Without the ACL, a new bucket needs a bucket policy allowing public
  `s3:GetObject` on `uploads/*` **or** (better, P37) CloudFront with OAC; otherwise
  uploads succeed but images show as broken (403). Run `pip install -r requirements.txt`
  to get Pillow. `Pipfile`/`Pipfile.lock` were not updated (they are replaced in P13).
  Resizing/WebP conversion is P24.

## P8 — Stop exposing private user data
- **Problem:** `User.to_dict()` included `email`, and almost every user endpoint used it.
  So any logged-in user, including anyone using the shared **demo** login, could call
  `GET /api/users/` and download every user's email address (also leaked through profile,
  "not following" suggestions and follow responses). That is a privacy leak and a spam
  list.
- **What changed:** `User` now has `to_public()` (id, username, names, picture,
  followers/following, liked post IDs, timestamps; **no email**) and `to_self()`
  (`to_public()` + email). `to_dict` is now an alias of `to_public`, so every existing
  call became safe without touching each route. Only the "this is me" endpoints use
  `to_self()`: `GET /api/auth/`, `POST /api/auth/login`, `POST /api/auth/signup`. The
  unused dev component `User.js` no longer displays an email.
- **Files:** `app/models/user.py`, `app/api/auth_routes.py`,
  `react-app/src/components/User.js`.
- **How to verify:** Log in as demo, open `/api/users/` in the browser -> no `email`
  keys, no `@aa.io` anywhere. `/api/auth/` -> your own email is present. Test-client
  script checks 7 endpoints for emails: 10/10.
- **Things to watch / follow-ups:** If you add a new user endpoint, use `to_public()`
  unless it is about the current user. The frontend never read other users' emails, so no
  UI change. P20 will make user payloads much smaller (no full follower lists).

## P9 — Config and input hardening
- **Problem:** `SECRET_KEY` could silently be `None` (Flask then can't sign sessions safely
  / crashes later in odd places). `SQLALCHEMY_ECHO = True` logged **every SQL query** in
  production (slow, and leaks data into logs). `DATABASE_URL` missing crashed with an
  unclear `AttributeError`. Cookies had no explicit `Secure`/`SameSite` settings.
  `CORS(app)` allowed any website to read API responses that don't need credentials,
  although nothing needs cross-origin access. Three files had `from crypt import methods`
  (an accidental editor auto-import) which **crashes on Python 3.13+** (the `crypt`
  module was removed). Forms had no length limits, so a 1,000-character caption reached
  the database and errored (500 on Postgres); passwords could be 1 character; inputs were
  not trimmed. A Heroku-only `https_redirect` hook was dead code.
- **What changed:** `app/config.py` now: raises a clear error at startup if `SECRET_KEY`
  or `DATABASE_URL` is missing **in production** (dev falls back to a random key and
  `sqlite:///dev.db`); `SQLALCHEMY_ECHO` comes from the env and defaults to **off**;
  session and remember-me cookies are `HttpOnly`, `SameSite=Lax`, and `Secure` in
  production; the CSRF cookie is `SameSite=Lax` (was `Strict`/unset) and `Secure` in
  production. Removed `flask-cors` (code and `requirements.txt`), the `crypt` imports and
  the Heroku redirect hook. Forms: `Length(max=...)` matching DB columns (caption 150,
  comment 255, username 40, email/names/img_url 255), signup password is a
  `PasswordField` with 8-128 chars, real `Email()` check, and text fields are trimmed
  (new `app/forms/filters.py`), so a caption of only spaces is rejected.
- **Files:** `app/config.py`, `app/__init__.py`, `app/api/post_routes.py`,
  `app/api/user_routes.py`, `app/api/comment_routes.py`, `app/forms/*.py` (new
  `filters.py`), `requirements.txt`.
- **How to verify:** `FLASK_ENV=production SECRET_KEY= python -c "import app"` -> fails
  with "SECRET_KEY is not set". Logged in: post with a 151-char caption -> 400; caption
  `"   hi   "` is saved as `"hi"`; signup with password `abc` -> 400 with a password
  error. Response headers contain no `Access-Control-Allow-Origin`; the `csrf_token`
  Set-Cookie has `SameSite=Lax`. Test-client script: 14/14, and P3-P8 scripts re-run green.
- **Things to watch / follow-ups:** **Production needs `SECRET_KEY` and `DATABASE_URL`
  set** or it will refuse to start (on purpose). With `Secure` cookies, production must be
  served over HTTPS (CloudFront in P36) or login won't stick. The old `Dockerfile` still
  sets `ENV SQLALCHEMY_ECHO=True`, which now really turns echo on in that image; it is
  replaced in P33 (set it to `false` if you build it before then). `Pipfile` still lists
  Flask-Cors (P13 replaces it). Existing demo users with the 8-char password `password`
  still log in (the min length applies to new signups only). If you ever run the React dev
  server against a different origin without the CRA proxy, you'd need CORS back for that origin only.

## P10 — Fix the home feed (bug + speed)
- **Problem:** `GET /api/me/following/posts` looped over everyone you follow and ran one
  query **per followed user**, appending results in follow order. So the feed showed all
  of user A's posts, then all of user B's, instead of newest-first, and the frontend
  didn't re-sort. It was also slow: `to_dict()` on the current user loaded followers,
  following and likes just to get the followed IDs, then 1 query per followed user (an
  "N+1" pattern). For the demo user this was 14 SQL queries per feed load.
- **What changed:** One query: posts whose `user_id` is in
  `(SELECT followed_id FROM follows WHERE follower_id = me)`, ordered by
  `created_at DESC, id DESC` (id breaks ties, e.g. seed posts created in the same
  second). Authors are loaded with `selectinload` (one extra batched query, not one per
  post). The response shape (`{"Posts": [...]}` with a `users` object per post) is
  unchanged, so the frontend needs no change. Your own posts are still **not** included
  (same as before).
- **Files:** `app/api/me_routes.py`.
- **How to verify:** Log in as demo, open `/api/me/following/posts`: posts from different
  users are mixed and `createdAt` goes from newest to oldest. With
  `SQLALCHEMY_ECHO=true` you see ~3 queries instead of ~14. Test-client script: 4/4
  (same post set as before, only followed users, sorted, 14 -> 3 queries measured).
- **Things to watch / follow-ups:** Uses SQLAlchemy 1.4 `Model.query` style; P14 converts
  it to `select()` style. Pagination/infinite scroll is P22; indexes on
  `follows(follower_id)` and `posts(user_id, created_at)` are P21. Whether to include your
  own posts in the home feed is an open question below.

## P11 — Distinct branding to avoid phishing flags
- **Problem:** The site was flagged as phishing in Feb 2023 (several "fix phishing" commits
  only changed the page title). The login page copied Instagram's look: a centered white
  card with a script-style wordmark image positioned with Instagram's sprite offsets
  (`background-position: 0px -554px`, with the original Instagram sprite URL still in a
  comment), Instagram's button blue `rgb(0,149,246)`, Instagram's exact sign-up copy
  ("Sign up to see photos and videos from your friends", "By signing up, you agree to our
  Terms, Privacy Policy and Cookies Policy"), a phone screenshot image used by
  Instagram's login page, an unused `Instagram_logo.png`, a favicon in Instagram's
  pink/orange gradient colours, `alt="instagram"` / `alt="Instagram Post"`, and a
  "Finstagram" credit. A login form that looks like Instagram's on an unrelated domain
  is exactly what Google Safe Browsing flags, and it is a trademark problem.
- **What changed:** New original **Postpix** identity: a text wordmark component
  (`components/Brand/Wordmark.js`: a teal rounded "P" mark + lowercase "post**pix**", no
  image, no third-party font) used in the nav bar, login card and sign-up modal. One teal
  brand accent (`--pp-accent: #0f766e`, darker `#115e59`) defined as CSS variables in
  `index.css` and used everywhere the Instagram blue was. Font stack changed from
  `'proxima nova'` to a neutral stack (`--pp-font`). Login card gets a teal top border
  and rounded corners, a tagline ("Share photos with friends.") and a visible
  **portfolio-demo note** ("not affiliated with any other social network; don't reuse a
  real password"). Sign-up copy rewritten in our own words with the same demo note. New
  original favicon (teal square with a white "P", generated, multi-size `.ico`). Page
  `<title>` is "Postpix" with a matching meta description and theme colour. Deleted
  `Carousel.js`, `screenshot1-2x.png`, `Instagram_logo.png` and both old wordmark
  images; post image alt text now uses the caption. Removed the "Finstagram" comment.
- **Files:** `react-app/public/index.html`, `react-app/public/favicon.ico`,
  `react-app/src/index.css`, new `react-app/src/components/Brand/Wordmark.js` and
  `Brand.css`, `components/LoginPage/{index.js,LoginForm.js,SignUpForm.js,LoginPage.css,ProPicImageUpload.js}`,
  `components/NavBar/index.js`, `components/HomeFeed/SideStuff.js`,
  `components/reUsedComponents/SinglePostModal.{js,css}`,
  `components/UserProfile/UserProfile.css`,
  `components/NavBar/ImageUploadComponent/ImageUploadComponent.css`; deleted
  `components/LoginPage/Carousel.js` and four images in `src/images/`.
- **How to verify:** `cd react-app && npm install && npm run build` (on Node 17+ prefix
  with `NODE_OPTIONS=--openssl-legacy-provider`, needed by react-scripts 4). Built
  successfully in a scratch copy (only pre-existing lint warnings). `grep -ri instagram
  react-app/build` finds nothing; served by Flask, `/` shows `<title>Postpix</title>` and
  `/favicon.ico` is 200. Then visually: open the login page -> teal "postpix" wordmark,
  teal buttons, demo note; nav bar shows the wordmark; Demo Login still works (also
  verified over real HTTP with curl: CSRF-protected login, feed and like all 200).
- **Things to watch / follow-ups:** I could not look at the page in a browser here, so
  **please eyeball the login page, sign-up modal and nav bar** (wordmark size/spacing).
  The layout is still a centered card (common to many sites); the full visual refresh is
  P32. The repo name `Instagram-Group-Project` and the README title "Instagram Clone"
  remain (README rewrite is P46; repo rename is an open question). Found but **not fixed**
  (out of scope): refreshing a deep link like `/explore` on the Flask-served build returns
  404, because Flask's static route catches it before the React catch-all; this was
  already broken on `main` (fits P31/P33).

---

# Batch 2 items (modern stack)

Batch 2 = P0 (new: safe seeding) and the stack upgrades P12-P19 (app factory, Python
3.12, current Flask/SQLAlchemy, clean migrations, Vite, React 19, react-router 7, Redux
Toolkit).

## P0 — Safe seeding (new item, not in the original plan)
- **Problem:** `.github/workflows/main.yml` (the old Heroku deploy) ran `flask seed undo`
  and then `flask seed all` on **every push to `main`**, which wiped every real user,
  post, comment and like and replaced them with demo data. On top of that, `flask seed all`
  itself ran `TRUNCATE ... RESTART IDENTITY CASCADE` on every table when
  `FLASK_ENV=production`. Any deploy = total data loss. The seed files also hard-coded
  database ids (`user_id=4`, `post_id=12`), which only work if ids start at 1.
- **What changed:**
  - Deleted the obsolete Heroku workflow `.github/workflows/main.yml` (Heroku is gone;
    Batch 4 / P39 adds the AWS pipeline).
  - `flask seed all` now **only seeds an empty database** (no users). If there is any
    user it prints `Database already has data. Skipping seed.` and exits successfully.
  - New `flask seed all --reset`: deletes all data child-to-parent (likes, comments,
    follows, posts, users) and then seeds. **Refuses in production** with a
    `click.ClickException` (exit code 1).
  - `flask seed undo` deletes all data the same way and also **refuses in production**.
  - Removed the `TRUNCATE` blocks and the per-file `undo_*` functions (one central
    `_delete_all()` with SQLAlchemy `delete()` statements, no raw SQL strings).
  - Removed hard-coded ids: `seed_users()` returns `{seed number: User}` and
    `seed_posts(users)` returns `{seed number: Post}`; comments/likes use
    `users[4].id` / `posts[12].id`. The seed numbers are the `#1`..`#15` comments next
    to each user and `post1`..`post50`. Same demo data as before, but it works whatever
    ids the database hands out. Removed a leftover `likes = 1` on post 15 (the counter is
    recounted from real likes anyway).
- **Deploy rules (read this before any deploy):**
  1. A deploy runs `flask db upgrade && flask seed all`. This is safe every time: on an
     empty database it creates the demo data, on a database with data it does nothing.
  2. `flask seed all --reset` and `flask seed undo` are **local only** (they refuse when
     `FLASK_ENV=production`).
  3. **Never run `docker compose down -v`** against production: `-v` deletes the Postgres
     volume, i.e. the whole database. Plain `docker compose down` is fine.
  4. **Back up the database before every production migration** (`pg_dump`, see P40).
- **Tyler action:** on GitHub, repo -> Settings -> Secrets and variables -> Actions,
  **delete the `HEROKU_API_KEY` and `HEROKU_APP_NAME` secrets**. Nothing uses them now.
- **Files:** deleted `.github/workflows/main.yml`; `app/seeds/__init__.py`,
  `app/seeds/users.py`, `app/seeds/posts.py`, `app/seeds/comments.py`,
  `app/seeds/postLikes.py`.
- **How to verify:** on a fresh SQLite DB: `flask db upgrade && flask seed all` ->
  "Seeded demo data." (15 users, 50 posts, 80 comments, 17 likes, 61 follows); run
  `flask seed all` again -> "Database already has data. Skipping seed."; `flask seed all
  --reset` -> deletes and reseeds; `FLASK_ENV=production flask seed all --reset` and
  `FLASK_ENV=production flask seed undo` -> `Error: ... disabled in production`, exit
  code 1. A test script inserted a user with id 100 first and seeded: demo got id 101 and
  every post/comment/like still pointed to the right user and post (4/4). All Batch 1
  test-client scripts re-run green (85/85).
- **Things to watch:** to refresh the demo data locally use `flask seed all --reset`
  (the old `flask seed undo && flask seed all` still works locally). Because ids are no
  longer reset, on Postgres a reset gives new, higher ids; any bookmarked URL like
  `/posts/5` may point elsewhere afterwards (local only). `app/seeds/follows.py` (dead,
  commented model) is removed in P15.

## P12 — Refactor to an app factory with config classes
- **Problem:** `app/__init__.py` built one global `app` at import time and `app/config.py`
  read `SECRET_KEY` / `DATABASE_URL` while being imported, so simply importing the package
  could crash, tests could not create a fresh app with different settings, and there was
  only one `Config` class for every environment.
- **What changed:** `app/__init__.py` now has `create_app(config_name=None)`, which builds
  a new app, attaches the extensions (`db`, `Migrate`, `LoginManager`, `CSRFProtect`,
  created once at module level and `init_app`-ed), registers the blueprints, the
  `flask seed` commands, the JSON error handlers, the CSRF cookie hook and the React
  catch-all. `app/config.py` has `Config` (shared settings), `DevConfig` (SQLite
  `dev.db` and a random key if none is set), `TestConfig` (in-memory SQLite or
  `TEST_DATABASE_URL`, CSRF off, `TESTING=True`) and `ProdConfig` (secure cookies, refuses
  to start without `SECRET_KEY` or `DATABASE_URL`). Environment variables are read when
  the app is created, not when the module is imported. The class is picked by the
  argument or by `FLASK_ENV` (`development` default, `testing`, `production`). New
  `wsgi.py` (`app = create_app()`) for gunicorn; new `GET /api/health` -> `{"status":"ok"}`
  (no login, no DB) for Docker/CloudFront health checks. The seed commands read
  `IS_PRODUCTION` from the app config.
- **Files:** `app/__init__.py`, `app/config.py`, new `wsgi.py`, `app/seeds/__init__.py`,
  `Dockerfile` (CMD `gunicorn app:app` -> `gunicorn wsgi:app`, otherwise untouched until
  P33).
- **How to verify:** `flask routes` / `flask db upgrade` / `flask seed all` still work
  with `FLASK_APP=app` (Flask finds `create_app` automatically).
  `curl localhost:5000/api/health` -> `{"status":"ok"}`. `python -c "import app"` with no
  env vars works; `FLASK_ENV=production SECRET_KEY= python -c "from app import
  create_app; create_app()"` -> "SECRET_KEY is not set". Ran `gunicorn wsgi:app` and
  curled `/api/health` (200) and `/api/posts/` (401 logged out). Test-client scripts:
  new P12 script 8/8 (health, testing config, import without env, prod fail-fast, wsgi),
  plus all earlier scripts green.
- **Things to watch:** anything that did `from app import app` must now call
  `create_app()` (only the old Dockerfile did). `migrations/env.py` did not need changes
  for the factory (it uses `current_app`); it is cleaned up in P15.

## P13 — Upgrade Python to 3.12 and backend packages to current
- **Problem:** The backend ran on Python 3.9 (end of life Oct 2025) with 2021-era
  packages (Flask 2.0, SQLAlchemy 1.4, Werkzeug 2.0, gunicorn 20...). `pip-audit` on
  `requirements.txt` reported **138 known vulnerabilities in 10 packages** at the start of
  Batch 2 (the plan's audit said 81; new advisories were published since). There were two
  dependency files that disagreed (`Pipfile` and `requirements.txt`; the old CI
  regenerated one from the other) and unused pins (`GeoAlchemy2`, `python-editor`, ...).
- **What changed:**
  - One tool: `requirements.in` lists only the **direct** dependencies; `requirements.txt`
    is the fully pinned file generated from it with
    `uv pip compile requirements.in -o requirements.txt --python-version 3.12`
    (`pip-compile` works too). `requirements-dev.in` -> `requirements-dev.txt` adds
    pytest, ruff, moto[s3] and pip-audit, constrained to the same versions. Deleted
    `Pipfile` and `Pipfile.lock`. Added `.python-version` (`3.12`).
  - New versions: Flask 3.1.3, Werkzeug 3.1.9, Flask-SQLAlchemy 3.1.1, SQLAlchemy
    2.1.9, Flask-Migrate 4.1.0 / Alembic 1.20.1, Flask-Login 0.6.3, Flask-WTF 1.3.0,
    WTForms 3.3.2, email-validator 2.4.0, boto3 1.44.10, Pillow 13.0.0, gunicorn
    27.0.1, python-dotenv 1.2.4, and **psycopg 3** (`psycopg[binary]` 3.3.9) instead of
    the unpinned `psycopg2` the Dockerfile installed. Dropped GeoAlchemy2, python-editor,
    greenlet, six, packaging and other unused or transitive pins.
  - `app/config.py`: Postgres URLs (`postgres://` or `postgresql://`) are rewritten to
    `postgresql+psycopg://` so SQLAlchemy uses psycopg 3.
  - `migrations/env.py`: `db.get_engine()` (deprecated in Flask-SQLAlchemy 3, removed in
    3.2) -> `db.engine`; the URL is rendered with the password so Alembic can connect.
  - `Dockerfile` (still the old Heroku-style one until P33): `python:3.12-slim`, no
    separate `pip install psycopg2`, and `SQLALCHEMY_ECHO=false` (the P9 note flagged
    `True`).
  - `.env.example`: documents `FLASK_DEBUG=1` and the instance-folder SQLite path.
    `README.md`: install steps use a venv + `pip install -r requirements.txt` instead of
    pipenv (full README rewrite is P46).
- **Files:** new `requirements.in`, `requirements-dev.in`, `requirements-dev.txt`,
  `.python-version`; `requirements.txt`, `app/config.py`, `migrations/env.py`,
  `Dockerfile`, `.env.example`, `README.md`; deleted `Pipfile`, `Pipfile.lock`.
- **How to verify:** `python3.12 -m venv .venv && source .venv/bin/activate && pip install
  -r requirements.txt -r requirements-dev.txt`, then `flask db upgrade && flask seed all
  && flask run`. `pip-audit -r requirements.txt` -> **No known vulnerabilities found**
  (also for `requirements-dev.txt`). All test-client scripts pass on Python 3.12 with the
  new packages (P0, P3-P10, P12: 97/97); `gunicorn wsgi:app` serves `/api/health`.
- **Things to watch (breaking for local runs):**
  - **Python 3.12 is required** now (3.13 should also work). Recreate your virtualenv;
    `pipenv` is no longer used.
  - **Flask 3 ignores `FLASK_ENV` for debug mode.** Use `FLASK_DEBUG=1` (or `flask run
    --debug`) for the reloader/debugger. `FLASK_ENV` is still read by our own config to
    pick development/testing/production.
  - **SQLite `dev.db` moved**: Flask-SQLAlchemy 3 resolves a relative
    `sqlite:///dev.db` inside the `instance/` folder (`instance/dev.db`, git-ignored),
    not `app/dev.db`. Your old `app/dev.db` is no longer used (and P15 resets the
    migrations, so start fresh with `flask db upgrade && flask seed all`).
  - Postgres with psycopg 3 was **not tested against a real Postgres server** here (no
    Postgres available in the sandbox); only the URL rewrite and driver loading were
    checked. Test it with the P34 docker compose Postgres.
  - SQLAlchemy 2.1 is newer than the 2.0 the plan named; everything tested fine. If a
    library ever complains, pin `SQLAlchemy<2.1` in `requirements.in` and recompile.
  - Code still uses legacy `Model.query.get()`; it works but warns until P14.

## P14 — Update code to SQLAlchemy 2.0 / Flask-SQLAlchemy 3 style
- **Problem:** The code used the legacy 1.x query API (`Model.query.get()`,
  `Model.query.filter(...).first()`, `Query.update()`), which SQLAlchemy 2 marks legacy and
  prints warnings for; Batch 1 used `Model.query.get_or_404()` as a stop-gap. Followers
  used `lazy='dynamic'` (legacy in 2.0). Timestamps used Python's `datetime.now` (local
  time, no timezone) and the API returned Flask's HTTP-date strings
  (`"Mon, 23 Nov 2026 18:04:05 GMT"`), which are awkward to parse. The like-recount in the
  seeds used a raw SQL string.
- **What changed:**
  - All queries use the 2.0 style: `db.session.get(Model, id)`,
    `db.get_or_404(Model, id, description=...)` (same JSON 404 messages as before),
    `db.session.scalars(select(Model).where(...)).all()`,
    `db.session.scalar(select(...))`, and `db.session.execute(update(Post)...)` for the
    race-safe like counter. Covers `app/api/*.py`, the login/signup forms and the
    Flask-Login user loader. No `Model.query` is left in the app.
  - `User.followers` / `User.follows` are now normal lists (`lazy='select'`) instead of
    dynamic queries; the code that appends/removes followers works unchanged.
  - New `TimestampMixin` in `app/models/db.py`: `created_at` / `updated_at` are
    `DateTime(timezone=True)`, `NOT NULL`, with `server_default=func.now()` (database
    clock) and `onupdate=func.now()`. It also sets `default=func.now()` so inserts work on
    the tables made by the old migrations (which have no server default); P15 drops that
    once the new baseline migration exists.
  - API timestamps are ISO-8601 with a UTC offset (`"2026-11-23T18:04:05+00:00"`) via a
    small `iso()` helper (SQLite returns naive values; they are UTC and get marked so).
    The frontend shows them with a new `react-app/src/utils/formatDate.js`
    (`"Nov 23, 2026"`, in the viewer's locale) on the home feed and in the post modal.
    Before, the raw HTTP-date string was printed.
  - The explore list (`GET /api/posts/`) now sorts by `created_at DESC, id DESC`, so
    posts created in the same second keep a stable order (SQLite's clock has 1-second
    resolution).
  - Seeds: `recount_post_likes()` uses an ORM `update()` with a correlated
    `select(func.count())` instead of a raw SQL string. (The other raw SQL in the seed
    files was already removed in P0; the dead `app/seeds/follows.py` goes in P15.)
- **Files:** `app/__init__.py`, `app/api/{auth,comment,me,post,user}_routes.py`,
  `app/forms/{login_form,signup_form}.py`, `app/models/{db,comments,posts,postLike,user}.py`,
  `app/seeds/postLikes.py`, new `react-app/src/utils/formatDate.js`,
  `react-app/src/components/HomeFeed/ActualFeed.js`,
  `react-app/src/components/reUsedComponents/SinglePostModal.js`.
- **How to verify:** `grep -rn "\.query\." app` finds nothing outside the dead
  `app/seeds/follows.py`. New test-client script (P14, 20/20) runs with SQLAlchemy
  legacy/deprecation warnings turned into errors and calls every GET endpoint, like/unlike,
  comment create/edit and follow/unfollow; checks `createdAt` parses as ISO-8601 with a
  timezone and 404 messages are unchanged. All earlier scripts green (the P10 feed-order
  check now parses ISO dates). `npm run build` succeeds (CRA, pre-existing warnings only).
- **Things to watch:** **API change:** `createdAt`/`updatedAt` are ISO strings now. The
  frontend only displayed them, and it now formats them, so nothing else breaks; any
  external script that parsed the old HTTP-date format must switch. Dates show as a date
  only ("Nov 23, 2026"); "3 hours ago" style is a possible P31 polish. Seeded rows all get
  (nearly) the same timestamp now, because the database clock is read once per statement.

## P15 — Remove the Heroku schema hack and reset migrations
- **Problem:** Every model had `if environment == "production": __table_args__ =
  {'schema': SCHEMA}` and `add_prefix_for_prod('users.id')` foreign keys, and
  `migrations/env.py` created a Postgres schema and set `search_path` in production. That
  existed only because App Academy's shared Heroku Postgres gave each student a schema; it
  made every model harder to read and had broken deploys before. The migration history
  was 4 old App Academy migrations (one empty, one swapping a `followers` table for
  `follows`) plus the Batch 1 P6 migration, and two dead files (`app/models/follows.py`,
  `app/seeds/follows.py`, fully commented out / importing a name that no longer exists).
- **What changed:**
  - Removed `environment`, `SCHEMA` and `add_prefix_for_prod` from `app/models/db.py`
    and every model; foreign keys are plain `'users.id'` / `'posts.id'`. Removed the
    schema/search_path code from `migrations/env.py` and `SCHEMA` from `.env.example`.
  - Added a SQLAlchemy **naming convention** (`pk_`, `fk_`, `uq_`, `ix_`, `ck_` prefixes)
    so every constraint has a predictable name that later migrations can refer to.
  - `follows` columns are now `NOT NULL` and the pair has a named unique constraint
    `uq_follows_follower_followed` (same rule as before, now with a name).
  - Deleted all 5 old migrations and generated **one baseline**
    `migrations/versions/0001_baseline_schema.py` (revision id `0001_baseline`) from the
    models, then tidied it: `server_default=sa.func.now()` instead of the SQLite-specific
    `CURRENT_TIMESTAMP` text so it is portable to Postgres. **The Batch 1 P6 rule is in the
    baseline**: `post_likes` has `UNIQUE (user_id, post_id)` named
    `uq_post_likes_user_post` (the old migration's duplicate-cleanup step is not needed on
    an empty database).
  - `TimestampMixin` drops the temporary `default=func.now()` from P14; the tables now
    have `DEFAULT now()` themselves.
  - `Migrate(..., render_as_batch=True)`: future migrations that alter constraints also
    work on SQLite (Alembic rebuilds the table there).
  - Deleted `app/models/follows.py` and `app/seeds/follows.py`.
- **Files:** `app/models/{db,user,posts,comments,postLike}.py`, `app/__init__.py`,
  `migrations/env.py`, `.env.example`, new `migrations/versions/0001_baseline_schema.py`;
  deleted `migrations/versions/{356ea97f15e1_,8e380edbf296_,bd907f496434_,e66be29cbd54_,a1f3c9d2e7b4_unique_post_likes}.py`,
  `app/models/follows.py`, `app/seeds/follows.py`.
- **How to verify:** on an empty SQLite DB: `flask db upgrade` -> "Running upgrade ->
  0001_baseline"; `flask db check` -> "No new upgrade operations detected" (models and
  migration match); `flask db downgrade base && flask db upgrade` works; `flask seed all`
  works. Postgres DDL checked offline with
  `DATABASE_URL=postgresql://u:p@localhost/postpix flask db upgrade --sql`: shows
  `TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL` and
  `CONSTRAINT uq_post_likes_user_post UNIQUE (user_id, post_id)`. Test-client script
  (P15, 5/5): constraint present, duplicate like rejected by the DB, alembic version is
  `0001_baseline`, a raw SQL insert gets `created_at` from the server default. All earlier
  scripts green.
- **Things to watch (breaking for local runs):**
  - **Existing local databases cannot be upgraded** (their `alembic_version` points at a
    revision that no longer exists: "Can't locate revision ..."). Delete the old file
    (`app/dev.db` or `instance/dev.db`) and run `flask db upgrade && flask seed all`.
    There is no production database, so nothing real is lost.
  - From now on, every schema change is a **new** migration on top of `0001_baseline`
    (`flask db migrate -m "..."`, review the file, `flask db upgrade`). Never edit the
    baseline once a real database uses it.
  - The baseline was not run against a real Postgres server (none available here); the
    generated Postgres SQL was reviewed instead. Run it once against the P34 compose
    Postgres.

## P16 — Replace Create React App with Vite
- **Problem:** The frontend was built with Create React App (`react-scripts` 4), which is
  abandoned, needed `NODE_OPTIONS=--openssl-legacy-provider` on Node 17+, was slow, and
  caused almost all of the **193 npm audit findings (16 critical, 56 high)**.
- **What changed:**
  - `react-scripts`, `http-proxy-middleware` and the CRA testing libraries are removed;
    **Vite 8** + `@vitejs/plugin-react` are the dev server and bundler. New
    `react-app/vite.config.js`: dev server on port **3000** with a proxy
    `/api -> http://localhost:5000` (replaces CRA's `"proxy"` field), and
    `build.outDir: "build"` so Flask and the Dockerfile keep serving `react-app/build`.
  - `public/index.html` moved to `react-app/index.html` (Vite's entry) with
    `<script type="module" src="/src/index.jsx">` and `/favicon.ico` instead of
    `%PUBLIC_URL%`. `public/` still holds the favicon (copied to the build as-is).
  - The 49 `.js` files containing JSX were renamed to `.jsx` (`git mv`, history kept).
    Plain re-export `index.js` files, `store/` and `utils/` stay `.js`. Imports without
    extensions keep working.
  - `store/index.js`: `process.env.NODE_ENV === "production"` ->
    `import.meta.env.PROD`, and `require("redux-logger")` -> a normal `import` (Vite
    has no `require`).
  - Fixed a broken import Vite refuses to build (webpack only warned):
    `PostGrid.jsx` imported a non-existent `getAllFollowingPosts` from `store/post`.
  - `package.json`: scripts `dev`/`start` (`vite`), `build` (`vite build`), `preview`;
    `"type": "module"`; `engines.node >= 22.12`; dropped `eslintConfig`, `browserslist`,
    `proxy`. React 17 / router 5 / Redux 4 versions are unchanged here (P17-P19).
    `package-lock.json` regenerated from scratch.
  - The old `NODE_OPTIONS=--openssl-legacy-provider` workaround is no longer needed
    (docs updated in the walkthrough commit).
  - Env vars: the unused `REACT_APP_BASE_URL` was removed from `.env.example` and the
    `Dockerfile`; `.env.example` explains the `VITE_` prefix rule for any future
    frontend variable (and that they are public). `react-app/README.md` rewritten for Vite.
- **Files:** `react-app/package.json`, `react-app/package-lock.json`, new
  `react-app/vite.config.js`, `react-app/index.html` (moved from `public/`),
  `react-app/src/**/*.jsx` (renamed), `react-app/src/store/index.js`,
  `react-app/src/components/reUsedComponents/PostGrid.jsx`, `react-app/README.md`,
  `.env.example`, `Dockerfile`.
- **How to verify:** `cd react-app && npm install && npm run build` -> built in ~0.2 s
  (JS 216 kB, 67 kB gzipped). `npm audit` -> **0 vulnerabilities** (was 193).
  Served the build from Flask (`gunicorn wsgi:app`): `/`, the hashed `/assets/*.js` and
  `/favicon.ico` -> 200; CSRF login, feed and like over HTTP -> 200. With `npm run dev`
  plus Flask, the same login/feed/like calls through `localhost:3000` work via the proxy.
  Headless check (jsdom loading the built bundle from Flask): Demo Login -> home feed
  with 31 images, Explore (50 images), a profile page, back home; no console errors.
- **Things to watch (breaking for local runs):** use **`npm run dev`** (or `npm start`,
  same thing) and **Node 22.12+**; drop any `NODE_OPTIONS=--openssl-legacy-provider`.
  Delete your old `react-app/node_modules` and run `npm install` (the lockfile was
  regenerated). Environment variables for the frontend must be `VITE_*`, read with
  `import.meta.env`. Linting (`eslint`) came with CRA and is gone until P43. The 4.7 MB
  `stock.jpg` is still bundled (P24). Deep-link refresh on the Flask-served build is
  fixed in P18.

## P17 — Upgrade React 17 -> 19
- **Problem:** React 17 is out of support, `ReactDOM.render` was removed in React 19, and
  newer libraries (react-redux 9, react-router 7, Redux Toolkit 2) need React 18+.
- **What changed:**
  - `react` / `react-dom` 17 -> **19.3.1**; `react-redux` 7 -> **9.3.1**; `redux` 4 ->
    5.0.1 and `redux-thunk` 2 -> 3.1.0 (react-redux 9 expects Redux 5; thunk 3 only has a
    named export, so `import { thunk } from "redux-thunk"`); `react-icons` 4 -> 5.7.0
    (every icon used still exists; the build would fail otherwise).
  - `src/index.jsx`: `ReactDOM.render(<App/>, root)` -> `createRoot(root).render(<App/>)`.
  - `src/context/Modal.jsx`: `ReactDOM.createPortal` -> named `createPortal` import.
  - Removed `@fortawesome/free-solid-svg-icons` and `@fortawesome/react-fontawesome`:
    nothing imports them (the plan said to bump them; removing unused packages is the
    smaller, safer change).
  - StrictMode double-effects: React 18+ runs effects twice in **development** only. I
    checked every `useEffect`: they only load data (GET requests), so the second run is
    a harmless duplicate fetch; no effect creates, likes or deletes anything.
- **Files:** `react-app/package.json`, `react-app/package-lock.json`,
  `react-app/src/index.jsx`, `react-app/src/context/Modal.jsx`,
  `react-app/src/store/index.js`.
- **How to verify:** `npm install && npm run build` -> OK (JS 306 kB, 93 kB gzipped;
  React 19 is larger than 17). `npm audit` -> 0 vulnerabilities. Headless jsdom run of the
  built app against Flask: Demo Login -> feed (31 images), Explore (50), open a post modal,
  like it (0 -> 1 likes, red heart), add a comment (shown in the modal), close the modal,
  open a profile, back home, log out via the profile menu; **no console errors**.
- **Things to watch:** in `npm run dev` you will see each page's GET requests twice in the
  Network tab and in the redux-logger output; that is StrictMode, not a bug, and does
  not happen in the production build. react-router is still v5 here (works with React 19
  for these routes); P18 upgrades it.

## P18 — Upgrade react-router v5 -> v7 (and fix deep-link refresh)
- **Problem:** react-router v5 is unmaintained and not built for React 19. The route
  table used `<Switch>`, a `ProtectedRoute` that wrapped `<Route>`, `useHistory` and
  `<Redirect>`, and the catch-all `/:userId` swallowed every unknown URL (e.g. `/typo`
  rendered an empty profile). Separately, **refreshing a deep link** such as `/explore`
  on the Flask-served build returned **404** (Flask's `/<path>` static route answered
  before the React catch-all; open question 4 from Batch 1).
- **What changed:**
  - `react-router-dom` 5 -> **`react-router` 7.18.6** (in v7 everything, including
    `BrowserRouter` and `NavLink`, is imported from `react-router`; `react-router-dom` is
    only a re-export). All imports updated.
  - `App.jsx`: `<Switch>` -> `<Routes>` with `element={...}`. `/` renders the feed when
    logged in and the login page otherwise. `/users`, `/explore` and `/:userId` sit
    inside a **layout route** `<Route element={<ProtectedRoute />}>`. New `*` route shows
    a new **NotFound** page (`components/NotFound/`).
  - `ProtectedRoute.jsx` is now a layout route: `user ? <Outlet /> : <Navigate to="/"
    replace />`.
  - `useHistory()` -> `useNavigate()` (`history.push(x)` -> `navigate(x)`) in
    `PostForm`, `SignUpForm`, `SearchBar`; `<Redirect to="/" />` -> `<Navigate to="/"
    replace />` in `LoginForm`, `SignUpForm`, `TempLogin`, `EditCaptionForm`, `PostForm`.
  - Profiles stay at `/:userId` (the plan's "keep /:userId" option, so no links change).
    v7 ranks static paths (`/explore`, `/users`) above dynamic ones automatically, and
    `UserProfile` shows the NotFound page when the id is not a number (`/typo`).
  - **Deep-link fix (Flask):** the app is created with `static_folder=None` and
    `react_root()` serves the build itself: an existing file under `react-app/build` is
    sent with `send_from_directory` (which refuses `..` paths); a missing path that looks
    like a file (has a `.` in the last segment, e.g. an old `/assets/index-abc.js`) is a
    JSON 404; every other non-`/api` path gets `index.html`, so React Router handles
    `/explore`, `/42` and its own 404 page. The build folder is configurable as
    `FRONTEND_DIST` (default `react-app/build`).
- **Files:** `react-app/package.json`, `react-app/package-lock.json`,
  `react-app/src/App.jsx`, `react-app/src/components/reUsedComponents/ProtectedRoute.jsx`,
  `react-app/src/components/UserProfile/index.jsx`, new
  `react-app/src/components/NotFound/{index.jsx,NotFound.css}`, every component that
  imported from `react-router-dom` (24 files, import path and the hooks above),
  `app/__init__.py`.
- **How to verify:** `npm run build` OK; `npm audit` 0. Served by Flask: `curl` of
  `/explore`, `/1`, `/no-such-page` -> 200 (index.html); `/assets/nope.js` -> 404;
  `/../app/config.py` (with `--path-as-is`) -> 404, no file leak; `/api/nope` -> JSON 404.
  Headless jsdom runs: **loading `/explore` and `/1` directly (logged in)** render the
  explore grid (50 images) and Demo's profile; `/no-such-page` and `/a/b/c` render "Page
  not found"; `/explore` logged out redirects to the login page; the full click-through
  (login, feed, explore, post modal like + comment, profile, logout) still passes with no
  console errors. Backend test-client scripts all green.
- **Things to watch:** `NavLink` still adds an `active` class (no CSS uses it). A numeric
  id that does not exist (`/99999`) still renders an empty profile shell (the API returns
  404); a proper "user not found" state is P31. If you later add a real route that
  contains a dot (e.g. `/u/john.doe`), adjust the "looks like a file" rule in
  `react_root()`. Data loading still happens in components (`useEffect`), not in v7
  loaders; that could come with P19/P31.

## P19 — (Optional) Move to Redux Toolkit
- **Problem:** 14 hand-written reducers with string action-type constants, action
  creators and `switch` statements (about 1,000 lines), a manual store setup
  (`createStore` + `applyMiddleware(thunk, logger)` + DevTools compose), and
  `comments` registered twice in `combineReducers`. The deprecated `createStore` is what
  Redux 5 warns about. Several slices hold overlapping data (`follow`, `followers`,
  `profileFollowing`, `notFollowed`, `users`, `searchUsers`).
- **What changed:**
  - Added `@reduxjs/toolkit` 2.15.0 and removed `redux` and `redux-thunk` (RTK includes
    both).
  - `store/index.js`: `configureStore({ reducer, middleware })`. RTK adds redux-thunk,
    Redux DevTools support and, **in development only**, checks that throw if state is
    mutated outside a reducer or if non-serializable values are dispatched. The duplicate
    `comments` key is gone. `redux-logger` is kept for development, now via
    `createLogger({ collapsed: true })`.
  - Every reducer file is now a `createSlice` (`session`, `posts`, `comments`, `follow`,
    `users`, `currentPost`, `userLikes`, `userPostLikes`, `followingPosts`, `followers`,
    `notFollowed`, `searchUsers`, `profileFollowing`, `profileUser`). Reducers are short
    "mutating" functions that Immer turns into safe copies (e.g. the old comment-edit
    reducer really mutated state; now it is safe). A tiny `store/helpers.js` `keyBy()`
    replaces the repeated "list -> object keyed by id" loops.
  - **Same state shape and the same exported thunks** (`login`, `getAllPosts`,
    `addFollowing`, ...), with the same return values, so no component had to change.
    Thunks stay plain async functions (not `createAsyncThunk`) for exactly that reason:
    components use `const errors = await dispatch(login(...))`.
  - **Bug fixed (introduced in P16):** `import logger from "redux-logger"` gives the
    CommonJS module object, not the middleware function, so with P16-P18 the
    **development** build / `npm run dev` crashed at start-up with "logger is not a
    function" (production builds were fine, which is what the earlier checks ran). Now a
    named `import { createLogger }`; checked in the Vite dev server's transformed output
    and in a development-mode bundle.
- **Files:** `react-app/package.json`, `react-app/package-lock.json`,
  `react-app/src/store/*.js` (all 15 files), new `react-app/src/store/helpers.js`.
- **How to verify:** `npm run build` OK; `npm audit` 0. Headless jsdom runs on the
  production bundle **and on a development-mode bundle** (so RTK's mutation and
  serializability checks, StrictMode double effects and redux-logger are active):
  Demo Login, feed, explore, post modal like (0 -> 1, red heart) and comment, profile,
  logout; on `/9` Follow -> "Following" and followers 0 -> 1, then Unfollow -> back to 0;
  deep links `/explore`, `/1`, `/no-such-page`; **no console errors** in any run.
- **Things to watch:** this is the "minimal safe" version of P19. The overlapping slices
  were **not merged** and **RTK Query was not introduced**: merging them changes which
  data each screen reads and needs screen-by-screen testing (better done with P31's
  loading/error states and P43's frontend tests). Action type strings changed (e.g.
  `session/SET_USER` -> `session/setUser`); only visible in DevTools/logger. In
  development RTK will now throw if a component ever mutates store data; that is on
  purpose.

# Batch 3 items (performance and UI/UX)

Batch 3 = P20-P32 (performance, then UI/UX) plus four add-ons Tyler approved: Z1 (merge
the overlapping Redux slices and load like state once), Z2 (drop redux-logger), Z3 (a
proper not-found page for unknown profile ids) and Z4 (your own posts in your home feed).
Commits are in this order: P20, P21, Z4, P25, Z1, Z2, Z3, P22, P23, P24, P26, then the
look and feel (P27, P32, P29, P28, P30, P31), then the walkthrough update.

## P20 — Lightweight user payloads
- **Problem:** `User.to_dict()` loaded the full follower list, following list and like
  list for every user it serialized (3 extra queries per user, megabytes of JSON as the
  data grows). `/api/users/` with the 14 seeded users ran dozens of queries, and so did
  login, `/api/auth/` and every follow/unfollow. `/notfollowing` loaded every user and
  filtered in Python; follow/unfollow loaded the whole follower list to check for
  duplicates.
- **What changed:**
  - A user payload now has counts computed by the database in the same query
    (`followerCount`, `followingCount`, `postCount`) plus `isFollowedByMe` for the logged-in
    viewer. The `followers`, `following` and `likes` lists are gone from it. New
    `User.stats_select(viewer_id)` builds that one query (correlated `COUNT` subqueries and
    an `EXISTS`), `User.row_to_dict()` turns a row into the payload, and `to_dict()` /
    `to_self()` use them (still one query each). `to_self()` adds `email` as before.
  - New "summary" shape for lists (`id`, `username`, `firstName`, `lastName`,
    `profilePicture`), used by `/followers`, `/following` and `/posts/<id>/likes/users`
    (one joined query each, no `to_dict()` per row). List items are keyed by `id` now
    (they used `userId` in the followers/following lists).
  - `GET /api/users/<id>/notfollowing` is one query with `NOT IN (subquery)`, excludes the
    user, takes `?limit=` (default 10, max 50). `GET /api/users/` is capped (`?limit=`,
    default 50, max 100) until P23 replaces its only use.
  - Follow/unfollow use a single `INSERT` / `DELETE` on the `follows` table (the unique
    constraint turns a duplicate into the same 409 as before) instead of loading the
    follower list. They return the same `{currentUser, followingUser}` shape.
  - Unknown user ids on `/users/<id>` and its sub-routes return a JSON 404.
  - Comment create/update use `current_user` directly instead of serializing the user.
  - Frontend (minimum to keep it working; Z1 reshapes the store properly): the profile
    header uses `isFollowedByMe`, `followerCount`, `followingCount`; follower/following
    list slices key by `id`; the following modal loads its list from the `/following`
    endpoint when opened.
- **Files:** `app/models/user.py`, `app/api/user_routes.py`, `app/api/post_routes.py`,
  `app/api/comment_routes.py`, and in `react-app/src`: `store/follower.js`,
  `store/following.js`, `store/profile_following_store.js`, `CircleFaces.jsx`,
  `UserInfoBox.jsx`, the follower/following list modals.
- **How to verify:** test-client script (27 checks): counts match the database for every
  user, `/api/users/` runs at most 4 queries (was ~46), `notfollowing` honours `limit` and
  never returns the user or people already followed, follow/unfollow counts and 409s,
  404s for missing users, no `email` or lists in public payloads, comments still work. The
  older Batch 1/2 scripts (P3, P4, P5, P6, P7, P8, P9, P10, P12, P14, P15, P0 ids) still
  pass. Production build + jsdom click-through: demo login, feed, explore, like, comment,
  profile, logout, and Follow/Unfollow on `/9` (followers 0 -> 1 -> 0), 0 console errors.
- **Things to watch:** this is an API shape change: anything outside this repo reading
  `user.followers` / `user.following` / `user.likes` would break (nothing in the app does
  now). `to_dict()` still costs one query per call; for lists always use `stats_select()`.
  The follower/following lists are not paginated until P22.

## P21 — Add database indexes
- **Problem:** Postgres does not index foreign keys automatically. Profile pages, the
  explore page, comment lists, like lists and "who follows X" would scan whole tables as
  the data grows. The `follows` foreign keys also had no `ON DELETE CASCADE`.
- **What changed:** New migration `0002_indexes` (on top of `0001_baseline`, which is
  untouched) creates five indexes, and the models declare the same ones:
  `posts(user_id, created_at)` (profile grid), `posts(created_at, id)` (explore and home
  feed ordering, used by P22's cursor paging), `comments(post_id)`, `post_likes(post_id)`,
  `follows(followed_id)`. It also recreates the two `follows` foreign keys with
  `ON DELETE CASCADE` (batch mode, so SQLite can do it too). The `follows` columns were
  already `NOT NULL` from P15. The migration downgrades cleanly (drops the indexes and
  restores the plain foreign keys).
- **Files:** `migrations/versions/0002_indexes_and_follow_cascade.py`,
  `app/models/{posts,comments,postLike,user}.py`.
- **How to verify:** on a fresh SQLite file `flask db upgrade` -> `flask seed all` ->
  `flask db check` ("No new upgrade operations detected") -> `flask db downgrade` ->
  `flask db upgrade` -> `flask db downgrade base` all succeed. `EXPLAIN QUERY PLAN` shows
  every query above using its index instead of a table scan. All earlier test scripts
  still pass (the P15 script now expects revision `0002_indexes`).
- **Things to watch:** the two `posts` indexes are plain ascending, not `DESC` as the plan
  wrote them: both databases read an index backwards for `ORDER BY ... DESC`, and
  expression indexes make `flask db check` report false changes. Run the migration once
  on Postgres in P34 (generated SQL only was reviewed; no Postgres is available here).
  On SQLite `ON DELETE CASCADE` only acts when `PRAGMA foreign_keys=ON`; the ORM still
  removes follow rows itself when a user is deleted, so behaviour is the same.

## Z4 — Your own posts in your home feed (add-on)
- **Problem:** The home feed (`GET /api/me/following/posts`) only returned posts by people
  you follow, so a new user, or anyone who just posted, saw an empty feed and no sign that
  their post worked. This was open question 1 from Batch 1; Tyler decided yes.
- **What changed:** the feed query now matches `user_id IN (followed) OR user_id = me`.
  Still one posts query (plus one batched authors query), still newest first with the
  `id` tie-break. The route keeps its URL and response shape.
- **Files:** `app/api/me_routes.py`.
- **How to verify:** test-client script (5 checks): own posts present, nothing from people
  you do not follow, still sorted newest first, 3 queries or fewer, and a post created
  during the test is first in the feed. The P10 script was updated to expect your own
  posts too.
- **Things to watch:** the route name still says `following`; renaming it would break the
  frontend for no gain. P22 will paginate this endpoint.

## P25 — Bundle and dead-code cleanup
- **Problem:** The frontend carried unused test components (`TempFollow`, `TempLogin`,
  `TempLogout`, `TempPost`, `TempComment`, `User`, `UsersList`) that were still imported
  by `App.jsx` and made hard-coded API calls (e.g. `/api/posts/1`, `/api/comments/4`);
  82 commented-out `console.log` calls; hundreds of lines of commented-out code; and
  the whole app shipped as one 337 kB script.
- **What changed:**
  - Deleted the seven unused components and the `CreatePost` / `CreateComment` folders
    that only held them, plus the `/users` route that listed every user (it now falls to
    the 404 page like any unknown URL).
  - Removed all commented-out `console.*` lines and commented-out code (JS lines, JSX
    `{/* <Component /> */}` blocks, and a few commented CSS rules), found with a script and
    then reviewed in the diff. Explanatory comments were kept.
  - `App.jsx`: each page (login, home, explore, profile, 404) is loaded with `React.lazy`
    inside `<Suspense>`, so the first load downloads only what that page needs.
    The main script went from 337 kB to 242 kB (gzip 105 kB -> 76 kB); the rest arrives
    in small per-page chunks (the post modal chunk loads when a page that has one is
    opened).
  - Icons: the app already uses a single library (`react-icons`, from P17), so nothing to
    merge there.
- **Files:** `react-app/src/App.jsx`, the deleted component folders, and light edits in
  about 40 `.jsx` / `.js` / `.css` files (only removed comments).
- **How to verify:** `npm run build` OK. jsdom click-through on both a production-mode and
  a development-mode single-file bundle: demo login, feed, explore (50 images), post modal
  open + like + comment + close, profile, logout, 0 console errors in both.
- **Things to watch:** this commit only removes dead code and comments; behaviour is
  unchanged. The 4.7 MB `stock.jpg` is still imported at this point (P24 removes it).
  Lazy routes show a blank page for a moment on a slow connection; P31 adds proper loading
  states.

## Z1 — One clean Redux store; likes loaded once (add-on)
- **Problem:** The store had 14 slices that overlapped or were never read: `follow`,
  `followers`, `profileFollowing`, `notFollowed`, `users`, `searchUsers`, `profileUser`,
  `currentPost`, `userLikes`, `userPostLikes`, `followingPosts`, `posts`, ... Several held
  the same people or posts under different names, many were written but nothing read them
  (`searchUsers`, `followers`), and components re-fetched everything to keep them in sync.
  Worst: every post tile ran `GET /api/users/likes` when it mounted, so the Explore page
  sent about 50 identical requests, and `PostGrid` re-requested all posts on top of the
  page that had just loaded them.
- **What changed:**
  - **Backend:** post payloads now include `likedByMe` and `commentCount`, computed for a
    whole list with 2 extra queries (not one per post) by the new
    `app/api/serializers.py`. Used by the explore list, home feed, single post, create and
    edit post, and the profile's `Posts`. Like/unlike responses include `likedByMe`. So the
    frontend never needs to ask "which posts have I liked?" (`GET /api/users/likes` is no
    longer called; the endpoint is kept, now one query).
  - **Store:** six slices instead of fourteen:
    `session` (the logged-in user), `users` (users by id plus the home page's
    `followingIds` / `suggestionIds`), `posts` (posts by id: the one place post data
    lives), `feeds` (ordered post ids for `home` and `explore`, with a load status),
    `profile` (open profile: user id, status, post ids) and `comments` (comments of the
    open post). Feeds and profiles hold only ids, so a like in the modal updates the feed,
    the grid and the modal at once. Removed: `follow`, `followers`, `profileFollowing`,
    `notFollowed`, `searchUsers`, `profileUser`, `currentPost`, `userLikes`,
    `userPostLikes`, `followingPosts` (and the old `post.js`).
  - New post/comment/follow thunks return `null` on success or an array of error messages
    (the old ones returned a mix of arrays, `undefined` and response objects). New
    `utils/api.js` wraps `apiFetch` into `{ ok, status, data, errors }` and never throws.
  - Lists that only one screen needs (followers, following, people who liked a post, the
    nav search results) are fetched by that screen with a small `hooks/useFetch.js` and are
    not stored; one `UserListModal` replaces three near-identical modal components.
  - Logging out resets every slice, so the next user never sees the previous user's likes
    or feeds (the old store kept them).
  - The home feed is shown in the order the server sent (newest first). The old code
    reversed an object keyed by id, which was newest-by-id and ignored the timestamps.
  - Components changed to read the new store: home feed, avatar row, suggestions,
    profile, explore, post grid, post modal (reads the post by id; no per-tile requests),
    comments, caption/comment edit and delete, new-post form. The home feed's like button
    now works (it was commented out), with `aria-pressed`.
- **Files:** `app/api/serializers.py` (new), `app/api/{post,me,user}_routes.py`,
  `react-app/src/store/*` (6 slices + `index.js`), `react-app/src/utils/api.js`,
  `react-app/src/hooks/useFetch.js`, and the components listed above.
- **How to verify:** test-client script (15 checks): `likedByMe` and `commentCount` match the
  database for the explore list, home feed and profile, constant query count (5 including
  the login lookup) for any number of posts, like/unlike flip `likedByMe`, create/edit
  payloads. Earlier backend scripts still pass. jsdom run on production **and** development
  bundles (development mode turns on Redux Toolkit's mutation and non-serializable checks):
  login, home feed, explore (50 images), open post, like (0 -> 1, red heart), comment,
  profile (5 posts, 7 followers, 5 following), follow/unfollow on `/9` (followers 0 -> 1 ->
  0), logout; **0 console errors**. Request log for that run: 0 calls to
  `/api/users/likes` (was about 50 on Explore alone) and 1 call to `/api/posts/` for Explore.
- **Things to watch:** every component that read the old slice names changed in this
  commit; anything not in this repo that read them would break (nothing known). In
  development React StrictMode runs effects twice, so the request counts double there.
  `redux-logger` is still installed until Z2. The profile header shows nothing while
  loading or when the user does not exist until Z3 and P31 add those states. The nav
  search still downloads up to 100 users once (replaced by server search in P23).

## Z2 — Drop redux-logger (add-on)
- **Problem:** `redux-logger` printed every action to the browser console in development
  and was a source of bugs (the P16 import error fixed in P19). The Redux DevTools
  browser extension already shows every action and state, and Redux Toolkit wires it in.
- **What changed:** removed the `redux-logger` package and its code in `store/index.js`,
  which is now just `configureStore({ reducer })`. RTK still adds redux-thunk, DevTools
  support and, in development only, the "no state mutation / serializable values" checks.
- **Files:** `react-app/package.json`, `react-app/package-lock.json`,
  `react-app/src/store/index.js`.
- **How to verify:** `npm install` + `npm run build` OK, `npm audit` reports 0
  vulnerabilities; `redux-logger` is gone from the lock file and the source; jsdom
  click-through on a development-mode bundle (RTK's checks on): 0 console errors.
- **Things to watch:** install the "Redux DevTools" browser extension to inspect actions;
  nothing is logged to the console any more.

## Z3 — Not-found state for profiles that do not exist (add-on)
- **Problem:** Opening `/99999` (a numeric id with no user) showed the nav bar and a blank
  page: the profile component simply rendered nothing when the API said 404. Very large
  ids (`/99999999999999999999`) made the backend raise an error instead of answering 404.
- **What changed:**
  - The profile slice already tracks `status` (`ready`, `notFound`, ...); the profile page
    now shows the shared `NotFound` component with the text "Profile not found" and a link
    home when the status is `notFound`. `NotFound` takes an optional title and message
    (the unknown-URL page keeps "Page not found").
  - Backend: all `<int:id>` URL parts are now `<int(max=2147483647):id>`, so an id larger
    than a database integer is a normal JSON 404 instead of an `OverflowError` (500 in
    production).
- **Files:** `react-app/src/components/UserProfile/UserInfoBox.jsx`,
  `react-app/src/components/NotFound/index.jsx`, `app/api/{user,post,comment}_routes.py`.
- **How to verify:** test-client: `/api/users/99999`, `/api/users/99999999999999999999999`
  and `/api/users/0` all return a JSON 404. jsdom (development-mode bundle, logged in):
  `/99999` and `/99999999999999999999` show "Profile not found"; `/abc` shows "Page not
  found"; `/1` still shows the real profile; 0 console errors. Earlier scripts still pass.
- **Things to watch:** a profile that is still loading renders nothing until P31 adds a
  skeleton. The not-found page is plain until the P32 restyle.

## P22 — Pagination and infinite scroll
- **Problem:** Every list endpoint returned everything: explore sent every post ever made,
  the home feed every followed post, a profile all its posts (inside the user payload),
  and comments, followers, following and likers were unbounded. Cost grows with the
  data, and the frontend rendered thousands of tiles at once.
- **What changed:**
  - **Cursor pagination** on the list endpoints, with a shared `app/api/pagination.py`.
    Every response gets `"nextCursor"` (send it back to get the next page, `null` = no more).
    - Posts, newest first: `GET /api/posts/`, `GET /api/me/following/posts` and the new
      `GET /api/users/<id>/posts`: `?limit=12&before=<cursor>` (limit 1-50, default 12).
      The cursor is `<created_at>,<id>`, so posts created in the same second cannot be
      skipped or repeated.
    - Comments, oldest first: `?limit=20&after=<cursor>` (limit up to 100).
    - Followers, following, people who liked a post: `?limit=30&after=<last id>`.
  - Each page runs a fixed number of queries (5 for 50 posts including login lookup).
  - `GET /api/users/<id>` no longer embeds the user's posts (use `/posts`), and
    `GET /api/auth/` no longer embeds `Posts` either: both were unbounded and nothing used
    the login copy.
  - **Frontend:** the `feeds`, `profile` and `comments` slices keep `nextCursor` and a
    "loading more" flag; new thunks `loadMoreFeed`, `loadMoreProfilePosts`,
    `loadMoreComments`. A `LoadMore` component loads the next page by itself when it
    scrolls within 400 px of the viewport (`IntersectionObserver`, `hooks/useInfiniteScroll.js`)
    and is also a real button ("Load more posts"), so keyboard users and browsers without
    the API can use it. The followers / following / likers modal list uses
    `hooks/usePagedList.js` with the same button.
- **Files:** `app/api/pagination.py` (new), `app/api/serializers.py`, `app/api/{post,me,user,auth}_routes.py`,
  `react-app/src/store/{feeds,profile,comments}.js`, `react-app/src/hooks/{useInfiniteScroll,usePagedList}.js`,
  `LoadMore.jsx`, `ActualFeed`, `ExplorePage`, `UserInfoBox`, `CommentContainer`, `UserListModal`.
- **How to verify:** test-client script (24 checks): walking every page returns every post
  exactly once, in newest-first order, for explore, home feed, profile, comments (including
  25 extra posts created within the same second), followers, following and likers; default
  and clamped limits; bad cursor gives a JSON 400; missing user gives 404. jsdom (development
  bundle): with a mocked `IntersectionObserver` Explore keeps loading until all posts are
  shown with no duplicates; without it, the first page is 12 tiles and the button adds 12
  more; home feed 12 -> 21 posts; profile shows its 5 posts; the followers modal lists
  7 people; the post modal lists comments; 0 console errors.
- **Things to watch:** this changes the API (no embedded `Posts`; list endpoints return only
  the first page unless you follow `nextCursor`). Cursors are opaque: do not build them by
  hand. On SQLite timestamps are compared as text (`CURRENT_TIMESTAMP` has no fraction), so
  the cursor helper formats the comparison value the same way; Postgres compares real
  timestamps. Plan said `?before=` for every list; comments and people lists use `after`
  because they read oldest-first / by id (see "Deviations from plan").

## P23 — Server-side user search
- **Problem:** The nav bar downloaded a list of users (all of them, with all their
  relations before P20) every time it mounted, just to filter by username in the browser.
- **What changed:**
  - New `GET /api/users/search?q=ab&limit=10`: case-insensitive prefix match on username,
    up to 25 results (default 10), summary shape (no email). It is a range comparison
    (`lower(username) >= 'ab' AND lower(username) < 'ac'`) so it uses the new index and
    treats `%` and `_` as ordinary characters (no `LIKE` wildcards to escape).
  - New migration `0003_user_search` creates the index `ix_users_username_lower` on
    `lower(username)` (downgrades cleanly); the model declares it too.
  - Search bar: nothing is downloaded on page load; typing waits 250 ms after the last
    key, sends one request, ignores answers that are out of date, and shows the matches
    or "No users with that username found!". `GET /api/users/` (capped list) is no longer
    used by the app and `hooks/useFetch.js` was deleted.
- **Files:** `app/api/user_routes.py`, `app/models/user.py`,
  `migrations/versions/0003_user_search_index.py`, `react-app/src/components/NavBar/SearchBar.jsx`.
- **How to verify:** test-client script (15 checks): prefix and case-insensitive matches equal
  the expected names, `%`/`_`/empty/very long/edge-character queries are safe, limit clamps,
  login required, `EXPLAIN QUERY PLAN` shows the index. `flask db upgrade`, `check`,
  `downgrade`, `upgrade`, `downgrade base` all work. jsdom: no search or user list request on
  load; typing "m", "ma", "mar" quickly makes exactly 1 request; results render; a no-match
  term shows the message; clicking a result opens that profile and clears the box.
- **Things to watch:** only the username prefix is searched (as before), not first/last
  name. `flask db check` prints a warning that SQLite cannot reflect expression indexes;
  it reports no changes. Search results have no keyboard (arrow key) navigation or
  combobox roles yet; P30 adds those.

## P24 — Image optimization
- **Problem:** the build shipped a 4.7 MB `stock.jpg` (imported by a component that did not
  use it); uploads were stored exactly as sent, so a 3-8 MB phone photo was downloaded in
  full to draw a 300 px grid tile (and kept its camera metadata, including GPS location);
  post images had no `loading` / size hints, so the page jumped as they arrived.
- **What changed:**
  - **Bundle:** deleted `react-app/src/images/` (`stock.jpg` and four icon images, none
    imported by anything; icons come from `react-icons`). The largest file in the build is
    now the 224 kB main script.
  - **Uploads** (`app/s3_helpers.py`): after the existing validation, the image is decoded
    with Pillow, rotated per its camera orientation, and re-encoded: a WebP of at most
    1080 x 1350 px (quality 82) plus a 400 px WebP thumbnail (quality 78); images are never
    enlarged. Profile pictures (signup and `kind=avatar`) become one 320 px WebP. All
    metadata (EXIF, GPS) is dropped because the new file does not carry it. GIFs become a
    still image. Files are uploaded with `Cache-Control: public, max-age=31536000, immutable`
    (their random names are never reused).
  - `POST /api/img/upload` now answers `{url, thumbUrl, width, height}`.
  - **Database:** migration `0004_post_images` adds nullable `thumb_url`, `img_width`,
    `img_height` to `posts` (downgrades cleanly); post payloads carry `thumbUrl`,
    `imgWidth`, `imgHeight`; `POST /api/posts/` accepts them (all optional, so older posts,
    seeds with external pictures and older clients keep working).
  - **Frontend:** grid tiles use `thumbUrl` (falling back to `imgUrl`) with
    `loading="lazy"` and `decoding="async"`, and the tiles have a fixed `aspect-ratio`; feed
    images are lazy and carry their `width`/`height`; the new-post form passes the upload's
    URLs and size on.
- **Files:** `app/s3_helpers.py`, `app/api/{img,auth,post}_routes.py`, `app/models/posts.py`,
  `app/forms/create_post.py`, `migrations/versions/0004_post_images.py`, `PostForm.jsx`,
  `ImageUploadComponent.jsx`, `SinglePostModal.jsx`, `ActualFeed.jsx`, `PostGrid.css`,
  `store/posts.js`, deleted `src/images/*`.
- **How to verify:** test-client script (18 checks, S3 replaced by a fake): a 3000x2000 JPEG
  becomes a 1080x720 WebP plus a 400x267 thumbnail under 30 kB; small images are not
  enlarged; a tall image is capped at 1350 px; EXIF rotation is applied and the camera
  maker string is gone from the bytes; PNG with alpha and GIF work; avatars get one 320 px
  file; fake images and bad extensions are still rejected; posts store and return the
  thumbnail and size, and the old payload (no thumbnail) still works. The P7 script was
  updated for the new `.webp` names and cache header. Frontend builds; jsdom explore, home
  and profile runs have 0 errors. Migration up/down/up and `flask db check` are clean.
- **Things to watch:** uploading to the real S3 bucket was not tried (needs credentials);
  everything up to the S3 call is covered by the fake. Existing seeded posts still point at
  external pictures, so they have no thumbnail until P37 gives the project its own bucket.
  Pillow's WebP encoder must be present in the install (it is in the pinned wheels). A
  future batch migration on `users` on SQLite would drop the `lower(username)` expression
  index from P23 (SQLite cannot reflect it): recreate it in such a migration.

## P26 — Server tuning and caching (the part that exists today)
- **Problem:** `gunicorn wsgi:app` ran with defaults (one process, one request at a time);
  every response, including the 224 kB JavaScript file that never changes, was served
  without cache headers, so browsers either re-downloaded or guessed; and API answers
  (per-user data) had no "do not cache" header.
- **What changed:**
  - New `gunicorn.conf.py` (read automatically when you run `gunicorn wsgi:app` from the
    project folder): 2 `gthread` workers with 4 threads each (sized for a 1-2 GB server),
    `preload_app`, worker recycling every ~1000 requests, access and error logs to
    stdout/stderr, in-memory heartbeat files. `WEB_CONCURRENCY`, `GUNICORN_THREADS`,
    `GUNICORN_TIMEOUT`, `BIND`, `LOG_LEVEL` override it.
  - Flask now sends `Cache-Control` for the React build: `assets/*` (hashed file names)
    `public, max-age=31536000, immutable`; `index.html` and the deep-link fallback
    `no-cache` (so a deploy is picked up at once); other files (favicon) one hour. Every
    `/api/*` response gets `Cache-Control: no-store` unless the route set its own.
- **Files:** `gunicorn.conf.py` (new), `app/__init__.py`.
- **How to verify:** `gunicorn --check-config wsgi:app` OK; starting it shows "Using worker:
  gthread" and 2 booted workers; test-client script (8 checks) covers every header above
  and that a missing asset is still a 404 and an unknown API URL still a JSON 404.
- **Things to watch:** the Postgres memory settings, the Docker compose file and the
  CloudFront cache policy / compression named in the plan belong to P33, P34 and P36,
  which do not exist yet; they are not done here (see "Deviations from plan"). When
  CloudFront is added, give `/api/*` and `index.html` a "no cache" policy to match these
  headers. gzip/Brotli is left to CloudFront as the plan says; Flask serves the files
  uncompressed.

# Batch 3 UI/UX items

Design direction (Tyler: "as appealing as possible, must not look like Instagram"): P27 fixes the
HTML shell, P32 sets up the design tokens, fonts, logo and the login/sign-up screens, P28
rebuilds the layout of every page for phones and desktops, P29 rebuilds modals on the native
`<dialog>` element, P30 is the accessibility audit, and P31 adds loading, empty and error states
and instant (optimistic) likes and follows. Exact colours, fonts and screen descriptions are in
the P32 section.

## P27 — Fix the HTML shell
- **Problem:** `index.html` had no viewport tag (phones drew a shrunken desktop page), no link
  preview tags, a favicon in one format only, and no theme colour.
- **What changed:** `react-app/index.html` now has `<meta name="viewport" content="width=device-width,
  initial-scale=1, viewport-fit=cover">`, a description, `color-scheme` (light and dark), two
  `theme-color` values (light `#F3F6F5`, dark `#0B1413`), Open Graph and Twitter card tags
  (title, description, site name), a `<noscript>` message and the title "Postpix". New icons made
  from the Postpix "P" mark: `favicon.svg` (sharp at any size), `favicon.ico` (16/32/48 px),
  `apple-touch-icon.png` (180), `icon-192.png`, `icon-512.png`, a maskable 512 icon for Android, and
  `manifest.webmanifest` so "Add to home screen" shows the name and teal icon. The icons are
  generated by a small Pillow script from the same geometry as the SVG; they are committed files.
- **Files:** `react-app/index.html`, `react-app/public/*` (icons and manifest).
- **How to verify:** `npm run build` copies all files to `build/`; through the Flask server `/`,
  `/favicon.svg`, `/favicon.ico`, `/apple-touch-icon.png`, `/manifest.webmanifest` and
  `/icon-512.png` all answer 200 with the right content types; the manifest is valid JSON; the
  page contains no occurrence of the word "Instagram". On a phone: the page now fits the screen
  width (no pinch-zoom to read).
- **Things to watch:** there is no `og:image` yet: link previews need an absolute image URL, which
  depends on the final domain (P36). The `upgrade-insecure-requests` policy from Batch 1 stays.

## P32 — Visual refresh: design tokens, type, logo, login (and a design system for the rest)
- **Problem:** colours, sizes and fonts were hard-coded in 20 CSS files (often the same rule
  pasted three times), `* { font-family }` overrode everything, nothing was fluid, there was no
  dark mode, and the login page had the typical "centred card" look that gets flagged as a
  look-alike. No real browser is available here, so the look below is described rather than
  screenshotted (see the note at the end).
- **What changed:**
  - **Design tokens** in `src/styles/tokens.css` (CSS variables): colour, type scale, spacing
    (4 px grid), radius, shadow, layout widths, motion, z-index. Dark colours switch on with the
    operating system setting (`prefers-color-scheme`). Old `--pp-*` names are aliases so
    unrewritten CSS keeps working until P28/P29.
  - **Base styles** in `src/styles/base.css`: a small reset, typography, one visible keyboard
    focus ring (3 px, `--focus`, 2 px offset), a "skip to content" style, reduced-motion support,
    and shared building blocks: `.btn` (`primary`, `secondary`, `ghost`, `danger`, `sm`, `block`),
    `.icon-btn`, `.field` + `.input`, `.form-errors`, `.avatar`, `.spinner`.
  - **Fonts:** Bricolage Grotesque (headings, logo) and Figtree (everything else), both open
    fonts (SIL OFL 1.1) installed as npm packages and served from our own server (no Google
    request). Only the Latin files (about 64 kB) are downloaded for English text; the extended
    sets load only if a name needs them. System fonts are the fallback.
  - **Logo:** the original teal "P" mark and lowercase "postpix" wordmark, refined: the mark is
    now an SVG (a geometric white P in a rounded square, the same shapes as the favicon) and the
    wordmark is set in Bricolage Grotesque 800 with a tight tracking and a teal "pix". A light
    version is used on the dark login panel.
  - **Login screen (new layout):** on a wide screen it is split in two: on the left a deep-teal
    panel (`#08403B` with a soft glow) holds the logo, the headline "Share photos with friends."
    in 56 px Bricolage Grotesque and a wall of 8 tinted "photo" tiles (teal, deep teal, sand,
    mint; each a tiny drawn landscape: sun, hills, moon, stripes, dots; staggered by a few pixels
    like pinned prints); on the right the form sits on the page colour, left-aligned, with "Log
    in", labelled Email and Password fields, a primary "Log in" button, an "or" divider, a
    secondary "Demo Login" button with the line "Look around as a ready-made user. No sign-up
    needed.", then "New to Postpix? Sign up" and the demo disclaimer. On a phone the panel
    becomes a compact header above the form (no tile wall). It shares nothing with another
    network's login page: no phone mock-up, no centred boxed card, no gradient, no app-store
    badges, its own mark and fonts.
  - **Sign-up form:** labelled fields (first name, last name, username, email, password with a
    hint, repeat password), an optional profile photo picker with a preview, errors in a red
    alert box, autocomplete attributes, a primary "Sign up" button. Still shown in the old dialog
    until P29.
  - **Not-found page** restyled with the tokens and a real button.
- **Colours (light / dark):** page `#F3F6F5` / `#0B1413`; surface `#FFFFFF` / `#121E1D`; text
  `#10201E` / `#E8F1EF`; secondary text `#4B5F5C` / `#9DB3AF`; hairlines `#D5DEDC` / `#263C39`;
  input borders `#778B88` / `#5F7A76`; accent teal `#0F766E` / `#3CC4B4` (hover `#0B5E58` /
  `#6AD9CB`); soft teal tint `#D9F0EC` / `#123A36`; like heart `#C92A3C` / `#FF6B7A`; error
  `#B42318` / `#FF8A80`; focus ring `#0B5E58` / `#6AD9CB`; photo backdrop `#0D1A19`.
- **Files:** new `react-app/src/styles/{tokens,base}.css`, `components/Brand/{LogoMark,Wordmark,Mosaic}.jsx`
  and CSS, `components/LoginPage/*`, `NotFound/*`, `src/index.css` (trimmed to one copy of the
  rules the edit dialogs still use), `src/index.jsx`, `package.json` / lock (two font packages).
- **How to verify:** `python3 contrast.py` (a small script that reads `tokens.css`) checks 24
  colour pairs in both light and dark against WCAG AA (4.5:1 text, 3:1 for borders, focus ring
  and icons): **0 failures** (the first run caught the input border at 2.6:1; it was darkened to
  `#778B88`, now 3.3:1+). Build OK and `npm audit` 0. jsdom click-through (login via Demo Login,
  feed, explore, post modal like and comment, profile, logout) with 0 console errors.
- **Things to watch:** nobody has looked at the result in a real browser yet: please open the
  login page, resize it to phone width and toggle your system dark mode, and tell me what looks
  off. Refreshed README screenshots are not included for the same reason. The rest of the app
  still uses its old layout until P28 (it already picks up the new fonts and colours).

## P29 — Accessible dialogs and post detail
- **Problem:** Every pop-up was a `div` with a click-catching backdrop: no focus trap, no
  Escape, no labels, no focus return, background still scrollable. Post detail, the post
  menu, caption/comment edit, delete confirm, new post, likers and sign-up each had their
  own copy of the markup, and tiles were clickable images rather than buttons.
- **What changed:**
  - `context/Modal.jsx` is now one `Modal` component on the native `<dialog>` element
    (`showModal()`): the browser provides the focus trap, Escape, inert background and
    `::backdrop`. We add: backdrop click closes, focus returns to the opener, the page
    scroll is locked (counter-based so stacked dialogs work), a titled header with a Close
    button (`aria-labelledby`), sizes `sm`/`md`/`lg`. Phones get a bottom sheet (full
    screen for `lg`), 40rem+ a centered card. The `ModalProvider` is gone.
  - New `Post/` components: `PostTile` (a `<button>`; counts show on hover and keyboard
    focus), `PostGrid` (responsive; `mosaic` makes every 7th Explore tile 2x2),
    `PostDetail` (photo shown whole on a dark ground, author, caption, comments with Load
    more, like button, likers list, labelled comment box), `PostOptions`,
    `CommentOptions`, `NewPost` (choose a file, preview, caption with counter), `LikeButton`
    (`aria-pressed`). Shared `ui/Avatar` and `ui/Time` (a `<time>` element).
  - Deleted the old Edit*/Delete*/SinglePost/CommentContainer/PostForm/ImageUpload/
    PostSettings/Logout files; the likers list and sign-up use the new `Modal`.
- **Files:** `react-app/src/context/Modal.{jsx,css}`, `react-app/src/components/Post/*`,
  `components/ui/*`, `UserListModal`, `LoginPage/SignUpModal.jsx`, plus the importers.
- **How to verify:** open Explore, press Tab to a tile and Enter: the post opens; Tab stays
  inside; Escape closes and focus returns to the tile. Like, comment, edit caption,
  delete. jsdom check `p29.mjs` (13 checks) passes; `p22.mjs` was updated to the new markup.
- **Things to watch:** jsdom has no modal `<dialog>`, so focus trap and Escape are only
  checked as "close event unmounts"; I could not test them in a real browser. NavBar and
  feed still use their old layout until P28 (they only got the new components).

## P28 — Page layouts: nav, home feed, Explore, profile
- **Problem:** Fixed pixel layouts (a 935 px feed, absolute positions, desktop-only nav
  with an icon-only dropdown), no mobile layout at all, tiny hit areas, and a profile
  page that was a small avatar plus three numbers.
- **What changed:**
  - **Nav:** a sticky top bar (logo mark + "postpix", pill search, links). On screens under
    40rem the same single `<nav aria-label="Main">` becomes a tab bar fixed to the bottom
    (Home, Explore, New post, You) with 44 px targets and safe-area padding; the logo
    shrinks to the mark so search gets the room. Between 40 and 56rem the labels go
    icon-only (still read aloud). The account menu is a real disclosure button (Profile,
    Log out; Escape and outside click close it). Search is a labelled `type=search`
    field; results are links; a polite live region says how many people were found;
    Escape clears it.
  - **Home:** one column 38rem wide, with a "people you follow" row of squircle faces
    (teal ring) on top. Each post is a card: author, date, the photo in a frame that
    follows its own shape (clamped between 4:5 and 3:2, square when unknown, so no layout
    jump), heart, comments button, like count, caption, and "View all N comments", which
    opens the post dialog. From 64rem a sticky right rail shows you, "People to follow"
    (with working Follow buttons) and the credits (GitHub/LinkedIn icons, labelled).
  - **Explore:** page heading and a mosaic grid: every 7th tile is 2x2 and uses the
    full-size image; other tiles use the 400 px thumbnail. 2 columns at 375 px.
  - **Profile:** large squircle avatar with a teal ring, full name as the `h1`,
    `@username`, posts/followers/following (the last two open the people dialogs), and a
    Follow/Following button with `aria-pressed`. Side by side from 40rem, centered on
    phones. A profile with no posts shows an empty state.
  - `<main id="main">` and a "Skip to content" link are in `App.jsx`; Login and NotFound no
    longer nest their own `main`. `LoadMore` has its own CSS. Removed the old nav, feed,
    explore and profile CSS, the side-column components and `index.css`.
- **Files:** `components/NavBar/*`, `HomeFeed/*`, `ExplorePage/*`, `UserProfile/*`,
  `reUsedComponents/LoadMore.*`, `App.jsx`, `index.jsx`.
- **How to verify:** `npm run build`; log in as the demo user and resize to 375 px:
  tab bar at the bottom, 2-column Explore grid, no sideways scroll. At 1200 px the rail
  appears. jsdom check `p28.mjs` (22 checks) covers landmarks, rail follow, account menu,
  Explore mosaic, profile, follow toggle, not-found and search keyboard behavior.
- **Things to watch:** no real browser was available, so spacing, sticky behavior and
  breakpoints were written from the design and checked only as markup. Please look at it
  at 375, 768 and 1200 px.

## P30 — Accessibility pass (WCAG 2.2 AA)
- **Problem:** Before Batch 3 a scripted audit of the running app found 81 DOM issues
  (images without alt text, buttons and links with no name, unlabelled inputs, no `main`/`nav`/`h1`,
  modals that were not dialogs) plus 13 elements with click handlers that a keyboard
  cannot reach: 94 in total.
- **What changed:** most of it came with the rebuilds in P27-P29 (native dialogs with
  titles, labelled inputs, `button`/`a` for every click target, alt text rules, `main`,
  one labelled `nav`, one `h1` per page, tiles as buttons, `aria-pressed` on like/follow,
  visible focus ring from the tokens, 44 px targets, reduced-motion CSS). This item adds:
  - a "Skip to content" link and `<main id="main">` in `App.jsx`;
  - on every in-app navigation the tab title changes ("Explore - Postpix") and focus moves
    to the page content, because a single-page app otherwise leaves keyboard and screen
    reader users where they were;
  - the post dialog's "Comments" heading is an `h2`, so headings never skip a level;
  - `react-app/scripts/check_contrast.py` (the contrast check P32 refers to): 0 failures
    in light and dark.
- **Files:** `react-app/src/App.jsx`, `Post/PostDetail.jsx`, `react-app/scripts/check_contrast.py`.
- **How to verify:** `python3 scripts/check_contrast.py` from `react-app/` ends with
  `failures: 0`. Tab from the top of any page: the first stop is the skip link; Enter
  jumps to the content. Audit result after the work: **0 DOM issues and 0 non-interactive
  clickable elements (was 81 + 13 = 94)**, over login, sign-up, home, Explore, post
  dialog, profile, not-found and new-post dialog. jsdom check `p30.mjs` (7 checks).
- **Things to watch:** the audit is my own script on jsdom, not axe or a screen reader.
  Focus trapping and Escape rely on the browser's native `<dialog>`; color contrast is
  computed from the tokens only (not from rendered pixels, e.g. text on photos in the
  tile counts, which sit on a dark gradient).

## P31 — Loading, empty and error states, toasts, optimistic updates
- **Problem:** Pages showed nothing while loading and nothing when a request failed; an
  empty feed or profile was a blank area; likes and follows waited for the server before
  anything moved, so the app felt slow, and a failed request left no trace.
- **What changed:**
  - **Skeletons** (`ui/Skeletons.jsx`): grey, softly shimmering placeholders laid out like
    the real feed card, photo grid and profile header, so the page does not jump when data
    arrives. They announce "Loading ..." once to screen readers; the shimmer stops under
    `prefers-reduced-motion`.
  - **Empty and error states** (`ui/StatusMessage.jsx`): home ("Your feed is empty", with a
    button to Explore), Explore ("Nothing here yet"), profile ("No posts yet", worded
    for you or for them), plus error states with a "Try again" button on home, Explore,
    profile and the comments list in the post dialog. Errors are announced (`role=alert`).
  - **Toasts** (`utils/toast.js`, `ui/Toaster.jsx`): small messages at the bottom ("Post
    shared.", "Post deleted.", "Could not like this post. Try again."). Kept out of Redux
    because they are short-lived feedback. The container is a `popover`, which sits in the
    browser's top layer so toasts still show above an open dialog.
  - **Optimistic like and follow:** the heart, like count, Follow button and follower
    counts change immediately; the response then replaces them with the server's numbers;
    on failure everything is restored (including a suggestion in the right rail) and an
    error toast appears. A second tap on the same post during a request is ignored.
- **Files:** `store/posts.js`, `store/users.js`, `utils/toast.js`, `components/ui/*`,
  `HomeFeed/ActualFeed.jsx`, `ExplorePage/index.jsx`, `UserProfile/UserInfoBox.jsx`,
  `Post/PostDetail.jsx`, `App.jsx`.
- **How to verify:** in dev tools set the network to Offline (or throttle) and tap a heart:
  it fills at once and flips back with a message. Reload with throttling to see skeletons.
  jsdom check `p31.mjs` (12 checks: optimistic flip, rollback for like and follow, toast
  role, skeleton, error state, retry).
- **Things to watch:** Toasts opened while a dialog is open are visible but cannot be
  clicked (the dialog makes the rest of the page inert); they dismiss themselves after
  4 s (7 s for errors). Comment and caption edits are not optimistic: they show inline
  errors in their dialogs.

## Brand — official name is "PostPix"
- **What changed:** every user-facing spelling of the name (page and tab titles, wordmark, logo label, sign-up/login text, empty states, link-preview tags, web manifest, favicon title, README title, walkthrough) is now **PostPix**. The wordmark reads "Post" + "Pix" with "Pix" in the accent colour.
- **Not changed (on purpose):** lowercase technical identifiers such as the repo name and URL (`github.com/tyler-tor/postpix`). Older entries in this file keep the spelling they were written with.
- **Files:** `react-app/index.html`, `react-app/public/{favicon.svg,manifest.webmanifest}`, `react-app/src/**` (12 files), `app/__init__.py`, `README.md`, `docs/WALKTHROUGH.md`

---

# Batch 4 items (AWS deployment, app side)

Batch 4 prepares the app for AWS. This repo only gets the **app side**; the Terraform (P35, P36),
the deploy pipeline (P39) and backups (P40) live in a separate, shared infra repo that also hosts
Tyler's other two apps. Architecture decisions Tyler approved (they replace the plan where they
differ):

- **Database:** AWS RDS PostgreSQL, one shared instance with one database `postpix` and one user
  for this app (no Postgres container in production). The app reads `DATABASE_URL` (psycopg 3),
  SSL via `DATABASE_SSLMODE=require`. Local development keeps SQLite.
- **Servers:** one shared EC2 runs the three apps' API containers behind a Caddy reverse proxy.
  The React app is built to static files on S3 + CloudFront at `https://postpix.tylertorrero.dev`,
  and CloudFront sends `/api/*` to the EC2, so site and API are the same origin. Flask is
  **API-only** in production.
- **Images:** S3 through boto3's default credential chain (EC2 instance role in production,
  `AWS_PROFILE` locally); no access keys in the app. Public URLs start with `MEDIA_BASE_URL`
  (e.g. `https://postpix.tylertorrero.dev/media`).

## P33 — New API-only Dockerfile
- **Problem:** The old `Dockerfile` copied the whole repo (including `.env` if present, `.git`
  and local databases) into one stage, needed `react-app/build` to exist before building (it
  baked the frontend into the API image), ran as root, had no health check, and started
  gunicorn without the project's `gunicorn.conf.py` settings for the container's port.
- **What changed:**
  - **New multi-stage `Dockerfile`:** stage 1 (`python:3.12-slim`) installs the pinned
    `requirements.txt` into `/opt/venv`; stage 2 (`python:3.12-slim`) copies only that venv,
    `app/`, `migrations/`, `wsgi.py`, `gunicorn.conf.py` and two small scripts. Runs as an
    unprivileged user (uid/gid 10001); the code is owned by root, so the app cannot modify
    itself. `PORT=8000`, `FLASK_ENV=production`, no bytecode files, unbuffered logs.
    `CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]`.
  - **`HEALTHCHECK`** every 30 s runs `docker/healthcheck.py` (standard-library Python, since
    the slim image has no curl), which calls `GET /api/health` (no login, no database).
  - **`docker/entrypoint.sh`:** optional start-up steps, both off by default:
    `RUN_MIGRATIONS=1` runs `flask db upgrade`, `SEED_ON_START=1` runs `flask seed all` (safe:
    only seeds an empty database). Then `exec`s the command so gunicorn is PID 1 and gets
    Docker's stop signal. Production should run migrations as a deploy step after a database
    snapshot (P0 rule 4), which is why it is off in the image.
  - **`.dockerignore` is an allowlist** (`*`, then `!app/`, `!migrations/`, ...), so `.env`,
    `.git`, `node_modules`, `react-app/`, `.venv`, `instance/` and `*.db` can never end up in
    the build context, even if new files are added later.
  - **API-only Flask in production:** new setting `SERVE_FRONTEND` (env, default **off in
    production**, on in development). When off, the React catch-all route is not registered at
    all, so `/` and `/explore` are 404 and the image does not need `react-app/build`. Local
    `flask run` after `npm run build` still serves the build as before.
  - **`gunicorn.conf.py`:** binds `0.0.0.0:$PORT` when `PORT` is set (the container), `BIND`
    still wins, and with neither it is `127.0.0.1:8000` (local only). Disabled gunicorn 27's new
    "control socket" (it tried to create `$HOME/.gunicorn`, which the container user cannot
    write, and logged a `Permission denied` error on every start).
  - **First pytest files:** `pytest.ini` and `tests/` (`conftest.py` with an app/client fixture
    on in-memory SQLite, `test_api_only.py`). Run with `python -m pytest` after
    `pip install -r requirements-dev.txt`. (P42 later grows this into the full suite.)
- **Files:** `Dockerfile`, new `.dockerignore`, new `docker/entrypoint.sh`, new
  `docker/healthcheck.py`, `gunicorn.conf.py`, `app/config.py`, `app/__init__.py`, new
  `pytest.ini`, new `tests/conftest.py`, new `tests/test_api_only.py`.
- **How to verify:**
  - With Docker: `docker build -t postpix-api .` then
    `docker run --rm -p 8000:8000 -e SECRET_KEY=dev -e DATABASE_URL=sqlite:////data/p.db -e RUN_MIGRATIONS=1 -e SEED_ON_START=1 postpix-api`;
    `curl localhost:8000/api/health` -> `{"status":"ok"}`; `curl -i localhost:8000/` -> 404;
    after ~30 s `docker ps` shows `(healthy)`; `docker run --rm postpix-api id` -> `uid=10001`;
    `docker image ls postpix-api` should be roughly 250-300 MB (was about 1 GB).
  - Without Docker: `python -m pytest tests/test_api_only.py` (3 tests).
- **Things to watch:**
  - Docker was **not available** where this was written, so the image was not actually built.
    What was checked instead: `hadolint` (no findings), `shellcheck` on the entrypoint (clean),
    and an "image simulation": the exact allowlisted files plus a fresh Python 3.12 venv from
    `requirements.txt`, started through `entrypoint.sh` with `FLASK_ENV=production`,
    `RUN_MIGRATIONS=1`, `SEED_ON_START=1` -> 4 migrations, "Seeded demo data.", gunicorn on
    `0.0.0.0:$PORT` with 2 gthread workers, `healthcheck.py` exit 0 (exit 1 when nothing
    listens), `/` 404, `/api/posts/` 401. The venv is 110 MB (boto3/botocore is most of it).
    Please run the Docker commands above once on your Mac.
  - `docker run` with `FLASK_ENV=production` makes cookies `Secure`; browsers accept those on
    `http://localhost`, except older Safari. For local work use docker compose (P34), which runs
    the development config.
  - The health check uses `PORT`. If you ever set `BIND` to a different port, set `PORT` too.

## P34 — docker compose for local development (+ RDS-ready database settings)
- **Problem:** There was no one-command way to run the API in the same container that production
  will use, no way to try the app on Postgres locally, and the database connection had no
  settings for a managed, shared Postgres (RDS): no SSL option, no protection against connections
  RDS has closed, and SQLAlchemy's default pool (up to 15 connections per worker process) on a
  database instance shared with two other apps.
- **What changed:**
  - **New `docker-compose.yml`** (local development only; production compose lives in the infra
    repo):
    - `api`: built from the P33 `Dockerfile`, runs Flask's development server with auto-reload on
      port 8000 (published on `127.0.0.1` only), your code bind-mounted (`app/` read-only,
      `migrations/` writable), SQLite in a named volume (`/data/postpix-dev.db`). Loads your
      `.env` if it exists; the compose `environment` wins for `FLASK_ENV=development`,
      `DATABASE_URL`, and `RUN_MIGRATIONS=1` + `SEED_ON_START=1` (so the first start creates
      the tables and the demo data by itself).
    - `api-pg` + `db` in an optional **`postgres` profile** ("prod-like"): the same API on
      `postgres:17-alpine` (named volume, `pg_isready` health check, the API waits until it is
      healthy). Postgres is published on `127.0.0.1:5433` for a GUI client.
  - **Database settings for RDS** (`app/config.py`), only applied to Postgres URLs:
    - `DATABASE_SSLMODE` (e.g. `require`) and optional `DATABASE_SSLROOTCERT` are passed to
      psycopg 3. RDS accepts SSL; `require` encrypts the connection. (`verify-full` also checks the
      server certificate and needs the RDS CA bundle file in the image, a possible later step.)
    - `DATABASE_PASSWORD` (optional): if set, it is put into `DATABASE_URL` correctly escaped,
      so the URL can be written without a password. RDS-generated passwords often contain
      `@ / : #`, which break a hand-written URL.
    - Connection pool: `pool_pre_ping` (a connection RDS closed is replaced instead of failing a
      request), `pool_recycle` 300 s, `pool_size` 5 + `max_overflow` 2 per worker process
      (2 workers -> at most 14 connections for this app), `connect_timeout` 10 s,
      `application_name=postpix` (shows up in `pg_stat_activity`, handy on a shared instance).
      Each can be changed with `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_RECYCLE`,
      `DB_CONNECT_TIMEOUT`, `DB_APPLICATION_NAME`.
    - SQLite (local, tests) gets none of these options, as before.
  - README: a short "Running the API with Docker" section.
- **Commands:**
  - `docker compose up --build` -> API with SQLite on http://localhost:8000.
  - `docker compose up --build api-pg` -> API with Postgres (naming `api-pg` turns on the
    `postgres` profile and starts `db` too). Run only one of `api` / `api-pg`: both use port 8000.
  - Frontend as usual: `cd react-app && npm run dev` (http://localhost:3000, proxies `/api` to 8000).
  - One-off commands: `docker compose exec api flask seed all --reset`,
    `docker compose exec api flask routes`, `docker compose logs -f api`.
  - `docker compose down` stops; **`docker compose down -v` deletes the local databases** (named
    volumes `api-data`, `pg-data`).
- **Files:** new `docker-compose.yml`, `app/config.py`, new `tests/test_db_config.py`, `README.md`.
- **How to verify:** `docker compose up --build`, then `curl localhost:8000/api/health` and open
  http://localhost:3000 (Vite) and log in with Demo. Then `docker compose down` and
  `docker compose up --build api-pg`: the log shows the 4 migrations running against
  `PostgresqlImpl` and "Seeded demo data."; log in again. `python -m pytest tests/test_db_config.py`
  (3 tests: pool + SSL options accepted by SQLAlchemy/psycopg, password with `@:/#` escaped,
  SQLite untouched).
- **Things to watch:**
  - Docker was **not available** here, so compose was not run. The file was validated against the
    official Compose Specification JSON schema (`check-jsonschema --builtin-schema
    vendor.compose-spec`: ok) and its merged services were inspected. The Postgres path was not
    run against a real Postgres either (no Postgres in this environment); the options were checked
    by building a SQLAlchemy engine with them.
  - `env_file` with `required: false` needs Docker Compose 2.24 or newer (Docker Desktop has it).
  - S3 uploads inside the container need AWS credentials. The container does not see your
    `~/.aws` folder; uploads from the Docker API will say "upload failed" unless you add a
    read-only mount of `~/.aws` and `AWS_PROFILE` (or simply run Flask on your Mac for upload
    work). Everything else works without S3.
  - Keep the `db` image's major version (17) in step with the RDS engine version chosen in the
    infra repo.

## P37 — Uploads with the instance role, MEDIA_BASE_URL, and a seed media manifest (code side)
- **Problem:** `app/s3_helpers.py` built a boto3 client at import time from `S3_KEY` /
  `S3_SECRET` (static access keys, the kind that leaked in P1), read the bucket and URL settings
  at import time (outside the app factory), and built public URLs from a bucket URL that only
  works for a public bucket. Every seed image was hot-linked from hosts Tyler does not control
  (a teammate's `capstone-strava-clone-aktiv` bucket, imgur, vecteezy, and an Adobe Stock
  preview for the default avatar), so the demo could lose its pictures at any time.
- **What changed:**
  - **No access keys anywhere.** The S3 client is created on first use, per app, with only
    `region_name=AWS_REGION`; boto3's default credential chain finds the EC2 instance role in
    production and `AWS_PROFILE` / `aws sso login` locally. `S3_KEY`, `S3_SECRET` and
    `S3_PUBLIC_URL_BASE` are gone from code and `.env.example`.
  - **New settings** in `app/config.py`: `S3_BUCKET`, `AWS_REGION` (default `us-east-2`; also
    reads `AWS_DEFAULT_REGION`), `MEDIA_BASE_URL` (public base, e.g.
    `https://postpix.tylertorrero.dev/media`, trailing `/` removed).
  - **New `app/media.py`:** one rule for every image URL: `MEDIA_BASE_URL + "/" + key`. Uploads
    keep their keys `uploads/<random>.webp` (+ `_thumb.webp`), uploaded without an ACL. With no
    `MEDIA_BASE_URL`, an upload's URL falls back to the regional S3 URL
    (`https://<bucket>.s3.<region>.amazonaws.com/<key>`), which only displays if that bucket is
    public; set `MEDIA_BASE_URL` once CloudFront exists.
  - **New `app/seeds/media_manifest.json`:** maps every seed image to an S3 key under `seed/`:
    15 avatars (`seed/avatars/user-01.jpg` ... `user-15.jpg`, by the `#N` seed number in
    `users.py`), 50 post images (`seed/posts/post-01.jpg` ... `post-50.png`, by `postN` in
    `posts.py`) and the default avatar (`seed/avatars/default.jpg`). Each entry also keeps the
    original URL as `source`. `users.py` / `posts.py` now call `seed_avatar_url(n)` /
    `seed_post_url(n)` instead of hard-coding URLs.
  - **Local fallback:** without `MEDIA_BASE_URL` the seeds use each entry's `source` (the same
    URLs as before), so local development needs no AWS at all and looks exactly as it did.
  - **Default avatar** for new users without a picture is now a callable column default
    (`default_avatar_url()`), so it also comes from the media bucket in production.
    (Python-side default only; no migration needed.)
  - Upload failures are logged with `app.logger.exception` instead of `print`.
- **What the infra repo must do (P35/P36 media pack):** create the uploads bucket (private,
  Block Public Access on, Object Ownership "bucket owner enforced"); serve it through the site's
  CloudFront at `/media/*` with Origin Access Control, stripping the `/media` prefix (a
  CloudFront Function on the viewer request: `request.uri = request.uri.replace(/^\/media/, '')`)
  because the keys start at `uploads/` and `seed/`; upload the media pack: for every entry in
  `media_manifest.json` download `source` and put it at `key` with the right `Content-Type`
  and `Cache-Control: public, max-age=31536000, immutable`. Replacement pictures can be
  uploaded at the same keys (see "Things to watch").
- **Files:** new `app/media.py`, new `app/seeds/media_manifest.json`, `app/s3_helpers.py`,
  `app/config.py`, `app/models/user.py`, `app/seeds/users.py`, `app/seeds/posts.py`,
  `.env.example`, new `tests/test_media.py`.
- **How to verify:** `python -m pytest tests/test_media.py` (7 tests, S3 faked with moto: upload
  lands under `uploads/` with `image/webp`, a year-long `Cache-Control` and no ACL grant; URL
  starts with `MEDIA_BASE_URL`; regional URL without it; clean 502 "S3 is not configured"
  without a bucket; manifest covers seed users 1-15, posts 1-50 and the default avatar, all
  keys unique and under `seed/`; seeding with and without `MEDIA_BASE_URL`; new users get the
  default avatar). Locally: `flask seed all --reset` and the feed shows the same pictures as
  before.
- **Things to watch:**
  - **Your local `.env`:** `S3_KEY` / `S3_SECRET` are no longer read. If you test uploads
    locally, use `AWS_PROFILE=<profile>` (or `aws sso login`) with an identity that may
    `s3:PutObject` on `uploads/*` in your bucket, and set `AWS_REGION`.
  - **Image rights:** the media pack copies third-party pictures (imgur uploads, a vecteezy
    stock icon used by posts 1-3, an Adobe Stock preview as the default avatar, and the
    teammate's bucket). Copying them into your own bucket does not make them yours. Consider
    replacing them with your own or properly licensed photos: upload the new files at the same
    keys and nothing in the code changes. The teammate's bucket may also be gone already; the
    infra step should report any `source` that fails to download.
  - Existing databases keep the URLs they were seeded with; only new seeds (or the P41 demo
    reset for the demo user's posts) use `MEDIA_BASE_URL`. Production starts empty, so it is
    seeded with the new URLs from day one.
  - The manifest's keys must never be changed after upload: CloudFront and browsers cache them
    for a year. To change a picture, use a new key.

## P38 — App side of protecting the origin: trusted proxies, security headers, health checks
- **Problem:** In production every request reaches Flask through two proxies (CloudFront, then
  Caddy on the EC2). Without trusting their `X-Forwarded-*` headers Flask believes every request
  is plain `http` to an internal host name from Caddy's IP address. That matters for more than
  logs: on HTTPS, Flask-WTF's CSRF check requires the `Referer` to match `https://<request.host>/`,
  so a wrong host makes every login and post fail with "The referrer does not match the host."
  (reproduced in a test). There were also no security headers, the health check handed out a
  session and CSRF cookie on every probe, and there was no way to check the database.
- **What changed:**
  - **ProxyFix with configurable trusted hops:** `TRUSTED_PROXY_HOPS` (how many proxies to
    believe for `X-Forwarded-Proto` and `X-Forwarded-Host`; default **1 in production** =
    Caddy, **0 elsewhere** = ignore them) and `TRUSTED_PROXY_HOPS_FOR` (the same for
    `X-Forwarded-For`, the client IP; defaults to `TRUSTED_PROXY_HOPS`). With 0/0 nothing is
    wrapped, so locally nobody can fake these headers.
  - **Security headers** on every Flask response: `X-Content-Type-Options: nosniff`,
    `Referrer-Policy: strict-origin-when-cross-origin`, `X-Frame-Options: DENY`; on `/api/*`
    also `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'` and
    `Cross-Origin-Resource-Policy: same-origin`; in production
    `Strict-Transport-Security: max-age=31536000` (`HSTS_SECONDS`, 0 turns it off). The
    existing `Cache-Control: no-store` on API answers stays, so CloudFront never caches them.
  - **Health checks:** `/api/health` stays the cheap liveness check (no database, no login) and
    now sets **no cookies**. New **`/api/health/db`** runs `SELECT 1` and answers 200
    `{"status":"ok","database":"ok"}` or 503 `{"status":"error","database":"unreachable"}`
    (details only in the server log). Use it for monitoring / after a deploy, **not** as the
    Docker health check (a database blip must not make Docker restart a healthy container).
- **What the infra repo must do (Caddy / CloudFront), or CSRF fails:**
  1. CloudFront's `/api/*` behaviour must forward the viewer's `Host` header to the origin (an
     origin request policy that includes `Host`, e.g. the managed "AllViewer"), plus cookies,
     query strings and the `X-CSRFToken`, `Content-Type` and `Referer` headers; caching disabled.
  2. Caddy (one site block per app, matched by host) passes `Host` through and sets
     `X-Forwarded-Host` / `X-Forwarded-For` by itself. It sets `X-Forwarded-Proto` to the scheme
     of its own connection, so if CloudFront talks to the EC2 over plain HTTP add
     `header_up X-Forwarded-Proto https` in the PostPix block (the visitor's connection is
     always HTTPS at CloudFront). If X-Forwarded-Proto says `https` but the host is wrong,
     every POST fails the CSRF check.
  3. Only one proxy (Caddy) writes those headers, so keep `TRUSTED_PROXY_HOPS=1`. For real client
     IPs either configure Caddy's `trusted_proxies` with CloudFront's ranges and set
     `TRUSTED_PROXY_HOPS_FOR=2`, or leave it at 1 (then Flask sees the CloudFront edge IP, which
     is harmless today: nothing in the app uses the client IP yet).
  4. The React site's headers come from a CloudFront **response headers policy** on the S3
     behaviour: HSTS, `nosniff`, `frame-ancestors 'none'`/`X-Frame-Options: DENY`, and a CSP
     such as `default-src 'self'; img-src 'self' data: blob:; style-src 'self' 'unsafe-inline';
     font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self';
     form-action 'self'` (with `MEDIA_BASE_URL` on the same domain, `img-src 'self'` covers all
     production images). Its `Referrer-Policy` must **not** be `no-referrer` /
     `same-origin`-less variants that drop the Referer on same-origin requests; use
     `strict-origin-when-cross-origin`.
  5. The secret `X-Origin-Verify` header from the plan is best checked in Caddy (shared by all
     three apps), not in Flask; nothing app-side was added for it.
- **Files:** `app/__init__.py`, `app/config.py`, new `tests/test_proxy_security.py`.
- **How to verify:** `python -m pytest tests/test_proxy_security.py` (12 tests: forwarded
  headers trusted with 1 hop and ignored with 0; production defaults; login with CSRF **on**
  behind the proxy with a same-origin Referer -> 200, a foreign Referer -> 400 "referrer does not
  match", no token -> 400; every security header; HSTS only in production and switchable off;
  `/api/health` without cookies; `/api/health/db` 200, and 503 on an unreachable database while
  `/api/health` stays 200). By hand: `curl -i localhost:8000/api/health` shows the headers and
  no `Set-Cookie`; `curl localhost:8000/api/health/db`.
- **Things to watch:**
  - `/api/health/db` is public through CloudFront. It only runs `SELECT 1` and reveals nothing,
    but Caddy can restrict it if you prefer.
  - gunicorn's own access log still shows the proxy's IP (it does not use ProxyFix). Caddy's
    access log has the real client IP.
  - gunicorn adds a `Server: gunicorn` header; Caddy can remove it (`header -Server`).

## P41 + Q1 — Keep the demo account clean: `flask demo reset` (nightly)
- **Problem:** "Demo Login" (`demo@aa.io`) is shared by every visitor. Over time it collects
  their posts, deleted seed posts, random comments, likes and follows, so the next visitor sees
  a messy (or empty) demo, and anyone could delete the account through `DELETE /api/users/<id>`,
  breaking Demo Login for everyone. The only existing fix (`flask seed all --reset`) wipes the
  whole database and is (rightly) disabled in production.
- **What changed:**
  - **New command `flask demo reset`** (`app/seeds/demo.py`) that restores **only the demo
    user's data** to the seed state:
    - the demo user row (recreated with the seed password if it is missing; username, names and
      picture restored),
    - the demo user's posts: exactly the 5 seed posts. A seed post that still has its seed image
      and caption is kept as is (same id); edited or deleted ones are recreated; extra posts are
      deleted (with their comments and likes),
    - on those posts, exactly the seed comments and likes,
    - comments and likes the demo user made on other people's posts,
    - who the demo user follows and who follows the demo user.
  - **Never touched:** other users, their posts, their comments and likes on anything except the
    demo user's posts, and follows between other users. The only side effect on others: like
    counters of the posts whose demo like was added or removed are recounted from the real likes.
  - **How it knows the seed state without a copy of it:** it runs the normal seed functions in a
    throwaway in-memory SQLite database and reads the demo user's part by natural keys (emails,
    captions, comment text), never by ids (which differ between databases). So editing the seed
    files automatically changes what the reset restores. Seed images follow the current
    `MEDIA_BASE_URL` (P37).
  - **Safe for production:** allowed when `FLASK_ENV=production` (unlike `seed all --reset` /
    `seed undo`), one transaction (all or nothing), the demo row is locked (`SELECT ... FOR
    UPDATE` on Postgres) so two runs cannot interleave, and it refuses to run on an empty
    database ("Run `flask seed all` first"), because a lone demo user would make
    `flask seed all` skip seeding later. **Idempotent:** a second run reports
    `already matches the seed data` and changes nothing.
  - `--dry-run` shows what would change and rolls back. Output is one line with a UTC
    timestamp, made for a log file, e.g.
    `[2026-11-24T09:17:02Z] demo reset: posts removed 2, posts restored 2, following restored 5, ... (1.0s).`
  - **The demo account can no longer be deleted:** `DELETE /api/users/<demo id>` answers 403
    "The demo account cannot be deleted." (P41's optional item; the reset would recreate it
    anyway, but meanwhile Demo Login would fail). New `User.is_demo` / `DEMO_EMAIL` constant in
    `app/models/user.py`.
  - **Demo uploads are tagged** `postpix-demo=true` in S3 (both the image and its thumbnail), so
    an S3 lifecycle rule can delete them after the reset has removed their posts. Other users'
    uploads are not tagged.
- **Nightly schedule on the EC2 (infra repo installs it).** The host clock on EC2 is UTC;
  09:17 UTC = 2:17 AM in Denver in winter, 3:17 AM in summer. Replace `/opt/apps` and
  `postpix-api` with the compose folder and service name the infra repo uses.
  - **crontab** (`crontab -e` as the user that runs Docker; Amazon Linux 2023 needs
    `sudo dnf install -y cronie && sudo systemctl enable --now crond` first):
    ```
    17 9 * * * cd /opt/apps && /usr/bin/docker compose exec -T postpix-api flask demo reset >> /var/log/postpix/demo-reset.log 2>&1
    ```
    (`-T` because cron has no terminal; create `/var/log/postpix/` writable by that user.)
  - **or a systemd timer** (no extra package on Amazon Linux 2023; logs go to
    `journalctl -u postpix-demo-reset`):
    ```
    # /etc/systemd/system/postpix-demo-reset.service
    [Unit]
    Description=Reset the PostPix demo account to the seed data
    Requires=docker.service
    After=docker.service

    [Service]
    Type=oneshot
    WorkingDirectory=/opt/apps
    ExecStart=/usr/bin/docker compose exec -T postpix-api flask demo reset

    # /etc/systemd/system/postpix-demo-reset.timer
    [Unit]
    Description=Nightly PostPix demo reset

    [Timer]
    OnCalendar=*-*-* 09:17:00 UTC
    Persistent=true

    [Install]
    WantedBy=timers.target
    ```
    then `sudo systemctl daemon-reload && sudo systemctl enable --now postpix-demo-reset.timer`;
    `systemctl list-timers postpix*` shows the next run. Test once by hand with
    `docker compose exec postpix-api flask demo reset --dry-run`.
  - **S3 lifecycle rule** on the uploads bucket: filter by tag `postpix-demo` = `true`, expire
    current objects after 2 days. (Needs `s3:PutObjectTagging` in the instance role, see the infra
    list in the Batch 4 notes.)
- **Files:** new `app/seeds/demo.py`, `app/__init__.py` (registers `flask demo`),
  `app/models/user.py`, `app/api/user_routes.py`, `app/api/img_routes.py`, `app/s3_helpers.py`,
  new `tests/test_demo_reset.py`.
- **How to verify:** `python -m pytest tests/test_demo_reset.py` (11 tests: fresh seed -> no
  changes; snapshot matches the seeded demo; after a scripted "visitor session" (deleted, edited
  and new demo posts, comments, likes, follows) plus unrelated activity by other and brand-new
  users, the reset restores the demo state exactly while everything not involving the demo user
  is identical and every like counter is right; second run changes nothing; deleted demo account
  is recreated with a working password; CLI output, `--dry-run` saves nothing; refuses an empty
  database (exit 1); runs under the production config; demo account deletion -> 403; demo
  uploads tagged, others not). By hand: `flask seed all`, log in as Demo, delete a post, like
  something, follow someone, then `flask demo reset` and reload.
- **Things to watch:**
  - **Other people's comments and likes on the demo user's posts are removed** by the reset
    (those posts are part of the demo's data). Their own posts and everything else stay.
  - Restored posts are new rows: they get new ids and today's date, so they show up at the top of
    feeds after a night in which a visitor deleted them, and old links to the deleted post 404.
  - Matching other people's posts (for the demo's seed comments/likes) uses owner + caption. If a
    seed user edits a caption, the demo's seed comment on that post is not restored. Every seed
    user also has the password `password`, so visitors can log in as them too; only the demo
    account is reset (see open questions).
  - The demo password is only set when the account is recreated (there is no "change password"
    feature, so it cannot drift).
  - The reset runs the seed in memory each time (about 1 s, mostly hashing 15 seed passwords).

## Q2 — Demo account notice (add-on)
- **Problem:** Visitors using Demo Login had no way to know that the demo data is reset every
  night (P41), so a post they made "disappears" the next day without explanation.
- **What changed:**
  - The logged-in user's own payload (`/api/auth/`, login, signup: `User.to_self()`) has a new
    field **`isDemo`** (true only for `demo@aa.io`). Public user payloads do not get it.
  - New **`components/ui/DemoNotice.jsx`**, shown right under the top bar when
    `session.user.isDemo` is true: "You're using the demo account. Demo data resets nightly, so
    changes you make here will be cleared."
  - **Accessibility:** the message is a `role="status"` live region inside a labelled
    `<aside aria-label="Demo account notice">` (so it is in a landmark); the info and close icons
    are `aria-hidden`; the close button is a real `<button>` named "Dismiss demo account notice"
    with the usual 44 px target; after dismissing, focus moves to the page content instead of
    getting lost.
  - **Dismissal is remembered for the session** (`sessionStorage`, key
    `postpix.demoNoticeDismissed`): it stays hidden across pages and reloads in that tab and comes
    back in a new browser session. If storage is blocked it simply shows again next load.
  - **Design tokens only:** `--accent-soft` background, `--ink` text (14.1:1 light, 10.8:1 dark),
    `--accent-strong` icon, `--content-max` width, `--gutter` padding, `--text-sm`; works in dark
    mode automatically. Both colour pairs were added to `scripts/check_contrast.py` (all pass).
- **Files:** new `react-app/src/components/ui/DemoNotice.jsx`, `react-app/src/components/ui/ui.css`,
  `react-app/src/App.jsx`, `react-app/scripts/check_contrast.py`, `app/models/user.py`, new
  `tests/test_demo_flag.py`.
- **How to verify:** log in with Demo Login: the teal-tinted bar appears under the top bar; click
  the X, reload: it stays hidden; open a new browser window (new session): it is back. Log in as
  `marnie@aa.io`: no bar. `python -m pytest tests/test_demo_flag.py` (3 tests). Checked here in
  jsdom (10 checks on the component: role, exact text, landmark, button name, hidden icons,
  dismissal, sessionStorage, focus, stays hidden, comes back in a new session; plus the whole
  `<App/>` with a fake backend: shown right after the `<header>` for the demo user, not shown for
  another user), `npm run build`, and the Vite dev server serving `App.jsx`, `DemoNotice.jsx` and
  `ui.css` without errors.
- **Things to watch:** jsdom does not draw anything, so the look (spacing, wrapping on a 375 px
  phone) was written from the design tokens and not seen; please glance at it on your phone.
