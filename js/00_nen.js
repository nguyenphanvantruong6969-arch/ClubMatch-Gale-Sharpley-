/* ==========================================================================
   Giao diện chính (js/00_nen.js … js/08_khoi_dong.js) — logic frontend cho kiosk Phân bổ Câu lạc bộ (RB-DA)
   ==========================================================================
   Toàn bộ giao tiếp với Python đi qua window.pywebview.api.<ten_ham>(...),
   mỗi hàm trả về Promise<{ok, data, errors}> (quy ước thống nhất ở api.py).
   Không dùng alert()/confirm() ở bất cứ đâu — thay bằng toast + xác nhận
   2 bước ngay tại chỗ (đổi label nút, yêu cầu bấm lần 2).

   Song ngữ (vi/en): mọi chuỗi hiển thị đi qua I18N.t(key, params) (xem
   i18n.js) — không hardcode chuỗi tiếng Việt/Anh trực tiếp trong file
   này. Lỗi/chi tiết bước từ backend là {code, params} (xem api.py +
   i18n_errors.py) và được dịch bằng I18N.translateError(s).
   ========================================================================== */

/* js/00_nen.js — Nền: t()/lỗi dùng chung, gọi API (mới nhất / dùng chung), thông báo,
   nút bận, trợ năng cho phần tử bấm được.

   Một phần của giao diện chính, tách từ app.js cũ. Các tệp js/ là SCRIPT
   THƯỜNG (không phải ES module) nạp theo đúng thứ tự trong index.html và
   dùng chung một phạm vi — như một tệp duy nhất trước đây. Không dùng ES
   module vì mở trang bằng file:// thì trình duyệt chặn chúng.
*/
"use strict";

const t = window.I18N.t;
const trErr = window.I18N.translateError;
const trErrs = window.I18N.translateErrors;

/* ------------------------------------------------------------------ *
 * 0. TIỆN ÍCH DÙNG CHUNG
 * ------------------------------------------------------------------ */

const { apiSanSang, callApi, armTwoStepConfirm, nhaMoiNutXacNhan, choBackend } = window.RBDA;

/* Ma NOI BO cua "buoi mac dinh" (truong chi co mot buoi, hoac CLB chua
   khai buoi) — trung voi BUOI_MAC_DINH o rbda_priority_pipeline.py. Khong
   phai chu de doc: hien len man hinh thi luon qua nhanBuoi(). */
const BUOI_MAC_DINH = "__mac_dinh__";

/* Hai noi cung doc mot bao cao NGAY CUNG LUC (vd mo tab Quan ly: bang
   tai theo buoi va lich tuan deu can get_tai_theo_buoi) thi dung chung
   MOT yeu cau dang bay, khong gui hai lan. Chi dung cho ham DOC: xong la
   bo, lan goi sau van lay du lieu moi. */
const dangBayChung = {};
function callApiDocChung(name, ...args) {
  const khoa = name + JSON.stringify(args);
  if (!dangBayChung[khoa]) {
    dangBayChung[khoa] = callApi(name, ...args).finally(() => {
      delete dangBayChung[khoa];
    });
  }
  return dangBayChung[khoa];
}

/* Goi API ma CHI lan goi moi nhat tren cung `kenh` duoc tra ket qua.

   O tim kiem go tung chu, moi lan dung tay gui mot yeu cau. Tra ve
   KHONG theo thu tu gui: yeu cau cho "Ng" den SAU yeu cau cho "Nguyen"
   thi bang hien ket qua cua "Ng" duoi o dang ghi "Nguyen". Bam nhanh
   hai hoc sinh cung vay — nguoi dung dang nhin em thu hai ma man hinh
   lai do du lieu em thu nhat. Lan goi cu tra ve thi bi bo qua: Promise
   khong bao gio xong, nen doan `.then` phia sau khong chay. */
