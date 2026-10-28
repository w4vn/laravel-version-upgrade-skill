# Version path and runtime reference

**Edition / retrieval: 2026-10-26.** Official release notes identify Laravel **13** as the latest stable major. The newest released entry observed in the pinned 13.x framework changelog is **v13.38.0 (2026-10-20)**, followed by Unreleased. Re-check live official sources for every real upgrade; this is not a permanent latest-patch pin.

## Every required breaking-change hop

```text
5.0 → 5.1 → 5.2 → 5.3 → 5.4 → 5.5 → 5.6 → 5.7 → 5.8
    → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13
```

Start at the observed version. Laravel 5.x used breaking minor releases; do not jump 5.1→5.8 as a supposedly safe minor update. The suite covers 17 version lines / 16 boundaries. 4.x→5.0 is outside the requested execution scope even though the archived 5.0 guide also documents it.

## Historical framework PHP floors

The exact constraints below come from **initial release-tag** `laravel/framework/composer.json` snapshots, not from a generic blog table. They establish historical floors only. Later patch constraints, officially tested PHP ranges, root constraints and all locked dependencies determine the actual permitted runtime.

| Laravel line | Initial framework PHP constraint | Floor | Local official guide |
|---|---|---:|---|
| 5.0 | `>=5.4.0` | 5.4.0 | [5.0](official/5.0/upgrade.md) |
| 5.1, historic LTS | `>=5.5.9` | 5.5.9 | [5.1](official/5.1/upgrade.md) |
| 5.2 | `>=5.5.9` | 5.5.9 | [5.2](official/5.2/upgrade.md) |
| 5.3 | `>=5.6.4` | 5.6.4 | [5.3](official/5.3/upgrade.md) |
| 5.4 | `>=5.6.4` | 5.6.4 | [5.4](official/5.4/upgrade.md) |
| 5.5, historic LTS | `>=7.0` | 7.0.0 | [5.5](official/5.5/upgrade.md) |
| 5.6 | `^7.1.3` | 7.1.3 | [5.6](official/5.6/upgrade.md) |
| 5.7 | `^7.1.3` | 7.1.3 | [5.7](official/5.7/upgrade.md) |
| 5.8 | `^7.1.3` | 7.1.3 | [5.8](official/5.8/upgrade.md) |
| 6, historic LTS | `^7.2` | 7.2.0 | [6](official/6.x/upgrade.md) |
| 7 | `^7.2.5` | 7.2.5 | [7](official/7.x/upgrade.md) |
| 8 | `^7.3` | 7.3.0 | [8](official/8.x/upgrade.md) |
| 9 | `^8.0.2` | **8.0.2** | [9](official/9.x/upgrade.md) |
| 10 | `^8.1` | 8.1.0 | [10](official/10.x/upgrade.md) |
| 11 | `^8.2` | 8.2.0 | [11](official/11.x/upgrade.md) |
| 12 | `^8.2` | 8.2.0 | [12](official/12.x/upgrade.md) |
| 13 | `^8.3` | 8.3.0 | [13](official/13.x/upgrade.md) |

Laravel 10–13's initial manifests require `composer-runtime-api ^2.2`; Laravel 10's guide explicitly requires Composer ≥2.2.0. Every version folder also contains its exact initial `framework-composer.json`, release notes, and (where found) framework changelog. PHP 5-era extension requirements, including mcrypt in Laravel 5.0's runtime requirements, must be checked against the exact source artifact.

## Official support windows observed on the edition date

Sources: [8.x release notes](official/8.x/releases.md), [9.x release notes](official/9.x/releases.md), [13.x release notes](official/13.x/releases.md). “Supported PHP” is the documented framework range, **not** every patch's Composer constraint or a guarantee about application packages.

