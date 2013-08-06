<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Delete Account</title>
    <script type="text/javascript">
        function confirmDelete() {
            return confirm("<span py:replace="confirm_msg"/>");
        }
    </script>
</head>

<body>
    <h1>Delete Account</h1>
    
    <p>
        Please enter your account password to delete your account. 
        Submitting this password will immediately and permanently 
        remove your account from this site.
    </p>
    
    <p py:content="form(action=action, submit_text=submit_text)">
        User deletion form goes here.
    </p>

</body>
</html>