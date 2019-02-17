(function(f) {
   	function e(a, b) {
   		this.seed instanceof e ? this.seed.init(a, b) : this instanceof e ? this.init(a, b) : this.seed = new e(a, b);
   		return this.seed
   	}

   	function x(a) {
   		this.appnm = a;
   		this.sendQueue = {}
   	}

   	function n(a, b) {
   		this.batchs = [];
   		this.project = "Yoda-FE";
   		this.catVersion = 1;
   		this.origin = window.location.origin;
   		this.unionId = a || "";
   		this.env = "pro" === b ? "pro" : "dev";
   		this.host = {
   			pro: "//catfront.dianping.com",
   			dev: "//catfront.51ping.com"
   		}[this.env];
   		var c = this;
   		setTimeout(function() {
   			c.sendBatch()
   		}, 500)
   	}

   	function F(a, b, c) {
   		if ("object" ===
   			typeof b) {
   			var d = [],
   				p;
   			for (p in b) d.push(encodeURIComponent(p) + "=" + encodeURIComponent(b[p]));
   			b = d.join("&")
   		}
   		d = {
   			"Content-Type": "application/x-www-form-urlencoded"
   		};
   		try {
   			var C = Date.now(),
   				h = new f.XMLHttpRequest;
   			if ("withCredentials" in h) {
   				h.open("post", a, !0);
   				if (d)
   					for (var g in d) d.hasOwnProperty(g) && h.setRequestHeader(g, d[g]);
   				h.onload = function() {
   					4 === h.readyState && (200 <= h.status && 300 > h.status || 304 === h.status) && (c(h.responseText), h = null)
   				}
   			} else if ("undefined" !== typeof f.XDomainRequest) {
   				h = new f.XDomainRequest;
   				var e = 0 < a.indexOf("?") ? "&" + b : "?" + b;
   				h.open("get", a + e);
   				h.onload = function() {
   					c(h.responseText);
   					h = null
   				}
   			} else throw Error("\u79cd\u5b50\u4ee3\u7801\u521b\u5efaXMLHttpRequest\u5bf9\u8c61\u5931\u8d25");
   			h.onerror = function(a) {
   				h.abort();
   				throw Error("XMLHttpRequest\u8bf7\u6c42\u670d\u52a1\u5668\u53d1\u751f\u5f02\u5e38" + a.message);
   			};
   			h.send(b)
   		} catch (G) {
   			throw window.Yoda.CAT.postBatch(a, 0, 0, Date.now() - C, "500|0", "ajax"), window.Yoda.CAT.sendBatch(), window.Yoda.CAT.sendLog(a, "ajaxError", "[\u8bf7\u6c42\u5f02\u5e38]",
   				G.message), Error("\u8bf7\u6c42\u670d\u52a1\u5668\u53d1\u751f\u5f02\u5e38: " + G.message);
   		}
   	}

   	function H(a, b) {
   		for (var c in b) b.hasOwnProperty(c) && b[c] && (a[c] = b[c]);
   		return a
   	}
   	var l = document,
   		q = /mobile|iPhone|Android|htc|Lenovo|huawei/i.test(f.navigator.userAgent.toString());
   	f.Yoda = {};
   	f.YODA_CONFIG = {};
   	var y = new x("yoda_seed");
   	f.Yoda.LX = y;
   	var z = {
   		pro: "https://verify.meituan.com",
   		staging: "//verify-test.meituan.com",
   		dev: "//verify.inf.dev.sankuai.com",
   		test: "//verify.inf.test.sankuai.com",
   		ppe: "//verify.inf.ppe.sankuai.com",
   		development: "//verify-test.meituan.com"
   	}, E = "",
   		r = "",
   		t = "",
   		u = "",
   		v = "",
   		g = "",
   		D = "",
   		w = "",
   		A = "",
   		B = "",
   		k = "",
   		m = "";
   	e.prototype.init = function(a, b) {
   		E = Date.now();
   		t = r = !1;
   		v = u = !0;
   		m = k = B = A = w = D = g = "";
   		this.env = b || "pro";
   		var c = new n(a.requestCode, this.env);
   		f.Yoda.CAT = c;
   		this.options = a;
   		q = void 0 === a.isMobile ? q : a.isMobile;
   		this.feVersion = "1.4.0";
   		this.source = q ? 3 : 1;
   		this.getConf(this.options.requestCode)
   	};
   	e.prototype.getConf = function(a) {
   		var b = z[this.env] + "/v2/ext_api/page_data";
   		a = {
   			requestCode: a,
   			feVersion: this.feVersion,
   			source: this.source
   		};
   		var c = this,
   			d = Date.now();
   		F(b, a, function(a) {
   			a = JSON.parse(a);
   			var f = Date.now() - d,
   				h = {
   					kvs: {
   						pagedata: [f],
   						TTFB: [f]
   					},
   					tags: {
   						action: a.data ? a.data.action : "",
   						type: a.data ? a.data.type : "",
   						result: a.status ? a.status : ""
   					},
   					ts: Date.now()
   				};
   			window.Yoda.CAT.metric(h);
   			window.Yoda.CAT.postBatch(b, 0, 0, f, "200|" + a.status, "ajax");
   			c.confBack(a)
   		})
   	};
   	e.prototype.confBack = function(a) {
   		if (1 === a.status && a.data) {
   			var b = H(a.data, this.options);
   			this.config = b;
   			this._yoda_config || (this._yoda_config = JSON.stringify(b), this._yoda_options = JSON.stringify(this.options),
   				this._yoda_listIndex = a.data.defaultIndex || 0, this._yoda_riskLevel = this.config.riskLevel);
   			this.config.category = this.config.isHideSwitch ? "MULTIPLE" : this.config.category;
   			b = a.data.yodaVersion;
   			a = a.data.verifyMethodVersion;
   			this.filter();
   			this.ensureVersion(b, a)
   		} else f.Yoda.CAT.sendLog(z[this.env] + "/v2/ext_api/page_data", "jsError", "[dataException]:\u8bf7\u6c42pageData\u63a5\u53e3\u672a\u6b63\u5e38\u8fd4\u56de\u6570\u636e, \u73af\u5883\u4fe1\u606f\u4e3a:" + this.source, JSON.stringify(a)), this.handleError(a)
   	};
   	e.prototype.ensureVersion = function(a, b) {
   		a = JSON.parse(a);
   		b = JSON.parse(b);
   		a && (m = q ? a.i : a.d);
   		try {
   			var c = JSON.parse(this.config.riskLevelInfo)[Number(D)];
   			g = JSON.parse(c).name;
   			(b = JSON.parse(b[g])) && (k = q ? b.i : b.d);
   			this.isNeedLoad();
   			this.getSourcePath();
   			this.loadSource()
   		} catch (d) {
   			f.Yoda.CAT.sendLog(z[this.env] + "/v2/ext_api/page_data", "jsError", "[dataException]:\u89e3\u6790pageData\u63a5\u53e3\u6570\u636e\u5931\u8d25, \u73af\u5883\u4fe1\u606f\u4e3a:" + this.source, d.message), this.handleError("\u521d\u59cb\u5316\u5931\u8d25")
   		}
   	};
   	e.prototype.isNeedLoad = function() {
   		var a = l.getElementsByTagName("script"),
   			b = a.length,
   			c = 0;
   		if (m && k && b)
   			for (; c < b; c++) {
   				var d = a[c].src;~
   				d.indexOf(m) && (u = !1, t = !0);~
   				d.indexOf(k) && (v = !1, r = !0);
   				if (!u && !v) break
   			}
   	};
   	e.prototype.loadSource = function() {
   		var a = this,
   			b = function() {
   				function b(b) {
   					return function(c, d, g) {
   						var h = Date.now(),
   							e = l.createElement(b),
   							p = l.head,
   							C = "src",
   							k = "link" === b ? "css" : "js";
   						e.onload = function() {
   							e = e.onload = e.onerror = e.onreadystatechange = null;
   							var p = Date.now() - h;
   							"script" === b && y.report(d, "duration", {
   								custom: {
   									duration: p,
   									result: "download",
   									requestCode: a.options.requestCode
   								}
   							});
   							f.Yoda.CAT.postBatch(c, 0, 0, p, "200|", k);
   							"function" === typeof g && g();
   							"pro" !== a.env && (f.YODA_CONFIG.__API_URL__ = z[a.env], a.setDomain(z[a.env]))
   						};
   						e.onerror = function() {
   							a.handleError("\u52a0\u8f7d\u5931\u8d25");
   							var b = Date.now() - h;
   							f.Yoda.CAT.postBatch(c, 0, 0, b, "500|", k);
   							y.report(d, "downloadFailed");
   							f.Yoda.CAT.sendLog(c, "resourceError", "downloadFailed", "[\u4e0b\u8f7djs\u5931\u8d25]:" + c)
   						};
   						switch (b) {
   							case "script":
   								e.type = "text/javascript";
   								e.async = !1;
   								e.defer = !0;
   								break;
   							case "link":
   								e.type = "text/css", e.rel = "stylesheet", C = "href"
   						}
   						e[C] = c;
   						p.appendChild(e)
   					}
   				}
   				return {
   					css: b("link"),
   					js: b("script")
   				}
   			}();
   		u && (y.report("yoda", "req"), b.js(A, "yoda", function() {
   			t = !t;
   			a.moduleInit()
   		}));
   		if (v)
   			if (y.report(g, "req"), "withCredentials" in new f.XMLHttpRequest) b.js(w, g, function() {
   				r = !0;
   				a.moduleInit()
   			});
   			else if ("undefined" !== typeof XDomainRequest) var c = window.setInterval(function() {
   			void 0 !== window.Yoda.Ballade && b.js(w, g, function() {
   				r = !0;
   				a.moduleInit();
   				window.clearInterval(c)
   			})
   		}, 1E3);
   		u ||
   			v || this.moduleInit();
   		B && b.css(B)
   	};
   	e.prototype.moduleInit = function() {
   		if (r && t) {
   			this[g] = {};
   			this.config.yodaInitTime = E;
   			if ("function" === typeof f.Yoda[g]) return this[g].initModule = new f.Yoda[g](this.config), !1;
   			var a = l.createElement("script");
   			a.type = "text/javascript";
   			a.appendChild(l.createTextNode(this.moduleText));
   			l.body.appendChild(a);
   			this[g].initModule = new f.Yoda[g](this.config)
   		}
   	};
   	e.prototype.getSourcePath = function() {
   		var a = q ? "i" : "d";
   		m = m ? m + "." : "";
   		k = k ? k + "." : "";
   		"development" === this.env ? (a = "i" === a ? "mobile" :
   			"desktop", w = "/modules/" + g + "/" + a + "/" + g + ".js", B = "/modules/" + g + "/" + a + "/" + g + ".css", A = "./yoda-" + a + ".js") : (A = "https://static.meituan.net/bs/yoda-static/file:file/" + a + "/js/yoda." + m + "js", w = "https://static.meituan.net/bs/yoda-static/file:file/" + a + "/js/" + g + "." + k + "js")
   	};
   	e.prototype.handleError = function(a, b) {
   		"string" !== typeof a && (a = (b = a) && b.error && b.error.message);
   		var c = this.options.failCallbackFun;
   		if (c && "function" === typeof f[c]) {
   			var d = {
   				code: "121333",
   				requestCode: this.options.requestCode
   			};
   			setTimeout(function() {
   					f[c](d)
   				},
   				1E3)
   		}
   		var e = this.options.failCallbackUrl;
   		e && setTimeout(function() {
   			var a = document.createElement("a");
   			a.href = e;
   			f.location.href = (a.origin || a.protocol + "//" + a.host) + a.pathname + a.search + a.hash
   		}, 1E3);
   		this.notifyErr(a)
   	};
   	e.prototype.notifyErr = function(a) {
   		var b = l.getElementById(this.options.root);
   		if (q) {
   			var c = l.createElement("div");
   			var d = l.createElement("div");
   			d.innerHTML = a;
   			c.appendChild(d)
   		} else c = l.createElement("div"), c.innerHTML = a;
   		b.appendChild(c)
   	};
   	e.prototype.setDomain = function(a) {
   		setTimeout(function() {
   			window.YODA_CONFIG.__API_URL__ =
   				a
   		}, 0)
   	};
   	e.prototype.resetVariable = function(a) {
   		E = Date.now();
   		r = a.moduleLoaded || !1;
   		t = a.yodaLoaded || !1;
   		u = a.yodaNeedLoad || !0;
   		v = a.moduleNeedLoad || !0;
   		g = a.MODULE_NAME || "";
   		w = a.MODULE_URL || "";
   		A = a.YODA_URL || "";
   		B = a.CSS_URL || "";
   		k = a.MODULE_VERSION || "";
   		m = a.YODA_VERSION || ""
   	};
   	e.prototype.filter = function() {
   		var a = this.config.riskLevel.split(/[,|]/g);
   		if (a[0] && 1 === a.length) D = this.config.riskLevel;
   		else {
   			a = JSON.parse(this.config.riskLevelInfo);
   			for (var b = JSON.parse(this.config.verifyMethodVersion), c = this.config.riskLevel.split("|"),
   					d = this.config.defaultIndex || 0; d < c.length; d++) {
   				for (var e = c[d].split(","), f = 0, h = 1; f < e.length; f++) {
   					var g = JSON.parse(a[Number(e[f])]);
   					if (!g.name || !b[g.name]) {
   						h = 0;
   						break
   					}
   				}
   				if (h) {
   					D = e[0];
   					this._yoda_listIndex = d;
   					break
   				}
   			}
   		}
   	};
   	x.prototype.report = function(a, b, c) {
   		if ("pro" !== window.seed.env) return !1;
   		var d = {
   			appnm: this.appnm,
   			channel: "techportal",
   			ct: q ? "i" : "www",
   			ch: "web",
   			sc: window.screen.width + "*" + window.screen.height,
   			ua: window.navigator.userAgent
   		};
   		a = {
   			nm: "MV",
   			tm: Date.now(),
   			nt: 0,
   			isauto: 6,
   			val_cid: a,
   			val_bid: b,
   			val_lab: c
   		};
   		this.addToSendQueue(d,
   			a)
   	};
   	x.prototype.addToSendQueue = function(a, b) {
   		var c;
   		(c = this.sendQueue[a.channel]) ? c = c.data : (c = [], this.sendQueue[a.channel] = {
   			conf: a,
   			data: c
   		});
   		c.push(b);
   		var d = this;
   		setTimeout(function() {
   			d.send()
   		}, 0)
   	};
   	x.prototype.send = function() {
   		var a = [];
   		for (d in this.sendQueue)
   			if (this.sendQueue.hasOwnProperty(d)) {
   				var b = this.sendQueue[d];
   				var c = b.conf;
   				(b = H(c, {
   					appnm: c.appnm,
   					category: "data_sdk_" + d,
   					evs: b.data
   				})) && a.push(b)
   			}
   		if (0 < a.length) {
   			var d = "https://report.meituan.com/?_lxskd_rnd=" + Date.now() + Math.ceil(1E3 * Math.random());
   			this.sendStatic(d, {
   				data: a
   			})
   		}
   		this.sendQueue = {}
   	};
   	x.prototype.sendStatic = function(a, b) {
   		if (0 === b.data.length) return !1;
   		try {
   			var c = new f.XMLHttpRequest;
   			if ("withCredentials" in c) c.open("POST", a, !0);
   			else if ("undefined" !== typeof f.XDomainRequest) c = new f.XDomainRequest, c.open("POST", a);
   			else throw Error("\u7075\u7280\u521b\u5efaXHR\u5bf9\u8c61\u5931\u8d25");
   			c.onerror = function() {
   				c.abort();
   				c = null
   			};
   			c.send(JSON.stringify(b.data))
   		} catch (d) {
   			throw Error("\u7075\u7280XHR\u8bf7\u6c42\u670d\u52a1\u5668\u53d1\u751f\u5f02\u5e38: " +
   				d.message);
   		}
   		return !0
   	};
   	n.prototype.postBatch = function(a, b, c, d, e, f) {
   		a = a + "\t" + Date.now() + "\t" + b + "\t" + c + "\t" + d + "\t" + this.project + "\t" + this.origin + "\t" + e + "\t\t\t\t" + f;
   		this.batchs.push(a)
   	};
   	n.prototype.sendBatch = function() {
   		if (0 < this.batchs.length) {
   			var a = this.host + "/api/batch?v=" + this.catVersion,
   				b = {
   					c: "S\t\t\t\t\t\t" + this.unionId + "\n" + this.batchs.join("\n")
   				};
   			this.sendStatic(a, b);
   			this.batchs = []
   		}
   	};
   	n.prototype.speed = function(a, b) {
   		var c = "&project=" + this.project + "&pageurl=" + window.location.href + "&unionId=" + this.unionId +
   			"&timestamp=" + Date.now() + "&speed=" + a + "&customspeed=" + b;
   		c = this.host + "/api/speed?v=" + this.catVersion + c;
   		var d = this,
   			e = new f.XMLHttpRequest;
   		e.open("GET", c);
   		e.onerror = function() {
   			d.speed(a, b);
   			e.abort();
   			e = null
   		};
   		e.send()
   	};
   	n.prototype.sendLog = function(a, b, c, d) {
   		a = [{
   			project: this.project,
   			pageUrl: window.location.origin,
   			resourceUrl: a || "",
   			category: b,
   			sec_category: c,
   			level: "error",
   			unionId: this.unionId,
   			timestamp: Date.now(),
   			content: d || ""
   		}];
   		this.sendStatic(this.host + "/api/log?v=" + this.catVersion, {
   			c: JSON.stringify(a)
   		})
   	};
   	n.prototype.metric = function(a) {
   		this.sendStatic(this.host + "/api/metric?v=" + this.catVersion + "&p=" + this.project, {
   			data: JSON.stringify(a)
   		})
   	};
   	n.prototype.sendStatic = function(a, b) {
   		F(a, b, function() {});
   		return !0
   	};
   	n.prototype["byte"] = function(a) {
   		var b = 0,
   			c = a.length;
   		if (a) {
   			for (var d = 0; d < c; d++) 255 < a.charCodeAt(d) ? b += 2 : b++;
   			return b
   		}
   		return 0
   	};
   	f.YodaSeed = e
   })(window);