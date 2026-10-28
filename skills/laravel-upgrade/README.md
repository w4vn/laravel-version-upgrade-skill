# Bộ skill nâng cấp Laravel 5.x → 13.x

**Edition: 2026-10-26.** Cài trong thư mục skills của agent (ví dụ `~/.claude/skills/` với Claude Code), dùng chung nhiều dự án. Đây là quy trình có lưu trạng thái và dữ liệu tham chiếu, không phải quyền tự chạy upgrade từ một yêu cầu audit. Việc cài/sửa skill không chạy ứng dụng, cài dependency hay deploy.

## Bốn entry point

| Skill | Công việc | Quyền mặc định |
|---|---|---|
| `/laravel-upgrade` | Audit và lập plan toàn tuyến, gom quyết định trước, in lệnh để người dùng copy | Chỉ đọc/lập plan; không đọc step skill để tự bắt đầu |
| `/laravel-upgrade-audit` | Framework/lock/runtime/package/test/integration và blocker | Chỉ đọc, không boot app |
| `/laravel-upgrade-step` | Một chặng hoặc dải liên tục như `5.8 -> 13` | Chỉ người dùng tự gọi; cần plan được duyệt và môi trường cô lập |
| `/laravel-upgrade-verify` | Đối chiếu baseline gốc, chặng trước, candidate; security và rollback | Review evidence; chỉ chạy gate khi được phép |

## Cách dùng chung

```text
/laravel-upgrade-audit /absolute/app/path 13
/laravel-upgrade /absolute/app/path 13 plan
```

