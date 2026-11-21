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

/* UX2-L8 (#10): hang MOI cua bang truot vao (<= 20 hang, 180 ms, tre xep chong toi da 19 ms nen tong <= 200 ms). CHI trang
   tri: hang bam duoc ngay (khong pointer-events, khong cho); khong lam gi voi khung cho L7 (hang .ux2-khung-hang) va khong
   hoat hoa tu hang thu 21 (bang 800 dong). Tat hieu ung / giam chuyen dong thi khong gan lop (ux2ChoPhepChuyenDong).
   "MOI" = khoa hang chua tung xuat hien trong bang nay (tap khoa TICH LUY theo tung tbody): ve lai cung du lieu (tai lai, tim
   kiem, sap xep, doi ngon ngu, loc roi bo loc) -> 0 hang truot, KHONG nhap nhay; them mot CLB / hoc sinh -> dung hang do;
   do bang trong lan dau -> toi da 20 hang dau. Tbody bi lam trong han (khong con hang du lieu) thi quen tap khoa de lan do
   day tiep theo la "lan dau". Khoa moi bang (UX2_KHOA_HANG): ket qua = ma hoc sinh + ten CLB (mot em nhieu buoi = nhieu hang),
   hoc sinh quan ly = data-student-id, CLB quan ly = data-club-id, lich su chay = ma lan chay (cot dau). */
const UX2_VAO_TOI_DA = 20;
const UX2_KHOA_HANG = {
  resultsTableBody: (tr) => (tr.cells[1] ? tr.cells[1].textContent.trim() : "") + "|" + (tr.cells[5] ? tr.cells[5].textContent.trim() : ""),
  adminStudentTableBody: (tr) => { const o = tr.querySelector("[data-student-id]"); return o ? o.dataset.studentId : ""; },
  adminClubTableBody: (tr) => tr.dataset.clubId || "",
  historyTableBody: (tr) => (tr.cells[0] ? tr.cells[0].textContent.trim() : ""),
};

function ux2QuanSatBang(dsId) {
  dsId.forEach((id) => {
    const tb = el(id);
    if (!tb || tb.__ux2Quan || typeof MutationObserver === "undefined") return;
    const khoaCua = UX2_KHOA_HANG[id] || ((tr) => (tr.cells[0] ? tr.cells[0].textContent.trim() : ""));
    const daThay = new Set();
    tb.__ux2DaThay = daThay;
    tb.__ux2Quan = new MutationObserver((cacBanGhi) => {
      const hang = [];
      let coGo = false;
      cacBanGhi.forEach((m) => {
        m.addedNodes.forEach((n) => { if (n.nodeName === "TR" && !n.classList.contains("ux2-khung-hang")) hang.push(n); });
        m.removedNodes.forEach((n) => { if (n.nodeName === "TR" && !n.classList.contains("ux2-khung-hang")) coGo = true; });
      });
      if (coGo && !tb.querySelector("tr:not(.ux2-khung-hang)")) daThay.clear(); /* bang bi lam trong han: lan do ke tiep la lan dau */
      const moi = [];
      hang.forEach((tr) => {
        if (!tr.isConnected) return;
        const k = khoaCua(tr);
        if (k !== "" && daThay.has(k)) return;
        if (k !== "") daThay.add(k);
        moi.push(tr);
      });
      if (!ux2ChoPhepChuyenDong()) return;
      moi.slice(0, UX2_VAO_TOI_DA).forEach((tr, i) => {
        tr.style.animationDelay = Math.min(i, 19) + "ms";
        tr.classList.add("ux2-vao");
        const bo = () => { tr.classList.remove("ux2-vao"); tr.style.animationDelay = ""; };
        tr.addEventListener("animationend", bo, { once: true });
        setTimeout(bo, 500);
      });
    });
    tb.__ux2Quan.observe(tb, { childList: true });
  });
}

/* UX2-L7 (#6): khung cho (skeleton) cho bang dang tai. CHI hien neu tai lau hon UX2_KHUNG_TRE_MS (nhanh thi khong chen
   gi: khong nhap nhay) va chi khi tbody dang TRONG (bang con du lieu cu thi cu de du lieu cu). Hang khung aria-hidden,
   bang aria-busy true -> false. `hoi` (promise cua lan tai) duoc gan then(ket, ket): go khung ca khi THANH CONG lan LOI /
   bi tu choi (khong bao gio ket). Goi lan hai khi lan mot chua xong: huy khung cu, chi con MOT bo khung; lan tai cu ve
   muon khong go nham khung moi (so khop `st`). caoHang (px, tuy chon) = chieu cao hang that de khung khong lam bang nhay. Chay xong thi nguoi goi tu ve du lieu hoac trang thai rong (L6). */
const UX2_KHUNG_TRE_MS = 300;

