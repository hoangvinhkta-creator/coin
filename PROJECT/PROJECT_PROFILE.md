# PROJECT PROFILE

Status:
ACTIVE

Selected Profile:
PRODUCT

Ngày chốt:
2026-08-23 (S000)

Người chốt:
Chủ dự án + agent phiên S000

## Bối cảnh dự án

Tên dự án:
ETH DCA Operating System — V2.1.5

Mục tiêu cuối của chủ dự án:
Một công cụ chạy trên trình duyệt, dùng như bảng tính, để theo dõi quá trình hold/trade coin
và phát cảnh báo dựa trên các chỉ báo phân tích đã được đặc tả trong bộ spec
(`docs/spec/01_PRODUCT_SPEC_V2_1_5.md` và `docs/spec/02_STRATEGY_SPEC_V2_1_5.md`).

Trạng thái hiện tại:
Đang build dở. Repo đã có backtest engine Python (`src/eth_dca_os/`, 26 module) và một bản
webapp prototype (`webapp/`). Chưa có phiên governance nào chạy trước S000.

Loại dự án:
LEGACY (theo nghĩa governance) — code đã tồn tại đáng kể và được viết TRƯỚC khi bộ governance
được đưa vào repo, nên chưa có bằng chứng tuân thủ nào được ghi nhận.

## Đánh giá đầu vào chọn profile

Team Size:
1 người (solo). Không có reviewer thứ hai là con người.

Project Maturity:
Prototype nghiên cứu đã hoàn chỉnh về mặt cơ chế, chưa có official run, chưa phát hành.

Production Data:
CÓ — dữ liệu giao dịch/danh mục/vốn thật của chủ dự án sẽ được nhập và lưu trong công cụ.
Đây là dữ liệu nghiệp vụ thật, không phải dữ liệu mẫu.

Personal/Customer Data:
KHÔNG có dữ liệu của bên thứ ba. Chỉ có dữ liệu tài chính cá nhân của chính chủ dự án.

Authentication:
Chưa có. Cần quyết định ở giai đoạn thiết kế app (xem `PROJECT/PROJECT_DECISIONS.md`).
Nếu app chạy hoàn toàn cục bộ trong trình duyệt thì auth có thể NOT_APPLICABLE, nhưng điều đó
phải được ghi nhận thành quyết định có lý do, không mặc định bỏ qua.

Financial / Pricing Sensitivity:
CAO — công cụ tính toán phân bổ vốn, P&L, và sinh cảnh báo ảnh hưởng tới quyết định xuống tiền
thật. Đây là "material financial calculation" theo `AGENT_CAPABILITY_MATRIX.md`, kích hoạt
hard floor tối thiểu Tier C và Effort tối thiểu `high` cho mọi task chạm vào lớp tính toán này.

External Users:
KHÔNG. Một người dùng duy nhất là chủ dự án.

Compliance / Legal:
Không có ràng buộc pháp lý/quy định bên ngoài được xác định.

CI/CD:
KHÔNG có. Đã kiểm tra: repo không có `.github/`, không có pipeline nào.

Staging:
KHÔNG có.

Backup:
KHÔNG có cơ chế backup nào cho dữ liệu người dùng. Đây là rủi ro đã được ghi nhận —
`results/` đang nằm trong `.gitignore` và dữ liệu app hiện lưu phía client.

Monitoring:
KHÔNG có.

Uncertainty Level:
CAO. Chưa có official run nên chưa có verdict; chưa biết chiến lược có vượt benchmark không.
Chưa có bằng chứng code khớp spec.

Expected Lifespan:
Dài hạn — công cụ phục vụ chiến lược tích lũy nhiều năm.

## Profile được chọn: PRODUCT

### Lý do chọn PRODUCT (không phải SOLO_LITE)

SOLO_LITE dành cho prototype, tiện ích nhỏ, "dự án không có dữ liệu production nhạy cảm".
Dự án này không thỏa điều kiện đó vì ba lý do:

1. **Dữ liệu nghiệp vụ thật.** Công cụ lưu lịch sử giao dịch và trạng thái vốn thật. Mất hoặc
   sai dữ liệu này là thiệt hại thật, không phải phiền toái. `RULE_PRECEDENCE.md` xếp Data
   Integrity ở hạng 2.
