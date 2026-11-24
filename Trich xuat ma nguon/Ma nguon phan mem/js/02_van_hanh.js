/* js/02_van_hanh.js — Thẻ 01 — Vận hành: chạy sắp xếp, sức khoẻ dữ liệu, nạp Sổ nhập CLB.

   Một phần của giao diện chính, tách từ app.js cũ. Các tệp js/ là SCRIPT
   THƯỜNG (không phải ES module) nạp theo đúng thứ tự trong index.html và
   dùng chung một phạm vi — như một tệp duy nhất trước đây. Không dùng ES
   module vì mở trang bằng file:// thì trình duyệt chặn chúng.
*/
"use strict";

/* ------------------------------------------------------------------ *
 * 3. TAB 1 — VẬN HÀNH PIPELINE
 * ------------------------------------------------------------------ */

/* So nhap dang cho (toi da MOT phan tu):
   { ten, b64, tomTat, dangDoc, xong, ketQuaSo, loiRaw, loiText } */
let importQueue = [];

// Bộ nhớ lần render gần nhất của stepper/log — dùng để dịch lại đúng
// nội dung khi người dùng đổi ngôn ngữ giữa chừng (không gọi lại API).
let lastRenderedSteps = null;
let lastRenderedTopErrors = null;

/* O hat giong: hien DUNG so lan chay truoc da dung, khong phai 42 co
   dinh. Truoc day mo lai app la o ve 42, va chay lai mot buoi voi hat
   giong khac lan truoc bi phan loi tu choi (khong_doi_hat_giong_...).
   Nguoi dung da go tay thi KHONG ghi de — chuyen the roi quay lai khong
   duoc xoa so ho vua go. */
let seedDaSua = false;

// Goi tu refreshSidebarStatus(), noi da doc san thong tin lan chay truoc.
function napHatGiongLanTruoc(lanTruoc) {
  if (seedDaSua || !lanTruoc) return;
  const seed = lanTruoc.seed;
  if (seed !== null && seed !== undefined) el("seedInput").value = seed;
}

/* Tra ve so nguyen, hoac null neu o khong phai so nguyen. Truoc day
   `parseInt(...) || 42` bien o trong, so 0, hay "1.5" thanh 42 ma khong
   noi gi — chay voi mot hat giong nguoi dung khong he chon. */
function docHatGiong() {
  const chu = String(el("seedInput").value).trim();
  if (!/^-?\d+$/.test(chu)) return null;
  const so = Number(chu);
  return Number.isSafeInteger(so) ? so : null;
}

function loadPipelineTab() {
  ux2VePha(); /* UX2-L5: ve 4 pha ngay khi mo the (trang thai hien co, mac dinh "chua chay") */
  refreshDashboardStats();
  refreshStbLockLine();
  refreshSidebarStatus();
  loadHealthReport();
  loadChonBuoi();
}

/* ---- Cảnh báo sức khoẻ dữ liệu (pre-flight) ---- */

/* Tra ve promise cua lan goi, de nut Kiem tra dung chung mot ket qua
   voi o Canh bao du lieu thay vi hoi phan loi hai lan. */
function loadHealthReport() {
  const hoi = callApi("get_data_health_report");
  /* Lần hỏi đang bay: thanh "Việc tiếp theo" dùng chung thay vì hỏi lại backend. */
  window.healthDangHoi = hoi;
  hoi.then(() => { if (window.healthDangHoi === hoi) window.healthDangHoi = null; }, () => { if (window.healthDangHoi === hoi) window.healthDangHoi = null; });
  /* Danh sách cảnh báo chỉ hiện SAU khi thanh "Việc tiếp theo" đã có trạng thái: hai nơi nói cùng một điều nên không
     được lệch nhau (trước đây thanh còn chờ thêm hai lời gọi sau khi danh sách đã hiện: người xem, và test, thấy
     danh sách mà thanh còn trống). UX1A-L1: thanh dùng luôn kết quả vừa có. */
  hoi.then((res) => Promise.resolve(typeof capNhatViecTiepTheo === "function" ? capNhatViecTiepTheo(res) : null)
    .catch(() => null).then(() => {
    const summary = el("healthSummary");
    const list = el("healthList");
    clear(list);
    const gap = el("healthChiTiet");   /* UX5B-L2: danh sách cảnh báo nằm trong mục gập; tự mở khi có mục nghiêm trọng */
    gap.hidden = true;

    if (!res.ok) {
      summary.className = "health-summary is-warn";
      summary.textContent = trErrs(res.errors).join(" ");
      ganChiTietKyThuat(summary, res.errors);
      return;
    }

    const d = res.data;
    if (khoa.thieuDuLieu) { /* T3-01: dữ liệu trống thì KHÔNG báo xanh "đã sẵn sàng" */
      hienChuaCoDuLieu();
      return;
    }
    if (!d.n_warnings) {
      summary.className = "health-summary is-clean";
      summary.textContent = t("health_clean");
      return;
    }

    /* UX1B-L5c: sổ mang điểm quyết tâm / huy chương sai chỗ -> MỘT dòng có số em và tên CLB, không từng dòng một. */
    let dsHien = d.warnings;
    let nHien = d.n_warnings;
    let nCao = d.n_high;
    const gop = d.gop_huy_chuong;
    if (gop) {
      const la = (w) => /^fa_huy_chuong_/.test(w.code) && !/_nhom$/.test(w.code);
      const bo = dsHien.filter(la);
      /* Không in "ví dụ ở: " rỗng: không có tên CLB (vd. cùng huy chương hai lần) thì dùng câu không có vế ví dụ. */
      dsHien = [gop.clb.length
        ? { code: "ux1b_huy_chuong_gop", severity: "high",
            params: { n: gop.n_em, clb: gop.clb.join(", ") + (gop.n_clb > gop.clb.length ? "…" : "") } }
        : { code: "ux1b_huy_chuong_gop_khong_clb", severity: "high", params: { n: gop.n_em } },
        ...dsHien.filter((w) => !la(w))];
      nHien += 1 - bo.length;
      nCao += 1 - bo.filter((w) => w.severity === "high").length;
    }

    /* Đỏ chỉ khi có mục NGHIÊM TRỌNG (mục đó chặn việc chạy); còn lại để trung tính. */
    summary.className = nCao > 0 ? "health-summary is-warn" : "health-summary";
    summary.textContent = t("health_summary", { n: nHien, n_high: nCao });

    const SEV_LABEL = {
      high: "health_sev_high",
      medium: "health_sev_medium",
      info: "health_sev_info",
    };
    // nghiêm trọng lên trước — người vận hành đọc từ trên xuống
    const order = { high: 0, medium: 1, info: 2 };
    dsHien
      .slice()
      .sort((a, b) => (order[a.severity] ?? 9) - (order[b.severity] ?? 9))
      .forEach((w) => {
        const row = document.createElement("div");
        row.className = "health-item sev-" + (w.severity || "info");
        const sev = document.createElement("span");
        sev.className = "health-sev";
        sev.textContent = t(SEV_LABEL[w.severity] || "health_sev_info");
        const msg = document.createElement("span");
        msg.textContent = trErr(w);
        row.appendChild(sev);
        row.appendChild(msg);
        /* T3-02: dong chan chay vi ho so diem quyet tam co nut nhay thang toi cho sua. */
        if (w.code === "health_wharton_chua_hop_le") {
          const di = document.createElement("button");
          di.type = "button";
          di.className = "btn btn-secondary btn-nho health-di-toi";
          di.textContent = t("health_mo_diem_quyet_tam");
          di.addEventListener("click", moDanhSachCanXuLy);
          row.appendChild(di);
        }
        if (w.code === "ux1b_huy_chuong_gop" || w.code === "ux1b_huy_chuong_gop_khong_clb") {   /* UX1B-L5c: lối về khung Cài đặt (nơi có nút Quay lại Chia 100 điểm) */
          const di = document.createElement("button");
          di.type = "button";
          di.className = "btn btn-secondary btn-nho health-di-toi";
          di.id = "btnUx1bHealthCaiDat";
          di.textContent = t("ux1b_nut_huy_chuong_sai");
          di.addEventListener("click", () => ux1bMoCaiDat());
          row.appendChild(di);
        }
        list.appendChild(row);
      });
    gap.hidden = false;
    gap.open = nCao > 0;
  }));
  return hoi;
}

