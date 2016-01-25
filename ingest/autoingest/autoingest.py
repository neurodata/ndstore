# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import argparse
import requests
import os
import requests
from jsonspec.validators import load

CHANNEL_SCHEMA = load({
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Schema for Channel JSON object for ingest",
    "type": "object",
    "properties": {
        "channel_name": {
            "description": "Channel name for the channel",
            "type": "string"
        },
        "datatype": {
            "description": "Datatype of the channel",
            "enum": [ "uint8", "uint16", "uint32", "uint64", "float32" ]
        },
        "channel_type": {
            "description": "Type of Scaling - Isotropic(1) or Normal(0)",
            "enum": [ "image", "annotation", "probmap", "timeseries" ]
        },
        "exceptions": {
            "description": "Enable exceptions - Yes(1) or No(0) (for annotation data)",
            "type": "integer"
        },
        "resolution": {
            "description": "Start Resolution (for annotation data)",
            "type": "integer"
        },
        "windowrange": {
            "description": "Window clamp function for 16-bit channels with low max value of pixels",
            "type": "array"
        },
        "readonly": {
            "description": "Read-only Channel(1) or Not(0). You can remotely post to channel if it is not readonly and overwrite data",
            "type": "integer"
        },
        "data_url": {
            "description": "This url points to the root directory of the files. Dropbox is not an acceptable HTTP Server.",
            "type": "string"
        },
        "file_format": {
            "description": "This is the file format type. For now we support only Slice stacks and CATMAID tiles.",
            "enum": [ "SLICE", "CATMAID" ]
        },
        "file_type": {
            "description": "This the file type the data is stored in",
            "enum": [ "tif", "png", "tiff" ]
        },
    },
    "required": ["channel_name", "channel_type", "data_url", "datatype", "file_format", "file_type"]
})

DATASET_SCHEMA = load({
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Schema for Dataset JSON object for ingest",
    "type": "object",
    "properties": {
        "dataset_name": {
            "description": "The name of the dataset",
            "type": "string"
        },
        "imagesize": {
          	"type": "array",
            "description": "The image dimensions of the dataset",
        },
        "voxelres": {
          	"type": "array",
            "description": "The voxel resolutoin of the data",
        },
        "offset": {
            "type": "array",
            "description": "The dimensions offset from origin",
        },
        "timerange": {
            "description": "The timerange of the data",
              "type": "array",
        },
        "scalinglevels": {
            "description": "Required Scaling levels/ Zoom out levels",
            "type": "integer"
        },
        "scaling": {
            "description": "Type of Scaling - Isotropic(1) or Normal(0)",
            "type": "integer"
        },
    },
    "required": ["dataset_name", "imagesize", "voxelres"]
})

PROJECT_SCHEMA = load({
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Schema for Dataset JSON object for ingest",
    "type": "object",
    "properties": {
        "project_name": {
            "description": "The name of the project",
            "type": "string"
        },
        "public": {
            "description": "Whether or not the project is publicly viewable, by default not",
            "type": "integer"
        },
        "token_name":  {
            "description": "The token name for the project, by default same as project_name",
            "type": "string"
        },
    },
    "required": ["project_name"]
})