2. **Tính toán tài chính trọng yếu.** OSCORE, phân bổ vốn, ladder, P&L đều dẫn tới quyết định
   xuống tiền. Sai số ở đây có hậu quả vật chất.
3. **Đã tồn tại kỷ luật đặc tả ở mức PRODUCT.** Bộ spec V2.1.5 đã áp đặt precedence tài liệu,
   gate ngưỡng cứng, freeze rule, verdict — mức nghi thức này vượt xa SOLO_LITE. Hạ xuống
   SOLO_LITE sẽ mâu thuẫn với chính spec pack của dự án.

### Lý do KHÔNG chọn TEAM_PRODUCTION

Không có nhiều lập trình viên, không có quy trình phát hành chính thức, không có người dùng
bên ngoài, không có CI/CD. Áp TEAM_PRODUCTION sẽ tạo nghi thức không ai thực thi được, làm
governance thành hình thức. Các nhóm luật của TEAM_PRODUCTION được xếp vào CONDITIONAL bên dưới
và sẽ được kích hoạt riêng lẻ khi có nhu cầu thật.

### Lý do KHÔNG chọn AUDIT làm profile dự án

AUDIT là read-only và không dẫn tới sản phẩm. Mục tiêu cuối là xây công cụ, nên profile dự án
phải là PRODUCT.

**Tuy nhiên:** vì code hiện có được viết trước governance và chưa có bằng chứng tuân thủ,
phiên kế tiếp (S001) sẽ **chạy ở chế độ AUDIT read-only** theo
`governance/core/00_SESSION_ORCHESTRATION.md` mục "Large / Legacy Project".
Chế độ AUDIT là chế độ của phiên, không phải profile của dự án.
Trong S001 không được sửa code sản phẩm.

## Mandatory Governance

Kế thừa CORE + SOLO_LITE + PRODUCT theo `governance/core/PROJECT_PROFILE_STANDARD.md`.

CORE:
- `CLAUDE.md`
- `governance/core/00_SESSION_ORCHESTRATION.md`
- `governance/core/07_CODING_RULES.md`
- `governance/core/08_CHANGE_MANAGEMENT_RULES.md`
- `governance/core/09_TESTING_RULES.md`
- `governance/core/10_AI_AGENT_EXECUTION_PROTOCOL.md`
- `governance/core/11_FORBIDDEN_ACTIONS.md`
- `governance/core/RULE_PRECEDENCE.md`
- `governance/core/EVIDENCE_STANDARD.md`
- `governance/core/TASK_MODE_STANDARD.md`
- `governance/core/TASK_READY_GATE_STANDARD.md`
- `governance/core/TASK_COMPLETION_GATE_STANDARD.md`

Thêm từ SOLO_LITE:
- `governance/core/04_SECURITY_RULES.md`

Thêm từ PRODUCT:
- `governance/core/01_PROJECT_ARCHITECTURE_RULES.md`
- `governance/core/02_ROUTING_RULES.md`
- `governance/core/03_DATA_MODEL_RULES.md`
- `governance/core/05_BUSINESS_LOGIC_RULES.md`
- `governance/core/06_DATABASE_API_RULES.md`
- `governance/product/12_PRODUCT_REQUIREMENTS_RULES.md`
- `governance/product/13_ENVIRONMENT_CONFIGURATION.md`
- `governance/product/15_LOGGING_AUDIT_OBSERVABILITY.md`
- `governance/product/16_BACKUP_DISASTER_RECOVERY.md`
- `governance/product/17_DATA_GOVERNANCE_PRIVACY.md`
- `governance/core/PHASE_RELEASE_GATE_STANDARD.md`

Bổ sung bắt buộc riêng cho dự án này (do có chế độ AUDIT ở S001):
- `governance/audit/DISCOVERY_BASELINE_TEMPLATE.md`
- `governance/audit/AUDIT_FINDINGS_TEMPLATE.md`

Bổ sung bắt buộc do dự án có bộ spec riêng:
- `docs/spec/00_MASTER_INDEX_V2_1_5.md` quy định precedence giữa các tài liệu spec.
  Khi spec dự án và governance mâu thuẫn, xử lý theo `governance/core/RULE_PRECEDENCE.md`
  và ghi nhận bằng khối `RULE CONFLICT`; không tự ý chọn bên nào.

## Conditional Governance

Kích hoạt khi điều kiện tương ứng xuất hiện, không kích hoạt sẵn:

