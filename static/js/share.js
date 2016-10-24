var body = document.getElementsByTagName("body")[0],
	share = document.getElementById("share");
//		动态创建HTML
var div = document.createElement('div');
var ua = navigator.userAgent.toLowerCase();
if(ua.match(/MicroMessenger/i)=="micromessenger") {
    div.className = 'share-guide-box share-top';
} else if (ua.indexOf('qq/')!= -1){
    div.className = 'share-guide-box share-top';
} else {
    div.className = 'share-guide-box share-bottom';
}
	div.id = 'share_guide_box';
	body.appendChild(div);

//		点击分享按钮弹出弹窗
var share_guide_box = document.getElementById("share_guide_box");
share.addEventListener("tap",function () {
	share_guide_box.style.display = "block";
});
//		点击背景关闭分享弹窗;
share_guide_box.addEventListener("tap",function () {
	share_guide_box.style.display = "none";
});
