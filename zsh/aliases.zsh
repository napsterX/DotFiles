###############################################
#   Some of the aliases I use                 #
###############################################

# Kubernetes aliases

alias kdp='kubectl describe pods'
alias kgp='kubectl get pods'
alias kl='kubectl logs'
alias cl='/Users/manish/.local/bin/claude'

# Local Alias
alias -s rb=vim
alias -s log="less -MN"
alias grep='grep  --color=auto --exclude-dir={.bzr,CVS,.git,.hg,.svn}'
alias egrep='egrep --color'
alias 'cd..=cd ..'
alias 'g'='git'
alias 'gg'='git grep'
#alias 'g st'='git status'
#alias 'glo'='git log'
#alias 'g di'='git diff'
alias 'grp'='git reset --hard HEAD~1 ; git pull'
alias ping='ping -c 100000'
alias dmesg='dmesg --color --reltime'

alias bypass='sudo /System/Library/Extensions/TMSafetyNet.kext/Helpers/bypass'
alias port='sudo port'
alias glist=/Users/mankumar/code/itops/python/glulist
alias smcli='smcli --post_review_path=/usr/local/bin/post-review --rbt_path /usr/local/bin/rbt'

# Global Aliases
alias -g gi='| grep -i'

# Flush Directory Service cache
alias flush="dscacheutil -flushcache && killall -HUP mDNSResponder"

# Show active network interfaces
alias ifactive="ifconfig | pcregrep -M -o '^[^\t:]+:([^\n]|\n\t)*status: active'"

# IP addresses
alias ip="dig +short myip.opendns.com @resolver1.opendns.com"
alias localip="ipconfig getifaddr en0"
alias ips="ifconfig -a | grep -o 'inet6\? \(addr:\)\?\s\?\(\(\([0-9]\+\.\)\{3\}[0-9]\+\)\|[a-fA-F0-9:]\+\)' | awk '{ sub(/inet6? (addr:)? ?/, \"\"); print }'"

# Show/hide hidden files in Finder
alias show="defaults write com.apple.finder AppleShowAllFiles -bool true && killall Finder"
alias hide="defaults write com.apple.finder AppleShowAllFiles -bool false && killall Finder"

# Intuitive map function
# For example, to list all directories that contain a certain file:
# find . -name .gitattributes | map dirname
alias map="xargs -n1"

# Lock the screen (when going AFK)
alias afk="/System/Library/CoreServices/Menu\ Extras/User.menu/Contents/Resources/CGSession -suspend"

# Print each PATH entry on a separate line
alias path='echo -e ${PATH//:/\\n}'

# kubeclt aliases
alias k=kubectl
#complete -F __start_kubectl k

# Minio aliases
alias minfo='mc admin info'
alias mheal='mc admin heal'
