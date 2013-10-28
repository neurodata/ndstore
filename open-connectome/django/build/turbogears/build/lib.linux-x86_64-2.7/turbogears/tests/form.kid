<html xmlns:py="http://purl.org/kid/ns#">
<head>
    <link py:for="css in tg_css" py:replace="css.display()" />
    <script py:for="js in tg_js_head" py:replace="js.display()" />
</head>
<body>
    <div py:for="js in tg_js_bodytop" py:replace="js.display()" />
    <div id="content">
        <div py:replace="form.display(action='testform')"/>
    </div>
    <div py:for="js in tg_js_bodybottom" py:replace="js.display()" />
</body>
</html>
