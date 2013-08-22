<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:layout="'../login.kid'">

	<!-- !Replace the href below with the path to the real 'lost_password' controller -->
	<a py:def="lost_password_link()" href="/registration/lost_password">Lost Password</a>

	
	<div py:match="item.attrib.get('id', '') == 'loginBox'" 
		py:content="item[:] + [lost_password_link()] " py:attrs="item.attrib"/>
</html>