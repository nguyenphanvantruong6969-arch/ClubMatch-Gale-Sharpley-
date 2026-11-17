@echo off
REM QUEN_MAT_KHAU.bat - dat CANH PhanBoCauLacBo.exe. Dung khi quen mat khau quan tri.
REM Xoa TOAN BO tai khoan (quan tri + giao vien) sau khi sao luu. Ket qua xep, hoc sinh, CLB giu nguyen.
REM Hay DONG phan mem truoc. Sau do mo lai phan mem va tao tai khoan quan tri moi.
chcp 65001 >nul
echo ============================================================
echo  QUEN MAT KHAU QUAN TRI
echo  Se XOA TOAN BO tai khoan (quan tri va giao vien).
echo  Du lieu xep, hoc sinh, cau lac bo GIU NGUYEN; co sao luu truoc.
echo  Hay DONG phan mem truoc khi tiep tuc.
echo ============================================================
set /p XAC_NHAN="Go XOA roi bam Enter de xac nhan (bam Enter khong go gi = huy): "
if not "%XAC_NHAN%"=="XOA" (
  echo Da huy. Khong xoa gi.
  pause
  exit /b 1
)
del "%~dp0QUEN_MAT_KHAU_ket_qua.txt" >nul 2>nul
start "" /wait "%~dp0PhanBoCauLacBo.exe" --xoa-tai-khoan --yes
if exist "%~dp0QUEN_MAT_KHAU_ket_qua.txt" (
  type "%~dp0QUEN_MAT_KHAU_ket_qua.txt"
) else (
  echo Khong thay ket qua. Hay dam bao QUEN_MAT_KHAU.bat nam CANH PhanBoCauLacBo.exe.
)
pause