/* T3-10: moi luc dung MOT nut mau chinh. Chua co du lieu -> "Nhap du lieu" noi bat, hai khung kia lui
   xuong; co du lieu chua chay -> "Chay sap xep"; da chay xong -> dong ket qua (T3-06), Chay tro thanh nut phu. */
let trangThaiVanHanh = "trong";
let ux5bSoNguoi = 0;
/* UX5B-L2: dòng trạng thái của thẻ Xếp CLB: việc đã xong và việc tiếp theo (cùng nguồn với nút vàng: capNhatKhoaVanHanh). */
function ux5bVeTrangThaiPipeline() {
  const o = el("ux5bTtPipeline");
  if (!o) return;
  const cho = importQueue[0] && importQueue[0].b64 && !importQueue[0].xong;
  o.textContent = cho ? t("ux5b_tt_buoc_cho_nhap")
    : trangThaiVanHanh === "xong" ? t("ux5b_tt_buoc_xong")
    : trangThaiVanHanh === "san_sang" ? t("ux5b_tt_buoc_chay", { n: ux5bSoNguoi })
    : t("ux5b_tt_buoc_nhap");
}
function datTrangThaiVanHanh(d) {
  ux5bSoNguoi = d.n_students || 0;
  trangThaiVanHanh = (!d.n_students || !d.n_clubs) ? "trong" : (d.n_matched > 0 ? "xong" : "san_sang");
  const v = el("view-pipeline");
  if (v) v.dataset.trangThai = trangThaiVanHanh;
  capNhatKhoaVanHanh();
}

function refreshDashboardStats() {
  callApi("get_dashboard_status").then((res) => {
    if (!res.ok) {
      showErrorToast(res.errors);
      return;
    }
    el("statStudents").textContent = res.data.n_students;
    el("statClubs").textContent = res.data.n_clubs;
    el("statMatched").textContent = res.data.n_matched;
    datTrangThaiVanHanh(res.data);
    if (typeof capNhatViecTiepTheo === "function") capNhatViecTiepTheo(); /* UX1A-L1 */
    /* T3-01 (B2): chưa có học sinh hoặc chưa có CLB thì khoá nút Chạy kèm lý do (backend cũng chặn
       bằng `chua_co_du_lieu_de_chay`, nên đây chỉ là báo sớm cho người vận hành). */
    const trong = !res.data.n_students || !res.data.n_clubs;
    const doi = trong !== khoa.thieuDuLieu;
    khoa.thieuDuLieu = trong;
    capNhatKhoaVanHanh();
    const summary = el("healthSummary");
    if (trong && summary.classList.contains("is-clean")) hienChuaCoDuLieu();
    else if (!trong && doi && summary.classList.contains("is-empty")) loadHealthReport();
  });
}

function hienChuaCoDuLieu() {
  const summary = el("healthSummary");
  clear(el("healthList"));
  el("healthChiTiet").hidden = true;
  summary.className = "health-summary is-warn is-empty";
  summary.textContent = t("health_chua_co_du_lieu");
}

function refreshStbLockLine() {
  callApi("get_stb_lock_status").then((res) => {
    const line = el("stbLockLine");
    if (!res.ok) {
      line.textContent = "";
      return;
    }
    clear(line);
    const dot = document.createElement("span");
    dot.className = "lock-dot";
    line.className = "stb-lock-line" + (res.data.is_locked ? "" : " is-unlocked");
    line.appendChild(dot);
    const label = document.createElement("span");
    label.textContent = res.data.is_locked
      ? t("stb_locked_label", { locked_at: dinhDangGio(res.data.locked_at) })
      : t("stb_unlocked_label");
    line.appendChild(label);

    seedKhoa = res.data.is_locked && res.data.seed !== null && res.data.seed !== undefined
      ? res.data.seed : null;
    capNhatOHatGiong();

    if (res.data.is_locked) {
      const redrawBtn = document.createElement("button");
      redrawBtn.className = "redraw-toggle";
      redrawBtn.textContent = t("btn_redraw_stb");
      redrawBtn.addEventListener("click", () => promptForceRedraw());
      line.appendChild(redrawBtn);
      capNhatKhoaVanHanh(); // nut moi dung lai: ap dung trang thai khoa
    }
  });
}

let forceRedrawArmed = false;
let veLaiTimer = null;
let veLaiToast = null;

/* Bat/tat che do "ve lai so boc tham". Thong bao nhac GAN LIEN voi trang
   thai: con bat thi con hien, tat (bam lai, het 20 giay, xac nhan, huy,
   doi ngon ngu) thi go ngay. Truoc day thong bao tat sau 3,6 giay con
   che do van bat 20 giay — nguoi dung khong biet no con bat hay khong.
   Bam × tren thong bao cung la tat che do. */
function datCheDoVeLai(bat) {
  forceRedrawArmed = bat;
  clearTimeout(veLaiTimer);
  veLaiTimer = null;
  if (veLaiToast) {
    const cu = veLaiToast;
    veLaiToast = null;          // truoc goBo(): khiDong ben duoi khong goi lai
    cu.goBo();
  }
  if (bat) {
    /* Ghim: gioi han 4 thong bao khong duoc go loi nhac nay trong khi che
       do van bat. Va dong no bang BAT KY duong nao (× hay cach khac) deu
       tat che do — khong bao gio con che do bat ma khong con loi nhac. */
    const nhac = showToast(t("toast_redraw_armed"), "warn", {
      ghim: true,
      khiDong: () => { if (veLaiToast === nhac) datCheDoVeLai(false); },
    });
    veLaiToast = nhac;
    veLaiTimer = setTimeout(() => datCheDoVeLai(false), 20000);
  }
  capNhatOHatGiong();
}

/* Hat giong dang khoa cung bo so boc tham (null = chua khoa). Khoa roi
   thi o hat giong CHI DOC va hien dung hat giong da khoa: doi no cung
   doi thu tu uu tien moi buoi, tuc la cung tac dung voi ve lai bo so —
   nen phai di cung mot cua, qua nut "Ve lai". Backend cung chan
   (`hat_giong_da_khoa`); o day chi de nguoi dung khong phai go roi moi
   biet la khong duoc. */
let seedKhoa = null;

function capNhatOHatGiong() {
  const o = el("seedInput");
  if (!o) return;
  const dangKhoa = seedKhoa !== null && !forceRedrawArmed;
  if (dangKhoa) o.value = seedKhoa;
  o.readOnly = dangKhoa;
  o.title = "";
  /* Bốc thăm lại thì ô mã phải thấy được để nhập mã mới: mở mục Nâng cao. */
  if (forceRedrawArmed && el("nangCao")) el("nangCao").open = true;
}

/* Mot cua duy nhat bat/tat che do ve lai: loi nhac ghim, hen gio 20 giay
   va o hat giong (mo khoa khi ve lai) di cung nhau. */
function datVeLai(bat) {
  datCheDoVeLai(bat);
}

function promptForceRedraw() {
  datCheDoVeLai(!forceRedrawArmed);
}

/* Buoc nao phan loi tra ve ma KHONG co dong tinh trong #stepper (vd.
   "rollback" khi mot lan chay bi hoan tac, "unknown" khi loi la) thi
   them mot dong rieng cho no. Truoc day renderSteps lang le bo qua cac
   buoc nay — nen cau tran an "du lieu da quay ve dung trang thai truoc
   khi bam chay" chua bao gio hien ra. */