const luotGoiMoiNhat = {};
function callApiMoiNhat(kenh, name, ...args) {
  const luot = (luotGoiMoiNhat[kenh] = (luotGoiMoiNhat[kenh] || 0) + 1);
  return callApi(name, ...args).then((res) =>
    luot === luotGoiMoiNhat[kenh] ? res : new Promise(() => {}));
}

function el(id) {
  return document.getElementById(id);
}

/* Gio dang may "2026-11-03T03:18:45" -> "03/11/2026 03:18" (T3-08). Khong khop thi giu nguyen. */
function dinhDangGio(s) {
  const m = /^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})/.exec(String(s || ""));
  return m ? m[3] + "/" + m[2] + "/" + m[1] + " " + m[4] + ":" + m[5] : String(s || "");
}

/* Mot cau loi hien cho nguoi dung tu danh sach loi cua backend. Truoc day
   cung mot bieu thuc `t(khoa, { errors: trErrs(x).join("; ") })` duoc
   viet lai o 14 cho. */
/* Nhan "Dien trung tuyen" — hai bang ket qua tung tu viet lai phep nay. */
function nhanDien(tier) {
  return tier === "reserve" ? t("tier_reserve") : tier === "general" ? t("tier_general") : "—";
}

/* Loi JS trong mot `.then` nao do truoc day chi nam trong console — ma
   ban dong goi khong co console. Nguoi dung thay nut khong phan ung va
   khong biet vi sao. Hien no ra thanh thong bao. */
window.addEventListener("unhandledrejection", (ev) => {
  console.error(ev.reason);
  showToast(t("loi_giao_dien_ngoai_du_kien"), "error",
    [{ code: "loi_giao_dien_ngoai_du_kien", params: { detail: String(ev.reason) } }]);
});

/* UX2-L1 (#2 + #13): MOT cho dat/bo trang thai "dang ban" cho nut — dung chung cho chayNut, khiBan va btnRun
   (capNhatKhoaVanHanh). KHONG khoa `disabled` (nguoi goi tu khoa, vi btnRun con nhieu co khoa khac).
   bat=true: giu cac nut con that (icon khong mat), khoa min-width o be rong hien tai (nut khong nhay),
   thay noi dung bang <span.ux2-xoay aria-hidden> + nhan t(khoaNhan), aria-busy="true", lop is-ban.
   bat=false: tra nut con that; neu noi dung da bi viet lai giua chung (doi ngon ngu, khiXong tu doi nhan) thi
   KHONG ghi de. Goi lap lai khi dang ban chi lam moi nhan. */
function datNutBan(nut, bat, khoaNhan) {
  if (!nut) return;
  const trang = nut.__ux2Ban;
  if (bat) {
    goDauXong(nut);
    const khoa = khoaNhan || "dang_xu_ly";
    const chu = t(khoa);
    if (trang) {
      trang.khoa = khoa;
      if (trang.chu.parentNode === nut) trang.chu.textContent = chu;
      return;
    }
    const rong = nut.offsetWidth /* bo qua transform (:active scale) */;
    const xoay = document.createElement("span");
    xoay.className = "ux2-xoay";
    xoay.setAttribute("aria-hidden", "true");
    const nhan = document.createElement("span");
    nhan.className = "ux2-nhan-ban";
    nhan.textContent = chu;
    nut.__ux2Ban = { con: Array.from(nut.childNodes), xoay, chu: nhan, khoa, minGoc: nut.style.minWidth };
    if (rong > 0) nut.style.minWidth = Math.ceil(rong) + "px";
    while (nut.firstChild) nut.removeChild(nut.firstChild);
    nut.append(xoay, nhan);
    nut.setAttribute("aria-busy", "true");
    nut.classList.add("is-ban");
    return;
  }
  if (!trang) return;
  if (trang.xoay.parentNode === nut && trang.chu.parentNode === nut) {
    while (nut.firstChild) nut.removeChild(nut.firstChild);
    const kd = nut.getAttribute("data-i18n");
    if (kd) nut.textContent = t(kd); /* nhan tinh: tra theo ngon ngu HIEN TAI (co the da doi luc dang ban) */
    else {
      trang.con.forEach((n) => nut.appendChild(n));
      /* nut con tach roi khoi DOM luc ban nen applyStaticText bo qua: dich lai cac con [data-i18n] */
      nut.querySelectorAll("[data-i18n]").forEach((c) => { c.textContent = t(c.getAttribute("data-i18n")); });
    }
  }
  nut.style.minWidth = trang.minGoc;
  nut.setAttribute("aria-busy", "false");
  nut.classList.remove("is-ban");
  delete nut.__ux2Ban;
}

