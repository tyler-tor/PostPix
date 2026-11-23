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

---

## Open questions for Tyler

1. **Home feed (P10):** should your own posts appear in your home feed (Instagram does)? Currently only followed users' posts are shown, same as before. It's a one-line change.
2. **Branding (P11):** OK with the teal "postpix" wordmark and accent, or do you have preferred colours/logo for P32?
3. **Repo name:** rename the GitHub repo from `Instagram-Group-Project` to something like `postpix` (GitHub redirects old URLs)? Avoids the trademark name in your portfolio URL.
4. **Deep links (found during P11):** refreshing `/explore` on the Flask-served build returns 404 (pre-existing). Fix in P31/P33, or earlier as a small separate change? **Answered in Batch 2: fixed in P18.**

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