function hienKhungCho(tbody, soCot, soDong, hoi, caoHang) {
  if (!tbody) return () => {};
  const bang = tbody.closest("table");
  if (tbody.__ux2Khung) tbody.__ux2Khung.go();
  const st = {};
  st.go = () => {
    clearTimeout(st.hen);
    tbody.querySelectorAll(".ux2-khung-hang").forEach((r) => r.remove());
  };
  st.hen = setTimeout(() => {
    if (tbody.__ux2Khung !== st || tbody.children.length) return;
    const cot = soCot || (bang ? bang.querySelectorAll("thead th").length : 0) || 1;
    for (let i = 0; i < (soDong || 5); i += 1) {
      const tr = document.createElement("tr");
      tr.className = "ux2-khung-hang";
      tr.setAttribute("aria-hidden", "true");
      if (caoHang) tr.style.height = caoHang + "px"; /* bang co o nhap trong hang: hang that cao hon hang chu */
      /* MOT o tran het chieu ngang (colspan): khung khong lam cot nao gian ra, nen tieu de cot dung yen y nhu luc bang trong. */
      const td = document.createElement("td");
      td.colSpan = cot;
      const x = document.createElement("span");
      x.className = "ux2-khung";
      td.appendChild(x);
      tr.appendChild(td);
      tbody.appendChild(tr);
    }
  }, UX2_KHUNG_TRE_MS);
  tbody.__ux2Khung = st;
  if (bang) bang.setAttribute("aria-busy", "true");
  const ket = () => {
    if (tbody.__ux2Khung !== st) return;
    st.go();
    delete tbody.__ux2Khung;
    if (bang) bang.setAttribute("aria-busy", "false");
  };
  if (hoi && typeof hoi.then === "function") hoi.then(ket, ket);
  return ket;
}

/* UX2-L6 (#12): trang thai RONG co huong dan + MOT nut chinh (he nut L3). Tham so la KHOA i18n (khong chuoi co dinh) de
   ve lai theo ngon ngu khi langchange. cfg = {chu, thamSo, huongDan, nut: {nhan, quyen, tab, oId}}:
   chu = cau neu hien trang (giu cau cu cua trang thai rong, test cu van khop); huongDan = nen lam gi; nut = viec nen lam
   (nhan = khoa; quyen = "quan_tri" -> nut mang data-quyen, giao_vien khong thay; tab = the can toi; oId = o nhap nhan con tro).
   gv = cau cho giao_vien (the Van hanh / Quan ly an voi ho: bao nho quan tri, khong nut). Ten the lay tu nav (ux2TenThe).
   Khong co nut thi chi co chu + huong dan. hop KHONG con data-i18n (applyStaticText se xoa nut). */
function ux2DiToi(tab, oId) {
  const the = document.querySelector('.nav-item[data-tab="' + tab + '"]');
  if (the) the.click();
  setTimeout(() => { const o = oId ? el(oId) : null; if (o) o.focus(); }, 0);
}

/* Ten cac the dung trong cau huong dan: LAY TU nav (cung khoa nav_*) de khong bao gio lech ten the that. */
function ux2TenThe(them) {
  return Object.assign({ the_xep: t("nav_pipeline"), the_quan_ly: t("nav_admin"), the_nhap: t("nav_fallback") }, them || {});
}

function ux2VeRong(hop) {
  const cfg = hop && hop.__ux2Rong;
  if (!cfg) return;
  clear(hop);
  /* giao_vien khong thay the Van hanh / Quan ly: cfg.gv = {chu?, huongDan} thay cau chi cho the do va BO nut. */
  const gv = document.body.dataset.vai === "giao_vien" && cfg.gv ? cfg.gv : null;
  const tham = ux2TenThe(cfg.thamSo);
  const p1 = document.createElement("p");
  p1.className = "ux2-rong-chu";
  p1.textContent = t((gv && gv.chu) || cfg.chu, tham);
  hop.appendChild(p1);
  const huong = (gv && gv.huongDan) || cfg.huongDan;
  if (huong) {
    const p2 = document.createElement("p");
    p2.className = "ux2-rong-huong";
    p2.textContent = t(huong, tham);
    hop.appendChild(p2);
  }
  if (cfg.nut && !gv) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "btn btn-primary ux2-rong-nut";
    if (cfg.nut.quyen) b.setAttribute("data-quyen", cfg.nut.quyen);
    b.textContent = t(cfg.nut.nhan, tham);
    b.addEventListener("click", () => ux2DiToi(cfg.nut.tab, cfg.nut.oId));
    hop.appendChild(b);
  }
}

function veTrangThaiRong(hop, cfg) {
  if (!hop) return;
  hop.__ux2Rong = cfg;
  ux2VeRong(hop);
}

/* Ve lai khi doi ngon ngu VA khi doi vai (dang nhap / dang xuat): ganVai() ban "ux2vai". */
["langchange", "ux2vai"].forEach((ev) => window.addEventListener(ev, () => {
  document.querySelectorAll(".empty-state").forEach((h) => { if (h.__ux2Rong) ux2VeRong(h); });
}));

