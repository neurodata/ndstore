Authentication
**************

**Overview**
The security authentication for ndstore applies to any endpoint that is specified as secured for non-public data. The docs are broken into three parts; user access, endpoint security and tests. If you are a user of the service you should only need to deal with the first section. If you are writing endpoints for ndstore then you should review the later two sections as well.

**Interacting with the Endpoints**


**Securing an Endpoint**
In order to secure an endpoint there are a number of decorators that should be added to the views method. First is the @api_view(['GET','POST']) decorator, which specifies what types of HTTP requests can be sent to this endpoint. For example if the decorator @api_view(['GET']) is added above the method then only GET requests can be made to this endpoint. Next is the @authentication_classes((SessionAuthentication, TokenAuthentication)) decorator, which specifies the types of authentication that are required when using a specific endpoint. In this example case above, the endpoint can be accessed using both token based authentication and session based authentication. However if desired only a single type of authentication can be specified, which is recommended for endpoints that should only be accessed with token based authentication. Finally, adding the @permission_classes((PublicAuthentication,)) decorator will add the user authentication for the endpoint. Specifically it will use the permission class created for the backend that allows access if the data is public or owned by the user requesting it (or the user is a super user). Alternatively if you wish to use a different permission class (for example allowing any users that identify themselves) simply specify that instead.

**Security Testing**
As outlined above, in order to access non-private data the user must send a token with the request to identify themselves to the backend. In order to test that users do not have the ability to view datasets they do not own, two users are created in the backend during set up of the server, a super user with full permissions to every dataset and a "temporary" user that only has access to one dataset. When the tests are run the tests read the files that hold the tokens for the two users and make sample calls to the backend. 
