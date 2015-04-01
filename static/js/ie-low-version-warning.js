/* IE 去死 modal 提示脚本 v1
 * 無用實驗室 荣誉出品
 * http://www.wuyongzhiyong.com
 * @license MIT
 *
 * 这是由David Huang修改的版本
 * 将各国产浏览器换成安全、可靠、快捷、方便、简洁、省电的浏览器。
 * 自动通过操作系统判断，Windows XP系统推荐Firefox，
 * Windows 7及以上的操作系统推荐使用IE11，
 * Vista和Mac用户被残忍地忽略不计了。
 * https://hjc.im
 */
;(function (){
var css = '.iedie-wrapper div{border:0 none;margin:0;padding:0;}'+
    'html,body,#iedie-bg{height:100%!important;width:100%!important;overflow:hidden!important;}'+
    '#iedie-bg{height:150%!important;}'+
    '#iedie-bg{position:absolute;top:0;left:0;z-index:10;background-color:#666;-ms-filter: "progid:DXImageTransform.Microsoft.Alpha(Opacity=90)";filter: alpha(opacity=90);}'+
    '#iedie-modal-wrapper{position:absolute;top:60px;left:50%;z-index:20;}'+
    '#iedie-modal{position:absolute;top:0px;left:-320px;width:600px;padding:20px;z-index:30;background-color:#F4F4F4;font-size:14px;line-height:1.2;color:#555;}'+
    '.iedie-line,.iedie-clear{clear:both;height:0px;overflow:hidden;}'+
    '.iedie-title-wrapper .iedie-clear{clear:both;height:10px;overflow:hidden;}'+
    '.iedie-line{background:black;height:1px;}'+
    '.iedie-close{font-size:12px;color:#999;float:right;display:inline;background:#eee;text-decoration:none;padding:3px 5px;}'+
    '.iedie-title{float:left;padding-bottom:14px;font-size:18px;color:#333;}'+
    'a.iedie-browser .iedie-browser-name{padding-top:3px;}'+
    'a{text-decoration:none;color:#666;font-weight:bold;}'+
    '.iedie-body a:hover{text-decoration:underline;}'+
    'a .iedie-browser-desc{text-decoration:none;font-weight:normal;}'+
    'a.iedie-browser .iedie-browser-desc{padding-top:2px;color:#999;}'+
    'a.iedie-close{font-weight:normal;}' +
    '.iedie-img{width:60px;height:45px;float:left;cursor:pointer;}' +
    '';

var isXP = /Windows NT 5/.test(navigator.userAgent);
var hint = '<p>您正在使用的浏览器版本过低，不被本站支持，继续使用此浏览器访问本站，您可能会遇到页面样式错乱及某些功能无法正常使用的情况。低版本的浏览器也很可能存在安全漏洞，因此为了您在网上浏览及进行资金操作时的信息安全，请您尽快更换最新的浏览器。</p><p>推荐使用'+(isXP?'Firefox':'IE11')+'浏览器：</p>';
if (typeof IEDIE_HINT === 'string') {
    hint = IEDIE_HINT;
    delete IEDIE_HINT;
}

if (isXP) {
    //Firefox
    document.write('<div id="iedie-wrapper" class="iedie-wrapper"><div id="iedie-bg"></div><div id="iedie-modal-wrapper"><div id="iedie-modal"><div class="iedie-title-wrapper"><a class="iedie-close" onclick="__iedie_close()" href="javascript:;">&times;&nbsp;关闭</a><div class="iedie-title">温馨提示：您正在使用的浏览器版本过低</div><div class="iedie-clear"></div></div><div class="iedie-line"></div><div class="iedie-body">' +
    hint +
    '<a class="iedie-browser" href="https://www.mozilla.org/en-US/firefox/all/" target="_blank"><p><div class="iedie-img"><img border="0" width="50" height="50" src="/static/image/icon/browser/firefox.png"></img></div><div class="iedie-browser-name">Firefox浏览器</div><div class="iedie-browser-desc">来自Mozilla基金会，开源、快速、简洁易用的浏览器</div><div class="iedie-clear"></div></p></a>' +
    '<p>您还可以选择：<br/>升级到最新操作系统：<a href="http://windows.microsoft.com/en-us/windows-8/features" target="_blank">Windows 8.1</a>、<a href="http://windows.microsoft.com/zh-cn/windows/windows-help#windows=windows-7" target="_blank">Windows 7</a>' +
    '</p><a class="iedie-close" onclick="__iedie_close()" href="javascript:;">我已了解，继续访问 &gt;&gt;</a><div class="iedie-clear"></div></div></div></div></div>' +
    '');
} else {
    //IE11
    document.write('<div id="iedie-wrapper" class="iedie-wrapper"><div id="iedie-bg"></div><div id="iedie-modal-wrapper"><div id="iedie-modal"><div class="iedie-title-wrapper"><a class="iedie-close" onclick="__iedie_close()" href="javascript:;">&times;&nbsp;关闭</a><div class="iedie-title">温馨提示：您正在使用的浏览器版本过低</div><div class="iedie-clear"></div></div><div class="iedie-line"></div><div class="iedie-body">' +
    hint +
    '<a class="iedie-browser" href="http://www.microsoft.com/en-us/download/internet-explorer-11-for-windows-7-details.aspx" target="_blank"><p><div class="iedie-img"><img border="0" width="50" height="50" src="/static/image/icon/browser/ie.png"></img></div><div class="iedie-browser-name">Internet Explorer 11浏览器</div><div class="iedie-browser-desc">IE11由微软公司出品，适用于最新Windows系统，是一款速度快，功能强大而又简洁的浏览器。</div><div class="iedie-clear"></div></p></a>' +
    '</p><a class="iedie-close" onclick="__iedie_close()" href="javascript:;">我已了解，继续访问 &gt;&gt;</a><div class="iedie-clear"></div></div></div></div></div>' +
    '');
}

var styleElem = document.createElement('style');
styleElem.type = 'text/css' ;
styleElem.styleSheet.cssText = css;
var wrapper = document.getElementById('iedie-wrapper');
wrapper.insertBefore(styleElem, document.getElementById('iedie-bg'));
//wrapper.appendChild(styleElem); // 添加为第一个子节点是为了下面能 trigger relayout

(function r(f){/in/.test(document.readyState)?setTimeout(function(){r(f);},9):f()}(function(){
  // 解决刷新的时候自动恢复位置的问题，在 domready 后 scrollTo 页面顶部
  // domready 代码来自 http://www.dustindiaz.com/smallest-domready-ever
  setTimeout(function(){
    window.scrollTo(0,0);
  }, 1);
}));

__iedie_close = function() {
  setTimeout(function () {
    __iedie_close = void 0;
    delete __iedie_close;
  }, 1);
  while (wrapper.firstChild) {
    wrapper.removeChild(wrapper.firstChild);
    if (wrapper.parentNode) {
      var tmp = 0; // trigger relayout，不然 IE7 下滚动条不会恢复
      tmp = wrapper.parentNode.offsetTop  +  'px';
    }
  }
  if (wrapper.parentNode) {
    wrapper.parentNode.removeChild(wrapper);
  }
};

}());
