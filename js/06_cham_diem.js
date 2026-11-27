/* js/06_cham_diem.js — Thẻ 06 — Nhập điểm (chấm mù).

   Một phần của giao diện chính, tách từ app.js cũ. Các tệp js/ là SCRIPT
   THƯỜNG (không phải ES module) nạp theo đúng thứ tự trong index.html và
   dùng chung một phạm vi — như một tệp duy nhất trước đây. Không dùng ES
   module vì mở trang bằng file:// thì trình duyệt chặn chúng.
*/
"use strict";

/* ------------------------------------------------------------------ *
 * 7. TAB 5 — NHẬP ĐIỂM
 * ------------------------------------------------------------------ */

let currentScoringClub = null;

/* Luật chấm điểm của workspace đang mở (đặt bởi wsApDungCauHinh):
   theoNguoi = MỘT điểm cho cả người (không chấm từng CLB);
   an        = luật chỉ xếp theo nhóm, không dùng điểm, nên ẩn cả thẻ Nhập điểm. */
let LUAT_CHAM_DIEM = { theoNguoi: false, an: false };

function apDungLuatChamDiem(luat) {
  LUAT_CHAM_DIEM = {
    an: luat.priority === "tier",
    theoNguoi: luat.score_scope === "per_person" && luat.priority !== "tier",
  };
  const nut = document.querySelector('.nav-item[data-tab="scoring"]');
  if (nut) nut.hidden = LUAT_CHAM_DIEM.an;
}

function loadScoringTab() {
  el("scoringWorkArea").hidden = true;
  el("chuaLuuDiem").hidden = true;
  currentScoringClub = null;
  el("scoringClubPanel").hidden = LUAT_CHAM_DIEM.theoNguoi;
  el("scoringPersonArea").hidden = !LUAT_CHAM_DIEM.theoNguoi;
  if (LUAT_CHAM_DIEM.theoNguoi) {
    loadScoringPersons();
    return;
  }
  loadScoringOverview();
}

/* Chấm theo NGƯỜI: một ô điểm cho mỗi người. Vẫn chấm mù: chỉ mã và họ tên. */
/* UX2-L6: giao_vien thay huong dan (nho quan tri nap danh sach), khong thay nut cua quan tri. */
const UX2_RONG_CHAM_NGUOI = {
  chu: "scoring_person_empty", huongDan: "ux2_rong_huong_cham_nguoi",
  gv: { chu: "ux2_rong_chu_cham_nguoi_gv", huongDan: "ux2_rong_huong_cham_nguoi_gv" },
  nut: { nhan: "ux2_rong_nut_xep", quyen: "quan_tri", tab: "pipeline", oId: "dropZone" },
};

function loadScoringPersons() {
  return callApi("get_person_scoring_list").then((res) => {
    const body = el("scoringPersonBody");
    clear(body);
    const rong = !res.ok || !res.data.persons.length;
    if (rong) veTrangThaiRong(el("scoringPersonEmpty"), UX2_RONG_CHAM_NGUOI);
    el("scoringPersonEmpty").hidden = !rong;
    el("btnSavePersonScores").hidden = rong;
    el("scoringPersonProgress").textContent = rong ? "" : t("scoring_person_progress", {
      n_scored: res.data.n_scored, n: res.data.persons.length });
    if (!res.ok) {
      showErrorToast(res.errors);
      return;
    }
    res.data.persons.forEach((p) => {
      const tr = document.createElement("tr");
      const tdInput = document.createElement("td");
      const input = document.createElement("input");
      input.type = "text";           /* không dùng type="number": xem openScoringClub */
      input.inputMode = "decimal";
      input.className = "score-input";
      input.dataset.studentId = p.student_id;
      if (p.score !== null && p.score !== undefined) input.value = p.score;
      tdInput.appendChild(input);
      tr.innerHTML = `<td>${esc(p.student_id)}</td><td>${esc(p.name)}</td>`;
      tr.appendChild(tdInput);
      body.appendChild(tr);
    });
  });
}

function loadScoringOverview() {
  callApi("get_scoring_overview").then((res) => {
    const body = el("scoringOverviewBody");
    const emptyState = el("scoringOverviewEmpty");
    clear(body);
    const withApplicants = res.ok ? res.data.filter((c) => c.n_applicants > 0) : [];
    /* UX5B-L3: dòng trạng thái ("còn m CLB chưa chấm xong" hoặc "Đã chấm xong hết") và MỘT nút vàng "Chấm tiếp"
       ở CLB đầu tiên chưa chấm xong (Von Restorff); các nút "Chấm" còn lại là nút thường. */
    const chuaXong = withApplicants.filter((c) => c.n_scored < c.n_applicants);
    const dong = el("ux5bTtDiem");
    if (dong) dong.textContent = !withApplicants.length ? "" : chuaXong.length
      ? t("ux5b_tt_diem", { m: chuaXong.length }) : t("ux5b_tt_diem_xong");
    if (!res.ok || !withApplicants.length) {
      emptyState.hidden = false;
      return;
    }
    emptyState.hidden = true;
    withApplicants.forEach((c) => {
      const tr = document.createElement("tr");
      const tdProgress = document.createElement("td");
      tdProgress.textContent = `${c.n_scored}/${c.n_applicants}`;
      tr.innerHTML = `<td>${esc(c.name)}</td><td>${esc(c.n_applicants)}</td>`;
      tr.appendChild(tdProgress);
      const tdAction = document.createElement("td");
      const btn = document.createElement("button");
      const tiep = chuaXong.length > 0 && c === chuaXong[0];
      btn.className = (tiep ? "btn btn-primary" : "btn btn-secondary") + " btn-row-link";
      btn.textContent = t(tiep ? "ux5b_cham_tiep" : "btn_score_link");
      btn.addEventListener("click", () => openScoringClub(c.club_id));
      tdAction.appendChild(btn);
      tr.appendChild(tdAction);
      body.appendChild(tr);
    });
  });
}