/* UX2-L2 (#3): dau ✓ tren CHINH nut vua luu/xuat xong (thanh cong, khong phai loi). La TRANG THAI, khong phai
   chuyen dong: van hien khi tat hieu ung (chi hieu ung hien dan moi tat). ~1,2 s roi go, min-width khoa de nut khong nhay.
   Dung lai khi dang ban (datNutBan(true) go ✓ truoc) va khi doi ngon ngu (applyStaticText ghi de noi dung -> ✓ mat, don dep van chay). */
const UX2_XONG_MS = 1200;

function goDauXong(nut) {
  const x = nut && nut.__ux2Xong;
  if (!x) return;
  clearTimeout(x.hen);
  if (x.dau.parentNode) x.dau.parentNode.removeChild(x.dau);
  nut.style.minWidth = x.minGoc;
  nut.classList.remove("is-xong");
  delete nut.__ux2Xong;
}

function nutDaXong(nut) {
  if (!nut || nut.__ux2Ban) return;
  goDauXong(nut);
  const dau = document.createElement("span");
  dau.className = "ux2-xong";
  dau.setAttribute("aria-hidden", "true");
  dau.textContent = "\u2713";
  const rong = nut.offsetWidth /* bo qua transform (:active scale) */;
  const x = { dau, minGoc: nut.style.minWidth, hen: 0 };
  if (rong > 0) nut.style.minWidth = Math.ceil(rong) + "px";
  nut.insertBefore(dau, nut.firstChild);
  nut.classList.add("is-xong");
  x.hen = setTimeout(() => goDauXong(nut), UX2_XONG_MS);
  nut.__ux2Xong = x;
}

/* Doi ngon ngu luc nut dang ban: nhan ban theo ngon ngu moi (nut khong co data-i18n khong qua applyStaticText). */
window.addEventListener("langchange", () => {
  document.querySelectorAll(".is-ban").forEach((n) => {
    const tr = n.__ux2Ban;
    if (tr && tr.chu.parentNode === n) tr.chu.textContent = t(tr.khoa);
  });
});

/* Khoa nut trong luc yeu cau dang chay, MO LAI du yeu cau thanh cong,
   that bai hay nem loi.

   Truoc day cac nut luu/xuat khong khoa: bam dup "Xuat" ra hai tep, bam
   dup "Luu diem" gui hai lan. Con nut nao tu khoa thi chi mo lai o
   nhanh thanh cong — mot loi JS giua chung la nut xam vinh vien, phai
   tat app mo lai. Nut dang khoa thi bo qua lan bam (tra Promise khong
   bao gio xong, doan `.then` phia sau khong chay). */
function khiBan(nut, taoPromise, tuyChon) {
  if (!nut || nut.disabled) return new Promise(() => {});
  const tc = tuyChon || {};
  let ket;
  nut.disabled = true;
  datNutBan(nut, true);
  return Promise.resolve()
    .then(taoPromise)
    .then((r) => { ket = r; return r; })
    .finally(() => {
      datNutBan(nut, false);
      nut.disabled = false;
      if (tc.xongKhi && ket !== undefined && tc.xongKhi(ket)) nutDaXong(nut);
    });
}

