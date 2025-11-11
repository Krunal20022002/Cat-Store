-- author- Krunal Rajendra Shirsath

# Cat-Store 

- Cat-Store is a lightweight Flask demo app that models a simple storefront and gallery for cat products. It demonstrates server-rendered pages, basic user flows (register/login), a contact form, and simple persistence for users, products, and messages. It’s ideal as a learning project or starter prototype to extend.

Core ideas
- Presentation: Server-rendered templates deliver pages and reuse layout blocks.
- Application: Flask routes handle request validation, session state, and orchestration.
- Persistence: A small DB interface stores Users, Products, and Contacts; keep this abstract so the storage can change later.
- Static assets: CSS and JS provide styling and client-side UX; server-side validation remains authoritative.

Key features 
- Product listing and detail views (shop)
- Image gallery
- User registration and login
- Contact form and admin list of messages
- Minimal, extensible data models (User, Product, Contact)

Minimal conceptual data shapes
- Product: id, name, description, price, image path, stock
- User: id, name, email, password_hash, role flag
- Contact: id, name, email, message, timestamp

Common routes 
- Public: `/`, `/shop`, `/gallery`, `/register`, `/login`, `/contact`
- Admin: `/contacts`, users, plus product CRUD if added

Configuration & security 
- Use env vars for secrets (SECRET_KEY) and DB path.
- Hash passwords; enable CSRF for forms.
- Validate input server-side; escape output in templates.
- Protect admin routes with authorization checks.

Folder structure 
- app.py — app entry / routes
- database.py — DB helpers / model layer
- templates — Jinja2 templates (home, shop, gallery, register, login, contact, contacts, users)
- static
  - `css/` — styles
  - `js/` — client scripts
  - `images/` — product/gallery images
- Optional: `tests/`, `migrations/`, `docs/`, `Dockerfile`, `.github/workflows/`, `requirements.txt`, `CONTRIBUTING.md`, `LICENSE`

 

