# NPM Publishing Setup Procedure

This document outlines the temporary manual steps required to enable our GitHub Actions CI to automatically publish new releases of the `koff` binary wrappers to NPM.

## 1. Generate an NPM Access Token
1. Log in to your NPM account at [npmjs.com](https://www.npmjs.com/).
2. Click on your profile picture in the top right corner and select **Access Tokens**.
3. Click on **Generate New Token** and select **Classic Token**.
4. Name the token (e.g., "koff-github-actions") and set the type to **Automation** (this allows the token to bypass 2FA for publishing, which is required for CI).
5. Click **Generate Token** and immediately copy the token. **Do not share this token.**

## 2. Store the Token in GitHub Secrets
1. Make sure you have the GitHub CLI (`gh`) installed and authenticated locally.
2. From the root of the `koff` repository, run:
   ```bash
   gh secret set NODE_AUTH_TOKEN
   ```
3. When prompted, paste the automation token you copied from NPM and press Enter.

## 3. Trigger a Release
The `.github/workflows/release.yml` workflow is configured to run automatically whenever a new Git tag is pushed (e.g., `v0.1.0`).

Once testing is complete, you can trigger a release by:
```bash
git tag v1.0.0
git push origin v1.0.0
```

The workflow will build the native PyApp binaries for all platforms and publish the wrapper packages to NPM using the `NODE_AUTH_TOKEN`.