/* SG-9: MOT cho cho moi lan goi API. Truoc day ~68 cho viet `callApi(..).then(..)` tran: loi JS trong
   `.then` khong ai bat, nut co the xam mai, bam dup gui hai lan.
   - baoLoiGiaoDien: mot thong bao loi chung (cung cau voi `unhandledrejection` o tren).
   - chayTai(promise, khiXong): tai/lam moi KHONG do nut bam. Loi (API hay trong khiXong) -> thong bao loi,
     khong nem tiep; tra Promise luon xong (gia tri cua khiXong, hoac undefined khi loi).
   - chayNut(nut, taoPromise, khiXong, tuyChon): nut bam. Khoa nut + nhan "Dang..." (chi the <button>, chi xoa
     nhan neu khiXong khong tu doi), loi -> thong bao, `finally` mo lai nut + tra nhan. Nut dang khoa thi
     bo qua lan bam (Promise khong bao gio xong) nen bam dup chi goi API MOT lan.
     Mac dinh nut mo lai ngay khi API tra ve (truoc khiXong, nhu khiBan: khiXong co the khoa nut lai).
     tuyChon.nhan = khoa i18n cua nhan ban ("dang_xu_ly"); tuyChon.giuDenKhiXong = true: giu khoa den het khiXong;
     tuyChon.sauCung: ham chay trong `finally`; tuyChon.xongKhi(ketQua) -> true: hien dau ✓ tren nut (UX2-L2, nutDaXong). */
function baoLoiGiaoDien(loi) {
  console.error(loi);
  showToast(t("loi_giao_dien_ngoai_du_kien"), "error",
    [{ code: "loi_giao_dien_ngoai_du_kien", params: { detail: String(loi) } }]);
}

function chayTai(promise, khiXong) {
  return Promise.resolve(promise).then(khiXong).catch(baoLoiGiaoDien);
}

function noiTiep(...cacHam) {
  return cacHam.reduce((p, f) => p.then(() => f()), Promise.resolve());
}

function chayNut(nut, taoPromise, khiXong, tuyChon) {
  if (!nut || nut.disabled) return new Promise(() => {});
  const tc = tuyChon || {};
  const laNutBam = nut.tagName === "BUTTON";
  nut.disabled = true;
  if (laNutBam) datNutBan(nut, true, tc.nhan);
  let ket;
  const khoi = () => {
    if (laNutBam) datNutBan(nut, false);
    nut.disabled = false;
    /* UX2-L2: tuyChon.xongKhi(ketQua) -> true thi hien ✓ tren nut (khong khi API ne loi / tra {ok:false}). */
    if (laNutBam && tc.xongKhi && ket !== undefined && tc.xongKhi(ket)) nutDaXong(nut);
    if (tc.sauCung) tc.sauCung();
  };
  const goi = Promise.resolve().then(taoPromise).then((r) => { ket = r; return r; });
  if (tc.giuDenKhiXong) return goi.then(khiXong).catch(baoLoiGiaoDien).finally(khoi);
  return goi.finally(khoi).then(khiXong).catch(baoLoiGiaoDien);
}

/* Bien mot <div> bam duoc thanh thu ban phim dung duoc: Tab toi duoc,
   Enter/Space kich hoat, va trinh doc man hinh biet no la gi. Truoc day
   ca tab Nhap tai cho chi dung duoc bang chuot. `laOTick`: o tick bat/tat
   (class is-checked) — dong bo aria-checked sau MOI lan bam. */
function choBamDuoc(elm, laOTick) {
  elm.tabIndex = 0;
  elm.setAttribute("role", laOTick ? "checkbox" : "button");
  const dongBo = () => {
    if (laOTick) elm.setAttribute("aria-checked", String(elm.classList.contains("is-checked")));
  };
  dongBo();
  elm.addEventListener("click", dongBo);
  elm.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter" || ev.key === " ") {
      ev.preventDefault();
      elm.click();
    }
  });
}