function dongBuocThem(stepper, ten) {
  let li = stepper.querySelector(`.step[data-step="${ten}"]`);
  if (li) return li;
  li = document.createElement("li");
  li.className = "step";
  li.dataset.step = ten;
  li.dataset.dong = "them";
  // Khung co dinh, khong chua du lieu; chu do renderSteps ghi bang textContent.
  li.innerHTML = '<span class="step-dot"></span><div class="step-body">'
    + '<div class="step-title"></div><div class="step-detail"></div></div>';
  stepper.appendChild(li);
  return li;
}

/* ---- UX2-L5 (#11): 4 pha tien trinh — CHI HIEN THI ----
   run_pipeline tra danh sach buoc khi da xong het, nen trong luc chay ca 4 pha cung "dang chay" (khong dinh); khi co
   ket qua thi suy tung pha tu `steps`. Thu tu pha = thu tu cua bat bien 5 (backup -> validate -> bốc thăm -> xếp ->
   ghi -> xuat). Moi ten buoc trong api.py run_pipeline phai co o day (test tinh); "unknown" co y khong thuoc pha nao:
   no la loi, hien tren pha DANG CHAY. "rollback" thuoc pha Ghi nhung KHONG BAO GIO tinh la "xong": no chi noi
   "da hoan tac" (dong ghi chu), pha loi van la pha loi. */
const UX2_PHA = [
  { ma: "kiem_tra", buoc: ["backup", "validate"] },
  { ma: "xep", buoc: ["stb_lottery", "rbda_cascade"] },
  { ma: "ghi", buoc: ["write_results", "rollback"] },
  { ma: "xuat", buoc: ["export"] },
];
const UX2_PHA_BO_QUA = ["unknown"];
const UX2_PHA_CHU = {
  cho: "step_not_run_yet", dang: "step_running", xong: "ux2_pha_xong", loi: "ux2_pha_loi", chua_den: "ux2_pha_chua_den",
  canh_bao: "ux2_pha_canh_bao",
};
let ux2PhaTrang = { che: "cho", steps: [], ok: true };

/* Thuan: (steps, ok) -> {pha: [{ma, tt}], hoanTac, canhBao}. tt = cho | dang | xong | loi | chua_den | canh_bao.
   canh_bao: buoc sao luu loi nhung lan chay VAN THANH CONG (api.py: sao luu hong khong chan chay) — khong phai loi;
   canhBao = chi tiet cua buoc do (de hien o dong ghi chu). Loi xuat tep khi ok van la "loi" (ket qua da ghi). */
function ux2TinhPha(steps, ok) {
  const cuoi = {};
  (steps || []).forEach((s) => { cuoi[s.step] = s.status; });
  const pha = UX2_PHA.map((p) => {
    const that = p.buoc.filter((b) => b !== "rollback");
    const tt = that.map((b) => cuoi[b]);
    let st = "chua_den";
    if (tt.includes("error")) st = (ok && p.ma === "kiem_tra" && cuoi.validate !== "error") ? "canh_bao" : "loi";
    else if (tt.every((x) => x === "done")) st = "xong";
    else if (tt.includes("running")) st = "dang"; /* dung giua chung: sap bi doi thanh loi ben duoi */
    return { ma: p.ma, tt: st };
  });
  const coLoiChung = !ok || cuoi.unknown === "error";
  let iLoi = pha.findIndex((p) => p.tt === "loi");
  if (iLoi < 0 && coLoiChung) {
    /* loi khong gan voi buoc nao (vd "unknown", hoac API nem loi): pha DANG CHAY, khong thi pha dau tien chua xong */
    iLoi = pha.findIndex((p) => p.tt === "dang");
    if (iLoi < 0) iLoi = pha.findIndex((p) => p.tt !== "xong");
    if (iLoi >= 0) pha[iLoi].tt = "loi";
  }
  if (!ok && iLoi >= 0) for (let i = iLoi + 1; i < pha.length; i += 1) pha[i].tt = "chua_den";
  const bk = ok && cuoi.backup === "error" ? (steps || []).filter((s) => s.step === "backup" && s.status === "error").pop() : null;
  return { pha, hoanTac: cuoi.rollback === "done" && !ok, canhBao: bk ? (bk.detail || null) : null };
}

function ux2VePha() {
  const hop = el("ux2Pha");
  if (!hop) return;
  const tc = ux2PhaTrang;
  let kq;
  if (tc.che === "cho") kq = { pha: UX2_PHA.map((p) => ({ ma: p.ma, tt: "cho" })), hoanTac: false };
  else if (tc.che === "dang") kq = { pha: UX2_PHA.map((p) => ({ ma: p.ma, tt: "dang" })), hoanTac: false };
  else kq = ux2TinhPha(tc.steps, tc.ok);
  kq.pha.forEach((p) => {
    const li = hop.querySelector('[data-pha="' + p.ma + '"]');
    if (!li) return;
    li.dataset.trangThai = p.tt;
    li.querySelector(".ux2-pha-tt").textContent = t(UX2_PHA_CHU[p.tt]);
    if (p.tt === "dang") li.setAttribute("aria-current", "step");
    else li.removeAttribute("aria-current");
  });
  hop.setAttribute("aria-busy", tc.che === "dang" ? "true" : "false");
  const ghiChu = el("ux2PhaGhiChu");
  if (ghiChu) {
    const chu = kq.hoanTac ? trErr({ code: "pipeline_rolled_back", params: {} })
      : (kq.canhBao ? (Array.isArray(kq.canhBao) ? chuLoiBuocGon(kq.canhBao) : trErr(kq.canhBao)) : "");
    ghiChu.hidden = !chu;
    ghiChu.textContent = chu;
  }
}

function ux2DatPha(che, steps, ok) {
  ux2PhaTrang = { che, steps: steps || [], ok: ok !== false };
  ux2VePha();
}

function renderSteps(steps) {
  lastRenderedSteps = steps;
  const stepper = el("stepper");
  steps.forEach((s) => {
    const li = dongBuocThem(stepper, s.step);
    if (li.dataset.dong === "them") {
      // Dat lai tieu de moi lan ve de doi ngon ngu cung dich theo.
      const khoaTieuDe = "step_title_" + s.step;
      const tieuDe = t(khoaTieuDe);
      li.querySelector(".step-title").textContent =
        tieuDe !== khoaTieuDe ? tieuDe : t("step_title_unknown");
    }
    li.dataset.status = s.status;
    const detail = li.querySelector(".step-detail");
    if (s.status === "running") detail.textContent = t("step_running");
    else if (s.status === "done") detail.textContent = s.detail ? trErr(s.detail) : t("step_done_default");
    else if (s.status === "error")
      detail.textContent = Array.isArray(s.detail) ? chuLoiBuocGon(s.detail) : (s.detail ? trErr(s.detail) : t("generic_error"));
  });
}

/* T3-06: chay xong thanh cong thi thu 6 buoc thanh mot dong ket qua; "Chi tiet" mo lai danh sach buoc.
   Dang chay, co loi, hoan tac: giu nguyen danh sach buoc (bat bien 5). */
let lastRunXong = null;   // {n_matched, n_total, rounds, path} sau lan chay thanh cong
let chiTietBuocMo = false;

function veRunXong() {
  const hop = el("runXong");
  if (!hop) return;
  hop.hidden = !lastRunXong;
  el("stepper").hidden = !!lastRunXong && !chiTietBuocMo;
  if (!lastRunXong) return;
  el("runXongChu").textContent = t("toast_run_success", {
    n_matched: lastRunXong.n_matched, n_total: lastRunXong.n_total, rounds: lastRunXong.rounds,
  });
  el("btnMoThuMucKq").hidden = !lastRunXong.path;
  el("btnChiTietBuoc").textContent = t(chiTietBuocMo ? "btn_an_chi_tiet_buoc" : "btn_chi_tiet_buoc");
  el("btnChiTietBuoc").setAttribute("aria-expanded", chiTietBuocMo ? "true" : "false");
}

