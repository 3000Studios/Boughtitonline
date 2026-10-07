# 3000 Studios Shopify storefront

Canonical source: `3000Studios/Boughtitonline`, production branch `main`.
Production domain: https://boughtitonline.com
Shopify store: `ath0bu-tg.myshopify.com`; live Horizon theme: `188515188815`.

## Local checks

Install the locked tools with `npm ci`, then run `npm run theme:check`.
Shopify compiles Liquid and JSON templates in its storefront runtime; there is no separate local production build or application type-check command.
Run `npm run bridge:status` to verify the existing private MUSE connection without printing credentials.

## Deployment

Commit and push validated changes to `main`. Deploy only the scoped theme files through Shopify; verify the exact file contents and the live custom domain on mobile and desktop. GitHub Actions is disabled. Automatic Shopify GitHub sync has not been verified for this theme.
`python scripts/current-store.py deploy --files templates/index.json sections/header-group.json sections/footer-group.json` deploys these exact committed files through Shopify, rejects dirty tracked files, verifies the configured store and live theme, checks remote checksums for concurrent edits, and reads each result back.
The private renewable client lives in the existing MUSE pipeline; set `MUSE_PIPELINE_ROOT` if that local pipeline moves. Credentials remain in its private owner-controlled configuration and never enter Git.

See [current-store-migration.md](docs/current-store-migration.md) for the source migration and rollback boundary.
