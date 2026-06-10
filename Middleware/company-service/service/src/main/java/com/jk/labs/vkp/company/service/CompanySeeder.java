package com.jk.labs.vkp.company.service;

import com.jk.labs.vkp.company.common.enums.ResourceType;
import com.jk.labs.vkp.company.common.enums.Status;
import com.jk.labs.vkp.company.dao.entity.CompEntity;
import com.jk.labs.vkp.company.dao.entity.CompResourceEntity;
import com.jk.labs.vkp.company.dao.repository.CompRepository;
import com.jk.labs.vkp.company.dao.repository.CompResourceRepository;
import com.jk.labs.vkp.company.utils.IdGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * Seeds a default catalogue of vehicle manufacturers + their brand websites on startup.
 *
 * <p>The source list (github.com/kingjosephm/vehicle_make_model_dataset) is by <b>Make</b> (brand), so a
 * raw load would make all 59 brands "companies". That's wrong — most brands are owned by a parent company
 * or group. So each brand is mapped to its <b>real parent company</b> (e.g. Lexus + Scion → Toyota;
 * Jeep + Ram + Dodge + … → Stellantis; Audi + Porsche + Bentley + Lamborghini → VW Group), giving 24 actual
 * companies that cover all 59 brands. Each company also gets its active brands' official websites seeded as
 * {@code company_resources} (the root URLs the discovery/crawl pipeline starts from).
 *
 * <p>Idempotent &amp; additive: companies are inserted only when their name is not already present;
 * resources only when their host is not already present for that company — so it never duplicates or
 * overwrites existing rows (including the Liquibase 002 seed). Disable with
 * {@code vkp.seed.default-companies=false}. Defunct brands (Pontiac, Saturn, Saab, Mercury, Scion,
 * Plymouth, …) are kept on the company description but get no website. A few attributions are era-based
 * judgment calls (Saab + Daewoo → GM; Volvo + Polestar + Lotus → Geely).
 */
@Component
@ConditionalOnProperty(name = "vkp.seed.default-companies", matchIfMissing = true)
@RequiredArgsConstructor
@Slf4j
@Order(1)
public class CompanySeeder implements CommandLineRunner {

    private final CompRepository compRepo;
    private final CompResourceRepository resourceRepo;

    /** Each row = { parent company, brand, brand, … } — covers all 59 Makes in the dataset. */
    private static final String[][] COMPANIES = {
            {"Toyota", "Toyota", "Lexus", "Scion"},
            {"Honda", "Honda", "Acura"},
            {"Ford", "Ford", "Lincoln", "Mercury"},
            {"General Motors", "Chevrolet", "GMC", "Buick", "Cadillac", "Pontiac", "Saturn",
                    "Oldsmobile", "HUMMER", "Daewoo", "Saab"},
            {"Stellantis", "Jeep", "Ram", "Dodge", "Chrysler", "Fiat", "Alfa Romeo", "Maserati", "Plymouth"},
            {"Volkswagen Group", "Volkswagen", "Audi", "Porsche", "Bentley", "Lamborghini"},
            {"BMW", "BMW", "MINI", "Rolls-Royce"},
            {"Mercedes-Benz", "Mercedes-Benz", "Maybach", "smart"},
            {"Hyundai Motor Group", "Hyundai", "Kia", "Genesis"},
            {"Nissan", "Nissan", "INFINITI"},
            {"Geely", "Volvo", "Polestar", "Lotus"},
            {"Jaguar Land Rover", "Jaguar", "Land Rover"},
            {"Mazda", "Mazda"},
            {"Subaru", "Subaru"},
            {"Mitsubishi Motors", "Mitsubishi"},
            {"Suzuki", "Suzuki"},
            {"Isuzu", "Isuzu"},
            {"Tesla", "Tesla"},
            {"Rivian", "Rivian"},
            {"Fisker", "Fisker"},
            {"Ferrari", "Ferrari"},
            {"Aston Martin", "Aston Martin"},
            {"McLaren", "McLaren"},
            {"Panoz", "Panoz"},
    };