function resetSteps() {
  lastRunXong = null;
  chiTietBuocMo = false;
  veRunXong();
  lastRenderedSteps = null;
  ux2DatPha("cho");
  document.querySelectorAll('#stepper .step[data-dong="them"]').forEach((li) => li.remove());
  document.querySelectorAll("#stepper .step").forEach((li) => {
    li.dataset.status = "";
    li.querySelector(".step-detail").textContent = t("step_not_run_yet");
  });
}

/* Luc bam Chay, phan loi chi tra ket qua cac buoc KHI DA XONG HET. Trong
   luc cho, danh dau moi buoc la "dang chay" de man hinh khong dung yen o
   "Chua chay" — nhin nhu treo, va nguoi dung bam tiep hoac chuyen the. */
function danhDauDangChay() {
  ux2DatPha("dang");
  renderSteps(
    Array.from(document.querySelectorAll("#stepper .step")).map((li) => ({
      step: li.dataset.step, status: "running",
    }))
  );
}

/* ---- Khoa thao tac trong luc lam viec ----
   Moi co mot co rieng; capNhatKhoaVanHanh() suy ra trang thai MOI nut tu
   tat ca cac co, thay vi moi thao tac tu bat/tat nut theo y minh. Truoc
   day nut Kiem tra bat lai nut cua chinh no giua luc dang chay, va nut
   Chay chi bi khoa SAU khi hoi xong phan loi — bam dup la chay hai lan. */
const khoa = {
  dangHoiChay: false,   // tu luc bam Chay toi luc biet co can xac nhan hay khong
  dangChay: false,      // run_pipeline dang chay
  dangKiemTra: false,   // check_data_integrity dang chay
  dangNhap: false,      // dang nhap tep
  dangXuat: false,      // mot lan xuat (chayXuat) dang chay
  thieuDuLieu: false,   // 0 hoc sinh hoac 0 CLB: khong co gi de xep (T3-01)
};

function capNhatKhoaVanHanh() {
  const coThanhXacNhan = !!el("runConfirmBar");
  const btnRun = el("btnRun");
  btnRun.disabled = khoa.dangChay || khoa.dangHoiChay || coThanhXacNhan
    || khoa.dangNhap || khoa.dangKiemTra || khoa.thieuDuLieu;
  if (khoa.thieuDuLieu) btnRun.title = t("health_chua_co_du_lieu");
  else btnRun.removeAttribute("title");
  /* UX2-L1: dung datNutBan (spinner + aria-busy + khoa min-width), khong tu doi textContent luc dang chay. */
  datNutBan(btnRun, khoa.dangChay || khoa.dangHoiChay, "ux2_dang_xep");
  if (!(khoa.dangChay || khoa.dangHoiChay) && btnRun.textContent !== t("btn_run_pipeline")) btnRun.textContent = t("btn_run_pipeline");
  const nutChinh = trangThaiVanHanh === "san_sang" && !importQueue.length;
  btnRun.classList.toggle("btn-primary", nutChinh);
  btnRun.classList.toggle("btn-secondary", !nutChinh);
  el("stepper").setAttribute("aria-busy", khoa.dangChay ? "true" : "false");
  el("btnValidate").disabled = khoa.dangChay || khoa.dangKiemTra || khoa.dangNhap;
  el("btnImportAll").disabled = khoa.dangChay || khoa.dangNhap;
  el("btnClearQueue").disabled = khoa.dangChay || khoa.dangNhap;
  el("btnTaiSoMau").disabled = khoa.dangChay || khoa.dangNhap;
  ux5bVeTrangThaiPipeline();
  if (el("btnXuatTuyChon")) el("btnXuatTuyChon").disabled = khoa.dangChay || khoa.dangXuat;
  if (typeof capNhatNutXuatTheoLop === "function") capNhatNutXuatTheoLop();

  const zone = el("dropZone");
  const khoaTha = khoaVungTha();
  zone.classList.toggle("is-disabled", khoaTha);
  zone.setAttribute("aria-disabled", khoaTha ? "true" : "false");

  // Doi pham vi buoi giua luc dang chay la vo nghia: pham vi da gui di roi.
  document.querySelectorAll(
    "#seedInput, #chonBuoiChip .buoi-chip, #btnChonTatCaBuoi, #stbLockLine .redraw-toggle"
  ).forEach((n) => { n.disabled = khoa.dangChay; });
}

function khoaVungTha() {
  return khoa.dangChay || khoa.dangNhap;
}

function datKhoa(ten, bat) {
  khoa[ten] = bat;
  capNhatKhoaVanHanh();
}

/* Lỗi chặn vì hồ sơ điểm quyết tâm có thể lên tới hàng trăm dòng (mỗi em mỗi quỹ một lỗi). Màn hình
   chỉ hiện tóm tắt, vài em đầu (mỗi em MỘT dòng gộp mọi lỗi của em) và nút sang danh sách đầy đủ ở
   tab Quản lý. Backend vẫn trả đủ mọi lỗi; chỉ cách HIỆN đổi (bất biến 6). */
const MA_LOI_HO_SO_WHARTON = [
  "wharton_chua_dung_het", "wharton_vuot_ngan_sach", "wharton_diem_khong_hop_le",
  "wharton_ngoai_tap", "wharton_tang_lech", "wharton_nguyen_vong_chua_xep",
];
const LOG_SO_EM_TOI_DA = 5;
const LOG_SO_LOI_MOI_MA = 5;

/* Tách `errors` thành {khac: lỗi thường, em: [[sid, [lỗi]]] theo mã tăng dần, gop: có gộp không}. */
function tachLoiWharton(errors) {
  const em = new Map();
  const khac = [];
  errors.forEach((e) => {
    if (e && typeof e === "object" && e.code === "wharton_ho_so_chua_hop_le") return;
    if (e && typeof e === "object" && MA_LOI_HO_SO_WHARTON.includes(e.code) && e.params
        && e.params.student_id !== undefined) {
      if (!em.has(e.params.student_id)) em.set(e.params.student_id, []);
      em.get(e.params.student_id).push(e);
    } else khac.push(e);
  });
  const ds = Array.from(em.entries()).sort((a, b) => (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0));
  return { khac, em: ds };
}

function chuMotLoiWharton(e) {
  const p = e.params || {};
  let cau;
  if (e.code === "wharton_chua_dung_het") cau = t("wh_loi_p_thieu", { quy: p.quy, x: p.thieu });
  else if (e.code === "wharton_vuot_ngan_sach") cau = t("wh_loi_p_thua", { quy: p.quy, x: p.tong - p.ngan_sach });
  else if (e.code === "wharton_ngoai_tap") cau = t("wh_loi_p_ngoai_tap", { quy: p.quy });
  else if (e.code === "wharton_tang_lech") cau = t("wh_loi_p_tang_lech");
  else if (e.code === "wharton_diem_khong_hop_le") cau = t("wh_loi_p_khong_hop_le");
  else if (e.code === "wharton_nguyen_vong_chua_xep") cau = t("wh_loi_p_nguyen_vong");
  else cau = t("wh_loi_p_khac");
  if (p.buoi && p.buoi !== BUOI_MAC_DINH) cau += " (" + nhanBuoi(p.buoi) + ")";
  return cau;
}

/* Chữ lỗi của MỘT bước trong danh sách bước: lỗi hồ sơ điểm quyết tâm chỉ còn câu tóm tắt (chi tiết
   từng em nằm ở khung "Các lỗi cần xử lý" và ở tab Quản lý), lỗi khác giữ nguyên. */
function chuLoiBuocGon(errors) {
  const { khac, em } = tachLoiWharton(errors);
  const cau = khac.map((e) => trErr(e));
  if (em.length) cau.push(trErr({ code: "wharton_tom_tat_chua_hop_le", params: { n: em.length } }));
  return cau.join(" ");
}

