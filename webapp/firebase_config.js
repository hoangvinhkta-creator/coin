/* T-09B — cấu hình Firebase public client cho ETH DCA Tracker.
 *
 * Đây là "web app config" mà Firebase Console cấp (Project settings → Your apps → Web app).
 * Theo mô hình Firebase, các giá trị này KHÔNG phải secret: chúng nằm trong trang web mà mọi
 * trình duyệt tải về. Ranh giới bảo mật nằm ở Firebase Authentication + firestore.rules
 * (khoá cứng một owner UID), không nằm ở việc giấu apiKey. KHÔNG bao giờ đặt service account,
 * private key hay mật khẩu vào file này.
 *
 * Chủ dự án điền sau khi tạo project (xem webapp/README.md § Thiết lập Firebase), rồi chạy
 * `node webapp/build_app.js` và `firebase deploy`. Chừng nào còn giá trị "REQUIRED", app hiện
 * banner "CHƯA CẤU HÌNH FIREBASE" và KHÔNG ghi sổ (fail closed).
 *
 * `window.ETHDCA_FIREBASE_CONFIG || {...}`: nếu một script chạy TRƯỚC đã đặt config (test
 * harness trỏ vào Firebase Emulator Suite), giá trị đó được giữ; production không đặt trước
 * nên luôn dùng khối dưới đây.
 */
window.ETHDCA_FIREBASE_CONFIG = window.ETHDCA_FIREBASE_CONFIG || {
  apiKey: "AIzaSyDw6DL84PQHR7HUnqpupio778mIXkSMC9w",
  authDomain: "tinphatcontent.firebaseapp.com",
  projectId: "tinphatcontent",
  appId: "1:899674842478:web:ece1b9917e3ce9342b8d7f",
  // Sau bao lâu chưa có xác nhận từ máy chủ thì UI báo "CHƯA XÁC NHẬN" (ms). Lệnh ghi vẫn
  // tiếp tục chờ; khi máy chủ trả lời, trạng thái đổi sang "Đã lưu bền".
  ackTimeoutMs: 15000,
};
// LƯU Ý DÙNG CHUNG PROJECT (ghi tại phiên real-setup, 2026-09-02): project `tinphatcontent`
// KHÔNG dành riêng cho CoinDCA/ETH DCA OS — trước đó phục vụ một ứng dụng khác ("TinphatContent"
// / Content) và Firestore của project này đang có dữ liệu Content cũ. CoinDCA CHỈ được đọc/ghi
// namespace đã freeze `ethdca/state` + `ethdca/seed`. KHÔNG merge/mở rộng phạm vi qua namespace
// khác. `firestore.rules` PHẢI được merge an toàn với rules hiện có của Content trước khi
// deploy — xem cảnh báo ở đầu `firestore.rules` và `webapp/README.md` § Thiết lập Firebase.
