_c2llm_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    opts="fixed persistence browser status --help"
    
    # If it's the first argument after 'c2llm'
    if [[ ${COMP_CWORD} -eq 1 ]] ; then
        if [[ ${cur} == -* ]] ; then
            COMPREPLY=( $(compgen -W "--help" -- "${cur}") )
            return 0
        fi
        # Suggest subcommands AND files
        COMPREPLY=( $(compgen -W "${opts}" -- "${cur}") $(compgen -f -- "${cur}") )
        return 0
    fi
    
    # Subcommand specific logic
    case "${prev}" in
        fixed)
            COMPREPLY=( $(compgen -W "-a -rm" -- "${cur}") )
            return 0
            ;;
        persistence|browser)
            COMPREPLY=( $(compgen -W "toggle" -- "${cur}") )
            return 0
            ;;
        -a|-rm)
            COMPREPLY=( $(compgen -f -- "${cur}") )
            return 0
            ;;
        and|+|,)
            COMPREPLY=( $(compgen -f -- "${cur}") )
            return 0
            ;;
    esac
    
    # Default to file/directory completion for everything else
    COMPREPLY=( $(compgen -f -- "${cur}") )
}

complete -F _c2llm_completion c2llm
