Frequently Asked Questions (FAQ)
********************************

This page will be updated to reflect commonly asked questions to provide a common reference point for questions and answers.  Users may also wish to search for answers on the general `NeuroData Support mailing list <https://groups.google.com/forum/#!forum/ocp-support>`_ archives.

New questions should be asked on  `our support pages <support@neurodata.io>`_.

**What is this project?**

This project is part of `NeuroData <http://neurodata.io>`_.  The following information applies across our projects.

**How do I get started?**

To learn how to navigate the web console please visit our `Adminstrator Console <console>`_ page.

**How do I install NeuroData?**

Please begin with the `configuration <config>`_ page, which should get you up and running in no time.

**How do I contribute my data to NeuroData?**

Please visit our `How to Ingest Data <ingesting>`_ page, which will help you with mulitple options.

**Can I keep my data private?**

We are an open science data portal so we do encourage you to make their data public as this will enable open science and allow other people to work on your data. But the project does **NOT** enforce you to make your data public. You can keep your data private for as long as you like.

**How much data can I upload?**

You can upload upto 1TB using the auto-ingest function provided. If you have more data please send us a note on our support forums and one of us will contact you.

**How do I contribute code to NeuroData?**

This project is under active development.  To contribute new functionality or extend the project, either get in touch with us directly, or clone our git repo and issue a pull request. Prior to contributing, checkout our dev branches to see if some of your suggestions are already being implemented. To issue a pull request, head over to our repository and select the pull requests option on the righthand side, then issue a new pull request.

**How do I put in a new feature request or propose an idea?**

You can open an issue on our github `repository <https://github.com/neurodata/ndstore/issues>`_ and tag it as a feature. Prior to opening a new feature request, please checout our other feature issues to see if some of your suggestions or features have not been discussed before.

**How do I report code bugs?**

You can open an issue on our github `repository <https://github.com/neurodata/ndstore/issues>`_ and tag it as a bug. Prior to reporting a bug, please checout our other bugs to see if your bug has been reported or not. Do also have a look at our support forums to identify if this is a bug or not.

**How do I view my data?**

Please visit our `NeuroDataViz page <http://docs.neurodata.io/ndviz/>`_.

**Why is the first slice of my data blank?**
First check the offset of your data to make certain it is correct. If it is it could be that there is just not visualizable data on that slice, such as if the data is present by at too low of an insensity to be seen.

**What if I think my data is missing?**
First do the following: Check if it is propagated or not. Check the resolution. Try fetching data at base resolution using the data API. Try a region in the center of dataset. If your data is 16-bit check if the window is correctly set. If you have tried all of the above recommendations then you should contact us by opening a git issue.

**What if the API is down?**
First make certain you actually cannot access the API and that it isn't just slow. Once you have verified that the API is unaccessible wait at least three hours before opening an issue, or if the issue is urgent send an email (with all of your issue details) to support@neurodata.io. This email or issue should include all relevent details such a when you tried accessing the APIs, what you tried to fix it and what api documentation you looked at. 

**How do I use the RESTful interface?**

The RESTful interface can be accessed with any browser by inputting the correct link or any package that supports web requests. Alternatively if you do not wish to use the api directly we recommend you use our python interface `ndio <https://github.com/neurodata/ndio>`_.

**If I want to set up my own instance of ndstore?**
Generally we do not recommend setting up your own ndstore instance for storing data. However if you do wish to do this, the setup script can be found at 

**Is there a way to retrieve (near-) isotropic jpeg stacks?**
There is no current way to retrieve near-isotropic data in JPEG format. We do store both isotropic and near-isotropic data for some of our datasets.

**Is it possible to deploy instances of the ndstore with Docker?**
Yes, however it is highly not recommended and there is no formal support for it.

**Is there a support forum?**

Information on making a support request and archived questions and answers may be found `here <https://groups.google.com/a/neurodata.io/forum/#!forum/support>`_.
