package com.jk.labs.vkp.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;

import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.util.Arrays;
import java.util.Base64;

/**
 * AES-256-GCM encrypt/decrypt of session tokens and configured request parameters.
 *
 * Token layout: base64url( iv[12] || ciphertext+tag ). GCM provides confidentiality AND integrity,
 * so a tampered token fails to decrypt. The key is a base64 32-byte secret (vkp.session.secret).
 */
@Slf4j
public class SessionCryptoService {

    private static final String ALGO = "AES/GCM/NoPadding";
    private static final int IV_LEN = 12;     // 96-bit nonce (recommended for GCM)
    private static final int TAG_BITS = 128;

    private final SecretKeySpec key;
    private final SecureRandom random = new SecureRandom();
    private final ObjectMapper mapper = new ObjectMapper();
    private final Base64.Encoder b64 = Base64.getUrlEncoder().withoutPadding();
    private final Base64.Decoder b64d = Base64.getUrlDecoder();

    public SessionCryptoService(String base64Secret) {
        byte[] k;
        if (base64Secret == null || base64Secret.isBlank()) {
            k = new byte[32];
            new SecureRandom().nextBytes(k);
            log.warn("vkp.session.secret not set — generated an EPHEMERAL AES-256 key (DEV ONLY; "
                    + "tokens won't survive a restart or work across services. Set a stable base64 32-byte key in prod).");
        } else {
            k = Base64.getDecoder().decode(base64Secret.trim());
            if (k.length != 32) {
                throw new IllegalArgumentException(
                        "vkp.session.secret must be base64 of exactly 32 bytes (AES-256); got " + k.length + " bytes");
            }
        }
        this.key = new SecretKeySpec(k, "AES");
    }

    /** Encrypt arbitrary text into an opaque base64url token. */
    public String encrypt(String plaintext) {
        try {
            byte[] iv = new byte[IV_LEN];
            random.nextBytes(iv);
            Cipher c = Cipher.getInstance(ALGO);
            c.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(TAG_BITS, iv));
            byte[] ct = c.doFinal(plaintext.getBytes(StandardCharsets.UTF_8));
            byte[] out = new byte[iv.length + ct.length];
            System.arraycopy(iv, 0, out, 0, iv.length);
            System.arraycopy(ct, 0, out, iv.length, ct.length);
            return b64.encodeToString(out);
        } catch (Exception e) {
            throw new SessionCryptoException("encrypt failed", e);
        }
    }

    /** Decrypt a token produced by {@link #encrypt}; throws if tampered or wrong key. */
    public String decrypt(String token) {
        try {
            byte[] in = b64d.decode(token);
            if (in.length <= IV_LEN) {
                throw new IllegalArgumentException("token too short");
            }
            byte[] iv = Arrays.copyOfRange(in, 0, IV_LEN);
            byte[] ct = Arrays.copyOfRange(in, IV_LEN, in.length);
            Cipher c = Cipher.getInstance(ALGO);
            c.init(Cipher.DECRYPT_MODE, key, new GCMParameterSpec(TAG_BITS, iv));
            return new String(c.doFinal(ct), StandardCharsets.UTF_8);
        } catch (Exception e) {
            throw new SessionCryptoException("decrypt failed", e);
        }
    }

    /** Issue an encrypted session token carrying the context (JSON inside the ciphertext). */
    public String issue(SessionContext ctx) {
        try {
            return encrypt(mapper.writeValueAsString(ctx));
        } catch (Exception e) {
            throw new SessionCryptoException("issue session token failed", e);
        }
    }

    /** Decrypt + parse a session token back into a {@link SessionContext}. */
    public SessionContext parse(String token) {
        try {
            return mapper.readValue(decrypt(token), SessionContext.class);
        } catch (SessionCryptoException e) {
            throw e;
        } catch (Exception e) {
            throw new SessionCryptoException("parse session token failed", e);
        }
    }
}
