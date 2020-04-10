"if exists("b:did_hol")
"  finish
"endif

let s:defaultholpipe = "/tmp/replfifo"
if empty($VIMHOL_FIFO)
  let s:holpipe = s:defaultholpipe
else
  let s:holpipe = $VIMHOL_FIFO
endif

new
setlocal buftype=nofile
setlocal bufhidden=hide
setlocal nobuflisted
setlocal noswapfile
let s:holnr = bufnr("")
hide

let s:tmpprefix = "/tmp/vimhol"
function! TempName()
  let l:n = 0
  while glob(s:tmpprefix.l:n."Message.ml") != ""
    let l:n = l:n + 1
  endwhile
  return s:tmpprefix.l:n."Message.ml"
endf

function! HOLCStart()
  let s:prev = bufnr("")
  let s:wins = winsaveview()
  silent exe "keepjumps hide bu" s:holnr
  setlocal foldmethod=manual
  keepjumps %d_
endf

function! HOLCRestore()
  silent exe "w>>" . s:holpipe
  silent exe "keepjumps bu" s:prev
  call winrestview(s:wins)
endf

function! HOLCEnd(c)
  let s:temp = TempName()
  silent exe "w" . s:temp
  keepjumps %d_
  silent exe "normal i" . a:c . s:temp
  call HOLCRestore()
endf

function! HOLSend(c)
  call HOLCStart()
  silent exe "normal i" . a:c
  call HOLCRestore()
endf

function! HOLSendPaste(c)
  silent normal gvy
  call HOLCStart()
  silent exe "normal i" . a:c
  silent normal p
  call HOLCRestore()
endf

function! HOLSendFile(c) range
  silent normal gvy
  call HOLCStart()
  silent normal P
  call HOLCEnd(a:c)
  exe "normal gv\<Esc>"
endf

function! HOLSelect(l,r)
  let l:cursor = getpos(".")
  if search(a:l,"Wbc") == 0
    return
  endif
  normal v
  if search(a:r,"W") == 0
    normal <ESC>
    call setpos('.', l:cursor)
    return
  endif
  call search(a:r,"ce")
endf

if !(exists("maplocalleader"))
  let maplocalleader = "\\"
endif

vmap <silent><buffer> <LocalLeader>e :call HOLSendFile("E")<CR>
vmap <silent><buffer> <LocalLeader>s :call HOLSendFile("S")<CR>
vmap <silent><buffer> <LocalLeader>g :call HOLSendFile("G")<CR>
vmap <silent><buffer> <LocalLeader>h :call HOLSendPaste("h")<CR>

nmap <silent><buffer><expr> <LocalLeader>e "V".maplocalleader."e"
nmap <silent><buffer><expr> <LocalLeader>s "V".maplocalleader."s"
nmap <silent><buffer><expr> <LocalLeader>g "V".maplocalleader."g"
nmap <silent><buffer><expr> <LocalLeader>h "viw".maplocalleader."h"

nmap <silent><buffer> <LocalLeader>b :call HOLSend("b")<CR>
nmap <silent><buffer> <LocalLeader>c :call HOLSend("c")<CR>
nmap <silent><buffer> <LocalLeader>p :call HOLSend("p")<CR>
nmap <silent><buffer> <LocalLeader>r :call HOLSend("r")<CR>
nmap <silent><buffer> <LocalLeader>t :call HOLSelect('`\\|‘','`\\|’')<CR>
nmap <silent><buffer> <LocalLeader>T :call HOLSelect('``\\|“','``\\|”')<CR>

let b:did_hol = 1
