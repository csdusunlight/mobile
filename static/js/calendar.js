function is_leap(year) { 
   return (year%100==0?res=(year%400==0?1:0):res=(year%4==0?1:0));
} //是否为闰年

var nstr=new Date(); //当前Date
var ynow=nstr.getFullYear(); //年份
var mnow=nstr.getMonth(); //月份
var dnow=nstr.getDate(); //今日日期
var n1str=new Date(ynow,mnow,1); //当月第一天Date

var firstday=n1str.getDay(); //当月第一天星期几

var m_days=new Array(31,28+is_leap(ynow),31,30,31,30,31,31,30,31,30,31); //各月份的总天数

var tr_str=Math.ceil((m_days[mnow] + firstday)/7); //表格所需要行数

//打印表格第一行（有星期标志）
for(var i=0;i<tr_str;i++) { //表格的行
   document.write("<tr>");
   for(var k=0;k<7;k++) { //表格每行的单元格
      idx=i*7+k; //单元格自然序列号
      var date_str=idx-firstday+1; //计算日期
      var num = (date_str<=0 || date_str>m_days[mnow]) ? "" : date_str; //过滤无效日期（小于等于零的、大于月总天数的）
      //打印日期：
      document.write ("<td><number>" + num + "</number></td>");
   }
   document.write("</tr>"); //表格的行结束
}

