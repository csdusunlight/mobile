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

var share_pyq = document.getElementById("share_pengyouquan");
share_pyq.addEventListener("tap",function () {
	wx.onMenuShareTimeline({
	    title: 'nihaoma', // 分享标题
	    link: share_url, // 分享链接
	    imgUrl: '', // 分享图标
	    success: function () { 
	        alert('yes');// 用户确认分享后执行的回调函数
	    },
	    cancel: function () {
	    	alert('no');
	        // 用户取消分享后执行的回调函数
	    }
	});
});