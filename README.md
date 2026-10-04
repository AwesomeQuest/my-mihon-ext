# mihon-ext-store

Personal [Mihon](https://mihon.app) extension store. Extensions are built and signed
locally; there is no CI.

## Add to Mihon

Settings → Browse → Extension store → Add:

```
https://github.com/AwesomeQuest/my-mihon-ext/raw/main/index.json
```

## Updating

1. Build the extension release with the signing key.
2. Replace the APK in this repository under a neutral, versioned file name and
   regenerate the index:

   ```bash
   python3 tools/make-index.py \
     --source-info <keiyoushi-source-info.json> \
     --apk <release.apk> \
     --apk-name tachiyomi-all.aq-v<version>.apk \
     --icon <icon.png>
   ```

3. Delete the previous APK, commit and push, then refresh the store in Mihon.

## Important

`signingkey.jks` and `signing.env` (git-ignored) must be kept somewhere safe:
extensions only install over an existing version when signed with the same key.
Never commit them.