function showLog(errors) {
  lastRenderedTopErrors = errors;
  const panel = el("logPanel");
  const box = el("logBox");
  if (!errors || !errors.length) {
    panel.hidden = true;
    box.textContent = "";
    return;
  }
  panel.hidden = false;
  clear(box);
  const ds = Array.isArray(errors) ? errors : [errors];
  const { khac, em } = tachLoiWharton(ds);
  const them = (cau, lop, loi) => {
    const dong = document.createElement("div");
    dong.className = "log-dong" + (lop ? " " + lop : "");
    const c = document.createElement("div");
    c.textContent = cau;
    dong.appendChild(c);
    if (loi) ganChiTietKyThuat(dong, [loi]);
    box.appendChild(dong);
  };
  /* FG-6: lỗi cùng mã gom lại, tối đa LOG_SO_LOI_MOI_MA dòng mỗi mã rồi "và N lỗi nữa". */
  const dem = {};
  khac.forEach((e) => {
    dem[e.code] = (dem[e.code] || 0) + 1;
    if (dem[e.code] <= LOG_SO_LOI_MOI_MA) them(trErr(e), "", e);
  });
  Object.keys(dem).forEach((ma) => {
    if (dem[ma] > LOG_SO_LOI_MOI_MA) them(t("log_loi_nua", { m: dem[ma] - LOG_SO_LOI_MOI_MA }), "log-tom-tat");
  });
  if (!em.length) return;
  them(trErr({ code: "wharton_tom_tat_chua_hop_le", params: { n: em.length } }), "log-tom-tat");
  em.slice(0, LOG_SO_EM_TOI_DA).forEach(([sid, loi]) => {
    const chiTiet = Array.from(new Set(loi.map(chuMotLoiWharton))).join(", ");
    them(t("wh_loi_dong_em", { student_id: sid, chi_tiet: chiTiet }), "log-em");
  });
  const hang = document.createElement("div");
  hang.className = "log-hang-cuoi";
  if (em.length > LOG_SO_EM_TOI_DA) {
    const con = document.createElement("span");
    con.className = "log-them";
    con.textContent = t("wh_loi_khac", { m: em.length - LOG_SO_EM_TOI_DA });
    hang.appendChild(con);
  }
  const nut = document.createElement("button");
  nut.type = "button";
  nut.className = "btn btn-secondary log-mo-ds";
  nut.textContent = t("wh_loi_mo_ds");
  nut.addEventListener("click", moDanhSachCanXuLy);
  hang.appendChild(nut);
  if (typeof wsMoTinhNangDangMo === "function") {
    const goiY = document.createElement("span");
    goiY.className = "log-goi-y";
    goiY.textContent = t("wh_goi_y_tat");
    hang.appendChild(goiY);
    const tat = document.createElement("button");
    tat.type = "button";
    tat.id = "btnMoTinhNangTuLoi";
    tat.className = "btn btn-secondary";
    tat.textContent = t("wh_mo_tinh_nang");
    tat.addEventListener("click", wsMoTinhNangDangMo);
    hang.appendChild(tat);
  }
  box.appendChild(hang);
}

function initPipelineHandlers() {
  el("btnValidate").addEventListener("click", () => {
    datKhoa("dangKiemTra", true);
    callApi("check_data_integrity").then((res) => {
      datKhoa("dangKiemTra", false);
      if (res.ok) {
        showLog(null);
        const hopLe = t("toast_data_valid", { n_students: res.data.n_students, n_clubs: res.data.n_clubs });
        /* "Hop le" chi co nghia la khong co loi CHAN chay. Canh bao nghiem
           trong (vd. thieu diem) van con thi noi ro, dung de mot thong bao
           xanh noi nguoc voi o Canh bao du lieu ngay phia tren. */
        loadHealthReport().then((sk) => {
          const nHigh = sk && sk.ok && sk.data ? sk.data.n_high : 0;
          if (nHigh > 0) {
            showToast(hopLe + "\n" + t("toast_hop_le_con_canh_bao", { n_high: nHigh }), "warn");
          } else {
            showToast(hopLe, "success");
          }
        });
      } else if (coLoiCsdlBan(res.errors)) {
        showErrorToast(res.errors);
        loadHealthReport();
      } else {
        showToast(t("toast_data_invalid"), "error");
        showLog(res.errors);
        loadHealthReport();
      }
    });
  });

  el("btnRun").addEventListener("click", () => {
    runPipelineFlow();
  });
  el("btnChiTietBuoc").addEventListener("click", () => { chiTietBuocMo = !chiTietBuocMo; veRunXong(); });
  el("btnMoThuMucKq").addEventListener("click", () => {
    if (lastRunXong && lastRunXong.path) callApi("mo_thu_muc", lastRunXong.path);
  });

  el("btnToggleHistory").addEventListener("click", () => {
    const table = el("historyTable");
    table.hidden = !table.hidden;
    if (!table.hidden) loadRunHistory();
  });

  el("seedInput").addEventListener("input", () => { seedDaSua = true; });

  initCsvImportHandlers();
}

function runPipelineFlow() {
  /* CHUP MOT LAN, dung suot ca luong. `buoiGuiDi()` doc trang thai dang
     chon TAI LUC GOI, nen hoi lai no o nut Xac nhan la hoi mot trang thai
     co the da khac: chon thu_5 -> bam Chay -> bam Chon tat ca -> bam Xac
     nhan thi ghi de CA TUAN, trong khi hop thoai vua hua giu nguyen cac
     buoi khac. Hua sai ve pham vi mot viec khong hoan tac duoc la dung
     cai ma tinh nang nay sinh ra de tranh. */
  const chiBuoi = buoiGuiDi();

  /* `[]` la TRUTHY trong JavaScript, nen khong chan o day thi nhanh
     "chay mot phan" chay voi danh sach rong: hop thoai hien ra KHONG NEU
     BUOI NAO, va phai di het mot vong len nen tang moi bao loi. */
  if (chiBuoi && chiBuoi.length === 0) {
    showToast(trErr({ code: "chua_chon_buoi_nao", params: {} }), "error");
    return;
  }

  /* Khoa nut Chay NGAY, truoc khi hoi phan loi. Khoa sau khi hoi (nhu
     truoc day) thi co mot khoang ho: bam dup lan chay dau tien (khong
     can xac nhan) la goi run_pipeline HAI lan. */
  if (khoa.dangHoiChay || khoa.dangChay) return;

  const seed = docHatGiong();
  if (seed === null) {
    showToast(t("hat_giong_khong_hop_le"), "error");
    baoLoiTaiO(el("seedInput"), () => t("hat_giong_khong_hop_le")); /* UX2-L4: lỗi ngay tại ô (toast giữ nguyên: ô nằm trong mục Nâng cao) */
    focusODau([el("seedInput")]);
    return;
  }

  datKhoa("dangHoiChay", true);

  callApi("get_pipeline_run_warning").then((warn) => {
    khoa.dangHoiChay = false;
    const wantsRedraw = forceRedrawArmed;
    const needsConfirm = (warn.ok && warn.data.has_existing_results) || wantsRedraw;

    if (!needsConfirm) {
      executeRun(seed, false, chiBuoi);
      return;
    }

    // Chèn thanh xác nhận ngay dưới nút, thay vì confirm() native.
    let bar = el("runConfirmBar");
    if (bar) bar.remove();
    bar = document.createElement("div");
    bar.id = "runConfirmBar";
    bar.className = "run-confirm-bar";
    const msg = document.createElement("span");
    /* Chạy một phần thì câu "sẽ GHI ĐÈ kết quả cũ" nói sai phạm vi: nó
       chỉ ghi đè những buổi đang chọn. Người vận hành đọc câu đó rồi
       huỷ vì tưởng mất hết các ngày đã công bố — đúng cái tính năng này
       sinh ra để tránh. Nêu đích danh buổi sẽ bị ghi đè. */
    const chon = chiBuoi;
    if (wantsRedraw) {
      msg.textContent = t("confirm_redraw_run");
    } else if (chon) {
      msg.textContent = t("confirm_overwrite_mot_phan")
        .replace("{buoi}", chon.map(nhanBuoi).join(", "));
    } else {
      msg.textContent = t("confirm_overwrite_run");
    }
    bar.appendChild(msg);
    const confirmBtn = document.createElement("button");
    confirmBtn.className = "btn btn-primary";
    confirmBtn.textContent = t("btn_confirm_run");
    confirmBtn.addEventListener("click", () => {
      confirmBtn.disabled = true;
      goThanhXacNhanNeuCo();
      executeRun(seed, wantsRedraw, chiBuoi);
    });
    const cancelBtn = document.createElement("button");
    cancelBtn.className = "btn btn-ghost";
    cancelBtn.textContent = t("btn_cancel");
    cancelBtn.addEventListener("click", () => goThanhXacNhanNeuCo());
    bar.appendChild(confirmBtn);
    bar.appendChild(cancelBtn);
    el("stepper").insertAdjacentElement("beforebegin", bar);
    capNhatKhoaVanHanh();
    confirmBtn.focus();
  });
}

