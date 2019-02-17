        window.yodaTheme = setTheme;
        function setTheme(theme) {
            var theme = theme || 'meituan';
            var header = document.getElementById('header');
            header.style.display = "block";
            var logo = document.getElementById('logo');
            var footer = document.getElementById('footer');
            footer.style.display = "block";

            var link = document.createElement('link');
            link.rel = 'shortcut icon';
            link.type = 'image/x-icon';

            if (theme === 'meituan' || theme === 'mt' || theme === '') {
                link.href = '/static/favicon.ico';
            }
            if (theme === 'dianping' || theme === 'dp') {
                header.className = 'dpHeader';
                logo.className = 'dpLogo';
                footer.innerHTML = '? 2003-2017 dianping.com, All Rights Reserved.';
                link.href = '//www.dpfile.com/s/res/favicon.5ff777c11d7833e57e01c9d192b7e427.ico';
            }

            document.head.appendChild(link);
        }

            var options = {
            requestCode: "87e3ad563cab4889b032c751d7df4691",
            succCallbackUrl: "https\x3A\x2F\x2Foptimus\x2Dmtsi\x2Emeituan\x2Ecom\x2Foptimus\x2FverifyResult\x3ForiginUrl\x3Dhttp\x253A\x252F\x252Fwww\x2Edianping\x2Ecom\x252Fsearch\x252Fkeyword\x252F240\x252F10\x5F\x2525E8\x2525B6\x252585\x2525E7\x2525BA\x2525A7\x2525E9\x2525B8\x2525A1\x2525E8\x2525BD\x2525A6",
            failCallbackUrl: "",
            forceCallback: "false",
            root: "root",
            platform: "1000",
            theme: "dianping",
            isMobile: false
        }
        YodaSeed(options, "pro");
