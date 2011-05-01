all: static/wmd/wmd.combined.min.js static/wmd/wmd.css static/wmd/wmd-buttons.png

static/wmd/wmd.combined.min.js: wmd/wmd.combined.min.js
	cat $< | sed -e 's~images/~~g' > $@

static/wmd/wmd.css: wmd/wmd.css
	cat $< | sed -e 's~images/~~g' > $@

static/wmd/wmd-buttons.png: wmd/images/wmd-buttons.png
	cp -v $< $@

wmd/wmd.combined.min.js: wmd/wmd.combined.js wmd/jsmin.py
	cat $< | python wmd/jsmin.py > $@

wmd/wmd.combined.js: wmd/wmd.js wmd/showdown.js
	cat $^ > $@
