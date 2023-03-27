install-proxy::
	rm -r -f /usr/share/dhttp-proxy/
	mkdir -p /usr/share/dhttp-proxy/
	cp -r -f -v proxy/* /usr/share/dhttp-proxy/
	ln -f -s /usr/share/dhttp-proxy/proxy.py /usr/bin/dhttp-proxy
	cp -f proxy.service /etc/systemd/user/dhttp-proxy.service

install-static-server::
	rm -r -f /usr/share/dhttp-static/
	mkdir -p /usr/share/dhttp-static/
	cp -r -f -v server/* /usr/share/dhttp-static/
	ln -f -s /usr/share/dhttp-static/staticserver.py /usr/bin/dhttp-static
	cp -f dhttp-static.service /etc/systemd/user/dhttp-static.service