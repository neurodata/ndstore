<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title py:if="is_valid">Registration Complete</title>
    <title py:if="not is_valid">User Validation Error</title>
</head>

<body>
    <!-- !This section is only displayed if the validation credentials were correct -->
    <span py:strip="True" py:if="is_valid">
        <h1>Welcome ${name}</h1>
        
        <p>
            You have successfully registered. 
			<span py:if="tg.identity.anonymous" py:strip="True">
				If you like, you can now <a href="${login}">login</a>.
			</span>
        </p>
        
        <p>Thank you.</p>
    </span>
    
    <!-- !This section is displayed if the validation credentials were bad -->
    <span py:strip="True" py:if="not is_valid">
        <h1>Validation Error</h1>
		<?python
		# try to find the name in the admin_email.
		lt_index = admin_email.find(' <')
		if lt_index != -1:
			admin_name = admin_email[:lt_index]
		else:
			admin_name = admin_email
		?>
        
        <p>
            This web address will not properly validate a user.  If you followed the link
            we sent and still received this page, please email 
            <a href="mailto:${admin_email}">${admin_name}</a> and let us know you are having 
            problems.
        </p>
    </span>

</body>
</html>