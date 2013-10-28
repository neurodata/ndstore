<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml"
    xmlns:py="http://purl.org/kid/ns#">

<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'" py:attrs="item.items()">
    <link py:for="css in tg_css" py:replace="css.display()"/>
    <link py:for="js in tg_js_head" py:replace="js.display()"/>
    <meta py:replace="item[:]"/>
</head>

<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'" py:attrs="item.items()">
    <div py:for="js in tg_js_bodytop" py:replace="js.display()"/>
    <div py:replace="[item.text]+item[:]"/>
    <div py:for="js in tg_js_bodybottom" py:replace="js.display()"/>
</body>

</html>
