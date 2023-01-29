#!/bin/bash
ALLOWED_PYTHON_VERSION="3.8"
alias python3=python${ALLOWED_PYTHON_VERSION}
alias

[[ $ZSH_EVAL_CONTEXT =~ :file$ ]] && zsh_sourced=1 || zsh_sourced=0
am_I_sourced()
{
  if [ $zsh_sourced = 1 ]; then 
     echo "I am being sourced, zsh shell"
     return 0
  else
    if [ "${FUNCNAME[1]}" = source ]; then
      if [ "$1" = -v ]; then
        echo "I am being sourced, this filename is ${BASH_SOURCE[0]} and my caller script/shell name was $0"
      fi
      return 0
    else
      if [ "$1" = -v ]; then
        echo "I am not being sourced, my script/shell name was $0"
      fi
      return 1
    fi
  fi
}

if am_I_sourced -v; then

export PATH="/usr/local/opt/python@$ALLOWED_PYTHON_VERSION/bin:$PATH"
VIRTUAL_ENV="${VIRTUAL_ENV:-.venv}"
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[0:2])))')
if [ "$PYTHON_VERSION" != "$ALLOWED_PYTHON_VERSION" ]
then
  echo "$PYTHON_VERSION IS WRONG PYHTON VERSION!!!! IT SHOULD BE $ALLOWED_PYTHON_VERSION"
  echo "$PYTHON_VERSION IS WRONG PYHTON VERSION!!!! IT SHOULD BE $ALLOWED_PYTHON_VERSION"
  echo "$PYTHON_VERSION IS WRONG PYHTON VERSION!!!! IT SHOULD BE $ALLOWED_PYTHON_VERSION"
  return -1
fi
python3 -m pip install virtualenv --pre
python3 -m virtualenv ${VIRTUAL_ENV}
source ${VIRTUAL_ENV}/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install keyring artifacts-keyring --pre
tee ${VIRTUAL_ENV}/pip.conf <<EOF
[global]
index-url=https://pypi.org/simple
EOF
python3 -m pip install -r requirements.txt

  echo "Do something with sourced script"
else
  echo "Do something with executed script"
fi

