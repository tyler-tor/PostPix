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

- **P5:** used `Model.query.get_or_404()` (works on the current Flask-SQLAlchemy 2.5) instead of `db.get_or_404()` (Flask-SQLAlchemy 3). Switch in P14.
- **P6:** kept the `posts.likes` counter (the plan's alternative option) but made it race-safe and recounted, instead of dropping the column; the new migration sits on top of the existing chain because P15 (migration reset) is Batch 2.
- **P3:** the signup profile-picture upload had to move into the signup request (multipart) because `/api/img/upload` now requires login; not spelled out in the plan.
- **P11:** the plan said "own logo, colors and login layout"; done as a text wordmark + accent colour + demo note + new favicon; the larger layout change is left to P32.

---

## Open questions for Tyler

1. **Home feed (P10):** should your own posts appear in your home feed (Instagram does)? Currently only followed users' posts are shown, same as before. It's a one-line change.
2. **Branding (P11):** OK with the teal "postpix" wordmark and accent, or do you have preferred colours/logo for P32?
3. **Repo name:** rename the GitHub repo from `Instagram-Group-Project` to something like `postpix` (GitHub redirects old URLs)? Avoids the trademark name in your portfolio URL.
4. **Deep links (found during P11):** refreshing `/explore` on the Flask-served build returns 404 (pre-existing). Fix in P31/P33, or earlier as a small separate change?

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
