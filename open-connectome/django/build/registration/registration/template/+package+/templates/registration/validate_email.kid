<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title py:if="is_valid">Email Address Changed</title>
    <title py:if="not is_valid">Email Validation Error</title>
</head>

<body>
    <!-- !This section is only displayed if the validation credentials were correct -->
    <span py:strip="True" py:if="is_valid">
        <h1>Email Address Changed</h1>
        
        <p>
            ${name}, your email address has been changed to ${email}.
        </p>
        
        <p>Thank you.</p>
    </span>
    
    <!-- !This section is displayed if the validation credentials were bad -->
    <span py:strip="True" py:if="not is_valid">
        <h1>Email Validation Error</h1>
        
        <p>
            This web address will not properly validate a changed email address.  
			If you followed the link we sent and still received this page, please email 
            <a href="mailto:${admin_email}">${admin_email}</a> and let us know you are having 
            problems.
        </p>
    </span>

</body>
</html>