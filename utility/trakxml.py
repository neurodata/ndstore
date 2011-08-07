#!/usr/bin/python

import random

class TrakXML:
    def __init__(self):
        random.seed()
        self.oid = 0
        self.unuid = "{0}.{1}.{2}".format(random.randint(0,100000000000), random.randint(0,100000000), random.randint(0,100000000))

    def getoid(self):
        self.oid = self.oid + 1
        return self.oid


    def writeHeader(self, file):
        file.write("""
        <!DOCTYPE trakem2_anything [
            <!ELEMENT trakem2 (project,t2_layer_set,t2_display)>
            <!ELEMENT project (anything)>
            <!ATTLIST project id NMTOKEN #REQUIRED>
            <!ATTLIST project unuid NMTOKEN #REQUIRED>
            <!ATTLIST project title NMTOKEN #REQUIRED>
            <!ATTLIST project preprocessor NMTOKEN #REQUIRED>
            <!ATTLIST project mipmaps_folder NMTOKEN #REQUIRED>
            <!ATTLIST project storage_folder NMTOKEN #REQUIRED>
            <!ATTLIST project image_resizing_mode NMTOKEN #REQUIRED>
            <!ATTLIST project look_ahead_cache NMTOKEN #REQUIRED>
            <!ATTLIST project n_undo_steps NMTOKEN #REQUIRED>
            <!ELEMENT anything EMPTY>
            <!ATTLIST anything id NMTOKEN #REQUIRED>
            <!ATTLIST anything expanded NMTOKEN #REQUIRED>
            <!ELEMENT t2_layer (t2_patch,t2_label,t2_layer_set,t2_profile)>
            <!ATTLIST t2_layer oid NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer thickness NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer z NMTOKEN #REQUIRED>
            <!ELEMENT t2_layer_set (t2_prop,t2_linked_prop,t2_annot,t2_layer,t2_pipe,t2_ball,t2_area_list,t2_calibration,t2_stack,t2_treeline)>
            <!ATTLIST t2_layer_set oid NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set layer_id NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set transform NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set style NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set locked NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set visible NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set title NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set links NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set composite NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set layer_width NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set layer_height NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set rot_x NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set rot_y NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set rot_z NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set snapshots_quality NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set color_cues NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set area_color_cues NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set avoid_color_cue_colors NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set n_layers_color_cue NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set paint_arrows NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set paint_tags NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set paint_edge_confidence_boxes NMTOKEN #REQUIRED>
            <!ATTLIST t2_layer_set preload_ahead NMTOKEN #REQUIRED>
            <!ELEMENT t2_calibration EMPTY>
            <!ATTLIST t2_calibration pixelWidth NMTOKEN #REQUIRED>
            <!ATTLIST t2_calibration pixelHeight NMTOKEN #REQUIRED>
            <!ATTLIST t2_calibration pixelDepth NMTOKEN #REQUIRED>
            <!ATTLIST t2_calibration xOrigin NMTOKEN #REQUIRED>
            <!ATTLIST t2_calibration yOrigin NMTOKEN #REQUIRED>
            <!ATTLIST t2_calibration zOrigin NMTOKEN #REQUIRED>
            <!ATTLIST t2_calibration info NMTOKEN #REQUIRED>
            <!ATTLIST t2_calibration valueUnit NMTOKEN #REQUIRED>
            <!ATTLIST t2_calibration timeUnit NMTOKEN #REQUIRED>
            <!ATTLIST t2_calibration unit NMTOKEN #REQUIRED>
            <!ELEMENT t2_ball (t2_prop,t2_linked_prop,t2_annot,t2_ball_ob)>
            <!ATTLIST t2_ball oid NMTOKEN #REQUIRED>
            <!ATTLIST t2_ball layer_id NMTOKEN #REQUIRED>
            <!ATTLIST t2_ball transform NMTOKEN #REQUIRED>
            <!ATTLIST t2_ball style NMTOKEN #REQUIRED>
            <!ATTLIST t2_ball locked NMTOKEN #REQUIRED>
            <!ATTLIST t2_ball visible NMTOKEN #REQUIRED>
            <!ATTLIST t2_ball title NMTOKEN #REQUIRED>
            <!ATTLIST t2_ball links NMTOKEN #REQUIRED>
            <!ATTLIST t2_ball composite NMTOKEN #REQUIRED>
            <!ATTLIST t2_ball fill NMTOKEN #REQUIRED>
            <!ELEMENT t2_ball_ob EMPTY>
            <!ATTLIST t2_ball_ob x NMTOKEN #REQUIRED>
            <!ATTLIST t2_ball_ob y NMTOKEN #REQUIRED>
            <!ATTLIST t2_ball_ob r NMTOKEN #REQUIRED>
            <!ATTLIST t2_ball_ob layer_id NMTOKEN #REQUIRED>
            <!ELEMENT t2_label (t2_prop,t2_linked_prop,t2_annot)>
            <!ATTLIST t2_label oid NMTOKEN #REQUIRED>
            <!ATTLIST t2_label layer_id NMTOKEN #REQUIRED>
            <!ATTLIST t2_label transform NMTOKEN #REQUIRED>
            <!ATTLIST t2_label style NMTOKEN #REQUIRED>
            <!ATTLIST t2_label locked NMTOKEN #REQUIRED>
            <!ATTLIST t2_label visible NMTOKEN #REQUIRED>
            <!ATTLIST t2_label title NMTOKEN #REQUIRED>
            <!ATTLIST t2_label links NMTOKEN #REQUIRED>
            <!ATTLIST t2_label composite NMTOKEN #REQUIRED>
            <!ELEMENT t2_patch (t2_prop,t2_linked_prop,t2_annot,ict_transform,ict_transform_list)>
            <!ATTLIST t2_patch oid NMTOKEN #REQUIRED>
            <!ATTLIST t2_patch layer_id NMTOKEN #REQUIRED>
            <!ATTLIST t2_patch transform NMTOKEN #REQUIRED>
            <!ATTLIST t2_patch style NMTOKEN #REQUIRED>
            <!ATTLIST t2_patch locked NMTOKEN #REQUIRED>
            <!ATTLIST t2_patch visible NMTOKEN #REQUIRED>
            <!ATTLIST t2_patch title NMTOKEN #REQUIRED>
            <!ATTLIST t2_patch links NMTOKEN #REQUIRED>
            <!ATTLIST t2_patch composite NMTOKEN #REQUIRED>
            <!ATTLIST t2_patch file_path NMTOKEN #REQUIRED>
            <!ATTLIST t2_patch original_path NMTOKEN #REQUIRED>
            <!ATTLIST t2_patch type NMTOKEN #REQUIRED>
            <!ATTLIST t2_patch ct NMTOKEN #REQUIRED>
            <!ATTLIST t2_patch o_width NMTOKEN #REQUIRED>
            <!ATTLIST t2_patch o_height NMTOKEN #REQUIRED>
            <!ATTLIST t2_patch pps NMTOKEN #REQUIRED>
            <!ELEMENT t2_pipe (t2_prop,t2_linked_prop,t2_annot)>
            <!ATTLIST t2_pipe oid NMTOKEN #REQUIRED>
            <!ATTLIST t2_pipe layer_id NMTOKEN #REQUIRED>
            <!ATTLIST t2_pipe transform NMTOKEN #REQUIRED>
            <!ATTLIST t2_pipe style NMTOKEN #REQUIRED>
            <!ATTLIST t2_pipe locked NMTOKEN #REQUIRED>
            <!ATTLIST t2_pipe visible NMTOKEN #REQUIRED>
            <!ATTLIST t2_pipe title NMTOKEN #REQUIRED>
            <!ATTLIST t2_pipe links NMTOKEN #REQUIRED>
            <!ATTLIST t2_pipe composite NMTOKEN #REQUIRED>
            <!ATTLIST t2_pipe d NMTOKEN #REQUIRED>
            <!ATTLIST t2_pipe p_width NMTOKEN #REQUIRED>
            <!ATTLIST t2_pipe layer_ids NMTOKEN #REQUIRED>
            <!ELEMENT t2_polyline (t2_prop,t2_linked_prop,t2_annot)>
            <!ATTLIST t2_polyline oid NMTOKEN #REQUIRED>
            <!ATTLIST t2_polyline layer_id NMTOKEN #REQUIRED>
            <!ATTLIST t2_polyline transform NMTOKEN #REQUIRED>
            <!ATTLIST t2_polyline style NMTOKEN #REQUIRED>
            <!ATTLIST t2_polyline locked NMTOKEN #REQUIRED>
            <!ATTLIST t2_polyline visible NMTOKEN #REQUIRED>
            <!ATTLIST t2_polyline title NMTOKEN #REQUIRED>
            <!ATTLIST t2_polyline links NMTOKEN #REQUIRED>
            <!ATTLIST t2_polyline composite NMTOKEN #REQUIRED>
            <!ATTLIST t2_polyline d NMTOKEN #REQUIRED>
            <!ELEMENT t2_profile (t2_prop,t2_linked_prop,t2_annot)>
            <!ATTLIST t2_profile oid NMTOKEN #REQUIRED>
            <!ATTLIST t2_profile layer_id NMTOKEN #REQUIRED>
            <!ATTLIST t2_profile transform NMTOKEN #REQUIRED>
            <!ATTLIST t2_profile style NMTOKEN #REQUIRED>
            <!ATTLIST t2_profile locked NMTOKEN #REQUIRED>
            <!ATTLIST t2_profile visible NMTOKEN #REQUIRED>
            <!ATTLIST t2_profile title NMTOKEN #REQUIRED>
            <!ATTLIST t2_profile links NMTOKEN #REQUIRED>
            <!ATTLIST t2_profile composite NMTOKEN #REQUIRED>
            <!ATTLIST t2_profile d NMTOKEN #REQUIRED>
            <!ELEMENT t2_area_list (t2_prop,t2_linked_prop,t2_annot,t2_area)>
            <!ATTLIST t2_area_list oid NMTOKEN #REQUIRED>
            <!ATTLIST t2_area_list layer_id NMTOKEN #REQUIRED>
            <!ATTLIST t2_area_list transform NMTOKEN #REQUIRED>
            <!ATTLIST t2_area_list style NMTOKEN #REQUIRED>
            <!ATTLIST t2_area_list locked NMTOKEN #REQUIRED>
            <!ATTLIST t2_area_list visible NMTOKEN #REQUIRED>
            <!ATTLIST t2_area_list title NMTOKEN #REQUIRED>
            <!ATTLIST t2_area_list links NMTOKEN #REQUIRED>
            <!ATTLIST t2_area_list composite NMTOKEN #REQUIRED>
            <!ATTLIST t2_area_list fill_paint NMTOKEN #REQUIRED>
            <!ELEMENT t2_area (t2_path)>
            <!ATTLIST t2_area layer_id NMTOKEN #REQUIRED>
            <!ELEMENT t2_path EMPTY>
            <!ATTLIST t2_path d NMTOKEN #REQUIRED>
            <!ELEMENT t2_dissector (t2_prop,t2_linked_prop,t2_annot,t2_dd_item)>
            <!ATTLIST t2_dissector oid NMTOKEN #REQUIRED>
            <!ATTLIST t2_dissector layer_id NMTOKEN #REQUIRED>
            <!ATTLIST t2_dissector transform NMTOKEN #REQUIRED>
            <!ATTLIST t2_dissector style NMTOKEN #REQUIRED>
            <!ATTLIST t2_dissector locked NMTOKEN #REQUIRED>
            <!ATTLIST t2_dissector visible NMTOKEN #REQUIRED>
            <!ATTLIST t2_dissector title NMTOKEN #REQUIRED>
            <!ATTLIST t2_dissector links NMTOKEN #REQUIRED>
            <!ATTLIST t2_dissector composite NMTOKEN #REQUIRED>
            <!ELEMENT t2_dd_item EMPTY>
            <!ATTLIST t2_dd_item radius NMTOKEN #REQUIRED>
            <!ATTLIST t2_dd_item tag NMTOKEN #REQUIRED>
            <!ATTLIST t2_dd_item points NMTOKEN #REQUIRED>
            <!ELEMENT t2_stack (t2_prop,t2_linked_prop,t2_annot,(iict_transform|iict_transform_list)?)>
            <!ATTLIST t2_stack oid NMTOKEN #REQUIRED>
            <!ATTLIST t2_stack layer_id NMTOKEN #REQUIRED>
            <!ATTLIST t2_stack transform NMTOKEN #REQUIRED>
            <!ATTLIST t2_stack style NMTOKEN #REQUIRED>
            <!ATTLIST t2_stack locked NMTOKEN #REQUIRED>
            <!ATTLIST t2_stack visible NMTOKEN #REQUIRED>
            <!ATTLIST t2_stack title NMTOKEN #REQUIRED>
            <!ATTLIST t2_stack links NMTOKEN #REQUIRED>
            <!ATTLIST t2_stack composite NMTOKEN #REQUIRED>
            <!ATTLIST t2_stack file_path CDATA #REQUIRED>
            <!ATTLIST t2_stack depth CDATA #REQUIRED>
            <!ELEMENT t2_tag EMPTY>
            <!ATTLIST t2_tag name NMTOKEN #REQUIRED>
            <!ATTLIST t2_tag key NMTOKEN #REQUIRED>
            <!ELEMENT t2_node (t2_area*,t2_tag*)>
            <!ATTLIST t2_node x NMTOKEN #REQUIRED>
            <!ATTLIST t2_node y NMTOKEN #REQUIRED>
            <!ATTLIST t2_node lid NMTOKEN #REQUIRED>
            <!ATTLIST t2_node c NMTOKEN #REQUIRED>
            <!ATTLIST t2_node r NMTOKEN #IMPLIED>
            <!ELEMENT t2_treeline (t2_node*,t2_prop,t2_linked_prop,t2_annot)>
            <!ATTLIST t2_treeline oid NMTOKEN #REQUIRED>
            <!ATTLIST t2_treeline layer_id NMTOKEN #REQUIRED>
            <!ATTLIST t2_treeline transform NMTOKEN #REQUIRED>
            <!ATTLIST t2_treeline style NMTOKEN #REQUIRED>
            <!ATTLIST t2_treeline locked NMTOKEN #REQUIRED>
            <!ATTLIST t2_treeline visible NMTOKEN #REQUIRED>
            <!ATTLIST t2_treeline title NMTOKEN #REQUIRED>
            <!ATTLIST t2_treeline links NMTOKEN #REQUIRED>
            <!ATTLIST t2_treeline composite NMTOKEN #REQUIRED>
            <!ELEMENT t2_areatree (t2_node*,t2_prop,t2_linked_prop,t2_annot)>
            <!ATTLIST t2_areatree oid NMTOKEN #REQUIRED>
            <!ATTLIST t2_areatree layer_id NMTOKEN #REQUIRED>
            <!ATTLIST t2_areatree transform NMTOKEN #REQUIRED>
            <!ATTLIST t2_areatree style NMTOKEN #REQUIRED>
            <!ATTLIST t2_areatree locked NMTOKEN #REQUIRED>
            <!ATTLIST t2_areatree visible NMTOKEN #REQUIRED>
            <!ATTLIST t2_areatree title NMTOKEN #REQUIRED>
            <!ATTLIST t2_areatree links NMTOKEN #REQUIRED>
            <!ATTLIST t2_areatree composite NMTOKEN #REQUIRED>
            <!ELEMENT t2_connector (t2_node*,t2_prop,t2_linked_prop,t2_annot)>
            <!ATTLIST t2_connector oid NMTOKEN #REQUIRED>
            <!ATTLIST t2_connector layer_id NMTOKEN #REQUIRED>
            <!ATTLIST t2_connector transform NMTOKEN #REQUIRED>
            <!ATTLIST t2_connector style NMTOKEN #REQUIRED>
            <!ATTLIST t2_connector locked NMTOKEN #REQUIRED>
            <!ATTLIST t2_connector visible NMTOKEN #REQUIRED>
            <!ATTLIST t2_connector title NMTOKEN #REQUIRED>
            <!ATTLIST t2_connector links NMTOKEN #REQUIRED>
            <!ATTLIST t2_connector composite NMTOKEN #REQUIRED>
            <!ELEMENT t2_prop EMPTY>
            <!ATTLIST t2_prop key NMTOKEN #REQUIRED>
            <!ATTLIST t2_prop value NMTOKEN #REQUIRED>
            <!ELEMENT t2_linked_prop EMPTY>
            <!ATTLIST t2_linked_prop target_id NMTOKEN #REQUIRED>
            <!ATTLIST t2_linked_prop key NMTOKEN #REQUIRED>
            <!ATTLIST t2_linked_prop value NMTOKEN #REQUIRED>
            <!ELEMENT t2_annot EMPTY>
            <!ELEMENT t2_display EMPTY>
            <!ATTLIST t2_display id NMTOKEN #REQUIRED>
            <!ATTLIST t2_display layer_id NMTOKEN #REQUIRED>
            <!ATTLIST t2_display x NMTOKEN #REQUIRED>
            <!ATTLIST t2_display y NMTOKEN #REQUIRED>
            <!ATTLIST t2_display magnification NMTOKEN #REQUIRED>
            <!ATTLIST t2_display srcrect_x NMTOKEN #REQUIRED>
            <!ATTLIST t2_display srcrect_y NMTOKEN #REQUIRED>
            <!ATTLIST t2_display srcrect_width NMTOKEN #REQUIRED>
            <!ATTLIST t2_display srcrect_height NMTOKEN #REQUIRED>
            <!ATTLIST t2_display scroll_step NMTOKEN #REQUIRED>
            <!ATTLIST t2_display c_alphas NMTOKEN #REQUIRED>
            <!ATTLIST t2_display c_alphas_state NMTOKEN #REQUIRED>
            <!ATTLIST t2_display filter_enabled NMTOKEN #REQUIRED>
            <!ATTLIST t2_display filter_min_max_enabled NMTOKEN #REQUIRED>
            <!ATTLIST t2_display filter_min NMTOKEN #REQUIRED>
            <!ATTLIST t2_display filter_max NMTOKEN #REQUIRED>
            <!ATTLIST t2_display filter_invert NMTOKEN #REQUIRED>
            <!ATTLIST t2_display filter_clahe_enabled NMTOKEN #REQUIRED>
            <!ATTLIST t2_display filter_clahe_block_size NMTOKEN #REQUIRED>
            <!ATTLIST t2_display filter_clahe_histogram_bins NMTOKEN #REQUIRED>
            <!ATTLIST t2_display filter_clahe_max_slope NMTOKEN #REQUIRED>
            <!ELEMENT ict_transform EMPTY>
            <!ATTLIST ict_transform class CDATA #REQUIRED>
            <!ATTLIST ict_transform data CDATA #REQUIRED>
            <!ELEMENT iict_transform EMPTY>
            <!ATTLIST iict_transform class CDATA #REQUIRED>
            <!ATTLIST iict_transform data CDATA #REQUIRED>
            <!ELEMENT ict_transform_list (ict_transform|iict_transform)*>
            <!ELEMENT iict_transform_list (iict_transform*)>
        ] >

""")

    def writeBody(self, file, height, width):
        file.write("""
        <trakem2>
            <project 
                id="0"
                title="CATMAID Crop (experimental)"
""")
        file.write('unuid="{0}"\n'.format(self.unuid))
        file.write("""
                storage_folder=""
                image_resizing_mode="Gaussian"
                look_ahead_cache="0"
                n_undo_steps="32"
                layer_mipmaps="true"
            >
            </project>
            <t2_layer_set
""")
        file.write('oid="{0}"\n'.format(self.getoid()))
        file.write("""
                width="20.0"
                height="20.0"
                transform="matrix(1.0,0.0,0.0,1.0,0.0,0.0)"
                title="Top Level"
                links=""
""")
        file.write('layer_width="{0}"\n'.format(width))
        file.write('layer_height="{0}"\n'.format(height))
        file.write("""
                rot_x="0.0"
                rot_y="0.0"
                rot_z="0.0"
                snapshots_quality="true"
                snapshots_mode="Disabled"
                color_cues="true"
                area_color_cues="true"
                avoid_color_cue_colors="false"
                n_layers_color_cue="0"
                paint_arrows="true"
                paint_tags="true"
                paint_edge_confidence_boxes="true"
                prepaint="true"
                preload_ahead="0"
            >
                <t2_calibration
                    pixelWidth="1.0"
                    pixelHeight="1.0"
                    pixelDepth="1.0"
                    xOrigin="0.0"
                    yOrigin="0.0"
                    zOrigin="0.0"
                    info="null"
                    valueUnit="Gray Value"
                    timeUnit="sec"
                    unit="pixel"
                />
        """)


    def writeLayer(self, file, layer, filename, height, width):
        file.write('<t2_layer oid="{0}" thickness="40.0" z="{1}.0" title="" >\n'.format(self.getoid(), layer))
        file.write('<t2_patch oid="{0}"\n'.format(self.getoid()))
        file.write('width="{0}" height="{1}" o_width="{0}" o_height="{1}"\n'.format(width, height, width, height))
        #print 'width="{0}" height="{1}"'.format(256,256)
        #print 'o_width="{0}" o_height="{1}"'.format(256,256)
        #print 'transform="matrix(1.0,0.0,0.0,1.0,{0},{1})"'.format(256*x,256*y)
        file.write('transform="matrix(1.0,0.0,0.0,1.0,0,0)"\n')
        file.write('style="fill-opacity:1.0;stroke:#ffff00;"\n')
        file.write('min="0" max="255"\n')
        file.write('title="{0}"\n'.format(filename))
        file.write('links=""\n')
        file.write('type="0"\n')
        #print 'file_path="http://openconnectomeproject.org/data/misc/nodata.png"'
        file.write('file_path="{0}"\n'.format(filename))
        #print 'file_path="http://openconnectomeproject.org/~eric/trakweb/image.cgi/{0}-{1}/{0}-{1}-{2}.png"'.format(x, y, layer)
        #print 'file_path="{0}-{1}-{2}.png"'.format(x, y, layer)
        #print 'file_path="180-220-int/180-220-int-02.tif"'
        file.write('>\n')
        file.write('</t2_patch>\n'+'</t2_layer>\n')

    def writeFooter(self, file):
        file.write('</t2_layer_set>\n')
        file.write('<t2_display id="{0}"\n'.format(self.getoid()))
        file.write('/>\n')
        file.write('</trakem2>\n')