    /** Official website per ACTIVE brand. Defunct brands are intentionally absent. */
    private static final String[][] BRAND_SITES = {
            {"Toyota", "https://www.toyota.com"}, {"Lexus", "https://www.lexus.com"},
            {"Honda", "https://www.honda.com"}, {"Acura", "https://www.acura.com"},
            {"Ford", "https://www.ford.com"}, {"Lincoln", "https://www.lincoln.com"},
            {"Chevrolet", "https://www.chevrolet.com"}, {"GMC", "https://www.gmc.com"},
            {"Buick", "https://www.buick.com"}, {"Cadillac", "https://www.cadillac.com"},
            {"Jeep", "https://www.jeep.com"}, {"Ram", "https://www.ramtrucks.com"},
            {"Dodge", "https://www.dodge.com"}, {"Chrysler", "https://www.chrysler.com"},
            {"Fiat", "https://www.fiatusa.com"}, {"Alfa Romeo", "https://www.alfaromeousa.com"},
            {"Maserati", "https://www.maserati.com"},
            {"Volkswagen", "https://www.vw.com"}, {"Audi", "https://www.audiusa.com"},
            {"Porsche", "https://www.porsche.com"}, {"Bentley", "https://www.bentleymotors.com"},
            {"Lamborghini", "https://www.lamborghini.com"},
            {"BMW", "https://www.bmwusa.com"}, {"MINI", "https://www.miniusa.com"},
            {"Rolls-Royce", "https://www.rolls-roycemotorcars.com"},
            {"Mercedes-Benz", "https://www.mbusa.com"},
            {"Hyundai", "https://www.hyundaiusa.com"}, {"Kia", "https://www.kia.com"},
            {"Genesis", "https://www.genesis.com"},
            {"Nissan", "https://www.nissanusa.com"}, {"INFINITI", "https://www.infinitiusa.com"},
            {"Volvo", "https://www.volvocars.com"}, {"Polestar", "https://www.polestar.com"},
            {"Lotus", "https://www.lotuscars.com"},
            {"Jaguar", "https://www.jaguarusa.com"}, {"Land Rover", "https://www.landroverusa.com"},
            {"Mazda", "https://www.mazdausa.com"}, {"Subaru", "https://www.subaru.com"},
            {"Mitsubishi", "https://www.mitsubishicars.com"}, {"Suzuki", "https://www.globalsuzuki.com"},
            {"Isuzu", "https://www.isuzucv.com"},
            {"Tesla", "https://www.tesla.com"}, {"Rivian", "https://www.rivian.com"},
            {"Ferrari", "https://www.ferrari.com"}, {"Aston Martin", "https://www.astonmartin.com"},
            {"McLaren", "https://www.mclaren.com"}, {"Panoz", "https://www.panoz.com"},
    };

    private static final Map<String, String> SITE = new HashMap<>();

    static {
        for (String[] bs : BRAND_SITES) {
            SITE.put(bs[0].toLowerCase(), bs[1]);
        }
    }

    @Override
    public void run(String... args) {
        seedCompanies();
        seedResources();
    }

    private void seedCompanies() {
        Set<String> existing = new HashSet<>();
        compRepo.findAll().forEach(c -> {
            if (c.getName() != null) {
                existing.add(c.getName().trim().toLowerCase());
            }
        });
        Instant now = Instant.now();
        List<CompEntity> toAdd = new ArrayList<>();
        for (String[] row : COMPANIES) {
            String company = row[0];
            if (existing.contains(company.toLowerCase())) {
                continue;
            }
            String brands = String.join(", ", Arrays.copyOfRange(row, 1, row.length));
            String desc = "Vehicle manufacturer. Brands: " + brands + ".";
            toAdd.add(CompEntity.builder()
                    .companyId(IdGenerator.newId())
                    .name(company)
                    .description(desc.length() > 250 ? desc.substring(0, 250) : desc)
                    .status(Status.DEFAULT)
                    .createdDt(now).updatedDt(now)
                    .createdBy("system").updatedBy("system")
                    .build());
        }
        if (!toAdd.isEmpty()) {
            compRepo.saveAll(toAdd);
            log.info("Seeded {} default companies (additive; {} already present).", toAdd.size(), existing.size());
        }
    }

    private void seedResources() {
        // name -> companyId for the companies we know about
        Map<String, String> idByName = new HashMap<>();
        compRepo.findAll().forEach(c -> {
            if (c.getName() != null) {
                idByName.put(c.getName().trim().toLowerCase(), c.getCompanyId());
            }
        });
        Instant now = Instant.now();
        List<CompResourceEntity> toAdd = new ArrayList<>();
        for (String[] row : COMPANIES) {
            String companyId = idByName.get(row[0].toLowerCase());
            if (companyId == null) {
                continue;
            }
            Set<String> hosts = new HashSet<>();
            resourceRepo.findByCompanyId(companyId).forEach(r -> hosts.add(host(r.getResourceLink())));
            for (int i = 1; i < row.length; i++) {
                String brand = row[i];
                String url = SITE.get(brand.toLowerCase());
                if (url == null || hosts.contains(host(url))) {
                    continue;   // defunct brand, or this site already seeded for the company
                }
                hosts.add(host(url));
                toAdd.add(CompResourceEntity.builder()
                        .companyResourceId(IdGenerator.newId())
                        .companyId(companyId)
                        .resourceName(brand)
                        .resourceLink(url)
                        .resourceType(ResourceType.WEBSITE.name())
                        .status(Status.DEFAULT)
                        .createdDt(now).updatedDt(now)
                        .createdBy("system").updatedBy("system")
                        .build());
            }
        }
        if (toAdd.isEmpty()) {
            log.info("Default company resources already present — nothing to seed.");
            return;
        }
        resourceRepo.saveAll(toAdd);
        log.info("Seeded {} default brand-website resources across companies.", toAdd.size());
    }

    /** Bare host of a URL, lower-cased, without scheme / path / leading www. */
    private static String host(String url) {
        if (url == null) {
            return "";
        }
        String s = url.toLowerCase();
        int p = s.indexOf("://");
        if (p >= 0) {
            s = s.substring(p + 3);
        }
        int slash = s.indexOf('/');
        if (slash >= 0) {
            s = s.substring(0, slash);
        }
        return s.startsWith("www.") ? s.substring(4) : s;
    }
}