| Laravel | Documented PHP | Release | Bug fixes through | Security through | Status on 2026-10-26 |
|---|---|---|---|---|---|
| 8 | 7.3–8.1 | 2020-09-08 | 2022-07-26 | 2023-01-24 | EOL |
| 9 | 8.0–8.2 | 2022-02-08 | 2023-08-08 | 2024-02-06 | EOL |
| 10 | 8.1–8.3 | 2023-02-14 | 2024-08-06 | 2025-02-04 | EOL |
| 11 | 8.2–8.4 | 2024-03-12 | 2025-09-03 | 2026-03-12 | EOL |
| 12 | 8.2–8.5 | 2025-02-24 | 2026-08-13 | 2027-02-24 | Security fixes only |
| 13 | 8.3–8.5 | 2026-03-17 | Q3 2027 | 2028-03-17 | Active |

Laravel 5.x–7.x are also EOL. LTS in 5.1/5.5/6 is a **historical designation**, not continuing support. Laravel 9's broad release table says PHP 8.0, while the exact framework floor is 8.0.2; use the more precise constraint when solving.

## Framework-level runtime bridges — validate, do not copy blindly

The ranges below are framework-level overlaps, not app-ready runtime guarantees. Patch markers identify when the snapshots record added PHP support; also intersect the exact source and target patches, every locked package, root PHP constraint, required extensions/system libraries, Composer/plugins and test/deployment tooling before selecting a bridge.

| Hop | Documented framework runtime overlap | Candidate to investigate | Snapshot evidence and patch qualifiers |
|---|---|---|---|
| 5.8→6 | PHP 7.2–7.4 | PHP 7.4 | PHP 7.4 support was added in 5.8.35 ([5.8 changelog](official/5.8/framework-changelog.md)); the official 6 release table lists PHP 7.2–8.0 ([8.x release notes](official/8.x/releases.md)). Use 5.8.35 or later for the source side. |
| 6→7 | PHP 7.2.5–8.0 | PHP 7.4 | Full PHP 8.0 support appears in 6.20.0 and 7.29.0 ([6.x changelog](official/6.x/framework-changelog.md), [7.x changelog](official/7.x/framework-changelog.md)); use at least those patches for PHP 8.0. |
| 7→8 | PHP 7.3–8.0 | PHP 7.4 or PHP 8.0 | PHP 8.0 support appears in 8.12.0 ([8.x changelog](official/8.x/framework-changelog.md)); PHP 8.0 also requires 7.29.0 or later on the Laravel 7 side; a chain starting at Laravel 6 additionally needs 6.20.0 or later. |
| 8→9 | PHP 8.0.2–8.1 | PHP 8.1 | Laravel 9's exact initial floor is PHP 8.0.2 ([9 initial framework manifest](official/9.x/framework-composer.json)); Laravel 8 added PHP 8.1 support in 8.67.0 ([8.x changelog](official/8.x/framework-changelog.md)). Use 8.67.0 or later on the Laravel 8 side for PHP 8.1. |
| 9→10 | PHP 8.1–8.2 | PHP 8.2 if the selected lock supports it | Framework-level overlap; check exact patches and lock. |
| 10→11 | PHP 8.2–8.3 | PHP 8.3 | Framework-level overlap; check exact patches and lock. |
| 11→12 | PHP 8.2–8.4 | PHP 8.4 | Framework-level overlap; check exact patches and lock. |
| 12→13 | PHP 8.3–8.5 | PHP 8.4 or PHP 8.5 according to extensions, packages and deployment support | Framework-level overlap; check exact patches and lock. |

These are candidates to investigate, not tested plans. For hops before 5.8, derive exact patch intersections from source and target manifests plus the full lock; do not infer a universal PHP sequence from one successful upgrade. PHP 7.4, 8.0 and 8.1 are EOL and may be used only as temporary, isolated upgrade bridges—not as final deployment runtimes.

Current PHP support itself matters: as of the edition date PHP 8.0/8.1 are EOL; PHP 8.2 security support ends 2026-12-31, 8.3 ends 2027-12-31, 8.4 ends 2028-12-31, 8.5 ends 2029-12-31. Verify the live [PHP support table](https://www.php.net/supported-versions.php) before selecting a final runtime. No PHP minimum authorizes ignoring transitive requirements, missing extensions or vendor support.

See [runtime-and-dependencies.md](runtime-and-dependencies.md) for Composer/lock/platform handling and [sources.md](sources.md) for immutable provenance and updates.
