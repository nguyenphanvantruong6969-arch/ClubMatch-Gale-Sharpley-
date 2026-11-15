#Requires -Version 7.2
<#
.SYNOPSIS
    Tự động làm SP02 đến SP09 (và bảng của PA16): tạo trang SharePoint, các bảng dữ liệu,
    cột, chỉ mục, chặn trùng, phân quyền, cách xem "Xuat_kiosk", và nạp danh sách từ CSV.

.DESCRIPTION
    - Chỉ TẠO MỚI và THÊM. Tệp lệnh này không xoá trang, bảng, cột hay dòng nào.
    - Chạy lại nhiều lần được: thứ gì đã có thì bỏ qua (dòng có mã đã tồn tại cũng bỏ qua).
    - Dùng -ChayThu để xem trước sẽ làm gì mà không ghi gì lên SharePoint.
    - Hướng dẫn chạy: SP00_tu_dong.md (cùng thư mục cha).

.NOTES
    Cần: PowerShell 7.4 trở lên, mô-đun PnP.PowerShell, một ứng dụng đăng ký trong Entra ID
    (lệnh Register-PnPEntraIDAppForInteractiveLogin), tài khoản quản trị SharePoint.
    Tên cột hiển thị phải khớp hợp đồng cột của rbda-kiosk: KHÔNG sửa các tên trong $BANG.
#>
[CmdletBinding()]
param(
    # Phần đầu địa chỉ SharePoint của trường. Ví dụ trường có https://truongabc.sharepoint.com thì ghi truongabc
    [Parameter(Mandatory)][string]$TenTenant,
    # Mã ứng dụng (Application/Client ID) lấy được khi đăng ký ứng dụng ở Bước 3 của SP00
    [Parameter(Mandatory)][string]$ClientId,
    # Thư điện tử người đứng tên chủ trang
    [Parameter(Mandatory)][string]$EmailChuTrang,
    # Tên trang (cũng là phần cuối địa chỉ trang)
    [string]$TenTrang = "CLB-2026",
    # Thư điện tử các giáo viên phụ trách (được toàn quyền trên trang)
    [string[]]$EmailGiaoVien = @(),
    # Nhóm tài khoản học sinh: thư điện tử của nhóm, hoặc mã đối tượng (Object ID) của nhóm
    [string]$NhomHocSinh = "",
    # Đường dẫn tệp CSV học sinh (cột: student_id,name,class_id,email,reserve_group)
    [string]$TepHocSinh = "",
    # Đường dẫn tệp CSV câu lạc bộ (cột: club_id,name,capacity,reserve_capacity,reserve_group,mo_ta,co_thi)
    [string]$TepCLB = "",
    # Có câu lạc bộ thi tuyển: tạo thêm bảng ChonThi (SP07)
    [switch]$CoThiTuyen,
    # Có bài thi trong ứng dụng (PA16): tạo thêm CauHoi, DapAn, BaiLam. Tự bật -CoThiTuyen
    [switch]$CoBaiThi,
    # Chỉ in ra việc sẽ làm, không ghi gì
    [switch]$ChayThu
)

$ErrorActionPreference = "Stop"
if ($CoBaiThi) { $CoThiTuyen = $true }

