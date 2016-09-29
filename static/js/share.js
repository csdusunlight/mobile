window.onload=function(){
	var share = document.getElementById("share"),
		share_close = document.getElementById("share_close"),
		share_bg = document.getElementById("share_bg"),
	content_box = document.getElementById("content_box");
		//监听点击事件
		share.addEventListener("tap",function () {
			share_bg.style.display = "block";
		  	content_box.setAttribute("class","content-box-01");
		});

		share_close.addEventListener("tap",function () {
			share_bg.style.display = "none";
		  	content_box.setAttribute("class","content-box-02");
		});
}