class AutoIngest:

    def __init__(self):
        self.channels = {}
        self.dataset = []
        self.project = []
        self.metadata = ''

    def add_channel(
        self, channel_name, datatype, channel_type, data_url, file_format,
            file_type, exceptions=0, resolution=0,
            windowrange=(0, 0), readonly=0):
        """
        Arguments:
            channel_name (str): Channel Name is the specific name of a
            specific series of data. Standard naming convention is to do
            ImageTypeIterationNumber or NameSubProjectName.

            datatype (str): The data type is the storage method of data in
            the channel. It can be uint8, uint16, uint32, uint64, or
            float32.

            channel_type (str): The channel type is the kind of data being
            stored in the channel. It can be image, annotation, or
            timeseries.

            data_url (str): This url points to the root directory of the
            files. Dropbox (or any data requiring authentication to
            download such as s3) is not an acceptable HTTP Server.

            file_format (str): File format refers to the overarching kind
            of data, as in slices (normal image data) or catmaid
            (tile-based).

            file_type (str): File type refers to the specific type of file
            that the data is stored in, as in, tiff, png, or tif.

            exceptions (int): Exceptions is an option to enable the
            possibility for annotations to contradict each other (assign
            different values to the same point). 1 corresponds to True, 0
            corresponds to False.

            resolution (int): Resolution is the starting resolution of the
            data being uploaded to the channel.

            windowrange (int, int): Window range is the maximum and minimum
            pixel values for a particular image. This is used so that the
            image can be displayed in a readable way for viewing through
            RESTful calls

            readonly (int): This option allows the user to control if,
            after the initial data commit, the channel is read-only.
            Generally this is suggested with data that will be publicly
            viewable.

        Returns:
            None
        """
        self.channels[
            channel_name] = [channel_name, datatype, channel_type, data_url,
                             file_format, file_type, exceptions, resolution,
                             windowrange, readonly]

    def add_project(self, project_name, token_name='', public=0):
        """
        Arguments:
            project_name (str): Project name is the specific project within
            a dataset's name. If there is only one project associated with
            a dataset then standard convention is to name the project the
            same as its associated dataset.

            token_name (str): The token name is the default token. If you
            do not wish to specify one, a default one will be created for
            you with the same name as the project name. However, if the
            project is private you must specify a token.

            public (int): This option allows users to specify if they want
            the project/channels to be publicly viewable/search-able.
            (1, 0) = (TRUE, FALSE)

        Returns:
            None
        """

        self.project = (project_name, token_name, public)

    def add_dataset(self, dataset_name, imagesize, voxelres,
                    offset=(0, 0, 0), timerange=(0, 0), scalinglevels=0,
                    scaling=0):
        self.dataset = (dataset_name, imagesize, voxelres,
                        offset, timerange, scalinglevels, scaling)
        """
        Arguments:
            dataset_name (str): Dataset Name is the overarching name of the
            research effort. Standard naming convention is to do
            LabNamePublicationYear or LeadResearcherCurrentYear.

            imagesize (int, int, int): Image size is the pixel count
            dimensions of the data. For example is the data is stored as a
            series of 100 slices each 2100x2000 pixel TIFF images, the X,Y,Z
            dimensions are (2100, 2000, 100).

            voxelres (flt, flt, flt): Voxel Resolution is the number of
            voxels per unit pixel. We store X,Y,Z voxel resolution separately.

            offset (int, int, int): If your data is not well aligned and
            there is "excess" image data you do not wish to examine, but
            are present in your images, offset is how you specify where your
            actual image starts. Offset is provided a pixel coordinate offset
            from origin which specifies the "actual" origin of the image.
            The offset is for X,Y,Z dimensions.

            timerange (int, int): Time Range is a parameter to support
            storage of Time Series data, so the value of the tuple is a 0
            to X range of how many images over time were taken. It takes 2
            inputs timeStepStart and timeStepStop.

            scalinglevels (int): Scaling levels is the number of levels the
            data is scalable to (how many zoom levels are present in the
            data). The highest resolution of the data is at scaling level 0,
            and for each level up the data is down sampled by 2x2
            (per slice). To learn more about the sampling service used,
            visit the the propagation service page.

            scaling (int): Scaling is the orientation of the data being
            stored, 0 corresponds to a Z-slice orientation (as in a
            collection of tiff images in which each tiff is a slice on the
            z plane) and 1 corresponds to an isotropic orientation (in
            which each tiff is a slice on the y plane).

        Returns:
            None
        """

    def add_metadata(self, metadata=""):
        self.metadata = metadata

        """
        Arguements:
            metadata(str): Any metadata as appropriate from the LIMS schema

        Returns:
            None
        """

    def nd_json(self, dataset, project, channel_list, metadata):
        """Genarate ND json object"""
        nd_dict = {}
        nd_dict['dataset'] = self.dataset_dict(*dataset)
        nd_dict['project'] = self.project_dict(*project)
        nd_dict['metadata'] = metadata
        nd_dict['channels'] = {}
        for channel_name, value in channel_list.iteritems():
            nd_dict['channels'][channel_name] = self.channel_dict(*value)

        return json.dumps(nd_dict, sort_keys=True, indent=4)

    def nd_json_list(self, dataset, project, channel_list, metadata):
        """Genarate ND json object"""
        nd_dict = {}
        nd_dict['dataset'] = self.dataset_dict(*dataset)
        nd_dict['project'] = self.project_dict(*project)
        nd_dict['metadata'] = metadata
        nd_dict['channels'] = {}
        for channel_name, value in channel_list.iteritems():
            nd_dict['channels'].append(self.channel_dict(*value))

        return json.dumps(nd_dict, sort_keys=True, indent=4)

    def dataset_dict(
        self, dataset_name, imagesize, voxelres,
            offset=[0, 0, 0], timerange=[0, 0], scalinglevels=0, scaling=0):
        """Generate the dataset dictionary"""
        dataset_dict = {}
        dataset_dict['dataset_name'] = dataset_name
        dataset_dict['imagesize'] = imagesize
        dataset_dict['voxelres'] = voxelres
        if offset is not None:
            dataset_dict['offset'] = offset
        if timerange is not None:
            dataset_dict['timerange'] = timerange
        if scalinglevels is not None:
            dataset_dict['scalinglevels'] = scalinglevels
        if scaling is not None:
            dataset_dict['scaling'] = scaling
        return dataset_dict

    def channel_dict(
        self, channel_name, datatype, channel_type, data_url, file_format,
            file_type, exceptions=0, resolution=0,
            windowrange=[0, 0], readonly=0):
        """Genearte the project dictionary"""
        channel_dict = {}
        channel_dict['channel_name'] = channel_name
        channel_dict['datatype'] = datatype
        channel_dict['channel_type'] = channel_type
        if exceptions is not None:
            channel_dict['exceptions'] = exceptions
        if resolution is not None:
            channel_dict['resolution'] = resolution
        if windowrange is not None:
            channel_dict['windowrange'] = windowrange
        if readonly is not None:
            channel_dict['readonly'] = readonly
        channel_dict['data_url'] = data_url
        channel_dict['file_format'] = file_format
        channel_dict['file_type'] = file_type
        return channel_dict

    def project_dict(self, project_name, token_name=None, public=0):
        """Genarate the project dictionary"""
        project_dict = {}
        project_dict['project_name'] = project_name
        if token_name is not None:
             if token_name == '':
                 project_dict['token_name'] = project_name 
             else:
                 project_dict['token_name'] = token_name
        else: 
             project_dict['token_name'] = project_name 

        project_dict['public'] = public
        return project_dict

    def verify_path(self, data):
        # Insert try and catch blocks
        try:
            token_name = data["project"]["token_name"]
        except:
            token_name = data["project"]["project_name"]

        channel_names = data["channels"].keys()

        for i in range(0, len(channel_names)):
            channel_type = data["channels"][
                channel_names[i]]["channel_type"]
            path = data["channels"][channel_names[i]]["data_url"]

            if (channel_type == "timeseries"):
                timerange = data["dataset"]["timerange"]
                for j in xrange(timerange[0], timerange[1] + 1):
                    # Test for tifs or such? Currently test for just not
                    # empty
                    work_path = "{}{}/{}/time{}/".format(
                        path, token_name, channel_names[i], j)
                    resp = requests.head(work_path)
                    assert(resp.status_code == 200)
            else:
                # Test for tifs or such? Currently test for just not empty
                work_path = "{}{}/{}/".format(
                    path, token_name, channel_names[i])
                resp = requests.head(work_path)
                assert(resp.status_code == 200)

    def verify_json(self, data):
        # Channels
        channel_names = data["channels"].keys()
        for i in range(0, len(channel_names)):
            channel_object = data["channels"][channel_names[i]]
            try:
                CHANNEL_SCHEMA.validate(channel_object)
            except:
                print 'Check inputted variables. Dumping to /tmp/'
                self.output_json('/tmp/ND_{}.json'.format(channel_names[i]))

        # Dataset
        dataset_object = data["dataset"]
        try:
            DATASET_SCHEMA.validate(dataset_object)
        except:
            print "Check inputted variables. Dumping to /tmp/"
            self.output_json('/tmp/ND_dataset.json')

        # Project
        project_object = data["project"]
        try:
            PROJECT_SCHEMA.validate(project_object)
        except:
            print "Check inputted variables. Dumping to /tmp/"
            self.output_json('/tmp/ND_project.json')

    def put_data(self, data, site_host):
        # try to post data to the server
        URLPath = "{}ocp/ca/autoIngest/".format(site_host)
        try:
            r = requests.post(URLPath, data=json.dumps(data))
            assert( r.status_code == 200 )
        except:
            print "Error in posting JSON file"

    def post_data(self, site_host='http://openconnectome.me', file_name=None):
        """
        Arguements:
            site_host(str): The site host to post the data to, by default
            http://openconnectome.me.

            file_name(str): The file name of the json file to post (optional).
            If this is left unspecified it is assumed the data is in the
            AutoIngets object.

        Returns:
            None
        """

        if (file_name is None):
            complete_example = (
                self.dataset, self.project, self.channels, self.metadata)
            data = json.loads(self.nd_json(*complete_example))

        else:
            try:
                with open(file_name) as data_file:
                    data = json.load(data_file)
            except:
                print "Error opening file"

        self.verify_path(data)
        self.verify_json(data)

        self.put_data(data, site_host)

    def output_json(self, file_name='/tmp/ND.json'):
        """
        Arguements:
            file_name(str): The file name to store the json to, by default
            /tmp/ND.json

        Returns:
            None
        """
        complete_example = (
            self.dataset, self.project, self.channels, self.metadata)
        data = self.nd_json(*complete_example)
        self.verify_json(json.loads(data))

        f = open(file_name, 'w')
        f.write(data)
        f.close()
