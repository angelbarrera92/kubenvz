PLATFORM?=linux_x64

.PHONY: build package

build:
	@PYTHONOPTIMIZE=1 pyinstaller kubenvz.py --onefile --clean --osx-bundle-identifier com.nutellinoit.os.kubenvz --nowindowed
	@chmod +x dist/kubenvz

package:
	@cd dist && tar -czvf ./kubenvz_$(PLATFORM).tar.gz kubenvz