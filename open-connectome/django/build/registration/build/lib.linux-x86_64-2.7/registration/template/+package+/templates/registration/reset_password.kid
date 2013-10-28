<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Reset Password</title>
</head>

<body>

    <h1>Reset Password</h1>
    
    <p py:if="err_msg" py:content="err_msg">Error message goes here.</p>

    <span py:if="show_form" py:strip="True">
        <p py:content="form(data, action=action, submit_text=submit_text)">Lost Password form goes here</p>
    </span>
    
    <span py:if="not show_form" py:strip="True">
        <p>There was a problem with the link as entered. Please check to ensure that 
            you entered all of the link information correctly.
        </p>
    </span>

</body>
</html>