function executeRun(seed, forceRedraw, chiBuoi) {
  resetSteps();
  showLog(null);
  datKhoa("dangChay", true);
  danhDauDangChay();

  /* Nhan `chiBuoi` tu tren xuong, KHONG goi lai `buoiGuiDi()`: con so
     gui di phai dung bang con so da hua o thanh xac nhan. */
  callApi("run_pipeline", seed, forceRedraw, chiBuoi).then((res) => {
    datKhoa("dangChay", false);
    const steps = (res.data && res.data.steps) || (res.errors && res.errors.steps) || [];
    // Xoa dau "dang chay" o nhung buoc phan loi khong bao lai (vd. dung som).
    resetSteps();
    renderSteps(steps);
    ux2DatPha("xong", steps, res.ok); /* UX2-L5: 4 pha suy tu danh sach buoc */

    if (res.ok) {
      const thongBao = t("toast_run_success", {
        n_matched: res.data.n_matched,
        n_total: res.data.n_total,
        rounds: res.data.rounds_run,
      });
      /* Chay xong nhung KHONG sao luu duoc truoc do: van la thanh cong,
         nhung nguoi dung phai biet minh dang khong co ban sao luu. */
      const saoLuuHong = steps.find((x) => x.step === "backup" && x.status === "error");
      if (saoLuuHong) {
        showToast(thongBao + "\n" + t("toast_run_success_no_backup"), "warn",
          [saoLuuHong.detail]);
      } else {
        lastRunXong = {
          n_matched: res.data.n_matched, n_total: res.data.n_total, rounds: res.data.rounds_run,
          path: res.data.export_path || null,
        };
        chiTietBuocMo = false;
        veRunXong();
      }
      showLog(null);
      seedDaSua = false;
      refreshDashboardStats();
      refreshStbLockLine();
      refreshSidebarStatus();
      if (!el("historyTable").hidden) loadRunHistory();
    } else {
      const errs = Array.isArray(res.errors) ? res.errors : [String(res.errors)];
      showToast(coLoiCsdlBan(errs) ? trErrs(errs).join(" ") : t("toast_run_failed"), "error");
      showLog(errs);
    }
  });
}

/* Hien nhan buoi cho nguoi doc, khong hien ma tho. Dong cu (truoc khi
   co cot nay) de trong — dung la "khong biet", va noi dung the con hon
   doan. Truong mot buoi cung de trong: o do khong co khai niem buoi. */
function nhanBuoiDaChay(gia_tri) {
  if (!gia_tri) return "—";
  const ds = String(gia_tri).split(",").filter(Boolean);
  if (!ds.length) return "—";
  if (ds.length === 1 && ds[0] === BUOI_MAC_DINH) return "—";
  return ds.map(nhanBuoi).join(", ");
}

/* T3-09: thẻ Lịch sử chỉ hiện khi đã có từ hai lần chạy; một lần thì thân bảng rỗng, chỉ thừa tiêu đề. */
function capNhatTheLichSu() {
  callApi("get_run_history", 2).then((res) => {
    const the = el("historyPanel");
    if (!the) return;
    the.hidden = !(res.ok && res.data.length >= 2);
    if (!the.hidden && !el("historyTable").hidden) loadRunHistory();
  });
}

function loadRunHistory() {
  const hoi = callApi("get_run_history", 20);
  hienKhungCho(el("historyTableBody"), 0, 5, hoi); /* UX2-L7 */
  hoi.then((res) => {
    const body = el("historyTableBody");
    clear(body);
    if (!res.ok || !res.data.length) {
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = 8;
      td.textContent = t("history_empty");
      tr.appendChild(td);
      body.appendChild(tr);
      return;
    }
    res.data.forEach((r) => {
      const tr = document.createElement("tr");
      tr.innerHTML =
        `<td>${esc(r.run_id)}</td><td>${esc(dinhDangGio(r.run_at))}</td><td>${esc(r.seed)}</td>` +
        `<td>${esc(r.rounds_run)}</td><td>${esc(r.n_matched)}</td><td>${esc(r.n_total)}</td>` +
        `<td>${esc(nhanBuoiDaChay(r.buoi_da_chay))}</td>` +
        `<td>${r.stb_redrawn ? esc(t("yes")) : esc(t("no"))}</td>`;
      body.appendChild(tr);
    });
  });
}

/* ---- Nạp dữ liệu: MỘT Sổ nhập CLB (so_nhap.py) ----
 *
 * Trước đây là ba tệp (danh sách CLB, chọn CLB dự thi, xếp hạng nguyện
 * vọng), mỗi tệp một bộ cột tiếng Anh, phải nạp đúng thứ tự. Ban giám khảo
 * chê đúng chỗ đó: một người vận hành không làm nổi. Giờ chỉ còn một sổ
 * Excel. Thả sổ vào -> phần mềm đọc thử (xem_truoc_so_nhap, không ghi gì)
 * -> hiện tóm tắt hoặc danh sách lỗi kèm sheet, dòng -> bấm Nhập.
 *
 * Sổ có lỗi thì nút Nhập bị khoá: nạp một nửa sổ còn tệ hơn không nạp.
 */

function initCsvImportHandlers() {
  const zone = el("dropZone");
  const input = el("fileAny");
  if (!zone || !input) return;

  /* SF-B8: `#fileAny` nằm TRONG `#dropZone`, nên `input.click()` nổi bọt lên đây và gọi `input.click()` lần hai.
     Bỏ qua cú bấm xuất phát từ chính ô chọn tệp: mỗi lần mở hộp chọn tệp chỉ gọi MỘT lần. */
  zone.addEventListener("click", (ev) => { if (ev.target !== input && !khoaVungTha()) input.click(); });
  zone.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter" || ev.key === " ") {
      ev.preventDefault();
      if (!khoaVungTha()) input.click();
    }
  });
  input.addEventListener("change", (ev) => {
    themFileVaoHangDoi(ev.target.files);
    input.value = ""; // cho phep tha lai dung file do
  });

  ["dragenter", "dragover"].forEach((e) =>
    zone.addEventListener(e, (ev) => {
      ev.preventDefault();
      if (!khoaVungTha()) zone.classList.add("is-dragover");
    })
  );
  ["dragleave", "drop"].forEach((e) =>
    zone.addEventListener(e, (ev) => {
      ev.preventDefault();
      zone.classList.remove("is-dragover");
    })
  );
  zone.addEventListener("drop", (ev) => {
    // Dang chay/dang nhap: tha tep vao luc nay la doi du lieu giua chung.
    if (khoaVungTha()) return;
    themFileVaoHangDoi(ev.dataTransfer && ev.dataTransfer.files);
  });

  el("btnImportAll").addEventListener("click", nhapTatCa);
  el("btnClearQueue").addEventListener("click", boHangDoiNhap);
  el("btnTaiSoMau").addEventListener("click", () => taiSoNhapMau("thuong"));
}

