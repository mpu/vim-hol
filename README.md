## Interactive HOL Light in vim

The interactive mode is composed of a python wrapper for
HOL and a buffer-local vim mode providing key bindings
to interact with the live toplevel.

To install it, try:

    sudo ln -s `pwd`/replwrap/replwrap.py /usr/local/bin/replwrap
    mkdir -p ~/.vim
    cp vim/hol.vim ~/.vim
    echo ":command HOL :source $HOME/.vim/hol.vim" >> ~/.vim/vimrc

Interactive editing is done with two windows (or tmux panes),
one for the source file openned in vim and the other with the
ocaml toplevel with HOL loaded.

    # in the toplevel window
    replwrap -F hol -- ocaml
    # start HOL normally with #use "hol.ml";;

    # in the edit window
    vim arith.ml
    # in vim, load the interactive editing
    # mode by typing the command :HOL

You are now ready to start sending commands from the vim window
to the toplevel.

### Commands

Most commands will work in visual and normal mode; in visual mode
the data sent is the selection, in normal mode the current line
or word is sent.

Commands that accept input:

  - `\e` sends the line as tactic (strips THEN, unbalenced parens, ...)
  - `\s` sends the word as ML code
  - `\g` sends the line formula to `g`
  - `\h` shows help for a word

Control commands:

  - `\b` backs up one step in the proof
  - `\c` interrupts a long-running computation
  - `\p` prints the current goalstack
  - `\r` rotates the goalstack

Selection commands:

  - `\t` selects the enclosing quotation