/* UX2-L4 (#7): loi NGAY TAI O. Chu luon di qua trErr/t (mot nguon, bat bien 6); khong chuoi moi trong JS.
   baoLoiTaiO(o, chu, tuyChon): aria-invalid, lop is-loi, <div.loi-o> ngay sau o (hoac sau <label> boc o) noi voi o
     bang aria-describedby; lac 200 ms (ux2Rung) CHI khi cho phep chuyen dong; go chu vao o thi loi tu xoa.
     tuyChon.them = [lop cu can giu, vd "is-invalid"], tuyChon.tieuDe = true: giu title cu cua o diem,
     tuyChon.khongRung = true: ve lai loi sau khi bang bi dung lai (doi ngon ngu), khong lac lan nua.
     chu co the la () => chuoi: ve lai theo ngon ngu khi doi ngon ngu (lang change) — KHONG xoa loi.
   xoaLoiTaiO(o): go sach moi dau vet (aria-invalid, lop, .loi-o, describedby, ham nghe).
   focusODau(dsO): dua tro vao o DAU TIEN (theo thu tu tren trang), mo <details> dong boc no.
   baoLoiForm(goc, errors, bangMaO, tuyChon): bangMaO = {ma_loi: "idO" | (err) => "idO"}; loi co o thi hien tai o, loi
     khong co o (hoac ma la) thi tuyChon.khac(errors) hoac toast — KHONG BAO GIO im lang. Tra {conO, khac}. */
let ux2SoLoiO = 0;

/* Doi ngon ngu luc loi con hien: ve lai chu theo ngon ngu moi (KHONG xoa loi). Cung kieu voi datNutBan. */
window.addEventListener("langchange", () => {
  document.querySelectorAll(".is-loi").forEach((o) => {
    const st = o.__ux2Loi;
    if (!st || !st.hop.parentNode) return;
    const chu = st.fn();
    st.hop.textContent = chu;
    if (st.tieuDe) o.title = chu;
  });
});

function ux2ChoPhepChuyenDong() {
  return !(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches)
    && !document.documentElement.classList.contains("tat-hieu-ung");
}

function xoaLoiTaiO(o) {
  if (!o) return;
  const st = o.__ux2Loi;
  if (!st) return;
  if (st.hop && st.hop.parentNode) st.hop.parentNode.removeChild(st.hop);
  const con = (o.getAttribute("aria-describedby") || "").split(/\s+/).filter((x) => x && x !== st.id);
  if (con.length) o.setAttribute("aria-describedby", con.join(" "));
  else o.removeAttribute("aria-describedby");
  o.removeAttribute("aria-invalid");
  o.classList.remove("is-loi", "ux2-rung");
  (st.them || []).forEach((c) => o.classList.remove(c));
  if (st.tieuDe) o.removeAttribute("title");
  o.removeEventListener("input", st.ham);
  o.removeEventListener("change", st.ham);
  delete o.__ux2Loi;
}

function baoLoiTaiO(o, chuHoacHam, tuyChon) {
  if (!o) return;
  xoaLoiTaiO(o);
  const tc = tuyChon || {};
  /* chuHoacHam: chuoi, hoac () => chuoi de CHU THEO NGON NGU khi doi ngon ngu luc loi con hien (langchange ve lai). */
  const fn = typeof chuHoacHam === "function" ? chuHoacHam : () => chuHoacHam;
  const chu = fn();
  ux2SoLoiO += 1;
  const id = "loi-o-" + ux2SoLoiO;
  const hop = document.createElement("div");
  hop.className = "loi-o";
  hop.id = id;
  hop.textContent = chu;
  const moc = o.closest("label") || o;
  moc.parentNode.insertBefore(hop, moc.nextSibling);
  const ham = () => xoaLoiTaiO(o);
  o.__ux2Loi = { id, hop, ham, fn, them: tc.them || [], tieuDe: !!tc.tieuDe };
  o.setAttribute("aria-invalid", "true");
  o.setAttribute("aria-describedby", ((o.getAttribute("aria-describedby") || "") + " " + id).trim());
  o.classList.add("is-loi");
  (tc.them || []).forEach((c) => o.classList.add(c));
  if (tc.tieuDe) o.title = chu;
  o.addEventListener("input", ham);
  o.addEventListener("change", ham);
  if (!tc.khongRung && ux2ChoPhepChuyenDong()) {
    o.classList.remove("ux2-rung");
    void o.offsetWidth;
    o.classList.add("ux2-rung");
    setTimeout(() => o.classList.remove("ux2-rung"), 260);
  }
}

function focusODau(dsO) {
  const co = dsO.filter(Boolean);
  if (!co.length) return;
  co.sort((a, b) => (a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1));
  const dau = co[0];
  const d = dau.closest("details");
  if (d && !d.open) d.open = true;
  dau.focus();
}

function baoLoiForm(goc, errors, bangMaO, tuyChon) {
  const tc = tuyChon || {};
  const dsO = [];
  const khac = [];
  (errors || []).forEach((e) => {
    const m = bangMaO && bangMaO[e && e.code];
    const idO = typeof m === "function" ? m(e) : m;
    const o = idO ? (goc && goc.querySelector ? goc.querySelector("#" + idO) : null) || el(idO) : null;
    if (!o) { khac.push(e); return; }
    baoLoiTaiO(o, () => trErr(e));
    dsO.push(o);
  });
  focusODau(dsO);
  if (khac.length) (tc.khac || ((x) => showErrorToast(x)))(khac);
  return { conO: dsO.length > 0, khac };
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