function clear(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
}

/* SG-7 (H4, M1) — MỘT luật cho mọi danh sách cảnh báo dài (cùng luật FG-6 của nhật ký chạy):
   gom theo mã; mỗi mã nhiều hơn CANH_BAO_VD_TOI_DA thì có dòng số đếm + đúng ngần ấy ví dụ + "và N trường hợp nữa";
   ít hơn thì hiện hết, không thêm dòng nào. `muc` = [{ma, chu}] (chu đã là câu đọc được). Vẽ vào `hop`. */
const CANH_BAO_VD_TOI_DA = 5;

function veCanhBaoGom(hop, muc) {
  const nhom = new Map();
  muc.forEach((m) => {
    if (!nhom.has(m.ma)) nhom.set(m.ma, []);
    nhom.get(m.ma).push(m.chu);
  });
  const them = (cha, lop, chu) => {
    const d = document.createElement("div");
    d.className = lop;
    d.textContent = chu;
    cha.appendChild(d);
  };
  nhom.forEach((ds) => {
    const n = document.createElement("div");
    n.className = "canh-bao-nhom";
    const dai = ds.length > CANH_BAO_VD_TOI_DA;
    if (dai) them(n, "canh-bao-tieu-de", t("canh_bao_gom_dau", { n: ds.length }));
    ds.slice(0, CANH_BAO_VD_TOI_DA).forEach((c) => them(n, "canh-bao-dong", "• " + c));
    if (dai) them(n, "canh-bao-con-lai", t("canh_bao_gom_nua", { m: ds.length - CANH_BAO_VD_TOI_DA }));
    hop.appendChild(n);
  });
}

/* Thoat ca dau nhay: truoc day chi an toan GIUA hai the. Chi can mot
   cho sau nay dung esc() trong thuoc tinh (title="${esc(ten)}") la mot
   ten co dau nhay kep pha thuoc tinh ra va chen duoc ma. */
