#!/bin/sh

pacman -Qeti | awk '{
	if ($1 ~ "Name") pkg_name = $3
	else if ($1 ~ "Installed") {
		sep_len = 40 - length(pkg_name) - length($4)
		sep = ""
		for (i=0;i<sep_len;i++) sep = sep " "

		print pkg_name sep $4substr($5,0,1)
	}
}' | sort -hk2 # Sort (h)uman numerically, on the (2)nd (k)olumn.