function openScoringClub(clubId) {
  return callApi("get_club_applicants_for_scoring", clubId).then((res) => {
    if (!res.ok) {
      showErrorToast(res.errors);
      return;
    }
    currentScoringClub = clubId;
    el("scoringWorkArea").hidden = false;
    clearTimeout(choQuayLaiDiem);
    choQuayLaiDiem = null;
    el("scoringClubPanel").hidden = true;   /* UX5B-L3: đang chấm một CLB thì danh sách lui đi; nút "‹ Danh sách" đưa về */
    el("scoringClubLabel").textContent = `${res.data.club_name} (${res.data.club_id})`;

    const body = el("scoringTableBody");
    clear(body);
    res.data.applicants.forEach((a) => {
      const tr = document.createElement("tr");
      const tdInput = document.createElement("td");
      const input = document.createElement("input");
      /* KHONG dung type="number". Trinh duyet NUOT mat dau phay va con
         bao la hop le: go "8,5" thi .value tra ve "85" va
         validity.valid === true. Diem bi nhan len 10 lan, im lang. Da
         do trong Chromium that, ca locale en-US lan vi-VN.

         Ma "8,5" la cach viet thap phan BINH THUONG cua tieng Viet —
         khong phai go nham, ma go dung thoi quen rồi máy hiểu sai.
         Backend doc bang _doc_diem() nen nhan ca dau phay lan dau cham. */
      input.type = "text";
      input.inputMode = "decimal";   // may cam ung van hien ban phim so
      input.className = "score-input";
      input.dataset.studentId = a.student_id;
      if (a.score !== null && a.score !== undefined) input.value = a.score;
      input.dataset.cu = input.value;   /* UX5B-FIX1: giá trị đã lưu, để biết còn điểm chưa lưu */
      tdInput.appendChild(input);
      tr.innerHTML = `<td>${esc(a.student_id)}</td><td>${esc(a.name)}</td>`;
      tr.appendChild(tdInput);
      body.appendChild(tr);
    });
    veChuaLuuDiem();
  });
}

/* UX5B-FIX1: điểm gõ rồi mà chưa Lưu thì nút "‹ Danh sách" hỏi trước (bấm lần hai trong 4 giây mới bỏ), như thẻ Nhập nguyện vọng. */
let choQuayLaiDiem = null;
function diemChuaLuu() {
  return Array.from(document.querySelectorAll("#scoringTableBody .score-input")).some((i) => i.value !== (i.dataset.cu || ""));
}
function veChuaLuuDiem() {
  el("chuaLuuDiem").hidden = el("scoringWorkArea").hidden || !diemChuaLuu();
}

