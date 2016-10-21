
wx.config({
    debug: false, // 开启调试模式,调用的所有api的返回值会在客户端alert出来，若要查看传入的参数，可以在pc端打开，参数信息会通过log打出，仅在pc端时才会打印。
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
wx.ready(function () {
    wx.checkJsApi({
        jsApiList: [
            'onMenuShareTimeline',
        ],
    });
	wx.onMenuShareTimeline({
	    title: 'nihaoma', // 分享标题
	    link: share_url, //分享链接
	    imgUrl: 'http://m.wafuli.cn/static/images/choujiang-zhuanpan.png', // 分享图标
	    success: function () { 
	    },
	    cancel: function () {
	        // 用户取消分享后执行的回调函数
	    }
	});
    wx.error(function(res){
        // config信息验证失败会执行error函数，如签名过期导致验证失败，具体错误信息可以打开config的debug模式查看，也可以在返回的res参数中查看，对于SPA可以在这里更新签名。

    });
});
