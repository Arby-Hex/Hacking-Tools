install:
	pkg update -y && pkg upgrade -y

	# Install dependencies utama
	pkg install -y python python-pip nodejs-lts ruby wget clang git curl openssh termux-api

	# Library penting
	pkg install -y libjpeg-turbo libpng freetype zlib

	# Upgrade tools Python
	pip install --upgrade pip setuptools wheel

	# Install semua module Python yang diperlukan
	pip install \
		phonenumbers \
		flask \
		termux-api \
		requests \
		beautifulsoup4 \
		colorama \
		aiohttp \
		httpx \
		scapy \
		whois \
		rich \
		fake_useragent \
		pycryptodome \
		inquirer \
		sh \
		instaloader \
		python-whois \
		readchar \
		pytz \
		pystyle \
		rich \
		colorama \
		pyfiglet \
		

	# Clear layar dan tampilkan pesan akhir
	clear
	@echo "[*] Package & module berhasil diinstall.."
	@echo "[!] Run script dg ketik '\033[1;32mpython Sec_Dmn.pyc\033[0m'"
