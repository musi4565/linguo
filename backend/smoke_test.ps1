$ErrorActionPreference = "Stop"
$Base = "http://127.0.0.1:8001/api"

function Post($url, $body, $token) {
    $headers = @{"Content-Type" = "application/json"}
    if ($token) { $headers["Authorization"] = "Bearer $token" }
    return Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body ($body | ConvertTo-Json) -UseBasicParsing
}
function Get($url, $token) {
    $headers = @{}
    if ($token) { $headers["Authorization"] = "Bearer $token" }
    return Invoke-RestMethod -Uri $url -Method Get -Headers $headers -UseBasicParsing
}
function Delete($url, $token) {
    $headers = @{Authorization = "Bearer $token"}
    return Invoke-RestMethod -Uri $url -Method Delete -Headers $headers -UseBasicParsing
}

$email = "testuser$(Get-Random)@linguo.uz"

Write-Host "== 1. Register =="
$reg = Post "$Base/auth/register/" @{name = "Test Foydalanuvchi"; email = $email; password = "Parol12345!"}
$token = $reg.access
Write-Host "OK user id=$($reg.user.id) name=$($reg.user.name)"

Write-Host "== 2. Login =="
$login = Post "$Base/auth/login/" @{email = $email; password = "Parol12345!"}
if (-not $login.access) { throw "login failed" }
Write-Host "OK access token olindi"

Write-Host "== 3. Refresh =="
$rf = Post "$Base/auth/refresh/" @{refresh = $login.refresh}
if (-not $rf.access) { throw "refresh failed" }
$token = $rf.access
Write-Host "OK yangi access token"

Write-Host "== 4. Languages =="
$langs = Get "$Base/languages/" $token
Write-Host "OK $($langs.Count) ta til: $(($langs | ForEach-Object { $_.name }) -join ', ')"
$langId = $langs[0].id

Write-Host "== 5. Language books =="
$books = Get "$Base/languages/$langId/books/" $token
Write-Host "OK '$($books.name)': $($books.books.Count) kitob; birinchisi: $($books.books[0].topic) featured=$($books.books[0].is_featured)"
$bookId = $books.books[0].id

Write-Host "== 6. Book detail =="
$book = Get "$Base/books/$bookId/" $token
Write-Host "OK bo'limlar soni=$($book.sections.Count); 1-bo'lim gaplar=$($book.sections[0].sentences.Count); audio=$($book.sections[0].audio_url)"

Write-Host "== 7. Progress save =="
$pr = Post "$Base/progress/" @{book_id = $bookId; section_id = $book.sections[0].id; percent = 25} $token
Write-Host "OK percent=$($pr.percent_complete)"

Write-Host "== 8. Progress summary =="
$sum = Get "$Base/progress/summary/" $token
Write-Host "OK overall=$($sum.overall_percent)%"

Write-Host "== 9. Bookmarks =="
$bm = Post "$Base/bookmarks/" @{book_id = $bookId} $token
$bms = Get "$Base/bookmarks/" $token
Delete "$Base/bookmarks/$($bms[0].id)/" $token | Out-Null
Write-Host "OK qo'shildi va o'chirildi"

Write-Host "== 10. Saved words =="
$sw = Post "$Base/saved-words/" @{language_id = $langId; word = "hello"; translation = "salom"} $token
$sws = Get "$Base/saved-words/" $token
Write-Host "OK $($sws.Count) ta so'z: $($sws[0].word) -> $($sws[0].translation)"

Write-Host "== 11. Log session + stats =="
Post "$Base/stats/log-session/" @{minutes = 5; language_id = $langId} $token | Out-Null
$daily = Get "$Base/stats/daily/" $token
$weekly = Get "$Base/stats/weekly/" $token
$byLang = Get "$Base/stats/by-language/" $token
Write-Host "daily: streak=$($daily.streak) minutes=$($daily.total_minutes) words=$($daily.words_learned)"
Write-Host "weekly bugun: $($weekly.today_minutes) daqiqa"
Write-Host "by-language: $($byLang.languages[0].name) = $($byLang.languages[0].percent)%"

Write-Host "== 12. Profile =="
$prof = Get "$Base/profile/" $token
Write-Host "OK profil: $($prof.user.email), oy: $($prof.month.minutes_spent) daqiqa, streak=$($prof.streak)"
$ach = Get "$Base/achievements/" $token
Write-Host "OK yutuqlar: $(($ach | Where-Object { $_.earned }).Count)/$($ach.Count) olingan"

Write-Host "== 13. Password change =="
$headers = @{"Content-Type" = "application/json"; Authorization = "Bearer $token"}
$pwBody = @{old_password = "Parol12345!"; new_password = "YangiParol12345!"} | ConvertTo-Json
Invoke-RestMethod -Uri "$Base/profile/password/" -Method Patch -Headers $headers -Body $pwBody -UseBasicParsing | Out-Null
Write-Host "OK parol o'zgartirildi"
Post "$Base/auth/login/" @{email = $email; password = "YangiParol12345!"} | Out-Null
Write-Host "OK yangi parol bilan kirish"
Post "$Base/auth/logout/" @{refresh = $rf.refresh} $token | Out-Null
Write-Host "OK logout"

Write-Host ""
Write-Host "BARCHA TESTLAR O'TDI ✔" -ForegroundColor Green

