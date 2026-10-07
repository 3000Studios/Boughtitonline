# BoughtItOnline Agent Rules

- Canonical repository: `3000Studios/Boughtitonline`; production branch: `main`; live store: `ath0bu-tg.myshopify.com`.
- Do not use GitHub Actions. Theme deployment is Shopifyâ€™s native GitHub theme integration connected to `main`.
- Before changing theme code, run `npm run theme:check`. Commit and push only validated changes. Verify exact deployed file contents and the custom domain before reporting a live update.
- Products, collections, pages, navigation, and theme settings require an installed Shopify app with least-privilege Admin API scopes. Do not claim these updates are possible until `npm run bridge:status` reports `CONNECTED`.
- Never print, commit, paste into chat, or share Shopify credentials. Do not publish a theme, modify checkout, or make bulk product changes without explicit owner authorization.
