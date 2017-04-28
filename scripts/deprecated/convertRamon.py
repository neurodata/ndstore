# Copyright 2016 NeuroData (http://neurodata.io)
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

import os, sys
import argparse
import MySQLdb
from contextlib import closing


sys.path += [os.path.abspath('../django')]
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ND.settings'
import django
from django.conf import settings
django.setup()

from nduser.models import Project, Channel
from ndproject import NDProject, NDChannel
import annotation
import mysqlramondb
import ramondb

class ConvertRamon:
    """ Converts an annotation project from the old RAMON format (spread across many tables) to the new RAMON format (consolidated in a single table) """

    def __init__(self, project, channel):
        try:
            self.pr = Project.objects.get( project_name = project )
        except Project.DoesNotExist:
            raise

        self.ch = Channel.objects.get( channel_name = channel, project = self.pr )

        # pr and ch are django objects. proj and chan are NDStore objects
        self.proj = NDProject(self.pr.project_name)
        self.chan = NDChannel(self.proj, self.ch.channel_name)

        self.annodb = mysqlramondb.MySQLRamonDB(self.proj)
        self.ramondb = ramondb.RamonDB(self.proj)

        self.getAllAnnoIDs()

    def createRAMONTables(self):

        with closing(MySQLdb.connect(host = self.proj.getDBHost(), user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db = self.proj.getDBName(), connect_timeout=1)) as conn:
            with closing(conn.cursor()) as cursor:

                try:

                    ramonTableName = '{}_ramon'.format(self.ch.channel_name)

                    cursor.execute("CREATE TABLE {} ( annoid BIGINT, kv_key VARCHAR(255), kv_value VARCHAR(20000), INDEX ( annoid, kv_key ) USING BTREE)".format(ramonTableName))

                    # Commiting at the end
                    conn.commit()

                except MySQLdb.Error, e:
                    print "Error: Failed to create new RAMON table: {}".format(e)
                    sys.exit(1)

    def processAnnos(self):
        for id in self.ids:
            self.processExistingAnnotationByID(id)

    def getAllAnnoIDs(self):
        with closing(MySQLdb.connect(host = self.proj.getDBHost(), user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db = self.proj.getDBName(), connect_timeout=1)) as conn:
            with closing(conn.cursor()) as cursor:
                idTableName = "{}_ids".format( self.ch.channel_name )
                sql = "SELECT id FROM {}".format( idTableName )

                try:
                    cursor.execute( sql )
                    tmpids = cursor.fetchall()
                except MySQLdb.Error, e:
                    print "Error: Failed to fetch existing RAMON IDs: {}".format(e)
                    sys.exit(1)

        self.ids = [x[0] for x in tmpids]

    def _getAnnoType(self, id):

        with closing(MySQLdb.connect(host = self.proj.getDBHost(), user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db = self.proj.getDBName(), connect_timeout=1)) as conn:
            with closing(conn.cursor()) as cursor:
                annoTableName = "{}_annotations".format( self.ch.channel_name )
                sql = "SELECT type FROM {} WHERE annoid={}".format( annoTableName, id )

                try:
                    cursor.execute( sql )
                    res = cursor.fetchall()
                    return res[0]
                except MySQLdb.Error, e:
                    print "Error: Failed to get annotation type for RAMON object with ID {}: {}".format(id, e)
                    sys.exit(1)

    def _readAnnoMetadata(self, id):
        # reads the basic metadata in for all annotation types (from annotation_annotations table)

        with closing(MySQLdb.connect(host = self.proj.getDBHost(), user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db = self.proj.getDBName(), connect_timeout=1)) as conn:
            with closing(conn.cursor()) as cursor:
                annoTableName = "{}_annotations".format( self.ch.channel_name )
                sql = "SELECT confidence, status FROM {} WHERE annoid={}".format( annoTableName, id )

                try:
                    cursor.execute( sql )
                    res = cursor.fetchall()
                    return res[0]
                except MySQLdb.Error, e:
                    print "Error: Failed to get annotation type for RAMON object with ID {}: {}".format(id, e)
                    sys.exit(1)

    def _readKVPairs(self, id):
        # reads and returns KV Pairs from the kvpairs table
        with closing(MySQLdb.connect(host = self.proj.getDBHost(), user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db = self.proj.getDBName(), connect_timeout=1)) as conn:
            with closing(conn.cursor()) as cursor:
                kvTableName = "{}_kvpairs".format( self.ch.channel_name )
                sql = "SELECT kv_key, kv_value FROM {} WHERE annoid={}".format( kvTableName, id )

                try:
                    cursor.execute( sql )
                    res = cursor.fetchall()
                except MySQLdb.Error, e:
                    print "Error: Failed to get annotation type for RAMON object with ID {}: {}".format(id, e)
                    sys.exit(1)
        kvpairs = {}
        for row in res:
            kvpairs[ row[0] ] = row[1]
        return kvpairs

    def _readSynapse(self, id):
        # create a new synapse
        anno = annotation.AnnSynapse( self.annodb, self.ch )

        # set the synapse ID
        anno.setField('annid', id)

        # fill in the fields
        # basic metadata first
        [confidence, status] = self._readAnnoMetadata(id)

        anno.setField('status', status)
        anno.setField('confidence', confidence)

        # synapse related metadata
        with closing(MySQLdb.connect(host = self.proj.getDBHost(), user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db = self.proj.getDBName(), connect_timeout=1)) as conn:
            with closing(conn.cursor()) as cursor:
                synapseTableName = "{}_synapses".format( self.ch.channel_name )
                sql = "SELECT synapse_type, weight FROM {} WHERE annoid={}".format( synapseTableName, id )

                try:
                    cursor.execute( sql )
                    res = cursor.fetchall()[0]
                except MySQLdb.Error, e:
                    print "Error: Failed to get annotation type for RAMON object with ID {}: {}".format(id, e)
                    sys.exit(1)

        anno.setField('synapse_type', res[0])
        anno.setField('weight', res[1])

        # parse kvpairs
        kvpairs = self._readKVPairs(id)
        for key in kvpairs.keys():
            value = kvpairs[key]
            if key == 'ann_author':
                anno.setField('author', value)
            elif key == 'organelles':
                continue
            elif key == 'synapses':
                continue
            else:
                anno.setField(key, value)

        # return newly created anno object
        return anno

    def _readSeed(self, id):
        # create a new seed
        anno = annotation.AnnSeed( self.annodb, self.ch )

        # set the anno ID
        anno.setField('annid', id)

        # fill in the fields
        # basic metadata first
        [confidence, status] = self._readAnnoMetadata(id)

        anno.setField('status', status)
        anno.setField('confidence', confidence)

        # segment related metadata
        with closing(MySQLdb.connect(host = self.proj.getDBHost(), user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db = self.proj.getDBName(), connect_timeout=1)) as conn:
            with closing(conn.cursor()) as cursor:
                seedTableName = "{}_seeds".format( self.ch.channel_name )
                sql = "SELECT parentid, sourceid, cube_location, positionx, positiony, positionz FROM {} WHERE annoid={}".format( seedTableName, id )

                try:
                    cursor.execute( sql )
                    res = cursor.fetchall()[0]
                except MySQLdb.Error, e:
                    print "Error: Failed to get annotation type for RAMON object with ID {}: {}".format(id, e)
                    sys.exit(1)

        anno.setField('parent', res[0])
        anno.setField('source', res[1])
        anno.setField('cubelocation', res[2])
        anno.setField('position', "{},{},{}".format( res[3], res[4], res[5] ))

        # parse kvpairs
        kvpairs = self._readKVPairs(id)
        for key in kvpairs.keys():
            value = kvpairs[key]
            if key == 'ann_author':
                anno.setField('author', value)
            else:
                anno.setField(key, value)

        # return newly completed anno object
        return anno

    def _readSegment(self, id):
        # create a new segment
        anno = annotation.AnnSegment( self.annodb, self.ch )

        # set the segment ID
        anno.setField('annid', id)

        # fill in the fields
        # basic metadata first
        [confidence, status] = self._readAnnoMetadata(id)

        anno.setField('status', status)
        anno.setField('confidence', confidence)

        # segment related metadata
        with closing(MySQLdb.connect(host = self.proj.getDBHost(), user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db = self.proj.getDBName(), connect_timeout=1)) as conn:
            with closing(conn.cursor()) as cursor:
                segTableName = "{}_segments".format( self.ch.channel_name )
                sql = "SELECT segmentclass, parentseed, neuron FROM {} WHERE annoid={}".format( segTableName, id )

                try:
                    cursor.execute( sql )
                    res = cursor.fetchall()[0]
                except MySQLdb.Error, e:
                    print "Error: Failed to get annotation type for RAMON object with ID {}: {}".format(id, e)
                    sys.exit(1)

        anno.setField('segmentclass', res[0])
        anno.setField('parentseed', res[1])
        anno.setField('neuron', res[2])

        # parse kvpairs
        kvpairs = self._readKVPairs(id)
        for key in kvpairs.keys():
            value = kvpairs[key]
            if key == 'ann_author':
                anno.setField('author', value)
            elif key == 'organelles':
                continue
            elif key == 'synapses':
                continue
            else:
                anno.setField(key, value)

        # return newly completed anno object
        return anno

    def _readNeuron(self, id):
        # create a new neuron
        anno = annotation.AnnNeuron( self.annodb, self.ch )

        # set the anno ID
        anno.setField('annid', id)

        # fill in the fields
        # basic metadata first
        [confidence, status] = self._readAnnoMetadata(id)

        anno.setField('status', status)
        anno.setField('confidence', confidence)

        # parse kvpairs
        kvpairs = self._readKVPairs(id)
        for key in kvpairs.keys():
            value = kvpairs[key]
            if key == 'ann_author':
                anno.setField('author', value)
            elif key == 'segments':
                continue
            else:
                anno.setField(key, value)

        # return newly completed anno object
        return anno

    def _readOrganelle(self, id):
        # create a new organelle
        anno = annotation.AnnOrganelle( self.annodb, self.ch )

        # set the organelle ID
        anno.setField('annid', id)

        # fill in the fields
        # basic metadata first
        [confidence, status] = self._readAnnoMetadata(id)

        anno.setField('status', status)
        anno.setField('confidence', confidence)

        # segment related metadata
        with closing(MySQLdb.connect(host = self.proj.getDBHost(), user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db = self.proj.getDBName(), connect_timeout=1)) as conn:
            with closing(conn.cursor()) as cursor:
                orgTableName = "{}_organelles".format( self.ch.channel_name )
                sql = "SELECT organelleclass, parentseed, centroidx, centroidy, centroidz FROM {} WHERE annoid={}".format( orgTableName, id )

                try:
                    cursor.execute( sql )
                    res = cursor.fetchall()[0]
                except MySQLdb.Error, e:
                    print "Error: Failed to get annotation type for RAMON object with ID {}: {}".format(id, e)
                    sys.exit(1)

        anno.setField('organelleclass', res[0])
        anno.setField('parentseed', res[1])
        anno.setField('centroid', "{},{},{}".format(res[2], res[3], res[4]))

        # parse kvpairs
        kvpairs = self._readKVPairs(id)
        for key in kvpairs.keys():
            value = kvpairs[key]
            if key == 'ann_author':
                anno.setField('author', value)
            else:
                anno.setField(key, value)

        # return newly completed anno object
        return anno

    def _readNode(self, id):
        # create a new organodenelle
        anno = annotation.AnnNode( self.annodb, self.ch )

        # set the organelle ID
        anno.setField('annid', id)

        # fill in the fields
        # basic metadata first
        [confidence, status] = self._readAnnoMetadata(id)

        anno.setField('status', status)
        anno.setField('confidence', confidence)

        # segment related metadata
        with closing(MySQLdb.connect(host = self.proj.getDBHost(), user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db = self.proj.getDBName(), connect_timeout=1)) as conn:
            with closing(conn.cursor()) as cursor:
                nodeTableName = "{}_nodes".format( self.ch.channel_name )
                sql = "SELECT skeletonid, nodetype, parentid, locationx, locationy, locationz, radius FROM {} WHERE annoid={}".format( nodeTableName, id )

                try:
                    cursor.execute( sql )
                    res = cursor.fetchall()[0]
                except MySQLdb.Error, e:
                    print "Error: Failed to get annotation type for RAMON object with ID {}: {}".format(id, e)
                    sys.exit(1)

        anno.setField('skeleton', res[0])
        anno.setField('nodetype', res[1])
        anno.setField('parent', res[2])
        anno.setField('location', "{},{},{}".format(res[3], res[4], res[5]))
        anno.setField('radius', res[6])

        # parse kvpairs
        kvpairs = self._readKVPairs(id)
        for key in kvpairs.keys():
            value = kvpairs[key]
            if key == 'ann_author':
                anno.setField('author', value)
            elif key == 'children':
                continue
            else:
                anno.setField(key, value)

        # return newly completed anno object
        return anno

    def _readSkeleton(self, id):
        # create a new skeleton
        anno = annotation.AnnSkeleton( self.annodb, self.ch )

        # set the skeleton ID
        anno.setField('annid', id)

        # fill in the fields
        # basic metadata first
        [confidence, status] = self._readAnnoMetadata(id)

        anno.setField('status', status)
        anno.setField('confidence', confidence)

        # segment related metadata
        with closing(MySQLdb.connect(host = self.proj.getDBHost(), user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db = self.proj.getDBName(), connect_timeout=1)) as conn:
            with closing(conn.cursor()) as cursor:
                skeletonTableName = "{}_skeletons".format( self.ch.channel_name )
                sql = "SELECT skeletontype, rootnode FROM {} WHERE annoid={}".format( skeletonTableName, id )

                try:
                    cursor.execute( sql )
                    res = cursor.fetchall()[0]
                except MySQLdb.Error, e:
                    print "Error: Failed to get annotation type for RAMON object with ID {}: {}".format(id, e)
                    sys.exit(1)

        anno.setField('skeletontype', res[0])
        anno.setField('rootnode', res[1])

        # parse kvpairs
        kvpairs = self._readKVPairs(id)
        for key in kvpairs.keys():
            value = kvpairs[key]
            if key == 'ann_author':
                anno.setField('author', value)
            elif key == 'skeletonnodes':
                continue
            else:
                anno.setField(key, value)

        # return newly completed anno object
        return anno

    def _readAnnotation(self, id):
        # create a new annotation
        anno = annotation.Annotation( self.annodb, self.ch )

        # set the segment ID
        anno.setField('annid', id)

        # fill in the fields
        # basic metadata first
        [confidence, status] = self._readAnnoMetadata(id)

        anno.setField('status', status)
        anno.setField('confidence', confidence)

        # parse kvpairs
        kvpairs = self._readKVPairs(id)
        for key in kvpairs.keys():
            value = kvpairs[key]
            if key == 'ann_author':
                anno.setField('author', value)
            else:
                anno.setField(key, value)

        # return newly completed anno object
        return anno

    def processExistingAnnotationByID(self, id):

        # get the annotation type
        anntype = self._getAnnoType(id)[0]
        if anntype == annotation.ANNO_SYNAPSE:
            anno = self._readSynapse(id)
        elif anntype == annotation.ANNO_SEED:
            anno = self._readSeed(id)
        elif anntype == annotation.ANNO_SEGMENT:
            anno = self._readSegment(id)
        elif anntype == annotation.ANNO_NEURON:
            anno = self._readNeuron(id)
        elif anntype == annotation.ANNO_ORGANELLE:
            anno = self._readOrganelle(id)
        elif anntype == annotation.ANNO_NODE:
            anno = self._readNode(id)
        elif anntype == annotation.ANNO_SKELETON:
            anno = self._readSkeleton(id)
        elif anntype == annotation.ANNO_ANNOTATION:
            anno = self._readAnnotation(id)
        else:
            print "Unknown annotation type: {}".format(anntype)
            sys.exit(1)

        try:
            self.ramondb.putAnnotation( self.chan, anno )
        except Exception, e:
            print e
            import pdb; pdb.set_trace()

def main():

    parser = argparse.ArgumentParser(description='Convert a channel from the old RAMON format (multiple tables) to the new RAMON format (single tables)')
    parser.add_argument('project', action='store', help='Project (not token) name')
    parser.add_argument('channel', action='store', help='Channel name')
    parser.add_argument('--skip-table', action='store_true', help='Skip creatin the new annotation table.')

    result = parser.parse_args()

    cr = ConvertRamon(result.project, result.channel)
    if not result.skip_table:
        cr.createRAMONTables()

    cr.processAnnos()

if __name__ == '__main__':
    main()
