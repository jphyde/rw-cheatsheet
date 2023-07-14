#!/bin/sh

# Decrypt the file
mkdir $HOME/secrets
# --batch to prevent interactive command
# --yes to assume "yes" for questions
gpg --quiet --batch --yes --decrypt --passphrase="$GOOGLE_API_DECRYPT_PW" \
--output $HOME/secrets/rwcs-credentials.json rwcs-credentials.json.gpg