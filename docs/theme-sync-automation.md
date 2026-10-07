# Shopify theme deployment

Current target: ath0bu-tg.myshopify.com, Horizon 188515188815, boughtitonline.com, repository 3000Studios/Boughtitonline/main.

GitHub Actions is disabled. Automatic native Shopify GitHub integration is not verified for this live theme. Commit and push main, then use the guarded scoped Shopify deployment documented in README. Do not push the entire repository to Shopify: retained historical files are not live assets.

Verify deployed contents and the real domain before claiming completion. Revert the scoped commit or restore the preserved original configuration files for rollback.
