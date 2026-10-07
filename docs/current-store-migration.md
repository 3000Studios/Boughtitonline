# Current store source migration - 2026-10-07

The repository previously targeted knkxfs-xd.myshopify.com / 181944025389. Live Shopify and the custom domain verified ath0bu-tg.myshopify.com / Horizon 188515188815 instead.

The 486-file Shopify snapshot is preserved outside the repository in the local store-build audit. Only native theme directories were synchronized into this repository. Existing files absent from the live theme were retained and are not included in deployment. Shopify-sourced AGENTS.md was excluded; repository instructions remain owner-controlled.

This source synchronization accounts for the broad vendor-theme diff. It mirrors existing production, rather than deploying those vendor changes. The storefront change is restricted to templates/index.json, sections/header-group.json and sections/footer-group.json: readable bundle hero, separate instrumentals/merch grids, relevant CTAs, existing WELCOME10 announcement. Product prices, rights, fulfillment, customer data, billing and policies are not changed by this theme deployment.

Native GitHub sync is not verified on the current published theme. Deployment uses scoped Shopify Admin theme-file updates after main is pushed, with content readback and browser QA. No GitHub Actions, competing repository, production branch or theme is created.

Rollback: restore the three original configuration files from the preserved local snapshot through Shopify, or revert the homepage change and deploy only those files. The source migration does not require a wholesale live-theme push.

Digital delivery: the Digital Products app shows sixteen files attached to the USD 49 bundle, one file per single/pack. This is attachment verification, not a paid test purchase.

Eight Thunder Dome mockups and print designs are accessible in the owner-supplied Drive folder. A mockup is not fulfillment setup; supplier costs, variants, shipping and billing must be verified before publication.