$thoiDiem = Get-Date -Format "yyyyMMdd_HHmmss"
$tepNhatKy = Join-Path (Get-Location) "nhat_ky_sharepoint_$thoiDiem.txt"
Start-Transcript -Path $tepNhatKy | Out-Null
try {

$soViecLam = 0
$soViecBoQua = 0

function Ghi([string]$chu, [string]$mau = "Gray") { Write-Host $chu -ForegroundColor $mau }
function BoQua([string]$chu) { $script:soViecBoQua++; Ghi "  = Đã có, bỏ qua: $chu" "DarkGray" }

# Mọi việc GHI đều đi qua hàm này, để -ChayThu chặn được.
function Lam([string]$moTa, [scriptblock]$viec) {
    $script:soViecLam++
    if ($ChayThu) { Ghi "  [THỬ] Sẽ làm: $moTa" "Yellow"; return $null }
    Ghi "  + $moTa" "Green"
    return & $viec
}

# ---------------------------------------------------------------------------
# Định nghĩa các bảng. Ten = tên hiển thị (khớp hợp đồng cột của kiosk, KHÔNG sửa).
# Noi = tên bên trong (chỉ đặt khi khác tên hiển thị, để tránh trùng tên có sẵn).
# Loai: Text (chữ ngắn), Note (đoạn văn), Number (số), Boolean (có/không), DateTime (ngày giờ).
# ---------------------------------------------------------------------------
function Cot([string]$ten, [string]$loai, [hashtable]$them = @{}) {
    $c = @{ Ten = $ten; Loai = $loai; BatBuoc = $false; SoLe = 0; Noi = $ten }
    foreach ($k in $them.Keys) { $c[$k] = $them[$k] }
    return $c
}

$pref = 1..10 | ForEach-Object { Cot "pref_$_" "Text" }
$thi = 1..5 | ForEach-Object { (Cot "test_club_$_" "Text"), (Cot "score_$_" "Number" @{ SoLe = 1 }) }

$BANG = [ordered]@{
    CLB        = @{
        Tieu = "club_id"; TieuBatBuoc = $true
        Cot = @(
            (Cot "name" "Text" @{ Noi = "ten"; BatBuoc = $true }),
            (Cot "capacity" "Number" @{ BatBuoc = $true }),
            (Cot "reserve_capacity" "Number"),
            (Cot "reserve_group" "Text"),
            (Cot "mo_ta" "Note"),
            (Cot "co_thi" "Boolean")
        )
        ChiMuc = @("club_id"); KhongTrung = @("club_id")
        XuatKiosk = @("club_id", "name", "capacity", "reserve_capacity", "reserve_group")
        Quyen = "Doc"
    }
    HocSinh    = @{
        Tieu = "student_id"; TieuBatBuoc = $true
        Cot = @(
            (Cot "name" "Text" @{ Noi = "ten"; BatBuoc = $true }),
            (Cot "class_id" "Text"),
            (Cot "email" "Text" @{ BatBuoc = $true }),
            (Cot "reserve_group" "Text")
        )
        ChiMuc = @("student_id", "email"); KhongTrung = @("student_id", "email")
        XuatKiosk = @()
        Quyen = "Doc"
    }
    NguyenVong = @{
        Tieu = "student_id"; TieuBatBuoc = $false
        Cot = @((Cot "name" "Text" @{ Noi = "ten" })) + $pref + @(
            (Cot "email" "Text"),
            (Cot "nop_luc" "DateTime"),
            (Cot "so_lan_nop" "Number")
        )
        ChiMuc = @("student_id"); KhongTrung = @("student_id")
        XuatKiosk = @("student_id", "name") + ($pref | ForEach-Object { $_.Ten })
        Quyen = "CuaMinh"
    }
}
if ($CoThiTuyen) {
    $BANG["ChonThi"] = @{
        Tieu = "student_id"; TieuBatBuoc = $false
        Cot = @((Cot "name" "Text" @{ Noi = "ten" })) + $thi
        ChiMuc = @("student_id"); KhongTrung = @("student_id")
        XuatKiosk = @("student_id", "name") + ($thi | ForEach-Object { $_.Ten })
        Quyen = "CuaMinh"
    }
}
if ($CoBaiThi) {
    $BANG["CauHoi"] = @{
        Tieu = "ma_cau"; TieuBatBuoc = $true
        Cot = @(
            (Cot "club_id" "Text"),
            (Cot "so_cau" "Number"),
            (Cot "cau_hoi" "Note"),
            (Cot "lua_chon_a" "Text"), (Cot "lua_chon_b" "Text"),
            (Cot "lua_chon_c" "Text"), (Cot "lua_chon_d" "Text")
        )
        ChiMuc = @("ma_cau", "club_id"); KhongTrung = @("ma_cau")
        XuatKiosk = @(); Quyen = "Doc"
    }
    $BANG["DapAn"] = @{
        Tieu = "ma_cau"; TieuBatBuoc = $true
        Cot = @((Cot "club_id" "Text"), (Cot "dap_an" "Text"))
        ChiMuc = @("ma_cau", "club_id"); KhongTrung = @("ma_cau")
        XuatKiosk = @(); Quyen = "ChiGiaoVien"
    }
    $BANG["BaiLam"] = @{
        Tieu = "student_id"; TieuBatBuoc = $false
        Cot = @(
            (Cot "name" "Text" @{ Noi = "ten" }),
            (Cot "club_id" "Text"),
            (Cot "ma_bai" "Text"),
            (Cot "tra_loi" "Note"),
            (Cot "nop_luc" "DateTime")
        )
        ChiMuc = @("ma_bai", "club_id", "student_id"); KhongTrung = @("ma_bai")
        XuatKiosk = @(); Quyen = "CuaMinh"
    }
}

function XmlCot([hashtable]$c) {
    $bb = if ($c.BatBuoc) { "TRUE" } else { "FALSE" }
    $chung = "DisplayName='$($c.Ten)' Name='$($c.Noi)' StaticName='$($c.Noi)' Required='$bb'"
    switch ($c.Loai) {
        "Text"     { return "<Field Type='Text' $chung MaxLength='255' />" }
        "Note"     { return "<Field Type='Note' $chung NumLines='6' RichText='FALSE' />" }
        "Number"   { return "<Field Type='Number' $chung Decimals='$($c.SoLe)' />" }
        "Boolean"  { return "<Field Type='Boolean' $chung><Default>0</Default></Field>" }
        "DateTime" { return "<Field Type='DateTime' $chung Format='DateTime' />" }
        default    { throw "Loại cột không biết: $($c.Loai)" }
    }
}

# Tìm cột theo TÊN HIỂN THỊ, trả về tên bên trong. Cột Title đã đổi tên trả về "Title".
function TenNoi([string]$bang, [string]$hienThi) {
    $f = Get-PnPField -List $bang | Where-Object {
        $_.Title -eq $hienThi -and -not $_.Hidden -and $_.InternalName -notlike "LinkTitle*"
    } | Select-Object -First 1
    if ($f) { return $f.InternalName } else { return $null }
}

function CoBang([string]$ten) {
    if (Get-PnPList -Identity $ten -ErrorAction SilentlyContinue) { return $true }
    Ghi "  [THỬ] Bảng $ten chưa có (sẽ được tạo), bỏ qua phần này." "Yellow"
    return $false
}

function DocCsv([string]$tep, [string[]]$cotCan) {
    if (-not (Test-Path $tep)) { throw "Không thấy tệp: $tep" }
    $dong1 = Get-Content -Path $tep -TotalCount 1 -Encoding UTF8
    $phan = if ($dong1 -match ";" -and $dong1 -notmatch ",") { ";" } else { "," }
    $rows = @(Import-Csv -Path $tep -Delimiter $phan -Encoding UTF8)
    if ($rows.Count -eq 0) { throw "Tệp trống: $tep" }
    $co = $rows[0].PSObject.Properties.Name | ForEach-Object { $_.Trim().TrimStart([char]0xFEFF) }
    $thieu = $cotCan | Where-Object { $_ -notin $co }
    if ($thieu) { throw "Tệp $tep thiếu cột: $($thieu -join ', '). Dòng đầu phải đúng: $($cotCan -join ',')" }
    return $rows
}

function GiaTri($r, [string]$cot) {
    $p = $r.PSObject.Properties | Where-Object { $_.Name.Trim().TrimStart([char]0xFEFF) -eq $cot } | Select-Object -First 1
    if ($p -and $null -ne $p.Value) { return ([string]$p.Value).Trim() } else { return "" }
}

# ---------------------------------------------------------------------------
Ghi ""
Ghi "=== Tạo môi trường SharePoint cho ứng dụng đăng ký câu lạc bộ ===" "Cyan"
if ($ChayThu) { Ghi "CHẾ ĐỘ CHẠY THỬ: không ghi gì lên SharePoint." "Yellow" }
Ghi "Nhật ký: $tepNhatKy"

$TenTenant = $TenTenant.Trim().ToLower() -replace "\.sharepoint\.com.*$", "" -replace "^https?://", ""
$diaChiQuanTri = "https://$TenTenant-admin.sharepoint.com"
$diaChiTrang = "https://$TenTenant.sharepoint.com/sites/$TenTrang"

if (-not (Get-Module -ListAvailable -Name PnP.PowerShell)) {
    throw "Chưa cài PnP.PowerShell. Làm Bước 2 trong SP00_tu_dong.md."
}
Import-Module PnP.PowerShell

# --- 1. Trang ---------------------------------------------------------------
Ghi ""
Ghi "[1/6] Trang SharePoint: $diaChiTrang" "Cyan"
Connect-PnPOnline -Url $diaChiQuanTri -Interactive -ClientId $ClientId
$trangCo = $null
try { $trangCo = Get-PnPTenantSite -Identity $diaChiTrang -ErrorAction Stop } catch { $trangCo = $null }

if ($trangCo) {
    BoQua "trang $TenTrang"
} else {
    Lam "Tạo trang $TenTrang (riêng tư, không kèm nhóm Microsoft 365, giao diện tiếng Anh)" {
        New-PnPSite -Type TeamSiteWithoutMicrosoft365Group -Title $TenTrang -Url $diaChiTrang `
            -Owner $EmailChuTrang -Lcid 1033 -Wait | Out-Null
    } | Out-Null
}

if ($ChayThu -and -not $trangCo) {
    Ghi ""
    Ghi "Trang chưa có nên không xem được bên trong. Sẽ tạo các bảng:" "Yellow"
    foreach ($ten in $BANG.Keys) {
        $b = $BANG[$ten]
        $dsCot = @($b.Tieu) + ($b.Cot | ForEach-Object { $_.Ten })
        Ghi "  [THỬ] Bảng $ten : $($dsCot -join ', ')" "Yellow"
    }
    Ghi "Chạy thử xong. Bỏ -ChayThu để làm thật." "Yellow"
    return
}

Connect-PnPOnline -Url $diaChiTrang -Interactive -ClientId $ClientId

# --- 2. Bảng và cột ---------------------------------------------------------
Ghi ""
Ghi "[2/6] Bảng dữ liệu và cột" "Cyan"
foreach ($ten in $BANG.Keys) {
    $b = $BANG[$ten]
    Ghi "Bảng $ten"
    $ds = Get-PnPList -Identity $ten -ErrorAction SilentlyContinue
    if ($ds) { BoQua "bảng $ten" }
    else {
        Lam "Tạo bảng $ten" { New-PnPList -Title $ten -Template GenericList | Out-Null } | Out-Null
        if ($ChayThu) { continue }
    }

    # Đổi tên cột Title
    $title = Get-PnPField -List $ten -Identity "Title"
    if ($title.Title -eq $b.Tieu) { BoQua "cột Title đã tên $($b.Tieu)" }
    else {
        Lam "Đổi tên cột Title thành $($b.Tieu)" {
            Set-PnPField -List $ten -Identity "Title" -Values @{ Title = $b.Tieu; Required = $b.TieuBatBuoc } | Out-Null
            foreach ($lt in "LinkTitle", "LinkTitleNoMenu") {
                try { Set-PnPField -List $ten -Identity $lt -Values @{ Title = $b.Tieu } | Out-Null }
                catch { Ghi "    (Không đổi được tên hiển thị của $lt, không ảnh hưởng)" "DarkYellow" }
            }
        } | Out-Null
    }

    # Thêm cột
    foreach ($c in $b.Cot) {
        if (TenNoi $ten $c.Ten) { BoQua "cột $($c.Ten)" ; continue }
        Lam "Thêm cột $($c.Ten) ($($c.Loai))" {
            Add-PnPFieldFromXml -List $ten -FieldXml (XmlCot $c) | Out-Null
        } | Out-Null
    }

    # Thứ tự cột ở cách xem mặc định
    if (-not $ChayThu) {
        $noi = @("LinkTitle") + ($b.Cot | ForEach-Object { TenNoi $ten $_.Ten })
        $vMacDinh = Get-PnPView -List $ten | Where-Object { $_.DefaultView } | Select-Object -First 1
        Lam "Sắp thứ tự cột ở cách xem mặc định" {
            Set-PnPView -List $ten -Identity $vMacDinh.Id -Fields $noi | Out-Null
        } | Out-Null
    }
}

# --- 3. Chỉ mục và chặn trùng -----------------------------------------------
Ghi ""
Ghi "[3/6] Chỉ mục và chặn trùng" "Cyan"
foreach ($ten in $BANG.Keys) {
    $b = $BANG[$ten]
    if (-not (CoBang $ten)) { continue }
    foreach ($hien in $b.ChiMuc) {
        $n = TenNoi $ten $hien
        if (-not $n) { Ghi "  ! Không thấy cột $hien ở bảng $ten" "Red"; continue }
        $f = Get-PnPField -List $ten -Identity $n
        if ($f.Indexed) { BoQua "chỉ mục $ten.$hien" }
        else { Lam "Đánh chỉ mục $ten.$hien" { Set-PnPField -List $ten -Identity $n -Values @{ Indexed = $true } | Out-Null } | Out-Null }
    }
    foreach ($hien in $b.KhongTrung) {
        $n = TenNoi $ten $hien
        if (-not $n) { continue }
        $f = Get-PnPField -List $ten -Identity $n
        if ($f.EnforceUniqueValues) { BoQua "chặn trùng $ten.$hien" }
        else { Lam "Chặn trùng $ten.$hien" { Set-PnPField -List $ten -Identity $n -Values @{ EnforceUniqueValues = $true } | Out-Null } | Out-Null }
    }
}

# --- 4. Cách xem để xuất CSV cho kiosk --------------------------------------
Ghi ""
Ghi "[4/6] Cách xem Xuat_kiosk (dùng khi tải CSV về)" "Cyan"
foreach ($ten in $BANG.Keys) {
    $b = $BANG[$ten]
    if (-not (CoBang $ten)) { continue }
    if ($b.XuatKiosk.Count -eq 0) { continue }
    if (Get-PnPView -List $ten -Identity "Xuat_kiosk" -ErrorAction SilentlyContinue) { BoQua "cách xem Xuat_kiosk của $ten"; continue }
    $noi = $b.XuatKiosk | ForEach-Object { if ($_ -eq $b.Tieu) { "LinkTitle" } else { TenNoi $ten $_ } }
    Lam "Tạo cách xem Xuat_kiosk cho $ten ($($b.XuatKiosk -join ', '))" {
        Add-PnPView -List $ten -Title "Xuat_kiosk" -Fields $noi -RowLimit 5000 | Out-Null
    } | Out-Null
}

# --- 5. Phân quyền ----------------------------------------------------------
Ghi ""
Ghi "[5/6] Phân quyền" "Cyan"
$vaiTro = @{}
Get-PnPRoleDefinition | ForEach-Object { $vaiTro[$_.RoleTypeKind.ToString()] = $_.Name }
$nhomChu = Get-PnPGroup -AssociatedOwnerGroup

foreach ($gv in $EmailGiaoVien) {
    $gv = $gv.Trim().ToLower()
    if (-not $gv) { continue }
    $thanhVien = Get-PnPGroupMember -Group $nhomChu | Where-Object { $_.Email -eq $gv }
    if ($thanhVien) { BoQua "giáo viên $gv trong nhóm chủ trang" }
    else { Lam "Thêm giáo viên $gv vào nhóm chủ trang ($($nhomChu.Title))" { Add-PnPGroupMember -LoginName $gv -Group $nhomChu | Out-Null } | Out-Null }
}

$dangNhapHS = $null
if ($NhomHocSinh) {
    $ung = @()
    if ($NhomHocSinh -match "^[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$") {
        $ung = @("c:0t.c|tenant|$NhomHocSinh", "c:0o.c|federateddirectoryclaimprovider|$NhomHocSinh")
    } else { $ung = @($NhomHocSinh.Trim()) }
    foreach ($u in $ung) {
        try { $dangNhapHS = (New-PnPUser -LoginName $u -ErrorAction Stop).LoginName; break } catch { }
    }
    if (-not $dangNhapHS) {
        Ghi "  ! Không tìm thấy nhóm học sinh '$NhomHocSinh'. Thử dùng mã đối tượng (Object ID) của nhóm. Bỏ qua phần quyền học sinh." "Red"
    } else { Ghi "  Nhóm học sinh: $dangNhapHS" }
} else {
    Ghi "  ! Không có -NhomHocSinh: bỏ qua phần quyền học sinh (làm tay theo SP09 sau)." "DarkYellow"
}

if ($dangNhapHS) {
    Lam "Cho nhóm học sinh quyền Xem trên cả trang" {
        Set-PnPWebPermission -User $dangNhapHS -AddRole $vaiTro["Reader"] | Out-Null
    } | Out-Null
}

foreach ($ten in $BANG.Keys) {
    $b = $BANG[$ten]
    if ($b.Quyen -eq "Doc") { continue }
    if (-not (CoBang $ten)) { continue }
    $ds = Get-PnPList -Identity $ten -Includes HasUniqueRoleAssignments, ReadSecurity, WriteSecurity

    if ($b.Quyen -eq "ChiGiaoVien") {
        if ($ds.HasUniqueRoleAssignments) { BoQua "bảng $ten đã tách quyền" }
        else {
            Lam "Bảng ${ten}: tách quyền, chỉ còn nhóm chủ trang (Full Control)" {
                Set-PnPList -Identity $ten -BreakRoleInheritance -ClearSubscopes | Out-Null
                Set-PnPListPermission -Identity $ten -Group $nhomChu -AddRole $vaiTro["Administrator"] | Out-Null
            } | Out-Null
        }
        continue
    }

    # CuaMinh: học sinh tạo và sửa phiếu của chính mình, chỉ xem phiếu của chính mình
    if ($ds.HasUniqueRoleAssignments) { BoQua "bảng $ten đã tách quyền" }
    else {
        Lam "Bảng ${ten}: tách quyền (giữ quyền đang có)" {
            Set-PnPList -Identity $ten -BreakRoleInheritance -CopyRoleAssignments | Out-Null
        } | Out-Null
    }
    if ($dangNhapHS) {
        Lam "Bảng ${ten}: nhóm học sinh được thêm và sửa (Contribute)" {
            Set-PnPListPermission -Identity $ten -User $dangNhapHS -AddRole $vaiTro["Contributor"] | Out-Null
        } | Out-Null
    }
    if ($ds.ReadSecurity -eq 2 -and $ds.WriteSecurity -eq 2) { BoQua "bảng ${ten}: quyền theo từng phiếu" }
    else {
        Lam "Bảng ${ten}: chỉ xem và sửa phiếu do chính mình tạo" {
            Set-PnPList -Identity $ten -ReadSecurity 2 -WriteSecurity 2 | Out-Null
        } | Out-Null
    }
}

# --- 6. Nạp dữ liệu từ CSV ---------------------------------------------------
Ghi ""
Ghi "[6/6] Nạp dữ liệu từ CSV" "Cyan"

function NapBang([string]$bang, [string]$tep, [string[]]$cotCan, [scriptblock]$chuyen) {
    if (-not $tep) { Ghi "  Không có tệp cho bảng $bang, bỏ qua."; return }
    if (-not (CoBang $bang)) { return }
    $rows = DocCsv $tep $cotCan
    $map = @{}
    foreach ($c in $cotCan) { $map[$c] = if ($c -eq $BANG[$bang].Tieu) { "Title" } else { TenNoi $bang $c } }

    $coSan = @{}
    if ($true) {
        Get-PnPListItem -List $bang -PageSize 500 -Fields "Title" | ForEach-Object { $coSan[[string]$_["Title"]] = $true }
    }
    $trongTep = @{}
    $them = 0; $bo = 0; $loi = 0
    $lo = if ($ChayThu) { $null } else { New-PnPBatch }
    $i = 1
    foreach ($r in $rows) {
        $i++
        $giaTri = & $chuyen $r
        if ($giaTri -is [string]) { Ghi "  ! Dòng $i bỏ qua: $giaTri" "Red"; $loi++; continue }
        $ma = $giaTri[$BANG[$bang].Tieu]
        if ($trongTep.ContainsKey($ma)) { Ghi "  ! Dòng $i bỏ qua: mã $ma bị trùng trong tệp" "Red"; $loi++; continue }
        $trongTep[$ma] = $true
        if ($coSan.ContainsKey($ma)) { $bo++; continue }
        $v = @{}
        foreach ($k in $giaTri.Keys) { $v[$map[$k]] = $giaTri[$k] }
        if ($ChayThu) { $them++; continue }
        Add-PnPListItem -List $bang -Values $v -Batch $lo | Out-Null
        $them++
    }
    if ($them -gt 0) {
        Lam "Bảng ${bang}: thêm $them dòng" { Invoke-PnPBatch -Batch $lo | Out-Null } | Out-Null
    }
    Ghi "  Bảng ${bang}: thêm $them, đã có (bỏ qua) $bo, lỗi $loi." $(if ($loi) { "Yellow" } else { "Gray" })
}

NapBang "CLB" $TepCLB @("club_id", "name", "capacity", "reserve_capacity", "reserve_group", "mo_ta", "co_thi") {
    param($r)
    $ma = GiaTri $r "club_id"
    if (-not $ma) { return "thiếu club_id" }
    if ($ma -notmatch "^[a-z0-9_]+$") { return "club_id '$ma' chỉ được dùng chữ thường không dấu, số, dấu gạch dưới" }
    $cap = 0
    if (-not [int]::TryParse((GiaTri $r "capacity"), [ref]$cap) -or $cap -le 0) { return "capacity của $ma phải là số nguyên lớn hơn 0" }
    $res = 0
    $resChu = GiaTri $r "reserve_capacity"
    if ($resChu -and (-not [int]::TryParse($resChu, [ref]$res) -or $res -lt 0 -or $res -gt $cap)) { return "reserve_capacity của $ma phải từ 0 đến $cap" }
    $thiChu = (GiaTri $r "co_thi").ToLower()
    $coThi = $thiChu -in @("yes", "y", "true", "1", "có", "co", "x")
    return @{ club_id = $ma; name = (GiaTri $r "name"); capacity = $cap; reserve_capacity = $res
              reserve_group = (GiaTri $r "reserve_group"); mo_ta = (GiaTri $r "mo_ta"); co_thi = $coThi }
}

NapBang "HocSinh" $TepHocSinh @("student_id", "name", "class_id", "email", "reserve_group") {
    param($r)
    $ma = GiaTri $r "student_id"
    if (-not $ma) { return "thiếu student_id" }
    $em = (GiaTri $r "email").ToLower()
    if ($em -notmatch "^[^@\s]+@[^@\s]+\.[^@\s]+$") { return "email của $ma không hợp lệ: '$em'" }
    if (-not (GiaTri $r "name")) { return "thiếu name của $ma" }
    return @{ student_id = $ma; name = (GiaTri $r "name"); class_id = (GiaTri $r "class_id")
              email = $em; reserve_group = (GiaTri $r "reserve_group") }
}

# ---------------------------------------------------------------------------
Ghi ""
Ghi "=== Xong ===" "Cyan"
Ghi "Số việc đã làm: $soViecLam · Số việc bỏ qua vì đã có: $soViecBoQua"
Ghi "ĐỊA CHỈ TRANG: $diaChiTrang" "Green"
if ($ChayThu) { Ghi "Đây là chạy thử. Bỏ -ChayThu để làm thật." "Yellow" }
}
finally {
    Stop-Transcript | Out-Null
}
