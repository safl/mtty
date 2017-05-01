default: install

install:
	mkdir -p /srv/wtty/output
	mkdir -p /srv/wtty/input
	touch /srv/wtty/input/ttyUSB0.in
	cp ./etc/wtty.conf /etc/
	cp ./etc/init.d/wtty-appd /etc/init.d/
	cp ./etc/init.d/wtty-iod /etc/init.d/
	update-rc.d wtty-iod defaults
	update-rc.d wtty-appd defaults
	pip install -r requirements.txt
	python setup.py install

start:
	service wtty-iod start
	service wtty-appd start

stop:
	service wtty-appd stop
	service wtty-iod stop

start_ubuntu:
	sudo ./etc/init.d/wtty-iod start
	sudo ./etc/init.d/wtty-appd start

stop_ubuntu:
	sudo ./etc/init.d/wtty-appd stop
	sudo ./etc/init.d/wtty-iod stop

clean:
	rm -r build