| Nhóm luật | Điều kiện kích hoạt |
|---|---|
| `governance/product/14_CI_CD_RELEASE_RULES.md` | Khi dựng CI hoặc có quy trình phát hành thật |
| `governance/product/18_INCIDENT_RESPONSE.md` | Khi công cụ được dùng vận hành thật và có sự cố mất/sai dữ liệu |
| `governance/product/19_DEPENDENCY_MANAGEMENT.md` | Khi app web bắt đầu dùng dependency ngoài |
| `governance/product/20_API_VERSIONING_COMPATIBILITY.md` | Khi có backend/API hoặc định dạng lưu trữ cần tương thích ngược |
| `governance/product/21_ACCESSIBILITY_UI_RULES.md` | Khi bước vào task giao diện (T-08 trở đi) |
| `governance/product/22_CODE_OWNERSHIP_REVIEW.md` | Khi có người thứ hai tham gia repo |
| `governance/product/23_DOCUMENTATION_STANDARDS.md` | Khi phát hành công cụ cho người khác dùng |
| `governance/reference/OPTIONAL_ENFORCEMENT_LAYER.md` | Khi có CI để gắn validator vào |

Lưu ý về `20_API_VERSIONING_COMPATIBILITY.md`: dù chưa có API, **định dạng file lưu dữ liệu
người dùng cũng là một hợp đồng cần tương thích ngược**. Nhóm luật này phải được kích hoạt ngay
khi T-08 chốt định dạng lưu trữ, không đợi đến khi có HTTP API.

## Not Applicable

| Nhóm | Lý do |
|---|---|
| Phân quyền theo vai trò (roles/permissions) | Một người dùng duy nhất, không có vai trò phân biệt |
| Quy trình review nhiều người | Solo. E2 được tạo bằng thủ tục "Solo Independent Review" trong `EVIDENCE_STANDARD.md`, lưu tại `docs/reviews/` |
| Tuân thủ pháp lý/quy định ngành | Không có ràng buộc được xác định |

Các mục NOT_APPLICABLE trên được ghi nhận có lý do theo yêu cầu của
`PROJECT_PROFILE_STANDARD.md`, không phải bỏ qua im lặng.

## Hệ quả bắt buộc của profile PRODUCT

1. **Evidence.** Mọi REQUIRED check thực thi được phải đạt tối thiểu E1. Check thuộc nhóm
   dữ liệu/tài chính nên tìm E2 qua phiên reviewer độc lập, lưu tại `docs/reviews/`.
2. **Routing.** Mọi task chạm lớp tính toán tài chính mang category `accounting_financial`,
   kéo theo hard floor Tier ≥ C và Effort ≥ `high`. Không được chọn Tier/Effort bằng cảm tính;
   phải tính bằng `governance/scripts/governance/routing_engine.py` và pass
   `validate_routing.py`.
3. **Backup/DR.** `16_BACKUP_DISASTER_RECOVERY.md` là bắt buộc. Công cụ không được phép
   phát hành khi chưa có đường xuất/nhập dữ liệu và cơ chế chống mất lịch sử giao dịch.
4. **Data model.** `03_DATA_MODEL_RULES.md` bắt buộc; schema phải bám
   `docs/spec/04_DATA_MODEL_V2_1_5.md`.

## Provider Mapping (xác nhận tại S000)

Theo `AGENT_CAPABILITY_MATRIX.md`, mapping mặc định được xác nhận còn hiệu lực trong phiên này:

| Tier | Model class | Khả dụng |
|---|---|---|
| A | Haiku | Có |
| B | Sonnet | Có |
| C | Opus | Có |
| D | Fable | Có |

Effort levels khả dụng: `low`, `medium`, `high`, `xhigh`, `max`.

## Justification (tóm tắt)

Dự án lưu dữ liệu tài chính thật của một người dùng, thực hiện tính toán ảnh hưởng tới quyết định
xuống tiền, và đã tự áp một bộ spec có gate và precedence ở mức PRODUCT. Nhưng dự án không có
đội ngũ, CI, staging hay người dùng ngoài để biện minh cho TEAM_PRODUCTION. PRODUCT là mức
tương xứng: đủ kỷ luật về dữ liệu, tính toán nghiệp vụ và sao lưu, mà không tạo nghi thức
không thể thực thi bởi một người.
