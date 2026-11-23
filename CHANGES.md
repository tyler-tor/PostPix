# Postpix Change Log (Modernization)

This file explains every change made on the `modernize` branch, item by item, using the
numbering from `MODERNIZATION_PLAN.md` (P1-P48). Each section says what was wrong, what
changed, which files, how to check it yourself, and what to watch out for.

Batch 1 = security and bug fixes (P2-P11) on the **current** stack (Flask 2.0 /
SQLAlchemy 1.4 / Create React App). Stack upgrades are Batch 2.

---

## Tyler action: P1 key rotation (step by step)

A real AWS access key (ID starts with `AKIA`), its secret, and a Flask `SECRET_KEY` were
committed in a `.env` file in early Nov 2022 (deleted a couple of days later). Deleting a
file does **not** remove it from git history, and the GitHub repo is public. Nothing in this
branch can fix that from code; it needs these manual steps.

1. **Find whose key it is.** Run `git log --all --diff-filter=A --name-only -- .env` to see
   the commit(s); open one with `git show <hash>:.env` **on your own machine only** and look
   at the access key ID (do not paste it anywhere public). Sign in to the AWS account that
   owned the bucket (`S3_BUCKET` value). If it was a teammate's or App Academy's account,
   tell them so they can do steps 2-4.
2. **Deactivate, then delete the key.** AWS console -> IAM -> Users -> (the user) ->
   Security credentials -> Access keys -> find the key ID -> **Deactivate** -> confirm the
   app still works without it (it should; this branch does not need it) -> **Delete**.
   If the key no longer appears, it was already deleted (that is fine; say so in the
   open questions).
3. **Check for misuse.** CloudTrail -> Event history, filter by "Access key" = the old key
   ID, look back as far as allowed (90 days). Also check Billing -> Bills for unexpected
   services/regions (EC2 in odd regions is the classic sign of a stolen key). If you see
   anything odd, open an AWS Support case; they often waive charges from leaked keys.
4. **Make a new key only if you need one.** The plan (P37) moves to an EC2 IAM role so the
   app needs **no** access keys at all. Until then, if you need uploads locally, create a
   new key for an IAM user that only has `s3:PutObject` on your own bucket, put it in your
   local `.env` (which is git-ignored), and never commit it.
5. **New Flask SECRET_KEY.** Generate one with
   `python -c "import secrets; print(secrets.token_hex(32))"` and put it in `.env` /
   the server's environment. The old one is public, so anyone could forge session cookies
   for any deployment that still uses it.
6. **GitHub repo secrets.** Repo -> Settings -> Secrets and variables -> Actions: delete
   `HEROKU_API_KEY` / `HEROKU_APP_NAME` (Heroku deploy is dead; see P39).

**Why deactivating the key matters more than rewriting history:** the key was public for
years. Bots scrape GitHub for `AKIA...` strings within minutes, and anyone who forked or
cloned the repo still has the old history. Rewriting history cannot "un-leak" it; it only
hides it from people browsing later. A deactivated key is useless no matter who has a copy.
So: rotate first (required), rewrite history second (optional, cosmetic/reputation).

**If you want to rewrite history later (optional, destructive):**
1. Make a full backup: `git clone --mirror <repo-url> postpix-backup.git`.
2. Install git-filter-repo: `brew install git-filter-repo` (or `pip install git-filter-repo`).
3. In a **fresh** clone: `git filter-repo --invert-paths --path .env --path app/dev.db`
   (removes those files from every commit; every commit hash changes).
4. Re-add the remote (filter-repo removes it): `git remote add origin <repo-url>`.
5. Force-push all branches and tags: `git push --force --all && git push --force --tags`.
6. Ask GitHub Support to purge cached views of old commits if needed; teammates must
   re-clone (their old clones still contain the key - another reason rotation is the real fix).
Do this only after the `modernize` branch is merged or rebased, because it rewrites it too.

---

## Deviations from plan

_None yet._

---

## Open questions for Tyler

_None yet._

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
