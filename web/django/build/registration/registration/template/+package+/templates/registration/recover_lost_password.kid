<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Reset Password</title>
</head>

<body>
    <!-- !This section is displayed if the user was found and an email was sent -->
    <span py:strip="True" py:if="mail_sent">
	
        <h1>Reset Password</h1>
    
        <p>
            We have sent an email to the address on record for this account. Please follow
            the directions it contains to reset your password.
        </p>    
		<p>
			Bear in mind that normal network delays can occasionally cause email messages to 
			take several hours to be delivered.
		</p>

    </span>
    
    <!-- !This section is displayed if the email address was bad -->
    <span py:strip="True" py:if="not mail_sent">
        <h1>User Not Found</h1>
        
		<p>There is no account with that user name or email address at this website.</p>

    </span>

</body>
</html>