package com.jk.labs.vkp.security;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;

import java.util.ArrayList;
import java.util.List;

/** Per-service config (prefix {@code vkp.session}). */
@ConfigurationProperties(prefix = "vkp.session")
@Getter
@Setter
public class SessionSecurityProperties {

    /** Enable the auto-registered decrypt filter. */
    private boolean enabled = true;

    /** Base64 (standard) of a 32-byte AES-256 key. Blank => random dev key (DEV ONLY). */
    private String secret;

    /** Header that carries the encrypted session token. */
    private String header = "X-VKP-Session";

    /** Request param that carries the encrypted session token (fallback when the header is absent). */
    private String param = "sid";

    /** Request params whose VALUES arrive encrypted and should be transparently decrypted for controllers. */
    private List<String> encryptedParams = new ArrayList<>();

    /** Reject (401) requests that have no/invalid session token. Default off so adoption is incremental. */
    private boolean required = false;
}
