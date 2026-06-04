package com.jk.labs.vkp.security;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletRequestWrapper;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;

/**
 * Transparently decrypts the configured encrypted request parameters, so a controller reading
 * {@code @RequestParam("X")} gets the plaintext without knowing the value arrived encrypted.
 * Non-configured params pass through unchanged; a value that fails to decrypt passes through as-is.
 */
public class DecryptingRequestWrapper extends HttpServletRequestWrapper {

    private final SessionCryptoService crypto;
    private final Set<String> encryptedParams;

    public DecryptingRequestWrapper(HttpServletRequest request, SessionCryptoService crypto, Set<String> encryptedParams) {
        super(request);
        this.crypto = crypto;
        this.encryptedParams = encryptedParams;
    }

    private String maybeDecrypt(String name, String value) {
        if (value == null || !encryptedParams.contains(name)) {
            return value;
        }
        try {
            return crypto.decrypt(value);
        } catch (RuntimeException e) {
            return value;   // not encrypted / wrong key -> leave as-is
        }
    }

    @Override
    public String getParameter(String name) {
        return maybeDecrypt(name, super.getParameter(name));
    }

    @Override
    public String[] getParameterValues(String name) {
        String[] values = super.getParameterValues(name);
        if (values == null || !encryptedParams.contains(name)) {
            return values;
        }
        String[] out = new String[values.length];
        for (int i = 0; i < values.length; i++) {
            out[i] = maybeDecrypt(name, values[i]);
        }
        return out;
    }

    @Override
    public Map<String, String[]> getParameterMap() {
        Map<String, String[]> map = new LinkedHashMap<>(super.getParameterMap());
        for (String p : encryptedParams) {
            if (map.containsKey(p)) {
                map.put(p, getParameterValues(p));
            }
        }
        return Collections.unmodifiableMap(map);
    }
}
