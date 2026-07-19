# 脏输入测试
<script>alert(1)</script>
<div class=x onclick="alert(1)" style="display:flex">危险</div>
[点击这里](javascript:alert(1))
&nbsp;&ensp;&emsp;
真正的问题是，危险代码不应该作为正文出现。