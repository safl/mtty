default:

dev:
	sudo python setup.py install

start:
	sudo ./etc/init.d/wtty.io start
	./etc/init.d/wtty.app start

stop:
	sudo ./etc/init.d/wtty.io stop
	./etc/init.d/wtty.app stop

clean:
	rm -r build
