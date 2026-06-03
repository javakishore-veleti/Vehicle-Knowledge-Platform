package com.jk.labs.vkp.indexing.common.dto.admin;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** Credential summary — config (secrets) is intentionally omitted from listings. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CredentialDTO {

    private String providerCredentialId;
    private String providerType;
    private String name;
    private String status;
}