Plan phải phủ tất cả chặng. Khi người dùng duyệt, lưu đúng nội dung đã duyệt ra file **ngoài repo**, mặc định `~/.claude/laravel-upgrade-notes/<project>/plan-<date>.md` hoặc vị trí họ chỉ định; không ghi đè phiên bản cũ. Resolve thành đường dẫn tuyệt đối, kiểm file tồn tại và tính SHA-256 rồi mới in lệnh có app path/range/**source-plan path tuyệt đối**. Plan chỉ nằm trong chat chưa sẵn sàng chạy. Người dùng tự copy gọi lệnh; model không tự load/invoke step để bỏ qua `disable-model-invocation: true`.

```text
# Một chặng; commit local chỉ khi đã được cho phép.
/laravel-upgrade-step /absolute/app/path "8 -> 9" "/absolute/private-notes/project/plan-2026-10-26.md"

# Dải liên tục; người dùng gọi lệnh này cho phép thực hiện các chặng đã duyệt
# và commit local mỗi chặng trong branch/worktree upgrade riêng.
/laravel-upgrade-step /absolute/app/path "5.8 -> 13" "/absolute/private-notes/project/plan-2026-10-26.md"

/laravel-upgrade-verify /absolute/app/path "B=<original> P=<previous> C=<candidate>" evidence-only
```

Các path và `<...>` trên là placeholder; command thực tế phải thay bằng file source đã lưu, dùng home path tuyệt đối chứ không in `~`. Người dùng tự gọi lệnh dải với đường dẫn đó là duyệt thực hiện đúng bytes của plan; lưu command/time/SHA-256 làm approval ban đầu. Step copy bytes vào `docs/upgrade/plan.md` và bản archive `docs/upgrade/plans/plan-v1.md` của worktree, xác minh hash bằng source. Mở phiên mới nếu command chưa hiện trong autocomplete; không cần sửa permissions/settings/hooks.

## Chạy dải liên tục và chạy tiếp

**Chuẩn bị trước một lần:** plan phải duyệt đầy đủ từng hop, PHP/Docker image và extension, package phải thay/bỏ và chặng bị chặn, policy session/CSRF/security, baseline reconciliation nếu có, và từng ngoại lệ Mức 1/2 được chấp nhận PARTIAL. Gom mọi câu hỏi còn thiếu thành một lượt trước khi bắt đầu. Dependency/tool/network chỉ trong phạm vi đã duyệt; không mount SSH/auth hay dùng dịch vụ thật ngầm.

**Workspace/Git:** tạo branch `upgrade/laravel-<x>-to-<y>` từ B trong **worktree riêng**, không checkout/sửa worktree người dùng. Với range đã gọi thủ công, đóng mỗi chặng bằng **một local commit** chứa code, lock, hop doc, README, ledger và run-state. Commit message theo quy định attribution của người dùng/dự án (ví dụ CLAUDE.md), không push, không PR, không deploy. Branch/path trùng có dữ liệu không được ghi đè hay reset để chạy lại.

**Vòng lặp:** thực hiện chặng → chạy gate → sửa regression trong scope nếu cần → ghi evidence/hop doc/ledger/state → commit đóng chặng → tự sang chặng kế tiếp. Chỉ nạp full guide của chặng hiện tại. Intermediate EOL versions chỉ là checkpoint trong môi trường cô lập, không phải đích deploy.

**Giới hạn 3 vòng:** tối đa **3 lượt gate tổng cộng mỗi chặng**, gồm lượt đầu. Lưu counter atomically trước mỗi lượt trong `docs/upgrade/run-state.json`; mất phiên/gọi lại/context nén không đặt lại. Hết 3 lượt còn lỗi thì dừng. Chỉ reset sau khi đã có can thiệp và người dùng **cho phép thử lại/reset rõ ràng**; lưu counter cũ, can thiệp, lý do và approval vào reset history, không tự xóa lịch sử.

**Điểm dừng cứng:** hết 3 vòng vẫn lỗi; cần quyết định chưa duyệt; security regression; truy cập dịch vụ thật ngoài dự kiến; lộ secret; schema phá hủy; mất evidence của B; hoặc state/worktree/lock/runtime không khớp mà chưa giải thích được. Báo chặng dừng và cần gì để tiếp tục, không đoán quyết định hay ghi secret vào report.

**Resume:** gọi lại **đúng lệnh cũ** từ cùng repository. Dùng `git worktree list` tìm workspace phù hợp; đọc run-state, plan, README, hop doc và ledger. Kiểm B/plan approval/hash/HEAD lineage/lock/image/dirty edits; chỉ bỏ qua chặng chứng minh đã có closure commit. Tiếp tục chặng chưa đóng, không tạo run mới, không đặt lại counter hoặc ghi đè worktree. Counter hết hạn cần approval reset sau can thiệp; stop vì security/dịch vụ thật/secret/B chỉ hết hiệu lực khi nguyên nhân đã được xử lý. State lưu trên upgrade worktree nên dùng tiếp được sau context compaction và phiên mới; đây không phải daemon tự hồi sinh khi process bị tắt.

**Tới target:** so sánh terminal C↔B, viết báo cáo tổng cùng khác biệt/PARTIAL, security/deployment/rollback limits trước commit chặng cuối. Nếu B không cài được và có B-reconciled đã duyệt, ghi đúng reference đã chạy; không mạo nhận direct-B hoặc production parity. Chỉ coi complete khi closure commit cuối được xác minh. Không tự push/PR/deploy.

**Đổi plan giữa chừng:** sau quyết định mới của người dùng, tạo source version mới (ví dụ `plan-<date>-v2.md`) và bản archive mới, giữ nguyên mọi bản cũ. Ghi reply nguyên văn nếu không nhạy cảm; nếu có secret/thông tin cá nhân thì chỉ ghi bản đã che và liệt kê phần bỏ. Append lịch sử `plan_versions` với source/copy path, SHA-256, thời điểm và decision ID; cập nhật active copy và `approved_plan` đúng bản mới nhất. Không sửa âm thầm, không reset counter và không viết lại approval của các hop đã đóng. Plan update không tự cho phép nới scope/security.

Khi resume bằng **lệnh cũ còn trỏ v1**, dùng nó xác định cùng run, nhưng kiểm source/archive/active copy theo phiên bản mới nhất đã duyệt (ví dụ v2). Approval ban đầu là invocation đã ghi; revision dựa vào reply/command thực của người dùng được lưu, không đòi hỏi chat cũ phải còn trong context. Hash không có record invocation/decision không phải approval. Chạy kiểm tra chỉ đọc dưới đây trước khi tiếp tục; file bị sửa mà thiếu history/approval hoặc copy không khớp sẽ bị BLOCKED. Schema cũ chỉ được migrate có duyệt, giữ nguyên progress/counter.

```bash
SKILL_DIR=~/.claude/skills/laravel-upgrade   # nơi đã cài skill laravel-upgrade
python3 -I "$SKILL_DIR"/scripts/check.py --run-state /absolute/upgrade-worktree/docs/upgrade/run-state.json --plan-source ~/.claude/laravel-upgrade-notes/project/plan-2026-10-26.md
```

Mẫu schema 2, history và recovery: [templates.md](references/templates.md). Helper chỉ kiểm tính nhất quán plan, không xác thực con người bằng mật mã hay thay việc kiểm Git/gate. Quy trình execution vẫn chỉ bắt đầu khi người dùng tự gọi step.

## Gate theo ba mức

| Mức | Khi nào bắt buộc | Nội dung |
|---|---|---|
| **0** | Mọi chặng | Validate manifest/lock và real platform; boot cô lập; diff route list B/P/C; toàn bộ test hiện có; HTTP smoke trang chính theo từng role trên DB fixture dùng xong bỏ |
| **1** | Tính năng audit đánh dấu quan trọng | Characterization auth/role, mail, PDF/export, storage, queue/schedule với cùng input B/P/C |
| **2** | Người phụ trách yêu cầu hoặc rủi ro cao | Pixel PDF, MIME đầy đủ, CSRF matrix mở rộng, backup/restore |

Khi hop thay đổi request-forgery middleware/policy, **CSRF tối thiểu là bắt buộc**: vài POST tiêu biểu, mọi `$except`, case token/origin bị từ chối phù hợp và một valid success control; qua middleware thật, không dùng testing bypass. Không bắt chạy toàn Cartesian matrix cho mọi hop.

Đủ Mức 0 + Mức 1 áp dụng + Mức 2 bắt buộc theo rủi ro, không regression: `VERIFIED IN <env>`. Thiếu đúng Mức 1/2 đã duyệt trước: **PARTIAL**, có thể tiếp tục theo approval. Thiếu Mức 0: **BLOCKED**, không tự đi tiếp. Thiếu bằng chứng không thành PASS; matching baseline failure không thành all-green suite; security regression không được waiver.

Với app ít test, bắt đầu bằng HTTP route/role snapshots, golden text mail/PDF và fixtures tổng hợp/cố định clock. Giữ test/harness chạy được trên PHPUnit 7.5/PHP 7.x và các bản sau bằng syntax tương thích hoặc adapter nhỏ; không bắt mọi app có ngay một bộ pixel/MIME exhaustive. Xem [verification.md](references/verification.md).

## Dữ liệu tham chiếu và cấu trúc

- **17 dòng phiên bản / 16 ranh giới:** 5.0 → 5.1 → … → 5.8 → 6 → … → 13; không bỏ minor 5.x có breaking changes.
- **69 snapshot ban đầu giữ nguyên**, không refresh. Thêm một snapshot source `TransformsRequest` tại tag v13.38.0 để đính chính giới hạn cumulative input keys **20 MiB / HTTP 413**, không có trong guide/changelog: tổng **70** entry, có commit/SHA-256/số byte trong [manifest](references/source-manifest.json).
- [versions](references/versions.md): PHP floors, overlap có điều kiện patch, support/EOL. [runtime/dependencies](references/runtime-and-dependencies.md): host một PHP vẫn dùng Docker đa bản, network resolve tách offline tests, package major tối đa/chặng bị chặn.
- [legacy](references/legacy-5-to-8.md), [modern](references/modern-9-to-13.md), [audit](references/audit.md), [verification](references/verification.md), [operations](references/operations.md), [templates](references/templates.md).
- [Community review](references/community-review.md): năm input, ý tưởng giữ lại, corrections và license. [Sources](references/sources.md): provenance và kiểm source tại tag khi guide/changelog thiếu thông tin.

```text
<thư mục skills>/          # ví dụ ~/.claude/skills/
├── laravel-upgrade/
│   ├── SKILL.md
│   ├── README.md
│   ├── references/              # Tài liệu chung, manifest, official snapshots
│   └── scripts/
│       ├── inventory.py         # Static/read-only, không boot app
│       ├── compare_junit.py     # XML comparison, không boot app
│       └── check.py             # Fixtures + integrity/link/privacy checks offline
├── laravel-upgrade-audit/SKILL.md
├── laravel-upgrade-step/SKILL.md
└── laravel-upgrade-verify/SKILL.md
```

Dữ liệu riêng của dự án lưu **ngoài skill** ở `~/.claude/laravel-upgrade-notes/`; không tự nạp vào mọi dự án, không đưa identity/path/HEAD lịch sử vào knowledge chung. Trạng thái execution thực sự nằm ở `docs/upgrade/` của upgrade worktree, không ở notes chung.

## Công cụ đi kèm — Python 3.9+, chỉ stdlib

```bash
SKILL_DIR=~/.claude/skills/laravel-upgrade   # nơi đã cài skill laravel-upgrade
python3 -I "$SKILL_DIR"/scripts/check.py
python3 -I "$SKILL_DIR"/scripts/inventory.py /absolute/app/path --scan --target 13 --brief
# Omit --brief for the full locked-package catalog (including advisory coverage).
python3 -I "$SKILL_DIR"/scripts/inventory.py /absolute/app/path --scan --target 13
python3 -I "$SKILL_DIR"/scripts/compare_junit.py baseline.xml candidate.xml
```

Inventory không chạy PHP/Composer/Artisan/network và không ghi dự án. Mỗi package có `framework_requirements` từ `require` của lock, dạng `{constraint_nguyên_văn: [illuminate/* hoặc laravel/framework]}`, gộp các constraint giống nhau; không tự suy ra major tối đa. `--brief` chỉ giữ package trực tiếp (cả dev), abandoned hoặc có framework requirements và báo số bị lược bỏ; không có cờ này thì vẫn giữ toàn bộ catalog. Audit lấy compatibility bản đang khóa từ lock trước; tra Packagist cho bản ứng viên và phải expand p2 metadata kế thừa đúng. Advisory chỉ đọc dùng Packagist API theo lô/ngày truy vấn, bao phủ catalog đầy đủ; không có kết quả vẫn là UNVERIFIED, không phải sạch. Xem [audit.md](references/audit.md). Có `lock_in_sync` true/false/null, locked/computed Composer content hashes; false là baseline-install blocker, true không chứng minh vendor hoặc production đúng. Chỉ so selected metadata theo Composer `Locker::getContentHash`; không thay `composer validate` hay giải constraint.

Quét app/routes/database/config/bootstrap/tests/resources/views và Modules/modules/packages nếu có, bỏ vendor/node_modules/generated bootstrap/cache. Mỗi pattern tối đa 12 ví dụ file:line; không in source tùy ý hay `.env`. Blade `or` chỉ quét khi Laravel locked < 5.7; che toàn bộ `{{-- … --}}` nhưng giữ offset/dòng. Runtime discovery sâu tối đa 3 cấp, có Docker/CI/deploy; chỉ nhận tên Compose YAML hợp lệ, không nhầm `composer.json`/`composer.lock`; Dockerfile chỉ emit dòng `FROM`. Regex có giới hạn, không phải PHP AST: helper/serialization/TTL và dynamic code cần review thủ công, không suy ra đã tương thích từ zero hints.

JUnit dùng khóa `classname::name`; với PHPUnit 4.x/5.x thiếu `classname`, dùng `class` và đổi namespace separator sang dấu chấm. `<warning>` là status, sau error/failure và trước skipped/pass. **Exit 0** nếu status/identity khớp; **1** nếu đổi status (kể cả pass↔warning) hoặc thiếu/thừa case; **2** nếu report lỗi/rỗng/duplicate/không dùng được. Assertion count chỉ INFO. Giữ CLI exits/warnings/risky/deprecation/incomplete riêng; comparator không boot app và không biến hai suite cùng lỗi thành PASS.

Self-check chỉ dùng fixtures tổng hợp; kiểm serializer/lock sync, scanner positive/negative/Blade comments, Compose không nhầm Composer, JUnit legacy/warning/exit codes và plan v2 có duyệt resume được nhưng sửa âm thầm bị chặn; cùng local source hashes, link/frontmatter/privacy. B vẫn được chạy lại ở mỗi chặng; chưa triển khai reuse evidence xuyên chặng. Không phải kiểm thử ứng dụng, execution-mode evaluation hoặc chứng nhận deployment. Không chạy thử range trên dự án thật chỉ để kiểm skill.

## Chuyển sang máy khác

Copy cả bốn thư mục sibling, giữ relative links và license/provenance; không ghi đè skill có sẵn chưa review. Chạy `check.py`, mở phiên mới. Có thể cài project-local `.claude/skills/` nếu đội muốn version-control; skill tự tìm script theo thư mục của nó. Không copy private notes sang phạm vi chưa được phép. Không sửa settings/permissions để tự mở rộng quyền.
