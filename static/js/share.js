var body = document.getElementsByTagName("body")[0],
	share = document.getElementById("share");
//		动态创建HTML
var div_bg = document.createElement('div');
	div_bg.className = 'share-bg';
	div_bg.id = 'share_bg';
	body.appendChild(div_bg);
var div = document.createElement('div');
	div.className = 'share-big-box';
	div.innerHTML = '<div id="share_box"><div id="content_box" class="share-content-box">'+
					'<div id="share_close" class="share-close"></div>'+
					'<div class="share-content">'+
					'<a class="jiathis_button_qzone">QQ空间</a>'+
					'<a class="jiathis_button_tsina">新浪微博</a>'+
					'<a class="jiathis_button_tqq">腾讯微博</a>'+
					'<a id="share_pengyouquan" class="jiathis_button_weixin">微信</a>'+
					'<a class="jiathis_button_cqq">QQ好友</a>'+
					'</div></div></div></div>';
	body.appendChild(div);

share.addEventListener("tap",function () {

	var share_bg = document.getElementById("share_bg"),
		content_box = document.getElementById("content_box");
	share_bg.style.display = "block";
  	content_box.setAttribute("class","content-box-01");
});
//		点击背景关闭分享弹窗
var share_bg = document.getElementById("share_bg");
share_bg.addEventListener("tap",function () {
	var share_bg = document.getElementById("share_bg"),
		content_box = document.getElementById("content_box");
	share_bg.style.display = "none";
  	content_box.setAttribute("class","content-box-02");
});
wx.config({
    debug: true, // 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。
    appId: appId, // 必填，公众号的唯一标识
    timestamp: timestamp, // 必填，生成签名的时间戳
    nonceStr: nonceStr, // 必填，生成签名的随机串
    signature: signature,// 必填，签名，见附录1
    jsApiList: [
    	'onMenuShareTimeline',
    	'onMenuShareAppMessage',
    	'onMenuShareQQ',
    	'onMenuShareQZone',
    ] // 必填，需要使用的JS接口列表，所有JS接口列表见附录2
});
var share_pyq = document.getElementById("share_pengyouquan");
alert('ddd');
wx.ready(function () {
    wx.checkJsApi({
        jsApiList: [
            'onMenuShareTimeline',
        ],
    });
	wx.onMenuShareTimeline({
	    title: 'nihaoma', // 分享标题
	    link: share_url, // 分享链接
	    imgUrl: 'http://m.wafuli.cn/static/images/back01.jpg', // 分享图标
	    success: function () { 
	        alert('yes');// 用户确认分享后执行的回调函数
	    },
	    cancel: function () {
	    	alert('no');
	        // 用户取消分享后执行的回调函数
	    }
	});
    wx.error(function(res){
        // config信息验证失败会执行error函数，如签名过期导致验证失败，具体错误信息可以打开config的debug模式查看，也可以在返回的res参数中查看，对于SPA可以在这里更新签名。

    });
});