function initScoringHandlers() {
  /* UX5B-L3 (D4): lối quay về danh sách; dùng lại loadScoringTab nên tiến độ được nạp mới. */
  el("btnScoringQuayLai").addEventListener("click", () => {
    if (!el("scoringWorkArea").hidden && diemChuaLuu() && !choQuayLaiDiem) {
      showToast(t("ux5b_diem_chua_luu_canh_bao"), "warn");
      choQuayLaiDiem = setTimeout(() => { choQuayLaiDiem = null; }, 4000);
      return;
    }
    clearTimeout(choQuayLaiDiem);
    choQuayLaiDiem = null;
    loadScoringTab();
  });
  el("scoringTableBody").addEventListener("input", veChuaLuuDiem);
  window.addEventListener("langchange", () => {
    if (!el("scoringWorkArea").hidden || LUAT_CHAM_DIEM.theoNguoi) return;
    if (el("view-scoring").classList.contains("is-active")) loadScoringOverview();
  });
  el("btnSavePersonScores").addEventListener("click", () => {
    const inputs = document.querySelectorAll("#scoringPersonBody .score-input");
    inputs.forEach((input) => {
      xoaLoiTaiO(input);
      input.classList.remove("is-invalid");
      input.removeAttribute("title");
      input.removeAttribute("aria-invalid");
    });
    const scores = Array.from(inputs).map((input) => ({
      student_id: input.dataset.studentId,
      score: input.value === "" ? null : input.value,
    }));
    khiBan(el("btnSavePersonScores"), () => callApi("submit_person_scores", scores), { xongKhi: (r) => r && r.ok }).then((res) => {
      if (!res.ok) {
        feedbackErrors(el("scoringPersonFeedback"), res.errors);
        return;
      }
      const boQua = res.data.warnings || [];
      const oTheoMa = new Map(Array.from(inputs, (i) => [i.dataset.studentId, i]));
      boQua.forEach((w) => {
        const sid = w && w.params && w.params.student_id;
        const input = sid === undefined || sid === null ? null : oTheoMa.get(String(sid));
        if (!input) return;
        baoLoiTaiO(input, () => trErr(w), { them: ["is-invalid"], tieuDe: true }); /* UX2-L4: giữ is-invalid + title, thêm .loi-o */
      });
      focusODau(Array.from(inputs).filter((i) => i.__ux2Loi)); /* UX2-L4: con trỏ về ô sai đầu tiên */
      if (boQua.length) {
        const cau = t("feedback_scores_saved_mot_phan", { n: res.data.n_saved, k: boQua.length });
        feedback(el("scoringPersonFeedback"), cau, true);
        showToast(cau + "\n" + trErrs(boQua).join("\n"), "warn");
      } else {
        feedback(el("scoringPersonFeedback"), t("feedback_scores_saved", { n: res.data.n_saved }), false);
      }
      /* Chỉ làm mới dòng tiến độ: dựng lại bảng sẽ xoá dấu ô lỗi vừa đánh. */
      callApi("get_person_scoring_list").then((r) => {
        if (r.ok) el("scoringPersonProgress").textContent = t("scoring_person_progress", {
          n_scored: r.data.n_scored, n: r.data.persons.length });
      });
    });
  });

  el("btnSaveScores").addEventListener("click", () => {
    if (!currentScoringClub) return;
    const inputs = document.querySelectorAll("#scoringTableBody .score-input");
    inputs.forEach((input) => {
      xoaLoiTaiO(input);
      input.classList.remove("is-invalid");
      input.removeAttribute("title");
      input.removeAttribute("aria-invalid");
    });
    const scores = Array.from(inputs).map((input) => ({
      student_id: input.dataset.studentId,
      score: input.value === "" ? null : input.value,
    }));
    khiBan(el("btnSaveScores"), () => callApi("submit_club_scores", currentScoringClub, scores), { xongKhi: (r) => r && r.ok }).then((res) => {
      if (res.ok) {
        const boQua = res.data.warnings || [];
        if (boQua.length) {
          /* O nao bi bo qua thi TO DO dung o do, kem ly do. Truoc day chi
             bao ly do cua o DAU TIEN trong mot thong bao 3,6 giay, con dong
             chu xanh "Da luu" khien nguoi cham tuong da luu het. */
          const oTheoHs = new Map(Array.from(inputs, (i) => [i.dataset.studentId, i]));
          boQua.forEach((w) => {
            const sid = w && w.params && w.params.student_id;
            const input = sid === undefined || sid === null ? null : oTheoHs.get(String(sid));
            if (!input) return;
            baoLoiTaiO(input, () => trErr(w), { them: ["is-invalid"], tieuDe: true }); /* UX2-L4: giữ is-invalid + title, thêm .loi-o */
          });
          focusODau(Array.from(inputs).filter((i) => i.__ux2Loi)); /* UX2-L4: con trỏ về ô sai đầu tiên */
          const cau = t("feedback_scores_saved_mot_phan", { n: res.data.n_saved, k: boQua.length });
          feedback(el("scoringFeedback"), cau, true);
          showToast(cau + "\n" + trErrs(boQua).join("\n"), "warn");
        } else {
          feedback(el("scoringFeedback"), t("feedback_scores_saved", { n: res.data.n_saved }), false);
        }
        /* UX5B-FIX1: ô đã lưu (không bị đánh lỗi) thành giá trị "đã lưu" mới */
        inputs.forEach((i) => { if (!i.__ux2Loi) i.dataset.cu = i.value; });
        veChuaLuuDiem();
        loadScoringOverview();
      } else {
        /* Khong luu duoc dong nao vi o sai: to do dung cac o do (nhu nhanh luu mot phan). */
        const oTheoHs = new Map(Array.from(inputs, (i) => [i.dataset.studentId, i]));
        (res.errors || []).forEach((w) => {
          const sid = w && w.params && w.params.student_id;
          const input = sid === undefined || sid === null ? null : oTheoHs.get(String(sid));
          if (!input) return;
          baoLoiTaiO(input, () => trErr(w), { them: ["is-invalid"], tieuDe: true }); /* UX2-L4: giữ is-invalid + title, thêm .loi-o */
        });
        focusODau(Array.from(inputs).filter((i) => i.__ux2Loi)); /* UX2-L4: con trỏ về ô sai đầu tiên */
        feedbackErrors(el("scoringFeedback"), res.errors);
        /* Nhu nhanh luu mot phan: mot thong bao neu HET cac o sai, khong chi o dau tien. */
        if (res.errors && res.errors.some((w) => w && w.params && w.params.student_id !== undefined)) {
          showToast(trErrs(res.errors).join("\n"), "warn");
        }
      }
    });
  });
}
