!function(e,t){if(!e.CpaText){var n=function(){},r={parallel:function(e,t){var n=i.isArray(e)?[]:{},r=0,a=!1,o=i.keys(e).length;i.each(e,function(e,i){e(function(e){n.hasOwnProperty(i)||(n[i]=e,r++,r!==o||a||(a=!0,t(n)))})})}},a=function(){function n(n){if(n=n||e.event,n.isFixed)return n;if(n.isFixed=!0,n.preventDefault=n.preventDefault||function(){this.returnValue=!1},n.stopPropagation=n.stopPropagaton||function(){this.cancelBubble=!0},n.target||(n.target=n.srcElement),!n.relatedTarget&&n.fromElement&&(n.relatedTarget=n.fromElement==n.target?n.toElement:n.fromElement),null==n.pageX&&null!=n.clientX){var r=t.documentElement,a=t.body;n.pageX=n.clientX+(r&&r.scrollLeft||a&&a.scrollLeft||0)-(r.clientLeft||0),n.pageY=n.clientY+(r&&r.scrollTop||a&&a.scrollTop||0)-(r.clientTop||0)}return!n.which&&n.button&&(n.which=1&n.button?1:2&n.button?3:4&n.button?2:0),n}function r(e){e=n(e);var t=this.events[e.type];for(var r in t)if(t.hasOwnProperty(r)){var a=t[r],i=a.call(this,e);i===!1&&(e.preventDefault(),e.stopPropagation())}}function o(e){return function(t){for(var n=t.relatedTarget;n&&n!==this;)n=n.parentNode;return n!=this?e.call(this,t):void 0}}function s(e){return function(t){for(var n=t.relatedTarget;n&&n!==this;)n=n.parentNode;return n!=this?e.call(this,t):void 0}}var p=0;return{add:function(t,n,i){t.setInterval&&t!=e&&!t.frameElement&&(t=e),i.guid||(i.guid=++p),t.events||(t.events={},t.handle=function(e){return"undefined"!=typeof a&&r.call(t,e)});var u=i,f=n;"mouseenter"===n?(f="mouseover",u=s(i)):"mouseleave"===n&&(f="mouseout",u=o(i)),t.events[f]||(t.events[f]={},t.addEventListener?t.addEventListener(f,t.handle,!1):t.attachEvent&&t.attachEvent("on"+f,t.handle)),t.events[f][i.guid]=u},remove:function(e,t,n){var r=e.events&&e.events[t];if(r&&(delete r[n.guid],i.empty(r)&&(e.removeEventListener?e.removeEventListener(t,e.handle,!1):e.detachEvent&&e.detachEvent("on"+t,e.handle),delete e.events[t],i.empty(e.events))))try{delete e.handle,delete e.events}catch(a){e.removeAttribute("handle"),e.removeAttribute("events")}}}}(),i={whitespace:"[\\x20\\t\\r\\n\\f]",trim:function(e){var t=new RegExp("^"+i.whitespace+"+|((?:^|[^\\\\])(?:\\\\.)*)"+i.whitespace+"+$","g");return null==e?"":(e+"").replace(t,"")},toArray:function(e){return Array.prototype.slice.call(e)},isString:function(e){return"string"==typeof e},isArray:function(e){return Array.isArray?Array.isArray(e):"[object Array]"==Object.toString(e)},empty:function(e){if(!e)return!0;if(i.isArray(e)||i.isString(e))return 0===e.length;for(var t in e)if(e.hasOwnProperty(t))return!1;return!0},keys:function(e){var t=[];for(var n in e)e.hasOwnProperty(n)&&t.push(n);return t},each:function(e,t,n){if(e)if(e.length===+e.length){for(var r=0,a=e.length;a>r;r++)if(!1===t.call(n,e[r],r,e))return}else for(var i in e)if(e.hasOwnProperty(i)&&!1===t.call(n,e[i],i,e))return},extend:function(e){return e=e||{},i.each(i.toArray(arguments).slice(1),function(t){i.each(t,function(t,n){e[n]=t})}),e},toParams:function(e){var t,n,r=[],a=function(e,t){var n,r=[];if(t===!0?t="1":t===!1&&(t="0"),"function"==typeof t&&(t=t()),null!==t&&"object"==typeof t){for(n in t)t.hasOwnProperty(n)&&null!==t[n]&&r.push(a(e+"["+n+"]",t[n]));return r.join("&")}if("function"!=typeof t)return encodeURIComponent(e)+"="+encodeURIComponent(t);throw new Error};for(n in e)if(e.hasOwnProperty(n)){t=e[n];var i=a(n,t);i&&r.push(i)}return r.join("&")},parseJSON:function(t){if(e.JSON&&e.JSON.parse)return e.JSON.parse(t);if(null===t)return null;if("string"==typeof t&&(t=i.trim(t))){var n=/^[\],:{}\s]*$/,r=/(?:^|:|,)(?:\s*\[)+/g,a=/\\(?:["\\\/bfnrt]|u[\da-fA-F]{4})/g,o=/"[^"\\\r\n]*"|true|false|null|-?(?:\d+\.|)\d+(?:[eE][+-]?\d+|)/g,s=t.replace(a,"@").replace(o,"]").replace(r,"");if(n.test(s))return new Function("return "+t)()}throw new Error("Invalid JSON: "+t)},ajax:function(e){e=i.extend({dataType:"json"},e);var t=function(t){t&&n.setRequestHeader("Content-type","application/x-www-form-urlencoded; charset="+(e.charset||"utf-8"))};e.data=i.toParams(e.data||{}),e.async=e.async||!0;var n=i.prepareRequest(e);"POST"===e.type?(n.open("POST",e.url,e.async),t(1),n.send(e.data)):(n.open("GET",e.url+(i.empty(e.data)?"":(e.url.match(/\?/)?"&":"?")+e.data),e.async),t(),n.send(null))},prepareRequest:function(t){var r;if(e.XMLHttpRequest)r=new XMLHttpRequest,r.overrideMimeType&&r.overrideMimeType("text/html");else if(e.ActiveXObject)try{r=new ActiveXObject("Msxml2.XMLHTTP")}catch(o){try{r=new ActiveXObject("Microsoft.XMLHTTP")}catch(s){}}if(!r)throw new Error("Could not create a XMLHttpRequest instance.");return a.add(r,"readystatechange",function(){if(1===r.readyState)(t.load||n)();else if(4===r.readyState){var e=r.responseText;if("json"===t.dataType)try{e=i.parseJSON(e)}catch(a){}r.status>199&&r.status<300||304===r.status?(t.success||n)(e,r):(t.error||n)(e,r)}t.always=t.always||n;try{t.always(r.readyState,r.status,e)}catch(a){t.always(r.readyState)}}),r.withCredentials=!0,r},scheme:function(){return"https:"==t.location.protocol?"https://":"http://"},error:function(e){throw new Error("CpaText: "+e)},css:function(e,t){i.extend(e.style,t)},show:function(e){e.style.display="block"},hide:function(e){e.style.display="none"},parseLink:function(e){var n=t.createElement("a");return n.href=e,n},offset:function(e){for(var t=0,n=0;e;)t+=e.offsetTop||0,n+=e.offsetLeft||0,e=e.offsetParent;return{top:t,left:n}},bind:function(e,t){var r,a;Function.prototype.bind;var i=Array.prototype.slice;return r=i.call(arguments,2),a=function(){if(!(this instanceof a))return e.apply(t,r.concat(i.call(arguments)));n.prototype=e.prototype;var o=new n;n.prototype=null;var s=e.apply(o,r.concat(i.call(arguments)));return Object(s)===s?s:o}},getDomain:function(e){return e.hostname.toLowerCase().replace(/^www\./,"")}},o={initialized:!1,popup:null,popupTimeout:null,loadCss:function(){var e="cpatext-css";if(!t.getElementById(e)){var n=t.createElement("link");i.extend(n,{id:e,rel:"stylesheet",href:p.host+"/css/cpatext.css?cbea"});for(var r=["head","body"],a=0;a<r.length;a++){var o=t.getElementsByTagName(r[a])[0];if(o){o.appendChild(n);break}}}},post:function(e,t,r){t=i.extend({id:p.id},t),i.ajax({type:"POST",url:p.host+e,data:t,success:r||n})},init:function(){if(!this.initialized){o.checkConfiguration(),this.initialized=!0;var e=t.createElement("div");i.css(e,{position:"absolute",display:"none",zIndex:9999999}),t.body.appendChild(e),a.add(e,"mouseenter",function(){e.mouseEntered=!0}),a.add(e,"mouseleave",function(){e.mouseEntered=!1,o.hidePopup()}),this.popup=e,a.add(t,"click",function(e){for(var t=e.target;t&&("A"!=t.tagName||!t.hiddenHref);)t=t.parentNode;if(t){var n=t.href;t.href=t.hiddenHref,setTimeout(function(){t.href=n},1)}})}},run:function(e){if("complete"===t.readyState){this.init();var n={domains:i.bind(o.findDomains,o,e),phrases:i.bind(o.findPhrases,o,e)};r.parallel(n,function(t){var n={domains:t.domains.join(","),phrases:t.phrases.join(";")};o.post("/find",n,function(t){var n={link:i.bind(o.replaceLinks,o,e,t.link),phrase:i.bind(o.replacePhrases,o,e,t.phrase,o.createPhraseLink)};r.parallel(n,function(e){i.empty(e.link)&&i.empty(e.phrase)||o.post("/stat",{stat:JSON.stringify(e)})})})})}},findLinks:function(e,n,r){for(var a=e.getElementsByTagName("A"),o=i.getDomain(t.location),s=0;s<a.length;s++){var p=a[s];if(p.hostname){var u=i.getDomain(p);if(u&&-1===o.indexOf(u)&&-1===u.indexOf(o)&&!1===n(p,u))break}}r()},findDomains:function(e,t){if(!e||-1===p.modules.indexOf("link"))return t([]),void 0;var n={};this.findLinks(e,function(e,t){n[t]=1},function(){t(i.keys(n))})},replaceLinks:function(e,t,n){var r={};if(!e||!t)return n(r),void 0;var a=t.domains;this.findLinks(e,function(e,t){if(a.hasOwnProperty(t)){var n=a[t];e.hiddenHref=o.buildClickLink(i.extend({mod:"link",ulp:e.href},n));var s=n.campaign_id;r[s]||(r[s]=[[0]]),r[s][0][0]++}},function(){n(r)})},isPhraseNodeAllowed:function(e){if(!e.tagName)return!1;var t=["AUDIO","VIDEO","IFRAME","A","IMG","INPUT","BUTTON","SELECT","OPTION","SCRIPT","META","LINK","STYLE","NOSCRIPT","HEADER","FOOTER"];if(t=t.concat(["LABEL","H1","H2","H3","H4","H5","H6"]),-1!==t.indexOf(e.tagName.toUpperCase()))return!1;for(var n=["ya-partner","cpatext-exclude","header","footer"],r=0;r<n.length;r++)if(-1!==e.className.indexOf(n[r]))return!1;var a=["header","footer"];for(r=0;r<a.length;r++)if(e.id===a[r])return!1;return!0},findPhraseNodes:function(e,t,n){var r=[e],a=function(){for(var e=0;20>e&&r.length;e++){var s=r.shift();if(s.nodeType===Node.TEXT_NODE){var p=i.trim(s.textContent);if(p.length>2){var u=o.extractWords(s.textContent);if(u.length&&!1===t.call(o,s,u))return n.call(o),void 0}}else if(o.isPhraseNodeAllowed(s))for(var f=0,l=s.childNodes.length;l>f;f++)r.push(s.childNodes[f])}r.length?setTimeout(a,10):n.call(o)};a()},findPhrases:function(e,t){if(-1===p.modules.indexOf("phrase"))return t([]),void 0;var n=[],r="*",a=0;this.findPhraseNodes(e,function(e,t){var o=[];i.each(t,function(e){o.push(e.word)});var s=o.join(r);return a+=s.length,a>p.phrase_max_index_length?!1:(n.push(s),void 0)},function(){t(n)})},replacePhrases:function(e,n,r,a){var s={};if(!e||!n)return a(s),void 0;var u={};i.each(n.phrases,function(e,t){for(var n=o.extractWords(t),r=u,a=0;a<n.length;a++)r.hasOwnProperty(n[a].word)||(r[n[a].word]={parent:r}),r=r[n[a].word],a===n.length-1&&(r._meta=e)});var f=0,l={},c=[],d=Math.pow(p.phrase_min_distance,2);o.findPhraseNodes(e,function(e,n){for(var a,h=e.textContent,v=0,m=0;m<n.length;){for(var y=m,g=u;y<n.length&&g.hasOwnProperty(n[y].word);)g=g[n[y].word],y++;for(;g.parent&&!g._meta;)g=g.parent,y--;if(y>m&&g._meta){a=h.slice(v,n[m].index),""!=a&&e.parentNode.insertBefore(t.createTextNode(a),e);var w=n[y-1].index+n[y-1].word.length,x=h.slice(n[m].index,w),T=r(x,g);e.parentNode.insertBefore(T,e);var P=i.offset(T);P.width=T.offsetWidth,P.height=T.offsetHeight;for(var E=!0,_=c.length-1;_>=0;_--)if(o.getDistance(c[_],P)<d){E=!1;break}if(E){v=w,c.push(P);var b=g._meta.campaign_id,k=g._meta.banner_id||0,O=g._meta.phrase_id||0;if(s[b]||(s[b]={}),s[b][k]||(s[b][k]={}),s[b][k][O]||(s[b][k][O]=0),s[b][k][O]++,m=y,f++,l[x]=1,f>=p.phrase_max_replaces)break}else v=n[m].index,e.parentNode.removeChild(T),m++}else m++}e.textContent=h.slice(v)},function(){a(s)})},createPhraseLink:function(e,n){var r=t.createElement("a"),a=i.extend({mod:"phrase",phrase:e},n._meta);if(delete a.link,i.extend(r,{target:p.phrase_link_target,className:"cpatext-link",textContent:e,href:n._meta.link||"#",hiddenHref:o.buildClickLink(a)}),i.css(r,{position:"relative"}),1==p.show_popups){var s=n._meta.banner_id,u=n._meta.campaign_id;s&&o.initPopup(r,u,s)}return r},initPopup:function(e,n,r){this.loadCss();var o=this,s=!1,u=!1;a.add(e,"mouseenter",function(a){s=!0,u?o.displayPopup(e,a):(u=!0,i.ajax({url:p.host+"/popup?"+i.toParams({banner_id:r,campaign_id:n,site_id:p.id,phrase:e.textContent,url:t.location.href,popup_type:p.popup_type}),success:function(t){e.popupHTML=t,s&&o.displayPopup(e,a)}}))}),a.add(e,"mouseleave",function(){s=!1,o.hidePopup()})},displayPopup:function(e,n){if(e.popupHTML){clearTimeout(this.popupTimeout);var r=this.popup;r.innerHTML=e.popupHTML;for(var a=r.getElementsByTagName("A"),o=0;o<a.length;o++){var s=a[o];i.getDomain(s)==i.getDomain(e)&&i.extend(s,{target:e.target,hiddenHref:e.hiddenHref})}i.show(r);var p=t.documentElement,u=i.offset(e).top,f=u-r.offsetHeight;0>f&&(f=u+e.offsetHeight);var l=p.scrollLeft,c=l+p.clientWidth-r.offsetWidth,d={left:Math.min(Math.max(l,n.pageX-r.offsetWidth/2),c)+"px",top:f+"px"};i.css(r,d)}},hidePopup:function(){clearTimeout(this.popupTimeout);var e=this.popup;this.popupTimeout=setTimeout(function(){e.mouseEntered||i.hide(e)},300)},extractWords:function(e){var t,n=new RegExp("(?:[-._&]?[a-zа-яё0-9]+)+","ig"),r=[];for(r.wordsLength=0;t=n.exec(e);)r.push({word:t[0].toLowerCase(),text:t[0],index:t.index}),r.wordsLength+=t[0].length;return r},buildClickLink:function(e){var n=i.extend({id:p.id,ref:t.location.href,popup_type:p.popup_type},e);return p.host+"/click?"+i.toParams(n)},checkConfiguration:function(){p.id||i.error('Please provide "id"')},getDistance:function(e,t){var n,r,a,i;return e.top<t.top?(n=e.top+e.height,r=t.top):(n=t.top+t.height,r=e.top),e.left<t.left?(a=e.left+e.width,i=t.left):(a=t.left+t.width,i=e.left),Math.pow(n-r,2)+Math.pow(a-i,2)}},s=t.getElementById("cpatext-script");if(s){var p=i.extend({id:0,host:i.scheme()+i.parseLink(s.src).hostname,show_popups:1,modules:["phrase","link"],phrase_max_index_length:3e4,phrase_max_replaces:500,phrase_min_distance:200,popup_type:"horizontal",phrase_link_target:"_blank"},e.CpaTextConfig);e.CpaText={run:i.bind(o.run,o),replacePhrases:i.bind(o.replacePhrases,o),util:i},"complete"===t.readyState?o.run(t.body):a.add(e,"load",function(){o.run(t.body)})}}}(window,document);
