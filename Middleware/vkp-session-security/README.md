# vkp-session-security

A shared VKP **library** (a JAR, *not* a service). It gives every microservice a consistent way to
issue and read an **AES-256-GCM-encrypted session token**, and to transparently decrypt configured
encrypted request parameters — via a Spring auto-configured servlet filter.

## What it provides
- **`SessionCryptoService`** — `encrypt/decrypt` text and `issue/parse` a `SessionContext`
  (AES-256-GCM; tampered/wrong-key tokens fail to decrypt).
- **`Ids`** — `newSessionId()` / `newQueryId()`.
- **`SessionContext`** (`sessionId`, `userType` = GUEST|AUTH, `userId`, `issuedAt`) +
  **`SessionContextHolder`** (per-request access).
- **`SessionCryptoFilter`** (auto-registered) — reads the token from a header/param, decrypts it,
  exposes the `SessionContext`, and wraps the request so configured params are decrypted.

## Use it from a microservice
1. Add the dependency (after `mvn install` of this module):
   ```xml
   <dependency>
     <groupId>com.jk.labs.vkp</groupId>
     <artifactId>vkp-session-security</artifactId>
     <version>0.1.0</version>
   </dependency>
   ```
2. Configure (per service) — nothing else to wire; the filter auto-registers:
   ```yaml
   vkp:
     session:
       secret: ${VKP_SESSION_SECRET}     # base64 of a 32-byte AES-256 key (same across services)
       header: X-VKP-Session             # where the encrypted token arrives (default)
       param: sid                        # fallback param name
       encrypted-params: [companyId]     # request params whose VALUES arrive encrypted -> auto-decrypted
       required: false                   # set true to 401 requests without a valid token
   ```
3. Read it in code:
   ```java
   SessionContext ctx = SessionContextHolder.get();          // or @RequestAttribute("vkp.session")
   // @RequestParam("companyId") is already decrypted if listed in encrypted-params
   ```

## Generate a secret
```bash
openssl rand -base64 32      # use the same value for VKP_SESSION_SECRET in every service
```

> Token = `base64url( iv[12] || AES-256-GCM(ciphertext+tag) )`. GCM gives confidentiality + integrity,
> so the UI can hold the token but can't read or forge it. Without a configured secret a random
> **dev-only** key is generated (won't work across services/restarts).
