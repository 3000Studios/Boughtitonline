#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadEnv, getShopifyCredentials } from './lib/env.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
loadEnv();
loadEnv('C:\\Users\\MrJws\\OneDrive\\Workspaces\\global.env');

const creds = getShopifyCredentials();
const shop = creds.shop;
const themeId = creds.themeId || '181944025389';
const clientId = process.env.SHOPIFY_CLIENT_ID || process.env.SHOPIFY_API_KEY;
const clientSecret = process.env.SHOPIFY_CLIENT_SECRET || process.env.SHOPIFY_API_SECRET;

async function token() {
  if (creds.token && creds.token.startsWith('shpat_')) return creds.token;
  const res = await fetch(`https://${shop}/admin/oauth/access_token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'client_credentials',
      client_id: clientId,
      client_secret: clientSecret,
    }),
  });
  const json = await res.json();
  if (!json.access_token) {
    throw new Error(`token failed HTTP ${res.status} keys=${Object.keys(json).join(',')}`);
  }
  return json.access_token;
}

async function gql(tok, query, variables) {
  const res = await fetch(`https://${shop}/admin/api/${creds.apiVersion}/graphql.json`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Shopify-Access-Token': tok,
    },
    body: JSON.stringify({ query, variables }),
  });
  return res.json();
}

const files = [
  { filename: 'sections/td-flash.liquid', disk: path.join(root, 'sections', 'td-flash.liquid') },
  { filename: 'templates/index.json', disk: path.join(root, 'templates', 'index.json') },
];

const tok = await token();
const body = files.map((f) => ({
  filename: f.filename,
  body: { type: 'TEXT', value: fs.readFileSync(f.disk, 'utf8') },
}));

const result = await gql(
  tok,
  `mutation themeFilesUpsert($files: [OnlineStoreThemeFilesUpsertFileInput!]!, $themeId: ID!) {
    themeFilesUpsert(files: $files, themeId: $themeId) {
      upsertedThemeFiles { filename }
      userErrors { field message }
    }
  }`,
  { themeId: `gid://shopify/OnlineStoreTheme/${themeId}`, files: body },
);

if (result.errors) {
  console.error('graphql errors:', JSON.stringify(result.errors));
  process.exit(1);
}
const payload = result.data?.themeFilesUpsert;
console.log('upserted', (payload?.upsertedThemeFiles || []).map((f) => f.filename).join(', ') || '(none)');
if (payload?.userErrors?.length) {
  console.error('userErrors', JSON.stringify(payload.userErrors));
  process.exit(1);
}