function esc(s) {
  if (s === null || s === undefined) return "";
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/* Thong bao noi (toast).
   Quy tac (Truong chot 27/10/2026):
     - thanh cong (va thong bao thuong): tu dong sau 6 giay; cau dai them thoi
       gian theo do dai, toi da 10 giay; re chuot hoac dua tieu diem vao thi
       tam dung dem, roi dem tiep phan con lai;
     - loi, canh bao, hoac `sticky: true`: GIU cho toi khi bam ×;
     - thanh cong kem canh bao (`opts.canhBao` = cau, hoac {message, errors}):
       tach thanh hai thong bao — xanh tu dong, vang rieng va giu.
   Tra ve phan tu toast de ben goi co the tu go no (vd. het che do ve lai). */
const TOAST_TOI_DA = 4;
const TOAST_THANH_CONG_MS = 6000;
const TOAST_DAI_NHAT_MS = 10000;

function thoiGianToastMs(message) {
  const them = 40 * Math.max(0, String(message).length - 60);
  return Math.min(TOAST_DAI_NHAT_MS, TOAST_THANH_CONG_MS + them);
}

function showToast(message, type, opts) {
  /* Tham so thu ba: mang loi (tu showErrorToast) hoac tuy chon
     {sticky, ghim, khiDong, errors, canhBao}. */
  let errors = null;
  if (Array.isArray(opts)) {
    errors = opts;
    opts = {};
  } else if (opts && opts.errors) {
    errors = opts.errors;
  }
  /* Thanh cong kem canh bao: canh bao la thong bao vang rieng, con thong bao xanh van tu dong. */
  if (type === "success" && opts && opts.canhBao) {
    const cb = typeof opts.canhBao === "string" ? { message: opts.canhBao } : opts.canhBao;
    showToast(cb.message, "warn", cb.errors || []);
    opts = Object.assign({}, opts, { canhBao: null });
  }
  const stack = el("toastStack");
  const toastEl = document.createElement("div");
  toastEl.className = "toast" + (type === "error" ? " is-error"
    : type === "warn" ? " is-warn"
    : type === "success" ? " is-success" : "");
  /* Loi doc ngay (assertive); thong bao khac doc khi roi (polite). */
  if (type === "error") {
    toastEl.setAttribute("role", "alert");
    toastEl.setAttribute("aria-live", "assertive");
  } else {
    toastEl.setAttribute("aria-live", "polite");
  }

  const noiDung = document.createElement("div");
  noiDung.className = "toast-noi-dung";
  const msg = document.createElement("span");
  msg.className = "toast-msg";
  msg.textContent = message;
  noiDung.appendChild(msg);
  /* FG-9: tuy chon hanhDong {nhan, khiBam, tooltip}: mot nut trong thong bao; duong dan dai nam o tooltip. */
  if (opts && opts.hanhDong) {
    if (opts.hanhDong.tooltip) msg.title = opts.hanhDong.tooltip;
    const nutHd = document.createElement("button");
    nutHd.type = "button";
    nutHd.className = "btn btn-ghost toast-hanh-dong";
    nutHd.textContent = opts.hanhDong.nhan;
    if (opts.hanhDong.tooltip) nutHd.title = opts.hanhDong.tooltip;
    nutHd.addEventListener("click", opts.hanhDong.khiBam);
    noiDung.appendChild(nutHd);
  }
  /* Chi tiet ky thuat (vd. loi goc) nam rieng, dong san, mo ra khi can. */
  const coChiTiet = errors ? ganChiTietKyThuat(noiDung, errors) : false;
  toastEl.appendChild(noiDung);

  let hen = null;
  function go() {
    if (hen) clearTimeout(hen);
    if (!toastEl.isConnected || toastEl.classList.contains("is-leaving")) return;
    toastEl.classList.add("is-leaving");
    setTimeout(() => toastEl.remove(), 200);
    if (opts && opts.khiDong) opts.khiDong();
  }
  toastEl.goBo = go;
  /* Bam vao thong bao cung dong duoc no, nhu truoc. */
  msg.addEventListener("click", go);

  const giu = type === "error" || type === "warn" || coChiTiet || !!(opts && opts.sticky);
  if (giu) {
    const nutDong = document.createElement("button");
    nutDong.type = "button";
    nutDong.className = "toast-close";
    /* Dấu × vẽ bằng CSS (::before): chữ của thông báo không kèm "×" khi đọc/sao chép (FG-6). */
    nutDong.setAttribute("aria-label", t("btn_dong"));
    nutDong.addEventListener("click", go);
    toastEl.appendChild(nutDong);
  } else {
    /* Dem nguoc co the tam dung: nho phan con lai luc dung, dem tiep luc tha. */
    let conLai = thoiGianToastMs(message);
    let batDau = 0;
    const chay = () => {
      if (hen) return;
      batDau = Date.now();
      hen = setTimeout(go, conLai);
    };
    const dung = () => {
      if (!hen) return;
      clearTimeout(hen);
      hen = null;
      conLai = Math.max(0, conLai - (Date.now() - batDau));
    };
    toastEl.addEventListener("mouseenter", dung);
    toastEl.addEventListener("mouseleave", chay);
    toastEl.addEventListener("focusin", dung);
    toastEl.addEventListener("focusout", chay);
    chay();
  }

  // `ghim`: thong bao gan voi mot trang thai dang bat (vd. che do ve lai)
  // — gioi han so thong bao KHONG duoc tu dong go no.
  if (opts && opts.ghim) toastEl.classList.add("is-ghim");
  stack.appendChild(toastEl);
  // Khong de chong thong bao che het man hinh: bo cai cu nhat.
  const dangHien = Array.from(stack.querySelectorAll(".toast:not(.is-leaving):not(.is-ghim)"));
  dangHien.slice(0, Math.max(0, dangHien.length - TOAST_TOI_DA)).forEach((x) => x.goBo());
  return toastEl;
}

function feedback(node, message, isError) {
  node.textContent = message;
  node.className = "save-feedback " + (isError ? "is-error" : "is-success");
  const lanNay = (node.dataset.lan = String(Number(node.dataset.lan || 0) + 1));
  if (message) {
    /* Loi kem chi tiet ky thuat thi de lau hon cho kip mo ra doc. */
    setTimeout(() => {
      if (node.dataset.lan === lanNay) node.textContent = "";
    }, isError ? 12000 : 5000);
  }
}

/* Chi tiet ky thuat cua loi (thong bao goc cua may, vd "database is
   locked") KHONG nam trong cau hien ra. Cau noi bang loi thuong; chi
   tiet nam trong mot muc "Chi tiet ky thuat" dong san, de nguoi sua
   loi van doc duoc ma nguoi dung khong phai doc. */
function ganChiTietKyThuat(node, errors) {
  const ds = window.I18N.errorDetails(errors);
  if (!ds.length) return false;
  const hop = document.createElement("details");
  hop.className = "chi-tiet-ky-thuat";
  const tom = document.createElement("summary");
  tom.textContent = t("chi_tiet_ky_thuat");
  const noi = document.createElement("div");
  noi.className = "chi-tiet-ky-thuat-noi";
  noi.textContent = ds.join("\n");
  hop.appendChild(tom);
  hop.appendChild(noi);
  node.appendChild(hop);
  return true;
}

/* Bao loi tu mot phan hoi API. `khoaMau` (tuy chon) boc cau loi vao mot
   cau mau co {errors}, vd "Khong xuat duoc ket qua. {errors}". */
/* Danh sach loi co `csdl_dang_ban` khong: app.db dang bi tien trinh khac giu. Day KHONG phai loi
   cua du lieu hay cua lan chay, nen cac nut khong duoc noi "du lieu chua hop le" hay "that bai"
   chung chung — noi thang CSDL dang ban de nguoi van hanh thu lai sau vai giay (A13.11, N3). */
function coLoiCsdlBan(errors) {
  return Array.isArray(errors) && errors.some((e) => e && e.code === "csdl_dang_ban");
}

/* GT4 fix OL2: phiên hết hạn do nhàn rỗi -> mọi lỗi "cần đăng nhập" đều hỏi lại phiên ngay (mở hộp đăng nhập),
   không đợi vòng hỏi 30 giây và không chỉ chồng thông báo đỏ. */
function nhacHoiPhienNeuCan(errors) {
  if ((errors || []).some((x) => x && x.code === "gt3_can_dang_nhap")) window.dispatchEvent(new Event("tkLamMoi"));
}

function showErrorToast(errors, khoaMau) {
  nhacHoiPhienNeuCan(errors);
  const cau = trErrs(errors).join(" ");
  showToast(khoaMau ? t(khoaMau, { errors: cau }) : cau, "error", errors);
}

function feedbackErrors(node, errors) {
  nhacHoiPhienNeuCan(errors);
  feedback(node, trErrs(errors).join(" "), true);
  ganChiTietKyThuat(node, errors);
}

function debounce(fn, ms) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };
}


/* Menu "⋯" (<details class="menu-khac">): bam ra ngoai, bam mot muc hoac nhan Esc thi dong. */
document.addEventListener("click", (ev) => {
  document.querySelectorAll("details.menu-khac[open]").forEach((d) => {
    const trongHop = ev.target.closest && ev.target.closest(".menu-khac-hop");
    if (!d.contains(ev.target) || (trongHop && d.contains(trongHop) && ev.target.closest("button") && !ev.target.closest("[data-giu-menu]"))) d.open = false;
  });
});
document.addEventListener("keydown", (ev) => {
  if (ev.key !== "Escape") return;
  document.querySelectorAll("details.menu-khac[open]").forEach((d) => { d.open = false; });
});
