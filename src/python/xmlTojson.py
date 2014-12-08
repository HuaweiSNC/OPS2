
try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree
    
import json
 
def isdk_process_elemtree2dict(elem):
    
    
    d=dict()
    #d=dict(tag=elem.tag)
    if elem.text:
        d[elem.tag[elem.tag.find('}') + 1:]]=elem.text
    #if elem.attrib:
        #d['attributes']=elem.attrib
    children=elem.getchildren()
    if children:
        d[elem.tag[elem.tag.find('}') + 1:]]=map(isdk_process_elemtree2dict, children)
    #if elem.tail:
    #    d['tail']=elem.tail
    return d
#  
# def isdk_process_dict2elemtree(pfsh, factory=etree.Element):
#     
#     e=factory(pfsh['tag'], pfsh.get('attributes', {}))
#     e.text=pfsh.get('text', "")
#     e.tail=pfsh.get('tail', "")
#     for c in pfsh.get('children', ()):
#         e.append(isdk_process_dict2elemtree(c))
#     return e

def isdk_convert_xml2json(sxmlInput):
    tdoc = etree.fromstring(sxmlInput)
    dGeneratedDict = isdk_process_elemtree2dict(tdoc)
    #return json.dumps(dGeneratedDict, sort_keys=True, indent=4, separators=(', ',': '))
    return dGeneratedDict

# def isdk_convert_json2xml(jsonInput):
#     dDict = json.loads(jsonInput)
#     tdoc = isdk_process_dict2elemtree(dDict)
#     return etree.tostring(tdoc, pretty_print=False, encoding=None)    
     
if __name__ == '__main__':
    sxmlInput = '''<aaa xmlns="http://www.huawei.com/netconf/vrp" xmlns:ns0="urn:ietf:params:xml:ns:netconf:base:1.0" format-version="1.0" content-version="1.0">
      <taskGroupTaskMaps>
        <taskGroupTaskMap>
          <extendVrAttr>0</extendVrAttr>
          <taskName>interface-mgr</taskName>
          <read>enable</read>
          <write>enable</write>
          <execute>enable</execute>
          <taskGroupName>tg9</taskGroupName>
          <debug>disable</debug>
        </taskGroupTaskMap>
        <taskGroupTaskMap>
          <extendVrAttr>0</extendVrAttr>
          <taskName>config</taskName>
          <read>enable</read>
          <write>enable</write>
          <execute>enable</execute>
          <taskGroupName>tg9</taskGroupName>
          <debug>disable</debug>
        </taskGroupTaskMap>
        <taskGroupTaskMap>
          <extendVrAttr>0</extendVrAttr>
          <taskName>vlan</taskName>
          <read>enable</read>
          <write>enable</write>
          <execute>enable</execute>
          <taskGroupName>tg9</taskGroupName>
          <debug>disable</debug>
        </taskGroupTaskMap>
      </taskGroupTaskMaps>
    </aaa>'''

    jsonOutput = isdk_convert_xml2json(sxmlInput)
    #print "1->",jsonOutput 
    print jsonOutput

#     tdoc = isdk_process_dict2elemtree(jsonOutput)
#     print etree.tostring(tdoc, pretty_print=False, encoding=None)
    
    
    