function boHangDoiNhap() {
  importQueue = [];
  tepBoQuaGanNhat = [];
  /* Tep dang doc do dang (Excel qua backend, nhan dien loai) se tu
     them vao hang doi khi doc xong — tuc la tep nguoi dung vua xoa
     lai hien ve va bi nhap. Doi the he de cac lan doc cu tu bo. */
  theHeHangDoi += 1;
  /* Xoa luon phan hoi va canh bao cua lan nhap truoc — de lai thi
     nguoi dung tuong ket qua do la cua danh sach dang co. */
  feedback(el("feedbackImportAll"), "", false);
  canhBaoNhapGanNhat = [];
  veCanhBaoNhap();
  veHangDoi();
}

/* Goi sau "Xoa toan bo du lieu". Truoc day the Van hanh chi cap nhat cac
   o so: danh sach tep "Da nhap", canh bao nhap, cac buoc "Xong", bang loi,
   so khoi tao cua lan chay cu va bo chon buoi cu van nam nguyen — nhin
   nhu du lieu chua he bi xoa. Moi thu tren the nay phai ve trang thai cua
   mot lan mo app voi CSDL trong. */
function donSachTheVanHanh() {
  boHangDoiNhap();
  goThanhXacNhanNeuCo();
  datCheDoVeLai(false);
  resetSteps();
  showLog(null);
  seedDaSua = false;
  el("seedInput").value = el("seedInput").defaultValue;
  refreshStbLockLine();
  loadChonBuoi({ datLai: true });
  if (!el("historyTable").hidden) loadRunHistory();
}

/* Chuyen ArrayBuffer -> base64 de gui file nhi phan qua cau noi JS/Python.
   Phai cat khuc: String.fromCharCode.apply co gioi han so doi so, file
   vai tram KB la tran ngan xep. */
function bufferSangBase64(buf) {
  const bytes = new Uint8Array(buf);
  const KHUC = 0x8000;
  let chuoi = "";
  for (let i = 0; i < bytes.length; i += KHUC) {
    chuoi += String.fromCharCode.apply(null, bytes.subarray(i, i + KHUC));
  }
  return btoa(chuoi);
}

function laFileExcel(ten) {
  return /\.(xlsx|xlsm)$/i.test(ten || "");
}

/* "Tai so nhap mau": phan mem tao so (co san cac CLB dang co) trong thu
   muc Tai xuong roi mo thu muc do — giao vien khong phai tu di tim. */
/* SM2: MỘT nút, sổ luôn đủ cấu trúc. `kieu` "huy_chuong" chỉ còn do lời nhắc sai chế độ (Cài đặt) gọi. */
function taiSoNhapMau(kieu) {
  const nut = el("btnTaiSoMau");
  nut.disabled = true;
  callApi("tao_so_nhap_mau", "", kieu || "thuong").then((res) => {
    nut.disabled = false;
    if (!res.ok) {
      feedbackErrors(el("feedbackImportAll"), res.errors);
      return;
    }
    const phu = res.data.n_ten_doi ? "\n" + t("xuat_kq_ten_doi", { n: res.data.n_ten_doi }) : "";
    const cau = t("so_mau_da_tao", { path: res.data.path, n: res.data.n_clubs }) + phu;
    feedback(el("feedbackImportAll"), cau, false);
    if (typeof nutDaXong === "function") nutDaXong(nut); /* SM2: dấu ✓ UX2 */
    /* FG-9: thong bao ngan (khong kem duong dan); duong day du o tooltip, nut "Mo thu muc". Van tu mo thu muc nhu truoc. */
    const moThuMuc = () => callApi("mo_thu_muc", res.data.path);
    showToast(t("so_mau_da_tao_ngan", { n: res.data.n_clubs }) + phu, "success",
      { hanhDong: { nhan: t("btn_mo_thu_muc"), khiBam: moThuMuc, tooltip: res.data.path } });
    moThuMuc();
  });
}

let theHeHangDoi = 0;

/* Hang doi chi giu MOT so: tha so moi la thay so cu. */
function themFileVaoHangDoi(fileList) {
  const files = Array.prototype.slice.call(fileList || []);
  if (!files.length) return;
  const file = files.find((f) => laFileExcel(f.name)) || files[0];
  tepBoQuaGanNhat = files.filter((f) => f !== file).map((f) => f.name);
  theHeHangDoi += 1;
  const theHe = theHeHangDoi;
  canhBaoNhapGanNhat = [];
  veCanhBaoNhap();
  feedback(el("feedbackImportAll"), "", false);

  if (!laFileExcel(file.name)) {
    importQueue = [{ ten: file.name, loiRaw: [{ code: "so_nhap_chi_nhan_xlsx", params: {} }] }];
    veHangDoi();
    return;
  }
  importQueue = [{ ten: file.name, dangDoc: true }];
  veHangDoi();

  const reader = new FileReader();
  reader.onload = () => {
    const b64 = bufferSangBase64(reader.result);
    callApi("xem_truoc_so_nhap", b64).then((res) => {
      if (theHe !== theHeHangDoi) return; /* da bo hoac da tha so khac */
      if (!res.ok) importQueue = [{ ten: file.name, loiRaw: res.errors }];
      else if (res.data.loi.length) {
        importQueue = [{ ten: file.name, loiRaw: res.data.loi, tomTat: res.data }];
      } else importQueue = [{ ten: file.name, b64: b64, tomTat: res.data }];
      veHangDoi();
    });
  };
  // Loi cua chinh trinh duyet: khong co khoa i18n nao, giu nguyen chuoi.
  reader.onerror = () => {
    if (theHe !== theHeHangDoi) return;
    importQueue = [{ ten: file.name, loiText: String(reader.error || "") }];
    veHangDoi();
  };
  reader.readAsArrayBuffer(file);
}

/* Canh bao cua lan nhap gan nhat — giu DANG GOC (mang doi tuong loi),
   dich lai moi lan ve. */
let canhBaoNhapGanNhat = [];
let tepBoQuaGanNhat = [];   /* ST-B-005: tên các tệp thả cùng lúc mà không được đọc */

function veCanhBaoNhap() {
  const box = el("importWarnings");
  if (!box) return;
  clear(box);
  box.hidden = canhBaoNhapGanNhat.length === 0;
  /* SG-7 (M1): cung luat voi buoc 4 — gom theo ma, dem, 5 vi du, "va N truong hop nua" (veCanhBaoGom o 00_nen.js). */
  const muc = canhBaoNhapGanNhat.map((w) => ({ ma: w.code, chu: trErr(w) }));
  /* UX1A-L5: hàng trăm cảnh báo "chưa dùng hết điểm" của từng người: thêm MỘT dòng tóm tắt lên đầu (danh sách gom
     5 ví dụ + "và N nữa" bên dưới giữ nguyên). */
  const chuaDu = canhBaoNhapGanNhat.filter((w) => w.code === "wharton_chua_dung_het").length;
  if (chuaDu > CANH_BAO_VD_TOI_DA) {
    const tomTat = document.createElement("div");
    tomTat.className = "canh-bao-tom-tat";
    tomTat.textContent = t("ux1a_wh_chua_du", { n: chuaDu });
    box.appendChild(tomTat);
  }
  veCanhBaoGom(box, muc);
}

/* So loi hien toi da bay nhieu dong; con lai gom thanh "va N loi khac". */
const SO_LOI_HIEN = 12;

function tomTatSo(d) {
  return t("so_nhap_tom_tat", {
    n_clb: d.n_clb, n_hoc_sinh: d.n_hoc_sinh, n_buoi: d.n_buoi,
    n_nguyen_vong: d.n_nguyen_vong, n_thi: d.n_thi,
  });
}

