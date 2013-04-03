#!/usr/bin/make -f

INSTALL_DIR := install -d -m0755 -p
INSTALL_BIN := install -m0755 -p
INSTALL_DATA := install -m0644 -p

# Various bits to construct version.
VERSION ?= 0.0
RELEASE ?= 1

all: package
.PHONY: all

package: deb rpm
.PHONY: package

install-deb: src/vmsdoms.py src/vmsfs.py etc/collectd/vms-collectd-plugins.conf
	rm -rf dist-deb && $(INSTALL_DIR) dist-deb

	$(INSTALL_DIR) dist-deb/usr/lib/collectd
	$(INSTALL_DATA) src/vmsdoms.py dist-deb/usr/lib/collectd
	$(INSTALL_DATA) src/vmsfs.py dist-deb/usr/lib/collectd

	$(INSTALL_DIR) dist-deb/etc/collectd
	$(INSTALL_DATA) etc/collectd/vms-collectd-plugins.conf dist-deb/etc/collectd

deb: install-deb
	rm -rf debbuild && $(INSTALL_DIR) debbuild
	rsync -ruav packagers/deb/vms-collectd-plugins/ debbuild
	rsync -ruav dist-deb/* debbuild
	sed -i "s/VERSION/$(VERSION).$(RELEASE)/g" debbuild/DEBIAN/control
	dpkg -b debbuild/ .
.PHONY: deb

install-rpm:
	rm -rf dist-rpm && $(INSTALL_DIR) dist-rpm

	$(INSTALL_DIR) dist-rpm/var/lib/collectd
	$(INSTALL_DATA) src/vmsdoms.py dist-rpm/var/lib/collectd
	$(INSTALL_DATA) src/vmsfs.py dist-rpm/var/lib/collectd

	$(INSTALL_DIR) dist-rpm/etc/collectd.d
	$(INSTALL_DATA) etc/collectd/vms-collectd-plugins.conf dist-rpm/etc/collectd.d
	sed -i "s/\usr\/lib\/collectd\//var\/lib\/collectd\//g" dist-rpm/etc/collectd.d/vms-collectd-plugins.conf

rpm: install-rpm
	rm -rf rpmbuild
	$(INSTALL_DIR) rpmbuild/BUILD
	$(INSTALL_DIR) rpmbuild/BUILDROOT
	$(INSTALL_DIR) rpmbuild/RPMS/noarch
	$(INSTALL_DIR) rpmbuild/SOURCES
	$(INSTALL_DIR) rpmbuild/SPECS
	$(INSTALL_DIR) rpmbuild/SRPMS

	rpmbuild -bb --buildroot $(CURDIR)/rpmbuild/BUILDROOT \
          --define="%_topdir $(CURDIR)/rpmbuild" --define="%version $(VERSION).$(RELEASE)" \
	  --define="%release $(RELEASE)" packagers/rpm/vms-collectd-plugins.spec
	cp rpmbuild/RPMS/noarch/*.rpm .
.PHONY: rpm

clean:
	rm -rf *.deb debbuild dist-deb
	rm -rf *.rpm rpmbuild dist-rpm
.PHONY: clean
