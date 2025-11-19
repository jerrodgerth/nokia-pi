# Utilities


- [Starship](https://starship.rs) prompt with [no-nerd-font](https://starship.rs/presets/no-nerd-font) preset
- [Fastfetch](https://github.com/fastfetch-cli/fastfetch) -- for system info 
- [btop](https://github.com/aristocratos/btop) -- a modern resource monitor 
- [lazydocker](https://github.com/jesseduffield/lazydocker) -- a TUI for all things docker
- [eza](https://eza.rocks) -- a modern, maintained replacement for `ls` 
- [zoxide](https://github.com/ajeetdsouza/zoxide) -- a smarter `cd` command 
- [bat](https://github.com/sharkdp/bat) -- a better `cat` 

And a [~/.bash_aliases](bash_aliases) file is included for some handy CLI shortcuts

```
# enable zoxide in place of cd
if command -v zoxide &> /dev/null; then
  alias cd="z"
  z() {
    if [ $# -eq 0 ]; then
      builtin cd ~ && return
    elif [ -d "$1" ]; then
      builtin cd "$1"
    else
      z "$@" && printf "\U000F17A9 " && pwd || echo "Error: Directory not found"
    fi
  }
fi

# use eza instead of ls
if command -v eza &> /dev/null; then
  alias ls='eza -lh --group-directories-first --icons=auto'
  alias ll='eza -lh --group-directories-first --icons=auto'
  alias la='ls -a'
  alias lt='eza --tree --level=2 --long --icons --git'
  alias lta='lt -a'
  alias tree='eza --tree'
fi

alias ..='cd ..'
alias ...='cd ../..'

alias mkp='mkdir -p'
alias rmf='rm -f'
alias rmr='rm -rf'
alias c='clear'
alias h='history'

alias bat='batcat'
alias b='batcat'
alias bt='btop'
alias fast='fastfetch'
alias lzd='lazydocker'
alias snake='nsnake'
```