function veHangDoi() {
  const box = el("importQueue");
  const actions = el("importActions");
  clear(box);
  box.hidden = importQueue.length === 0;
  actions.hidden = importQueue.length === 0;
  capNhatKhoaVanHanh(); // T3-10: co tep cho nhap thi "Nhap so" la nut chinh
  if (!importQueue.length) return;

  const muc = importQueue[0];
  const row = document.createElement("div");
  row.className = "queue-row";
  const coLoi = !!(muc.loiRaw || muc.loiText);
  if (muc.xong) row.classList.add("is-done");
  else if (coLoi) row.classList.add("is-unknown");

  const trai = document.createElement("div");
  const ten = document.createElement("div");
  ten.className = "queue-file";
  ten.textContent = muc.ten;
  trai.appendChild(ten);

  const chiTiet = document.createElement("div");
  chiTiet.className = "queue-detail";
  // Dich LUC VE, khong cat cau da dich — doi ngon ngu thi ve lai dung tieng.
  if (muc.dangDoc) chiTiet.textContent = t("so_nhap_dang_doc");
  else if (muc.xong) chiTiet.textContent = t("so_nhap_xong", muc.ketQuaSo);
  else if (muc.loiText) chiTiet.textContent = muc.loiText;
  else if (muc.loiRaw) {
    chiTiet.textContent = muc.tomTat
      ? t("so_nhap_co_loi", { n: muc.loiRaw.length })
      : trErrs(muc.loiRaw).join(" ");
    ganChiTietKyThuat(chiTiet, muc.loiRaw);
  } else chiTiet.textContent = tomTatSo(muc.tomTat);
  trai.appendChild(chiTiet);

  /* ST-B-005: thả nhiều tệp một lần thì chỉ đọc MỘT: nói rõ tệp nào bị bỏ qua. */
  if (tepBoQuaGanNhat.length) {
    const bo = document.createElement("div");
    bo.className = "queue-detail";
    bo.textContent = t("so_nhap_bo_qua_tep", { n: tepBoQuaGanNhat.length, ten: tepBoQuaGanNhat.join(", ") });
    trai.appendChild(bo);
  }

  /* Sổ đọc được nhưng có lỗi: liệt kê từng lỗi kèm sheet, dòng. */
  if (muc.loiRaw && muc.tomTat && !muc.xong) {
    const ds = document.createElement("ul");
    ds.className = "so-nhap-loi";
    muc.loiRaw.slice(0, SO_LOI_HIEN).forEach((e) => {
      const li = document.createElement("li");
      li.textContent = trErr(e);
      ds.appendChild(li);
    });
    if (muc.loiRaw.length > SO_LOI_HIEN) {
      const li = document.createElement("li");
      li.textContent = t("so_nhap_loi_con_lai", { n: muc.loiRaw.length - SO_LOI_HIEN });
      ds.appendChild(li);
    }
    trai.appendChild(ds);
  }

  /* Sổ sạch nhưng nạp vào sẽ đổi dữ liệu đang có (xoá điểm, bỏ nhóm ưu
     tiên, CLB ngoài sổ): báo trước, KHÔNG chặn nút Nhập. */
  const canhBao = (muc.tomTat && muc.tomTat.canh_bao) || [];
  if (canhBao.length && !muc.loiRaw && !muc.xong) {
    const tieuDe = document.createElement("div");
    tieuDe.className = "so-nhap-canh-bao-tieu-de";
    tieuDe.textContent = t("so_nhap_canh_bao_tieu_de");
    trai.appendChild(tieuDe);
    const ds = document.createElement("ul");
    ds.className = "so-nhap-canh-bao";
    canhBao.forEach((w) => {
      const li = document.createElement("li");
      li.textContent = trErr(w);
      /* UX1A-L5: sổ có cột Huy chương / Loại mà chế độ huy chương tắt -> một nút bật (không bật ngầm). */
      if (w.code === "so_nhap_canh_bao_huy_chuong_che_do_tat" && typeof wsTrangThai !== "undefined" && wsTrangThai && wsTrangThai.enabled) {
        const nutBat = document.createElement("button");
        nutBat.type = "button";
        nutBat.id = "btnBatHuyChuong";
        nutBat.className = "btn btn-secondary btn-nho";
        nutBat.textContent = t("ux1a_btn_bat_huy_chuong");
        nutBat.addEventListener("click", () => batHuyChuongTuXemTruoc(muc, nutBat));
        li.append(" ", nutBat);
      }
      ds.appendChild(li);
    });
    trai.appendChild(ds);
  }
  row.appendChild(trai);
  box.appendChild(row);

  /* Chi nhap duoc so DA DOC, KHONG loi, CHUA nhap. */
  el("btnImportAll").hidden = !(muc.b64 && !muc.xong);
}

/* UX1A-L5: bật chế độ huy chương cho workspace đang mở bằng đường cấu hình sẵn có (quản trị, có dòng nhật ký),
   rồi đọc thử lại CHÍNH sổ đang chờ. Không bao giờ bật ngầm. */
function batHuyChuongTuXemTruoc(muc, nut) {
  nut.disabled = true;
  callApi("update_workspace_config", { rules: { wharton: true, fa_daa: true } }).then((r) => {
    if (!r.ok) { nut.disabled = false; showErrorToast(r.errors); return; }
    if (typeof ux1aApDungSong === "function") ux1aApDungSong(r.data.config);
    callApi("xem_truoc_so_nhap", muc.b64).then((res) => {
      if (res.ok && importQueue[0] === muc) {
        muc.tomTat = res.data;
        if (res.data.loi.length) { muc.loiRaw = res.data.loi; muc.b64 = ""; }
      }
      veHangDoi();
    });
  });
}

function nhapTatCa() {
  const muc = importQueue[0];
  if (!muc || !muc.b64 || muc.xong) {
    feedback(el("feedbackImportAll"), t("feedback_no_file_selected"), true);
    return;
  }
  datKhoa("dangNhap", true);
  canhBaoNhapGanNhat = [];
  veCanhBaoNhap();
  /* UX1A-L3 fix1: lần thử trước báo lỗi thì dòng đó còn nguyên; xoá trước khi thử lại (thành công không ghi dòng này). */
  feedback(el("feedbackImportAll"), "", false);

  callApi("import_so_nhap", muc.b64)
    .then((res) => {
      if (!res.ok || !res.data) {
        const loi = Array.isArray(res.errors) ? res.errors : [res.errors];
        feedbackErrors(el("feedbackImportAll"), loi);
        showToast(t("so_nhap_khong_nap"), "error");
        /* Lỗi CỦA SỔ (mã so_nhap_*): liệt kê, bắt sửa trong Excel. Lỗi phía
           phần mềm (CSDL bận…): sổ không sai — giữ tệp để bấm Nhập lại,
           đừng bảo người dùng đi sửa Excel. */
        if (loi.every((e) => e && String(e.code || "").indexOf("so_nhap_") === 0)) {
          muc.loiRaw = loi;
          muc.b64 = "";
        }
        return;
      }
      const d = res.data;
      muc.xong = true;
      // Cat KHOA + SO, khong cat cau da dich — xem veHangDoi().
      muc.ketQuaSo = {
        n_clb: d.n_clb, n_hoc_sinh: d.n_hoc_sinh,
        n_moi: d.n_students_created, n_bo: d.n_students_skipped,
      };
      canhBaoNhapGanNhat = d.warnings || [];
      /* UX1A-L3: kết quả (số CLB, số học sinh) hiện MỘT lần, ở hàng của tệp; thông báo nổi chỉ xác nhận, dòng
         phản hồi riêng bỏ (trước đây cùng một câu hiện ở ba nơi). */
      showToast(t("so_nhap_da_nap"), "success");
    })
    .catch((e) => {
      muc.loiText = String(e);
    })
    /* Mot buoc hong bat ngo thi van phai mo khoa — khong thi nut Nhap va
       vung tha tep bi khoa vinh vien toi khi mo lai app. */
    .then(() => {
      datKhoa("dangNhap", false);
      veHangDoi();
      veCanhBaoNhap();
      refreshDashboardStats();
      loadHealthReport(); // du lieu vua doi -> canh bao co the da khac
      /* So moi co the mang buoi moi vao: nap lai bo chon buoi va dat ve
         CHON HET — chay ca tuan an toan hon lang le bo sot buoi moi. */
      loadChonBuoi({ datLai: true });
    });
}
