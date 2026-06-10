package com.jk.labs.vkp.company.service;

import com.jk.labs.vkp.company.common.enums.Status;
import com.jk.labs.vkp.company.dao.entity.CompEntity;
import com.jk.labs.vkp.company.dao.repository.CompRepository;
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
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * Seeds a default catalogue of vehicle manufacturers on startup.
 *
 * <p>The source list (github.com/kingjosephm/vehicle_make_model_dataset) is by <b>Make</b> (brand), so a
 * raw load would make all 59 brands "companies". That's wrong — most brands are owned by a parent company
 * or group. So each brand is mapped to its <b>real parent company</b> (e.g. Lexus + Scion → Toyota;
 * Jeep + Ram + Dodge + Chrysler + Fiat + … → Stellantis; Audi + Porsche + Bentley + Lamborghini → VW Group),
 * giving 24 actual companies that cover all 59 brands.
 *
 * <p>Idempotent &amp; additive: it inserts only the default companies whose name is not already present
 * (case-insensitive), so existing companies are never duplicated or overwritten. Disable with
 * {@code vkp.seed.default-companies=false}. A few attributions are era-based judgment calls
 * (Saab + Daewoo → GM; Volvo + Polestar + Lotus → Geely; Maybach + smart → Mercedes-Benz).
 */
@Component
@ConditionalOnProperty(name = "vkp.seed.default-companies", matchIfMissing = true)
@RequiredArgsConstructor
@Slf4j
@Order(1)
public class CompanySeeder implements CommandLineRunner {

    private final CompRepository repo;

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

    @Override
    public void run(String... args) {
        Set<String> existing = new HashSet<>();
        repo.findAll().forEach(c -> {
            if (c.getName() != null) {
                existing.add(c.getName().trim().toLowerCase());
            }
        });

        Instant now = Instant.now();
        List<CompEntity> toAdd = new ArrayList<>();
        for (String[] row : COMPANIES) {
            String company = row[0];
            if (existing.contains(company.toLowerCase())) {
                continue;   // keep the existing one — never duplicate or overwrite
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

        if (toAdd.isEmpty()) {
            log.info("Default companies already present ({} total) — nothing to seed.", existing.size());
            return;
        }
        repo.saveAll(toAdd);
        log.info("Seeded {} default vehicle companies (additive; {} already present).",
                toAdd.size(), existing.size());
    }
}
