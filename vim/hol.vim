if exists("b:did_hol")
  finish
endif

let s:defaultholpipe = "/tmp/vimholfifo"
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
fu! TempName()
  let l:n = 0
  while glob(s:tmpprefix.l:n."Message") != ""
    let l:n = l:n + 1
  endwhile
  return s:tmpprefix.l:n."Message"
endf

fu! HOLCStart()
  let s:prev = bufnr("")
  let s:wins = winsaveview()
  silent exe "keepjumps hide bu" s:holnr
  setlocal foldmethod=manual
  keepjumps %d_
endf

fu! HOLCRestore()
  silent exe "w>>" . s:holpipe
  silent exe "keepjumps bu" s:prev
  call winrestview(s:wins)
endf

fu! HOLCEnd(c)
  let s:temp = TempName()
  silent exe "w" . s:temp
  keepjumps %d_
  silent exe "normal i" . a:c . s:temp
  call HOLCRestore()
endf

fu! HOLSend(c)
  call HOLCStart()
  silent exe "normal i" . a:c
  call HOLCRestore()
endf

fu! HOLSendFile(c) range
  silent normal gvy
  call HOLCStart()
  silent normal P
  call HOLCEnd(a:c)
  exe "normal gv\<Esc>"
endf

fu! HOLSelect(l,r)
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

vn <silent> <LocalLeader>e :call HOLSendFile("E")<CR>
vn <silent> <LocalLeader>s :call HOLSendFile("S")<CR>
vn <silent> <LocalLeader>g :call HOLSendFile("G")<CR>

nm <silent><expr> <LocalLeader>e "V".maplocalleader."e"
nm <silent><expr> <LocalLeader>s "V".maplocalleader."s"
nm <silent><expr> <LocalLeader>g "V".maplocalleader."g"

nn <silent> <LocalLeader>p :call HOLSend("p")<CR>
nn <silent> <LocalLeader>c :call HOLSend("c")<CR>
nn <silent> <LocalLeader>t :call HOLSelect('`\\|‘','`\\|’')<CR>
nn <silent> <LocalLeader>T :call HOLSelect('``\\|“','``\\|”')<CR>

no <LocalLeader>h h

let b:did_hol = 1
" vim: ft=vim
