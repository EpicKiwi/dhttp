install-proxy::
	rm -r -f /usr/share/dhttp-proxy/
	mkdir -p /usr/share/dhttp-proxy/
	cp -r -f -v proxy/* /usr/share/dhttp-proxy/
	ln -f -s /usr/share/dhttp-proxy/proxy.py /usr/bin/dhttp-proxy
	cp -f proxy.service /etc/systemd/user/dhttp-proxy.service