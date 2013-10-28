<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Lost Password</title>
</head>

<body>

    <h1>Lost Password</h1>
    
    <p>
        Please enter the user name or email address associated with your account. 
    </p>
    
    <?python
    submit_text = 'Email Password'
    ?>
    
    <p py:content="form(action=action, submit_text=submit_text)">Lost Password form goes here</p>

</body>
</html>
