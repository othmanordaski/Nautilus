# Nautilus Shell Completion
# Source this file in your shell configuration

_nautilus_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CURRENT]}"
    prev="${COMP_WORDS[COMP_CURRENT-1]}"
    
    opts="-h --help --version -c --continue -d --download -l --link -j --json -p --provider -q --quality -n --no-subs -e --edit"
    
    case "${prev}" in
        -p|--provider)
            COMPREPLY=( $(compgen -W "Vidcloud UpCloud" -- ${cur}) )
            return 0
            ;;
        -q|--quality)
            COMPREPLY=( $(compgen -W "360 480 720 1080 1440 2160 4k" -- ${cur}) )
            return 0
            ;;
        -d|--download)
            COMPREPLY=( $(compgen -d -- ${cur}) )
            return 0
            ;;
        *)
            ;;
    esac
    
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}

complete -F _nautilus_completion nautilus

# For zsh users, add this to ~/.zshrc:
# autoload -U +X compinit && compinit
# autoload -U +X bashcompinit && bashcompinit
# source /path/to/nautilus-completion.bash
