/* js/17_viec_tiep_theo.js — UX1A-L1: thanh "Việc tiếp theo" (#viecTiepTheo) ở đầu <main>.

   Chỉ ĐỌC dữ liệu đã có (get_dashboard_status, get_data_health_report, get_em_chua_co_cho) và
   chọn ĐÚNG MỘT nút chính theo thứ tự: nạp sổ -> xem cảnh báo chặn -> chạy -> xử lý {person_l}
   chưa có {slot_l} -> xuất. Không ghi gì, không đổi thuật toán. Script thường (không ES module). */
"use strict";

let viecTiepTheoLanGoi = 0;
let viecTiepTheoHanhDong = null;

/* Chờ điều kiện đúng (tối đa ~3 giây) rồi chạy: các khối ở thẻ khác nạp bất đồng bộ sau khi đổi thẻ. */
function viecChoRoiLam(dieuKien, lam) {
  let lan = 0;
  const tick = () => {
    if (dieuKien()) { lam(); return; }
    if (++lan < 30) setTimeout(tick, 100);
  };
  tick();
}

function viecXuLyChuaCoCho() {
  switchTab("others");
  viecChoRoiLam(() => {
    const p = el("chuaCoChoPanel");
    return p && !p.hidden && mucDangDong;
  }, () => moMucVaCuon("chuaCoChoPanel"));
}

const VIEC_HANH_DONG = {
  nap_so: () => { switchTab("pipeline"); const o = el("dropZone"); o.scrollIntoView({ block: "center" }); o.focus(); },
  canh_bao: () => {
    switchTab("pipeline");
    const o = el("healthSummary");
    o.tabIndex = -1;
    o.scrollIntoView({ block: "center" });
    o.focus();
  },
  chay: () => { switchTab("pipeline"); el("btnRun").click(); },
  xu_ly: viecXuLyChuaCoCho,
  /* UX1A-L3: một lần bấm xuất luôn bằng tuỳ chọn mặc định của "Xuất kết quả (Excel)" (đạt mục tiêu 4 lần bấm);
     muốn tuỳ chọn khác thì mở "Tuỳ chọn khác" ngay bên dưới nút đó. */
  xuat: () => {
    switchTab("others");
    viecChoRoiLam(() => el("btnXuatTuyChon") && el("btnXuatTuyChon").offsetParent !== null && !el("btnXuatTuyChon").disabled, () => {
      const nut = el("btnXuatTuyChon");
      nut.scrollIntoView({ block: "center" });
      nut.click();
    });
  },
};

function viecTinhTrangThai(dash, suc, cho) {
  if (!dash.ok) return null;
  if (!dash.data.n_students || !dash.data.n_clubs) return { ten: "nap_so" };
  if (suc.ok && suc.data.n_high > 0) return { ten: "canh_bao" };
  if (!(dash.data.has_results || dash.data.n_matched > 0)) return { ten: "chay" };
  const n = cho.ok ? cho.data.so_em : 0;
  return n > 0 ? { ten: "xu_ly", n } : { ten: "xuat" };
}

function capNhatViecTiepTheo() {
  const khung = el("viecTiepTheo");
  if (!khung) return;
  const lan = ++viecTiepTheoLanGoi;
  Promise.all([
    callApi("get_dashboard_status"),
    callApi("get_data_health_report"),
    callApi("get_em_chua_co_cho"),
  ]).then(([dash, suc, cho]) => {
    if (lan !== viecTiepTheoLanGoi) return; /* có lần gọi mới hơn: bỏ kết quả cũ */
    const tt = viecTinhTrangThai(dash, suc, cho);
    if (!tt) { khung.hidden = true; return; }
    khung.hidden = false;
    khung.dataset.trangThai = tt.ten;
    khung.dataset.n = tt.n === undefined ? "" : String(tt.n);
    el("viecTiepTheoCau").textContent = t("ux1a_cau_" + tt.ten, { n: tt.n });
    el("viecTiepTheoNut").textContent = t("ux1a_nut_" + tt.ten, { n: tt.n });
    viecTiepTheoHanhDong = VIEC_HANH_DONG[tt.ten];
    /* Còn người chưa có chỗ vẫn tải được kết quả ngay (nút phụ, cùng hành động với trạng thái "xuất"). */
    const nut2 = el("viecTiepTheoNut2");
    if (nut2) nut2.hidden = tt.ten !== "xu_ly";
  });
}

function initViecTiepTheo() {
  const nut = el("viecTiepTheoNut");
  if (!nut) return;
  nut.addEventListener("click", () => { if (viecTiepTheoHanhDong) viecTiepTheoHanhDong(); });
  const nut2 = el("viecTiepTheoNut2");
  if (nut2) nut2.addEventListener("click", () => VIEC_HANH_DONG.xuat());
  window.addEventListener("langchange", capNhatViecTiepTheo);
  capNhatViecTiepTheo();
}
